"""World map generator, tile management, and wandering map-enemy system.

Map is 100×80 tiles.  Old world_data coordinates were authored for a 30×22
grid; we auto-scale them with (_sx, _sy) below.

Connectivity guarantee
──────────────────────
After every map is generated the engine runs a BFS flood-fill from the
village tile and finds any walkable region that is cut off by water, lava or
mountain.  For each isolated island it BFS-searches (through any terrain)
for the shortest tunnel to the main reachable component, then carves those
blocking tiles to "path" — natural-looking bridges and mountain passes.
This loop repeats until the whole map is one connected component.
"""
import random
import math
from collections import deque
import pygame   # noqa – needed for MapEnemy.draw

from settings import MAP_W, MAP_H, TILE, ENCOUNTER_RATE
from data.world_data import BIOMES

# Tile types the player cannot walk through (water removed — player sails on it)
_BLOCKING = frozenset({"wall", "lava", "mountain"})

# Tile types non-aquatic monsters cannot enter (water added back)
_MONSTER_BLOCKING = frozenset({"wall", "water", "lava", "mountain"})

# Scale factors: old-coord → new-map-coord
_SX = MAP_W / 30.0
_SY = MAP_H / 22.0


def _scale_tile(t):
    """Scale an (x, y) tuple from 30×22 space to MAP_W×MAP_H space."""
    x, y = t
    return (
        max(2, min(MAP_W - 3, int(round(x * _SX)))),
        max(2, min(MAP_H - 3, int(round(y * _SY)))),
    )


# ── Extra location types drawn on the map ────────────────────────────────────
LOC_TYPES = {
    "shrine": {"tile": "ruins",  "color": (140, 100, 180), "label": "S"},   # Sacred shrine
    "chest":  {"tile": "path",   "color": (210, 170,  50), "label": "$"},   # Treasure chest
    "camp":   {"tile": "path",   "color": (160, 100,  40), "label": "C"},   # Campsite
    "ruins":  {"tile": "ruins",  "color": (120, 110, 100), "label": "R"},   # Ruins
    "well":   {"tile": "village","color": (100, 150, 200), "label": "W"},   # Well
    "altar":  {"tile": "ruins",  "color": (180,  60, 180), "label": "A"},   # Altar
}


