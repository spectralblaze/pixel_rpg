"""Multiplayer protocol helpers.

All messages are JSON objects sent over a TCP socket with a 4-byte big-endian
length prefix so the receiver knows exactly how many bytes to read.

Message format
--------------
  {
    "type": <MSG_*>,
    "data": { ... }   # payload depends on type
  }
"""
import json
import socket
import struct


# ── Port ──────────────────────────────────────────────────────────────────────
PORT = 55000

# ── Message type constants ────────────────────────────────────────────────────
MSG_HELLO        = "HELLO"        # guest → host  { version, name }
MSG_WELCOME      = "WELCOME"      # host → guest  { player_dict, host_name }
MSG_PEER_POS     = "PEER_POS"     # both ways     { biome, x, y }
MSG_CHAT         = "CHAT"         # both ways     { sender, text }
MSG_SAVE_REQ     = "SAVE_REQ"     # guest → host  { player_dict }
MSG_SAVE_ACK     = "SAVE_ACK"     # host → guest  { slot }
MSG_BYE          = "BYE"          # either side   {}
MSG_STATE        = "STATE"        # host → guest  { key, value }  (generic flag sync)
# Co-op battle messages
MSG_BATTLE_START = "BATTLE_START" # either side   { monster_id, is_boss }
MSG_BATTLE_END   = "BATTLE_END"   # either side   { outcome }  "victory"/"fled"
MSG_ALLY_ATTACK  = "ALLY_ATTACK"  # either side   { damage, name }
# Synced co-op turn messages
MSG_COOP_JOIN    = "COOP_JOIN"    # joiner → initiator  { name, char_class, level, hp, max_hp }
MSG_COOP_SYNC    = "COOP_SYNC"    # initiator → joiner  { monster_hp, monster_max_hp, ally_hp, ally_max_hp }
MSG_COOP_ACTION  = "COOP_ACTION"  # acting player → other { monster_hp, is_victory, is_game_over, ally_hp, ally_max_hp }

PROTOCOL_VERSION = 1


# ── Wire helpers ──────────────────────────────────────────────────────────────

def send_msg(sock: socket.socket, msg_type: str, data: dict = None) -> None:
    """Serialize and send a message with a 4-byte length prefix."""
    payload = json.dumps({"type": msg_type, "data": data or {}}).encode("utf-8")
    header  = struct.pack(">I", len(payload))
    sock.sendall(header + payload)


def recv_msg(sock: socket.socket):
    """Blocking read of one message.  Returns (type, data) or raises on error."""
    raw_len = _recv_exactly(sock, 4)
    if raw_len is None:
        return None, None
    (length,) = struct.unpack(">I", raw_len)
    if length == 0 or length > 2_000_000:
        return None, None
    raw = _recv_exactly(sock, length)
    if raw is None:
        return None, None
    obj = json.loads(raw.decode("utf-8"))
    return obj.get("type"), obj.get("data", {})


def _recv_exactly(sock: socket.socket, n: int):
    """Read exactly n bytes from sock.  Returns None on EOF/error."""
    buf = b""
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except OSError:
            return None
        if not chunk:
            return None
        buf += chunk
    return buf


# ── Utility ───────────────────────────────────────────────────────────────────

def get_local_ip() -> str:
    """Return the machine's LAN IP (best-effort; falls back to 127.0.0.1)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def get_public_ip(timeout: float = 6.0) -> str:
    """Return the machine's public/WAN IP via a free lookup service.
    Returns empty string if the request fails or times out."""
    import urllib.request
    for url in ("https://api.ipify.org", "https://icanhazip.com"):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return resp.read().decode().strip()
        except Exception:
            continue
    return ""
