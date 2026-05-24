import os

TITLE = "Legends of the Cursed Realm"
SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TILE = 48
# On Android (python-for-android) ANDROID_PRIVATE points to the app's
# writable internal storage — no permissions required.
_android_private = os.environ.get("ANDROID_PRIVATE", "")
if _android_private:
    SAVE_DIR = os.path.join(_android_private, "pixel_rpg_saves")
else:
    SAVE_DIR = os.path.join(os.path.expanduser("~"), "pixel_rpg_saves")

# ── Rarity ──────────────────────────────────────────────────────────────────
RARITIES = ["common", "uncommon", "rare", "epic", "legendary", "mythical"]
RARITY_COLORS = {
    "common":    (180, 180, 180),
    "uncommon":  (0,   210,  60),
    "rare":      (50,  120, 255),
    "epic":      (163,  53, 238),
    "legendary": (255, 140,   0),
    "mythical":  (220,  20,  60),
}
RARITY_WEIGHTS = {
    "common": 50, "uncommon": 25, "rare": 13, "epic": 7, "legendary": 3.5, "mythical": 1.5
}
RARITY_STAT_MULT = {
    "common": 1.0, "uncommon": 1.2, "rare": 1.5, "epic": 2.0, "legendary": 3.0, "mythical": 5.0
}

# ── Palette ──────────────────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GRAY  = ( 25,  25,  35)
MID_GRAY   = ( 60,  60,  80)
LIGHT_GRAY = (180, 180, 200)
RED        = (210,  50,  50)
DARK_RED   = (120,  20,  20)
GREEN      = ( 50, 200,  80)
DARK_GREEN = ( 20,  90,  30)
BLUE       = ( 50, 110, 220)
DARK_BLUE  = ( 20,  50, 150)
YELLOW     = (220, 210,  50)
ORANGE     = (230, 140,  40)
PURPLE     = (150,  50, 200)
CYAN       = ( 50, 210, 220)
GOLD       = (255, 200,  30)
PINK       = (230, 100, 170)

UI_BG        = ( 18,  18,  30)
UI_PANEL     = ( 32,  32,  52)
UI_BORDER    = ( 75,  75, 120)
UI_HIGHLIGHT = (100, 100, 180)
UI_TEXT      = (225, 225, 245)
UI_DIM       = (130, 130, 155)
HP_COL       = (210,  50,  50)
MP_COL       = ( 50, 110, 220)
EXP_COL      = (220, 200,  50)
STAMINA_COL  = ( 50, 200,  80)

# Biome tile draw colors
TILE_COL = {
    "grass":   ( 55, 130,  55),
    "forest":  ( 25,  85,  25),
    "water":   ( 35,  75, 175),
    "mountain":( 110,  95,  75),
    "sand":    ( 200, 180, 115),
    "snow":    ( 220, 230, 245),
    "ice":     ( 175, 210, 235),
    "swamp":   (  55,  75,  35),
    "lava":    ( 195,  75,  25),
    "volcanic":( 100,  55,  35),
    "ruins":   (  95,  85,  75),
    "crystal": ( 115, 160, 200),
    "cloud":   ( 195, 200, 220),
    "path":      ( 155, 135,  95),
    "village":   ( 175, 145,  95),
    "wall":      (  65,  60,  55),
    "cave":      (  50,  45,  40),
    # ── Special constructed tiles ────────────────────────────────────────
    "bridge":    ( 100,  70,  35),  # brown planks on minimap; water drawn in-game
    "boss_lair": (  40,  32,  28),  # dark flagstone floor
    "jungle":    (  15, 100,  15),  # dense tropical canopy
}

# ── Game constants ────────────────────────────────────────────────────────────
MAX_LEVEL          = 100
SUBCLASS_LEVEL        = 20
SUBCLASS_UNLOCK_LEVEL = 20
EXP_BASE           = 80
EXP_SCALE          = 1.45
ENCOUNTER_RATE     = 0.14      # per step on encounter tile
MAP_W, MAP_H       = 100, 80
SELL_MULT          = 0.4
MAX_INV_SLOTS      = 40
MAX_PET_LEVEL      = 60
PET_CAPTURE_BASE   = 0.25
MAX_STORED_PETS    = 30
ALPHA_CHANCE       = 0.06      # chance monster is Alpha
EVOLVED_CHANCE     = 0.04      # chance monster is Evolved variant
FAST_TRAVEL_COST   = 20        # gold per travel

# Class base stats  {hp, mp, atk, def, spd, int, lck}
CLASS_STATS = {
    "warrior":  {"hp":130,"mp": 30,"atk":16,"def":13,"spd": 8,"int": 4,"lck": 5},
    "mage":     {"hp": 60,"mp":130,"atk": 7,"def": 4,"spd": 8,"int":22,"lck": 7},
    "rogue":    {"hp": 80,"mp": 55,"atk":15,"def": 7,"spd":20,"int": 7,"lck":12},
    "healer":   {"hp": 85,"mp":110,"atk": 7,"def": 9,"spd":10,"int":16,"lck": 8},
    "summoner":  {"hp": 70,"mp":100,"atk": 9,"def": 6,"spd": 9,"int":17,"lck":10},
    "monk":      {"hp": 90,"mp": 60,"atk":13,"def":10,"spd":18,"int": 8,"lck": 8},
    "alchemist": {"hp": 75,"mp": 90,"atk":10,"def": 8,"spd":11,"int":18,"lck":10},
}
CLASS_GROWTH = {
    "warrior":   {"hp":14,"mp":2, "atk":2.0,"def":1.8,"spd":0.4,"int":0.2,"lck":0.3},
    "mage":      {"hp": 5,"mp":13,"atk":0.4,"def":0.4,"spd":0.5,"int":3.2,"lck":0.4},
    "rogue":     {"hp": 8,"mp":4, "atk":1.6,"def":0.7,"spd":2.1,"int":0.4,"lck":1.3},
    "healer":    {"hp": 8,"mp":11,"atk":0.4,"def":0.9,"spd":0.8,"int":2.1,"lck":0.7},
    "summoner":  {"hp": 7,"mp":10,"atk":0.8,"def":0.6,"spd":0.7,"int":2.2,"lck":1.0},
    "monk":      {"hp": 9,"mp":5, "atk":1.4,"def":1.2,"spd":2.0,"int":0.5,"lck":0.6},
    "alchemist": {"hp": 7,"mp":9, "atk":0.6,"def":0.7,"spd":0.8,"int":2.4,"lck":0.8},
}