# ─────────────────────────────────────────────────────────────────────────────
class TileMap:
    """Holds a 2-D tile grid for one biome, plus extra locations."""

    def __init__(self, biome_id: str, seed: int = None):
        self.biome_id = biome_id
        biome = BIOMES[biome_id]
        self.base = biome["tile_base"]
        self.features = biome["tile_features"]
        self.encounter_tiles = biome.get("encounter_tiles", [self.base])

        # Auto-scale village / boss / rare-area coords from old 30×22 space
        self.village_tile = _scale_tile(biome["village"]["tile"])
        raw_boss = biome.get("boss_tile", (MAP_W - 6, 4))
        self.boss_tile = _scale_tile(raw_boss)

        self.rare_areas = []
        for ra in biome.get("rare_skill_areas", []):
            entry = dict(ra)
            entry["tile"] = _scale_tile(ra["tile"])
            self.rare_areas.append(entry)

        self.connections = biome["connections"]

        rng = random.Random(seed if seed is not None else hash(biome_id))
        self.grid = self._generate(rng)

        # ── Guaranteed special tiles ─────────────────────────────────────────
        vx, vy = self.village_tile
        self.grid[vy][vx] = "village"
        bx, by = self.boss_tile
        self.grid[by][bx] = "path"

        for ra in self.rare_areas:
            rx, ry = ra["tile"]
            if 0 < rx < MAP_W - 1 and 0 < ry < MAP_H - 1:
                self.grid[ry][rx] = "cave"

        # ── Extra scattered locations ────────────────────────────────────────
        self.extra_locs = []   # list of {"tile": (x,y), "type": str}
        loc_plan = [
            ("shrine", 5, 8),
            ("camp",   4, 7),
            ("ruins",  5, 8),
            ("altar",  2, 4),
            ("well",   2, 4),
        ]
        for loc_type, lo, hi in loc_plan:
            count = rng.randint(lo, hi)
            for _ in range(count):
                for _attempt in range(40):
                    lx = rng.randint(4, MAP_W - 5)
                    ly = rng.randint(4, MAP_H - 5)
                    if self.grid[ly][lx] == self.base:
                        self.extra_locs.append({"tile": (lx, ly), "type": loc_type})
                        dest_tile = LOC_TYPES.get(loc_type, {}).get("tile", self.base)
                        self.grid[ly][lx] = dest_tile
                        break

        # ── Carve guaranteed path village → boss ─────────────────────────────
        self._carve_path(vx, vy, bx, by)

        # ── Border exits (all four edges walkable) ───────────────────────────
        for x in range(MAP_W):
            self.grid[0][x] = "path"
            self.grid[MAP_H - 1][x] = "path"
        for y in range(MAP_H):
            self.grid[y][0] = "path"
            self.grid[y][MAP_W - 1] = "path"

        # ── Connectivity pass: bridge any isolated walkable islands ──────────
        self._ensure_connectivity()

        # ── Boss lair — stamped LAST so it never sits on a bridge tile ───────
        self._stamp_boss_lair(bx, by)

        # ── Track which extra locations the player has already visited ───────
        self.used_locs: set = set()

        # ── Make sure the village entrance is always clear ───────────────────
        for _dy, _dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            _nx, _ny = vx + _dx, vy + _dy
            if 1 <= _nx < MAP_W - 1 and 1 <= _ny < MAP_H - 1:
                if self.grid[_ny][_nx] in _BLOCKING:
                    self.grid[_ny][_nx] = "path"

    # ── Terrain generation ────────────────────────────────────────────────────

    def _generate(self, rng: random.Random) -> list:
        """Multi-pass organic terrain: blobs → rivers → ridges → CA smooth."""
        grid = [[self.base] * MAP_W for _ in range(MAP_H)]

        # Pass 1 – blob clusters for each feature
        for feature, density in self.features.items():
            n_blobs = int(MAP_W * MAP_H * density / 25)  # fewer, larger blobs
            for _ in range(max(1, n_blobs)):
                cx = rng.randint(3, MAP_W - 4)
                cy = rng.randint(3, MAP_H - 4)
                radius = rng.randint(3, 7)
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        nx2, ny2 = cx + dx, cy + dy
                        if 0 < nx2 < MAP_W - 1 and 0 < ny2 < MAP_H - 1:
                            dist = math.sqrt(dx * dx + dy * dy)
                            if dist <= radius * rng.uniform(0.6, 1.1):
                                grid[ny2][nx2] = feature

        # Pass 2 – river carving (water features only)
        if "water" in self.features:
            for _ in range(rng.randint(2, 4)):
                self._carve_river(rng, grid, "water")

        # Pass 3 – mountain ridges
        if "mountain" in self.features:
            for _ in range(rng.randint(1, 3)):
                self._carve_ridge(rng, grid, "mountain")

        # Pass 4 – lava rivers (volcanic / lava biomes)
        if "lava" in self.features:
            for _ in range(rng.randint(1, 2)):
                self._carve_river(rng, grid, "lava")

        # Pass 5 – two rounds of CA smoothing
        grid = self._ca_smooth(grid, rng, 2)
        return grid

    def _carve_river(self, rng, grid, tile):
        """Random-walk a winding river across the map."""
        # Start from a random edge
        edge = rng.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            x, y = rng.randint(5, MAP_W - 6), 1
            dx, dy = 0, 1
        elif edge == "bottom":
            x, y = rng.randint(5, MAP_W - 6), MAP_H - 2
            dx, dy = 0, -1
        elif edge == "left":
            x, y = 1, rng.randint(5, MAP_H - 6)
            dx, dy = 1, 0
        else:
            x, y = MAP_W - 2, rng.randint(5, MAP_H - 6)
            dx, dy = -1, 0

        width = rng.randint(1, 3)
        steps = 0
        max_steps = MAP_W + MAP_H
        while 0 < x < MAP_W - 1 and 0 < y < MAP_H - 1 and steps < max_steps:
            # Widen the river
            for wy in range(-width, width + 1):
                for wx in range(-width, width + 1):
                    nx2, ny2 = x + wx, y + wy
                    if 0 < nx2 < MAP_W - 1 and 0 < ny2 < MAP_H - 1:
                        grid[ny2][nx2] = tile
            # Drift
            r = rng.random()
            if r < 0.6:
                x += dx
                y += dy
            elif r < 0.8:
                # Bend perpendicular
                if dx == 0:
                    x += rng.choice([-1, 1])
                else:
                    y += rng.choice([-1, 1])
            else:
                x += dx
                y += dy
                if rng.random() < 0.3:
                    if dx == 0:
                        x += rng.choice([-1, 1])
                    else:
                        y += rng.choice([-1, 1])
            steps += 1

    def _carve_ridge(self, rng, grid, tile):
        """Carve a diagonal mountain ridge."""
        x = rng.randint(5, MAP_W - 6)
        y = rng.randint(5, MAP_H - 6)
        length = rng.randint(15, 35)
        angle = rng.uniform(0, math.pi * 2)
        dx = math.cos(angle)
        dy = math.sin(angle)
        width = rng.randint(1, 3)
        for i in range(length):
            cx = int(x + dx * i)
            cy = int(y + dy * i)
            for wy in range(-width, width + 1):
                for wx in range(-width, width + 1):
                    nx2, ny2 = cx + wx, cy + wy
                    if 0 < nx2 < MAP_W - 1 and 0 < ny2 < MAP_H - 1:
                        grid[ny2][nx2] = tile

    def _ca_smooth(self, grid, rng, passes=1):
        """Cellular-automata smoothing – majority tile type among neighbours."""
        for _ in range(passes):
            new_grid = [row[:] for row in grid]
            for y in range(1, MAP_H - 1):
                for x in range(1, MAP_W - 1):
                    counts = {}
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            t = grid[y + dy][x + dx]
                            counts[t] = counts.get(t, 0) + 1
                    best = max(counts, key=counts.get)
                    # Only smooth if 5+ neighbours agree (prevents over-smoothing)
                    if counts[best] >= 5:
                        new_grid[y][x] = best
            grid = new_grid
        return grid

    def _carve_path(self, x1, y1, x2, y2):
        """Carve a guaranteed walkable L-shaped path between two points.

        Moves purely horizontally then purely vertically — never diagonal.
        Blocking tiles become 'bridge' over water/lava or 'path' through
        mountain/wall, so the village → boss corridor is always passable
        before the connectivity pass runs.
        """
        cx, cy = x1, y1
        # ── Horizontal leg ────────────────────────────────────────────────────
        while cx != x2:
            cx += 1 if cx < x2 else -1
            if self.grid[cy][cx] in _BLOCKING:
                t = self.grid[cy][cx]
                self.grid[cy][cx] = "bridge" if t in ("water", "lava") else "path"
        # ── Vertical leg ──────────────────────────────────────────────────────
        while cy != y2:
            cy += 1 if cy < y2 else -1
            if self.grid[cy][cx] in _BLOCKING:
                t = self.grid[cy][cx]
                self.grid[cy][cx] = "bridge" if t in ("water", "lava") else "path"

    # ── Connectivity helpers ──────────────────────────────────────────────────

    def _reachable_from(self, sx: int, sy: int) -> set:
        """BFS flood fill.  Returns the set of (x,y) walkable tiles
        reachable from (sx, sy) through 4-connected non-blocking tiles."""
        if self.grid[sy][sx] in _BLOCKING:
            # Starting tile is blocked; seed from nearest walkable neighbour
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                nx, ny = sx+dx, sy+dy
                if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                    if self.grid[ny][nx] not in _BLOCKING:
                        sx, sy = nx, ny
                        break
            else:
                return set()

        visited: set = set()
        stack = [(sx, sy)]
        visited.add((sx, sy))
        while stack:
            x, y = stack.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if (0 <= nx < MAP_W and 0 <= ny < MAP_H
                        and (nx, ny) not in visited
                        and self.grid[ny][nx] not in _BLOCKING):
                    visited.add((nx, ny))
                    stack.append((nx, ny))
        return visited

    def _ensure_connectivity(self):
        """Guarantee every walkable interior tile is reachable from the village.

        Algorithm (repeats until fully connected, ≤ 30 passes):
          1. Flood-fill from the village to find the *main* reachable set.
          2. Collect every walkable tile NOT in main  →  *isolated* set.
          3. If empty, done.
          4. Multi-source BFS from all isolated tiles, expanding through ANY
             terrain (including blocking tiles) until the first main tile is
             reached.
          5. Trace the path back and replace blocking tiles with 'path'
             (1 tile wide — looks like a bridge over water, a pass through
             mountains, or a hardened crossing over lava).
          6. Repeat.
        """
        vx, vy = self.village_tile

        for _pass in range(30):
            main = self._reachable_from(vx, vy)

            # Build isolated list (skip border row/col — always path already)
            isolated = []
            for y in range(1, MAP_H - 1):
                for x in range(1, MAP_W - 1):
                    if self.grid[y][x] not in _BLOCKING and (x, y) not in main:
                        isolated.append((x, y))

            if not isolated:
                break   # fully connected ✓

            # ── Multi-source BFS through ALL terrain ──────────────────────
            dist: dict = {}
            prev: dict = {}
            q: deque = deque()
            for t in isolated:
                dist[t] = 0
                q.append(t)

            found = None
            while q:
                x, y = q.popleft()
                if (x, y) in main:
                    found = (x, y)
                    break
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < MAP_W and 0 <= ny < MAP_H
                            and (nx, ny) not in dist):
                        dist[(nx, ny)] = dist[(x, y)] + 1
                        prev[(nx, ny)] = (x, y)
                        q.append((nx, ny))

            if found is None:
                break   # shouldn't happen on a finite bounded map

            # ── Trace back and carve bridge / pass ───────────────────────
            # Walk from `found` (in main) back toward the isolated source.
            # Water / lava tiles become 'bridge' (wooden planks visual).
            # Mountain / wall tiles become 'path' (mountain pass visual).
            cur = found
            bridge_len = 0
            while cur in prev:
                cur = prev[cur]
                cx, cy = cur
                if self.grid[cy][cx] in _BLOCKING:
                    t = self.grid[cy][cx]
                    self.grid[cy][cx] = "bridge" if t in ("water", "lava") else "path"
                    bridge_len += 1

            # Widen bridge by 1 tile perpendicular if it crosses water/lava
            # (makes it look like a proper bridge rather than a 1-pixel path)
            if bridge_len >= 3:
                self._widen_bridge(prev, found)

    def _stamp_boss_lair(self, bx: int, by: int) -> None:
        """Stamp a 3×3 region of 'boss_lair' tiles centred on the boss position.

        Always called AFTER _ensure_connectivity() so the arena is never
        overwritten by a bridge tile and never sits on water/lava.
        All nine tiles are walkable (not in _BLOCKING).
        """
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = bx + dx, by + dy
                if 1 <= nx < MAP_W - 1 and 1 <= ny < MAP_H - 1:
                    self.grid[ny][nx] = "boss_lair"

    def _widen_bridge(self, prev: dict, start) -> None:
        """Widen a 1-tile-wide bridge by one tile on each side where possible.

        Uses the direction between consecutive path tiles to determine which
        axis is perpendicular, then only widens in those two directions.
        This keeps bridges as straight rectangular bands rather than jagged
        lumps.  We only widen over blocking tiles to avoid clobbering
        walkable terrain.
        """
        cur = start
        while cur in prev:
            nxt = prev[cur]
            cx, cy = cur
            if self.grid[cy][cx] in ("bridge", "path"):
                # Travel direction from nxt → cur
                ddx = cx - nxt[0]
                ddy = cy - nxt[1]
                # Perpendicular = rotate 90°
                if ddx != 0:            # bridge runs east-west → widen N/S
                    perp = [(cx, cy - 1), (cx, cy + 1)]
                elif ddy != 0:          # bridge runs north-south → widen E/W
                    perp = [(cx - 1, cy), (cx + 1, cy)]
                else:
                    perp = []
                for px2, py2 in perp:
                    if (0 < px2 < MAP_W - 1 and 0 < py2 < MAP_H - 1
                            and self.grid[py2][px2] in _BLOCKING):
                        t2 = self.grid[py2][px2]
                        self.grid[py2][px2] = "bridge" if t2 in ("water", "lava") else "path"
                        break   # one extra tile per bridge step
            cur = nxt

    # ── Accessors ──────────────────────────────────────────────────────────────

    def tile_at(self, x: int, y: int) -> str:
        if 0 <= x < MAP_W and 0 <= y < MAP_H:
            return self.grid[y][x]
        return "wall"

    def is_walkable(self, x: int, y: int) -> bool:
        """True for any tile the player can enter (includes water — player uses a boat)."""
        return self.tile_at(x, y) not in _BLOCKING

    def is_land_walkable(self, x: int, y: int) -> bool:
        """True only for non-water walkable tiles.  Used by non-aquatic monsters."""
        return self.tile_at(x, y) not in _MONSTER_BLOCKING

    def is_encounter_tile(self, x: int, y: int) -> bool:
        return self.tile_at(x, y) in self.encounter_tiles

    def is_village(self, x: int, y: int) -> bool:
        return (x, y) == self.village_tile

    def is_boss_area(self, x: int, y: int) -> bool:
        bx, by = self.boss_tile
        return abs(x - bx) <= 1 and abs(y - by) <= 1

    def rare_area_at(self, x: int, y: int):
        for ra in self.rare_areas:
            if (x, y) == tuple(ra["tile"]):
                return ra
        return None

    def is_border_exit(self, x: int, y: int) -> bool:
        return x <= 0 or x >= MAP_W - 1 or y <= 0 or y >= MAP_H - 1

    # Tiles the player must never spawn on (water added: always start on land)
    _SPAWN_UNSAFE = _BLOCKING | frozenset({"water", "boss_lair", "village", "bridge"})

    def safe_entry_pos(self) -> tuple:
        """Return the nearest walkable, spawn-safe tile next to the village.

        Scans outward in a growing ring from the village tile.  Returns the
        first tile that is:
          • not in _BLOCKING  (not water / lava / mountain / wall)
          • not boss_lair     (player shouldn't appear inside the castle)
          • not village       (would immediately trigger the village screen)
          • not bridge        (bridges are narrow; spawn on solid ground)
          • inside map bounds (not a border tile)

        The village entrance is always cleared of blocking tiles in __init__,
        so radius 1 almost always succeeds immediately.
        """
        vx, vy = self.village_tile
        for radius in range(1, max(MAP_W, MAP_H)):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue  # only walk the ring perimeter
                    nx, ny = vx + dx, vy + dy
                    if 1 <= nx < MAP_W - 1 and 1 <= ny < MAP_H - 1:
                        if self.grid[ny][nx] not in TileMap._SPAWN_UNSAFE:
                            return nx, ny
        # Absolute fallback — should never be reached
        return vx + 1, vy

    def random_walkable(self, rng, exclude_radius=5, cx=None, cy=None, land_only=True):
        """Return a random walkable tile, optionally away from (cx, cy).

        land_only=True  (default) — skips water tiles; used for monster spawning.
        land_only=False — allows water; used for aquatic monster spawning.
        """
        for _ in range(300):
            x = rng.randint(3, MAP_W - 4)
            y = rng.randint(3, MAP_H - 4)
            tile = self.tile_at(x, y)
            if tile in _BLOCKING:
                continue
            if land_only and tile == "water":
                continue
            if self.is_village(x, y) or self.is_boss_area(x, y):
                continue
            if cx is not None and abs(x - cx) < exclude_radius and abs(y - cy) < exclude_radius:
                continue
            return x, y
        return MAP_W // 2, MAP_H // 2


