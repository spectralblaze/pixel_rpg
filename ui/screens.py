"""All game screens (states). Each inherits Screen and implements
handle_event(), update(), draw().
"""
import pygame, random, math
from settings import *
from ui.components import (Button, ScrollList, DialogBox, draw_panel,
                            draw_bar, draw_text, draw_text_centered,
                            draw_rarity_badge, get_font, wrap_text)
from data.world_data import BIOMES, STORY
from data.classes_data import CLASSES, BASE_CLASSES
from data.skills_data import SKILLS
from data.items_data import ITEMS
from data.monsters_data import MONSTERS
from ui.sprites import draw_player_sprite, draw_player_in_boat, draw_monster_sprite


# ── Base screen ───────────────────────────────────────────────────────────────
class Screen:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surf): pass


# ═════════════════════════════════════════════════════════════════════════════
# SPLASH / COVER ART SCREEN
# ═════════════════════════════════════════════════════════════════════════════
class SplashScreen(Screen):
    """Full-screen cover art shown on launch.
    Auto-advances to MainMenu after ~4 s, or instantly on any key / click.
    """
    DURATION = 4.0      # seconds before auto-advance
    FADE_IN  = 1.2      # fade-in duration (seconds)

    def __init__(self, game):
        super().__init__(game)
        self._t   = 0.0          # elapsed seconds
        self._done = False
        game.music.play_menu()

        # Pre-build the star field with a fixed seed so it's deterministic
        rng = random.Random(137)
        self._stars = [
            (rng.randint(0, SCREEN_W - 1),
             rng.randint(0, SCREEN_H - 1),
             rng.randint(1, 3),
             rng.random() * 6.28)   # phase offset
            for _ in range(120)
        ]

    # ── Input ────────────────────────────────────────────────────────────────
    def handle_event(self, event):
        if self._done:
            return
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            # Any key / tap skips to main menu
            self._advance()

    def _advance(self):
        if not self._done:
            self._done = True
            self.game.set_screen("main_menu")

    # ── Logic ────────────────────────────────────────────────────────────────
    def update(self, dt):
        if self._done:
            return
        self._t += dt
        if self._t >= self.DURATION:
            self._advance()

    # ── Drawing ──────────────────────────────────────────────────────────────
    def draw(self, surf):
        tick = pygame.time.get_ticks()

        # Deep space background
        surf.fill((8, 4, 18))

        # Animated star field
        for sx, sy, sr, phase in self._stars:
            bright = int(120 + 90 * math.sin(tick * 0.001 + phase))
            pygame.draw.circle(surf, (bright, bright, min(255, bright + 40)), (sx, sy), sr)

        cx = SCREEN_W // 2
        cy = SCREEN_H // 2

        # ── Dragon silhouette (Aldrath, King of Dragons) ──────────────────────
        dragon_size = min(SCREEN_W, SCREEN_H) * 2 // 3
        # Subtle glow halo behind the dragon
        glow_r = int(dragon_size * 0.55 + 8 * math.sin(tick * 0.0015))
        glow_col_a = 40 + int(20 * math.sin(tick * 0.0015))
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        for ri in range(glow_r, 0, -max(1, glow_r // 12)):
            alpha = max(0, int(glow_col_a * (1 - ri / glow_r) * 2))
            pygame.draw.circle(glow_surf, (180, 30, 0, alpha), (glow_r, glow_r), ri)
        surf.blit(glow_surf, (cx - glow_r, cy - glow_r + 30))

        # Dragon sprite
        draw_monster_sprite(surf, "aldrath", (210, 40, 20),
                            cx, cy + 30, dragon_size, tick)

        # ── Gold ornamental border ────────────────────────────────────────────
        border_col = (180, 140, 30)
        bw = 6
        pygame.draw.rect(surf, border_col, (bw, bw, SCREEN_W - bw*2, SCREEN_H - bw*2), bw)
        # Corner flourishes
        for (ox, oy) in [(bw, bw), (SCREEN_W - bw - 20, bw),
                         (bw, SCREEN_H - bw - 20), (SCREEN_W - bw - 20, SCREEN_H - bw - 20)]:
            pygame.draw.rect(surf, (220, 180, 60), (ox, oy, 20, 20), 3)

        # ── Title text ────────────────────────────────────────────────────────
        # Animated gold pulsing glow on title
        glow_v = int(30 * math.sin(tick * 0.002))
        title_col   = (220 + glow_v, 170 + glow_v // 2, 20, 255)
        title_col   = tuple(min(255, v) for v in title_col[:3])
        sub_col     = (200, 160, 90)

        title_y  = 60
        draw_text_centered(surf, "LEGENDS  OF  THE",    title_y,      title_col,  size=38, shadow=True)
        draw_text_centered(surf, "CURSED  REALM",       title_y + 52, title_col,  size=52, shadow=True)
        draw_text_centered(surf, "The Dragon's Secret", title_y + 114, sub_col,   size=22, shadow=True)

        # ── Subtitle / prompt ─────────────────────────────────────────────────
        blink = (tick // 600) % 2 == 0
        if blink:
            prompt_col = (180, 140, 40)
            draw_text_centered(surf, "Press any key to continue",
                               SCREEN_H - 56, prompt_col, size=16)

        # ── Studio tag ────────────────────────────────────────────────────────
        tag_fnt = get_font(12)
        tag = tag_fnt.render("Legends of the Cursed Realm  © 2026", True, (80, 70, 100))
        surf.blit(tag, (SCREEN_W // 2 - tag.get_width() // 2, SCREEN_H - 28))

        # ── Fade-in from black ────────────────────────────────────────────────
        if self._t < self.FADE_IN:
            alpha = int(255 * (1.0 - self._t / self.FADE_IN))
            fade = pygame.Surface((SCREEN_W, SCREEN_H))
            fade.fill((0, 0, 0))
            fade.set_alpha(alpha)
            surf.blit(fade, (0, 0))


# ═════════════════════════════════════════════════════════════════════════════
# MAIN MENU
# ═════════════════════════════════════════════════════════════════════════════
class MainMenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_W // 2
        bw, bh = 260, 50
        bx = cx - bw // 2
        self.buttons = {
            "new":      Button(pygame.Rect(bx, 280, bw, bh), "New Game",    DARK_GREEN),
            "load":     Button(pygame.Rect(bx, 340, bw, bh), "Load Game",   DARK_BLUE),
            "settings": Button(pygame.Rect(bx, 400, bw, bh), "Settings",    MID_GRAY),
            "quit":     Button(pygame.Rect(bx, 460, bw, bh), "Quit",        DARK_RED),
        }
        self.tick = 0
        game.music.play_menu()

    def handle_event(self, event):
        for key, btn in self.buttons.items():
            if btn.is_clicked(event):
                if key == "new":
                    self.game.set_screen("char_create")
                elif key == "load":
                    self.game.set_screen("load_game")
                elif key == "settings":
                    self.game._settings_return = "main_menu"
                    self.game.set_screen("settings")
                elif key == "quit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        for btn in self.buttons.values():
            btn.update(mp)
        self.tick += dt

    def draw(self, surf):
        surf.fill(UI_BG)
        # Animated stars
        rng = random.Random(42)
        for _ in range(80):
            sx = rng.randint(0, SCREEN_W)
            sy = rng.randint(0, SCREEN_H)
            r = rng.randint(1, 3)
            bright = int(100 + 80 * math.sin(self.tick * 0.001 + rng.random() * 6))
            pygame.draw.circle(surf, (bright, bright, bright), (sx, sy), r)

        # Title
        draw_text_centered(surf, "LEGENDS OF THE", 80, GOLD, size=32, shadow=True)
        draw_text_centered(surf, "CURSED REALM", 120, GOLD, size=38, shadow=True)
        draw_text_centered(surf, "The Dragon's Secret", 165, LIGHT_GRAY, size=20)

        for btn in self.buttons.values():
            btn.draw(surf)

        draw_text_centered(surf, "Arrow Keys / WASD to move  |  Touch supported", SCREEN_H - 30, UI_DIM, size=13)


# ═════════════════════════════════════════════════════════════════════════════
# LOAD GAME SCREEN
# ═════════════════════════════════════════════════════════════════════════════
class LoadGameScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        from systems.save_load import list_saves
        self.saves = list_saves()
        items = [(f"{s['name']} Lv{s['level']} {s['class'].title()} — {s['biome'].replace('_',' ').title()} | {s['saved_at']}",
                  s["path"], WHITE) for s in self.saves]
        if not items:
            items = [("No saves found", None, UI_DIM)]
        self.lst = ScrollList(pygame.Rect(100, 150, SCREEN_W - 200, 380), items, item_h=45)
        cx = SCREEN_W // 2
        self.btn_back  = Button(pygame.Rect(cx - 130, 560, 120, 44), "Back")
        self.btn_load  = Button(pygame.Rect(cx + 10,  560, 120, 44), "Load", DARK_GREEN)

    def handle_event(self, event):
        idx = self.lst.handle_event(event)
        if self.btn_back.is_clicked(event):
            self.game.set_screen("main_menu")
        if self.btn_load.is_clicked(event) and self.lst.selected >= 0:
            path = self.saves[self.lst.selected]["path"]
            if path:
                from systems.save_load import load_game
                self.game.player = load_game(path)
                self.game.set_screen("exploration")

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp); self.btn_load.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        draw_text_centered(surf, "Load Game", 80, GOLD, size=28)
        self.lst.draw(surf)
        self.btn_back.draw(surf)
        self.btn_load.draw(surf)


# ═════════════════════════════════════════════════════════════════════════════
# CHARACTER CREATION
# ═════════════════════════════════════════════════════════════════════════════
class CharCreateScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.name = "Hero"
        self.name_active = False
        self.selected_class = None
        self.page = "name"   # "name" -> "class"

        # Name input
        self.name_rect = pygame.Rect(SCREEN_W//2 - 180, 200, 360, 44)
        self.btn_next  = Button(pygame.Rect(SCREEN_W//2 - 80, 280, 160, 44), "Next →", DARK_GREEN)

        # Class buttons
        self.class_btns = {}
        for i, cls_id in enumerate(BASE_CLASSES):
            col = i % 3
            row = i // 3
            bx = 80 + col * 380
            by = 200 + row * 160
            self.class_btns[cls_id] = Button(
                pygame.Rect(bx, by, 340, 140),
                CLASSES[cls_id]["name"],
                color=tuple(max(20, c - 60) for c in CLASSES[cls_id]["color"])
            )

        self.btn_start = Button(pygame.Rect(SCREEN_W//2 - 100, SCREEN_H - 80, 200, 48), "Begin Journey", DARK_GREEN)
        self.btn_back  = Button(pygame.Rect(40, SCREEN_H - 80, 120, 44), "← Back")

    def handle_event(self, event):
        if self.page == "name":
            # ── Field focus ───────────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.name_rect.collidepoint(event.pos):
                    self.name_active = True
                    pygame.key.start_text_input()   # show Android soft keyboard
                else:
                    self.name_active = False
                    pygame.key.stop_text_input()
            elif event.type == pygame.FINGERDOWN:
                # Direct tap on field (Android — MOUSEBUTTONDOWN may not fire)
                fx = int(event.x * SCREEN_W)
                fy = int(event.y * SCREEN_H)
                if self.name_rect.collidepoint(fx, fy):
                    self.name_active = True
                    pygame.key.start_text_input()

            # ── Text entry ────────────────────────────────────────────────────
            if self.name_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.name.strip():
                            pygame.key.stop_text_input()
                            self.page = "class"
                elif event.type == pygame.TEXTINPUT:
                    # TEXTINPUT is the correct cross-platform path for typed
                    # characters — it handles IME / swipe keyboards on Android
                    # and avoids the double-input that happens when both
                    # KEYDOWN.unicode and TEXTINPUT fire simultaneously.
                    for ch in event.text:
                        if ch.isprintable() and len(self.name) < 16:
                            self.name += ch

            if self.btn_next.is_clicked(event) and self.name.strip():
                pygame.key.stop_text_input()
                self.page = "class"

        elif self.page == "class":
            for cls_id, btn in self.class_btns.items():
                if btn.is_clicked(event):
                    self.selected_class = cls_id
            if self.btn_back.is_clicked(event):
                self.page = "name"
            if self.btn_start.is_clicked(event) and self.selected_class:
                self._start_game()

    def _start_game(self):
        from entities.player import Player
        self.game.player = Player(self.name.strip() or "Hero", self.selected_class)
        self.game.show_intro = True
        self.game.set_screen("exploration")

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_next.update(mp)
        self.btn_start.update(mp)
        self.btn_back.update(mp)
        for btn in self.class_btns.values():
            btn.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        if self.page == "name":
            draw_text_centered(surf, "Create Your Hero", 100, GOLD, size=30)
            draw_text_centered(surf, "Enter your name:", 160, WHITE, size=18)
            col = GOLD if self.name_active else UI_BORDER
            pygame.draw.rect(surf, UI_PANEL, self.name_rect, border_radius=6)
            pygame.draw.rect(surf, col, self.name_rect, 2, border_radius=6)
            cursor = "|" if self.name_active and pygame.time.get_ticks() % 1000 < 500 else ""
            draw_text(surf, self.name + cursor, self.name_rect.x + 10, self.name_rect.y + 10, size=20)
            self.btn_next.draw(surf)

        elif self.page == "class":
            tick = pygame.time.get_ticks()

            # Subtle animated star field background
            rng2 = random.Random(99)
            for _ in range(28):
                sx2 = rng2.randint(0, SCREEN_W)
                sy2 = rng2.randint(0, SCREEN_H)
                br  = int(50 + 30 * math.sin(tick * 0.0008 + rng2.random() * 6))
                pygame.draw.circle(surf, (br, br, br + 20), (sx2, sy2), rng2.randint(1, 2))

            draw_text_centered(surf, f"Choose Your Class,  {self.name}",
                               22, GOLD, size=26, shadow=True)
            draw_text_centered(surf,
                               "Each class evolves into 3 unique subclasses at level 20",
                               56, UI_DIM, size=13)

            for cls_id, btn in self.class_btns.items():
                cls      = CLASSES[cls_id]
                rect     = btn.rect
                selected = (cls_id == self.selected_class)
                hovered  = btn.hovered

                base_col  = cls["color"]
                fill_dark = tuple(max(12, c // 4) for c in base_col)
                fill_mid  = tuple(max(28, c // 2) for c in base_col)
                card_fill = fill_mid if (selected or hovered) else fill_dark
                bdr_col   = (base_col if selected
                             else (tuple(min(255, c + 60) for c in base_col)
                                   if hovered else UI_BORDER))
                draw_panel(surf, rect, border_col=bdr_col, fill=card_fill, radius=8)

                # Animated pulsing outline + gold corner brackets when selected
                if selected:
                    pulse = 2 + int(2 * math.sin(tick * 0.004))
                    pygame.draw.rect(surf, base_col,
                                     rect.inflate(pulse * 2, pulse * 2), 2, border_radius=10)
                    cl = 14
                    for (bx2, by2), (dx2, dy2) in [
                        ((rect.x,     rect.y),      ( 1,  1)),
                        ((rect.right, rect.y),      (-1,  1)),
                        ((rect.x,     rect.bottom), ( 1, -1)),
                        ((rect.right, rect.bottom), (-1, -1)),
                    ]:
                        pygame.draw.line(surf, GOLD, (bx2, by2), (bx2 + dx2 * cl, by2), 2)
                        pygame.draw.line(surf, GOLD, (bx2, by2), (bx2, by2 + dy2 * cl), 2)

                # ── Sprite preview (left 112 px of card) ─────────────────────
                spr_cx = rect.x + 56
                spr_cy = rect.y + rect.h // 2
                draw_player_sprite(surf, cls_id, spr_cx, spr_cy, 72, tick)

                # Vertical divider
                dline = (tuple(min(255, c + 20) for c in base_col)
                         if selected else UI_BORDER)
                pygame.draw.line(surf, dline,
                                 (rect.x + 112, rect.y + 8),
                                 (rect.x + 112, rect.bottom - 8), 1)

                # ── Text section ──────────────────────────────────────────────
                tx = rect.x + 120
                ty = rect.y + 8

                name_col = (tuple(min(255, int(c * 1.3)) for c in base_col)
                            if selected else WHITE)
                draw_text(surf, cls["name"].upper(), tx, ty,
                          name_col, size=15, shadow=selected)
                ty += 22

                desc = cls.get("desc", "")
                _dfnt = get_font(11)
                _dmax = rect.right - tx - 10
                for _dl in wrap_text(desc, _dfnt, _dmax)[:3]:
                    draw_text(surf, _dl, tx, ty, UI_DIM, size=11)
                    ty += 13
                ty += 4

                stats = CLASS_STATS.get(cls_id, {})
                draw_text(surf,
                          f"HP:{stats.get('hp','?')}  MP:{stats.get('mp','?')}  "
                          f"ATK:{stats.get('atk','?')}  SPD:{stats.get('spd','?')}",
                          tx, ty, YELLOW, size=10)
                ty += 16

                sub_names = [CLASSES[s]["name"] for s in cls.get("subclasses", [])]
                draw_text(surf, " / ".join(sub_names), tx, ty, LIGHT_GRAY, size=10)
                ty += 14

                weapons = cls.get("weapons", [])
                if weapons:
                    draw_text(surf,
                              "Arms: " + ", ".join(w.title() for w in weapons[:3]),
                              tx, ty, UI_DIM, size=10)

            self.btn_start.draw(surf)
            self.btn_back.draw(surf)

            hint = (f"Selected: {CLASSES[self.selected_class]['name']}  —  Press Begin Journey!"
                    if self.selected_class else "Click a class card to select it")
            draw_text_centered(surf, hint, SCREEN_H - 106,
                               GOLD if self.selected_class else UI_DIM, size=13)


# ═════════════════════════════════════════════════════════════════════════════
# EXPLORATION
# ═════════════════════════════════════════════════════════════════════════════
class ExplorationScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.move_timer = 0
        self.move_delay = 0.15   # seconds between moves when key held
        self.keys_held = set()
        self.message = ""
        self.message_timer = 0
        self.dialog = None       # DialogBox for story events
        self._pending_encounter   = None
        self._pending_rare_area   = None
        self._pending_boss        = False
        self._pending_portal_dest = None   # biome_id to warp to via boss portal
        self._last_biome = None   # track biome changes for enemy respawn
        # Start explore music for current biome
        game.music.play_explore(game.player.position_biome if game.player else 'verdant_plains')

        # ── Multiplayer chat ───────────────────────────────────────────────────
        self._chat_typing  = False   # True while the player is typing a message
        self._chat_input   = ""      # current text being typed
        self._chat_visible = 5.0    # seconds the last chat line stays on screen
        self._chat_timer   = 0.0    # counts down after a message arrives

        # Dpad buttons (for mobile)
        pad_x, pad_y = SCREEN_W - 200, SCREEN_H - 200
        dsize = 55
        self.dpad = {
            "up":    Button(pygame.Rect(pad_x + dsize, pad_y,         dsize, dsize), "▲"),
            "down":  Button(pygame.Rect(pad_x + dsize, pad_y+dsize*2, dsize, dsize), "▼"),
            "left":  Button(pygame.Rect(pad_x,         pad_y+dsize,   dsize, dsize), "◄"),
            "right": Button(pygame.Rect(pad_x+dsize*2, pad_y+dsize,   dsize, dsize), "►"),
        }
        # Overlay buttons
        bw = 100
        self.btn_menu  = Button(pygame.Rect(10, SCREEN_H - 50, bw, 40), "Menu")
        self.btn_inv   = Button(pygame.Rect(bw + 20, SCREEN_H - 50, bw, 40), "Bag")
        self.btn_skills= Button(pygame.Rect(bw*2 + 30, SCREEN_H - 50, bw, 40), "Skills")
        self.btn_pet   = Button(pygame.Rect(bw*3 + 40, SCREEN_H - 50, bw, 40), "Pet")

        # Camera offset
        self.cam_x = 0
        self.cam_y = 0

    def _get_map(self):
        return self.game.world.get_map(self.game.player.position_biome)

    def handle_event(self, event):
        if self.dialog:
            if self.dialog.handle_event(event):
                self.dialog = None
                if self._pending_boss:
                    self._pending_boss = False
                    self.game.start_boss_battle()
                elif self._pending_encounter:
                    mid = self._pending_encounter
                    self._pending_encounter = None
                    self.game.start_battle(mid)
                elif self._pending_rare_area:
                    ra = self._pending_rare_area
                    self._pending_rare_area = None
                    self._reveal_skill(ra)
                elif self._pending_portal_dest:
                    dest = self._pending_portal_dest
                    self._pending_portal_dest = None
                    p = self.game.player
                    p.position_biome = dest
                    p.position_x = -1   # safe_entry_pos() will fix this
                    p.position_y = -1
                    self.keys_held.clear()
                    self.game.set_screen("exploration")
            # Keep keys_held accurate even while dialog is blocking input —
            # otherwise releasing a key during a dialog leaves it "stuck" in
            # keys_held and the player glides after the dialog closes.
            if event.type == pygame.KEYUP:
                self.keys_held.discard(event.key)
            return

        # ── Multiplayer chat input ────────────────────────────────────────────
        if self.game.mp_mode and self._chat_typing:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self._chat_input.strip():
                        self.game.mp_send_chat(self._chat_input.strip())
                        self._chat_timer = self._chat_visible
                    self._chat_typing = False
                    self._chat_input  = ""
                    pygame.key.stop_text_input()
                elif event.key == pygame.K_ESCAPE:
                    self._chat_typing = False
                    self._chat_input  = ""
                    pygame.key.stop_text_input()
                elif event.key == pygame.K_BACKSPACE:
                    self._chat_input = self._chat_input[:-1]
            elif event.type == pygame.TEXTINPUT:
                # TEXTINPUT handles both desktop (with start_text_input active)
                # and Android virtual keyboards / swipe / IME reliably.
                for ch in event.text:
                    if ch.isprintable() and len(self._chat_input) < 80:
                        self._chat_input += ch
            return   # absorb all events while typing

        if self.game.mp_mode and not self._chat_typing:
            _open_chat = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                _open_chat = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # "[T] Chat" hint is drawn near bottom-left; make it tappable
                _chat_hint = pygame.Rect(0, SCREEN_H - 86, 80, 30)
                if _chat_hint.collidepoint(event.pos):
                    _open_chat = True
            elif event.type == pygame.FINGERDOWN:
                _chat_hint = pygame.Rect(0, SCREEN_H - 86, 80, 30)
                if _chat_hint.collidepoint(int(event.x * SCREEN_W),
                                           int(event.y * SCREEN_H)):
                    _open_chat = True
            if _open_chat:
                self._chat_typing = True
                pygame.key.start_text_input()   # show Android soft keyboard
                return

        if event.type == pygame.KEYDOWN:
            self.keys_held.add(event.key)
            # J = join ally's battle (co-op)
            if event.key == pygame.K_j and self.game.mp_coop_battle:
                self._join_coop_battle()
                return
            self._try_move_key(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_held.discard(event.key)

        # D-pad
        for dir_name, btn in self.dpad.items():
            if btn.is_clicked(event):
                self._move(dir_name)

        if self.btn_menu.is_clicked(event):
            self.game.set_screen("pause")
        if self.btn_inv.is_clicked(event):
            self.game.set_screen("inventory")
        if self.btn_skills.is_clicked(event):
            self.game.set_screen("skills")
        if self.btn_pet.is_clicked(event):
            self.game.set_screen("pet_menu")

    def _join_coop_battle(self):
        """Join the co-op battle that the peer just started."""
        coop = self.game.mp_coop_battle
        if not coop:
            return
        mid     = coop.get("monster_id", "")
        is_boss = coop.get("is_boss", False)
        if not mid:
            return
        self.keys_held.clear()
        # Use the proper co-op join flow (sends MSG_COOP_JOIN, enters joiner mode)
        self.game.join_coop_battle(mid, is_boss=is_boss)

    def _try_move_key(self, key):
        mapping = {
            pygame.K_UP: "up", pygame.K_w: "up",
            pygame.K_DOWN: "down", pygame.K_s: "down",
            pygame.K_LEFT: "left", pygame.K_a: "left",
            pygame.K_RIGHT: "right", pygame.K_d: "right",
        }
        if key in mapping:
            self._move(mapping[key])

    def _move(self, direction: str):
        p = self.game.player
        dx, dy = {"up":(0,-1),"down":(0,1),"left":(-1,0),"right":(1,0)}[direction]
        nx, ny = p.position_x + dx, p.position_y + dy
        tmap = self._get_map()

        if not tmap.is_walkable(nx, ny):
            return

        p.position_x, p.position_y = nx, ny
        p.steps += 1
        if getattr(p, 'repel_steps', 0) > 0:
            p.repel_steps -= 1

        # Border exit → world map
        if tmap.is_border_exit(nx, ny):
            self.keys_held.clear()
            self.game.set_screen("world_map")
            return

        # Village
        if tmap.is_village(nx, ny):
            self.keys_held.clear()
            self.game.set_screen("village")
            return

        # Rare area
        ra = tmap.rare_area_at(nx, ny)
        if ra and ra["skill"] not in p.known_skills:
            lines = [ra["desc"], f"You sense a hidden power...", f"Learned skill: {SKILLS[ra['skill']]['name']}!"]
            self.dialog = DialogBox(lines)
            self._pending_rare_area = ra
            return

        # Boss check
        if tmap.is_boss_area(nx, ny):
            biome_data = BIOMES[p.position_biome]
            boss_id = biome_data.get("boss")
            if boss_id and boss_id not in p.defeated_bosses:
                # Boss still alive — trigger fight
                lines = STORY["boss_pre_dialogue"].get(boss_id, [f"A powerful enemy appears!"])
                self.dialog = DialogBox(lines)
                self._pending_boss = True
                self.game._pending_boss_id = boss_id
                return
            elif boss_id and boss_id in p.defeated_bosses:
                # Boss defeated — portal is active at the lair centre
                from data.monsters_data import MONSTERS
                unlock = MONSTERS.get(boss_id, {}).get("story_unlock", "")
                if unlock and unlock.endswith("_access"):
                    dest_biome = unlock.replace("_access", "")
                    dest_name  = BIOMES.get(dest_biome, {}).get("name", dest_biome)
                    self._pending_portal_dest = dest_biome
                    self.dialog = DialogBox([
                        "✦ A shimmering portal pulses with arcane energy.",
                        f"Destination: {dest_name}",
                        "Press any key to step through...",
                    ])
                    return

        # Extra location interaction (camp, well, shrine, altar, ruins, chest)
        self._check_extra_loc(tmap, p, nx, ny)

    def _reveal_skill(self, ra: dict):
        skill_id = ra["skill"]
        if self.game.player.learn_skill(skill_id):
            self.game.music.play_item_found()
            self.show_message(f"Learned: {SKILLS[skill_id]['name']}!")

    def _check_extra_loc(self, tmap, p, x: int, y: int):
        """Trigger a one-shot interaction when the player steps onto an extra
        location (camp / well / shrine / altar / ruins / chest).

        Each location fires once per map generation; subsequent visits are
        tracked in tmap.used_locs and silently ignored.
        """
        loc = next((el for el in tmap.extra_locs
                    if tuple(el["tile"]) == (x, y)), None)
        if loc is None:
            return
        if (x, y) in tmap.used_locs:
            return   # already used — no repeat
        tmap.used_locs.add((x, y))
        ltype = loc["type"]

        if ltype == "camp":
            heal = max(10, p.max_hp // 4)
            mana = max(5,  p.max_mp // 4)
            p.hp = min(p.max_hp, p.hp + heal)
            p.mp = min(p.max_mp, p.mp + mana)
            self.dialog = DialogBox([
                "Campsite",
                "A dying fire crackles. You rest and tend your wounds.",
                f"Recovered  HP +{heal}  |  MP +{mana}",
            ])

        elif ltype == "well":
            heal = max(8, p.max_hp // 5)
            p.hp = min(p.max_hp, p.hp + heal)
            self.dialog = DialogBox([
                "Ancient Well",
                "The cool, pure water refreshes you.",
                f"Recovered  HP +{heal}",
            ])

        elif ltype == "shrine":
            mana = max(10, p.max_mp // 3)
            p.mp = min(p.max_mp, p.mp + mana)
            self.dialog = DialogBox([
                "Sacred Shrine",
                "Ancient magic seeps through you, restoring your spirit.",
                f"Recovered  MP +{mana}",
            ])

        elif ltype == "altar":
            gold = random.randint(25, 100)
            p.gold += gold
            self.dialog = DialogBox([
                "Ancient Altar",
                "You leave a small offering. The spirits reward your respect.",
                f"Gold  +{gold}",
            ])

        elif ltype == "ruins":
            consumables = [k for k, v in ITEMS.items()
                           if v.get("type") == "consumable"]
            if consumables and random.random() < 0.45:
                found = random.choice(consumables)
                p.add_item(found, 1, "common")
                self.dialog = DialogBox([
                    "Ruins",
                    "You search the crumbling rubble...",
                    f"Found:  {ITEMS[found]['name']}!",
                ])
            else:
                self.dialog = DialogBox([
                    "Ruins",
                    "Crumbled stone and faded carvings.",
                    "Nothing of value remains here.",
                ])

        elif ltype == "chest":
            gear = [k for k, v in ITEMS.items()
                    if v.get("type") in ("weapon", "armor", "accessory")]
            if gear:
                from settings import RARITY_WEIGHTS
                rar_keys = list(RARITY_WEIGHTS.keys())
                rar_wts  = [RARITY_WEIGHTS[k] for k in rar_keys]
                rarity   = random.choices(rar_keys, weights=rar_wts, k=1)[0]
                found    = random.choice(gear)
                p.add_item(found, 1, rarity)
                self.game.music.play_item_found()
                self.dialog = DialogBox([
                    "Treasure Chest",
                    "The old chest groans open...",
                    f"Found:  {ITEMS[found]['name']}  [{rarity.upper()}]!",
                ])
            else:
                self.dialog = DialogBox(["Chest", "It is empty."])

    def show_message(self, msg: str, duration: float = 3.0):
        self.message = msg
        self.message_timer = duration

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        for btn in self.dpad.values(): btn.update(mp)
        for btn in (self.btn_menu, self.btn_inv, self.btn_skills, self.btn_pet):
            btn.update(mp)

        if self.message_timer > 0:
            self.message_timer -= dt

        # Update chat fade timer; refresh when new messages arrive
        if self.game.mp_mode:
            prev_len = getattr(self, "_chat_log_len", 0)
            cur_len  = len(self.game.mp_chat_log)
            if cur_len != prev_len:
                self._chat_log_len = cur_len
                self._chat_timer   = self._chat_visible
            elif self._chat_timer > 0:
                self._chat_timer -= dt

        self.move_timer += dt
        if self.move_timer >= self.move_delay and not self.dialog:
            self.move_timer = 0
            for key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s,
                        pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                if key in self.keys_held:
                    mapping = {
                        pygame.K_UP:"up", pygame.K_w:"up",
                        pygame.K_DOWN:"down", pygame.K_s:"down",
                        pygame.K_LEFT:"left", pygame.K_a:"left",
                        pygame.K_RIGHT:"right", pygame.K_d:"right",
                    }
                    self._move(mapping[key])
                    break

        # Camera
        p = self.game.player
        target_cx = p.position_x * TILE - SCREEN_W // 2
        target_cy = p.position_y * TILE - SCREEN_H // 2
        self.cam_x += (target_cx - self.cam_x) * 0.15
        self.cam_y += (target_cy - self.cam_y) * 0.15

        # Respawn enemies + update music when entering a new biome
        if p.position_biome != self._last_biome:
            self._last_biome = p.position_biome
            self.game.world.respawn_enemies(p.position_biome, p.level)
            self.game.music.play_explore(p.position_biome)

        # Tick wandering enemies — check for contact
        if not self.dialog:
            enemies = self.game.world.get_enemies(p.position_biome, p.level)
            for enemy in list(enemies):
                hit = enemy.update(dt, p.position_x, p.position_y)
                if hit:
                    if getattr(p, 'repel_steps', 0) > 0:
                        # Repellent active — monster backs off, no battle
                        continue
                    self.game.world.remove_enemy(p.position_biome, enemy)
                    self.game.start_battle(enemy.monster_id)
                    return

        # Area intro dialogue
        if hasattr(self.game, 'pending_area_intro') and self.game.pending_area_intro:
            lines = STORY["area_intro"].get(p.position_biome, [])
            if lines:
                self.dialog = DialogBox(lines)
            self.game.pending_area_intro = False

    def draw(self, surf):
        surf.fill(BLACK)
        p = self.game.player
        tmap = self._get_map()
        cx = int(self.cam_x)
        cy = int(self.cam_y)

        # Draw tiles
        start_tx = max(0, cx // TILE)
        start_ty = max(0, cy // TILE)
        end_tx = min(MAP_W, start_tx + SCREEN_W // TILE + 2)
        end_ty = min(MAP_H, start_ty + SCREEN_H // TILE + 2)

        # Build quick lookup sets for special tiles
        _extra_loc_map = {loc["tile"]: loc for loc in tmap.extra_locs}
        _rare_area_map  = {tuple(ra["tile"]): ra for ra in tmap.rare_areas}
        bx_t, by_t = tmap.boss_tile
        vx_t, vy_t = tmap.village_tile
        tick_ms = pygame.time.get_ticks()

        # Portal: active when the biome's boss has been defeated
        _biome_boss_id = BIOMES.get(p.position_biome, {}).get("boss")
        _portal_active = bool(_biome_boss_id and _biome_boss_id in p.defeated_bosses)

        # Pre-load any PNG tile overrides (cached; returns None if no file)
        from assets.loader import get_tile_img as _gti
        _tile_imgs = {tt: _gti(tt, TILE - 1) for tt in TILE_COL}

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = tmap.tile_at(tx, ty)
                col  = TILE_COL.get(tile, (40, 40, 40))
                sx   = tx * TILE - cx
                sy   = ty * TILE - cy

                # ── Tile base: PNG if available, else solid colour ─────────────
                _tpng = _tile_imgs.get(tile)
                if _tpng is not None:
                    surf.blit(_tpng, (sx, sy))
                else:
                    pygame.draw.rect(surf, col, (sx, sy, TILE - 1, TILE - 1))

                t_hash = (tx * 7 + ty * 13) & 0xFFFF  # stable per-tile noise

                if _tpng is None:  # skip procedural art when PNG tile is loaded
                    if tile == "forest":
                        # Dark tree canopy circles
                        for i in range(3):
                            tx2 = sx + 5 + (t_hash * (i + 1) * 11) % (TILE - 12)
                            ty2 = sy + 5 + (t_hash * (i + 1) *  7) % (TILE - 12)
                            r2  = 4 + (t_hash + i * 5) % 5
                            pygame.draw.circle(surf, (15, 65, 15), (tx2, ty2), r2)
                            # Trunk
                            pygame.draw.rect(surf, (70, 45, 20),
                                             (tx2 - 1, ty2 + r2 - 1, 3, 4))
    
                    elif tile == "mountain":
                        # Triangle peak
                        mid_x = sx + TILE // 2 + (t_hash % 9) - 4
                        peak_y = sy + 3 + (t_hash % 7)
                        base_y = sy + TILE - 4
                        hw     = 9 + (t_hash % 7)
                        pts    = [(mid_x, peak_y),
                                  (mid_x - hw, base_y),
                                  (mid_x + hw, base_y)]
                        pygame.draw.polygon(surf, (80, 70, 55), pts)
                        # Snow cap
                        cap_h = hw // 3
                        snow_pts = [(mid_x, peak_y),
                                    (mid_x - cap_h, peak_y + cap_h * 2),
                                    (mid_x + cap_h, peak_y + cap_h * 2)]
                        pygame.draw.polygon(surf, (230, 235, 245), snow_pts)
    
                    elif tile == "water":
                        # Ripple lines — three-segment wave, avoids draw.arc
                        # which has rendering glitches on Android ARM/SDL2.
                        wave_off = (tick_ms // 600 + t_hash) % 3
                        _wrc = (75, 145, 230)
                        for i in range(2):
                            wy = sy + 10 + i * 12 + wave_off * 2
                            wx = sx + 4 + (t_hash * (i + 1) * 3) % (TILE - 16)
                            pygame.draw.line(surf, _wrc,
                                             (wx,      wy + 4), (wx + 5,  wy),     1)
                            pygame.draw.line(surf, _wrc,
                                             (wx + 5,  wy),     (wx + 10, wy + 4), 1)
                            pygame.draw.line(surf, _wrc,
                                             (wx + 10, wy + 4), (wx + 15, wy),     1)
    
                    elif tile == "snow":
                        # Small cross snowflakes
                        for i in range(3):
                            fx = sx + 5 + (t_hash * (i + 1) * 9) % (TILE - 12)
                            fy = sy + 5 + (t_hash * (i + 1) * 5) % (TILE - 12)
                            pygame.draw.line(surf, (240, 245, 255),
                                             (fx - 3, fy), (fx + 3, fy), 1)
                            pygame.draw.line(surf, (240, 245, 255),
                                             (fx, fy - 3), (fx, fy + 3), 1)
    
                    elif tile == "ice":
                        # Diagonal sheen lines
                        for i in range(2):
                            off = 6 + i * 12 + (t_hash % 6)
                            pygame.draw.line(surf, (200, 230, 255),
                                             (sx + off, sy + 2),
                                             (sx + off - 8, sy + TILE - 3), 1)
    
                    elif tile == "lava":
                        # Glowing pulse circle
                        pulse = int(180 + 70 * math.sin(tick_ms * 0.003 + t_hash * 0.5))
                        r_col = (min(255, pulse), max(0, pulse - 130), 0)
                        cr    = 5 + (t_hash % 5)
                        lcx   = sx + 8 + (t_hash * 3) % (TILE - 18)
                        lcy   = sy + 8 + (t_hash * 7) % (TILE - 18)
                        pygame.draw.circle(surf, r_col, (lcx, lcy), cr)
    
                    elif tile == "swamp":
                        # Dark mud blobs
                        for i in range(2):
                            bx2 = sx + 5 + (t_hash * (i + 1) * 11) % (TILE - 14)
                            by2 = sy + 5 + (t_hash * (i + 1) *  9) % (TILE - 14)
                            pygame.draw.ellipse(surf, (35, 50, 20),
                                                (bx2, by2, 10, 6))
    
                    elif tile == "crystal":
                        # Diamond outline
                        dmx = sx + TILE // 2 + (t_hash % 7) - 3
                        dmy = sy + TILE // 2 + (t_hash % 5) - 2
                        dhw, dhh = 7, 10
                        dpts = [(dmx, dmy - dhh), (dmx + dhw, dmy),
                                (dmx, dmy + dhh), (dmx - dhw, dmy)]
                        pygame.draw.polygon(surf, (170, 220, 255), dpts, 2)
    
                    elif tile == "ruins":
                        # Cracked rect outline
                        pygame.draw.rect(surf, (75, 68, 58),
                                         (sx + 5, sy + 5, TILE - 10, TILE - 10), 2)
                        pygame.draw.line(surf, (55, 50, 42),
                                         (sx + 5, sy + 5),
                                         (sx + 14, sy + 14), 1)
    
                    elif tile == "cave":
                        # Arched entrance — polygon outline replaces draw.arc
                        # (arc has rendering glitches on Android ARM/SDL2)
                        _cca = (25, 22, 18)
                        _ccx = sx + TILE // 2
                        # Upper semicircle approx: 7 points spanning the arch
                        pygame.draw.lines(surf, _cca, False, [
                            (sx + 6,      sy + 8 + 17),
                            (sx + 10,     sy + 8 + 6),
                            (sx + 18,     sy + 8 + 1),
                            (_ccx,        sy + 8),
                            (sx + TILE - 18, sy + 8 + 1),
                            (sx + TILE - 10, sy + 8 + 6),
                            (sx + TILE - 6,  sy + 8 + 17),
                        ], 3)
                        pygame.draw.rect(surf, _cca,
                                         (sx + 9, sy + 8 + (TILE - 14) // 2,
                                          TILE - 18, (TILE - 14) // 2))
    
                    elif tile == "bridge":
                        # Water base (overrides the brown minimap colour)
                        T = TILE
                        pygame.draw.rect(surf, (28, 65, 168), (sx, sy, T - 1, T - 1))
                        # Animated water shimmer beneath the planks
                        wave_off = (tick_ms // 700 + t_hash) % 3
                        _bwc = (55, 110, 220)
                        for wi in range(2):
                            wy2 = sy + 6 + wi * 14 + wave_off * 2
                            wx2 = sx + 3 + (t_hash * (wi + 1) * 5) % (T - 14)
                            pygame.draw.line(surf, _bwc,
                                             (wx2,     wy2 + 3), (wx2 + 4,  wy2),     1)
                            pygame.draw.line(surf, _bwc,
                                             (wx2 + 4, wy2),     (wx2 + 9,  wy2 + 3), 1)
                            pygame.draw.line(surf, _bwc,
                                             (wx2 + 9, wy2 + 3), (wx2 + 13, wy2),     1)
                        # Detect orientation from neighbours:
                        #   N-S bridge (travels N↔S) → horizontal plank boards
                        #   E-W bridge (travels E↔W) → vertical plank boards
                        _water_tiles = ("bridge", "water", "lava")
                        _ns = (tmap.tile_at(tx, ty - 1) in _water_tiles or
                               tmap.tile_at(tx, ty + 1) in _water_tiles)
                        _ew = (tmap.tile_at(tx - 1, ty) in _water_tiles or
                               tmap.tile_at(tx + 1, ty) in _water_tiles)
                        # If ambiguous (corner/isolated), default to N-S (horizontal planks)
                        _horiz_planks = _ns or not _ew
                        plank_col = (125, 82, 32)
                        hi_col    = (165, 118, 55)
                        lo_col    = ( 90,  55, 18)
                        rail_col  = (160, 118, 52)
                        if _horiz_planks:
                            # Horizontal plank boards running left-right; rails N & S
                            ph = T // 4
                            for pi in range(3):
                                py2 = sy + 3 + pi * (ph + 2)
                                pygame.draw.rect(surf, plank_col, (sx + 5, py2, T - 10, ph))
                                pygame.draw.line(surf, hi_col,
                                                 (sx + 7, py2 + 1), (sx + T - 9, py2 + 1), 1)
                                pygame.draw.line(surf, lo_col,
                                                 (sx + 7, py2 + ph - 2),
                                                 (sx + T - 9, py2 + ph - 2), 1)
                            # Side rope rails (left & right)
                            pygame.draw.line(surf, rail_col,
                                             (sx + 3, sy + 3), (sx + 3, sy + T - 4), 2)
                            pygame.draw.line(surf, rail_col,
                                             (sx + T - 4, sy + 3), (sx + T - 4, sy + T - 4), 2)
                        else:
                            # Vertical plank boards running top-bottom; rails E & W
                            pw = T // 4
                            for pi in range(3):
                                px2 = sx + 3 + pi * (pw + 2)
                                pygame.draw.rect(surf, plank_col, (px2, sy + 5, pw, T - 10))
                                pygame.draw.line(surf, hi_col,
                                                 (px2 + 1, sy + 7), (px2 + 1, sy + T - 9), 1)
                                pygame.draw.line(surf, lo_col,
                                                 (px2 + pw - 2, sy + 7),
                                                 (px2 + pw - 2, sy + T - 9), 1)
                            # Top & bottom rope rails
                            pygame.draw.line(surf, rail_col,
                                             (sx + 3, sy + 3), (sx + T - 4, sy + 3), 2)
                            pygame.draw.line(surf, rail_col,
                                             (sx + 3, sy + T - 4), (sx + T - 4, sy + T - 4), 2)
    
                    elif tile == "boss_lair":
                        # Dark flagstone floor — 2×2 stone blocks per tile
                        T = TILE
                        for bi in range(2):
                            for bj in range(2):
                                bx3 = sx + 1 + bj * (T // 2)
                                by3 = sy + 1 + bi * (T // 2)
                                bw3 = T // 2 - 2
                                shade = 44 + (t_hash * (bi * 2 + bj + 1) * 7) % 14
                                pygame.draw.rect(surf, (shade, shade - 6, shade - 10),
                                                 (bx3, by3, bw3, bw3))
                                pygame.draw.rect(surf, (22, 17, 14),
                                                 (bx3, by3, bw3, bw3), 1)
                        # Random crack line for texture
                        if t_hash % 4 == 0:
                            crx = sx + 6 + (t_hash * 3) % (T - 14)
                            cry = sy + 5 + (t_hash * 7) % (T - 12)
                            pygame.draw.line(surf, (20, 15, 12),
                                             (crx, cry), (crx + 6, cry + 9), 1)
                        # ── Portal overlay on the centre tile when boss is defeated ──
                        if _portal_active and tx == bx_t and ty == by_t:
                            pcx = sx + TILE // 2
                            pcy = sy + TILE // 2
                            t_s = tick_ms * 0.003
                            # Layered pulsing rings
                            for layer, (rcol, rbase, ramp) in enumerate([
                                    ((80, 40, 200), 16, 4),
                                    ((120, 60, 255), 12, 3),
                                    ((200, 140, 255), 7,  2),
                            ]):
                                r = int(rbase + ramp * math.sin(t_s + layer * 1.2))
                                pygame.draw.circle(surf, rcol, (pcx, pcy), r, 2)
                            # Spinning spokes
                            for spoke in range(6):
                                ang = t_s * 1.5 + spoke * (math.pi / 3)
                                sx2 = int(pcx + 14 * math.cos(ang))
                                sy2 = int(pcy + 14 * math.sin(ang))
                                pygame.draw.line(surf, (180, 100, 255),
                                                 (pcx, pcy), (sx2, sy2), 1)
                            # Inner bright core
                            core_r = 3 + int(2 * math.sin(t_s * 2))
                            pygame.draw.circle(surf, (230, 200, 255), (pcx, pcy), core_r)
    
                    elif tile == "sand":
                        # Tiny dune ripple
                        ry = sy + 10 + (t_hash % (TILE - 20))
                        pygame.draw.line(surf, (185, 162, 95),
                                         (sx + 4, ry), (sx + TILE - 6, ry), 1)
    
                    elif tile == "volcanic":
                        # Crack lines
                        for i in range(2):
                            vx1 = sx + 6 + (t_hash * (i + 1) * 7) % (TILE - 14)
                            pygame.draw.line(surf, (60, 30, 15),
                                             (vx1, sy + 4),
                                             (vx1 + (t_hash % 5) - 2, sy + TILE - 5), 1)
    
                    elif tile == "cloud":
                        # Puffy bumps
                        for i in range(3):
                            clx = sx + 6 + i * 12 + (t_hash * (i + 1) * 3) % 8
                            cly = sy + TILE // 2
                            pygame.draw.circle(surf, (215, 220, 235), (clx, cly), 6)
    
                    elif tile == "grass":
                        # Blade lines (sparse)
                        if t_hash % 3 == 0:
                            for i in range(3):
                                gx2 = sx + 5 + (t_hash * (i + 1) * 11) % (TILE - 10)
                                gy2 = sy + TILE - 8
                                pygame.draw.line(surf, (40, 170, 40),
                                                 (gx2, gy2+ 4), (gx2 - 1, gy2), 1)
    
                    elif tile == "jungle":
                        # Large tropical canopy blobs — 2-3 overlapping circles per tile
                        for i in range(3):
                            jx = sx + 6  + (t_hash * (i + 1) * 13) % (TILE - 14)
                            jy = sy + 5  + (t_hash * (i + 1) *  9) % (TILE - 12)
                            jr = 6 + (t_hash + i * 7) % 6
                            # Deep canopy layer
                            pygame.draw.circle(surf, (8, 75, 8),  (jx, jy), jr)
                            # Bright highlight on top-left of each canopy
                            pygame.draw.circle(surf, (25, 130, 25), (jx - 1, jy - 1), max(2, jr - 3))
                        # Bamboo stalk (1 per tile based on hash)
                        if t_hash % 4 < 2:
                            bk_x = sx + 4 + (t_hash * 17) % (TILE - 10)
                            for seg in range(3):
                                seg_y = sy + 4 + seg * ((TILE - 8) // 3)
                                pygame.draw.line(surf, (60, 140, 30),
                                                 (bk_x, seg_y), (bk_x, seg_y + (TILE - 8) // 3 - 1), 2)
                                # Knuckle joint
                                pygame.draw.line(surf, (80, 160, 40),
                                                 (bk_x - 2, seg_y), (bk_x + 2, seg_y), 1)
                        # Occasional bright flower dot
                        if t_hash % 7 == 0:
                            fx2 = sx + 8 + (t_hash * 11) % (TILE - 18)
                            fy2 = sy + 8 + (t_hash *  7) % (TILE - 18)
                            pygame.draw.circle(surf, (230, 80, 180), (fx2, fy2), 2)
                        # Hanging vine (vertical drape line)
                        if t_hash % 5 == 1:
                            vn_x = sx + 10 + (t_hash * 9) % (TILE - 20)
                            pygame.draw.line(surf, (40, 110, 20),
                                             (vn_x, sy + 2), (vn_x + 1, sy + TILE - 6), 1)
    
                # ── Special tile markers ──────────────────────────────────────

                # Village — draw a pixel-art cottage house
                if (tx, ty) == (vx_t, vy_t):
                    T = TILE
                    # Foundation / base ground clear
                    pygame.draw.rect(surf, (185, 155, 100),
                                     (sx + 3, sy + 3, T - 6, T - 6))
                    # Walls
                    pygame.draw.rect(surf, (210, 178, 115),
                                     (sx + 6, sy + T // 2 - 2, T - 12, T // 2))
                    pygame.draw.rect(surf, (160, 130, 80),
                                     (sx + 6, sy + T // 2 - 2, T - 12, T // 2), 1)
                    # Roof triangle
                    roof_pts = [(sx + T // 2, sy + 4),
                                (sx + 3,      sy + T // 2),
                                (sx + T - 4,  sy + T // 2)]
                    pygame.draw.polygon(surf, (148, 62, 38), roof_pts)
                    pygame.draw.polygon(surf, (110, 42, 22), roof_pts, 1)
                    # Chimney (top-right side)
                    ch_x = sx + T - 16
                    pygame.draw.rect(surf, (130, 95, 65),
                                     (ch_x, sy + 7, 6, T // 2 - 5))
                    # Animated smoke puff
                    s_off = (tick_ms // 450) % 6
                    pygame.draw.circle(surf, (200, 200, 200),
                                       (ch_x + 3, sy + 6 - s_off), 3)
                    # Door
                    pygame.draw.rect(surf, (92, 52, 20),
                                     (sx + T // 2 - 4, sy + T - 15, 8, 11))
                    # Two windows with cross panes
                    for wx3 in (sx + 7, sx + T - 17):
                        pygame.draw.rect(surf, (215, 235, 255),
                                         (wx3, sy + T // 2 + 2, 8, 7))
                        pygame.draw.line(surf, (150, 175, 210),
                                         (wx3, sy + T // 2 + 5),
                                         (wx3 + 7, sy + T // 2 + 5), 1)
                        pygame.draw.line(surf, (150, 175, 210),
                                         (wx3 + 4, sy + T // 2 + 2),
                                         (wx3 + 4, sy + T // 2 + 9), 1)

                # Boss lair castle — drawn per-tile based on position in 3×3 grid
                elif abs(tx - bx_t) <= 1 and abs(ty - by_t) <= 1:
                    biome  = BIOMES[p.position_biome]
                    boss_id = biome.get("boss")
                    active  = boss_id and boss_id not in p.defeated_bosses
                    T  = TILE
                    dx_b = tx - bx_t
                    dy_b = ty - by_t
                    stone      = (62, 50, 44)
                    mortar     = (28, 22, 18)
                    dark       = (12, 9, 8)
                    battlement = (72, 58, 50)

                    if active:
                        if (dx_b, dy_b) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                            # ── Corner tower ────────────────────────────────
                            pygame.draw.circle(surf, stone,
                                               (sx + T // 2, sy + T // 2), T // 2 - 1)
                            pygame.draw.circle(surf, mortar,
                                               (sx + T // 2, sy + T // 2), T // 2 - 1, 2)
                            # Cross arrow slit
                            pygame.draw.rect(surf, dark,
                                             (sx + T // 2 - 2, sy + T // 2 - 8, 4, 11))
                            pygame.draw.rect(surf, dark,
                                             (sx + T // 2 - 6, sy + T // 2 - 3, 12, 4))
                            # Battlements along the top
                            for b in range(4):
                                bx4 = sx + 2 + b * (T // 4)
                                pygame.draw.rect(surf, battlement,
                                                 (bx4, sy + 1, T // 4 - 2, 5))

                        elif (dx_b, dy_b) == (0, -1):
                            # ── Top keep: tallest wall + red flag ───────────
                            pygame.draw.rect(surf, stone,
                                             (sx + 5, sy + 2, T - 10, T - 4))
                            pygame.draw.rect(surf, mortar,
                                             (sx + 5, sy + 2, T - 10, T - 4), 2)
                            # Battlements along top
                            seg_w = (T - 10) // 4
                            for b in range(4):
                                bx5 = sx + 5 + b * seg_w
                                pygame.draw.rect(surf, battlement,
                                                 (bx5, sy + 1, seg_w - 1, 5))
                            # Flagpole
                            pole_x = sx + T // 2
                            pygame.draw.line(surf, (195, 162, 95),
                                             (pole_x, sy + 2), (pole_x, sy + T // 2 - 1), 2)
                            # Waving flag (two triangles to suggest flutter)
                            flag_pts = [(pole_x, sy + 4),
                                        (pole_x + 13, sy + 9),
                                        (pole_x, sy + 14)]
                            pygame.draw.polygon(surf, (195, 18, 18), flag_pts)
                            # Skull dot on flag
                            pygame.draw.circle(surf, (230, 215, 195),
                                               (pole_x + 6, sy + 9), 3)
                            pygame.draw.circle(surf, dark,
                                               (pole_x + 5, sy + 8), 1)
                            pygame.draw.circle(surf, dark,
                                               (pole_x + 8, sy + 8), 1)

                        elif (dx_b, dy_b) == (0, 1):
                            # ── Bottom: drawbridge approach ──────────────────
                            # Small wall base at top
                            pygame.draw.rect(surf, stone,
                                             (sx + 5, sy + 2, T - 10, T // 3 - 1))
                            pygame.draw.rect(surf, mortar,
                                             (sx + 5, sy + 2, T - 10, T // 3 - 1), 1)
                            # Drawbridge plank boards
                            for pi in range(3):
                                py3 = sy + T // 3 + 2 + pi * ((T * 2 // 3 - 6) // 3)
                                pygame.draw.rect(surf, (118, 78, 35),
                                                 (sx + 7, py3, T - 14,
                                                  (T * 2 // 3 - 6) // 3 - 2))
                                pygame.draw.line(surf, (85, 52, 18),
                                                 (sx + 10, py3 + 2),
                                                 (sx + T - 12, py3 + 2), 1)
                            # Chain lines on sides
                            pygame.draw.line(surf, (135, 122, 105),
                                             (sx + 7, sy + T // 3),
                                             (sx + 7, sy + T - 5), 1)
                            pygame.draw.line(surf, (135, 122, 105),
                                             (sx + T - 8, sy + T // 3),
                                             (sx + T - 8, sy + T - 5), 1)

                        elif dx_b != 0 and dy_b == 0:
                            # ── Side wall with battlements + arrow slit ──────
                            pygame.draw.rect(surf, stone,
                                             (sx + 3, sy + 4, T - 6, T - 8))
                            pygame.draw.rect(surf, mortar,
                                             (sx + 3, sy + 4, T - 6, T - 8), 1)
                            # Top battlements
                            for b in range(3):
                                bx6 = sx + 3 + b * (T // 3)
                                pygame.draw.rect(surf, battlement,
                                                 (bx6, sy + 1, T // 3 - 2, 5))
                            # Vertical arrow slit
                            pygame.draw.rect(surf, dark,
                                             (sx + T // 2 - 2, sy + T // 3,
                                              4, T // 3 + 4))

                        elif (dx_b, dy_b) == (0, 0):
                            # ── Center: gate entrance with portcullis ────────
                            pygame.draw.rect(surf, stone,
                                             (sx + 2, sy + 2, T - 4, T - 4))
                            pygame.draw.rect(surf, mortar,
                                             (sx + 2, sy + 2, T - 4, T - 4), 1)
                            # Arch opening
                            arch_cx = sx + T // 2
                            arch_cy = sy + T // 2 - 4
                            arch_r  = T // 4
                            # Filled arch circle + rect body
                            pygame.draw.circle(surf, dark, (arch_cx, arch_cy), arch_r)
                            pygame.draw.rect(surf, dark,
                                             (arch_cx - arch_r, arch_cy,
                                              arch_r * 2, T - (arch_cy - sy) - 3))
                            # Portcullis vertical bars
                            for i in range(3):
                                px4 = arch_cx - arch_r + 3 + i * (arch_r * 2 // 3)
                                pygame.draw.line(surf, (75, 88, 70),
                                                 (px4, arch_cy - 2),
                                                 (px4, sy + T - 5), 1)
                            # Portcullis horizontal bar
                            pygame.draw.line(surf, (75, 88, 70),
                                             (arch_cx - arch_r + 2,
                                              arch_cy + arch_r // 2),
                                             (arch_cx + arch_r - 2,
                                              arch_cy + arch_r // 2), 1)
                            # Pulsing red ominous glow inside arch
                            pulse = int(120 + 65 * math.sin(tick_ms * 0.004))
                            pygame.draw.circle(surf, (min(255, pulse), 8, 8),
                                               (arch_cx, arch_cy + arch_r // 2),
                                               arch_r - 5)

                    else:
                        # ── Defeated boss: ruined castle rubble ──────────────
                        for bi in range(2):
                            for bj in range(2):
                                rx4 = sx + 2 + bj * (T // 2)
                                ry4 = sy + 2 + bi * (T // 2)
                                pygame.draw.rect(surf, (68, 55, 48),
                                                 (rx4, ry4, T // 2 - 3, T // 2 - 3))
                        # Scattered rubble dots
                        for ri in range(4):
                            rdx = sx + 5 + (t_hash * (ri + 1) * 11) % (T - 12)
                            rdy = sy + 5 + (t_hash * (ri + 1) *  7) % (T - 12)
                            pygame.draw.circle(surf, (95, 78, 68),
                                               (rdx, rdy), 2)

                # Rare skill area → glowing rune-stone pedestal
                coord = (tx, ty)
                _in_boss_zone = abs(tx - bx_t) <= 1 and abs(ty - by_t) <= 1
                if coord in _rare_area_map and not _in_boss_zone:
                    ra = _rare_area_map[coord]
                    if ra["skill"] not in p.known_skills:
                        T    = TILE
                        _mcx = sx + T // 2
                        _mcy = sy + T // 2
                        # Pulsing purple backdrop
                        _pp = int(25 + 20 * math.sin(tick_ms * 0.003 + t_hash * 0.7))
                        pygame.draw.rect(surf, (52 + _pp, 22, 82 + _pp),
                                         (sx + 5, sy + 5, T - 10, T - 10), border_radius=4)
                        # Stone pedestal
                        pygame.draw.rect(surf, (88, 78, 100),
                                         (_mcx - 9, _mcy + 2, 18, 10))
                        pygame.draw.rect(surf, (105, 95, 118),
                                         (_mcx - 11, _mcy + 10, 22, 5))
                        # Glowing magic orb on top
                        _ob = int(140 + 90 * math.sin(tick_ms * 0.005 + t_hash))
                        pygame.draw.circle(surf, (_ob // 3, 15, min(255, _ob)),
                                           (_mcx, _mcy - 6), 9)
                        pygame.draw.circle(surf, (175, 145, 255), (_mcx, _mcy - 6), 6)
                        pygame.draw.circle(surf, (220, 205, 255),
                                           (_mcx - 2, _mcy - 8), 3)
                        # 4-pointed star rays
                        _ray = 7 + int(3 * math.sin(tick_ms * 0.004))
                        for _ri in range(4):
                            _ang = _ri * math.pi / 2 + tick_ms * 0.0008
                            _ex  = _mcx + int(math.cos(_ang) * _ray)
                            _ey  = (_mcy - 6) + int(math.sin(_ang) * _ray)
                            pygame.draw.line(surf, (135, 95, 215),
                                             (_mcx, _mcy - 6), (_ex, _ey), 1)

                # Extra named locations — full pixel art per type
                if coord in _extra_loc_map:
                    T    = TILE
                    loc   = _extra_loc_map[coord]
                    ltype = loc["type"]
                    _mcx  = sx + T // 2
                    _mcy  = sy + T // 2

                    if ltype == "camp":
                        # Warm ground pad
                        pygame.draw.rect(surf, (98, 62, 22),
                                         (sx + 4, sy + 4, T - 8, T - 8), border_radius=3)
                        # Two crossed logs
                        pygame.draw.line(surf, (78, 46, 10),
                                         (sx + 8, sy + T - 12), (_mcx + 4, _mcy + 6), 4)
                        pygame.draw.line(surf, (78, 46, 10),
                                         (sx + T - 10, sy + T - 12), (_mcx - 4, _mcy + 6), 4)
                        pygame.draw.line(surf, (112, 70, 20),
                                         (sx + 8, sy + T - 12), (_mcx + 4, _mcy + 6), 2)
                        pygame.draw.line(surf, (112, 70, 20),
                                         (sx + T - 10, sy + T - 12), (_mcx - 4, _mcy + 6), 2)
                        # Ember base
                        pygame.draw.ellipse(surf, (175, 78, 8),
                                            (_mcx - 6, _mcy + 4, 12, 5))
                        # Animated flame
                        _fl = int(4 * math.sin(tick_ms * 0.009 + t_hash))
                        pygame.draw.polygon(surf, (212, 112, 8), [
                            (_mcx - 7, _mcy + 4), (_mcx - 2, _mcy - 6 + _fl),
                            (_mcx, _mcy - 12 + _fl),
                            (_mcx + 2, _mcy - 6 + _fl), (_mcx + 7, _mcy + 4)])
                        pygame.draw.polygon(surf, (255, 212, 32), [
                            (_mcx - 3, _mcy + 2), (_mcx - 1, _mcy - 3 + _fl),
                            (_mcx, _mcy - 8 + _fl),
                            (_mcx + 1, _mcy - 3 + _fl), (_mcx + 3, _mcy + 2)])
                        pygame.draw.circle(surf, (255, 248, 175),
                                           (_mcx, _mcy - 3 + _fl // 2), 2)

                    elif ltype == "well":
                        # Stone-blue backdrop
                        pygame.draw.rect(surf, (75, 95, 115),
                                         (sx + 4, sy + 4, T - 8, T - 8), border_radius=3)
                        # Wooden support posts
                        pygame.draw.rect(surf, (102, 68, 20),
                                         (_mcx - 14, _mcy - 10, 4, 22))
                        pygame.draw.rect(surf, (102, 68, 20),
                                         (_mcx + 10, _mcy - 10, 4, 22))
                        # Cross-beam
                        pygame.draw.rect(surf, (128, 85, 28),
                                         (_mcx - 14, _mcy - 12, 28, 5))
                        pygame.draw.rect(surf, (158, 112, 48),
                                         (_mcx - 14, _mcy - 12, 28, 2))
                        # Hanging rope
                        pygame.draw.line(surf, (172, 138, 58),
                                         (_mcx, _mcy - 7), (_mcx, _mcy - 1), 2)
                        # Stone rim
                        pygame.draw.ellipse(surf, (112, 122, 132),
                                            (_mcx - 12, _mcy - 4, 24, 14))
                        pygame.draw.ellipse(surf, (82, 93, 105),
                                            (_mcx - 12, _mcy - 4, 24, 14), 2)
                        # Water inside
                        pygame.draw.ellipse(surf, (32, 85, 172),
                                            (_mcx - 8, _mcy + 1, 16, 7))
                        _wv = int(math.sin(tick_ms * 0.004 + t_hash))
                        # V-ripple replaces draw.arc (unreliable on Android)
                        pygame.draw.line(surf, (72, 142, 222),
                                         (_mcx - 4, _mcy + 4 + _wv),
                                         (_mcx,     _mcy + 2 + _wv), 1)
                        pygame.draw.line(surf, (72, 142, 222),
                                         (_mcx,     _mcy + 2 + _wv),
                                         (_mcx + 4, _mcy + 4 + _wv), 1)

                    elif ltype == "shrine":
                        # Sacred purple backdrop
                        pygame.draw.rect(surf, (82, 52, 112),
                                         (sx + 4, sy + 4, T - 8, T - 8), border_radius=3)
                        # Stepped stone base (two steps)
                        pygame.draw.rect(surf, (85, 82, 93),
                                         (_mcx - 12, _mcy + 4, 24, 10))
                        pygame.draw.rect(surf, (98, 93, 106),
                                         (_mcx - 8, _mcy - 4, 16, 10))
                        # Central pillar
                        pygame.draw.rect(surf, (80, 76, 90),
                                         (_mcx - 4, _mcy - 15, 8, 19))
                        pygame.draw.rect(surf, (106, 100, 116),
                                         (_mcx - 4, _mcy - 15, 3, 19))
                        # Candles on base
                        pygame.draw.rect(surf, (212, 205, 175),
                                         (_mcx - 11, _mcy + 1, 3, 8))
                        pygame.draw.rect(surf, (212, 205, 175),
                                         (_mcx + 8, _mcy + 1, 3, 8))
                        # Candle flames
                        pygame.draw.circle(surf, (255, 198, 32),
                                           (_mcx - 10, _mcy), 2)
                        pygame.draw.circle(surf, (255, 198, 32),
                                           (_mcx + 9, _mcy), 2)
                        # Pulsing gem on pillar top
                        _gb = int(165 + 75 * math.sin(tick_ms * 0.005 + t_hash))
                        pygame.draw.circle(surf,
                                           (min(255, _gb // 2 + 80), 32,
                                            min(255, _gb)),
                                           (_mcx, _mcy - 17), 5)
                        pygame.draw.circle(surf, (212, 192, 255),
                                           (_mcx - 1, _mcy - 19), 2)

                    elif ltype == "altar":
                        # Arcane dark backdrop
                        pygame.draw.rect(surf, (42, 16, 62),
                                         (sx + 4, sy + 4, T - 8, T - 8), border_radius=3)
                        # Slab support legs
                        pygame.draw.rect(surf, (50, 40, 60),
                                         (_mcx - 10, _mcy + 7, 5, 8))
                        pygame.draw.rect(surf, (50, 40, 60),
                                         (_mcx + 5, _mcy + 7, 5, 8))
                        # Stone slab
                        pygame.draw.rect(surf, (58, 46, 70),
                                         (_mcx - 13, _mcy - 1, 26, 10))
                        pygame.draw.rect(surf, (70, 58, 82),
                                         (_mcx - 12, _mcy - 2, 24, 3))
                        # Glowing rune lines on slab
                        _rb = int(118 + 92 * math.sin(tick_ms * 0.006 + t_hash))
                        _rc = (min(255, _rb), 16, min(255, _rb + 32))
                        pygame.draw.line(surf, _rc,
                                         (_mcx - 8, _mcy + 3), (_mcx + 8, _mcy + 3), 1)
                        pygame.draw.line(surf, _rc,
                                         (_mcx - 5, _mcy), (_mcx + 5, _mcy + 6), 1)
                        pygame.draw.line(surf, _rc,
                                         (_mcx + 5, _mcy), (_mcx - 5, _mcy + 6), 1)
                        # Hovering orb (bobs up/down)
                        _oy  = _mcy - 12 + int(2 * math.sin(tick_ms * 0.003 + t_hash))
                        _ov  = int(148 + 88 * math.sin(tick_ms * 0.004 + t_hash))
                        pygame.draw.circle(surf,
                                           (min(255, _ov), 16, min(255, _ov + 48)),
                                           (_mcx, _oy), 7)
                        pygame.draw.circle(surf, (208, 172, 255),
                                           (_mcx - 1, _oy - 2), 3)
                        # Orbiting sparks
                        for _si in range(3):
                            _sang = _si * 2.094 + tick_ms * 0.004
                            _spx  = _mcx + int(math.cos(_sang) * 10)
                            _spy  = _oy  + int(math.sin(_sang) * 4)
                            pygame.draw.circle(surf, (192, 142, 255),
                                               (_spx, _spy), 1)

                    elif ltype == "ruins":
                        # Stone rubble backdrop
                        pygame.draw.rect(surf, (80, 72, 62),
                                         (sx + 4, sy + 4, T - 8, T - 8), border_radius=3)
                        # Left column (broken top)
                        pygame.draw.rect(surf, (90, 82, 73),
                                         (_mcx - 14, sy + 10, 9, T - 22))
                        pygame.draw.rect(surf, (106, 96, 86),
                                         (_mcx - 14, sy + 10, 4, T - 22))
                        pygame.draw.rect(surf, (66, 59, 51),
                                         (_mcx - 14, sy + 8, 9, 5))
                        # Chipped corner on left column cap
                        pygame.draw.polygon(surf, (80, 72, 62), [
                            (_mcx - 8, sy + 8),
                            (_mcx - 5, sy + 8),
                            (_mcx - 5, sy + 13)])
                        # Right column (intact, taller)
                        pygame.draw.rect(surf, (90, 82, 73),
                                         (_mcx + 5, sy + 6, 9, T - 17))
                        pygame.draw.rect(surf, (106, 96, 86),
                                         (_mcx + 5, sy + 6, 4, T - 17))
                        pygame.draw.rect(surf, (66, 59, 51),
                                         (_mcx + 5, sy + 4, 9, 5))
                        # Broken arch lintel — polyline replaces draw.arc
                        pygame.draw.lines(surf, (73, 66, 58), False, [
                            (_mcx - 13, sy + 21),
                            (_mcx - 10, sy + 14),
                            (_mcx - 5,  sy + 11),
                            (_mcx,      sy + 10),
                            (_mcx + 5,  sy + 11),
                            (_mcx + 10, sy + 14),
                            (_mcx + 13, sy + 21),
                        ], 3)
                        # Scattered rubble
                        for _ri in range(4):
                            _rrx = _mcx - 7 + (_ri * 5 + (t_hash >> 5)) % 16
                            _rry = sy + T - 14 + (_ri * 3 + (t_hash >> 8)) % 7
                            pygame.draw.rect(surf, (96, 88, 78),
                                             (_rrx, _rry, 4 + _ri % 2, 3))

                    elif ltype == "chest":
                        # Gold backdrop
                        pygame.draw.rect(surf, (115, 85, 16),
                                         (sx + 4, sy + 4, T - 8, T - 8), border_radius=3)
                        # Chest body
                        pygame.draw.rect(surf, (105, 60, 16),
                                         (_mcx - 13, _mcy - 1, 26, 14))
                        pygame.draw.rect(surf, (135, 80, 26),
                                         (_mcx - 12, _mcy - 1, 24, 4))
                        # Lid (slightly open)
                        pygame.draw.polygon(surf, (125, 70, 20), [
                            (_mcx - 13, _mcy - 1),
                            (_mcx - 11, _mcy - 11),
                            (_mcx + 11, _mcy - 11),
                            (_mcx + 13, _mcy - 1)])
                        # Lid highlight edge
                        pygame.draw.line(surf, (155, 100, 40),
                                         (_mcx - 10, _mcy - 10),
                                         (_mcx + 10, _mcy - 10), 1)
                        # Gold rim stripe on body
                        pygame.draw.rect(surf, (192, 152, 32),
                                         (_mcx - 13, _mcy - 2, 26, 3))
                        # Lock
                        pygame.draw.circle(surf, (192, 152, 26),
                                           (_mcx, _mcy + 5), 4)
                        pygame.draw.circle(surf, (142, 102, 10),
                                           (_mcx, _mcy + 5), 4, 1)
                        pygame.draw.rect(surf, (142, 102, 10),
                                         (_mcx - 2, _mcy + 5, 4, 5))
                        # Gold glow leaking from lid gap
                        _gl = int(160 + 60 * math.sin(tick_ms * 0.005 + t_hash))
                        pygame.draw.line(surf,
                                         (min(255, _gl + 80), min(255, _gl), 22),
                                         (_mcx - 9, _mcy - 10),
                                         (_mcx + 9, _mcy - 10), 2)
                        # Rotating sparkles above chest
                        for _sp in range(3):
                            _spang = _sp * 2.094 + tick_ms * 0.003
                            _spx2  = _mcx + int(math.cos(_spang) * 11)
                            _spy2  = _mcy - 14 + int(math.sin(_spang) * 5)
                            pygame.draw.circle(surf, (255, 228, 58),
                                               (_spx2, _spy2), 1)

                    else:
                        # Unknown type — plain coloured square fallback
                        pygame.draw.rect(surf, (120, 100, 80),
                                         (sx + 5, sy + 5, T - 10, T - 10),
                                         border_radius=3)

        # Wandering map enemies
        for enemy in self.game.world.get_enemies(p.position_biome, p.level):
            enemy.draw(surf, cx, cy, tick_ms)

        # Player — draw pixel-art sprite centred in the tile (drawn on top of enemies)
        px  = p.position_x * TILE - cx
        py  = p.position_y * TILE - cy
        pcx = px + TILE // 2
        pcy = py + TILE // 2
        if tmap.tile_at(p.position_x, p.position_y) == "water":
            draw_player_in_boat(surf, p.char_class, pcx, pcy, TILE - 8, tick_ms)
        else:
            draw_player_sprite(surf, p.char_class, pcx, pcy, TILE - 8, tick_ms)

        # ── Remote player (MP) ────────────────────────────────────────────────
        if (self.game.mp_mode
                and self.game.mp_peer_x >= 0
                and self.game.mp_peer_biome == p.position_biome):
            rsx = self.game.mp_peer_x * TILE - cx + TILE // 2
            rsy = self.game.mp_peer_y * TILE - cy + TILE // 2
            peer_d = self.game.mp_peer_dict
            peer_cls = peer_d.get("char_class", "warrior")
            peer_tile = tmap.tile_at(self.game.mp_peer_x, self.game.mp_peer_y)
            # Draw using the same sprite system as the local player
            if peer_tile == "water":
                draw_player_in_boat(surf, peer_cls, rsx, rsy, TILE - 8, tick_ms)
            else:
                draw_player_sprite(surf, peer_cls, rsx, rsy, TILE - 8, tick_ms)
            # Cyan glow ring so the peer stands out
            pygame.draw.circle(surf, (0, 230, 210), (rsx, rsy), TILE // 2 - 1, 2)
            # Name + level tag
            if self.game.mp_mode == "host":
                peer_name = (self.game.mp_server.guest_name
                             if self.game.mp_server else peer_d.get("name", ""))
            else:
                peer_name = (self.game.mp_client.host_name
                             if self.game.mp_client else peer_d.get("name", ""))
            peer_lvl  = peer_d.get("level", "")
            tag = f"{peer_name} Lv{peer_lvl}" if peer_lvl else peer_name
            if tag:
                # Semi-transparent name plate
                tag_w = len(tag) * 7 + 6
                tag_x = rsx - tag_w // 2
                tag_y = rsy - TILE // 2 - 16
                pygame.draw.rect(surf, (0, 0, 0, 160),
                                 (tag_x - 2, tag_y - 1, tag_w + 4, 14),
                                 border_radius=3)
                draw_text(surf, tag, tag_x, tag_y, (0, 255, 240), size=11)

            # Co-op battle join prompt: peer is in a battle, show blinking hint
            if self.game.mp_coop_battle:
                hint_y = SCREEN_H // 2 - 30
                hint_bg = pygame.Surface((400, 38), pygame.SRCALPHA)
                hint_bg.fill((0, 0, 0, 160))
                surf.blit(hint_bg, (SCREEN_W // 2 - 200, hint_y - 4))
                blink = (tick_ms // 500) % 2 == 0
                col = (255, 220, 50) if blink else (200, 170, 30)
                draw_text_centered(surf, "⚔ Ally is in battle!  [J] to join", hint_y, col,
                                   size=16, shadow=True)

        # HUD
        self._draw_hud(surf, p)

        # D-pad
        for btn in self.dpad.values():
            btn.draw(surf)

        # Bottom buttons
        for btn in (self.btn_menu, self.btn_inv, self.btn_skills, self.btn_pet):
            btn.draw(surf)

        # Message
        if self.message_timer > 0:
            draw_text_centered(surf, self.message, SCREEN_H // 2 - 40, YELLOW, size=18, shadow=True)

        # Dialog
        if self.dialog:
            self.dialog.draw(surf)

        # ── Multiplayer overlays ──────────────────────────────────────────────
        if self.game.mp_mode:
            self._draw_mp_overlay(surf)

    def _draw_hud(self, surf, p):
        # Top-left info panel
        panel = pygame.Rect(0, 0, 320, 90)
        draw_panel(surf, panel)
        draw_text(surf, f"{p.name}  Lv{p.level} {CLASSES[p.char_class]['name']}", 8, 6, GOLD, size=14)
        draw_bar(surf, 8, 26, 200, 14, p.hp, p.max_hp, HP_COL, label=f"HP {p.hp}/{p.max_hp}")
        draw_bar(surf, 8, 44, 200, 14, p.mp, p.max_mp, MP_COL, label=f"MP {p.mp}/{p.max_mp}")
        exp_need = p.exp_needed()
        draw_bar(surf, 8, 62, 200, 12, p.exp, exp_need, EXP_COL, label=f"EXP {p.exp}/{exp_need}")
        draw_text(surf, f"G:{p.gold}", 215, 28, GOLD, size=13)

        # Biome name
        biome_name = BIOMES[p.position_biome]["name"]
        draw_text_centered(surf, biome_name, 6, WHITE, size=14)

        # Mini-map (top-right) — float-scaled so 100×80 tiles all fit
        mm_w = 120
        mm_h = int(mm_w * MAP_H / MAP_W)   # keep aspect ratio ≈ 96
        mm_rect = pygame.Rect(SCREEN_W - mm_w - 4, 4, mm_w, mm_h)
        draw_panel(surf, mm_rect)
        tmap  = self._get_map()
        cxs   = mm_w / MAP_W   # horizontal scale (pixels per map tile)
        cys   = mm_h / MAP_H   # vertical   scale

        # Draw each tile as a 1- or 2-px rectangle
        for ty in range(MAP_H):
            for tx in range(MAP_W):
                tile = tmap.tile_at(tx, ty)
                col  = TILE_COL.get(tile, (40, 40, 40))
                mx   = mm_rect.x + int(tx * cxs)
                my   = mm_rect.y + int(ty * cys)
                mw   = max(1, int((tx + 1) * cxs) - int(tx * cxs))
                mh   = max(1, int((ty + 1) * cys) - int(ty * cys))
                pygame.draw.rect(surf, col, (mx, my, mw, mh))

        # Enemy dots (red)
        for enemy in self.game.world.get_enemies(p.position_biome, p.level):
            ex = mm_rect.x + int(enemy.x * cxs + cxs * 0.5)
            ey = mm_rect.y + int(enemy.y * cys + cys * 0.5)
            if mm_rect.collidepoint(ex, ey):
                pygame.draw.circle(surf, (220, 50, 50), (ex, ey), 2)

        # Player dot (white, larger — drawn on top)
        pdx = mm_rect.x + int(p.position_x * cxs + cxs * 0.5)
        pdy = mm_rect.y + int(p.position_y * cys + cys * 0.5)
        pygame.draw.circle(surf, WHITE, (pdx, pdy), 3)

        # Active pet
        if p.active_pet:
            pet = p.active_pet
            draw_text(surf, f"♦ {pet.name} Lv{pet.level}", 8, 82, tuple(pet.color[:3]), size=12)

        # Remote player dot on mini-map (teal)
        if (self.game.mp_mode
                and self.game.mp_peer_x >= 0
                and self.game.mp_peer_biome == p.position_biome):
            rdx = mm_rect.x + int(self.game.mp_peer_x * cxs + cxs * 0.5)
            rdy = mm_rect.y + int(self.game.mp_peer_y * cys + cys * 0.5)
            if mm_rect.collidepoint(rdx, rdy):
                pygame.draw.circle(surf, (0, 220, 210), (rdx, rdy), 3)

    def _draw_mp_overlay(self, surf):
        """Draw MP status bar, chat log, and chat input box."""
        g = self.game

        # ── Status bar (top-centre, below biome name) ──────────────────────
        if g.mp_mode == "host":
            peer_obj  = g.mp_server
            role_text = "HOST"
            con_col   = (60, 220, 80) if (peer_obj and peer_obj.connected) else (220, 80, 60)
            peer_name = peer_obj.guest_name if (peer_obj and peer_obj.connected) else "waiting..."
        else:
            peer_obj  = g.mp_client
            role_text = "GUEST"
            con_col   = (60, 220, 80) if (peer_obj and peer_obj.connected) else (220, 80, 60)
            peer_name = peer_obj.host_name if (peer_obj and peer_obj.connected) else "disconnected"

        status_txt = f"[MP {role_text}]  {peer_name}"
        sw = get_font(12).size(status_txt)[0] + 14
        sx_s = SCREEN_W // 2 - sw // 2
        pygame.draw.rect(surf, (0, 0, 0, 160),
                         (sx_s - 1, 22, sw + 2, 18), border_radius=4)
        pygame.draw.rect(surf, con_col, (sx_s - 1, 22, sw + 2, 18), 1, border_radius=4)
        draw_text(surf, status_txt, sx_s + 6, 24, con_col, size=12)

        # ── Chat log (bottom-left, above buttons) ──────────────────────────
        show_chat = self._chat_typing or self._chat_timer > 0
        chat_lines = g.mp_chat_log[-4:]   # last 4 lines
        chat_bottom = SCREEN_H - 58       # just above bottom buttons
        if show_chat and chat_lines:
            line_h = 16
            panel_h = len(chat_lines) * line_h + 6
            panel_y = chat_bottom - panel_h - (24 if self._chat_typing else 2)
            panel_w = 380
            chat_panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            chat_panel.fill((0, 0, 0, 140))
            surf.blit(chat_panel, (4, panel_y))
            for i, line in enumerate(chat_lines):
                draw_text(surf, line, 8, panel_y + 3 + i * line_h, (200, 220, 200), size=12)

        # ── Chat input box ─────────────────────────────────────────────────
        if self._chat_typing:
            box_y  = chat_bottom - 22
            box_w  = 380
            pygame.draw.rect(surf, (20, 20, 30), (4, box_y, box_w, 20), border_radius=3)
            pygame.draw.rect(surf, (0, 200, 190), (4, box_y, box_w, 20), 1, border_radius=3)
            cursor_char = "|" if pygame.time.get_ticks() % 800 < 400 else ""
            draw_text(surf, self._chat_input + cursor_char, 8, box_y + 3, WHITE, size=12)
            draw_text(surf, "Enter=send  Esc=cancel", 8, box_y - 14, (100, 140, 100), size=11)
        elif g.mp_mode:
            # Hint: press T to chat
            draw_text(surf, "[T] Chat", 8, chat_bottom - 14, (80, 110, 80), size=11)


# ═════════════════════════════════════════════════════════════════════════════
# COMBAT SCREEN
# ═════════════════════════════════════════════════════════════════════════════
class CombatScreen(Screen):
    def __init__(self, game, monster_id: str, is_boss: bool = False,
                 coop_mode: str = None):
        """
        coop_mode:
          None        — solo (or solo MP where peer isn't in this battle)
          "initiator" — started the battle; peer may join later
          "joiner"    — joined peer's battle; waits for initiator's first turn
        """
        super().__init__(game)
        from entities.monster import MonsterInstance
        self.monster = MonsterInstance(monster_id, game.player.level,
                                       force_variant="normal" if is_boss else None)
        self.is_boss = is_boss

        # ── Co-op state ───────────────────────────────────────────────────────
        # coop_mode stays None until the peer explicitly sends MSG_COOP_JOIN.
        # This means two players fighting different enemies work independently
        # with no turn-waiting — co-op only kicks in when the peer presses J.
        self.coop_mode = coop_mode    # None | "initiator" | "joiner"
        self.coop_ally: dict = {}     # {name, char_class, level, hp, max_hp}

        # Joiner waits for initiator's first action + MSG_COOP_SYNC
        if coop_mode == "joiner":
            self.state = "ally_turn"
        else:
            self.state = "player_turn"

        # Always tell peer a battle started (shows the [J] join prompt on their
        # exploration screen). We are NOT in co-op mode yet — that only happens
        # when they actually press J and we receive MSG_COOP_JOIN.
        if game.mp_mode and game.mp_peer and coop_mode != "joiner":
            from networking.protocol import MSG_BATTLE_START
            game.mp_peer.send(MSG_BATTLE_START, {
                "monster_id": monster_id,
                "is_boss":    is_boss,
            })

        # Purge any stale co-op messages left over from a previous battle
        # (e.g. a victory signal that arrived late) so they don't fire instantly
        game.mp_coop_inbox.clear()

        self.log = []
        self.log_scroll = 0
        self.turn = 0
        self.animation_timer = 0
        self.flash = False
        self.result_timer = 0
        self.captured_monster = None

        # Loot
        self.loot_items = []
        self.exp_gained = 0
        self.gold_gained = 0
        self.level_up_msgs = []

        # Action buttons
        bw, bh = 200, 44
        by = SCREEN_H - 58
        self.main_btns = {
            "attack": Button(pygame.Rect(20,  by, bw, bh), "⚔ Attack",  DARK_RED),
            "skill":  Button(pygame.Rect(280, by, bw, bh), "✦ Skills",  DARK_BLUE),
            "item":   Button(pygame.Rect(540, by, bw, bh), "◎ Items",   DARK_GREEN),
            "flee":   Button(pygame.Rect(800, by, bw, bh), "↩ Flee",    MID_GRAY),
            "capture":Button(pygame.Rect(1060,by, bw, bh), "◈ Capture", (100,80,40)),
        }
        # Submenu (skills / items)
        self.submenu = None   # "skills" | "items"
        self.skill_list = None
        self.item_list  = None

        # Capture: enabled solo only (can't capture in co-op — shared monster)
        p = game.player
        self.main_btns["capture"].enabled = (
            p.has_item("capture_net") and self.monster.capturable
            and coop_mode is None
        )

        self.add_log(f"A wild {self.monster.name} appeared!")
        if self.monster.variant == "alpha":
            self.add_log("An ALPHA variant! Much stronger!")
        elif self.monster.variant == "evolved":
            self.add_log("An EVOLVED form encountered!")

        # Start appropriate music
        biome = game.player.position_biome if game.player else 'verdant_plains'
        if is_boss:
            game.music.play_boss(monster_id)
        elif self.monster.variant == "alpha":
            game.music.play_alpha(biome)
        else:
            game.music.play_battle(biome)

    def add_log(self, msg: str):
        self.log.append(msg)
        if len(self.log) > 60:
            self.log = self.log[-60:]

    def handle_event(self, event):
        if self.state == "loot":
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN, pygame.FINGERDOWN):
                self._end_combat()
            return

        if self.state == "game_over":
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.game.set_screen("main_menu")
            return

        if self.state != "player_turn":
            return

        if self.submenu == "skills":
            idx = self.skill_list.handle_event(event)
            if idx >= 0:
                sk_id = self.skill_list.items[idx][1]
                self._player_do("skill", skill_id=sk_id)
                self.submenu = None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.submenu = None

        elif self.submenu == "items":
            idx = self.item_list.handle_event(event)
            if idx >= 0:
                item_id = self.item_list.items[idx][1]
                self._player_do("item", item_id=item_id)
                self.submenu = None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.submenu = None

        else:
            for key, btn in self.main_btns.items():
                if btn.is_clicked(event):
                    if key == "attack":
                        self._player_do("attack")
                    elif key == "skill":
                        self._open_skill_menu()
                    elif key == "item":
                        self._open_item_menu()
                    elif key == "flee":
                        self._player_do("flee")
                    elif key == "capture":
                        self._try_capture()

    def _open_skill_menu(self):
        p = self.game.player
        items = []
        for sk_id in p.known_skills:
            sk = SKILLS.get(sk_id, {})
            if sk.get("type") != "active":
                continue
            cost = sk.get("mp_cost", 0)
            can_use = p.mp >= cost
            col = WHITE if can_use else UI_DIM
            label = f"{sk['name']}  (MP:{cost})"
            items.append((label, sk_id, col))
        self.skill_list = ScrollList(pygame.Rect(100, 200, SCREEN_W - 200, 300), items, item_h=40)
        self.submenu = "skills"

    def _open_item_menu(self):
        p = self.game.player
        items = []
        for entry in p.inventory:
            item = ITEMS.get(entry["id"], {})
            if item.get("type") != "consumable":
                continue
            label = f"{item['name']} x{entry['qty']}"
            rarity_col = RARITY_COLORS.get(entry.get("rarity","common"), WHITE)
            items.append((label, entry["id"], rarity_col))
        if not items:
            items = [("No usable items", None, UI_DIM)]
        self.item_list = ScrollList(pygame.Rect(100, 200, SCREEN_W - 200, 300), items, item_h=40)
        self.submenu = "items"

    def _player_do(self, atype: str, **kwargs):
        from systems.combat import process_player_action, tick_player_status
        from entities.pet import capture_chance
        p = self.game.player

        if atype == "flee":
            flee_chance = 0.4 + p.luck * 0.01
            if random.random() < flee_chance:
                self.add_log("You fled successfully!")
                if self.coop_mode and self.game.mp_peer:
                    from networking.protocol import MSG_BATTLE_END
                    self.game.mp_peer.send(MSG_BATTLE_END, {"outcome": "fled"})
                self.state = "loot"  # loot = end screen with no loot
                self.loot_items = []
                self.exp_gained = 0
                self.gold_gained = 0
                return
            else:
                self.add_log("Couldn't escape!")
                if not self._pet_turn():
                    self._monster_turn()
                    if self.coop_mode and self.state not in ("game_over", "loot"):
                        self._coop_send_action()
                        self.state = "ally_turn"
                return

        action = {"type": atype}
        action.update(kwargs)
        msgs = process_player_action(action, p, self.monster, p.active_pet)

        if "CAPTURE" in msgs or "OMEGA_CAPTURE" in msgs:
            self._try_capture(omega="OMEGA" in str(msgs))
            return

        # Escape items (smoke_bomb, teleport_scroll) — guaranteed flee
        if "ESCAPE" in msgs:
            self.add_log("You escaped using an item!")
            self.state = "loot"
            self.loot_items = []
            self.exp_gained = 0
            self.gold_gained = 0
            return

        for m in msgs:
            self.add_log(m)

        # Check monster death
        if not self.monster.is_alive():
            self._victory()
            return

        # Extra turn (Eternal Moment) — player acts again before pet/monster
        if p.has_extra_turn:
            p.has_extra_turn = False
            self.add_log("Extra turn!")
            return  # player acts again

        # Pet acts on its own separate turn
        if self._pet_turn():
            return  # monster killed by pet

        # Monster's turn
        self._monster_turn()

        # Co-op: after monster attacked us, hand control to ally
        if self.coop_mode and self.state not in ("game_over", "loot"):
            self._coop_send_action()
            self.state = "ally_turn"

    def _pet_turn(self) -> bool:
        """Automatically run the active pet's turn.

        Returns True if the monster was killed by the pet (victory triggered),
        False otherwise.  Safe to call when there is no living pet.
        """
        from systems.combat import process_pet_turn
        p   = self.game.player
        pet = p.active_pet
        if not pet or not pet.is_alive():
            return False
        self.add_log(f"── {pet.name}'s Turn ──")
        msgs = process_pet_turn(pet, p, self.monster)
        for m in msgs:
            self.add_log(m)
        if not self.monster.is_alive():
            self._victory()
            return True
        return False

    def _monster_turn(self):
        from systems.combat import process_monster_action, tick_player_status
        p = self.game.player

        # Monster status tick
        for m in self.monster.tick_status():
            self.add_log(m)
        if not self.monster.is_alive():
            self._victory(); return

        # Player status tick
        for m in tick_player_status(p):
            self.add_log(m)
        if not p.is_alive():
            self._game_over(); return

        # Monster action
        action = self.monster.choose_action()
        msgs = process_monster_action(action, self.monster, p, p.active_pet)
        for m in msgs:
            self.add_log(m)

        if not p.is_alive():
            self._game_over()
            return

        self.turn += 1
        if not self.coop_mode:
            self.state = "player_turn"
        # In co-op, _player_do handles state (either "ally_turn" or keeps "game_over")

    def _try_capture(self, omega: bool = False):
        from entities.pet import capture_chance, Pet
        p = self.game.player
        if not omega and not p.has_item("capture_net"):
            self.add_log("You need a Capture Net!")
            return
        if not omega:
            p.remove_item("capture_net")

        chance = capture_chance(self.monster, p)
        if omega:
            chance = min(0.95, chance * 2)

        if random.random() < chance:
            pet = Pet(self.monster.base_id, self.monster.name)
            if len(p.stored_pets) < MAX_STORED_PETS:
                p.stored_pets.append(pet)
                if p.active_pet is None:
                    p.active_pet = pet
                    p.stored_pets.remove(pet)
                self.add_log(f"Captured {self.monster.name}!")
                self.captured_monster = pet
            else:
                self.add_log("Pet storage is full!")
        else:
            self.add_log(f"{self.monster.name} broke free!")

        # Pet acts, then monster (unless monster already dead from capture)
        if self.monster.is_alive():
            if not self._pet_turn():
                self._monster_turn()

    def _victory(self, from_ally: bool = False):
        """Resolve the battle as a win.

        from_ally=True when triggered by a MSG_COOP_ACTION is_victory message —
        in that case we do NOT send our own is_victory back (prevents echo loop).
        """
        from systems.loot import roll_drops
        p = self.game.player
        self.state = "loot"
        self.game.music.play_victory()
        self.exp_gained  = self.monster.exp_reward
        self.gold_gained = self.monster.gold_reward
        p.gold += self.gold_gained

        # Pet EXP
        if p.active_pet:
            pet_exp = max(5, self.exp_gained // 4)
            if "beast_bond" in p.known_skills:
                pet_exp = int(pet_exp * 1.5)
            msgs = p.active_pet.gain_exp(pet_exp)
            for m in msgs:
                self.add_log(m)

        # Loot
        self.loot_items = roll_drops(self.monster, p)
        for item_id, qty, rarity in self.loot_items:
            p.add_item(item_id, qty, rarity)

        # Boss flag
        if self.is_boss:
            p.defeated_bosses.add(self.monster.monster_id)
            unlock = MONSTERS[self.monster.monster_id].get("story_unlock")
            if unlock and unlock.endswith("_access"):
                target = unlock.replace("_access", "")
                p.unlocked_biomes.add(target)
                p.discovered_biomes.add(target)
                self.add_log(f"New area unlocked: {BIOMES.get(target,{}).get('name', target)}!")
            if unlock == "ending":
                p.story_flags.add("game_complete")
            # Post-boss story
            post_lines = STORY["boss_post_dialogue"].get(self.monster.monster_id, [])
            if post_lines:
                self.game.pending_boss_dialogue = post_lines

        # Player EXP
        lvl_msgs = p.gain_exp(self.exp_gained)
        self.level_up_msgs = lvl_msgs

        # Subclass unlock
        if not p.subclass_chosen and p.level >= SUBCLASS_UNLOCK_LEVEL:
            self.game.pending_subclass = True

        p.battles_won += 1

        # Notify peer that the battle is won.
        # from_ally=True means the peer's action triggered this _victory — don't
        # echo the signal back or we get an infinite EXP / loot loop.
        if self.game.mp_mode and self.game.mp_peer and not from_ally:
            if self.coop_mode:
                self._coop_send_action(is_victory=True)
            else:
                from networking.protocol import MSG_BATTLE_END
                self.game.mp_peer.send(MSG_BATTLE_END, {"outcome": "victory"})
        self.game.mp_coop_battle = None

    def _game_over(self):
        self.state = "game_over"
        self.add_log("You have been defeated...")
        self.game.music.play_gameover()
        if self.game.mp_mode and self.game.mp_peer:
            if self.coop_mode:
                self._coop_send_action(is_game_over=True)
            else:
                from networking.protocol import MSG_BATTLE_END
                self.game.mp_peer.send(MSG_BATTLE_END, {"outcome": "defeat"})

    def _coop_send_action(self, is_victory: bool = False, is_game_over: bool = False):
        """Send our current state to the co-op partner after acting."""
        from networking.protocol import MSG_COOP_ACTION
        if self.game.mp_peer and self.game.player:
            p = self.game.player
            self.game.mp_peer.send(MSG_COOP_ACTION, {
                "monster_hp":    self.monster.hp,
                "is_victory":    is_victory,
                "is_game_over":  is_game_over,
                "ally_hp":       p.hp,
                "ally_max_hp":   p.max_hp,
            })

    def _handle_coop_msg(self, mtype: str, data: dict):
        """Process a single message from game.mp_coop_inbox."""
        from networking.protocol import (MSG_COOP_JOIN, MSG_COOP_SYNC,
                                          MSG_COOP_ACTION, MSG_BATTLE_END)

        # Once our battle is resolved, ignore everything except disconnects
        if self.state in ("loot", "game_over"):
            return

        if mtype == MSG_COOP_JOIN and self.coop_mode in (None, "initiator"):
            # A peer joined our battle — we become (or confirm as) initiator
            self.coop_mode = "initiator"
            self.coop_ally = {
                "name":       data.get("name", "Ally"),
                "char_class": data.get("char_class", "warrior"),
                "level":      data.get("level", 1),
                "hp":         data.get("hp", 100),
                "max_hp":     data.get("max_hp", 100),
            }
            self.add_log(f"✦ {self.coop_ally['name']} joined the battle!")
            # Send current monster HP so joiner can sync
            from networking.protocol import MSG_COOP_SYNC
            if self.game.mp_peer and self.game.player:
                p = self.game.player
                self.game.mp_peer.send(MSG_COOP_SYNC, {
                    "monster_hp":     self.monster.hp,
                    "monster_max_hp": self.monster.max_hp,
                    "ally_hp":        p.hp,
                    "ally_max_hp":    p.max_hp,
                })
            # Disable capture now that ally is here
            self.main_btns["capture"].enabled = False

        elif mtype == MSG_COOP_SYNC and self.coop_mode == "joiner":
            # Initiator sent us the current monster HP — sync it
            self.monster.hp = min(data.get("monster_hp", self.monster.hp),
                                  self.monster.max_hp)
            # Record ally info from peer_dict (filled by MSG_PEER_POS)
            peer_d = self.game.mp_peer_dict
            self.coop_ally = {
                "name":       peer_d.get("name", "Ally"),
                "char_class": peer_d.get("char_class", "warrior"),
                "level":      peer_d.get("level", 1),
                "hp":         data.get("ally_hp", 100),
                "max_hp":     data.get("ally_max_hp", 100),
            }
            self.add_log(f"✦ Joined {self.coop_ally['name']}'s battle! "
                         f"Monster HP: {int(self.monster.hp)}/{int(self.monster.max_hp)}")

        elif mtype == MSG_COOP_ACTION:
            monster_hp    = data.get("monster_hp", self.monster.hp)
            is_victory    = data.get("is_victory", False)
            is_game_over  = data.get("is_game_over", False)
            ally_hp       = data.get("ally_hp", None)
            ally_max_hp   = data.get("ally_max_hp", None)
            # Update displayed ally HP
            if ally_hp is not None and self.coop_ally:
                self.coop_ally["hp"]     = ally_hp
                self.coop_ally["max_hp"] = ally_max_hp or self.coop_ally.get("max_hp", 100)

            if is_victory:
                # Ally killed the monster — victory on our side too
                self.monster.hp = 0
                self._victory(from_ally=True)   # don't echo back
            elif is_game_over:
                # Ally was defeated — they'll show game over; we continue solo
                ally_name = self.coop_ally.get("name", "Ally")
                self.add_log(f"✦ {ally_name} has fallen! You fight on alone...")
                self.coop_mode = None
                self.coop_ally = {}
                if self.state == "ally_turn":
                    self.state = "player_turn"
            else:
                # Normal action — sync HP, take our turn
                self.monster.hp = max(0.0, min(monster_hp, self.monster.max_hp))
                if self.state == "ally_turn":
                    self.state = "player_turn"

        elif mtype == MSG_BATTLE_END:
            if not self.coop_ally:
                return  # not in co-op — peer finished their own solo fight; ignore
            outcome = data.get("outcome", "")
            ally_name = self.coop_ally.get("name", "Ally")
            if outcome == "fled":
                self.add_log(f"✦ {ally_name} fled the battle!")
            else:
                self.add_log(f"✦ {ally_name} left the battle.")
            # Disconnect from co-op, continue solo
            self.coop_mode = None
            self.coop_ally = {}
            if self.state == "ally_turn":
                self.state = "player_turn"

    def _end_combat(self):
        # Show post-boss dialogue
        if hasattr(self.game, 'pending_boss_dialogue') and self.game.pending_boss_dialogue:
            self.game.post_battle_dialogue = self.game.pending_boss_dialogue
            self.game.pending_boss_dialogue = None
        if hasattr(self.game, 'pending_subclass') and self.game.pending_subclass:
            self.game.pending_subclass = False
            self.game.set_screen("subclass")
            return
        self.game.set_screen("exploration")

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        for btn in self.main_btns.values():
            btn.update(mp)
        self.animation_timer += dt

        # ── Co-op inbox ───────────────────────────────────────────────────────
        if self.game.mp_coop_inbox:
            for mtype, data in list(self.game.mp_coop_inbox):
                self._handle_coop_msg(mtype, data)
            self.game.mp_coop_inbox.clear()

        # If ally disconnected while we're waiting on them, resume solo
        if (self.coop_mode and self.state == "ally_turn"
                and self.game.mp_peer
                and not self.game.mp_peer.connected):
            ally_name = self.coop_ally.get("name", "Ally")
            self.add_log(f"✦ {ally_name} disconnected. Continuing solo...")
            self.coop_mode = None
            self.coop_ally = {}
            self.state = "player_turn"

    def draw(self, surf):
        surf.fill((10, 10, 20))
        p = self.game.player

        # Battle background (gradient strip)
        for i in range(SCREEN_H // 2):
            alpha = int(30 + i * 0.15)
            pygame.draw.line(surf, (alpha, alpha//2, alpha//3), (0, i), (SCREEN_W, i))

        # Monster
        mx, my = SCREEN_W * 3 // 4, SCREEN_H // 3
        self._draw_combatant(surf, mx, my, self.monster.color, self.monster.name,
                             self.monster.hp, self.monster.max_hp,
                             self.monster.hp / self.monster.max_hp, enemy=True,
                             sprite_id=self.monster.monster_id,
                             variant=self.monster.variant)

        # Player (shift left in co-op to make room for ally sprite)
        has_ally = bool(self.coop_ally)
        px_off = -55 if has_ally else 0
        px, py = SCREEN_W // 4 + px_off, SCREEN_H * 2 // 3 - 30
        self._draw_combatant(surf, px, py, CLASSES[p.base_class]["color"], p.name,
                             p.hp, p.max_hp, p.hp / p.max_hp, enemy=False,
                             mp=p.mp, max_mp=p.max_mp,
                             sprite_id=p.char_class)

        # Co-op ally sprite (beside player)
        if has_ally:
            self._draw_coop_ally(surf, SCREEN_W // 4 + 70, SCREEN_H * 2 // 3 - 30)

        # Pet — shown as its own combatant with sprite, name tag, HP bar
        if p.active_pet and p.active_pet.is_alive():
            pet = p.active_pet
            ppx = SCREEN_W // 4 + (160 if has_ally else 140)
            ppy = SCREEN_H * 2 // 3 - 20
            col = tuple(min(255, c) for c in pet.color[:3])
            pet_size = 56
            pet_half = pet_size // 2
            # Sprite
            draw_monster_sprite(surf, pet.monster_id, col, ppx, ppy, pet_size,
                                pygame.time.get_ticks())
            # Name tag
            fnt   = get_font(11)
            ntxt  = fnt.render(pet.name[:10], True, col)
            nx    = ppx - ntxt.get_width() // 2
            ny    = ppy - pet_half - 18
            pygame.draw.rect(surf, (18, 14, 28),
                             (nx - 4, ny - 2, ntxt.get_width() + 8, ntxt.get_height() + 4),
                             border_radius=3)
            pygame.draw.rect(surf, col,
                             (nx - 4, ny - 2, ntxt.get_width() + 8, ntxt.get_height() + 4),
                             1, border_radius=3)
            surf.blit(ntxt, (nx, ny))
            # HP bar
            draw_bar(surf, ppx - pet_half, ppy + pet_half + 4, pet_size, 8,
                     pet.hp, pet.max_hp, HP_COL)

        # Battle log — sits above the action buttons with plenty of room
        log_rect = pygame.Rect(10, SCREEN_H - 200, SCREEN_W - 20, 130)
        draw_panel(surf, log_rect)
        _lfnt    = get_font(13)
        _line_h  = 22
        _max_vis = log_rect.height // _line_h          # rows the panel can show
        _max_w   = log_rect.width - 20
        # Expand every log message to pixel-wrapped visual lines
        _vis_lines: list = []
        for _msg in self.log:
            _vis_lines.extend(wrap_text(_msg, _lfnt, _max_w))
        _start = max(0, len(_vis_lines) - _max_vis)
        for _i, _wline in enumerate(_vis_lines[_start:]):
            draw_text(surf, _wline, 16, log_rect.y + 6 + _i * _line_h, WHITE, size=13)

        # Action buttons / submenu
        if self.submenu == "skills" and self.skill_list:
            draw_panel(surf, pygame.Rect(90, 190, SCREEN_W - 180, 320))
            draw_text_centered(surf, "Choose a Skill (ESC to cancel)", 195, GOLD, size=15)
            self.skill_list.draw(surf)
        elif self.submenu == "items" and self.item_list:
            draw_panel(surf, pygame.Rect(90, 190, SCREEN_W - 180, 320))
            draw_text_centered(surf, "Choose an Item (ESC to cancel)", 195, GOLD, size=15)
            self.item_list.draw(surf)
        else:
            # Dim buttons when it's the ally's turn
            for btn in self.main_btns.values():
                btn.enabled = btn.enabled  # keep enabled state
                btn.draw(surf)

            # "Waiting for ally" overlay when it's not our turn
            if self.state == "ally_turn" and self.coop_ally:
                ally_name = self.coop_ally.get("name", "Ally")
                tick = pygame.time.get_ticks()
                if (tick // 500) % 2 == 0:
                    draw_text_centered(surf, f"⌛  {ally_name}'s turn...",
                                       SCREEN_H - 75, (0, 220, 180), size=16)

        # Monster stats in corner
        draw_text(surf, f"Lv{self.monster.level} | {self.monster.element.upper()}",
                  SCREEN_W - 200, 10, UI_DIM, size=12)

        # Player stats
        draw_text(surf, f"ATK:{int(p.atk)} DEF:{int(p.defense)} SPD:{int(p.spd)} INT:{int(p.intelligence)}",
                  10, 10, UI_DIM, size=12)

        # Status effects
        sx = 10
        for effect in p.status_effects:
            col = (200,80,80) if effect in ("poison","burn","bleed") else LIGHT_GRAY
            draw_text(surf, effect[:6].upper(), sx, 26, col, size=11)
            sx += 55

        if self.state == "loot":
            self._draw_loot(surf)
        elif self.state == "game_over":
            self._draw_game_over(surf)

    def _draw_combatant(self, surf, cx, cy, color, name, hp, max_hp, ratio, enemy,
                        mp=None, max_mp=None, sprite_id=None, variant=None):
        tick = pygame.time.get_ticks()
        size = 80 if not enemy else (120 if self.is_boss else 100)
        half = size // 2

        # Variant aura ring (drawn behind the sprite)
        if variant == "alpha":
            ar = half + 3 + int(2 * math.sin(tick * 0.003))
            pygame.draw.circle(surf, DARK_RED, (cx, cy), ar + 6, 7)
            pygame.draw.circle(surf, RED,      (cx, cy), ar,     3)
        elif variant == "evolved":
            ar = half + 2 + int(2 * math.sin(tick * 0.004))
            pygame.draw.circle(surf, (50, 0, 70), (cx, cy), ar + 6, 7)
            pygame.draw.circle(surf, PURPLE,      (cx, cy), ar,     3)

        # Sprite or fallback rectangle
        if sprite_id:
            if enemy:
                draw_monster_sprite(surf, sprite_id, color, cx, cy, size, tick)
            else:
                draw_player_sprite(surf, sprite_id, cx, cy, size, tick)
        else:
            pygame.draw.rect(surf, tuple(max(20, c - 20) for c in color),
                             (cx - half, cy - half, size, size), border_radius=8)
            pygame.draw.rect(surf, color,
                             (cx - half, cy - half, size, size), 3, border_radius=8)
            pygame.draw.circle(surf, WHITE, (cx, cy - size // 5), size // 6)

        # Name tag with dark panel backing
        name_col = RED if enemy else GOLD
        fnt  = get_font(13)
        ntxt = fnt.render(name, True, name_col)
        nx   = cx - ntxt.get_width() // 2
        ny   = cy - half - 30
        pygame.draw.rect(surf, (18, 14, 28),
                         (nx - 5, ny - 3, ntxt.get_width() + 10, ntxt.get_height() + 6),
                         border_radius=4)
        pygame.draw.rect(surf, name_col,
                         (nx - 5, ny - 3, ntxt.get_width() + 10, ntxt.get_height() + 6),
                         1, border_radius=4)
        surf.blit(ntxt, (nx, ny))

        # Bars
        bar_y = cy + half + 6
        draw_bar(surf, cx - half, bar_y, size, 13, hp, max_hp, HP_COL,
                 label=f"{int(hp)}/{int(max_hp)}")
        if mp is not None and max_mp is not None:
            draw_bar(surf, cx - half, bar_y + 17, size, 11, mp, max_mp, MP_COL)

    def _draw_coop_ally(self, surf, cx: int, cy: int):
        """Draw the co-op ally sprite beside the player."""
        ally  = self.coop_ally
        if not ally:
            return
        tick  = pygame.time.get_ticks()
        size  = 70
        half  = size // 2
        name  = ally.get("name", "Ally")
        lvl   = ally.get("level", 1)
        hp    = ally.get("hp", 100)
        maxhp = ally.get("max_hp", 100)
        cls   = ally.get("char_class", "warrior")

        # Glow ring (cyan / teal, pulses)
        ar = half + 4 + int(3 * math.sin(tick * 0.003))
        pygame.draw.circle(surf, (0, 160, 200), (cx, cy), ar + 5, 5)
        pygame.draw.circle(surf, (0, 220, 240), (cx, cy), ar,     2)

        # Sprite
        draw_player_sprite(surf, cls, cx, cy, size, tick)

        # Name / level tag
        fnt   = get_font(12)
        label = f"{name}  Lv{lvl}"
        ntxt  = fnt.render(label, True, (0, 220, 200))
        nx    = cx - ntxt.get_width() // 2
        ny    = cy - half - 26
        pygame.draw.rect(surf, (10, 20, 30),
                         (nx - 4, ny - 2, ntxt.get_width() + 8, ntxt.get_height() + 4),
                         border_radius=3)
        pygame.draw.rect(surf, (0, 180, 180),
                         (nx - 4, ny - 2, ntxt.get_width() + 8, ntxt.get_height() + 4),
                         1, border_radius=3)
        surf.blit(ntxt, (nx, ny))

        # HP bar
        bar_w = size + 10
        draw_bar(surf, cx - bar_w // 2, cy + half + 6, bar_w, 11,
                 max(0, hp), max(1, maxhp), HP_COL,
                 label=f"{int(hp)}/{int(maxhp)}")

    def _draw_loot(self, surf):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        panel = pygame.Rect(100, 80, SCREEN_W - 200, SCREEN_H - 160)
        draw_panel(surf, panel, border_col=GOLD)

        if self.exp_gained > 0:
            draw_text_centered(surf, "Victory!", 100, GOLD, size=30)
            draw_text_centered(surf, f"EXP +{self.exp_gained}   Gold +{self.gold_gained}", 140, YELLOW, size=18)
        else:
            draw_text_centered(surf, "Battle Over", 100, LIGHT_GRAY, size=24)

        # Level-up messages
        y = 175
        for msg in self.level_up_msgs:
            draw_text_centered(surf, msg, y, GREEN, size=16)
            y += 24

        # Loot
        if self.loot_items:
            draw_text_centered(surf, "Items Obtained:", y + 10, WHITE, size=16)
            y += 35
            for item_id, qty, rarity in self.loot_items:
                item = ITEMS.get(item_id, {})
                col = RARITY_COLORS.get(rarity, WHITE)
                label = f"{item.get('name','?')} x{qty}"
                draw_text_centered(surf, label, y, col, size=14)
                draw_rarity_badge(surf, rarity, SCREEN_W // 2 + 100, y - 2)
                y += 22

        draw_text_centered(surf, "Tap / Press any key to continue", SCREEN_H - 100, UI_DIM, size=14)

    def _draw_game_over(self, surf):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))
        draw_text_centered(surf, "GAME OVER", SCREEN_H // 2 - 40, RED, size=42, shadow=True)
        draw_text_centered(surf, "Press any key to return to menu", SCREEN_H // 2 + 40, WHITE, size=18)


# ═════════════════════════════════════════════════════════════════════════════
# SUBCLASS SELECTION
# ═════════════════════════════════════════════════════════════════════════════
class SubclassScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        p = game.player
        self.subclasses = CLASSES[p.base_class]["subclasses"]
        self.selected = None
        self.buttons = {}
        bw, bh = SCREEN_W - 200, 110
        for i, sc in enumerate(self.subclasses):
            self.buttons[sc] = Button(
                pygame.Rect(100, 160 + i * (bh + 15), bw, bh),
                CLASSES[sc]["name"],
                color=tuple(max(20, c - 40) for c in CLASSES[sc]["color"])
            )
        self.btn_confirm = Button(pygame.Rect(SCREEN_W//2 - 120, SCREEN_H - 80, 240, 48),
                                  "Confirm Subclass", DARK_GREEN)

    def handle_event(self, event):
        for sc, btn in self.buttons.items():
            if btn.is_clicked(event):
                self.selected = sc
        if self.btn_confirm.is_clicked(event) and self.selected:
            self.game.player.choose_subclass(self.selected)
            self.game.set_screen("exploration")

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_confirm.update(mp)
        for btn in self.buttons.values(): btn.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        p = self.game.player
        draw_text_centered(surf, f"Level {SUBCLASS_UNLOCK_LEVEL}!", 50, GOLD, size=28)
        draw_text_centered(surf, f"Choose your Subclass, {p.name}!", 90, WHITE, size=20)

        for sc, btn in self.buttons.items():
            if sc == self.selected:
                btn.color = CLASSES[sc]["color"]
            else:
                btn.color = tuple(max(20, c - 40) for c in CLASSES[sc]["color"])
            btn.draw(surf)
            cls = CLASSES[sc]
            bx, by = btn.rect.x + 12, btn.rect.y + 35
            draw_text(surf, cls["desc"][:55], bx, by, UI_DIM, size=13)
            bonus_str = "  ".join(f"{k}+{v}" for k, v in cls.get("bonus",{}).items())
            draw_text(surf, bonus_str, bx, by + 20, YELLOW, size=13)

        self.btn_confirm.draw(surf)


# ═════════════════════════════════════════════════════════════════════════════
# INVENTORY
# ═════════════════════════════════════════════════════════════════════════════
class InventoryScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.tab = "items"   # items | equipment
        self.selected_item = None
        self.msg = ""
        self._build_list()
        self.btn_back   = Button(pygame.Rect(10, SCREEN_H - 50, 100, 40), "← Back")
        self.btn_equip  = Button(pygame.Rect(SCREEN_W - 220, SCREEN_H - 50, 100, 40), "Equip/Use", DARK_GREEN)
        self.btn_drop   = Button(pygame.Rect(SCREEN_W - 110, SCREEN_H - 50, 100, 40), "Drop", DARK_RED)
        self.tab_items  = Button(pygame.Rect(200, 10, 120, 36), "Items")
        self.tab_equip  = Button(pygame.Rect(330, 10, 140, 36), "Equipment")

    def _build_list(self):
        p = self.game.player
        items = []
        for entry in p.inventory:
            item = ITEMS.get(entry["id"], {})
            rarity = entry.get("rarity","common")
            col = RARITY_COLORS.get(rarity, WHITE)
            label = f"{item.get('name','?')} x{entry['qty']}  [{rarity.upper()}]"
            items.append((label, entry["id"], col))
        self.inv_list = ScrollList(pygame.Rect(10, 60, SCREEN_W - 320, SCREEN_H - 130), items, item_h=38)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            self.game.set_screen("exploration")
            return
        if self.tab_items.is_clicked(event): self.tab = "items"; self._build_list()
        if self.tab_equip.is_clicked(event): self.tab = "equipment"

        if self.tab == "items":
            idx = self.inv_list.handle_event(event)
            if idx >= 0 and idx < len(self.game.player.inventory):
                self.selected_item = self.game.player.inventory[idx]["id"]

            if self.btn_equip.is_clicked(event) and self.selected_item:
                p = self.game.player
                item = ITEMS.get(self.selected_item, {})
                if item.get("type") == "consumable":
                    msgs = p.use_consumable(self.selected_item)
                    self.msg = " | ".join(msgs)
                else:
                    ok, msg = p.equip_item(self.selected_item)
                    self.msg = msg
                self._build_list()
            if self.btn_drop.is_clicked(event) and self.selected_item:
                self.game.player.remove_item(self.selected_item)
                self.selected_item = None
                self._build_list()

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        for btn in (self.btn_back, self.btn_equip, self.btn_drop, self.tab_items, self.tab_equip):
            btn.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        p = self.game.player
        draw_text_centered(surf, "Inventory", 14, GOLD, size=22)
        self.tab_items.draw(surf); self.tab_equip.draw(surf)

        if self.tab == "items":
            self.inv_list.draw(surf)
            # Item detail panel
            if self.selected_item:
                self._draw_item_detail(surf, self.selected_item)
        elif self.tab == "equipment":
            self._draw_equipment(surf, p)

        if self.msg:
            draw_text_centered(surf, self.msg, SCREEN_H - 70, YELLOW, size=13)

        self.btn_back.draw(surf); self.btn_equip.draw(surf); self.btn_drop.draw(surf)
        draw_text(surf, f"Gold: {p.gold}", SCREEN_W - 200, SCREEN_H - 44, GOLD, size=15)

    def _draw_item_detail(self, surf, item_id: str):
        item = ITEMS.get(item_id, {})
        panel = pygame.Rect(SCREEN_W - 305, 60, 295, SCREEN_H - 130)
        draw_panel(surf, panel)
        x, y = panel.x + 8, panel.y + 8
        draw_text(surf, item.get("name","?"), x, y, WHITE, size=16); y += 24
        draw_rarity_badge(surf, item.get("rarity","common"), x, y); y += 22
        draw_text(surf, item.get("desc",""), x, y, UI_DIM, size=12); y += 36
        for stat, val in item.get("stats", {}).items():
            col = GREEN if val > 0 else RED
            draw_text(surf, f"{stat.upper()}: {'+' if val>0 else ''}{val}", x, y, col, size=13); y += 18
        eff = item.get("effect", {})
        for k, v in eff.items():
            draw_text(surf, f"{k}: {v}", x, y, CYAN, size=12); y += 16
        buy = item.get("buy", 0)
        sell = int(buy * SELL_MULT)
        draw_text(surf, f"Buy: {buy}g  Sell: {sell}g", x, y + 8, GOLD, size=13)

    def _draw_equipment(self, surf, p):
        slots_display = [
            ("weapon",      "Weapon",   10,  100),
            ("armor_head",  "Head",     10,  180),
            ("armor_chest", "Chest",    10,  260),
            ("armor_legs",  "Legs",     10,  340),
            ("armor_hands", "Hands",    10,  420),
            ("armor_feet",  "Feet",     10,  500),
            ("ring1",       "Ring 1",   450, 100),
            ("ring2",       "Ring 2",   450, 180),
            ("amulet",      "Amulet",   450, 260),
            ("belt",        "Belt",     450, 340),
        ]
        for slot, label, x, y in slots_display:
            item_id = p.equipment.get(slot)
            if item_id:
                item = ITEMS.get(item_id, {})
                name = item.get("name","?")
                rarity = "uncommon"   # placeholder
                col = RARITY_COLORS.get(rarity, WHITE)
            else:
                name = "(empty)"
                col = UI_DIM
            draw_text(surf, f"{label}: {name}", x, y, col, size=14)
        # Stat totals
        sx = SCREEN_W//2 - 100
        draw_panel(surf, pygame.Rect(sx, 90, 200, 280))
        draw_text(surf, "Stats", sx + 10, 100, GOLD, size=16)
        for i, (stat, val) in enumerate([
            ("HP", f"{p.hp}/{p.max_hp}"), ("MP", f"{p.mp}/{p.max_mp}"),
            ("ATK", int(p.atk)), ("DEF", int(p.defense)),
            ("SPD", int(p.spd)), ("INT", int(p.intelligence)),
            ("LCK", int(p.luck)),
        ]):
            draw_text(surf, f"{stat}: {val}", sx + 10, 125 + i * 26, WHITE, size=14)


# ═════════════════════════════════════════════════════════════════════════════
# SKILLS SCREEN
# ═════════════════════════════════════════════════════════════════════════════
class SkillsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self._build()
        self.btn_back = Button(pygame.Rect(10, SCREEN_H - 50, 100, 40), "← Back")
        self.selected = -1

    def _build(self):
        p = self.game.player
        items = []
        for sk_id in p.known_skills:
            sk = SKILLS.get(sk_id, {})
            col = CYAN if sk.get("type") == "active" else LIGHT_GRAY
            if sk.get("source") == "found":
                col = GOLD
            label = f"{sk.get('name','?')}  [{sk.get('type','').upper()}]  MP:{sk.get('mp_cost',0)}"
            items.append((label, sk_id, col))
        self.lst = ScrollList(pygame.Rect(10, 60, SCREEN_W - 320, SCREEN_H - 120), items, item_h=38)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            self.game.set_screen("exploration")
        idx = self.lst.handle_event(event)
        if idx >= 0:
            self.selected = idx

    def update(self, dt):
        self.btn_back.update(pygame.mouse.get_pos())

    def draw(self, surf):
        surf.fill(UI_BG)
        draw_text_centered(surf, "Skills", 14, GOLD, size=24)
        self.lst.draw(surf)
        if self.selected >= 0 and self.selected < len(self.game.player.known_skills):
            sk_id = self.game.player.known_skills[self.selected]
            self._draw_detail(surf, sk_id)
        self.btn_back.draw(surf)

    def _draw_detail(self, surf, sk_id: str):
        sk = SKILLS.get(sk_id, {})
        panel = pygame.Rect(SCREEN_W - 310, 60, 300, 340)
        draw_panel(surf, panel)
        x, y = panel.x + 10, panel.y + 10
        draw_text(surf, sk.get("name","?"), x, y, sk.get("color", WHITE), size=17); y += 28
        ty = sk.get("type","").upper()
        src = sk.get("source","level").upper()
        col = GOLD if src == "FOUND" else CYAN
        draw_text(surf, f"[{ty}]  [{src}]", x, y, col, size=13); y += 22
        draw_text(surf, sk.get("desc",""), x, y, UI_DIM, size=12); y += 40
        if sk.get("mp_cost",0) > 0:
            draw_text(surf, f"MP Cost: {sk['mp_cost']}", x, y, MP_COL, size=13); y += 20
        if sk.get("power"):
            draw_text(surf, f"Power: {int(sk['power']*100)}%", x, y, YELLOW, size=13); y += 20
        if sk.get("dmg_type"):
            draw_text(surf, f"Element: {sk['dmg_type'].title()}", x, y, CYAN, size=13); y += 20
        if sk.get("status"):
            draw_text(surf, f"Status: {sk['status']}", x, y, PINK, size=12); y += 18


# ═════════════════════════════════════════════════════════════════════════════
# PET MENU
# ═════════════════════════════════════════════════════════════════════════════
class PetMenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.btn_back = Button(pygame.Rect(10, SCREEN_H - 50, 100, 40), "← Back")
        self.btn_switch = Button(pygame.Rect(120, SCREEN_H - 50, 130, 40), "Switch Pet", DARK_BLUE)
        self._build()
        self.selected = -1

    def _build(self):
        p = self.game.player
        items = []
        if p.active_pet:
            pet = p.active_pet
            col = tuple(min(255, c) for c in pet.color[:3])
            items.append((f"[ACTIVE] {pet.name} Lv{pet.level} Evo{pet.evo_stage}", "active", col))
        for i, pet in enumerate(p.stored_pets):
            col = tuple(min(255, c) for c in pet.color[:3])
            items.append((f"{pet.name} Lv{pet.level} Evo{pet.evo_stage}", i, col))
        self.lst = ScrollList(pygame.Rect(10, 60, SCREEN_W//2 - 20, SCREEN_H - 130), items, item_h=42)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            self.game.set_screen("exploration")
        idx = self.lst.handle_event(event)
        if idx >= 0: self.selected = idx
        if self.btn_switch.is_clicked(event) and self.selected >= 0:
            self._switch_pet(self.selected)

    def _switch_pet(self, idx: int):
        p = self.game.player
        items = self.lst.items
        if idx >= len(items): return
        val = items[idx][1]
        if val == "active": return
        if p.active_pet:
            p.stored_pets.append(p.active_pet)
        p.active_pet = p.stored_pets.pop(val)
        self._build()

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp); self.btn_switch.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        p = self.game.player
        draw_text_centered(surf, "Pet Menu", 14, GOLD, size=24)
        self.lst.draw(surf)

        # Detail panel for active pet
        if p.active_pet:
            self._draw_pet_detail(surf, p.active_pet, SCREEN_W//2 + 10, 60)

        self.btn_back.draw(surf); self.btn_switch.draw(surf)

    def _draw_pet_detail(self, surf, pet, px: int, py: int):
        panel = pygame.Rect(px, py, SCREEN_W//2 - 20, SCREEN_H - 130)
        draw_panel(surf, panel)
        col = tuple(min(255, c) for c in pet.color[:3])
        x, y = panel.x + 10, panel.y + 10
        draw_text(surf, pet.name, x, y, col, size=20); y += 28
        draw_text(surf, f"Level: {pet.level} / {MAX_PET_LEVEL}   Evo: {pet.evo_stage}", x, y, WHITE, size=14); y += 22
        draw_bar(surf, x, y, 200, 14, pet.exp, pet.exp_needed(), EXP_COL, label=f"EXP"); y += 20
        draw_text(surf, f"Element: {pet.element.title()}", x, y, CYAN, size=13); y += 20
        draw_bar(surf, x, y, 200, 14, pet.hp, pet.max_hp, HP_COL, label=f"HP {pet.hp}/{pet.max_hp}"); y += 22
        for stat, val in [("ATK", pet.atk), ("DEF", pet.defense), ("SPD", pet.spd)]:
            draw_text(surf, f"{stat}: {val}", x, y, LIGHT_GRAY, size=13); y += 18
        y += 10
        draw_text(surf, "Abilities:", x, y, GOLD, size=14); y += 22
        for ab in pet.abilities:
            draw_text(surf, f"• {ab.replace('_',' ').title()}", x, y, WHITE, size=12); y += 16
        if pet.evolve_name:
            evo_lvl = int(MAX_PET_LEVEL * 0.5) if pet.evo_stage == 0 else int(MAX_PET_LEVEL * 0.85)
            draw_text(surf, f"Evolves at Lv{evo_lvl}", x, y + 10, PURPLE, size=13)


# ═════════════════════════════════════════════════════════════════════════════
# VILLAGE
# ═════════════════════════════════════════════════════════════════════════════
class VillageScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        p = game.player
        biome = BIOMES[p.position_biome]
        self.village = biome["village"]
        self.msg = ""
        cx = SCREEN_W // 2
        bw, bh = 280, 52
        bx = cx - bw // 2
        self.buttons = {
            "inn":     Button(pygame.Rect(bx, 200, bw, bh), "🏨 Inn (Rest & Save)",  DARK_BLUE),
            "shop":    Button(pygame.Rect(bx, 265, bw, bh), "🛒 Shop",               DARK_GREEN),
            "smith":   Button(pygame.Rect(bx, 330, bw, bh), "⚒ Blacksmith",          (80,60,40)),
            "stable":  Button(pygame.Rect(bx, 395, bw, bh), "♦ Pet Stable",          PURPLE),
            "travel":  Button(pygame.Rect(bx, 460, bw, bh), "✈ Fast Travel",         (40,80,100)),
            "leave":   Button(pygame.Rect(bx, 540, bw, bh), "← Leave Village",       MID_GRAY),
        }

    def handle_event(self, event):
        if self.buttons["inn"].is_clicked(event):
            p = self.game.player
            p.hp = p.max_hp; p.mp = p.max_mp
            p.status_effects.clear()
            from systems.save_load import auto_save
            auto_save(p)
            self.msg = "Rested fully. Game auto-saved!"
        if self.buttons["shop"].is_clicked(event):
            self.game.set_screen("shop")
        if self.buttons["smith"].is_clicked(event):
            self.game.set_screen("blacksmith")
        if self.buttons["stable"].is_clicked(event):
            self.game.set_screen("pet_menu")
        if self.buttons["travel"].is_clicked(event):
            self.game.set_screen("fast_travel")
        if self.buttons["leave"].is_clicked(event):
            self.game.set_screen("exploration")

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        for btn in self.buttons.values(): btn.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        p = self.game.player
        draw_text_centered(surf, self.village["name"], 60, GOLD, size=30)
        draw_text_centered(surf, BIOMES[p.position_biome]["name"], 95, UI_DIM, size=16)
        # HP/MP bars
        draw_bar(surf, 20, 140, 220, 16, p.hp, p.max_hp, HP_COL, label=f"HP {p.hp}/{p.max_hp}")
        draw_bar(surf, 20, 162, 220, 16, p.mp, p.max_mp, MP_COL, label=f"MP {p.mp}/{p.max_mp}")
        draw_text(surf, f"Gold: {p.gold}g", 260, 145, GOLD, size=15)
        for btn in self.buttons.values(): btn.draw(surf)
        if self.msg:
            draw_text_centered(surf, self.msg, SCREEN_H - 40, YELLOW, size=14)


# ═════════════════════════════════════════════════════════════════════════════
# SHOP
# ═════════════════════════════════════════════════════════════════════════════
class ShopScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        p = game.player
        self.biome = BIOMES[p.position_biome]
        self.shop_items = self.biome["village"]["shop_items"]
        self.tab = "buy"
        self.msg = ""
        self.selected_buy = -1
        self.selected_sell = -1
        self._build()
        self.btn_back = Button(pygame.Rect(10, SCREEN_H - 50, 100, 40), "← Back")
        self.btn_buy  = Button(pygame.Rect(SCREEN_W - 220, SCREEN_H - 50, 100, 40), "Buy", DARK_GREEN)
        self.btn_sell = Button(pygame.Rect(SCREEN_W - 110, SCREEN_H - 50, 100, 40), "Sell", DARK_RED)
        self.tab_buy  = Button(pygame.Rect(200, 10, 100, 36), "Buy")
        self.tab_sell = Button(pygame.Rect(310, 10, 100, 36), "Sell")

    def _build(self):
        p = self.game.player
        # Buy list
        buy_items = []
        for iid in self.shop_items:
            item = ITEMS.get(iid, {})
            price = item.get("buy", 0)
            col = WHITE if p.gold >= price else UI_DIM
            buy_items.append((f"{item.get('name','?')}  {price}g", iid, col))
        self.buy_list = ScrollList(pygame.Rect(10, 60, SCREEN_W//2 - 20, SCREEN_H - 130), buy_items, item_h=38)

        # Sell list
        from systems.loot import item_sell_price
        sell_items = []
        for entry in p.inventory:
            iid = entry["id"]
            item = ITEMS.get(iid, {})
            rarity = entry.get("rarity","common")
            price = item_sell_price(iid, rarity)
            col = RARITY_COLORS.get(rarity, WHITE)
            sell_items.append((f"{item.get('name','?')} x{entry['qty']}  → {price}g", iid, col))
        self.sell_list = ScrollList(pygame.Rect(SCREEN_W//2 + 10, 60, SCREEN_W//2 - 20, SCREEN_H - 130), sell_items, item_h=38)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            self.game.set_screen("village")
        if self.tab_buy.is_clicked(event): self.tab = "buy"
        if self.tab_sell.is_clicked(event): self.tab = "sell"

        idx = self.buy_list.handle_event(event)
        if idx >= 0: self.selected_buy = idx

        idx = self.sell_list.handle_event(event)
        if idx >= 0: self.selected_sell = idx

        if self.btn_buy.is_clicked(event) and self.selected_buy >= 0:
            self._do_buy()
        if self.btn_sell.is_clicked(event) and self.selected_sell >= 0:
            self._do_sell()

    def _do_buy(self):
        p = self.game.player
        if self.selected_buy >= len(self.shop_items): return
        iid = self.shop_items[self.selected_buy]
        item = ITEMS.get(iid, {})
        price = item.get("buy", 0)
        if p.gold < price:
            self.msg = "Not enough gold!"; return
        p.gold -= price
        p.add_item(iid, 1, "common")
        self.msg = f"Bought {item.get('name','?')}!"
        self._build()

    def _do_sell(self):
        from systems.loot import item_sell_price
        p = self.game.player
        if self.selected_sell >= len(p.inventory): return
        entry = p.inventory[self.selected_sell]
        price = item_sell_price(entry["id"], entry.get("rarity","common"))
        p.gold += price
        p.remove_item(entry["id"])
        self.msg = f"Sold for {price}g!"
        self._build()

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        for btn in (self.btn_back, self.btn_buy, self.btn_sell, self.tab_buy, self.tab_sell):
            btn.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        p = self.game.player
        draw_text_centered(surf, "Shop", 14, GOLD, size=24)
        draw_text(surf, f"Gold: {p.gold}g", SCREEN_W - 190, 16, GOLD, size=15)
        self.tab_buy.draw(surf); self.tab_sell.draw(surf)
        self.buy_list.draw(surf)
        self.sell_list.draw(surf)
        self.btn_back.draw(surf); self.btn_buy.draw(surf); self.btn_sell.draw(surf)
        if self.msg:
            draw_text_centered(surf, self.msg, SCREEN_H - 70, YELLOW, size=14)


# ═════════════════════════════════════════════════════════════════════════════
# BLACKSMITH
# ═════════════════════════════════════════════════════════════════════════════
class BlacksmithScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.msg = ""
        self.selected = -1
        self._build()
        self.btn_back    = Button(pygame.Rect(10, SCREEN_H - 50, 100, 40), "← Back")
        self.btn_upgrade = Button(pygame.Rect(SCREEN_W//2 - 80, SCREEN_H - 50, 160, 40),
                                  "Upgrade (500g)", (80, 60, 30))

    def _build(self):
        p = self.game.player
        items = []
        for slot, iid in p.equipment.items():
            if iid:
                item = ITEMS.get(iid, {})
                items.append((f"[{slot}] {item.get('name','?')}", slot, WHITE))
        self.lst = ScrollList(pygame.Rect(10, 60, SCREEN_W - 20, SCREEN_H - 130), items, item_h=40)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            self.game.set_screen("village")
        idx = self.lst.handle_event(event)
        if idx >= 0: self.selected = idx
        if self.btn_upgrade.is_clicked(event) and self.selected >= 0:
            self._upgrade()

    def _upgrade(self):
        p = self.game.player
        if p.gold < 500:
            self.msg = "Need 500 gold!"; return
        slot = self.lst.items[self.selected][1]
        iid = p.equipment.get(slot)
        if not iid: return
        item = ITEMS.get(iid, {})
        p.gold -= 500
        # Boost stats by 10%
        for stat in item.get("stats", {}):
            old = item["stats"][stat]
            item["stats"][stat] = int(old * 1.1) if old > 0 else old
        self.msg = f"Upgraded {item.get('name','?')}! (+10% all stats)"
        self._build()

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp); self.btn_upgrade.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        draw_text_centered(surf, "Blacksmith — Upgrade Equipment", 14, GOLD, size=22)
        draw_text_centered(surf, "Select equipped item to upgrade (+10% all stats, costs 500g)", 48, UI_DIM, size=13)
        self.lst.draw(surf)
        self.btn_back.draw(surf); self.btn_upgrade.draw(surf)
        if self.msg:
            draw_text_centered(surf, self.msg, SCREEN_H - 80, YELLOW, size=14)


# ═════════════════════════════════════════════════════════════════════════════
# FAST TRAVEL / WORLD MAP
# ═════════════════════════════════════════════════════════════════════════════
class WorldMapScreen(Screen):
    """Shown when player reaches map border OR via fast travel."""

    def __init__(self, game, fast_travel_mode: bool = False):
        super().__init__(game)
        self.fast_travel = fast_travel_mode
        self.hovered_biome = None
        self.selected_biome = None
        self.msg = ""
        self.btn_back = Button(pygame.Rect(10, SCREEN_H - 50, 100, 40), "← Back")
        self.btn_go   = Button(pygame.Rect(SCREEN_W//2 - 80, SCREEN_H - 50, 160, 44), "Travel Here", DARK_GREEN)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            self.game.set_screen("exploration")
            return
        if self.btn_go.is_clicked(event) and self.selected_biome:
            self._travel(self.selected_biome)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for bid, bdata in BIOMES.items():
                bx, by = bdata["position"]
                if math.hypot(event.pos[0] - bx, event.pos[1] - by) < 28:
                    self.selected_biome = bid
                    break
        if event.type == pygame.MOUSEMOTION:
            self.hovered_biome = None
            for bid, bdata in BIOMES.items():
                bx, by = bdata["position"]
                if math.hypot(event.pos[0] - bx, event.pos[1] - by) < 28:
                    self.hovered_biome = bid
                    break

    def _travel(self, biome_id: str):
        p = self.game.player
        if biome_id not in p.unlocked_biomes:
            self.msg = "That area is locked! Defeat the local boss first."
            return
        cost = FAST_TRAVEL_COST if self.fast_travel and biome_id != p.position_biome else 0
        if cost > 0 and p.gold < cost:
            self.msg = f"Fast travel costs {cost}g."
            return
        p.gold -= cost
        old = p.position_biome
        p.position_biome = biome_id
        if biome_id != old:
            tmap = self.game.world.get_map(biome_id)
            p.position_x, p.position_y = tmap.safe_entry_pos()
            p.discovered_biomes.add(biome_id)
            self.game.pending_area_intro = True
        self.game.set_screen("exploration")

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp); self.btn_go.update(mp)

    def draw(self, surf):
        surf.fill((15, 20, 40))
        draw_text_centered(surf, "World Map", 14, GOLD, size=26)
        p = self.game.player

        # Draw connections
        for bid, bdata in BIOMES.items():
            if bid not in p.discovered_biomes:
                continue
            bx, by = bdata["position"]
            for nbid in bdata["connections"]:
                if nbid in p.discovered_biomes:
                    nx, ny = BIOMES[nbid]["position"]
                    pygame.draw.line(surf, UI_BORDER, (bx, by), (nx, ny), 2)

        # Draw nodes
        for bid, bdata in BIOMES.items():
            bx, by = bdata["position"]
            if bid not in p.discovered_biomes:
                pygame.draw.circle(surf, MID_GRAY, (bx, by), 16)
                draw_text(surf, "???", bx - 12, by - 7, UI_DIM, size=11)
                continue

            unlocked = bid in p.unlocked_biomes
            border = GOLD if bid == p.position_biome else (GREEN if unlocked else RED)
            size = 22
            col = bdata["color"]
            pygame.draw.circle(surf, col, (bx, by), size)
            pygame.draw.circle(surf, border, (bx, by), size, 3)

            if bid == self.selected_biome or bid == self.hovered_biome:
                pygame.draw.circle(surf, WHITE, (bx, by), size + 4, 2)

            name = bdata["name"].replace(" ", "\n")
            draw_text(surf, bdata["name"][:10], bx - 30, by + size + 4, WHITE, size=10)

            if bid == p.position_biome:
                pygame.draw.circle(surf, WHITE, (bx, by), 6)

        # Legend
        draw_text(surf, "● You are here", 20, SCREEN_H - 100, WHITE, size=12)
        draw_text(surf, "● Unlocked  ● Locked (defeat boss)", 20, SCREEN_H - 80, LIGHT_GRAY, size=12)

        if self.selected_biome and self.selected_biome in p.discovered_biomes:
            bd = BIOMES[self.selected_biome]
            info = f"{bd['name']}  Lv{bd['level_range'][0]}-{bd['level_range'][1]}  |  {bd['desc']}"
            draw_text_centered(surf, info, SCREEN_H - 140, CYAN, size=13)
            if self.fast_travel and self.selected_biome != p.position_biome:
                draw_text_centered(surf, f"Fast travel cost: {FAST_TRAVEL_COST}g", SCREEN_H - 120, GOLD, size=13)

        self.btn_back.draw(surf)
        if self.selected_biome and self.selected_biome in p.unlocked_biomes:
            self.btn_go.draw(surf)

        if self.msg:
            draw_text_centered(surf, self.msg, SCREEN_H - 90, RED, size=13)


# ═════════════════════════════════════════════════════════════════════════════
# PAUSE MENU
# ═════════════════════════════════════════════════════════════════════════════
class PauseScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_W // 2
        bw, bh = 240, 46
        bx = cx - bw // 2

        # If already in MP, show disconnect button; otherwise show host/join
        in_mp = bool(game.mp_mode)
        self.btns = {
            "resume":   Button(pygame.Rect(bx, 220, bw, bh), "Resume",          DARK_GREEN),
            "save":     Button(pygame.Rect(bx, 273, bw, bh), "Save Game",       DARK_BLUE),
            "inv":      Button(pygame.Rect(bx, 326, bw, bh), "Inventory",       MID_GRAY),
            "world":    Button(pygame.Rect(bx, 379, bw, bh), "World Map",       MID_GRAY),
            "settings": Button(pygame.Rect(bx, 432, bw, bh), "Settings",        MID_GRAY),
            "mp":       Button(pygame.Rect(bx, 485, bw, bh),
                               "Disconnect MP" if in_mp else "Multiplayer",
                               DARK_RED if in_mp else (60, 100, 160)),
            "menu":     Button(pygame.Rect(bx, 538, bw, bh), "Main Menu",       DARK_RED),
        }
        self.msg = ""

    def handle_event(self, event):
        if self.btns["resume"].is_clicked(event):
            self.game.set_screen("exploration")
        if self.btns["save"].is_clicked(event):
            from systems.save_load import save_game
            save_game(self.game.player)
            if self.game.mp_mode == "guest":
                self.game.mp_request_save()
            self.msg = "Game saved!"
        if self.btns["inv"].is_clicked(event):
            self.game.set_screen("inventory")
        if self.btns["world"].is_clicked(event):
            self.game.set_screen("world_map")
        if self.btns["settings"].is_clicked(event):
            self.game._settings_return = "pause"
            self.game.set_screen("settings")
        if self.btns["mp"].is_clicked(event):
            if self.game.mp_mode:
                self.game.stop_multiplayer()
                self.msg = "Disconnected from multiplayer."
                # Refresh button label
                self.btns["mp"].text = "Multiplayer"
                self.btns["mp"].color = (60, 100, 160)
            else:
                # Ask host or join
                self.game.set_screen("mp_menu")
        if self.btns["menu"].is_clicked(event):
            self.game.stop_multiplayer()
            self.game.set_screen("main_menu")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.set_screen("exploration")

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        for btn in self.btns.values(): btn.update(mp)

    def draw(self, surf):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surf.blit(overlay, (0, 0))
        panel = pygame.Rect(SCREEN_W//2 - 160, 148, 320, 468)
        draw_panel(surf, panel, border_col=GOLD)
        draw_text_centered(surf, "PAUSED", 163, GOLD, size=28)
        p = self.game.player
        draw_text_centered(surf, f"{p.name}  Lv{p.level}  {CLASSES[p.char_class]['name']}", 198, LIGHT_GRAY, size=15)
        # MP status line inside panel
        if self.game.mp_mode:
            mode_str = "HOST" if self.game.mp_mode == "host" else "GUEST"
            draw_text_centered(surf, f"[MP {mode_str} active]", 207, (0, 220, 200), size=12)
        for btn in self.btns.values(): btn.draw(surf)
        if self.msg:
            draw_text_centered(surf, self.msg, panel.bottom + 10, YELLOW, size=14)


# ═════════════════════════════════════════════════════════════════════════════
# SETTINGS SCREEN
# ═════════════════════════════════════════════════════════════════════════════
class SettingsScreen(Screen):
    """Volume control and basic settings."""

    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_W // 2
        bw, bh = 200, 46
        # "Back" button
        self.btn_back = Button(pygame.Rect(cx - bw // 2, 520, bw, bh), "Back", DARK_BLUE)
        # Volume as integer 0-10 (each step = 10%)
        self._vol_steps = round(game.music._volume * 10)

    def _apply_volume(self):
        vol = self._vol_steps / 10.0
        self.game.music.set_volume(vol)
        from systems.save_load import save_settings
        save_settings(vol)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            dest = getattr(self.game, "_settings_return", "main_menu")
            self.game.set_screen(dest)
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,):
                dest = getattr(self.game, "_settings_return", "main_menu")
                self.game.set_screen(dest)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self._vol_steps < 10:
                    self._vol_steps += 1
                    self._apply_volume()
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self._vol_steps > 0:
                    self._vol_steps -= 1
                    self._apply_volume()

        # Mouse click on ◄ / ► arrows
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            cy = SCREEN_H // 2
            bar_w = 340
            bar_x = SCREEN_W // 2 - bar_w // 2
            arrow_size = 40
            # Left arrow rect
            lr = pygame.Rect(bar_x - arrow_size - 8, cy - arrow_size // 2, arrow_size, arrow_size)
            # Right arrow rect
            rr = pygame.Rect(bar_x + bar_w + 8, cy - arrow_size // 2, arrow_size, arrow_size)
            if lr.collidepoint(mx, my) and self._vol_steps > 0:
                self._vol_steps -= 1
                self._apply_volume()
            elif rr.collidepoint(mx, my) and self._vol_steps < 10:
                self._vol_steps += 1
                self._apply_volume()

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_back.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)

        # Title
        draw_text_centered(surf, "SETTINGS", 90, GOLD, size=32, shadow=True)

        # Panel
        panel = pygame.Rect(SCREEN_W // 2 - 230, 130, 460, 360)
        draw_panel(surf, panel)

        # ── Music Volume section ─────────────────────────────────────────────
        draw_text_centered(surf, "Music Volume", 160, LIGHT_GRAY, size=20)

        cy = SCREEN_H // 2 - 10
        bar_w = 340
        bar_h = 22
        bar_x = SCREEN_W // 2 - bar_w // 2
        arrow_size = 40

        # Arrow buttons
        pygame.draw.rect(surf, UI_PANEL, (bar_x - arrow_size - 8, cy - arrow_size // 2, arrow_size, arrow_size), border_radius=6)
        pygame.draw.rect(surf, UI_BORDER, (bar_x - arrow_size - 8, cy - arrow_size // 2, arrow_size, arrow_size), 2, border_radius=6)
        draw_text_centered(surf, "◄", cy - arrow_size // 2 + 8, LIGHT_GRAY, size=18,
                           x_offset=bar_x - arrow_size - 8 + arrow_size // 2 - SCREEN_W // 2)

        pygame.draw.rect(surf, UI_PANEL, (bar_x + bar_w + 8, cy - arrow_size // 2, arrow_size, arrow_size), border_radius=6)
        pygame.draw.rect(surf, UI_BORDER, (bar_x + bar_w + 8, cy - arrow_size // 2, arrow_size, arrow_size), 2, border_radius=6)
        draw_text_centered(surf, "►", cy - arrow_size // 2 + 8, LIGHT_GRAY, size=18,
                           x_offset=bar_x + bar_w + 8 + arrow_size // 2 - SCREEN_W // 2)

        # Background track
        pygame.draw.rect(surf, MID_GRAY, (bar_x, cy - bar_h // 2, bar_w, bar_h), border_radius=8)
        # Filled portion
        filled_w = int(bar_w * self._vol_steps / 10)
        if filled_w > 0:
            col = (50, 200, 100) if self._vol_steps >= 5 else (220, 160, 40) if self._vol_steps >= 2 else (200, 60, 60)
            pygame.draw.rect(surf, col, (bar_x, cy - bar_h // 2, filled_w, bar_h), border_radius=8)
        # Border
        pygame.draw.rect(surf, UI_BORDER, (bar_x, cy - bar_h // 2, bar_w, bar_h), 2, border_radius=8)

        # Volume percentage label
        pct = self._vol_steps * 10
        draw_text_centered(surf, f"{pct}%", cy + bar_h // 2 + 14, GOLD, size=22)

        # Segment tick marks
        for i in range(11):
            tx = bar_x + int(bar_w * i / 10)
            th = 8 if i % 5 == 0 else 4
            pygame.draw.line(surf, UI_BORDER, (tx, cy - bar_h // 2 - th), (tx, cy - bar_h // 2), 1)

        # Controls hint
        draw_text_centered(surf, "◄ ► Arrow Keys or click arrows to adjust", cy + bar_h // 2 + 50, UI_DIM, size=13)

        # ── Controls hint section ────────────────────────────────────────────
        draw_text_centered(surf, "Controls", 390, LIGHT_GRAY, size=17)
        draw_text_centered(surf, "Move: Arrow Keys / WASD    Pause: ESC    Interact: Space/Enter", 415, UI_DIM, size=13)
        draw_text_centered(surf, "Inventory: I    World Map: M    Skills: K    Pet Menu: P", 435, UI_DIM, size=13)

        self.btn_back.draw(surf)


# ═════════════════════════════════════════════════════════════════════════════
# MULTIPLAYER MENU  (Host / Join chooser)
# ═════════════════════════════════════════════════════════════════════════════
class MultiplayerMenuScreen(Screen):
    """Simple screen to choose Host Game or Join Game."""

    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_W // 2
        bw, bh = 260, 56
        self.btn_host   = Button(pygame.Rect(cx - bw // 2, 280, bw, bh), "Host Game",  (50, 120, 200))
        self.btn_join   = Button(pygame.Rect(cx - bw // 2, 350, bw, bh), "Join Game",  DARK_GREEN)
        self.btn_cancel = Button(pygame.Rect(cx - bw // 2, 440, bw, bh), "Back",       MID_GRAY)

    def handle_event(self, event):
        if self.btn_host.is_clicked(event):
            self.game.start_host()
        if self.btn_join.is_clicked(event):
            self.game.set_screen("join_lobby")
        if self.btn_cancel.is_clicked(event):
            self.game.set_screen("pause")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.set_screen("pause")

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_host.update(mp)
        self.btn_join.update(mp)
        self.btn_cancel.update(mp)

    def draw(self, surf):
        surf.fill(UI_BG)
        draw_text_centered(surf, "MULTIPLAYER", 130, GOLD, size=34, shadow=True)
        draw_text_centered(surf, "Co-op adventure — same WiFi or over the internet", 180, LIGHT_GRAY, size=15)
        draw_text_centered(surf, "Host: opens a server on your machine", 204, UI_DIM, size=13)
        draw_text_centered(surf, "Join: connect using your friend's IP address", 222, UI_DIM, size=13)
        self.btn_host.draw(surf)
        self.btn_join.draw(surf)
        self.btn_cancel.draw(surf)


# ═════════════════════════════════════════════════════════════════════════════
# HOST LOBBY SCREEN
# ═════════════════════════════════════════════════════════════════════════════
class HostLobbyScreen(Screen):
    """Shows the host's LAN + public IP and waits for a guest to connect."""

    def __init__(self, game):
        super().__init__(game)
        import threading
        from networking.protocol import get_local_ip, get_public_ip, PORT
        self._local_ip  = get_local_ip()
        self._public_ip = "fetching…"
        self._port      = PORT
        self._tick      = 0.0
        self._dot_frame = 0

        # Fetch public IP in background so we don't block the game loop
        threading.Thread(target=self._fetch_public_ip, daemon=True).start()

        cx = SCREEN_W // 2
        bw, bh = 220, 46
        self.btn_cancel = Button(pygame.Rect(cx - bw // 2, 560, bw, bh), "Cancel", DARK_RED)

    def _fetch_public_ip(self):
        from networking.protocol import get_public_ip
        ip = get_public_ip()
        self._public_ip = ip if ip else "unavailable"

    def handle_event(self, event):
        if self.btn_cancel.is_clicked(event):
            self.game.stop_multiplayer()
            self.game.set_screen("pause")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.stop_multiplayer()
            self.game.set_screen("pause")

    def update(self, dt):
        self._tick += dt
        self._dot_frame = int(self._tick * 2) % 4
        self.btn_cancel.update(pygame.mouse.get_pos())
        srv = self.game.mp_server
        if srv and srv.connected:
            self.game.set_screen("exploration")

    def draw(self, surf):
        surf.fill(UI_BG)
        cx = SCREEN_W // 2

        draw_text_centered(surf, "HOST GAME", 72, GOLD, size=32, shadow=True)

        panel = pygame.Rect(cx - 310, 112, 620, 430)
        draw_panel(surf, panel, border_col=(60, 160, 220))

        srv = self.game.mp_server

        # ── Server status ─────────────────────────────────────────────────────
        if srv and srv.error:
            draw_text_centered(surf, "✗ Server failed to start", 132, (220, 80, 60), size=16)
            draw_text_centered(surf, srv.error, 154, (200, 80, 60), size=12)
        elif srv and srv.listening:
            draw_text_centered(surf, f"✓  Server listening on port {self._port}", 132, (60, 220, 80), size=15)
        else:
            draw_text_centered(surf, "Starting server…", 132, YELLOW, size=15)

        # ── Same WiFi (LAN) ───────────────────────────────────────────────────
        draw_text_centered(surf, "Same WiFi / LAN  — give guest this IP:", 165, LIGHT_GRAY, size=14)
        draw_text_centered(surf, self._local_ip, 187, (0, 240, 200), size=28, shadow=True)

        # ── Different network (internet) ──────────────────────────────────────
        draw_text_centered(surf, "Different WiFi / Internet  — give guest this IP:", 228, LIGHT_GRAY, size=14)
        pub_col = YELLOW if self._public_ip not in ("fetching…", "unavailable") else UI_DIM
        draw_text_centered(surf, self._public_ip, 250, pub_col, size=28, shadow=True)

        draw_text_centered(surf, f"Port {self._port} must be forwarded on your router to this PC.",
                           288, UI_DIM, size=12)

        # ── Firewall note (most common failure cause) ─────────────────────────
        fw_y = 308
        pygame.draw.rect(surf, (60, 30, 20), pygame.Rect(cx - 295, fw_y - 4, 590, 56), border_radius=4)
        pygame.draw.rect(surf, (180, 80, 40), pygame.Rect(cx - 295, fw_y - 4, 590, 56), 1, border_radius=4)
        draw_text_centered(surf, "⚠  Guest can't connect? Windows Firewall is usually the cause.", fw_y + 2,
                           (240, 160, 80), size=12)
        draw_text_centered(surf, "Run as Admin  OR  go to Windows Firewall → Allow an app", fw_y + 18,
                           LIGHT_GRAY, size=12)
        draw_text_centered(surf, f"→ Add an Inbound Rule → TCP port {self._port} → Allow.", fw_y + 34,
                           LIGHT_GRAY, size=12)

        # ── Waiting indicator ─────────────────────────────────────────────────
        dots = "." * self._dot_frame
        draw_text_centered(surf, f"Waiting for guest{dots}", 380, YELLOW, size=17)
        r = 10
        for i in range(8):
            angle = self._tick * 3 + i * math.pi / 4
            ix = cx + int(math.cos(angle) * r * 2)
            iy = 408 + int(math.sin(angle) * r)
            alpha = int(60 + 195 * i / 8)
            pygame.draw.circle(surf, (alpha, alpha, alpha), (ix, iy), 3)

        draw_text_centered(surf, "Same network? Use the LAN IP.  Different network? Use the Internet IP.",
                           432, UI_DIM, size=12)

        self.btn_cancel.draw(surf)


# ═════════════════════════════════════════════════════════════════════════════
# JOIN LOBBY SCREEN
# ═════════════════════════════════════════════════════════════════════════════
class JoinLobbyScreen(Screen):
    """IP address input + Connect button for the guest."""

    def __init__(self, game):
        super().__init__(game)
        self._ip_text    = ""
        self._ip_active  = True
        self._status     = "Enter the host's IP and press Connect."
        self._status_col = UI_DIM
        self._connecting = False
        self._connect_result = None   # set by background thread: (ok, err)
        self._spin       = 0.0

        cx = SCREEN_W // 2
        self._ip_rect = pygame.Rect(cx - 180, 270, 360, 46)

        bw, bh = 220, 46
        self.btn_connect = Button(pygame.Rect(cx - bw // 2, 345, bw, bh), "Connect", (60, 160, 60))
        self.btn_cancel  = Button(pygame.Rect(cx - bw // 2, 405, bw, bh), "Cancel",  DARK_RED)

        # Show the soft keyboard immediately — field is active on entry
        pygame.key.start_text_input()

    def handle_event(self, event):
        # While connecting, only allow Cancel
        if self._connecting:
            if self.btn_cancel.is_clicked(event):
                self._connecting = False
                self._connect_result = None
                self._status     = "Cancelled."
                self._status_col = UI_DIM
            return

        # ── IP field focus ────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._ip_rect.collidepoint(event.pos):
                self._ip_active = True
                pygame.key.start_text_input()
            else:
                self._ip_active = False
                pygame.key.stop_text_input()
        elif event.type == pygame.FINGERDOWN:
            fx = int(event.x * SCREEN_W)
            fy = int(event.y * SCREEN_H)
            if self._ip_rect.collidepoint(fx, fy):
                self._ip_active = True
                pygame.key.start_text_input()

        # ── Text entry ────────────────────────────────────────────────────
        if self._ip_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self._ip_text = self._ip_text[:-1]
                elif event.key == pygame.K_RETURN:
                    self._try_connect()
            elif event.type == pygame.TEXTINPUT:
                for ch in event.text:
                    if ch.isprintable() and len(self._ip_text) < 45:
                        self._ip_text += ch

        if self.btn_connect.is_clicked(event):
            self._try_connect()
        if self.btn_cancel.is_clicked(event):
            pygame.key.stop_text_input()
            self.game.set_screen("pause")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.key.stop_text_input()
            self.game.set_screen("pause")

    def _try_connect(self):
        ip = self._ip_text.strip()
        if not ip:
            self._status     = "Enter an IP address first."
            self._status_col = (220, 80, 60)
            return
        self._connecting     = True
        self._connect_result = None
        self._status         = f"Connecting to {ip} …"
        self._status_col     = YELLOW

        # Run the blocking connect in a background thread so the game
        # loop keeps running (no freeze).
        import threading
        threading.Thread(target=self._connect_thread, args=(ip,),
                         daemon=True).start()

    def _connect_thread(self, ip: str):
        ok, err = self.game.start_client(ip)
        if not ok:
            err = self._friendly_error(err)
        self._connect_result = (ok, err)

    @staticmethod
    def _friendly_error(raw: str) -> str:
        """Translate raw socket errors into plain-English hints."""
        r = raw.lower()
        if "timed out" in r or "timeout" in r:
            return ("Timed out — check: (1) correct IP? "
                    "(2) port 55000 forwarded on host's router? "
                    "(3) host's Windows Firewall allows port 55000?")
        if "refused" in r or "actively refused" in r:
            return ("Connection refused — host's game may not be on Host screen, "
                    "or Windows Firewall is blocking port 55000.")
        if "no route" in r or "unreachable" in r or "network" in r:
            return "Cannot reach host — double-check the IP address."
        if "name or service" in r or "getaddrinfo" in r:
            return "Invalid IP address — check for typos."
        return raw

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.btn_connect.update(mp)
        self.btn_cancel.update(mp)

        if self._connecting:
            self._spin += dt

        # Pick up result from background thread
        if self._connecting and self._connect_result is not None:
            ok, err = self._connect_result
            self._connect_result = None
            self._connecting     = False
            if ok:
                self._status     = "Connected!"
                self._status_col = (60, 220, 80)
                self.game.sync_guest_to_host()   # teleport to host's biome
                self.game.set_screen("exploration")
            else:
                self._status     = f"Failed: {err}"
                self._status_col = (220, 80, 60)

    def draw(self, surf):
        surf.fill(UI_BG)
        cx = SCREEN_W // 2

        draw_text_centered(surf, "JOIN GAME", 90, GOLD, size=32, shadow=True)

        panel = pygame.Rect(cx - 280, 150, 560, 310)
        draw_panel(surf, panel, border_col=(60, 220, 140))

        draw_text_centered(surf, "Enter the host's IP address:", 180, LIGHT_GRAY, size=17)
        draw_text_centered(surf, "Same WiFi → use LAN IP.  Different network → use public IP.", 205, UI_DIM, size=13)

        # IP input box (greyed out while connecting)
        box_col = UI_DIM if self._connecting else (GOLD if self._ip_active else UI_BORDER)
        pygame.draw.rect(surf, UI_PANEL, self._ip_rect, border_radius=6)
        pygame.draw.rect(surf, box_col, self._ip_rect, 2, border_radius=6)
        cursor = "|" if (self._ip_active and not self._connecting
                         and pygame.time.get_ticks() % 900 < 450) else ""
        txt_col = UI_DIM if self._connecting else WHITE
        draw_text(surf, self._ip_text + cursor,
                  self._ip_rect.x + 10, self._ip_rect.y + 12,
                  txt_col, size=18)

        # Spinner while connecting
        if self._connecting:
            r = 8
            for i in range(8):
                angle = self._spin * 4 + i * math.pi / 4
                ix = cx + int(math.cos(angle) * r * 2)
                iy = 390 + int(math.sin(angle) * r)
                alpha = int(60 + 195 * i / 8)
                pygame.draw.circle(surf, (alpha, alpha, alpha), (ix, iy), 3)

        # Status — may be a long error message, so break at " — "
        if self._status:
            parts = self._status.split(" — ")
            for i, part in enumerate(parts):
                draw_text_centered(surf, part, 418 + i * 17, self._status_col, size=13)

        self.btn_connect.draw(surf)
        self.btn_cancel.draw(surf)

        draw_text_centered(surf, f"Port 55000  —  host must forward this port + allow it in Windows Firewall",
                           510, UI_DIM, size=12)
