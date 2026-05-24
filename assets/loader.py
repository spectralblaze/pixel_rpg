"""Asset loader — drop PNG files in assets/monsters/, assets/tiles/, or
assets/players/ and the game will use them automatically.  Missing files
fall back to the built-in procedural pixel-art drawing.

Recommended sizes
-----------------
  assets/monsters/{name}.png   96 × 96  (can be larger — will be scaled down)
  assets/players/{class}.png   80 × 80
  assets/tiles/{type}.png      48 × 48  (exactly one tile)

File naming
-----------
  Monster sprites:  use the sprite-type name (slime, goblin, dragon …) OR
                    the exact monster_id (green_slime, golem_king …).
                    The exact ID takes priority.
  Player sprites:   use the class name (warrior, mage, rogue, healer, summoner)
                    OR the exact subclass name (berserker, assassin …).
                    The exact subclass takes priority.
  Tile textures:    use the tile type exactly as defined in TILE_COL
                    (grass, forest, water, sand, boss_lair …).

Run  python tools/export_sprites.py  to generate starter PNG files you can
edit in any image editor (Aseprite, GIMP, Paint.NET …).
"""
import os
import pygame

_DIR          = os.path.dirname(os.path.abspath(__file__))
_MONSTERS_DIR = os.path.join(_DIR, "monsters")
_PLAYERS_DIR  = os.path.join(_DIR, "players")
_TILES_DIR    = os.path.join(_DIR, "tiles")

# Raw image cache:   path  → Surface | None
_raw: dict = {}
# Scaled image cache: (path, size) → Surface | None
_scaled: dict = {}


def _raw_load(path: str):
    """Load and cache a PNG.  Returns None if missing or broken."""
    if path not in _raw:
        if os.path.isfile(path):
            try:
                _raw[path] = pygame.image.load(path).convert_alpha()
            except Exception:
                _raw[path] = None
        else:
            _raw[path] = None
    return _raw[path]


def _get(path: str, size: int):
    """Return image scaled to size×size pixels, or None."""
    key = (path, size)
    if key not in _scaled:
        img = _raw_load(path)
        _scaled[key] = (pygame.transform.scale(img, (size, size))
                        if img is not None else None)
    return _scaled[key]


# ── Monster sprite-type groups (mirrors ui/sprites.py) ───────────────────────
_MONSTER_TYPE: dict[str, str] = {}
for _t, _ids in {
    "slime":    {"green_slime","blue_slime","forest_slime","sand_slime",
                 "ice_slime","fire_slime","poison_slime","shadow_slime",
                 "crystal_slime","storm_slime","lava_slime","blizzard_slime",
                 "magma_slime","giant_frog","plague_frog"},
    "wolf":     {"prairie_wolf","alpha_wolf","snow_wolf","dire_frost_wolf"},
    "rat":      {"field_rat","giant_rat","dire_rat"},
    "goblin":   {"goblin_scout","goblin_warrior","goblin_shaman"},
    "skeleton": {"skeleton_archer","skeleton_knight","skeleton_king",
                 "death_knight","plague_bearer","lich_commander","cursed_knight"},
    "ghost":    {"ghost","specter","shadow_wraith"},
    "elemental":{"ice_elemental","blizzard_elemental","fire_elemental",
                 "prism_elemental","storm_elemental","chaos_elemental",
                 "void_elemental"},
    "dragon":   {"fire_drake","ember_dragon","frost_dragon","gem_dragon",
                 "volcanic_dragon_lord","aldrath_king_of_dragons",
                 "wind_serpent","thunder_serpent","thunder_roc"},
    "golem":    {"golem_king","magma_golem","crystal_golem","prism_golem",
                 "ancient_treant","tree_spirit","dark_ent"},
    "bee":      {"giant_bee","queen_bee"},
    "serpent":  {"sand_cobra","sand_king_cobra","swamp_serpent_lord",
                 "crystal_hydra","jungle_serpent_god"},
    "bat":      {"cave_bat","vampire_bat"},
    "mummy":    {"mummy","ancient_mummy"},
    "scorpion": {"desert_scorpion","emperor_scorpion"},
    "witch":    {"bog_witch","grand_witch"},
    "troll":    {"frost_troll","ice_giant","storm_giant","troll","yeti"},
    "harpy":    {"harpy","storm_harpy"},
    "djinn":    {"desert_djinn"},
}.items():
    for _id in _ids:
        _MONSTER_TYPE[_id] = _t

# ── Player base-class map ─────────────────────────────────────────────────────
_PLAYER_BASE: dict[str, str] = {
    "knight":       "warrior",  "berserker":   "warrior",
    "paladin":      "healer",
    "wizard":       "mage",     "warlock":     "mage",
    "elementalist": "mage",
    "assassin":     "rogue",    "ranger":      "rogue",    "shadow":    "rogue",
    "priest":       "healer",   "druid":       "healer",   "oracle":    "healer",
    "beastmaster":  "summoner", "necromancer": "summoner",
    "spirit_caller":"summoner",
    "monk":         "warrior",  "fighter":     "warrior",
    "martial_saint":"warrior",  "chi_master":  "warrior",
    "alchemist":    "mage",     "bomber":      "mage",
    "herbalist":    "healer",   "transmuter":  "mage",
}


# ── Public API ────────────────────────────────────────────────────────────────

def get_monster_img(monster_id: str, size: int):
    """Return a scaled Surface for this monster, or None (use procedural)."""
    for name in (monster_id, _MONSTER_TYPE.get(monster_id, "")):
        if not name:
            continue
        img = _get(os.path.join(_MONSTERS_DIR, f"{name}.png"), size)
        if img is not None:
            return img
    return None


def get_player_img(cls: str, size: int):
    """Return a scaled Surface for this player class, or None (use procedural)."""
    for name in (cls, _PLAYER_BASE.get(cls, "")):
        if not name:
            continue
        img = _get(os.path.join(_PLAYERS_DIR, f"{name}.png"), size)
        if img is not None:
            return img
    return None


def get_tile_img(tile_type: str, size: int = 48):
    """Return a scaled Surface for this tile type, or None (use procedural)."""
    return _get(os.path.join(_TILES_DIR, f"{tile_type}.png"), size)


def invalidate_cache():
    """Clear all cached images.  Call after hot-swapping PNG files."""
    _raw.clear()
    _scaled.clear()
