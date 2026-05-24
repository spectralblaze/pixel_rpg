"""Retro 8-bit pixel-art sprites for all player classes and monsters.
All drawing is pure pygame.draw — no image files.
draw_*(surf, cx, cy, size, tick) — cx/cy is the sprite CENTER.
"""
import pygame, math, random as _rng

# ── Shared palette ─────────────────────────────────────────────────────────────
_K = (  0,   0,   0)   # black outline
_W = (255, 255, 255)
_SK= (240, 195, 145)   # skin
_SD= (190, 140,  90)   # skin dark
_GD= (255, 200,  40)   # gold
_SV= (200, 215, 225)   # silver
_RD= (210,  40,  40)
_BL= (50,  100, 210)
_GR= ( 40, 180,  60)
_PU= (160,  50, 210)
_CY= ( 50, 210, 210)
_YL= (230, 210,  50)
_BR= (130,  80,  30)
_BO= (220, 210, 185)   # bone


# ── Low-level helpers ──────────────────────────────────────────────────────────
def _r(s, c, x, y, w, h):
    if c is None or w <= 0 or h <= 0: return
    pygame.draw.rect(s, c, (int(x), int(y), int(max(1,w)), int(max(1,h))))

def _dim(c, f=0.55):  return tuple(int(v*f) for v in c)
def _lit(c, f=1.35):  return tuple(min(255, int(v*f)) for v in c)


# ── Pixel-art core ─────────────────────────────────────────────────────────────
def _px(surf, col, gx, gy, gw, gh, p, ox, oy):
    """Draw a block of 'pixels' on an 8-bit grid."""
    if col is None or gw <= 0 or gh <= 0: return
    _r(surf, col, ox + gx*p, oy + gy*p, gw*p, gh*p)

