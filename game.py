"""Main Game class — manages screens, player, and the game loop."""
import pygame
from settings import *
from world.world_manager import WorldManager
from audio.music import MusicManager
from ui.screens import (SplashScreen, MainMenuScreen, LoadGameScreen,
                         CharCreateScreen, ExplorationScreen, CombatScreen,
                         SubclassScreen, InventoryScreen, SkillsScreen,
                         PetMenuScreen, VillageScreen, ShopScreen,
                         BlacksmithScreen, WorldMapScreen, PauseScreen,
                         SettingsScreen, HostLobbyScreen, JoinLobbyScreen,
                         MultiplayerMenuScreen)
from networking.protocol import (MSG_PEER_POS, MSG_CHAT, MSG_SAVE_REQ, MSG_SAVE_ACK, MSG_BYE,
                                   MSG_BATTLE_START, MSG_BATTLE_END, MSG_ALLY_ATTACK,
                                   MSG_COOP_JOIN, MSG_COOP_SYNC, MSG_COOP_ACTION)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()
        self.world  = WorldManager()
        self.music  = MusicManager()
        self.player = None

        # Apply saved volume immediately so music plays at the right level
        from systems.save_load import load_settings
        _saved = load_settings()
        self.music.set_volume(_saved["volume"])
        self.running = True

        # Pending events
        self.show_intro       = False
        self.pending_area_intro = False
        self.pending_boss_dialogue = None
        self.post_battle_dialogue  = None
        self.pending_subclass = False
        self._pending_boss_id = None

        self._settings_return = "main_menu"

        # ── Multiplayer state ──────────────────────────────────────────────────
        # mp_mode: None | "host" | "guest"
        self.mp_mode:   str | None = None
        self.mp_server = None   # networking.host.HostServer  (host only)
        self.mp_client = None   # networking.client.GuestClient (guest only)
        # Remote peer's last known world position
        self.mp_peer_biome: str = ""
        self.mp_peer_x: int = -1
        self.mp_peer_y: int = -1
        # Peer's player dict (name, level, class, color) for the HUD/sprite
        self.mp_peer_dict: dict = {}
        # Co-op battle state
        self.mp_coop_battle: dict | None = None   # {monster_id, is_boss} when peer started a battle
        self.mp_pending_ally_dmg: list = []       # [(damage, name)] queued ally attacks (legacy, kept for compat)
        self.mp_coop_inbox: list = []             # (mtype, data) tuples for CombatScreen to poll
        # In-game chat log  (list of "Name: text" strings, newest last)
        self.mp_chat_log: list = []
        # Countdown until next position broadcast (seconds)
        self._mp_sync_timer: float = 0.0

        self._current_screen = SplashScreen(self)

    # ── Screen management ────────────────────────────────────────────────────
    def set_screen(self, name: str, **kwargs):
        screens = {
            "splash":       lambda: SplashScreen(self),
            "main_menu":    lambda: MainMenuScreen(self),
            "load_game":    lambda: LoadGameScreen(self),
            "char_create":  lambda: CharCreateScreen(self),
            "exploration":  lambda: self._make_exploration(),
            "inventory":    lambda: InventoryScreen(self),
            "skills":       lambda: SkillsScreen(self),
            "pet_menu":     lambda: PetMenuScreen(self),
            "village":      lambda: VillageScreen(self),
            "shop":         lambda: ShopScreen(self),
            "blacksmith":   lambda: BlacksmithScreen(self),
            "world_map":    lambda: WorldMapScreen(self, fast_travel_mode=False),
            "fast_travel":  lambda: WorldMapScreen(self, fast_travel_mode=True),
            "pause":        lambda: PauseScreen(self),
            "subclass":     lambda: SubclassScreen(self),
            "settings":     lambda: SettingsScreen(self),
            "host_lobby":   lambda: HostLobbyScreen(self),
            "join_lobby":   lambda: JoinLobbyScreen(self),
            "mp_menu":      lambda: MultiplayerMenuScreen(self),
        }
        if name in screens:
            self._current_screen = screens[name]()
        else:
            raise ValueError(f"Unknown screen: {name}")

    def _make_exploration(self) -> ExplorationScreen:
        # ── Validate player spawn position before the screen is built ─────────
        # Covers: new game (hardcoded default), load game (old save), and any
        # other edge case where position_x/y might be on water or a structure.
        if self.player:
            tmap = self.world.get_map(self.player.position_biome)
            _unsafe = {"wall", "water", "lava", "mountain", "boss_lair", "bridge"}
            tile = tmap.tile_at(self.player.position_x, self.player.position_y)
            if tile in _unsafe:
                sx, sy = tmap.safe_entry_pos()
                self.player.position_x, self.player.position_y = sx, sy

        scr = ExplorationScreen(self)
        # Intro story
        if self.show_intro:
            self.show_intro = False
            from data.world_data import STORY
            from ui.components import DialogBox
            scr.dialog = DialogBox(STORY["intro"])
        # Post-battle boss dialogue
        if self.post_battle_dialogue:
            from ui.components import DialogBox
            scr.dialog = DialogBox(self.post_battle_dialogue)
            self.post_battle_dialogue = None
        if self.pending_area_intro:
            pass  # Exploration.update() handles this
        return scr

    def start_battle(self, monster_id: str):
        self._current_screen = CombatScreen(self, monster_id, is_boss=False)

    def start_boss_battle(self):
        boss_id = self._pending_boss_id
        self._pending_boss_id = None
        if boss_id:
            self._current_screen = CombatScreen(self, boss_id, is_boss=True)

    # ── Multiplayer helpers ──────────────────────────────────────────────────
    def start_host(self):
        """Open a TCP server and show the lobby while waiting for a guest."""
        from networking.host import HostServer
        self.mp_mode   = "host"
        self.mp_server = HostServer(
            self.player.to_dict() if self.player else {},
            self.player.name if self.player else "Host",
        )
        self.mp_server.start()
        self.set_screen("host_lobby")

    def start_client(self, host_ip: str):
        """Connect to a host as guest and show the lobby while handshaking."""
        from networking.client import GuestClient
        self.mp_mode   = "guest"
        self.mp_client = GuestClient(
            self.player.name if self.player else "Guest",
            self.player.to_dict() if self.player else {},
        )
        ok, err = self.mp_client.connect(host_ip)
        if ok:
            self.mp_client.start_loop()
            return True, ""
        else:
            self.mp_mode   = None
            self.mp_client = None
            return False, err

    def sync_guest_to_host(self):
        """When the guest first joins, teleport them to the host's biome.

        The host's player_dict was received during the handshake welcome
        message and stored in mp_client.host_player_dict.
        """
        if self.mp_mode != "guest" or not self.mp_client:
            return
        hd = self.mp_client.host_player_dict
        if not hd or not self.player:
            return
        # Store peer info for the HUD
        self.mp_peer_dict = hd
        biome = hd.get("position_biome", "")
        if biome and biome != self.player.position_biome:
            self.player.position_biome = biome
            # Force position recalculation to a safe tile in the new biome
            self.player.position_x = -1
            self.player.position_y = -1
        # Also set initial peer coordinates so the sprite shows immediately
        self.mp_peer_biome = biome
        self.mp_peer_x = hd.get("position_x", -1)
        self.mp_peer_y = hd.get("position_y", -1)

    def join_coop_battle(self, monster_id: str, is_boss: bool = False):
        """Called when this player (joiner) presses J to join the peer's battle.

        Sends MSG_COOP_JOIN to the initiator and enters a CombatScreen in
        joiner mode — the initiator acts first and the monster HP is synced
        via MSG_COOP_SYNC before this player's first turn.
        """
        from ui.screens import CombatScreen
        p = self.player
        if self.mp_peer and p:
            from networking.protocol import MSG_COOP_JOIN
            self.mp_peer.send(MSG_COOP_JOIN, {
                "name":       p.name,
                "char_class": p.char_class,
                "level":      p.level,
                "hp":         p.hp,
                "max_hp":     p.max_hp,
            })
        self.mp_coop_battle = None   # clear exploration join prompt
        self._current_screen = CombatScreen(self, monster_id,
                                            is_boss=is_boss, coop_mode="joiner")

    def stop_multiplayer(self):
        """Cleanly tear down the active MP connection."""
        if self.mp_server:
            self.mp_server.stop()
            self.mp_server = None
        if self.mp_client:
            self.mp_client.stop()
            self.mp_client = None
        self.mp_mode = None
        self.mp_peer_biome = ""
        self.mp_peer_x = -1
        self.mp_peer_y = -1
        self.mp_peer_dict = {}
        self.mp_coop_battle = None
        self.mp_pending_ally_dmg.clear()
        self.mp_coop_inbox.clear()
        self.mp_chat_log.clear()

    @property
    def mp_peer(self):
        """Return the active networking object regardless of role."""
        return self.mp_server if self.mp_mode == "host" else self.mp_client

    def _mp_broadcast_pos(self):
        """Send our current position (and basic identity) to the peer."""
        if not self.player or not self.mp_peer:
            return
        p = self.player
        self.mp_peer.send(MSG_PEER_POS, {
            "biome":      p.position_biome,
            "x":          p.position_x,
            "y":          p.position_y,
            "name":       p.name,
            "level":      p.level,
            "char_class": p.char_class,
        })

    def _mp_process_messages(self):
        """Drain incoming messages from the peer and act on them."""
        if not self.mp_peer:
            return
        for mtype, data in self.mp_peer.poll():
            if mtype == MSG_PEER_POS:
                self.mp_peer_biome = data.get("biome", "")
                self.mp_peer_x     = data.get("x", -1)
                self.mp_peer_y     = data.get("y", -1)
                # Keep peer dict name/level/class updated
                for k in ("name", "level", "char_class", "color"):
                    if k in data:
                        self.mp_peer_dict[k] = data[k]

            elif mtype == MSG_CHAT:
                sender = data.get("sender", "?")
                text   = data.get("text", "")
                self.mp_chat_log.append(f"{sender}: {text}")
                if len(self.mp_chat_log) > 40:
                    self.mp_chat_log.pop(0)

            elif mtype == MSG_SAVE_REQ and self.mp_mode == "host":
                # Guest is asking us to save their character
                from systems.save_load import save_player_dict
                pdict = data.get("player_dict", {})
                slot  = 98   # dedicated guest save slot
                save_player_dict(pdict, slot)
                self.mp_peer.send(MSG_SAVE_ACK, {"slot": slot})

            elif mtype == MSG_BATTLE_START:
                # Peer started a battle — queue a co-op join if we're nearby
                self.mp_coop_battle = {
                    "monster_id": data.get("monster_id", ""),
                    "is_boss":    data.get("is_boss", False),
                }

            elif mtype == MSG_BATTLE_END:
                self.mp_coop_battle = None
                # Also forward to CombatScreen inbox (ally fled/defeated)
                self.mp_coop_inbox.append((mtype, data))

            elif mtype == MSG_ALLY_ATTACK:
                self.mp_pending_ally_dmg.append(
                    (data.get("damage", 0), data.get("name", "Ally"))
                )

            # ── Synced co-op turn messages → forwarded to CombatScreen ──────
            elif mtype in (MSG_COOP_JOIN, MSG_COOP_SYNC, MSG_COOP_ACTION):
                self.mp_coop_inbox.append((mtype, data))

            elif mtype == MSG_BYE:
                self.mp_chat_log.append("-- Peer disconnected --")
                if self.mp_server:
                    self.mp_server.connected = False
                if self.mp_client:
                    self.mp_client.connected = False

    def mp_send_chat(self, text: str):
        """Send a chat message to the peer (also add to local log)."""
        if not self.mp_peer or not text.strip():
            return
        name = self.player.name if self.player else "Me"
        self.mp_peer.send(MSG_CHAT, {"sender": name, "text": text})
        self.mp_chat_log.append(f"{name}: {text}")
        if len(self.mp_chat_log) > 40:
            self.mp_chat_log.pop(0)

    def mp_request_save(self):
        """Guest calls this to ask the host to save their character."""
        if self.mp_mode == "guest" and self.mp_client and self.player:
            self.mp_client.send(MSG_SAVE_REQ, {"player_dict": self.player.to_dict()})

    # ── Main loop ────────────────────────────────────────────────────────────
    _MP_SYNC_INTERVAL = 0.2   # broadcast position 5× per second

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self._current_screen.handle_event(event)

            self._current_screen.update(dt)

            # ── Multiplayer tick ──────────────────────────────────────────────
            if self.mp_mode:
                self._mp_process_messages()
                self._mp_sync_timer -= dt
                if self._mp_sync_timer <= 0:
                    self._mp_sync_timer = self._MP_SYNC_INTERVAL
                    self._mp_broadcast_pos()

            self._current_screen.draw(self.screen)
            pygame.display.flip()

        # Clean up MP on exit
        self.stop_multiplayer()
        pygame.quit()
