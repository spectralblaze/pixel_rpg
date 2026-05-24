"""Export all procedural sprites to PNG files you can edit.

Run from the project root:
    python tools/export_sprites.py

Output directories
------------------
  assets/monsters/  — one PNG per sprite *type* (slime, wolf, goblin …)
                      96 × 96 pixels
  assets/players/   — one PNG per player *class* (warrior, mage, rogue …)
                      80 × 80 pixels
  assets/tiles/     — one PNG per tile type (grass, water, sand …)
                      48 × 48 pixels

Editing tips
------------
  • Open any PNG in Aseprite, GIMP, Paint.NET, Photoshop, etc.
  • Keep the canvas size the same OR larger — the game scales down to fit.
  • Save as PNG with transparency (RGBA) for best results.
  • The game picks up your edited file automatically — no restart needed,
    but you can call assets.loader.invalidate_cache() for hot-reload.
  • Delete a PNG to revert to the built-in procedural art.

Monster sprite types vs IDs
----------------------------
  The game first looks for {monster_id}.png (e.g. green_slime.png), then
  falls back to {sprite_type}.png (e.g. slime.png).  This script exports
  the sprite-type files; copy and rename to override a single variant.

Player sprite classes vs subclasses
------------------------------------
  Same priority: {subclass}.png beats {base_class}.png.
  E.g. assassin.png overrides rogue.png for assassins only.
"""

import os
import sys

# ── Make sure we can import from project root ──────────────────────────────────
_HERE    = os.path.dirname(os.path.abspath(__file__))
_PROJECT = os.path.dirname(_HERE)
if _PROJECT not in sys.path:
    sys.path.insert(0, _PROJECT)

# ── Must happen before any other pygame imports ────────────────────────────────
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")   # headless rendering
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))  # tiny window required for convert_alpha

from settings import TILE_COL
from ui.sprites import (
    draw_monster_sprite, draw_player_sprite,
    draw_slime, draw_wolf, draw_rat, draw_goblin, draw_skeleton,
    draw_ghost, draw_elemental, draw_dragon, draw_golem, draw_bee,
    draw_serpent, draw_bat, draw_mummy, draw_scorpion, draw_witch,
    draw_troll, draw_harpy, draw_djinn,
    PLAYER_SPRITES,
)

# ── Destination directories ────────────────────────────────────────────────────
_ASSETS   = os.path.join(_PROJECT, "assets")
_MON_DIR  = os.path.join(_ASSETS, "monsters")
_PLY_DIR  = os.path.join(_ASSETS, "players")
_TILE_DIR = os.path.join(_ASSETS, "tiles")
for d in (_MON_DIR, _PLY_DIR, _TILE_DIR):
    os.makedirs(d, exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_surf(size):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))  # transparent
    return surf


def _save(surf, path, label):
    pygame.image.save(surf, path)
    print(f"  wrote  {os.path.relpath(path, _PROJECT)}")


def _bg(surf, col, size):
    """Draw a subtle background so the sprite is visible in the editor."""
    r, g, b = col
    # Slightly lighter version as a 'paper' background
    bg = (min(r + 40, 255), min(g + 40, 255), min(b + 40, 255), 80)
    pygame.draw.rect(surf, bg, (0, 0, size, size))

# ── Monster sprites  (96 × 96, one per sprite type) ───────────────────────────
MONSTER_SIZE = 96

MONSTER_TYPES = {
    # type_name   : (draw_fn,              representative_color)
    "slime"      : (draw_slime,      (80,  200,  80)),
    "wolf"       : (draw_wolf,       (150, 140, 120)),
    "rat"        : (draw_rat,        (130, 110,  80)),
    "goblin"     : (draw_goblin,     (100, 160,  60)),
    "skeleton"   : (draw_skeleton,   (210, 200, 180)),
    "ghost"      : (draw_ghost,      (170, 185, 220)),
    "elemental"  : (draw_elemental,  ( 60, 180, 240)),
    "dragon"     : (draw_dragon,     (200,  60,  40)),
    "golem"      : (draw_golem,      (130, 120, 110)),
    "bee"        : (draw_bee,        (230, 190,  30)),
    "serpent"    : (draw_serpent,    ( 50, 180,  80)),
    "bat"        : (draw_bat,        (110,  80, 130)),
    "mummy"      : (draw_mummy,      (200, 185, 150)),
    "scorpion"   : (draw_scorpion,   (200, 150,  60)),
    "witch"      : (draw_witch,      (130,  60, 160)),
    "troll"      : (draw_troll,      ( 80, 130,  70)),
    "harpy"      : (draw_harpy,      (160,  80, 180)),
    "djinn"      : (draw_djinn,      ( 60, 180, 220)),
}

