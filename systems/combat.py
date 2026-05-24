"""Turn-based combat engine.
Returns structured result objects consumed by the combat screen.
"""
import random
import math
from data.skills_data import SKILLS
from data.items_data  import ITEMS


# ── Elemental type chart (attacker element vs defender element) ──────────────
ELEMENT_CHART = {
    # attacker -> {defender -> multiplier}
    "fire":      {"ice":1.5,  "nature":1.5, "fire":0.5, "water":0.5},
    "ice":       {"fire":0.5, "lightning":0.5, "water":1.0, "ice":0.5, "nature":0.5},
    "lightning": {"water":1.5, "earth":1.5, "lightning":0.5},
    "water":     {"fire":1.5, "earth":1.5, "water":0.5},
    "nature":    {"water":1.5, "earth":1.5, "dark":1.5, "nature":0.5},
    "earth":     {"lightning":0.5, "fire":0.5},
    "holy":      {"dark":2.0, "holy":0.5},
    "dark":      {"holy":0.5, "light":0.5},
    "arcane":    {},
    "elemental": {},   # combined elements
    "none":      {},
}


def elemental_mult(atk_element: str, def_element: str) -> float:
    chart = ELEMENT_CHART.get(atk_element, {})
    return chart.get(def_element, 1.0)


# ── Core damage formula ───────────────────────────────────────────────────────
def calc_damage(attacker_atk: int, defender_def: int, power: float = 1.0,
                use_int: int = 0, crit_chance: float = 0.05, crit_mult: float = 2.0,
                element: str = "none", def_element: str = "none",
                def_pierce: float = 0.0) -> tuple:
    """Returns (damage, is_crit, element_tag)."""
    eff_def = int(defender_def * (1.0 - def_pierce))
    base = max(1, (attacker_atk if not use_int else use_int) - eff_def // 2)
    dmg = int(base * power * random.uniform(0.88, 1.12))
    is_crit = random.random() < crit_chance
    if is_crit:
        dmg = int(dmg * crit_mult)
    elem_mult = elemental_mult(element, def_element)
    dmg = int(dmg * elem_mult)
    tag = ""
    if elem_mult > 1.0:
        tag = "SUPER EFFECTIVE!"
    elif elem_mult < 1.0:
        tag = "Not very effective..."
    return max(1, dmg), is_crit, tag


# ── Player action processor ───────────────────────────────────────────────────
def process_player_action(action: dict, player, monster, pet=None) -> list:
    """
    Process a single player action.
    Returns list of message strings for the battle log.
    action = {
        'type': 'attack'|'skill'|'item'|'pet'|'flee',
        'skill_id': str,   (if skill)
        'item_id':  str,   (if item)
    }
    """
    msgs = []
    atype = action.get("type")

    if atype == "attack":
        msgs += _player_basic_attack(player, monster)

    elif atype == "skill":
        msgs += _player_use_skill(action["skill_id"], player, monster, pet)

    elif atype == "item":
        msgs += player.use_consumable(action["item_id"], combat_target=monster)

    elif atype == "pet":
        if pet and pet.is_alive():
            msgs += _pet_action(pet, player, monster)
        else:
            msgs.append("No active pet!")

    elif atype == "flee":
        msgs.append("FLEE")  # combat screen handles flee logic

    elif atype == "capture":
        msgs.append("CAPTURE")  # combat screen handles

    return msgs


def _player_basic_attack(player, monster) -> list:
    msgs = []
    # Vanish backstab
    power = 1.0
    crit_bonus = 0.0
    if player.vanished:
        power = 2.0
        crit_bonus = 1.0   # guaranteed crit
        player.vanished = False
        msgs.append("Backstab from the shadows!")
    if player.trap_set:
        player.trap_set = False

    # Accuracy check (smoke bomb etc)
    if monster.status_effects.get("blinded", 0) > 0:
        if random.random() < 0.5:
            msgs.append(f"{monster.name} dodged!")
            return msgs

    # Shadow instinct passive
    crit_chance = 0.05 + crit_bonus
    if "shadow_instinct" in player.known_skills:
        crit_chance += 0.15
    crit_mult = 2.0
    if "shadow_instinct" in player.known_skills:
        crit_mult = 3.0

    # Apply death_mark
    power_mult = 1.0
    if monster.buffs.get("death_mark"):
        power_mult = monster.buffs["death_mark"].get("dmg_taken_mult", 1.0)
        del monster.buffs["death_mark"]

    dmg, is_crit, tag = calc_damage(
        player.atk, monster.effective_def,
        power=power * power_mult,
        crit_chance=crit_chance, crit_mult=crit_mult,
        def_element=monster.element,
    )

    # Eagle eye
    if "eagle_eye" in player.known_skills:
        dmg = int(dmg * 1.1)

    dmg = _apply_player_atk_buffs(dmg, player)
    actual = monster.take_damage(dmg)
    msg = f"You attack {monster.name} for {actual} damage!"
    if is_crit: msg += " CRITICAL HIT!"
    if tag: msg += f" {tag}"
    msgs.append(msg)

    # Lifesteal weapons
    weapon = player.equipment.get("weapon")
    if weapon and ITEMS.get(weapon, {}).get("special") == "lifesteal_30":
        heal = int(actual * 0.3)
        player.heal(heal)
        msgs.append(f"Drained {heal} HP!")

    # Thorns
    thorns_pct = monster.buffs.get("thorns", {}).get("thorns", 0)
    if thorns_pct:
        refl = max(1, int(actual * thorns_pct))
        player.take_damage(refl)
        msgs.append(f"Reflected {refl} damage from thorns!")

    return msgs


def _apply_player_atk_buffs(dmg: int, player) -> int:
    mult = 1.0
    for buff in player.buffs.values():
        mult *= buff.get("atk_mult", 1.0)
        mult *= buff.get("spell_power", 1.0)
    if "spell_mastery" in player.known_skills:
        mult *= 1.25
    return int(dmg * mult)


def _player_use_skill(skill_id: str, player, monster, pet) -> list:
    msgs = []
    if skill_id not in SKILLS:
        return ["Unknown skill!"]
    sk = SKILLS[skill_id]

    # MP check
    cost = sk["mp_cost"]
    # mp discount passive
    if "spell_haste" in player.known_skills:
        cost = int(cost * 0.85)
    if player.mp < cost:
        return [f"Not enough MP! (need {cost})"]
    player.mp = max(0, player.mp - cost)

    target = sk.get("target", "enemy")
    dmg_type = sk.get("dmg_type", "physical")
    power = sk.get("power", 1.0)
    use_int = player.intelligence if sk.get("use_int") else 0
    hits = sk.get("hits", 1)
    special = sk.get("special", "")

    # Buff self
    if "buff_self" in sk:
        _apply_buff_to_entity(player, sk["buff_self"])

    if target in ("enemy", "all_enemies"):
        # Damage skill
        for h in range(hits):
            if not monster.is_alive():
                break
            crit_chance = 0.05
            crit_mult = 2.0
            if "shadow_instinct" in player.known_skills:
                crit_chance += 0.15; crit_mult = 3.0

            dmg, is_crit, tag = calc_damage(
                player.atk, monster.effective_def,
                power=power,
                use_int=use_int,
                crit_chance=crit_chance, crit_mult=crit_mult,
                element=dmg_type, def_element=monster.element,
                def_pierce=0.3 if "eagle_eye" in player.known_skills else 0.0,
            )
            dmg = _apply_player_atk_buffs(dmg, player)

            # death_mark
            if monster.buffs.get("death_mark"):
                dmg = int(dmg * monster.buffs["death_mark"].get("dmg_taken_mult", 1.0))
                del monster.buffs["death_mark"]

            # dmg_taken_mult debuff
            if monster.buffs.get("demon_brand"):
                dmg = int(dmg * monster.buffs["demon_brand"].get("dmg_taken_mult", 1.0))

            # smite_dark
            if special == "smite_dark" and monster.element in ("dark","undead","shadow"):
                monster.hp = 0
                msgs.append(f"SMITE! {monster.name} is destroyed!")
                return msgs

            # execute_20pct
            if special == "execute_20pct" and monster.hp / monster.max_hp < 0.20:
                monster.hp = 0
                msgs.append(f"Coup de Grace! {monster.name} is slain!")
                return msgs

            actual = monster.take_damage(dmg)
            msg = f"{sk['name']} hits {monster.name} for {actual}"
            if hits > 1: msg += f" (hit {h+1})"
            msg += "!"
            if is_crit: msg += " CRITICAL HIT!"
            if tag: msg += f" {tag}"
            msgs.append(msg)

            # Lifesteal
            if special == "lifesteal_50" or "lifesteal" in special:
                heal = int(actual * 0.5)
                player.heal(heal)
                msgs.append(f"Drained {heal} HP!")

            # Spirit world
            if special == "spirit_world_dmg":
                bonus = int(monster.max_hp * 0.40)
                monster.take_damage(bonus)
                msgs.append(f"Spirit World deals {bonus} additional damage!")

        # Apply status
        if "status" in sk and monster.is_alive():
            for status, val in sk["status"].items():
                if status == "chance":
                    continue
                chance = sk["status"].get("chance", 1.0)
                if random.random() < chance:
                    monster.status_effects[status] = val
                    msgs.append(f"{monster.name} is afflicted with {status.title()} for {val} turns!")

        # Apply debuff
        if "debuff" in sk and monster.is_alive():
            _apply_buff_to_entity(monster, sk["debuff"])
            msgs.append(f"{monster.name}'s stats are reduced!")

        # strip_buffs
        if special == "strip_buffs":
            monster.buffs.clear()
            msgs.append(f"{monster.name}'s buffs were stripped!")

    elif target == "self":
        # Heal
        if "heal_pct" in sk:
            amount = int(player.max_hp * sk["heal_pct"])
            restored = player.heal(amount)
            msgs.append(f"{sk['name']}: Restored {restored} HP!")

        # Full restore
        if special == "full_restore":
            player.heal(player.max_hp)
            player.status_effects.clear()
            msgs.append("Fully restored HP and cured all status effects!")

        # Buff
        if "buff" in sk:
            _apply_buff_to_entity(player, sk["buff"])
            msgs.append(f"{sk['name']}: Applied buff!")

        # Special self-effects
        if special == "mana_shield":
            player.buffs["mana_shield"] = {"mana_shield": True, "turns": 3}
            msgs.append("Mana Shield activated! Damage hits MP first!")
        elif special == "shadow_clone":
            player.shadow_clone_active = True
            msgs.append("Shadow Clone created! It will take the next hit for you!")
        elif special == "vanish":
            player.vanished = True
            msgs.append("You vanish into the shadows! Next attack is guaranteed critical!")
        elif special == "fate_read":
            player.buffs["fate_read"] = {"fate_read": True, "turns": 1}
            msgs.append("You read fate. You will dodge the next attack and counter!")
        elif special == "extra_turn":
            player.has_extra_turn = True
            msgs.append("Time stops. You gain an extra action!")
        elif special == "trap":
            player.trap_set = True
            msgs.append("Trap set! It will spring when the enemy attacks!")
        elif special == "resurrection":
            player.resurrection_used = False  # rearm it
            player.buffs["resurrection"] = {"resurrection": True, "turns": 99}
            msgs.append("Resurrection: You will survive a fatal blow at 1 HP!")
        elif special == "self_dmg_20pct":
            dmg = int(player.max_hp * 0.20)
            player.take_damage(dmg)
            msgs.append(f"Dark Pact: Sacrificed {dmg} HP for power!")
        elif special == "cleanse_one":
            if player.status_effects:
                effect = next(iter(player.status_effects))
                del player.status_effects[effect]
                msgs.append(f"Cleansed {effect}!")
        elif special == "cleanse_all":
            player.status_effects.clear()
            msgs.append("All status effects removed!")
        elif special == "dark_step":
            player.buffs["dark_step"] = {"dark_step": True, "turns": 1}
            msgs.append("Dark Step! Next attack will be evaded, then countered!")
        elif special == "capture":
            msgs.append("CAPTURE")   # combat screen handles
        elif special == "omega_capture":
            msgs.append("OMEGA_CAPTURE")

        # Pet combat actions (require an active living pet)
        elif special in ("pet_attack_150", "pet_attack_250", "pet_buff_60_3t"):
            if pet and pet.is_alive():
                if special == "pet_attack_150":
                    dmg = int(pet.atk * 1.5)
                    monster.take_damage(dmg)
                    msgs.append(f"{pet.name} attacks for {dmg}!")
                elif special == "pet_attack_250":
                    dmg = int(pet.atk * 2.5)
                    monster.take_damage(dmg)
                    msgs.append(f"{pet.name} unleashes a primal surge for {dmg}!")
                elif special == "pet_buff_60_3t":
                    pet.atk = int(pet.atk * 1.6)
                    msgs.append(f"{pet.name}'s power surges!")
            else:
                msgs.append("No active pet to command!")

        # Summon Familiar — summoner unique: conjures a spirit even without a captured pet
        elif special == "summon_familiar":
            from entities.pet import Pet as _Pet
            if not pet or not pet.is_alive():
                spirit = _Pet("green_slime", "Spirit Familiar")
                # Override all stats to be INT-scaled for the summoner
                spirit.base_hp   = max(10, int(player.max_hp  * 0.35))
                spirit.base_atk  = max(5,  int(player.intelligence * 0.90))
                spirit.base_def  = max(2,  int(player.intelligence * 0.35))
                spirit.base_spd  = max(5,  player.spd)
                spirit.level     = max(1, player.level)
                spirit.element   = "arcane"
                spirit.color     = [160, 100, 240]
                spirit.abilities = ["phantom_touch", "soul_scream"]
                spirit.evolve_name = None
                spirit._refresh_stats()
                spirit.hp = spirit.max_hp
                player.active_pet = spirit
                msgs.append(
                    f"A Spirit Familiar materialises at your side!  "
                    f"ATK:{spirit.atk}  HP:{spirit.max_hp}"
                )
            else:
                # Pet already active — empower it with spirit energy
                heal = int(pet.max_hp * 0.40)
                pet.hp = min(pet.max_hp, pet.hp + heal)
                old_atk = pet.atk
                pet.atk = int(pet.atk * 1.10)
                msgs.append(
                    f"Spirit energy flows into {pet.name}!  "
                    f"+{heal} HP  ATK {old_atk}->{pet.atk}"
                )

    # Regen buff
    if "buff" in sk and "hp_regen_pct" in sk.get("buff", {}):
        msgs.append(f"Regeneration active: {int(sk['buff']['hp_regen_pct']*100)}% HP/turn for {sk['buff']['turns']} turns")

    return msgs


def _apply_buff_to_entity(entity, buff_data: dict):
    key = f"buff_{random.randint(1000,9999)}"
    entity.buffs[key] = dict(buff_data)


def _pet_action(pet, player, monster) -> list:
    """Legacy helper — delegates to the shared basic-attack function."""
    return _pet_basic_attack(pet, player, monster)


# ── Monster action processor ──────────────────────────────────────────────────
def process_monster_action(action: dict, monster, player, pet=None) -> list:
    msgs = []
    atype = action.get("type")

    if atype in ("stunned", "frozen", "paralyzed"):
        msgs.append(f"{monster.name} is {atype} and cannot act!")
        return msgs

    if atype == "attack":
        msgs += _monster_basic_attack(monster, player, pet)
    elif atype == "ability":
        msgs += _monster_ability(action["ability"], monster, player, pet)

    return msgs


def _monster_basic_attack(monster, player, pet=None) -> list:
    msgs = []

    # 25% chance the monster targets the active pet instead of the player
    if pet and pet.is_alive() and random.random() < 0.25:
        pet_def = getattr(pet, "defense", 0)
        pet_dmg = max(1, int((monster.effective_atk - pet_def // 2) * random.uniform(0.88, 1.12)))
        pet.hp = max(0, pet.hp - pet_dmg)
        msgs.append(f"{monster.name} attacks {pet.name} for {pet_dmg} damage!")
        if not pet.is_alive():
            msgs.append(f"{pet.name} has been defeated!")
        return msgs

    # Fate read counter
    if player.buffs.get("fate_read"):
        del player.buffs["fate_read"]
        dmg, _, _ = calc_damage(player.atk, monster.effective_def, power=1.0)
        monster.take_damage(dmg)
        msgs.append(f"You read the attack! Counter for {dmg} damage!")
        return msgs

    # Dark step
    if player.buffs.get("dark_step"):
        del player.buffs["dark_step"]
        dmg, _, _ = calc_damage(player.atk, monster.effective_def, power=1.2)
        monster.take_damage(dmg)
        msgs.append(f"You phase through the attack and counter for {dmg}!")
        return msgs

    # Shadow clone absorbs
    if player.shadow_clone_active:
        player.shadow_clone_active = False
        msgs.append("Your Shadow Clone takes the hit!")
        return msgs

    # Prophecy block
    if "prophecy_block" in player.buffs:
        pb = player.buffs["prophecy_block"]
        if pb.get("prophecy_block", 0) > 0 and random.random() < pb.get("chance", 0.7):
            pb["prophecy_block"] -= 1
            msgs.append("Prophecy Shield blocks the attack!")
            if pb["prophecy_block"] <= 0:
                del player.buffs["prophecy_block"]
            return msgs

    # Evasion
    for buff in player.buffs.values():
        evasion = buff.get("evasion", 0)
        if evasion and random.random() < evasion:
            msgs.append("You evade the attack!")
            return msgs

    dmg, is_crit, _ = calc_damage(
        monster.effective_atk, int(player.defense),
        crit_chance=0.05, crit_mult=2.0,
        element=monster.element, def_element="none",
    )

    # Damage reduction buff
    for buff in player.buffs.values():
        red = buff.get("dmg_reduction", 0)
        if red:
            dmg = int(dmg * (1.0 - red))
            break

    # Reflect
    for buff in player.buffs.values():
        ref = buff.get("reflect", 0)
        if ref:
            ref_dmg = int(dmg * ref)
            monster.take_damage(ref_dmg)
            msgs.append(f"Reflected {ref_dmg} damage!")
            break

    # Shield absorption
    for bname, buff in list(player.buffs.items()):
        shield = buff.get("shield", 0)
        if shield > 0:
            absorbed = min(dmg, shield)
            dmg -= absorbed
            buff["shield"] -= absorbed
            if buff["shield"] <= 0:
                del player.buffs[bname]
            msgs.append(f"Shield absorbed {absorbed} damage!")
            break

    # Mana shield
    if player.buffs.get("mana_shield") and player.mp > 0:
        mp_use = min(player.mp, dmg)
        dmg -= mp_use
        player.mp -= mp_use
        msgs.append(f"Mana Shield absorbed {mp_use} from MP!")

    # Destiny chain
    for buff in player.buffs.values():
        if buff.get("destiny_chain"):
            monster.take_damage(dmg * 2)
            msgs.append(f"Destiny Chain reflects {dmg*2} to {monster.name}!")
            break

    # Trap spring
    if player.trap_set:
        player.trap_set = False
        trap_dmg = int(player.atk * 1.5)
        monster.take_damage(trap_dmg)
        msgs.append(f"TRAP SPRUNG! Deals {trap_dmg} to {monster.name}!")

    if dmg > 0:
        actual = player.take_damage(dmg)
        msg = f"{monster.name} attacks you for {actual} damage!"
        if is_crit: msg += " CRITICAL HIT!"
        msgs.append(msg)

        # Indomitable check
        if not player.is_alive() and not player.indomitable_used:
            if "indomitable" in player.known_skills:
                player.hp = 1
                player.indomitable_used = True
                msgs.append("Indomitable! Survived at 1 HP!")
            elif player.buffs.get("resurrection") and not player.resurrection_used:
                player.hp = int(player.max_hp * 0.5)
                player.resurrection_used = True
                del player.buffs["resurrection"]
                msgs.append("Resurrection! Revived at 50% HP!")

    # Thorns
    for buff in player.buffs.values():
        thorns = buff.get("thorns", 0)
        if thorns and dmg > 0:
            refl = max(1, int(dmg * thorns))
            monster.take_damage(refl)
            msgs.append(f"Thorns deal {refl} to {monster.name}!")
            break

    # Death aura passive
    if "death_aura_30" in [SKILLS.get(sk, {}).get("special","") for sk in player.known_skills]:
        monster.take_damage(30)
        msgs.append("Death Aura deals 30 dark damage!")

    return msgs


# ── Shared ability lookup table (used by both monsters and pets) ──────────────
_ABILITY_TABLE = {
        "slime_tackle":    ("physical", 0.9),
        "split":           ("physical", 0.5),
        "water_jet":       ("water",    1.2),
        "bite":            ("physical", 1.1),
        "frenzy":          ("physical", 0.8),
        "gnaw":            ("physical", 0.9),
        "diseased_bite":   ("dark",     0.9),
        "howl":            ("buff",     0),
        "pack_rush":       ("physical", 1.4),
        "leader_charge":   ("physical", 1.6),
        "sting":           ("physical", 1.0),
        "poison_sting":    ("nature",   0.9),
        "swarm":           ("physical", 0.7),
        "stone_fist":      ("earth",    1.5),
        "boulder_throw":   ("earth",    1.8),
        "earth_quake":     ("earth",    2.0),
        "rock_armor":      ("buff",     0),
        "acid_splash":     ("nature",   1.1),
        "vine_wrap":       ("nature",   0.8),
        "stab":            ("physical", 1.1),
        "throw_rock":      ("earth",    0.9),
        "slash":           ("physical", 1.2),
        "battle_cry":      ("buff",     0),
        "shield_block":    ("buff",     0),
        "hex":             ("dark",     1.0),
        "nature_bolt":     ("nature",   1.3),
        "heal_self":       ("heal",     0),
        "thorn_spray":     ("nature",   1.0),
        "root_bind":       ("nature",   0.8),
        "nature_heal":     ("heal",     0),
        "bark_shield":     ("buff",     0),
        "sand_spit":       ("earth",    0.9),
        "quicksand":       ("earth",    1.1),
        "pincer_snap":     ("physical", 1.2),
        "tail_whip":       ("physical", 0.9),
        "venom_barrage":   ("nature",   1.0),
        "earth_slam":      ("earth",    1.5),
        "venom_spit":      ("nature",   1.1),
        "constrict":       ("physical", 1.3),
        "curse":           ("dark",     0.8),
        "bandage_throw":   ("physical", 0.7),
        "drain_life":      ("dark",     1.0),
        "fire_blast":      ("fire",     1.4),
        "sand_storm":      ("earth",    1.2),
        "ice_spit":        ("ice",      1.1),
        "club_smash":      ("physical", 1.4),
        "frost_breath":    ("ice",      1.5),
        "troll_regen":     ("heal",     0),
        "ice_slam":        ("ice",      1.3),
        "ice_spike":       ("ice",      1.2),
        "chill_aura":      ("buff",     0),
        "snow_punch":      ("ice",      1.1),
        "fire_claw":       ("fire",     1.1),
        "heat_breath":     ("fire",     1.4),
        "tail_sweep":      ("physical", 1.0),
        "magma_fist":      ("fire",     1.5),
        "eruption":        ("fire",     1.8),
        "fire_breath":     ("fire",     1.6),
        "claw_slash":      ("physical", 1.1),
        "wing_blast":      ("physical", 1.0),
        "phantom_touch":   ("dark",     1.0),
        "soul_scream":     ("dark",     1.2),
        "bone_arrow":      ("physical", 1.1),
        "dark_shot":       ("dark",     1.0),
        "bone_slash":      ("dark",     1.2),
        "dark_shield":     ("buff",     0),
        "crystal_spit":    ("none",     1.0),
        "prism_burst":     ("none",     1.3),
        "sonic_screech":   ("lightning",1.0),
        "dive_bite":       ("physical", 1.2),
        "wing_slash":      ("physical", 1.0),
        "blood_drain":     ("dark",     1.1),
        "lightning_spit":  ("lightning",1.1),
        "talon_strike":    ("physical", 1.2),
        "wind_slash":      ("lightning",0.9),
        "thunder_wing":    ("lightning",1.5),
        "thunder_slam":    ("lightning",1.8),
        "tongue_lash":     ("physical", 1.0),
        "swamp_leap":      ("physical", 1.1),
        "croak":           ("physical", 0.8),
        "mudball":         ("earth",    0.9),
        "toxic_tongue":    ("nature",   1.1),
        "disease_touch":   ("dark",     1.0),
        "toxic_cloud":     ("nature",   1.2),
        "putrid_slam":     ("physical", 1.3),
        "fire_spit":       ("fire",     1.0),
        "lava_pool":       ("fire",     0.9),
        "dragon_roar":     ("physical", 1.5),
        "inferno":         ("fire",     2.0),
        "rattle_bones":    ("dark",     0.7),
        "dark_nova":       ("dark",     1.3),
        "soul_harvest":    ("dark",     1.2),
        "crystal_punch":   ("none",     1.2),
        "crystallize":     ("buff",     0),
        "storm_screech":   ("lightning",1.2),
        "gale_dive":       ("lightning",1.3),
        "wind_fang":       ("lightning",1.0),
        "lightning_strike":("lightning",1.5),
        "cyclone":         ("lightning",1.4),
        "death_slash":     ("dark",     1.5),
        "undead_charge":   ("dark",     1.2),
}

# Abilities that heal or buff the user rather than dealing damage
_HEAL_BUFF_ABILITIES = frozenset({
    "troll_regen", "nature_heal", "heal_self", "rock_armor", "bark_shield",
    "chill_aura", "dark_shield", "crystallize", "battle_cry", "shield_block", "howl",
})


# ── Pet autonomous turn ───────────────────────────────────────────────────────
def process_pet_turn(pet, player, monster) -> list:
    """Pet acts on its own turn — basic attack or a random ability.

    Returns a list of log message strings.
    Never called when the pet is dead or absent (callers must check).
    """
    if not pet or not pet.is_alive():
        return []
    act = pet.action()
    if act["type"] == "pet_ability":
        return _pet_use_ability(act["ability"], pet, player, monster)
    return _pet_basic_attack(pet, player, monster)


def _pet_basic_attack(pet, player, monster) -> list:
    dmg = max(1, pet.atk - monster.effective_def // 2)
    dmg = int(dmg * random.uniform(0.9, 1.1))
    if "bond_strengthen" in player.known_skills:
        dmg = int(dmg * 1.2)
    actual = monster.take_damage(dmg)
    return [f"{pet.name} attacks {monster.name} for {actual} damage!"]


def _pet_use_ability(ability: str, pet, player, monster) -> list:
    """Pet uses one of its monster-derived abilities against the enemy."""
    # Heal/buff abilities — pet heals itself instead
    if ability in _HEAL_BUFF_ABILITIES:
        heal = max(1, int(pet.max_hp * 0.20))
        pet.hp = min(pet.max_hp, pet.hp + heal)
        return [f"{pet.name} uses {ability.replace('_', ' ').title()} and recovers {heal} HP!"]

    entry = _ABILITY_TABLE.get(ability)
    if entry is None:
        return _pet_basic_attack(pet, player, monster)

    atype, power = entry
    if atype in ("heal", "buff"):
        heal = max(1, int(pet.max_hp * 0.20))
        pet.hp = min(pet.max_hp, pet.hp + heal)
        return [f"{pet.name} uses {ability.replace('_', ' ').title()} and recovers {heal} HP!"]

    dmg, is_crit, tag = calc_damage(
        pet.atk, monster.effective_def,
        power=power,
        element=atype, def_element=monster.element,
        crit_chance=0.08, crit_mult=2.0,
    )
    if "bond_strengthen" in player.known_skills:
        dmg = int(dmg * 1.2)
    actual = monster.take_damage(dmg)
    msg = f"{pet.name} uses {ability.replace('_', ' ').title()} on {monster.name} for {actual}!"
    if is_crit: msg += " CRITICAL HIT!"
    if tag: msg += f" {tag}"
    return [msg]


# ── Monster ability processor ─────────────────────────────────────────────────
def _monster_ability(ability: str, monster, player, pet=None) -> list:
    msgs = []
    ability_table = _ABILITY_TABLE

    if ability in ability_table:
        atype, power = ability_table[ability]
        if atype == "heal":
            heal_amt = int(monster.max_hp * 0.20)
            monster.heal(heal_amt)
            msgs.append(f"{monster.name} heals {heal_amt} HP!")
            return msgs
        elif atype == "buff":
            monster.buffs[ability] = {"def_mult": 1.3, "turns": 2}
            msgs.append(f"{monster.name} uses {ability.replace('_',' ').title()}!")
            return msgs

        # Apply to player
        dmg, is_crit, tag = calc_damage(
            monster.effective_atk, int(player.defense),
            power=power, element=atype, def_element="none",
        )
        # Damage reduction
        for buff in player.buffs.values():
            red = buff.get("dmg_reduction", 0)
            if red:
                dmg = int(dmg * (1.0 - red))
                break

        # Shield
        for bname, buff in list(player.buffs.items()):
            shield = buff.get("shield", 0)
            if shield > 0:
                absorbed = min(dmg, shield)
                dmg -= absorbed
                buff["shield"] -= absorbed
                if buff["shield"] <= 0:
                    del player.buffs[bname]
                msgs.append(f"Shield absorbed {absorbed}!")
                break

        if dmg > 0:
            actual = player.take_damage(dmg)
            msg = f"{monster.name} uses {ability.replace('_',' ').title()} for {actual}!"
            if tag: msg += f" {tag}"
            msgs.append(msg)

            if not player.is_alive() and not player.indomitable_used:
                if "indomitable" in player.known_skills:
                    player.hp = 1
                    player.indomitable_used = True
                    msgs.append("Indomitable! Survived at 1 HP!")

        # Poison / status from certain abilities
        if ability in ("poison_sting","diseased_bite","venom_spit","venom_barrage","toxic_tongue","disease_touch","toxic_cloud"):
            if random.random() < 0.6:
                player.status_effects["poison"] = 3
                msgs.append("You are Poisoned!")
        if ability in ("curse","hex"):
            if random.random() < 0.5:
                player.status_effects["cursed"] = 3
                msgs.append("You are Cursed! ATK reduced.")
                player.buffs["cursed"] = {"atk_mult": 0.7, "turns": 3}
    else:
        # Unknown ability — generic attack
        dmg, is_crit, _ = calc_damage(monster.effective_atk, int(player.defense), power=1.2)
        actual = player.take_damage(dmg)
        msgs.append(f"{monster.name} uses a special ability for {actual}!")

    return msgs


# ── Player status tick ────────────────────────────────────────────────────────
def tick_player_status(player) -> list:
    msgs = []
    to_remove = []
    for effect, turns in list(player.status_effects.items()):
        if effect == "poison":
            dmg = max(1, int(player.max_hp * 0.05))
            player.take_damage(dmg)
            msgs.append(f"Poison deals {dmg} damage to you!")
        elif effect == "burn":
            dmg = max(1, int(player.max_hp * 0.06))
            player.take_damage(dmg)
            msgs.append(f"Burn deals {dmg} damage to you!")
        elif effect == "bleed":
            dmg = max(1, int(player.max_hp * 0.04))
            player.take_damage(dmg)
            msgs.append(f"You bleed for {dmg} damage!")
        player.status_effects[effect] = turns - 1
        if player.status_effects[effect] <= 0:
            to_remove.append(effect)
            msgs.append(f"{effect.title()} wore off!")
    for e in to_remove:
        del player.status_effects[e]
    # hp_regen_pct — tick once per turn (end of monster's turn)
    for buff in player.buffs.values():
        regen = buff.get("hp_regen_pct", 0)
        if regen:
            amount = int(player.max_hp * regen)
            player.heal(amount)
            msgs.append(f"Regeneration restores {amount} HP!")
            break

    # Buff tick
    for bname in list(player.buffs.keys()):
        if bname not in ("mana_shield", "shadow_clone", "fate_read", "dark_step",
                          "trap", "resurrection", "destiny_chain"):
            player.buffs[bname]["turns"] = player.buffs[bname].get("turns", 1) - 1
            if player.buffs[bname].get("turns", 0) <= 0:
                del player.buffs[bname]
    return msgs
