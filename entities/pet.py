"""Pet system — capture, level, evolve."""
import random
from settings import MAX_PET_LEVEL, PET_CAPTURE_BASE
from data.monsters_data import MONSTERS


EVO_THRESHOLD = 0.5    # pet evolves at 50% of max pet level
EVO_THRESHOLD2 = 0.85  # second evolution at 85%


def capture_chance(monster, player) -> float:
    """Calculate capture probability."""
    hp_ratio = monster.hp / monster.max_hp
    base = PET_CAPTURE_BASE
    # Lower HP = higher chance
    hp_bonus = (1.0 - hp_ratio) * 0.4
    # Luck bonus
    lck_bonus = player.luck * 0.002
    # Beastmaster bonus
    if player.char_class == "beastmaster":
        base *= 1.6
    # beast_taming passive
    if "beast_taming" in player.known_skills:
        base *= 1.25
    chance = min(0.95, base + hp_bonus + lck_bonus)
    if not monster.capturable:
        chance *= 0.1
    return chance


class Pet:
    def __init__(self, monster_id: str, name: str = None, level: int = 1):
        base = MONSTERS[monster_id]
        self.monster_id = monster_id
        self.name = name or base["name"]
        self.level = level
        self.evo_stage = 0       # 0=base, 1=first evo, 2=second evo
        self.exp = 0

        # Derive base stats from monster
        self.base_atk  = base["atk"]
        self.base_def  = base["def"]
        self.base_hp   = base["hp"]
        self.base_spd  = base["spd"]
        self.element   = base["element"]
        self.color     = list(base["color"])
        self.abilities = list(base.get("abilities", []))[:3]
        self.evolve_name = base.get("evolve_name")

        self.max_hp = self._calc_stat(self.base_hp)
        self.hp     = self.max_hp
        self.atk    = self._calc_stat(self.base_atk)
        self.defense = self._calc_stat(self.base_def)
        self.spd    = self._calc_stat(self.base_spd)

        self.status_effects = {}

    def _calc_stat(self, base_val: int) -> int:
        growth = 1.0 + self.level * 0.08 + self.evo_stage * 0.3
        return max(1, int(base_val * growth))

    def _refresh_stats(self):
        old_max = self.max_hp
        self.max_hp  = self._calc_stat(self.base_hp)
        self.atk     = self._calc_stat(self.base_atk)
        self.defense = self._calc_stat(self.base_def)
        self.spd     = self._calc_stat(self.base_spd)
        # Keep HP ratio
        if old_max > 0:
            ratio = self.hp / old_max
            self.hp = max(1, int(self.max_hp * ratio))

    def exp_needed(self):
        return int(50 * (1.4 ** (self.level - 1)))

    def gain_exp(self, amount: int) -> list:
        msgs = []
        self.exp += amount
        while self.level < MAX_PET_LEVEL and self.exp >= self.exp_needed():
            self.exp -= self.exp_needed()
            self.level += 1
            self._refresh_stats()
            msgs.append(f"{self.name} reached level {self.level}!")
            evo_msg = self._check_evolve()
            if evo_msg:
                msgs.append(evo_msg)
        return msgs

    def _check_evolve(self) -> str:
        if self.evo_stage == 0 and self.level >= int(MAX_PET_LEVEL * EVO_THRESHOLD):
            if self.evolve_name and self.evolve_name in MONSTERS:
                self._evolve_to(self.evolve_name, 1)
                return f"{self.name} evolved into {self.name}!"
        if self.evo_stage == 1 and self.level >= int(MAX_PET_LEVEL * EVO_THRESHOLD2):
            # Second evolution: boost stats significantly
            self.evo_stage = 2
            self.color = [min(255, c + 40) for c in self.color]
            self._refresh_stats()
            return f"{self.name} reached its ultimate form!"
        return ""

    def _evolve_to(self, monster_id: str, stage: int):
        base = MONSTERS[monster_id]
        self.monster_id = monster_id
        old_name = self.name
        self.name = base["name"]   # rename to evolved form
        self.evo_stage = stage
        self.base_atk  = base["atk"]
        self.base_def  = base["def"]
        self.base_hp   = base["hp"]
        self.base_spd  = base["spd"]
        self.element   = base["element"]
        self.color     = list(base["color"])
        # Add new abilities
        for ab in base.get("abilities", []):
            if ab not in self.abilities:
                self.abilities.append(ab)
        self.evolve_name = base.get("evolve_name")
        self._refresh_stats()

    def action(self) -> dict:
        if not self.abilities:
            return {"type": "pet_attack", "power": 1.0}
        ability = random.choice(self.abilities)
        return {"type": "pet_ability", "ability": ability}

    def restore(self):
        self.hp = self.max_hp
        self.status_effects.clear()

    def take_damage(self, amount: int) -> int:
        amount = max(1, amount)
        self.hp = max(0, self.hp - amount)
        return amount

    def is_alive(self):
        return self.hp > 0

    def to_dict(self):
        return {
            "monster_id": self.monster_id,
            "name": self.name,
            "level": self.level,
            "evo_stage": self.evo_stage,
            "exp": self.exp,
            "base_atk": self.base_atk,
            "base_def": self.base_def,
            "base_hp": self.base_hp,
            "base_spd": self.base_spd,
            "element": self.element,
            "color": self.color,
            "abilities": self.abilities,
            "evolve_name": self.evolve_name,
            "hp": self.hp,
            "max_hp": self.max_hp,
        }

    @classmethod
    def from_dict(cls, d: dict):
        pet = cls.__new__(cls)
        pet.monster_id   = d["monster_id"]
        pet.name         = d["name"]
        pet.level        = d["level"]
        pet.evo_stage    = d["evo_stage"]
        pet.exp          = d["exp"]
        pet.base_atk     = d["base_atk"]
        pet.base_def     = d["base_def"]
        pet.base_hp      = d["base_hp"]
        pet.base_spd     = d["base_spd"]
        pet.element      = d["element"]
        pet.color        = d["color"]
        pet.abilities    = d["abilities"]
        pet.evolve_name  = d["evolve_name"]
        pet.max_hp       = d["max_hp"]
        pet.hp           = d["hp"]
        pet.atk          = pet._calc_stat(pet.base_atk)
        pet.defense      = pet._calc_stat(pet.base_def)
        pet.spd          = pet._calc_stat(pet.base_spd)
        pet.status_effects = {}
        return pet