print("\n--- Monster sprites ---------------------------------------------------")
for type_name, (fn, col) in MONSTER_TYPES.items():
    path = os.path.join(_MON_DIR, f"{type_name}.png")
    if os.path.exists(path):
        print(f"  skip   assets/monsters/{type_name}.png  (already exists)")
        continue
    surf = _make_surf(MONSTER_SIZE)
    cx = cy = MONSTER_SIZE // 2
    try:
        fn(surf, cx, cy, MONSTER_SIZE, col, tick=0)
    except TypeError:
        fn(surf, cx, cy, MONSTER_SIZE, tick=0)
    _save(surf, path, type_name)

# ── Player sprites  (80 × 80, one per base class) ─────────────────────────────
PLAYER_SIZE = 80

# Base classes with a default color — matches how draw_player_sprite uses them
PLAYER_CLASSES = {
    "warrior"   : (200,  60,  60),
    "mage"      : ( 80,  80, 220),
    "rogue"     : ( 80, 160,  80),
    "healer"    : (220, 190,  60),
    "summoner"  : (160,  60, 200),
}

# Subclasses — same color as base but distinct file so user can customise
PLAYER_SUBCLASSES = {
    # warrior subclasses
    "knight"        : (190,  50,  50),
    "berserker"     : (220,  40,  40),
    "paladin"       : (220, 180,  60),
    "monk"          : (200,  80,  60),
    "fighter"       : (190,  70,  50),
    "martial_saint" : (210, 140,  60),
    "chi_master"    : (200, 120,  50),
    # mage subclasses
    "wizard"        : ( 70,  70, 210),
    "warlock"       : (120,  50, 180),
    "elementalist"  : ( 50, 160, 200),
    "alchemist"     : (100, 170,  60),
    "bomber"        : (220, 140,  40),
    "transmuter"    : ( 60, 170, 160),
    # rogue subclasses
    "assassin"      : ( 50, 140,  60),
    "ranger"        : ( 70, 160,  80),
    "shadow"        : ( 60,  70,  90),
    # healer subclasses
    "priest"        : (230, 200, 100),
    "druid"         : ( 80, 180,  80),
    "oracle"        : (180, 140, 220),
    "herbalist"     : ( 80, 190, 100),
    # summoner subclasses
    "beastmaster"   : (140, 100, 180),
    "necromancer"   : ( 80,  50, 140),
    "spirit_caller" : (150, 100, 200),
}

print("\n--- Player sprites ----------------------------------------------------")
for cls, col in {**PLAYER_CLASSES, **PLAYER_SUBCLASSES}.items():
    path = os.path.join(_PLY_DIR, f"{cls}.png")
    if os.path.exists(path):
        print(f"  skip   assets/players/{cls}.png  (already exists)")
        continue
    surf = _make_surf(PLAYER_SIZE)
    cx = cy = PLAYER_SIZE // 2
    draw_fn = PLAYER_SPRITES.get(cls, PLAYER_SPRITES.get("warrior"))
    if draw_fn:
        try:
            draw_fn(surf, cx, cy, PLAYER_SIZE, tick=0)
        except Exception as e:
            print(f"  warn   {cls}: {e}")
    _save(surf, path, cls)

# ── Tile textures  (48 × 48, one per tile type) ───────────────────────────────
TILE_SIZE = 48

