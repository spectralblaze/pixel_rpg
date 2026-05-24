"""Save/load system using JSON files."""
import json, os, datetime
from settings import SAVE_DIR


def ensure_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def list_saves() -> list:
    ensure_dir()
    saves = []
    for fname in sorted(os.listdir(SAVE_DIR)):
        if fname.endswith(".json"):
            path = os.path.join(SAVE_DIR, fname)
            try:
                with open(path) as f:
                    data = json.load(f)
                saves.append({
                    "filename": fname,
                    "path": path,
                    "name": data.get("player", {}).get("name", "?"),
                    "level": data.get("player", {}).get("level", 1),
                    "class": data.get("player", {}).get("char_class", "?"),
                    "biome": data.get("player", {}).get("position_biome", "?"),
                    "saved_at": data.get("saved_at", ""),
                })
            except Exception:
                pass
    return saves


def save_game(player, slot: int = 1) -> str:
    ensure_dir()
    data = {
        "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "player": player.to_dict(),
    }
    path = os.path.join(SAVE_DIR, f"save_{slot:02d}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def load_game(path: str):
    from entities.player import Player
    with open(path) as f:
        data = json.load(f)
    return Player.from_dict(data["player"])


def auto_save(player):
    save_game(player, slot=0)


def delete_save(path: str):
    if os.path.exists(path):
        os.remove(path)


_SETTINGS_PATH = os.path.join(SAVE_DIR, "game_settings.json")

def save_settings(volume: float) -> None:
    """Persist user settings (volume etc.) to disk."""
    ensure_dir()
    data = {"volume": round(max(0.0, min(1.0, volume)), 3)}
    try:
        with open(_SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def load_settings() -> dict:
    """Load persisted settings.  Returns defaults if file is missing/corrupt."""
    defaults = {"volume": 0.65}
    try:
        with open(_SETTINGS_PATH) as f:
            data = json.load(f)
        defaults["volume"] = float(data.get("volume", defaults["volume"]))
    except (OSError, ValueError, KeyError):
        pass
    return defaults


def save_player_dict(player_dict: dict, slot: int) -> str:
    """Save a raw player dict (used by host to save guest character)."""
    ensure_dir()
    data = {
        "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "player": player_dict,
    }
    path = os.path.join(SAVE_DIR, f"save_{slot:02d}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path
