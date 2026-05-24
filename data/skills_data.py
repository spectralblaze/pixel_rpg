"""All skill definitions.
type: 'active' | 'passive'
source: 'level' | 'found'   (found = discovered in rare world areas)
target: 'enemy' | 'self' | 'all_enemies'
effect: dict of stat changes or special flags
"""

SKILLS = {
    # ─── Universal ──────────────────────────────────────────────────────────
    "basic_attack": {
        "name": "Basic Attack", "type": "active", "source": "level",
        "desc": "A standard physical attack.", "mp_cost": 0,
        "target": "enemy", "dmg_type": "physical", "power": 1.0,
        "color": (180, 180, 180),
    },

    # ─── Warrior ────────────────────────────────────────────────────────────
    "power_strike": {
        "name": "Power Strike", "type": "active", "source": "level",
        "desc": "A heavy blow dealing 150% ATK damage.", "mp_cost": 8,
        "target": "enemy", "dmg_type": "physical", "power": 1.5,
        "color": (210, 80, 80),
    },
    "second_wind": {
        "name": "Second Wind", "type": "active", "source": "level",
        "desc": "Recover 25% max HP.", "mp_cost": 15,
        "target": "self", "heal_pct": 0.25, "color": (80, 200, 120),
    },
    "war_cry": {
        "name": "War Cry", "type": "active", "source": "level",
        "desc": "Boost ATK by 30% for 3 turns.", "mp_cost": 18,
        "target": "self", "buff": {"atk_mult": 1.3, "turns": 3},
        "color": (220, 130, 50),
    },
    "rend": {
        "name": "Rend", "type": "active", "source": "level",
        "desc": "Slash dealing 120% ATK and inflicting Bleed (3 turns).", "mp_cost": 14,
        "target": "enemy", "dmg_type": "physical", "power": 1.2,
        "status": {"bleed": 3}, "color": (180, 40, 40),
    },
    "battle_hardened": {
        "name": "Battle Hardened", "type": "passive", "source": "level",
        "desc": "Permanently increase DEF by 10.", "mp_cost": 0,
        "passive_bonus": {"def": 10}, "color": (140, 140, 200),
    },
    # Knight
    "shield_bash": {
        "name": "Shield Bash", "type": "active", "source": "level",
        "desc": "Bash with shield for 90% ATK + Stun 1 turn.", "mp_cost": 12,
        "target": "enemy", "dmg_type": "physical", "power": 0.9,
        "status": {"stun": 1}, "color": (150, 150, 210),
    },
    "taunt": {
        "name": "Taunt", "type": "active", "source": "level",
        "desc": "Force enemy to attack you next turn. Boost DEF 50%.", "mp_cost": 10,
        "target": "self", "buff": {"def_mult": 1.5, "turns": 1},
        "special": "taunt", "color": (200, 100, 50),
    },
    "fortress_stance": {
        "name": "Fortress Stance", "type": "active", "source": "level",
        "desc": "Reduce damage taken by 60% for 2 turns.", "mp_cost": 20,
        "target": "self", "buff": {"dmg_reduction": 0.6, "turns": 2},
        "color": (100, 100, 200),
    },
    "reflect_damage": {
        "name": "Reflect Damage", "type": "active", "source": "level",
        "desc": "Reflect 40% of next hit back to attacker for 2 turns.", "mp_cost": 25,
        "target": "self", "buff": {"reflect": 0.4, "turns": 2},
        "color": (180, 180, 255),
    },
    "indomitable": {
        "name": "Indomitable", "type": "passive", "source": "level",
        "desc": "Cannot be KO'd below 1 HP once per combat.", "mp_cost": 0,
        "passive_bonus": {}, "special": "indomitable", "color": (200, 200, 100),
    },
    "aegis": {
        "name": "Aegis", "type": "active", "source": "level",
        "desc": "Create a barrier absorbing 200 damage.", "mp_cost": 30,
        "target": "self", "buff": {"shield": 200, "turns": 5},
        "color": (100, 200, 255),
    },
    # Berserker
    "berserk_rage": {
        "name": "Berserk Rage", "type": "active", "source": "level",
        "desc": "Enter rage: ATK +50%, DEF -20%, for 4 turns.", "mp_cost": 20,
        "target": "self", "buff": {"atk_mult": 1.5, "def_mult": 0.8, "turns": 4},
        "color": (210, 50, 20),
    },
    "whirlwind": {
        "name": "Whirlwind", "type": "active", "source": "level",
        "desc": "Spin dealing 110% ATK to all enemies.", "mp_cost": 22,
        "target": "all_enemies", "dmg_type": "physical", "power": 1.1,
        "color": (200, 100, 30),
    },
    "bloodlust": {
        "name": "Bloodlust", "type": "passive", "source": "level",
        "desc": "Each kill restores 15% max HP.", "mp_cost": 0,
        "passive_bonus": {}, "special": "bloodlust", "color": (180, 30, 30),
    },
    "savage_roar": {
        "name": "Savage Roar", "type": "active", "source": "level",
        "desc": "Terrify enemy, reducing their ATK 30% for 3 turns.", "mp_cost": 18,
        "target": "enemy", "debuff": {"atk_mult": 0.7, "turns": 3},
        "color": (180, 80, 30),
    },
    "deathblow": {
        "name": "Deathblow", "type": "active", "source": "level",
        "desc": "200% ATK hit. If below 25% HP, deals 350% instead.", "mp_cost": 35,
        "target": "enemy", "dmg_type": "physical", "power": 2.0,
        "special": "deathblow", "color": (220, 20, 20),
    },
    "titan_smash": {
        "name": "Titan Smash", "type": "active", "source": "level",
        "desc": "Devastating 280% ATK ground slam + Stun all for 1 turn.", "mp_cost": 45,
        "target": "all_enemies", "dmg_type": "physical", "power": 2.8,
        "status": {"stun": 1}, "color": (255, 50, 0),
    },
    # Paladin
    "holy_strike": {
        "name": "Holy Strike", "type": "active", "source": "level",
        "desc": "Holy-infused strike: 130% ATK + extra vs Undead/Dark.", "mp_cost": 14,
        "target": "enemy", "dmg_type": "holy", "power": 1.3,
        "color": (230, 220, 100),
    },
    "divine_heal": {
        "name": "Divine Heal", "type": "active", "source": "level",
        "desc": "Restore 30% of max HP through holy light.", "mp_cost": 20,
        "target": "self", "heal_pct": 0.30, "color": (220, 220, 150),
    },
    "sacred_shield": {
        "name": "Sacred Shield", "type": "active", "source": "level",
        "desc": "Holy barrier absorbing 150 damage + removes 1 debuff.", "mp_cost": 25,
        "target": "self", "buff": {"shield": 150, "turns": 4},
        "special": "cleanse_one", "color": (200, 210, 255),
    },
    "smite_evil": {
        "name": "Smite Evil", "type": "active", "source": "level",
        "desc": "Holy explosion: 180% INT damage to enemy.", "mp_cost": 28,
        "target": "enemy", "dmg_type": "holy", "power": 1.8, "use_int": True,
        "color": (255, 230, 80),
    },
    "holy_aura": {
        "name": "Holy Aura", "type": "passive", "source": "level",
        "desc": "Passively regenerate 3% HP each turn.", "mp_cost": 0,
        "passive_bonus": {}, "special": "hp_regen_3pct", "color": (220, 230, 180),
    },
    "resurrection": {
        "name": "Resurrection", "type": "active", "source": "level",
        "desc": "Revive from death once per combat at 50% HP.", "mp_cost": 60,
        "target": "self", "special": "resurrection", "color": (255, 255, 200),
    },

    # ─── Mage ───────────────────────────────────────────────────────────────
    "arcane_bolt": {
        "name": "Arcane Bolt", "type": "active", "source": "level",
        "desc": "Hurl a bolt of pure arcane for 120% INT damage.", "mp_cost": 10,
        "target": "enemy", "dmg_type": "arcane", "power": 1.2, "use_int": True,
        "color": (100, 100, 230),
    },
    "mana_shield": {
        "name": "Mana Shield", "type": "active", "source": "level",
        "desc": "Absorb damage using MP instead of HP (up to 50 MP).", "mp_cost": 0,
        "target": "self", "special": "mana_shield", "color": (80, 120, 255),
    },
    "arcane_nova": {
        "name": "Arcane Nova", "type": "active", "source": "level",
        "desc": "Arcane burst hitting all enemies for 130% INT.", "mp_cost": 28,
        "target": "all_enemies", "dmg_type": "arcane", "power": 1.3, "use_int": True,
        "color": (120, 80, 255),
    },
    "spell_haste": {
        "name": "Spell Haste", "type": "passive", "source": "level",
        "desc": "All spells cost 15% less MP.", "mp_cost": 0,
        "passive_bonus": {}, "special": "mp_discount_15", "color": (100, 180, 255),
    },
    "mana_pool": {
        "name": "Mana Pool", "type": "passive", "source": "level",
        "desc": "Max MP +40.", "mp_cost": 0,
        "passive_bonus": {"mp": 40}, "color": (80, 80, 220),
    },
    # Wizard
    "arcane_blast": {
        "name": "Arcane Blast", "type": "active", "source": "level",
        "desc": "Devastating 220% INT arcane explosion.", "mp_cost": 35,
        "target": "enemy", "dmg_type": "arcane", "power": 2.2, "use_int": True,
        "color": (60, 60, 255),
    },
    "mana_surge": {
        "name": "Mana Surge", "type": "active", "source": "level",
        "desc": "Spend 30 MP to increase next spell power by 80%.", "mp_cost": 30,
        "target": "self", "buff": {"spell_power": 1.8, "turns": 1},
        "color": (100, 100, 255),
    },
    "spell_mastery": {
        "name": "Spell Mastery", "type": "passive", "source": "level",
        "desc": "All spell damage +25%.", "mp_cost": 0,
        "passive_bonus": {}, "special": "spell_power_25", "color": (130, 100, 255),
    },
    "arcane_torrent": {
        "name": "Arcane Torrent", "type": "active", "source": "level",
        "desc": "Rapid arcane volleys: 4 hits of 70% INT each.", "mp_cost": 40,
        "target": "enemy", "dmg_type": "arcane", "power": 0.7, "hits": 4, "use_int": True,
        "color": (80, 60, 255),
    },
    "time_stop": {
        "name": "Time Stop", "type": "active", "source": "found",
        "desc": "[RARE] Freeze enemy for 3 turns. They cannot act.", "mp_cost": 55,
        "target": "enemy", "status": {"freeze": 3}, "color": (150, 200, 255),
    },
    "galaxy_burst": {
        "name": "Galaxy Burst", "type": "active", "source": "found",
        "desc": "[RARE] Cosmic explosion: 500% INT to all enemies.", "mp_cost": 80,
        "target": "all_enemies", "dmg_type": "arcane", "power": 5.0, "use_int": True,
        "color": (180, 100, 255),
    },
    # Warlock
    "life_drain": {
        "name": "Life Drain", "type": "active", "source": "level",
        "desc": "Dark tendrils deal 150% INT + heal you for 50% of damage.", "mp_cost": 20,
        "target": "enemy", "dmg_type": "dark", "power": 1.5, "use_int": True,
        "special": "lifesteal_50", "color": (100, 50, 150),
    },
    "soul_curse": {
        "name": "Soul Curse", "type": "active", "source": "level",
        "desc": "Curse reduces enemy INT & ATK by 25% for 4 turns.", "mp_cost": 18,
        "target": "enemy", "debuff": {"atk_mult": 0.75, "int_mult": 0.75, "turns": 4},
        "color": (120, 40, 160),
    },
    "dark_pact": {
        "name": "Dark Pact", "type": "active", "source": "level",
        "desc": "Sacrifice 20% HP to gain ATK & INT +40% for 3 turns.", "mp_cost": 15,
        "target": "self", "buff": {"atk_mult": 1.4, "int_mult": 1.4, "turns": 3},
        "special": "self_dmg_20pct", "color": (150, 30, 130),
    },
    "demon_brand": {
        "name": "Demon Brand", "type": "active", "source": "level",
        "desc": "Dark mark: enemy takes +35% more damage for 4 turns.", "mp_cost": 22,
        "target": "enemy", "debuff": {"dmg_taken_mult": 1.35, "turns": 4},
        "color": (180, 20, 100),
    },
    "void_rift": {
        "name": "Void Rift", "type": "active", "source": "found",
        "desc": "[RARE] Open a void rift for 200% INT dark damage all + Silence 2 turns.", "mp_cost": 45,
        "target": "all_enemies", "dmg_type": "dark", "power": 2.0, "use_int": True,
        "status": {"silence": 2}, "color": (80, 0, 120),
    },
    "death_coil": {
        "name": "Death Coil", "type": "active", "source": "found",
        "desc": "[RARE] Coil of death: 350% INT dark + Doom (KO in 3 turns).", "mp_cost": 70,
        "target": "enemy", "dmg_type": "dark", "power": 3.5, "use_int": True,
        "status": {"doom": 3}, "color": (60, 0, 90),
    },
    # Elementalist
    "fire_ball": {
        "name": "Fire Ball", "type": "active", "source": "level",
        "desc": "Hurl a fireball for 160% INT fire + Burn 2 turns.", "mp_cost": 18,
        "target": "enemy", "dmg_type": "fire", "power": 1.6, "use_int": True,
        "status": {"burn": 2}, "color": (230, 120, 30),
    },
    "blizzard": {
        "name": "Blizzard", "type": "active", "source": "level",
        "desc": "Ice storm deals 140% INT ice to all enemies + Slow 2 turns.", "mp_cost": 22,
        "target": "all_enemies", "dmg_type": "ice", "power": 1.4, "use_int": True,
        "status": {"slow": 2}, "color": (150, 210, 255),
    },
    "thunder_strike": {
        "name": "Thunder Strike", "type": "active", "source": "level",
        "desc": "Lightning bolt: 200% INT lightning + chance to Paralyze.", "mp_cost": 28,
        "target": "enemy", "dmg_type": "lightning", "power": 2.0, "use_int": True,
        "status": {"paralyze": 1, "chance": 0.4}, "color": (220, 220, 50),
    },
    "fire_storm": {
        "name": "Fire Storm", "type": "active", "source": "level",
        "desc": "Inferno hitting all for 180% INT fire + Burn 3 turns.", "mp_cost": 38,
        "target": "all_enemies", "dmg_type": "fire", "power": 1.8, "use_int": True,
        "status": {"burn": 3}, "color": (255, 100, 20),
    },
    "frozen_world": {
        "name": "Frozen World", "type": "active", "source": "found",
        "desc": "[RARE] Freeze ALL enemies solid for 2 turns (250% INT ice).", "mp_cost": 55,
        "target": "all_enemies", "dmg_type": "ice", "power": 2.5, "use_int": True,
        "status": {"freeze": 2}, "color": (100, 180, 255),
    },
    "divine_storm": {
        "name": "Divine Storm", "type": "active", "source": "found",
        "desc": "[RARE] Combined elemental cataclysm: 600% INT to all.", "mp_cost": 90,
        "target": "all_enemies", "dmg_type": "elemental", "power": 6.0, "use_int": True,
        "color": (255, 200, 80),
    },

    # ─── Rogue ──────────────────────────────────────────────────────────────
    "quick_strike": {
        "name": "Quick Strike", "type": "active", "source": "level",
        "desc": "Two rapid hits of 60% ATK each. High crit chance.", "mp_cost": 8,
        "target": "enemy", "dmg_type": "physical", "power": 0.6, "hits": 2,
        "crit_bonus": 0.2, "color": (150, 150, 50),
    },
    "evasion": {
        "name": "Evasion", "type": "active", "source": "level",
        "desc": "Dodge chance +60% for 2 turns.", "mp_cost": 12,
        "target": "self", "buff": {"evasion": 0.6, "turns": 2},
        "color": (80, 80, 120),
    },
    "smoke_bomb": {
        "name": "Smoke Bomb", "type": "active", "source": "level",
        "desc": "Blind enemy: their accuracy -50% for 3 turns.", "mp_cost": 15,
        "target": "enemy", "debuff": {"accuracy": 0.5, "turns": 3},
        "color": (100, 100, 100),
    },
    "crippling_blow": {
        "name": "Crippling Blow", "type": "active", "source": "level",
        "desc": "Strike for 140% ATK + reduce enemy SPD by 40% for 3 turns.", "mp_cost": 18,
        "target": "enemy", "dmg_type": "physical", "power": 1.4,
        "debuff": {"spd_mult": 0.6, "turns": 3}, "color": (150, 80, 50),
    },
    "shadow_instinct": {
        "name": "Shadow Instinct", "type": "passive", "source": "level",
        "desc": "Critical hit damage +50%.", "mp_cost": 0,
        "passive_bonus": {}, "special": "crit_dmg_50", "color": (80, 60, 100),
    },
    # Assassin
    "shadow_strike": {
        "name": "Shadow Strike", "type": "active", "source": "level",
        "desc": "Strike from shadows for 220% ATK. Guaranteed crit from stealth.", "mp_cost": 25,
        "target": "enemy", "dmg_type": "physical", "power": 2.2,
        "color": (30, 30, 60),
    },
    "poison_blade": {
        "name": "Poison Blade", "type": "active", "source": "level",
        "desc": "Coat blade in venom: 100% ATK + Poison 5 turns.", "mp_cost": 16,
        "target": "enemy", "dmg_type": "physical", "power": 1.0,
        "status": {"poison": 5}, "color": (80, 180, 50),
    },
    "death_mark": {
        "name": "Death Mark", "type": "active", "source": "level",
        "desc": "Mark target: next attack deals +100% damage.", "mp_cost": 22,
        "target": "enemy", "debuff": {"dmg_taken_mult": 2.0, "turns": 1},
        "color": (180, 20, 20),
    },
    "blade_dance": {
        "name": "Blade Dance", "type": "active", "source": "level",
        "desc": "5 rapid slashes of 50% ATK each.", "mp_cost": 30,
        "target": "enemy", "dmg_type": "physical", "power": 0.5, "hits": 5,
        "color": (120, 120, 180),
    },
    "coup_de_grace": {
        "name": "Coup de Grace", "type": "active", "source": "found",
        "desc": "[RARE] Instant KO if target below 20% HP, else 300% ATK.", "mp_cost": 45,
        "target": "enemy", "dmg_type": "physical", "power": 3.0,
        "special": "execute_20pct", "color": (200, 30, 30),
    },
    "vanish": {
        "name": "Vanish", "type": "active", "source": "found",
        "desc": "[RARE] Enter stealth. Skip your turn, next attack is auto-crit.", "mp_cost": 30,
        "target": "self", "special": "vanish", "color": (50, 50, 80),
    },
    # Ranger
    "multi_shot": {
        "name": "Multi Shot", "type": "active", "source": "level",
        "desc": "Fire 3 arrows: 70% ATK each, hitting random enemies.", "mp_cost": 14,
        "target": "all_enemies", "dmg_type": "physical", "power": 0.7, "hits": 3,
        "color": (80, 150, 60),
    },
    "trap_set": {
        "name": "Trap Set", "type": "active", "source": "level",
        "desc": "Set a trap: enemy attacks trigger 150% ATK counter.", "mp_cost": 18,
        "target": "self", "special": "trap", "color": (120, 100, 50),
    },
    "eagle_eye": {
        "name": "Eagle Eye", "type": "passive", "source": "level",
        "desc": "Ranged attacks ignore 30% of enemy DEF.", "mp_cost": 0,
        "passive_bonus": {}, "special": "def_pierce_30", "color": (180, 200, 80),
    },
    "rain_of_arrows": {
        "name": "Rain of Arrows", "type": "active", "source": "level",
        "desc": "Arrow barrage hits all enemies for 100% ATK each.", "mp_cost": 32,
        "target": "all_enemies", "dmg_type": "physical", "power": 1.0,
        "color": (100, 160, 60),
    },
    "beast_taming": {
        "name": "Beast Taming", "type": "passive", "source": "level",
        "desc": "Capture rate +25% for all monsters.", "mp_cost": 0,
        "passive_bonus": {}, "special": "capture_25", "color": (160, 140, 80),
    },
    "heavens_arrow": {
        "name": "Heaven's Arrow", "type": "active", "source": "found",
        "desc": "[RARE] Divine arrow: 400% ATK ignoring all defenses.", "mp_cost": 60,
        "target": "enemy", "dmg_type": "holy", "power": 4.0,
        "color": (255, 240, 120),
    },
    # Shadow
    "shadow_clone": {
        "name": "Shadow Clone", "type": "active", "source": "level",
        "desc": "Create a clone that takes one hit for you this turn.", "mp_cost": 20,
        "target": "self", "special": "shadow_clone", "color": (60, 40, 90),
    },
    "dark_step": {
        "name": "Dark Step", "type": "active", "source": "level",
        "desc": "Phase into shadows: evade next attack, then counter 120% ATK.", "mp_cost": 18,
        "target": "self", "special": "dark_step", "color": (50, 30, 80),
    },
    "nightmare": {
        "name": "Nightmare", "type": "active", "source": "level",
        "desc": "Inflict Nightmare: enemy loses 10% HP each turn for 5 turns + Fear.", "mp_cost": 28,
        "target": "enemy", "status": {"nightmare": 5, "fear": 2}, "color": (80, 30, 80),
    },
    "void_dash": {
        "name": "Void Dash", "type": "active", "source": "level",
        "desc": "Dash through void dealing 160% ATK dark + Teleport behind.", "mp_cost": 25,
        "target": "enemy", "dmg_type": "dark", "power": 1.6, "color": (70, 40, 100),
    },
    "soul_rend": {
        "name": "Soul Rend", "type": "active", "source": "found",
        "desc": "[RARE] Tear the soul: 250% INT dark + Drain 50% of damage as HP.", "mp_cost": 50,
        "target": "enemy", "dmg_type": "dark", "power": 2.5, "use_int": True,
        "special": "lifesteal_50", "color": (100, 20, 100),
    },
    "umbra_collapse": {
        "name": "Umbra Collapse", "type": "active", "source": "found",
        "desc": "[RARE] Collapse all shadow into one: 700% ATK dark to enemy.", "mp_cost": 85,
        "target": "enemy", "dmg_type": "dark", "power": 7.0, "color": (40, 0, 60),
    },

    # ─── Healer ─────────────────────────────────────────────────────────────
    "heal": {
        "name": "Heal", "type": "active", "source": "level",
        "desc": "Restore 25% max HP.", "mp_cost": 18,
        "target": "self", "heal_pct": 0.25, "color": (60, 200, 100),
    },
    "cleanse": {
        "name": "Cleanse", "type": "active", "source": "level",
        "desc": "Remove all negative status effects.", "mp_cost": 12,
        "target": "self", "special": "cleanse_all", "color": (150, 230, 180),
    },
    "mend": {
        "name": "Mend", "type": "active", "source": "level",
        "desc": "Regenerate 8% HP per turn for 5 turns.", "mp_cost": 20,
        "target": "self", "buff": {"hp_regen_pct": 0.08, "turns": 5},
        "color": (80, 220, 130),
    },
    "barrier": {
        "name": "Barrier", "type": "active", "source": "level",
        "desc": "Shield absorbing 100 damage for 3 turns.", "mp_cost": 22,
        "target": "self", "buff": {"shield": 100, "turns": 3},
        "color": (100, 200, 200),
    },
    "empower": {
        "name": "Empower", "type": "active", "source": "level",
        "desc": "INT +40% for 3 turns (boosts heals and spell damage).", "mp_cost": 18,
        "target": "self", "buff": {"int_mult": 1.4, "turns": 3},
        "color": (180, 200, 100),
    },
    # Priest
    "holy_nova": {
        "name": "Holy Nova", "type": "active", "source": "level",
        "desc": "Holy burst: 160% INT holy to all enemies.", "mp_cost": 30,
        "target": "all_enemies", "dmg_type": "holy", "power": 1.6, "use_int": True,
        "color": (255, 240, 150),
    },
    "divine_blessing": {
        "name": "Divine Blessing", "type": "active", "source": "level",
        "desc": "Blessed by heaven: all stats +20% for 4 turns.", "mp_cost": 28,
        "target": "self",
        "buff": {"atk_mult": 1.2, "def_mult": 1.2, "spd_mult": 1.2, "int_mult": 1.2, "turns": 4},
        "color": (230, 230, 160),
    },
    "holy_rain": {
        "name": "Holy Rain", "type": "active", "source": "level",
        "desc": "Holy downpour: 200% INT holy to all enemies + heals 15% HP.", "mp_cost": 40,
        "target": "all_enemies", "dmg_type": "holy", "power": 2.0, "use_int": True,
        "heal_pct": 0.15, "color": (255, 255, 180),
    },
    "divine_judgement": {
        "name": "Divine Judgement", "type": "active", "source": "found",
        "desc": "[RARE] Smite with 350% INT holy. Instant KO undead/dark.", "mp_cost": 55,
        "target": "enemy", "dmg_type": "holy", "power": 3.5, "use_int": True,
        "special": "smite_dark", "color": (255, 250, 100),
    },
    "miracle": {
        "name": "Miracle", "type": "active", "source": "found",
        "desc": "[RARE] Fully restore HP and remove all debuffs.", "mp_cost": 80,
        "target": "self", "special": "full_restore", "color": (255, 255, 255),
    },
    # Druid
    "thornwall": {
        "name": "Thorn Wall", "type": "active", "source": "level",
        "desc": "Thorns return 30% melee damage to attacker for 4 turns.", "mp_cost": 18,
        "target": "self", "buff": {"thorns": 0.3, "turns": 4},
        "color": (80, 140, 50),
    },
    "regrowth": {
        "name": "Regrowth", "type": "active", "source": "level",
        "desc": "Deep heal: restore 40% max HP over 4 turns.", "mp_cost": 24,
        "target": "self", "buff": {"hp_regen_pct": 0.10, "turns": 4},
        "color": (60, 180, 80),
    },
    "shapeshift_bear": {
        "name": "Shapeshift: Bear", "type": "active", "source": "level",
        "desc": "Transform into bear: HP & DEF +50%, ATK +30% for 3 turns.", "mp_cost": 30,
        "target": "self",
        "buff": {"hp_mult": 1.5, "def_mult": 1.5, "atk_mult": 1.3, "turns": 3},
        "color": (140, 100, 60),
    },
    "natures_wrath": {
        "name": "Nature's Wrath", "type": "active", "source": "level",
        "desc": "Gaia strikes: 220% INT nature to all enemies + Poison 3 turns.", "mp_cost": 38,
        "target": "all_enemies", "dmg_type": "nature", "power": 2.2, "use_int": True,
        "status": {"poison": 3}, "color": (100, 200, 60),
    },
    "plague_bloom": {
        "name": "Plague Bloom", "type": "active", "source": "found",
        "desc": "[RARE] Toxic blossom: 150% INT + Poison 8 turns to all.", "mp_cost": 48,
        "target": "all_enemies", "dmg_type": "nature", "power": 1.5, "use_int": True,
        "status": {"poison": 8}, "color": (120, 180, 40),
    },
    "world_tree": {
        "name": "World Tree", "type": "active", "source": "found",
        "desc": "[RARE] Ancient tree: restore 60% HP and gain thorns + regen for 5 turns.", "mp_cost": 70,
        "target": "self",
        "heal_pct": 0.6, "buff": {"thorns": 0.4, "hp_regen_pct": 0.08, "turns": 5},
        "color": (60, 160, 60),
    },
    # Oracle
    "fate_read": {
        "name": "Fate Read", "type": "active", "source": "level",
        "desc": "Read enemy's next move: dodge it and counter 100% ATK.", "mp_cost": 20,
        "target": "self", "special": "fate_read", "color": (180, 150, 220),
    },
    "time_warp": {
        "name": "Time Warp", "type": "active", "source": "level",
        "desc": "Slow enemy SPD by 50% for 3 turns. Boost own SPD by 30%.", "mp_cost": 22,
        "target": "enemy", "debuff": {"spd_mult": 0.5, "turns": 3},
        "buff_self": {"spd_mult": 1.3, "turns": 3}, "color": (150, 120, 220),
    },
    "prophecy_shield": {
        "name": "Prophecy Shield", "type": "active", "source": "level",
        "desc": "Foresee attacks: 70% chance to block next 3 hits.", "mp_cost": 28,
        "target": "self", "buff": {"prophecy_block": 3, "chance": 0.7, "turns": 5},
        "color": (200, 180, 255),
    },
    "paradox": {
        "name": "Paradox", "type": "active", "source": "level",
        "desc": "Temporal paradox: deal 200% INT arcane, reset enemy buffs.", "mp_cost": 38,
        "target": "enemy", "dmg_type": "arcane", "power": 2.0, "use_int": True,
        "special": "strip_buffs", "color": (160, 100, 255),
    },
    "destiny_chain": {
        "name": "Destiny Chain", "type": "active", "source": "found",
        "desc": "[RARE] Link fate: enemy takes 200% of any damage you take (5 turns).", "mp_cost": 50,
        "target": "enemy", "special": "destiny_chain", "color": (180, 130, 255),
    },
    "eternal_moment": {
        "name": "Eternal Moment", "type": "active", "source": "found",
        "desc": "[RARE] Stop time: act twice next turn.", "mp_cost": 70,
        "target": "self", "special": "extra_turn", "color": (220, 200, 255),
    },

    # ─── Summoner ────────────────────────────────────────────────────────────
    "summon_familiar": {
        "name": "Summon Familiar", "type": "active", "source": "level",
        "desc": "Summon a spirit familiar to assist in battle (50 HP, 20 ATK).", "mp_cost": 25,
        "target": "self", "special": "summon_familiar", "color": (185, 105, 210),
    },
    "bond_strengthen": {
        "name": "Bond Strengthen", "type": "passive", "source": "level",
        "desc": "Pet/summon ATK & DEF +20%.", "mp_cost": 0,
        "passive_bonus": {}, "special": "pet_boost_20", "color": (200, 150, 220),
    },
    "pack_call": {
        "name": "Pack Call", "type": "active", "source": "level",
        "desc": "Call your pet to attack for 150% of its ATK stat.", "mp_cost": 12,
        "target": "enemy", "special": "pet_attack_150", "color": (180, 120, 200),
    },
    "shared_pain": {
        "name": "Shared Pain", "type": "active", "source": "level",
        "desc": "Transfer 40% of damage you take to your summoned ally.", "mp_cost": 18,
        "target": "self", "special": "shared_pain", "color": (160, 100, 180),
    },
    "evolution_touch": {
        "name": "Evolution Touch", "type": "active", "source": "level",
        "desc": "Give pet bonus EXP. If next battle is won with pet, +50% pet EXP.", "mp_cost": 20,
        "target": "self", "special": "pet_exp_boost", "color": (200, 160, 220),
    },
    # Beastmaster
    "alpha_tame": {
        "name": "Alpha Tame", "type": "active", "source": "level",
        "desc": "Attempt to capture a monster. Success based on HP ratio + LCK.", "mp_cost": 20,
        "target": "enemy", "special": "capture", "color": (170, 140, 80),
    },
    "beast_bond": {
        "name": "Beast Bond", "type": "passive", "source": "level",
        "desc": "Pet EXP gain +50%. Pet evolves 20% sooner.", "mp_cost": 0,
        "passive_bonus": {}, "special": "beast_bond", "color": (180, 160, 100),
    },
    "pack_leader": {
        "name": "Pack Leader", "type": "active", "source": "level",
        "desc": "Inspire pet: ATK & SPD +60% for 3 turns.", "mp_cost": 25,
        "target": "self", "special": "pet_buff_60_3t", "color": (200, 160, 80),
    },
    "feral_surge": {
        "name": "Feral Surge", "type": "active", "source": "level",
        "desc": "Pet unleashes primal power: deals 250% pet ATK.", "mp_cost": 30,
        "target": "enemy", "special": "pet_attack_250", "color": (220, 140, 60),
    },
    "omega_tame": {
        "name": "Omega Tame", "type": "active", "source": "found",
        "desc": "[RARE] Attempt to capture any monster, including Alphas.", "mp_cost": 40,
        "target": "enemy", "special": "omega_capture", "color": (200, 100, 40),
    },
    "primal_roar": {
        "name": "Primal Roar", "type": "active", "source": "found",
        "desc": "[RARE] Terrifying roar: all enemy stats -30% for 4 turns.", "mp_cost": 50,
        "target": "all_enemies", "debuff": {"atk_mult": 0.7, "def_mult": 0.7, "spd_mult": 0.7, "turns": 4},
        "color": (220, 120, 40),
    },
    # Necromancer
    "raise_dead": {
        "name": "Raise Dead", "type": "active", "source": "level",
        "desc": "Reanimate a fallen monster as undead ally (last killed enemy).", "mp_cost": 30,
        "target": "self", "special": "raise_dead", "color": (80, 130, 80),
    },
    "bone_spear": {
        "name": "Bone Spear", "type": "active", "source": "level",
        "desc": "Jagged bones pierce for 180% INT dark.", "mp_cost": 22,
        "target": "enemy", "dmg_type": "dark", "power": 1.8, "use_int": True,
        "color": (130, 160, 100),
    },
    "death_aura": {
        "name": "Death Aura", "type": "passive", "source": "level",
        "desc": "At turn start, deal 30 dark damage to enemy passively.", "mp_cost": 0,
        "passive_bonus": {}, "special": "death_aura_30", "color": (80, 100, 80),
    },
    "lich_form": {
        "name": "Lich Form", "type": "active", "source": "level",
        "desc": "Transform into Lich: INT +50%, immune to status for 4 turns.", "mp_cost": 40,
        "target": "self", "buff": {"int_mult": 1.5, "status_immune": True, "turns": 4},
        "color": (100, 130, 100),
    },
    "undead_army": {
        "name": "Undead Army", "type": "active", "source": "found",
        "desc": "[RARE] Summon 3 skeleton warriors to fight for you.", "mp_cost": 55,
        "target": "self", "special": "undead_army", "color": (80, 120, 80),
    },
    "apocalypse": {
        "name": "Apocalypse", "type": "active", "source": "found",
        "desc": "[RARE] Dark apocalypse: 600% INT dark to all enemies.", "mp_cost": 90,
        "target": "all_enemies", "dmg_type": "dark", "power": 6.0, "use_int": True,
        "color": (40, 80, 40),
    },
    # Spirit Caller
    "spirit_army": {
        "name": "Spirit Army", "type": "active", "source": "level",
        "desc": "Summon 2 spirit warriors (60 HP, 30 ATK each).", "mp_cost": 35,
        "target": "self", "special": "spirit_army", "color": (210, 210, 255),
    },
    "ethereal_form": {
        "name": "Ethereal Form", "type": "active", "source": "level",
        "desc": "Become ethereal: 80% dodge chance for 2 turns.", "mp_cost": 28,
        "target": "self", "buff": {"evasion": 0.8, "turns": 2},
        "color": (180, 200, 255),
    },
    "ancient_call": {
        "name": "Ancient Call", "type": "active", "source": "level",
        "desc": "Channel ancient spirit: INT +40%, deal 150% INT arcane.", "mp_cost": 32,
        "target": "enemy", "dmg_type": "arcane", "power": 1.5, "use_int": True,
        "buff_self": {"int_mult": 1.4, "turns": 2}, "color": (200, 200, 255),
    },
    "soul_storm": {
        "name": "Soul Storm", "type": "active", "source": "level",
        "desc": "Unleash tormented souls: 200% INT to all enemies + Silence 2t.", "mp_cost": 42,
        "target": "all_enemies", "dmg_type": "arcane", "power": 2.0, "use_int": True,
        "status": {"silence": 2}, "color": (170, 180, 255),
    },
    "spirit_world": {
        "name": "Spirit World", "type": "active", "source": "found",
        "desc": "[RARE] Pull enemy into spirit world: they lose 40% HP instantly.", "mp_cost": 55,
        "target": "enemy", "special": "spirit_world_dmg", "color": (190, 190, 255),
    },
    "transcendence": {
        "name": "Transcendence", "type": "active", "source": "found",
        "desc": "[RARE] Transcend mortality: all stats +100% for 3 turns.", "mp_cost": 80,
        "target": "self",
        "buff": {"atk_mult": 2.0, "def_mult": 2.0, "spd_mult": 2.0, "int_mult": 2.0, "turns": 3},
        "color": (255, 255, 255),
    },
}

# Quick lookup for found-only skills (spawned in rare world locations)
FOUND_SKILLS = [k for k, v in SKILLS.items() if v.get("source") == "found"]
