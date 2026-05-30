"""
Crafting recipes for CraftingScreen.

Each entry:
  id         – unique recipe key
  name       – display name (usually the output item name)
  inputs     – {item_id: qty_needed, ...}
  output     – item_id produced
  qty        – how many output items are produced per craft
"""

RECIPES = [
    # ── Consumables ───────────────────────────────────────────────────────────
    {"id": "r_hp_s",
     "name": "Health Potion (S)",
     "inputs": {"slime_gel": 2, "iron_ore": 1},
     "output": "health_potion_s", "qty": 2},

    {"id": "r_hp_m",
     "name": "Health Potion (M)",
     "inputs": {"slime_gel": 3, "beast_hide": 1},
     "output": "health_potion_m", "qty": 1},

    {"id": "r_hp_l",
     "name": "Health Potion (L)",
     "inputs": {"slime_gel": 5, "holy_dust": 1},
     "output": "health_potion_l", "qty": 1},

    {"id": "r_mp_s",
     "name": "Mana Potion (S)",
     "inputs": {"slime_gel": 1, "mana_seed": 2},
     "output": "mana_potion_s", "qty": 2},

    {"id": "r_mp_m",
     "name": "Mana Potion (M)",
     "inputs": {"slime_gel": 2, "mana_seed": 3},
     "output": "mana_potion_m", "qty": 1},

    {"id": "r_elixir",
     "name": "Elixir",
     "inputs": {"jungle_orchid": 1, "holy_dust": 1, "slime_gel": 2},
     "output": "elixir", "qty": 1},

    {"id": "r_antidote",
     "name": "Antidote",
     "inputs": {"poison_sac": 1, "slime_gel": 1},
     "output": "antidote", "qty": 2},

    {"id": "r_remedy",
     "name": "Remedy",
     "inputs": {"poison_sac": 2, "holy_dust": 1},
     "output": "remedy", "qty": 1},

    {"id": "r_fire_bomb",
     "name": "Fire Bomb",
     "inputs": {"fire_essence": 2, "slime_gel": 1},
     "output": "fire_bomb", "qty": 2},

    {"id": "r_ice_bomb",
     "name": "Ice Bomb",
     "inputs": {"ice_essence": 2, "slime_gel": 1},
     "output": "ice_bomb", "qty": 2},

    {"id": "r_smoke_bomb",
     "name": "Smoke Bomb",
     "inputs": {"dark_essence": 1, "slime_gel": 2},
     "output": "smoke_bomb", "qty": 1},

    {"id": "r_courage",
     "name": "Courage Brew",
     "inputs": {"monster_fang": 2, "fire_essence": 1},
     "output": "courage_brew", "qty": 1},

    {"id": "r_speed",
     "name": "Speed Brew",
     "inputs": {"monster_claw": 2, "lightning_essence": 1},
     "output": "speed_brew", "qty": 1},

    {"id": "r_iron_skin",
     "name": "Iron Skin Brew",
     "inputs": {"beast_hide": 2, "iron_ore": 1},
     "output": "iron_skin_brew", "qty": 1},

    # ── Weapons ───────────────────────────────────────────────────────────────
    {"id": "r_iron_sword",
     "name": "Iron Sword",
     "inputs": {"iron_ore": 4, "monster_claw": 2},
     "output": "iron_sword", "qty": 1},

    {"id": "r_iron_axe",
     "name": "Iron Axe",
     "inputs": {"iron_ore": 4, "monster_fang": 1},
     "output": "iron_axe", "qty": 1},

    {"id": "r_iron_dagger",
     "name": "Iron Dagger",
     "inputs": {"iron_ore": 2, "beast_hide": 1},
     "output": "iron_dagger", "qty": 1},

    {"id": "r_mithril_blade",
     "name": "Mithril Blade",
     "inputs": {"mithril_ore": 3, "monster_fang": 2},
     "output": "mithril_blade", "qty": 1},

    {"id": "r_crystal_sword",
     "name": "Crystal Sword",
     "inputs": {"crystal_shard": 4, "mithril_ore": 2},
     "output": "crystal_sword", "qty": 1},

    {"id": "r_dragonbone_bow",
     "name": "Dragonbone Bow",
     "inputs": {"dragon_bone": 2, "beast_hide": 3},
     "output": "dragonbone_bow", "qty": 1},

    # ── Armour ────────────────────────────────────────────────────────────────
    {"id": "r_leather_cap",
     "name": "Leather Cap",
     "inputs": {"beast_hide": 2},
     "output": "leather_cap", "qty": 1},

    {"id": "r_leather_vest",
     "name": "Leather Vest",
     "inputs": {"beast_hide": 4},
     "output": "leather_vest", "qty": 1},

    {"id": "r_iron_helm",
     "name": "Iron Helm",
     "inputs": {"iron_ore": 3},
     "output": "iron_helm", "qty": 1},

    {"id": "r_iron_chestplate",
     "name": "Iron Chestplate",
     "inputs": {"iron_ore": 5, "beast_hide": 2},
     "output": "iron_chestplate", "qty": 1},

    {"id": "r_chain_vest",
     "name": "Chain Vest",
     "inputs": {"iron_ore": 4, "monster_claw": 1},
     "output": "chain_vest", "qty": 1},

    # ── Materials (refine / combine) ──────────────────────────────────────────
    {"id": "r_mithril_ore",
     "name": "Mithril Ore (refine)",
     "inputs": {"iron_ore": 8, "fire_essence": 2},
     "output": "mithril_ore", "qty": 1},

    {"id": "r_holy_dust",
     "name": "Holy Dust (synthesise)",
     "inputs": {"slime_gel": 4, "ice_essence": 2},
     "output": "holy_dust", "qty": 1},

    {"id": "r_capture_net",
     "name": "Capture Net",
     "inputs": {"beast_hide": 2, "monster_claw": 1},
     "output": "capture_net", "qty": 2},
]