# Extra decoration colors — complement the base tile color
_TILE_DECO = {
    "grass"    : [(85, 160,  55), (45, 110, 45)],   # lighter + darker blades
    "forest"   : [(15,  60,  15), (40, 100, 20)],   # dark trunk + canopy
    "water"    : [(55, 100, 200), (200, 235, 255)],  # wave dark + foam
    "mountain" : [(140, 120, 95), (75, 68, 55)],     # highlight + shadow
    "sand"     : [(220, 200, 140), (170, 150, 95)],  # bright + shadowed
    "snow"     : [(240, 245, 255), (190, 200, 220)],
    "ice"      : [(200, 230, 250), (130, 180, 220)],
    "swamp"    : [(70, 100, 40), (40, 55, 25)],
    "lava"     : [(240, 100, 20), (255, 200, 50)],
    "volcanic" : [(130, 70, 45), (80, 40, 25)],
    "ruins"    : [(120, 110, 100), (65, 60, 55)],
    "crystal"  : [(155, 200, 240), (90, 130, 170)],
    "cloud"    : [(220, 225, 240), (170, 175, 200)],
    "path"     : [(175, 155, 110), (130, 115, 80)],
    "village"  : [(200, 165, 110), (145, 120, 80)],
    "wall"     : [(90, 85, 78), (50, 48, 44)],
    "cave"     : [(70, 64, 58), (38, 34, 30)],
    "bridge"   : [(130, 95, 50), (80, 58, 30)],
    "boss_lair": [(60, 48, 42), (30, 24, 20)],
    "jungle"   : [(30, 120, 20), (15, 75, 10)],
}


