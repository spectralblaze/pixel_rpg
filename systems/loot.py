"""Loot and drop system — rarity-weighted item generation."""
import random
from settings import RARITY_WEIGHTS, RARITY_STAT_MULT, RARITIES


def roll_rarity() -> str:
    pool = list(RARITY_WEIGHTS.items())
    total = sum(w for _, w in pool)
    r = random.uniform(0, total)
    cumul = 0
    for rarity, weight in pool:
        cumul += weight
        if r <= cumul:
            return rarity
    return "common"


def roll_drops(monster, player) -> list:
    """Return list of (item_id, qty, rarity) tuples."""
    results = []
    luck_bonus = player.luck * 0.003

    # Gold is always given (handled separately)
    for drop in monster.drops:
        chance = drop["chance"] + luck_bonus
        if random.random() <= chance:
            # Roll actual rarity (can upgrade from base)
            base_rarity = drop["rarity"]
            rolled = roll_rarity()
            # Use higher of the two
            final_rarity = _higher_rarity(base_rarity, rolled)
            qty = random.randint(1, 3) if _is_material(drop["item"]) else 1
            results.append((drop["item"], qty, final_rarity))

    # Chance for a random bonus drop based on luck
    if random.random() < 0.05 + luck_bonus:
        bonus = _random_bonus_drop(player.position_biome, player.level)
        if bonus:
            results.append(bonus)

    return results


def _higher_rarity(a: str, b: str) -> str:
    return a if RARITIES.index(a) >= RARITIES.index(b) else b


def _is_material(item_id: str) -> bool:
    from data.items_data import ITEMS
    return ITEMS.get(item_id, {}).get("type") == "material"


def _random_bonus_drop(biome: str, player_level: int):
    """Small chance to drop a random equipment appropriate to zone level."""
    from data.items_data import ITEMS
    # Filter items appropriate for the player's level (by price proxy)
    level_price_cap = player_level * 200
    candidates = [
        (iid, item) for iid, item in ITEMS.items()
        if item["type"] in ("weapon","armor_head","armor_chest","armor_legs",
                             "armor_hands","armor_feet","ring","amulet","belt")
        and item.get("buy", 0) <= level_price_cap
        and item.get("buy", 0) > 0
    ]
    if not candidates:
        return None
    item_id, item = random.choice(candidates)
    rarity = roll_rarity()
    return (item_id, 1, rarity)


def stat_multiplier_for_rarity(rarity: str) -> float:
    return RARITY_STAT_MULT.get(rarity, 1.0)


def item_sell_price(item_id: str, rarity: str) -> int:
    from data.items_data import ITEMS
    from settings import SELL_MULT
    item = ITEMS.get(item_id, {})
    base = item.get("buy", 0)
    mult = RARITY_STAT_MULT.get(rarity, 1.0)
    return max(1, int(base * SELL_MULT * mult))


def item_buy_price(item_id: str) -> int:
    from data.items_data import ITEMS
    return ITEMS.get(item_id, {}).get("buy", 0)