def _sprite(surf, cx, cy, size, rows):
    """rows = list of (col, gx, gy, gw, gh) — grid is 0..15 in each axis.
    size is the full sprite size in screen pixels; 1 grid unit = size//16."""
    p  = max(1, size // 16)
    ox = cx - 8 * p
    oy = cy - 8 * p
    for col, gx, gy, gw, gh in rows:
        _px(surf, col, gx, gy, gw, gh, p, ox, oy)


# ══════════════════════════════════════════════════════════════════════════════
# PLAYER SPRITES
# ══════════════════════════════════════════════════════════════════════════════

def draw_warrior(surf, cx, cy, size, tick=0):
    _C = (90, 100, 120)   # blue-steel armour
    _L = (120, 130, 150)  # light armour
    _R = (180,  40,  40)  # red shield
    blink = (tick // 600) % 2 == 0
    _sprite(surf, cx, cy, size, [
        # sword (right of body)
        (_SV,  13, 1,  1, 6),  # blade
        (_GD,  12, 6,  3, 1),  # guard
        # shield (left of body)
        (_R,    1, 4,  3, 5),
        (_GD,   1, 6,  3, 1),
        # helmet
        (_K,    4, 0,  8, 1),
        (_C,    4, 1,  8, 3),
        (_L,    5, 1,  6, 2),  # shine
        (_K,    5, 3,  6, 1),  # visor shadow
        # head
        (_SK,   5, 4,  6, 2),
        # body / plate
        (_K,    4, 6, 8, 1),
        (_C,    4, 7,  8, 4),
        (_L,    5, 7,  6, 2),
        (_K,    5, 9,  6, 1),
        # pauldrons
        (_L,    3, 6,  2, 2),
        (_L,   11, 6,  2, 2),
        # legs
        (_C,    5,11,  3, 4),
        (_C,    8,11,  3, 4),
        (_K,    5,15,  3, 1),
        (_K,    8,15,  3, 1),
        # eyes in visor
        ((_BL if blink else _K), 5, 4, 2, 1),
        ((_BL if blink else _K), 9, 4, 2, 1),
    ])

def draw_mage(surf, cx, cy, size, tick=0):
    gl = int(130 + 80 * math.sin(tick * 0.004))
    _OB = (gl, gl, 255)
    _HA = (50, 50, 150)   # hat
    _RO = (70, 70, 190)   # robe
    _sprite(surf, cx, cy, size, [
        # staff
        (_BR,  13, 0,  2,14),
        ((_OB), 13,0,  2, 1),
        ((_OB), 12,0,  4, 1),
        # hat brim
        (_HA,   3,3,  10, 2),
        # hat cone
        (_HA,   6, 0,  4, 3),
        (_GD,   7, 0,  2, 1),  # star tip
        # head
        (_SK,   5, 5,  6, 3),
        (_SD,   5, 7,  6, 1),  # beard
        # eyes
        (_OB,   6, 5,  1, 1),
        (_OB,  10, 5,  1, 1),
        # robe body
        (_RO,   4, 8, 8, 5),
        (_K,    4, 8,  1, 5),
        (_K,   11, 8,  1, 5),
        (_GD,   4,12,  8, 1),  # trim
        # robe stars
        (_OB,   6, 9,  1, 1),
        (_OB,   9,10,  1, 1),
        # sleeves
        (_RO,   2, 8,  3, 3),
        (_RO,  11, 8,  3, 3),
        # legs (robe hem)
        (_dim(_RO), 5,13, 3, 3),
        (_dim(_RO), 8,13, 3, 3),
    ])

def draw_rogue(surf, cx, cy, size, tick=0):
    _CL = (35, 30, 50)    # dark cloak
    _LT = (55, 45, 70)    # lighter leather
    _EY = (190, 80, 255)
    _sprite(surf, cx, cy, size, [
        # left dagger
        (_SV,   1, 5,  1, 6),
        (_BR,   1, 4,  1, 2),
        # right dagger
        (_SV,  14, 5,  1, 6),
        (_BR,  14, 4,  1, 2),
        # cloak back
        (_dim(_CL), 3, 8, 10, 8),
        # body
        (_CL,   4, 6, 8, 6),
        (_LT,   5, 7, 6, 4),
        # belt
        (_BR,   4,10, 8, 1),
        (_GD,   7,10, 2, 1),
        # hood
        (_CL,   4, 2, 8, 4),
        (_CL,   5, 1, 6, 2),
        (_CL,   6, 0, 4, 1),
        # face (in shadow)
        (_dim(_SK), 5, 4, 6, 2),
        # eyes
        (_EY,   6, 4, 1, 1),
        (_EY,  10, 4, 1, 1),
        # legs
        (_CL,   5,12, 3, 4),
        (_CL,   8,12, 3, 4),
    ])

def draw_healer(surf, cx, cy, size, tick=0):
    gl  = int(170 + 60 * math.sin(tick * 0.003))
    _HG = (gl, gl, 100)   # holy glow tint
    _RB = (230, 230, 245)  # white robe
    _sprite(surf, cx, cy, size, [
        # aura glow dots (corners)
        (_HG,   2, 2,  2, 2),
        (_HG,  12, 2,  2, 2),
        (_HG,   2,12,  2, 2),
        (_HG,  12,12,  2, 2),
        # staff
        (_BR,  13, 1,  2,13),
        (_HG,  12, 0,  4, 2),  # orb
        (_W,   13, 0,  2, 1),
        # hair
        (_GD,   4, 2, 8, 2),
        (_GD,   3, 4, 2, 3),
        (_GD,  11, 4, 2, 3),
        # head
        (_SK,   5, 4, 6, 4),
        # eyes
        (_GR,   6, 5, 1, 1),
        (_GR,  10, 5, 1, 1),
        # robe
        (_RB,   4, 8, 8, 5),
        # cross emblem
        (_RD,   7, 9, 2, 4),
        (_RD,   6,11, 4, 1),
        # sleeves
        (_RB,   2, 8, 3, 4),
        (_RB,  11, 8, 3, 4),
        # hem
        (_RB,   3,13, 10, 3),
        # robe outline
        (_K,    4, 8,  1, 5),
        (_K,   11, 8,  1, 5),
    ])

def draw_summoner(surf, cx, cy, size, tick=0):
    gl  = int(140 + 80 * math.sin(tick * 0.005))
    _OR = (gl, 50, 240)   # orb glow
    _RO = (75, 30, 110)   # deep purple robe
    # Orbiting familiar positions
    for i in range(3):
        ang = tick * 0.003 + i * 2.094
        p  = max(1, size // 16)
        ox = cx + int(math.cos(ang) * 9 * p)
        oy = cy + int(math.sin(ang) * 6 * p) - 2*p
        _r(surf, _OR, ox - p, oy - p, 3*p, 3*p)
        _r(surf, _W,  ox,     oy,     p,   p)
    _sprite(surf, cx, cy, size, [
        # staff
        (_dim(_RO), 13, 1, 2,14),
        (_OR,       12, 0, 4, 2),
        (_W,        13, 0, 2, 1),
        # rune dots on robe
        (_OR,  6, 9,  1, 1),
        (_OR, 10, 9,  1, 1),
        (_OR,  8,11,  1, 1),
        # hood
        (_RO,  5, 1,  6, 2),
        (_RO,  4, 3,  8, 2),
        # face
        (_SK,  5, 5,  6, 3),
        # glowing eyes
        (_OR,  6, 5,  1, 1),
        (_OR, 10, 5,  1, 1),
        # robe body
        (_RO,  4, 7,  8, 6),
        (_dim(_RO), 4, 7, 1, 6),
        (_dim(_RO),11, 7, 1, 6),
        # rune stripe
        (_lit(_RO), 4,12, 8, 1),
        # legs
        (_RO,  5,13,  3, 3),
        (_RO,  8,13,  3, 3),
    ])


PLAYER_SPRITES = {
    "warrior":      draw_warrior,
    "knight":       draw_warrior,
    "berserker":    draw_warrior,
    "paladin":      draw_healer,
    "mage":         draw_mage,
    "wizard":       draw_mage,
    "warlock":      draw_mage,
    "elementalist": draw_mage,
    "rogue":        draw_rogue,
    "assassin":     draw_rogue,
    "ranger":       draw_rogue,
    "shadow":       draw_rogue,
    "healer":       draw_healer,
    "priest":       draw_healer,
    "druid":        draw_healer,
    "oracle":       draw_healer,
    "summoner":     draw_summoner,
    "beastmaster":  draw_summoner,
    "necromancer":  draw_summoner,
    "spirit_caller":draw_summoner,
    # Monk uses warrior body; Alchemist uses mage body
    "monk":         draw_warrior,
    "fighter":      draw_warrior,
    "martial_saint":draw_warrior,
    "chi_master":   draw_warrior,
    "alchemist":    draw_mage,
    "bomber":       draw_mage,
    "herbalist":    draw_healer,
    "transmuter":   draw_mage,
}

def draw_player_sprite(surf, cls: str, cx, cy, size, tick=0):
    # PNG override: use image file if one exists in assets/players/
    try:
        from assets.loader import get_player_img
        img = get_player_img(cls, size)
        if img is not None:
            surf.blit(img, (cx - size // 2, cy - size // 2))
            return
    except Exception:
        pass
    PLAYER_SPRITES.get(cls, draw_warrior)(surf, cx, cy, size, tick)


def draw_player_in_boat(surf, cls: str, cx, cy, size, tick=0):
    """Draw the player character seated in a small wooden boat.

    The player's upper body is visible above the hull; a gentle sine-wave bob
    animates the boat rocking on the water.
    """
    bob = int(math.sin(tick * 0.003) * 2)   # gentle water bob (pixels)
    p   = max(1, size // 16)

    # Player drawn slightly higher so their legs are hidden inside the hull
    PLAYER_SPRITES.get(cls, draw_warrior)(surf, cx, cy - 3*p + bob, size, tick)

    # ── Boat hull (drawn on top to cover player's lower half) ─────────────────
    _BW = (145,  92, 38)   # main plank wood
    _BD = ( 90,  50, 15)   # dark outline / shadow
    _BL = (190, 140, 72)   # light highlight plank
    ox  = cx - 8*p
    by0 = cy        + bob  # hull top interior  (row 8 equivalent)

    # Gunwale highlight — thin strip just above hull top
    _r(surf, _BL, ox + p,   by0 - p,    14*p, p)
    # Top edge outline
    _r(surf, _BD, ox,        by0,        16*p, p)
    # Port / starboard side walls
    _r(surf, _BD, ox,        by0,        p,    5*p)
    _r(surf, _BD, ox + 15*p, by0,        p,    5*p)
    # Hull interior floor (covers player legs)
    _r(surf, _BW, ox + p,   by0,        14*p, 5*p)
    # Plank seam lines inside hull
    _r(surf, _BD, ox + 2*p, by0 + p,    12*p, p)
    _r(surf, _BD, ox + 2*p, by0 + 3*p,  12*p, p)
    # Hull bottom edge + keel taper
    _r(surf, _BD, ox,        by0 + 5*p,  16*p, p)
    _r(surf, _BD, ox + p,    by0 + 6*p,  14*p, p)
    _r(surf, _BD, ox + 2*p,  by0 + 7*p,  12*p, p)


# ══════════════════════════════════════════════════════════════════════════════
# MONSTER SPRITES
# ══════════════════════════════════════════════════════════════════════════════

def draw_slime(surf, cx, cy, size, col, tick=0):
    wb = int(math.sin(tick * 0.006) * 1.5)  # wobble offset in grid units
    D  = _dim(col)
    L  = _lit(col)
    _sprite(surf, cx, cy, size, [
        # shadow
        (D,      4,14, 8, 1),
        # body blob
        (col,    3, 7, 10, 6),
        (col,    4, 5,  8, 2),
        (col,    5, 4,  6, 1),
        # highlight
        (L,      5, 5,  3, 2),
        # eyes
        (_W,     4, 8,  3, 3),
        (_W,     9, 8,  3, 3),
        (_K,     5, 9,  2, 2),
        (_K,    10, 9,  2, 2),
        # pupils
        (_BL,    5, 9,  1, 1),
        (_BL,   10, 9,  1, 1),
        # smile
        (D,      5,12,  1, 1),
        (D,      6,13,  4, 1),
        (D,     10,12,  1, 1),
    ])

def draw_rat(surf, cx, cy, size, col, tick=0):
    sc = int(math.sin(tick * 0.012)) & 1  # scurry frame
    D  = _dim(col)
    _sprite(surf, cx, cy, size, [
        # tail (curved)
        (D,     12,10, 3, 1),
        (D,     13, 9, 2, 1),
        (D,     14, 8, 1, 2),
        # legs (drawn first)
        (D,      4,10, 2, 3+sc),
        (D,      7,10, 2, 3+sc),
        (D,     10,10, 2, 3+sc),
        # body
        (col,    3, 7, 10, 5),
        (col,    4, 6,  8, 1),
        # head
        (col,    1, 6,  5, 4),
        # snout
        (D,      0, 7,  2, 2),
        # nose
        (_RD,    0, 7,  1, 1),
        # eye
        (_RD,    2, 6,  2, 2),
        (_K,     2, 6,  1, 1),
        # ear
        (_lit(col), 4, 4, 2, 2),
        (_dim(col, 0.4), 4, 4, 1, 1),
        # outline
        (_K,     3, 7,  1, 5),
        (_K,    12, 7,  1, 5),
    ])

def draw_wolf(surf, cx, cy, size, col, tick=0):
    fr = (tick // 180) % 2  # walk frame
    D  = _dim(col)
    L  = _lit(col)
    _sprite(surf, cx, cy, size, [
        # tail
        (D,     11, 4,  2, 3),
        (D,     13, 3,  2, 2),
        # legs (front/back, frame alternates)
        (D,      3,10,  2, 4+fr),
        (D,      6,10,  2, 4+(1-fr)),
        (D,      9,10,  2, 4+(1-fr)),
        (D,     12,10,  2, 4+fr),
        # body
        (col,    2, 6, 12, 6),
        (L,      3, 6,  6, 3),
        # head
        (col,    0, 4,  6, 5),
        (L,      1, 4,  3, 2),
        # snout
        (D,      0, 7,  3, 2),
        (_K,     0, 8,  1, 1),  # nose
        # eye
        (_YL,    2, 5,  2, 2),
        (_K,     2, 5,  1, 1),
        # ear
        (col,    2, 2,  2, 3),
        (col,    4, 2,  2, 3),
        # outline
        (_K,     2, 6,  1, 6),
        (_K,    13, 6,  1, 6),
    ])

def draw_goblin(surf, cx, cy, size, col, tick=0):
    D = _dim(col)
    L = _lit(col)
    _sprite(surf, cx, cy, size, [
        # weapon
        (_BR,   12, 2,  2, 8),
        (_SV,   11, 2,  4, 3),
        # legs
        (D,      5,11,  3, 5),
        (D,      8,11,  3, 5),
        # body
        (col,    4, 7,  8, 5),
        (L,      5, 7,  6, 3),
        # loincloth
        (D,      5,11,  6, 2),
        # head (big)
        (col,    3, 2,  10, 6),
        (L,      4, 2,   8, 3),
        # ears
        (L,      1, 3,  3, 3),
        (L,     12, 3,  3, 3),
        (_RD,    2, 3,  1, 2),
        (_RD,   13, 3,  1, 2),
        # eyes
        (_RD,    5, 4,  2, 2),
        (_RD,    9, 4,  2, 2),
        (_K,     5, 4,  1, 1),
        (_K,     9, 4,  1, 1),
        # nose
        (D,      7, 6,  2, 1),
        # outline
        (_K,     3, 2,  1, 6),
        (_K,    12, 2,  1, 6),
        (_K,     4, 7,  1, 5),
        (_K,    11, 7,  1, 5),
    ])

def draw_skeleton(surf, cx, cy, size, col, tick=0):
    rt = (tick // 250) % 2  # rattle frame
    _sprite(surf, cx, cy, size, [
        # sword
        (_SV,   13, 1,  1, 7),
        (_BR,   12, 7,  3, 1),
        # legs
        (_BO,   5,11,  2, 5),
        (_BO,   9,11,  2, 5),
        # feet
        (_BO,   4,15,  4, 1),
        (_BO,   8,15,  4, 1),
        # pelvis
        (_BO,   4,10,  8, 2),
        # spine
        (_BO,   7, 5,  2,6),
        # ribs
        (_BO,   4, 5,  3, 1),
        (_BO,   4, 7,  3, 1),
        (_BO,   4, 9,  3, 1),
        (_BO,   9, 5,  3, 1),
        (_BO,   9, 7,  3, 1),
        (_BO,   9, 9,  3, 1),
        # arms (rattle)
        (_BO,   2, 4+rt, 3, 7),
        (_BO,  11, 4-rt, 3, 7),
        # skull
        (_BO,   4, 0,  8, 5),
        (_K,    5, 0,  6, 4),   # shadow socket area
        (_BO,   4, 0,  8, 5),
        # eye sockets
        (_K,    5, 1,  2, 2),
        (_K,    9, 1,  2, 2),
        (_RD,   5, 1,  2, 2),
        (_RD,   9, 1,  2, 2),
        # jaw
        (_BO,   4, 4,  8, 2),
        (_W,    5, 5,  1, 1),
        (_W,    7, 5,  1, 1),
        (_W,    9, 5,  1, 1),
    ])

def draw_ghost(surf, cx, cy, size, col, tick=0):
    dr = int(math.sin(tick * 0.004) * 2)   # drift (grid units, roughly)
    L  = _lit(col)
    D  = _dim(col, 0.5)
    _sprite(surf, cx, cy, size, [
        # wispy tail
        (D,      4,12+dr%2, 2, 3),
        (D,      8,13+dr%2, 2, 2),
        (D,     10,12+dr%2, 2, 3),
        # body
        (col,    3, 5,  10, 8),
        (col,    4, 3,   8, 2),
        (L,      4, 4,   8, 4),
        # arms
        (col,    1, 7,  3, 3),
        (col,   12, 7,  3, 3),
        # eyes (hollow)
        (_K,     5, 6,  2, 2),
        (_K,     9, 6,  2, 2),
        (_CY,    5, 6,  2, 2),
        (_CY,    9, 6,  2, 2),
        # wail mouth
        (_K,     6, 9,  4, 2),
    ])

def draw_elemental(surf, cx, cy, size, col, tick=0):
    pulse = int(1 + math.sin(tick * 0.006) * 1.5)
    L = _lit(col)
    D = _dim(col, 0.4)
    # Orbiting particles
    for i in range(6):
        ang = tick * 0.005 + i * 1.047
        p  = max(1, size // 16)
        ox = cx + int(math.cos(ang) * 7 * p)
        oy = cy + int(math.sin(ang) * 7 * p)
        _r(surf, L, ox - p, oy - p, 2*p+pulse, 2*p+pulse)
    _sprite(surf, cx, cy, size, [
        # outer glow
        (D,      2, 2, 12,12),
        # core
        (col,    3, 3, 10,10),
        (L,      5, 5,  6, 6),
        (_W,     7, 7,  2, 2),
        # eyes
        (_W,     5, 5,  2, 2),
        (_W,     9, 5,  2, 2),
        (col,    5, 5,  1, 1),
        (col,    9, 5,  1, 1),
    ])

def draw_dragon(surf, cx, cy, size, col, tick=0):
    fl = (tick // 200) % 2   # flap frame
    D  = _dim(col)
    L  = _lit(col)
    _sprite(surf, cx, cy, size, [
        # tail
        (D,     12, 9,  3, 2),
        (D,     13,11,  2, 2),
        (D,     14,12,  1, 2),
        # wing left
        (D,      0, 0,  5, 3+fl),
        (D,      1, 3,  4, 2),
        # wing right
        (D,     11, 0,  5, 3+fl),
        (D,     11, 3,  4, 2),
        # body
        (col,    3, 6, 10, 6),
        (L,      4, 6,  8, 3),
        # neck
        (col,    3, 3,  4, 4),
        # head
        (col,    1, 1,  6, 4),
        (L,      2, 1,  4, 2),
        # snout
        (D,      0, 3,  3, 2),
        (_K,     0, 3,  1, 1),  # nostril
        # eye
        (_YL,    3, 2,  2, 2),
        (_K,     3, 2,  1, 1),
        # horn
        (D,      4, 0,  1, 2),
        (D,      6, 0,  1, 2),
        # legs
        (D,      4,11,  3, 4),
        (D,      9,11,  3, 4),
        # claws
        (D,      3,14,  2, 1),
        (D,      5,14,  2, 1),
        (D,      8,14,  2, 1),
        (D,     10,14,  2, 1),
        # outline
        (_K,     3, 6,  1, 6),
        (_K,    12, 6,  1, 6),
    ])

def draw_golem(surf, cx, cy, size, col, tick=0):
    gw = int(160 + 70 * math.sin(tick * 0.004))
    EY = (gw, gw//2, 0)
    D  = _dim(col)
    L  = _lit(col)
    _sprite(surf, cx, cy, size, [
        # feet
        (D,      3,14,  4, 2),
        (D,      9,14,  4, 2),
        # legs
        (col,    4,10,  3, 5),
        (col,    9,10,  3, 5),
        # body
        (col,    3, 4, 10,7),
        (L,      4, 4,  8, 4),
        # arms
        (D,      0, 5,  4, 6),
        (D,     12, 5,  4, 6),
        # fists
        (col,    0, 9,  4, 4),
        (col,   12, 9,  4, 4),
        # head
        (col,    3, 0, 10, 5),
        (L,      4, 0,  8, 3),
        # cracks
        (D,      6, 1,  1, 4),
        (D,      9, 2,  1, 3),
        # eyes
        (EY,     5, 1,  2, 2),
        (EY,     9, 1,  2, 2),
        (_YL,    5, 1,  1, 1),
        (_YL,    9, 1,  1, 1),
        # outline
        (_K,     3, 0,  1, 5),
        (_K,    12, 0,  1, 5),
        (_K,     3, 4,  1, 7),
        (_K,    12, 4,  1, 7),
    ])

def draw_bee(surf, cx, cy, size, col, tick=0):
    bz = (tick // 60) % 2   # buzz frame
    WN = (180, 225, 255)
    _sprite(surf, cx, cy, size, [
        # wings (fast flap)
        (WN,     1, 2-bz, 5, 3),
        (WN,    10, 2+bz, 5, 3),
        # stinger
        (_K,     7,14,  2, 2),
        # body (striped)
        (col,    4, 7, 8, 7),
        (_K,     4, 8, 8, 1),
        (_K,     4,10, 8, 1),
        (_K,     4,12, 8, 1),
        (col,    4, 9, 8, 1),
        (col,    4,11, 8, 1),
        (_YL,    4, 7, 8, 1),
        (_YL,    4, 9, 8, 1),
        (_YL,    4,11, 8, 1),
        # head
        (col,    5, 3, 6, 4),
        # compound eyes
        ((80,200,80), 5, 3, 2, 2),
        ((80,200,80), 9, 3, 2, 2),
        # antennae
        (_K,     6, 1, 1, 2),
        (_K,     9, 1, 1, 2),
        (_YL,    5, 0, 2, 1),
        (_YL,    9, 0, 2, 1),
    ])

def draw_serpent(surf, cx, cy, size, col, tick=0):
    sv = (tick // 150) % 3   # slither frame
    D  = _dim(col)
    L  = _lit(col)
    _sprite(surf, cx, cy, size, [
        # coiled body segments
        (col,    2+sv, 8, 12, 3),
        (col,    3,   11,  10, 2),
        (D,      4,   13,   8, 2),
        (L,      3+sv, 8,   6, 2),
        # head
        (col,    3, 3,  6, 5),
        (L,      4, 3,  4, 3),
        # snout
        (D,      1, 5,  3, 2),
        # tongue
        (_RD,    1, 7,  1, 2),
        (_RD,    0, 8,  1, 1),
        (_RD,    2, 8,  1, 1),
        # eyes
        (_YL,    4, 4,  2, 2),
        (_K,     4, 4,  1, 1),
        # outline
        (_K,     3, 3,  1, 5),
        (_K,     8, 3,  1, 5),
    ])

def draw_bat(surf, cx, cy, size, col, tick=0):
    fl = (tick // 120) % 2
    D  = _dim(col)
    _sprite(surf, cx, cy, size, [
        # left wing
        (col,    0, 4-fl, 5, 4+fl),
        (D,      1, 8,   4, 2),
        # right wing
        (col,   11, 4+fl, 5, 4-fl),
        (D,     11, 8,   4, 2),
        # body
        (D,      5, 7,  6, 5),
        # head
        (col,    4, 3,  8, 5),
        # ears
        (col,    4, 0,  2, 4),
        (col,   10, 0,  2, 4),
        # eyes
        (_RD,    5, 5,  2, 2),
        (_RD,    9, 5,  2, 2),
        (_K,     5, 5,  1, 1),
        (_K,     9, 5,  1, 1),
        # fangs
        (_W,     6, 7,  1, 2),
        (_W,     9, 7,  1, 2),
    ])

def draw_mummy(surf, cx, cy, size, col, tick=0):
    gw = int(130 + 80 * math.sin(tick * 0.005))
    EY = (gw, gw//2, 0)
    L  = _lit(col)
    _sprite(surf, cx, cy, size, [
        # legs
        (col,    5,11,  3, 5),
        (col,    8,11,  3, 5),
        # bandage strips on legs
        (_dim(col,0.7), 4,12, 8, 1),
        (_dim(col,0.7), 4,14, 8, 1),
        # body
        (col,    4, 5, 8, 7),
        # chest bandages
        (L,      3, 6, 10, 1),
        (L,      3, 8, 10, 1),
        (L,      3,10, 10, 1),
        # arms (outstretched)
        (col,    1, 6, 4, 4),
        (col,   11, 6, 4, 4),
        # head
        (col,    4, 0, 8, 6),
        # head bandages
        (L,      3, 1, 10, 1),
        (L,      3, 3, 10, 1),
        (L,      3, 5, 10, 1),
        # eyes
        (EY,     5, 2,  2, 2),
        (EY,     9, 2,  2, 2),
        # outline
        (_K,     4, 0,  1, 6),
        (_K,    11, 0,  1, 6),
    ])

def draw_scorpion(surf, cx, cy, size, col, tick=0):
    D  = _dim(col)
    L  = _lit(col)
    # tail segments (curved up)
    p = max(1, size // 16)
    ox, oy = cx - 8*p, cy - 8*p
    for i in range(4):
        tx2 = int(ox + (10 + i) * p)
        ty2 = int(oy + (6 - i * 2) * p)
        _r(surf, D, tx2, ty2, 2*p, 2*p)
    _r(surf, _RD, int(ox+14*p), int(oy+0), 2*p, 2*p)  # stinger
    _sprite(surf, cx, cy, size, [
        # pincers
        (col,    0, 5,  3, 3),
        (D,      0, 4,  2, 1),
        (D,      0, 7,  2, 1),
        (col,   13, 5,  3, 3),
        (D,     14, 4,  2, 1),
        (D,     14, 7,  2, 1),
        # legs (3 per side)
        (D,      3, 9,  2, 3),
        (D,      5, 9,  2, 4),
        (D,      7, 9,  2, 3),
        (D,      9, 9,  2, 4),
        (D,     11, 9,  2, 3),
        # body
        (col,    3, 5, 10, 6),
        (L,      4, 5,  8, 3),
        # head
        (D,      4, 4,  8, 2),
        # eyes
        (_RD,    5, 4,  2, 1),
        (_RD,    9, 4,  2, 1),
    ])

def draw_witch(surf, cx, cy, size, col, tick=0):
    cb = int(80 + 80 * abs(math.sin(tick * 0.007)))
    EY = (cb, 180, 0)
    D  = _dim(col)
    _sprite(surf, cx, cy, size, [
        # staff
        (_BR,   13, 2,  2,10),
        (EY,    12, 1,  4, 2),
        # hat cone
        (D,      6, 0,  4, 3),
        (D,      5, 1,  6, 2),
        # hat brim
        (D,      3, 3, 10, 2),
        (_GD,    6, 4,  4, 1),  # buckle
        # cloak
        (col,    4, 5, 8, 8),
        (D,      3, 9, 10, 4),
        # body
        (_lit(col,0.8), 5, 5, 6, 6),
        # head
        (_SK,    5, 5,  6, 4),
        # nose (warty)
        (_SD,    7, 7,  3, 2),
        (_SD,    6, 8,  1, 1),
        # eyes
        (EY,     6, 5,  2, 1),
        (EY,    10, 5,  2, 1),
        (_K,     6, 5,  1, 1),
        (_K,    10, 5,  1, 1),
        # cauldron
        (_K,     4,14,  8, 2),
        ((0, cb, 0), 5,14,  6, 1),
    ])

def draw_troll(surf, cx, cy, size, col, tick=0):
    D = _dim(col)
    L = _lit(col)
    _sprite(surf, cx, cy, size, [
        # legs (stumpy)
        (D,      4,11,  4, 5),
        (D,      8,11,  4, 5),
        # feet
        (D,      3,15,  5, 1),
        (D,      8,15,  5, 1),
        # body
        (col,    3, 5, 10, 7),
        (L,      4, 5,  8, 4),
        # muscle lines
        (D,      5, 6,  2, 5),
        (D,      9, 6,  2, 5),
        # arms (long)
        (D,      0, 5,  4, 8),
        (D,     12, 5,  4, 8),
        # fists
        (col,    0,11,  4, 3),
        (col,   12,11,  4, 3),
        # head
        (col,    3, 0, 10, 6),
        (L,      4, 0,  8, 3),
        # brow ridge
        (D,      3, 3, 10, 2),
        # eyes
        (_RD,    5, 1,  2, 2),
        (_RD,    9, 1,  2, 2),
        (_K,     5, 1,  1, 1),
        (_K,     9, 1,  1, 1),
        # nose
        (D,      7, 4,  2, 2),
        # tusks
        (_W,     5, 5,  2, 2),
        (_W,     9, 5,  2, 2),
        # outline
        (_K,     3, 0,  1, 6),
        (_K,    12, 0,  1, 6),
        (_K,     3, 5,  1, 7),
        (_K,    12, 5,  1, 7),
    ])

def draw_harpy(surf, cx, cy, size, col, tick=0):
    fl = (tick // 180) % 2
    D  = _dim(col)
    L  = _lit(col)
    _sprite(surf, cx, cy, size, [
        # wings
        (col,    0, 3-fl, 5, 6+fl),
        (col,   11, 3+fl, 5, 6-fl),
        (D,      1, 8,   4, 2),
        (D,     11, 8,   4, 2),
        # body
        (L,      5, 5,  6, 5),
        (col,    4, 5,  8, 6),
        # head
        (_SK,    5, 1,  6, 5),
        # hair
        (col,    4, 0,  8, 2),
        # eyes
        (_YL,    6, 3,  2, 2),
        (_K,     6, 3,  1, 1),
        # talons
        (D,      5,11,  2, 4),
        (D,      9,11,  2, 4),
        (D,      4,14,  2, 1),
        (D,      6,14,  2, 1),
        (D,      8,14,  2, 1),
        (D,     10,14,  2, 1),
    ])

def draw_djinn(surf, cx, cy, size, col, tick=0):
    sw = (tick // 150) % 3   # swirl frame
    L  = _lit(col)
    D  = _dim(col, 0.4)
    _sprite(surf, cx, cy, size, [
        # smoke tail (wispy)
        (D,      4+sw,12, 8, 2),
        (D,      5,   14, 6, 2),
        (D,      6+sw,13, 4, 3),
        # body (upper)
        (col,    3, 4, 10, 8),
        (L,      4, 4,  8, 5),
        # arms
        (col,    0, 6,  4, 4),
        (col,   12, 6,  4, 4),
        # head
        (L,      4, 0,  8, 5),
        # turban
        (_GD,    3, 0,  10, 2),
        (_RD,    7, 0,   2, 2),  # jewel
        # eyes
        (_W,     5, 2,  2, 2),
        (_W,     9, 2,  2, 2),
        (col,    5, 2,  1, 1),
        (col,    9, 2,  1, 1),
    ])


# ── Monster ID → sprite function ──────────────────────────────────────────────
def _get_monster_draw_fn(monster_id: str):
    slimes     = {"green_slime","blue_slime","forest_slime","sand_slime","ice_slime",
                  "fire_slime","poison_slime","shadow_slime","crystal_slime",
                  "storm_slime","lava_slime","blizzard_slime","magma_slime"}
    wolves     = {"prairie_wolf","alpha_wolf","snow_wolf","dire_frost_wolf"}
    rats       = {"field_rat","giant_rat","dire_rat"}
    goblins    = {"goblin_scout","goblin_warrior","goblin_shaman"}
    skeletons  = {"skeleton_archer","skeleton_knight","skeleton_king",
                  "death_knight","plague_bearer"}
    ghosts     = {"ghost","specter"}
    elementals = {"ice_elemental","blizzard_elemental","fire_elemental",
                  "prism_elemental","storm_elemental"}
    dragons    = {"fire_drake","ember_dragon","frost_dragon","gem_dragon",
                  "volcanic_dragon_lord","aldrath_king_of_dragons",
                  "wind_serpent","thunder_serpent","thunder_roc"}
    golems     = {"golem_king","magma_golem","crystal_golem","prism_golem",
                  "ancient_treant","tree_spirit","dark_ent"}
    bees       = {"giant_bee","queen_bee"}
    serpents   = {"sand_cobra","sand_king_cobra","swamp_serpent_lord",
                  "crystal_hydra"}
    bats       = {"cave_bat","vampire_bat"}
    mummies    = {"mummy","ancient_mummy"}
    scorpions  = {"desert_scorpion","emperor_scorpion"}
    witches    = {"bog_witch","grand_witch"}
    trolls     = {"frost_troll","ice_giant","storm_giant","troll","yeti"}
    harpies    = {"harpy","storm_harpy"}
    djinn      = {"desert_djinn"}
    frogs      = {"giant_frog","plague_frog"}

    if monster_id in slimes:     return draw_slime
    if monster_id in wolves:     return draw_wolf
    if monster_id in rats:       return draw_rat
    if monster_id in goblins:    return draw_goblin
    if monster_id in skeletons:  return draw_skeleton
    if monster_id in ghosts:     return draw_ghost
    if monster_id in elementals: return draw_elemental
    if monster_id in dragons:    return draw_dragon
    if monster_id in golems:     return draw_golem
    if monster_id in bees:       return draw_bee
    if monster_id in serpents:   return draw_serpent
    if monster_id in bats:       return draw_bat
    if monster_id in mummies:    return draw_mummy
    if monster_id in scorpions:  return draw_scorpion
    if monster_id in witches:    return draw_witch
    if monster_id in trolls:     return draw_troll
    if monster_id in harpies:    return draw_harpy
    if monster_id in djinn:      return draw_djinn
    if monster_id in frogs:      return draw_slime
    return draw_golem


def draw_monster_sprite(surf, monster_id: str, col, cx, cy, size, tick=0):
    # PNG override: use image file if one exists in assets/monsters/
    try:
        from assets.loader import get_monster_img
        img = get_monster_img(monster_id, size)
        if img is not None:
            surf.blit(img, (cx - size // 2, cy - size // 2))
            return
    except Exception:
        pass
    fn = _get_monster_draw_fn(monster_id)
    try:
        fn(surf, cx, cy, size, col, tick)
    except TypeError:
        fn(surf, cx, cy, size, tick)