# ── Wandering map enemy ───────────────────────────────────────────────────────
class MapEnemy:
    """An enemy that wanders the exploration map and chases the player."""

    WANDER_INTERVAL = 1.6   # seconds between moves when wandering
    CHASE_INTERVAL  = 0.8   # seconds between moves when chasing
    CHASE_RANGE     = 6     # tiles (Manhattan) – start chasing within this
    ATTACK_RANGE    = 1     # tiles – trigger battle at this range

    def __init__(self, monster_id: str, x: int, y: int, tmap: "TileMap"):
        self.monster_id = monster_id
        self.x = x
        self.y = y
        self.tmap = tmap
        self._timer = 0.0
        self._rng = random.Random()
        self.chasing = False   # used by draw() for "!" indicator

        from data.monsters_data import MONSTERS
        md = MONSTERS.get(monster_id, {})
        raw_col = md.get("color", [50, 200, 200])
        self.color = tuple(min(255, max(0, int(c))) for c in raw_col[:3])
        # Aquatic monsters may enter water; non-aquatic cannot
        self._aquatic: bool = md.get("element") == "water"

    def update(self, dt: float, px: int, py: int) -> bool:
        """Tick the enemy.  Returns True when it reaches the player (battle!)."""
        interval = self.CHASE_INTERVAL if self.chasing else self.WANDER_INTERVAL
        self._timer += dt
        if self._timer < interval:
            return False
        self._timer = 0.0

        dx = px - self.x
        dy = py - self.y
        dist = abs(dx) + abs(dy)

        if dist <= self.ATTACK_RANGE:
            # Non-aquatic monsters can't attack a player who is sailing on water
            if not self._aquatic and self.tmap.tile_at(px, py) == "water":
                return False
            return True   # trigger battle

        self.chasing = (dist <= self.CHASE_RANGE)

        # Movement check: aquatic monsters may enter water; land monsters may not
        def _can_step(nx, ny):
            if self._aquatic:
                return self.tmap.is_walkable(nx, ny)
            return self.tmap.is_land_walkable(nx, ny)

        if self.chasing:
            # Step toward player (prefer the larger delta axis first)
            step_x = (1 if dx > 0 else -1) if dx != 0 else 0
            step_y = (1 if dy > 0 else -1) if dy != 0 else 0
            candidates = []
            if abs(dx) >= abs(dy):
                if step_x: candidates.append((self.x + step_x, self.y))
                if step_y: candidates.append((self.x, self.y + step_y))
            else:
                if step_y: candidates.append((self.x, self.y + step_y))
                if step_x: candidates.append((self.x + step_x, self.y))
            for nx, ny in candidates:
                if _can_step(nx, ny):
                    self.x, self.y = nx, ny
                    break
        else:
            # Random wander
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self._rng.shuffle(dirs)
            for ddx, ddy in dirs:
                nx, ny = self.x + ddx, self.y + ddy
                if _can_step(nx, ny):
                    self.x, self.y = nx, ny
                    break
        return False

    def draw(self, surf, cam_x: int, cam_y: int, tick: int):
        from ui.sprites import draw_monster_sprite
        sx = self.x * TILE - cam_x
        sy = self.y * TILE - cam_y
        sw = surf.get_width()
        sh = surf.get_height()
        if -TILE < sx < sw + TILE and -TILE < sy < sh + TILE:
            draw_monster_sprite(surf, self.monster_id, self.color,
                                sx + TILE // 2, sy + TILE // 2,
                                TILE - 6, tick)
            # Show "!" only when actively chasing
            if self.chasing:
                pygame.draw.rect(surf, (220, 40, 40),
                                 (sx + TILE - 7, sy + 1, 6, 6))
                pygame.draw.rect(surf, (255, 220, 0),
                                 (sx + TILE - 6, sy + 2, 4, 4))


