"""Monster entity — handles variants (alpha, evolved) and combat AI."""
import random
import copy
from settings import ALPHA_CHANCE, EVOLVED_CHANCE
from data.monsters_data import MONSTERS


class MonsterInstance:
    """A live monster in a battle, built from MONSTERS data."""

    def __init__(self, monster_id: str, player_level: int, force_variant: str = None):
        base = MONSTERS[monster_id]
        self.monster_id = monster_id
        self.base_id = monster_id

        # Roll variant
        roll = random.random()
        if force_variant:
            self.variant = force_variant
        elif roll < EVOLVED_CHANCE and base.get("evolve_name") and base["evolve_name"] in MONSTERS:
            self.variant = "evolved"
            evolved_id = base["evolve_name"]
            base = MONSTERS[evolved_id]
            self.monster_id = evolved_id
        elif roll < EVOLVED_CHANCE + ALPHA_CHANCE:
            self.variant = "alpha"
        else:
            self.variant = "normal"

        # Scale to player level
        lvl_min, lvl_max = sorted(base["level_range"])   # normalise inverted data
        lo = max(lvl_min, player_level - 3)
        hi = min(lvl_max, player_level + 3)
        if lo > hi:
            # Player is outside this monster's level band — pin to nearest end
            lo = hi = lvl_min if player_level < lvl_min else lvl_max
        self.level = max(1, random.randint(lo, hi))
        scale = 1.0 + (self.level - lvl_min) * 0.08

        alpha_mult = 2.0 if self.variant == "alpha" else 1.0

        raw_hp  = base["hp"]  * scale * alpha_mult
        raw_atk = base["atk"] * scale * alpha_mult
        raw_def = base["def"] * scale * alpha_mult
        raw_spd = base["spd"]
        raw_int = base["int"] * scale

        self.max_hp = int(raw_hp)
        self.hp     = self.max_hp
        self.atk    = int(raw_atk)
        self.defense = int(raw_def)
        self.spd    = int(raw_spd)
        self.intelligence = int(raw_int)

        self.name = base["name"]
        if self.variant == "alpha":
            self.name = "Alpha " + self.name
        elif self.variant == "evolved":
            self.name = self.name   # evolved already has its own name

        self.element   = base["element"]
        self.capturable = base["capturable"] and self.variant != "alpha"
        self.boss      = base.get("boss", False)
        self.ai_type   = base.get("ai", "random")
        self.color     = base["color"]
        self.abilities = list(base.get("abilities", []))
        self.drops     = base.get("drops", [])

        # Combat state
        self.status_effects = {}
        self.buffs = {}
        self.turn_count = 0

        # EXP / gold scaling
        exp_mult = 1.5 if self.variant == "alpha" else (1.2 if self.variant == "evolved" else 1.0)
        gold_mult = 1.5 if self.variant == "alpha" else 1.0
        self.exp_reward  = int(base["exp"]  * exp_mult * scale)
        g_min, g_max = sorted(base["gold"])   # normalise inverted data
        self.gold_reward = int(random.randint(g_min, g_max) * gold_mult)

    # ── Combat helpers ────────────────────────────────────────────────────────
    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        amount = max(1, amount)
        self.hp = max(0, self.hp - amount)
        return amount

    def heal(self, amount: int):
        self.hp = min(self.hp + amount, self.max_hp)

    # ── AI action selection ───────────────────────────────────────────────────
    def choose_action(self) -> dict:
        """Return an action dict for the combat system to process."""
        self.turn_count += 1

        if self.status_effects.get("stun", 0) > 0:
            return {"type": "stunned"}
        if self.status_effects.get("freeze", 0) > 0:
            return {"type": "frozen"}
        if self.status_effects.get("paralyze", 0) > 0 and random.random() < 0.5:
            return {"type": "paralyzed"}
        if self.status_effects.get("confuse", 0) > 0 and random.random() < 0.5:
            return {"type": "stunned"}   # confused: 50% chance to waste the turn

        hp_ratio = self.hp / self.max_hp

        if self.ai_type == "aggressive":
            # Mostly attacks, occasionally uses an ability
            if self.abilities and random.random() < 0.3:
                return {"type": "ability", "ability": random.choice(self.abilities)}
            return {"type": "attack"}

        elif self.ai_type == "defensive":
            # Heals when low, uses abilities often
            if hp_ratio < 0.35 and "heal_self" in self.abilities:
                return {"type": "ability", "ability": "heal_self"}
            if self.abilities and random.random() < 0.4:
                return {"type": "ability", "ability": random.choice(self.abilities)}
            return {"type": "attack"}

        elif self.ai_type == "magic":
            # Prefers abilities, cycles through them
            if self.abilities:
                idx = self.turn_count % len(self.abilities)
                return {"type": "ability", "ability": self.abilities[idx]}
            return {"type": "attack"}

        else:  # random
            if self.abilities and random.random() < 0.35:
                return {"type": "ability", "ability": random.choice(self.abilities)}
            return {"type": "attack"}

    # ── Status tick ──────────────────────────────────────────────────────────
    def tick_status(self) -> list:
        """Process per-turn status effects. Returns list of messages."""
        msgs = []
        to_remove = []
        for effect, turns in list(self.status_effects.items()):
            if effect == "poison":
                dmg = max(1, int(self.max_hp * 0.05))
                self.hp = max(0, self.hp - dmg)
                msgs.append(f"{self.name} takes {dmg} poison damage!")
            elif effect == "burn":
                dmg = max(1, int(self.max_hp * 0.06))
                self.hp = max(0, self.hp - dmg)
                msgs.append(f"{self.name} takes {dmg} burn damage!")
            elif effect == "bleed":
                dmg = max(1, int(self.max_hp * 0.04))
                self.hp = max(0, self.hp - dmg)
                msgs.append(f"{self.name} bleeds for {dmg} damage!")
            elif effect == "nightmare":
                dmg = max(1, int(self.max_hp * 0.10))
                self.hp = max(0, self.hp - dmg)
                msgs.append(f"{self.name} suffers nightmare for {dmg} damage!")
            elif effect == "doom":
                if turns <= 1:
                    self.hp = 0
                    msgs.append(f"{self.name} is consumed by Doom!")
            self.status_effects[effect] = turns - 1
            if self.status_effects[effect] <= 0:
                to_remove.append(effect)
        for e in to_remove:
            del self.status_effects[e]
        # Tick buffs
        for buff_name in list(self.buffs.keys()):
            self.buffs[buff_name]["turns"] -= 1
            if self.buffs[buff_name]["turns"] <= 0:
                del self.buffs[buff_name]
        return msgs

    @property
    def effective_atk(self):
        mult = 1.0
        for buff in self.buffs.values():
            mult *= buff.get("atk_mult", 1.0)
        return int(self.atk * mult)

    @property
    def effective_def(self):
        mult = 1.0
        for buff in self.buffs.values():
            mult *= buff.get("def_mult", 1.0)
        return int(self.defense * mult)