def _draw_tile(surf, tile_type, base_col, size):
    """Draw a simple but recognisable procedural tile texture."""
    import math, random
    rng = random.Random(hash(tile_type))   # deterministic noise
    r, g, b = base_col

    # --- solid base ---
    surf.fill(base_col)

    deco = _TILE_DECO.get(tile_type, [base_col])
    dc1  = deco[0] if len(deco) > 0 else base_col
    dc2  = deco[1] if len(deco) > 1 else dc1

    if tile_type == "grass":
        # scattered grass tufts
        for _ in range(12):
            x = rng.randint(2, size - 4)
            y = rng.randint(2, size - 4)
            h = rng.randint(4, 8)
            pygame.draw.line(surf, dc1, (x, y + h), (x, y), 1)
            pygame.draw.line(surf, dc2, (x + 1, y + h), (x - 1, y), 1)

    elif tile_type == "forest":
        # dark background + trunk + foliage circle
        surf.fill(dc2)
        tx, ty = size // 2, size // 2 + 6
        pygame.draw.rect(surf, (80, 50, 20), (tx - 3, ty, 6, size // 2 - ty + 4))
        pygame.draw.circle(surf, dc1, (tx, ty - 4), size // 4)

    elif tile_type == "water":
        # horizontal wave lines
        for row in range(0, size, 6):
            offset = 3 if (row // 6) % 2 else 0
            for x in range(offset, size, 8):
                pygame.draw.arc(surf, dc1, (x, row + 1, 6, 4), 0, math.pi, 2)
        # foam dots
        for _ in range(8):
            pygame.draw.circle(surf, dc2,
                               (rng.randint(2, size - 2), rng.randint(2, size - 2)), 1)

    elif tile_type == "mountain":
        # triangle peak
        pts = [(size // 2, 4), (4, size - 4), (size - 4, size - 4)]
        pygame.draw.polygon(surf, dc1, pts)
        pygame.draw.polygon(surf, dc2, pts, 2)
        # snow cap
        pygame.draw.polygon(surf, (240, 245, 255),
                            [(size // 2, 4), (size // 2 - 6, 14), (size // 2 + 6, 14)])

    elif tile_type in ("sand", "path", "village"):
        # subtle stipple
        for _ in range(20):
            px, py = rng.randint(0, size - 1), rng.randint(0, size - 1)
            shade  = rng.choice([dc1, dc2])
            surf.set_at((px, py), shade)

    elif tile_type in ("snow", "ice"):
        # cross sparkle pattern
        for _ in range(6):
            cx2 = rng.randint(4, size - 4)
            cy2 = rng.randint(4, size - 4)
            pygame.draw.line(surf, dc1, (cx2 - 3, cy2), (cx2 + 3, cy2), 1)
            pygame.draw.line(surf, dc1, (cx2, cy2 - 3), (cx2, cy2 + 3), 1)

    elif tile_type == "swamp":
        # murky puddles
        for _ in range(4):
            px, py = rng.randint(4, size - 8), rng.randint(4, size - 8)
            pygame.draw.ellipse(surf, dc1, (px, py, rng.randint(6, 12), 4))

    elif tile_type == "lava":
        # bright cracks
        for _ in range(5):
            x1 = rng.randint(0, size)
            y1 = rng.randint(0, size)
            x2 = x1 + rng.randint(-8, 8)
            y2 = y1 + rng.randint(-8, 8)
            pygame.draw.line(surf, dc2, (x1, y1), (x2, y2), 2)

    elif tile_type in ("volcanic", "cave", "boss_lair"):
        # dark cracks
        for _ in range(4):
            x1 = rng.randint(0, size)
            y1 = rng.randint(0, size)
            x2 = x1 + rng.randint(-6, 6)
            y2 = y1 + rng.randint(-6, 6)
            pygame.draw.line(surf, dc2, (x1, y1), (x2, y2), 1)

    elif tile_type == "ruins":
        # brick lines
        for row in range(0, size, 10):
            offset = 6 if (row // 10) % 2 else 0
            pygame.draw.line(surf, dc2, (0, row), (size, row), 1)
            for col_x in range(offset, size, 12):
                pygame.draw.line(surf, dc2, (col_x, row), (col_x, row + 10), 1)

    elif tile_type == "crystal":
        # diamond facets
        cx2, cy2 = size // 2, size // 2
        pts = [(cx2, 4), (size - 4, cy2), (cx2, size - 4), (4, cy2)]
        pygame.draw.polygon(surf, dc1, pts)
        pygame.draw.polygon(surf, dc2, pts, 1)
        pygame.draw.line(surf, dc2, pts[0], pts[2], 1)
        pygame.draw.line(surf, dc2, pts[1], pts[3], 1)

    elif tile_type == "cloud":
        # puffy circles
        for ox, oy, rr in [(-8, 2, 7), (0, -2, 9), (8, 2, 7), (0, 4, 6)]:
            pygame.draw.circle(surf, dc1, (size // 2 + ox, size // 2 + oy), rr)

    elif tile_type in ("wall",):
        # stone block grid
        for row in range(0, size, 12):
            offset = 6 if (row // 12) % 2 else 0
            pygame.draw.line(surf, dc2, (0, row), (size, row), 1)
            for col_x in range(offset, size, 12):
                pygame.draw.line(surf, dc2, (col_x, row), (col_x, row + 12), 1)

    elif tile_type == "bridge":
        # horizontal planks
        for row in range(0, size, 8):
            pygame.draw.rect(surf, dc2, (1, row + 1, size - 2, 6))
            pygame.draw.line(surf, dc1, (1, row), (size - 2, row), 1)

    elif tile_type == "jungle":
        # overlapping leaves
        surf.fill(dc2)
        for _ in range(8):
            lx = rng.randint(0, size)
            ly = rng.randint(0, size)
            pygame.draw.ellipse(surf, dc1, (lx - 8, ly - 4, 16, 8))

    # outline
    pygame.draw.rect(surf, dc2, (0, 0, size, size), 1)


print("\n--- Tile textures -----------------------------------------------------")
for tile_type, base_col in TILE_COL.items():
    path = os.path.join(_TILE_DIR, f"{tile_type}.png")
    if os.path.exists(path):
        print(f"  skip   assets/tiles/{tile_type}.png  (already exists)")
        continue
    surf = _make_surf(TILE_SIZE)
    _draw_tile(surf, tile_type, base_col, TILE_SIZE)
    _save(surf, path, tile_type)

print("\nDone!  Open the PNG files in any image editor to customise them.")
print("  Tip: delete a PNG to revert to the built-in procedural art.\n")
pygame.quit()