# ── World manager ─────────────────────────────────────────────────────────────
class WorldManager:
    """Manages biome tile maps, encounter rolls, and wandering enemy pools."""

    ENEMY_COUNT = 20   # wandering enemies per biome

    def __init__(self):
        self._maps: dict[str, TileMap] = {}
        self._enemies: dict[str, list] = {}   # biome_id → [MapEnemy]

    # ── Map cache ─────────────────────────────────────────────────────────────

    @staticmethod
    def _stable_seed(biome_id: str) -> int:
        """Deterministic seed that is identical across processes and platforms.

        We cannot use hash() because Python randomises its hash seed per-process
        (PYTHONHASHSEED), which means two separate game instances would generate
        completely different maps for the same biome — breaking multiplayer.
        This simple polynomial hash is 100% stable.
        """
        val = 0x12345678
        for ch in biome_id:
            val = (val * 31 + ord(ch)) & 0xFFFFFFFF
        return val

    def get_map(self, biome_id: str) -> TileMap:
        if biome_id not in self._maps:
            self._maps[biome_id] = TileMap(biome_id,
                                           seed=self._stable_seed(biome_id))
        return self._maps[biome_id]

    # ── Enemy pool ────────────────────────────────────────────────────────────

    def get_enemies(self, biome_id: str, player_level: int) -> list:
        """Return (and lazily create) the wandering enemy list for a biome."""
        if biome_id not in self._enemies:
            self._spawn_enemies(biome_id, player_level)
        return self._enemies[biome_id]

    def _spawn_enemies(self, biome_id: str, player_level: int):
        from data.monsters_data import MONSTERS as _M
        tmap = self.get_map(biome_id)
        rng  = random.Random(hash(biome_id) ^ player_level)
        pool = BIOMES[biome_id].get("monsters", [])
        if not pool:
            self._enemies[biome_id] = []
            return
        vx, vy = tmap.village_tile
        enemies = []
        for _ in range(self.ENEMY_COUNT):
            mid = rng.choice(pool)
            is_aquatic = _M.get(mid, {}).get("element") == "water"
            x, y = tmap.random_walkable(rng, exclude_radius=8, cx=vx, cy=vy,
                                        land_only=not is_aquatic)
            enemies.append(MapEnemy(mid, x, y, tmap))
        self._enemies[biome_id] = enemies

    def respawn_enemies(self, biome_id: str, player_level: int):
        """Force a fresh enemy spawn (called when player re-enters biome)."""
        if biome_id in self._enemies:
            del self._enemies[biome_id]
        self._spawn_enemies(biome_id, player_level)

    def remove_enemy(self, biome_id: str, enemy: "MapEnemy"):
        if biome_id in self._enemies and enemy in self._enemies[biome_id]:
            self._enemies[biome_id].remove(enemy)
            # Immediately respawn the enemy at a different map location so
            # the pool stays populated without clustering near the player.
            self._respawn_one(biome_id, enemy.monster_id)

    def _respawn_one(self, biome_id: str, monster_id: str):
        """Spawn one replacement enemy at a random walkable tile.

        Non-aquatic monsters avoid water / bridge / boss-lair tiles.
        Aquatic monsters (element == 'water') may spawn on water tiles.
        The spawn point is kept away from the village (6-tile radius) and
        the boss arena (2-tile radius).
        """
        from data.monsters_data import MONSTERS
        tmap = self.get_map(biome_id)
        rng  = random.Random()          # unseeded — true random each call
        vx, vy   = tmap.village_tile
        bx, by_b = tmap.boss_tile
        is_aquatic = MONSTERS.get(monster_id, {}).get("element") == "water"

        for _ in range(300):
            x = rng.randint(3, MAP_W - 4)
            y = rng.randint(3, MAP_H - 4)
            t = tmap.tile_at(x, y)

            if is_aquatic:
                # Aquatic monsters may use water; skip only lava / solid walls
                if t in ("wall", "mountain", "lava", "boss_lair", "village"):
                    continue
            else:
                # Regular monsters need land — cannot enter water
                if t in _MONSTER_BLOCKING or t in ("bridge", "boss_lair", "village"):
                    continue

            # Keep away from village entrance
            if abs(x - vx) < 6 and abs(y - vy) < 6:
                continue
            # Keep away from boss lair
            if abs(x - bx) <= 2 and abs(y - by_b) <= 2:
                continue

            self._enemies[biome_id].append(MapEnemy(monster_id, x, y, tmap))
            return

        # Fallback: use the safe helper (handles edge cases)
        x2, y2 = tmap.random_walkable(rng, exclude_radius=8, cx=vx, cy=vy)
        self._enemies[biome_id].append(MapEnemy(monster_id, x2, y2, tmap))

    # ── Encounter helpers ─────────────────────────────────────────────────────

    def roll_encounter(self, biome_id: str, x: int, y: int, player) -> bool:
        """Legacy step-encounter roll (kept for compatibility; not used in UI)."""
        tmap = self.get_map(biome_id)
        if not tmap.is_encounter_tile(x, y):
            return False
        import random as _r
        chance = ENCOUNTER_RATE
        if player.has_item("monster_bait"):
            chance = 1.0
            player.remove_item("monster_bait")
        return _r.random() < chance

    def pick_monster(self, biome_id: str, player_level: int) -> str:
        biome  = BIOMES[biome_id]
        pool   = biome.get("monsters", [])
        if not pool:
            return None
        from data.monsters_data import MONSTERS
        import random as _r
        weighted = []
        for mid in pool:
            if mid not in MONSTERS:
                continue
            ml, mh = MONSTERS[mid]["level_range"]
            dist = abs((ml + mh) / 2 - player_level)
            weight = max(1, 10 - int(dist))
            # Mini-bosses appear much more rarely on the overworld
            if MONSTERS[mid].get("mini_boss", False):
                weight = max(1, weight // 10)
            weighted.extend([mid] * weight)
        return _r.choice(weighted) if weighted else _r.choice(pool)

    def get_village_info(self, biome_id: str) -> dict:
        return BIOMES[biome_id]["village"]

    def biome_display_name(self, biome_id: str) -> str:
        return BIOMES.get(biome_id, {}).get("name", biome_id.replace("_", " ").title())
