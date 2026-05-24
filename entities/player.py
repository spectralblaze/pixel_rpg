"""Player entity — stats, inventory, equipment, skills, level-up."""
import math
import copy
from settings import *
from data.classes_data import CLASSES
from data.skills_data import SKILLS


EQUIP_SLOTS = ["weapon","armor_head","armor_chest","armor_legs","armor_hands","armor_feet",
               "ring1","ring2","amulet","belt"]


class Player:
    def __init__(self, name: str, base_class: str):
        self.name = name
        self.base_class = base_class
        self.char_class = base_class
        self.subclass_chosen = False

        self.level = 1
        self.exp = 0

        base = CLASS_STATS[base_class].copy()
        self.max_hp  = base["hp"]
        self.max_mp  = base["mp"]
        self.base_atk = base["atk"]
        self.base_def = base["def"]
        self.base_spd = base["spd"]
        self.base_int = base["int"]
        self.base_lck = base["lck"]

        self.hp = self.max_hp
        self.mp = self.max_mp

        self.gold = 200
        self.position_biome = "verdant_plains"
        self.position_x = -1   # sentinel — safe_entry_pos() sets real coords
        self.position_y = -1   # on first _make_exploration() call

        self.inventory = []           # list of {item_id, qty, rarity}
        self.equipment = {s: None for s in EQUIP_SLOTS}
        self.known_skills = list(CLASSES[base_class]["start_skills"])
        self.passive_bonuses = {}     # accumulated passive effects
        self.status_effects = {}      # {effect_name: turns_remaining}
        self.buffs = {}               # {buff_name: {value, turns}}

        self.discovered_biomes = {"verdant_plains"}
        self.unlocked_biomes = {"verdant_plains"}
        self.defeated_bosses = set()
        self.story_flags = set()
        self.quests = {}

        self.active_pet = None        # Pet object or None
        self.stored_pets = []         # list of Pet objects

        self.steps = 0
        self.battles_won = 0
        self.repel_steps = 0          # monster repellent counter
        self.indomitable_used = False  # reset per battle
        self.resurrection_used = False
        self.vanished = False
        self.shadow_clone_active = False
        self.trap_set = False
        self.has_extra_turn = False

    # ── Derived stats ────────────────────────────────────────────────────────
    @property
    def atk(self):
        bonus = sum(self._equipment_stat("atk"))
        passive = self.passive_bonuses.get("atk", 0)
        return max(1, self.base_atk + bonus + passive)

    @property
    def defense(self):
        bonus = sum(self._equipment_stat("def"))
        passive = self.passive_bonuses.get("def", 0)
        return max(0, self.base_def + bonus + passive)

    @property
    def spd(self):
        bonus = sum(self._equipment_stat("spd"))
        passive = self.passive_bonuses.get("spd", 0)
        return max(1, self.base_spd + bonus + passive)

    @property
    def intelligence(self):
        bonus = sum(self._equipment_stat("int"))
        passive = self.passive_bonuses.get("int", 0)
        return max(1, self.base_int + bonus + passive)

    @property
    def luck(self):
        bonus = sum(self._equipment_stat("lck"))
        passive = self.passive_bonuses.get("lck", 0)
        return max(1, self.base_lck + bonus + passive)

    def _equipment_stat(self, stat: str):
        from data.items_data import ITEMS
        for slot, item_id in self.equipment.items():
            if item_id and item_id in ITEMS:
                item = ITEMS[item_id]
                stats = item.get("stats", {})
                if stat in stats:
                    yield stats[stat]

    # ── EXP / level ──────────────────────────────────────────────────────────
    def exp_needed(self, level=None):
        lvl = level or self.level
        return int(EXP_BASE * (EXP_SCALE ** (lvl - 1)))

    def gain_exp(self, amount: int):
        """Returns list of level-up messages."""
        messages = []
        self.exp += amount
        while self.level < MAX_LEVEL and self.exp >= self.exp_needed():
            self.exp -= self.exp_needed()
            self.level += 1
            self._apply_level_up()
            messages.append(f"Level UP!  Now level {self.level}")
            new_skill = self._check_level_skills()
            if new_skill:
                messages.append(f"Learned: {SKILLS[new_skill]['name']}!")
        return messages

    def _apply_level_up(self):
        growth = CLASS_GROWTH[self.base_class]
        self.max_hp  += growth["hp"]
        self.max_mp  += growth["mp"]
        self.base_atk = round(self.base_atk + growth["atk"], 1)
        self.base_def = round(self.base_def + growth["def"], 1)
        self.base_spd = round(self.base_spd + growth["spd"], 1)
        self.base_int = round(self.base_int + growth["int"], 1)
        self.base_lck = round(self.base_lck + growth["lck"], 1)
        self.hp  = min(self.hp + growth["hp"], self.max_hp)
        self.mp  = min(self.mp + growth["mp"], self.max_mp)

    def _check_level_skills(self):
        level_skills = CLASSES[self.char_class].get("level_skills", {})
        if self.level in level_skills:
            skill_id = level_skills[self.level]
            if skill_id not in self.known_skills:
                self.known_skills.append(skill_id)
                return skill_id
        return None

    # ── Subclass selection ───────────────────────────────────────────────────
    def choose_subclass(self, subclass_id: str):
        cls = CLASSES[subclass_id]
        self.char_class = subclass_id
        self.subclass_chosen = True
        bonus = cls.get("bonus", {})
        for stat, val in bonus.items():
            if stat == "hp":
                self.max_hp += val; self.hp = min(self.hp + val, self.max_hp)
            elif stat == "mp":
                self.max_mp += val; self.mp = min(self.mp + val, self.max_mp)
            elif stat == "atk":  self.base_atk += val
            elif stat == "def":  self.base_def += val
            elif stat == "spd":  self.base_spd += val
            elif stat == "int":  self.base_int += val
            elif stat == "lck":  self.base_lck += val
        for sk in cls.get("start_skills", []):
            if sk not in self.known_skills:
                self.known_skills.append(sk)

    # ── Inventory helpers ────────────────────────────────────────────────────
    def add_item(self, item_id: str, qty: int = 1, rarity: str = "common"):
        for entry in self.inventory:
            if entry["id"] == item_id and entry.get("rarity") == rarity:
                entry["qty"] += qty
                return True
        if len(self.inventory) >= MAX_INV_SLOTS:
            return False
        self.inventory.append({"id": item_id, "qty": qty, "rarity": rarity})
        return True

    def remove_item(self, item_id: str, qty: int = 1):
        for entry in self.inventory:
            if entry["id"] == item_id:
                if entry["qty"] <= qty:
                    self.inventory.remove(entry)
                else:
                    entry["qty"] -= qty
                return True
        return False

    def has_item(self, item_id: str) -> bool:
        return any(e["id"] == item_id for e in self.inventory)

    def item_count(self, item_id: str) -> int:
        for e in self.inventory:
            if e["id"] == item_id:
                return e["qty"]
        return 0

    def equip_item(self, item_id: str):
        from data.items_data import ITEMS
        if item_id not in ITEMS:
            return False, "Unknown item"
        item = ITEMS[item_id]
        slot = item["type"]
        if slot.startswith("armor_"):
            pass  # armor_head etc
        elif slot == "ring":
            slot = "ring1" if self.equipment["ring1"] is None else "ring2"
        if slot not in self.equipment:
            return False, f"Cannot equip {item['name']}"
        # Unequip current
        if self.equipment[slot]:
            self.add_item(self.equipment[slot])
        self.equipment[slot] = item_id
        self.remove_item(item_id)
        self._rebuild_passives()
        return True, f"Equipped {item['name']}"

    def unequip_slot(self, slot: str):
        if self.equipment.get(slot):
            item_id = self.equipment[slot]
            if self.add_item(item_id):
                self.equipment[slot] = None
                self._rebuild_passives()
                return True
        return False

    def _rebuild_passives(self):
        """Recalculate all passive bonuses from skills."""
        self.passive_bonuses = {}
        for sk_id in self.known_skills:
            sk = SKILLS.get(sk_id, {})
            if sk.get("type") == "passive":
                for stat, val in sk.get("passive_bonus", {}).items():
                    self.passive_bonuses[stat] = self.passive_bonuses.get(stat, 0) + val

    def learn_skill(self, skill_id: str):
        if skill_id not in self.known_skills:
            self.known_skills.append(skill_id)
            self._rebuild_passives()
            return True
        return False

    # ── Combat helpers ───────────────────────────────────────────────────────
    def heal(self, amount: int):
        old = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        return self.hp - old

    def restore_mp(self, amount: int):
        old = self.mp
        self.mp = min(self.mp + amount, self.max_mp)
        return self.mp - old

    def take_damage(self, amount: int):
        amount = max(1, amount)
        if self.status_effects.get("shield", 0) > 0:
            absorbed = min(amount, self.buffs.get("shield", {}).get("value", 0))
            amount -= absorbed
            if amount <= 0:
                return 0
        self.hp = max(0, self.hp - amount)
        return amount

    def is_alive(self):
        return self.hp > 0

    def use_consumable(self, item_id: str, combat_target=None) -> list:
        """Returns list of result messages.

        combat_target  — the MonsterInstance currently being fought, or None
                         when used from the inventory screen outside of battle.
                         Required for damage/status effects that target the enemy.
        """
        from data.items_data import ITEMS
        item = ITEMS.get(item_id, {})
        if item.get("type") != "consumable":
            return ["That's not a consumable!"]
        effect = item.get("effect", {})
        msgs = []

        # ── Effects that target the enemy ─────────────────────────────────────
        # Damage (fire_bomb, ice_bomb, etc.)
        if "damage" in effect:
            if combat_target is None:
                return ["Can only be used in battle!"]
            eff_d  = effect["damage"]
            amount = eff_d["amount"]
            etype  = eff_d.get("type", "none")
            from systems.combat import elemental_mult
            mult     = elemental_mult(etype, getattr(combat_target, "element", "none"))
            final    = int(amount * mult)
            actual   = combat_target.take_damage(final)
            tag = ""
            if mult > 1.0: tag = " SUPER EFFECTIVE!"
            elif mult < 1.0: tag = " Not very effective..."
            msgs.append(f"{item['name']} deals {actual} {etype} damage!{tag}")

        # Status infliction on enemy (confusion_powder, jungle_toxin)
        if "status" in effect:
            if combat_target is None:
                return ["Can only be used in battle!"]
            for sname, sval in effect["status"].items():
                combat_target.status_effects[sname] = sval
                msgs.append(f"{combat_target.name} is afflicted with {sname.title()} for {sval} turns!")

        # ── Self-effects ──────────────────────────────────────────────────────
        if "heal" in effect:
            restored = self.heal(effect["heal"])
            msgs.append(f"Restored {restored} HP")
        if "heal_full" in effect:
            self.heal(self.max_hp)
            msgs.append("Fully restored HP")
        if "mp" in effect:
            restored = self.restore_mp(effect["mp"])
            msgs.append(f"Restored {restored} MP")
        if "mp_full" in effect:
            self.restore_mp(self.max_mp)
            msgs.append("Fully restored MP")
        if "cure" in effect:
            for status in effect["cure"]:
                self.status_effects.pop(status, None)
            msgs.append("Cured " + ", ".join(effect["cure"]))
        if "cure_all" in effect:
            self.status_effects.clear()
            msgs.append("Cured all status effects")
        if "buff" in effect:
            buff = effect["buff"]
            self.buffs[f"item_{item_id}"] = dict(buff)
            msgs.append("Gained a buff!")

        # Revive / emergency heal
        if "revive" in effect:
            frac = effect["revive"]
            amount = int(self.max_hp * frac)
            if self.hp <= 0:
                self.hp = amount
                msgs.append(f"Revived with {amount} HP!")
            else:
                restored = self.heal(amount)
                msgs.append(f"Restored {restored} HP")

        # Permanent stat boost (seeds, philosopher's stone)
        if "perm_stat" in effect:
            labels = []
            for stat, val in effect["perm_stat"].items():
                if   stat == "atk": self.base_atk += val;  labels.append(f"ATK+{val}")
                elif stat == "def": self.base_def += val;  labels.append(f"DEF+{val}")
                elif stat == "int": self.base_int += val;  labels.append(f"INT+{val}")
                elif stat == "spd": self.base_spd += val;  labels.append(f"SPD+{val}")
                elif stat == "lck": self.base_lck += val;  labels.append(f"LCK+{val}")
                elif stat == "hp":
                    self.max_hp += val
                    self.hp = min(self.hp + val, self.max_hp)
                    labels.append(f"MaxHP+{val}")
                elif stat == "mp":
                    self.max_mp += val
                    self.mp = min(self.mp + val, self.max_mp)
                    labels.append(f"MaxMP+{val}")
            msgs.append(f"Permanently gained: {', '.join(labels)}!")

        # Repel encounters
        if "repel_steps" in effect:
            self.repel_steps = effect["repel_steps"]
            msgs.append(f"Monsters will avoid you for {effect['repel_steps']} steps!")

        # Escape from battle (smoke_bomb, teleport_scroll)
        if "escape" in effect:
            msgs.append("ESCAPE")   # CombatScreen._player_do intercepts this tag

        self.remove_item(item_id)
        return msgs

    # ── Serialization ────────────────────────────────────────────────────────
    def to_dict(self):
        return {
            "name": self.name,
            "base_class": self.base_class,
            "char_class": self.char_class,
            "subclass_chosen": self.subclass_chosen,
            "level": self.level,
            "exp": self.exp,
            "max_hp": self.max_hp,
            "max_mp": self.max_mp,
            "hp": self.hp,
            "mp": self.mp,
            "base_atk": self.base_atk,
            "base_def": self.base_def,
            "base_spd": self.base_spd,
            "base_int": self.base_int,
            "base_lck": self.base_lck,
            "gold": self.gold,
            "position_biome": self.position_biome,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "inventory": self.inventory,
            "equipment": self.equipment,
            "known_skills": self.known_skills,
            "discovered_biomes": list(self.discovered_biomes),
            "unlocked_biomes": list(self.unlocked_biomes),
            "defeated_bosses": list(self.defeated_bosses),
            "story_flags": list(self.story_flags),
            "battles_won": self.battles_won,
            "repel_steps": self.repel_steps,
            "active_pet": self.active_pet.to_dict() if self.active_pet else None,
            "stored_pets": [p.to_dict() for p in self.stored_pets],
        }

    @classmethod
    def from_dict(cls, data: dict):
        from entities.pet import Pet
        p = cls.__new__(cls)
        for key, val in data.items():
            if key in ("discovered_biomes", "unlocked_biomes", "defeated_bosses", "story_flags"):
                setattr(p, key, set(val))
            elif key == "active_pet":
                p.active_pet = Pet.from_dict(val) if val else None
            elif key == "stored_pets":
                p.stored_pets = [Pet.from_dict(pd) for pd in val]
            else:
                setattr(p, key, val)
        p.status_effects = {}
        p.buffs = {}
        p.passive_bonuses = {}
        p.steps = 0
        if not hasattr(p, 'repel_steps'):
            p.repel_steps = 0
        p.indomitable_used = False
        p.resurrection_used = False
        p.vanished = False
        p.shadow_clone_active = False
        p.trap_set = False
        p.has_extra_turn = False
        p._rebuild_passives()
        return p
