"""Reusable UI drawing helpers."""
import pygame
from settings import *


def draw_panel(surf: pygame.Surface, rect: pygame.Rect, border_col=UI_BORDER, fill=UI_PANEL, radius=6):
    pygame.draw.rect(surf, fill, rect, border_radius=radius)
    pygame.draw.rect(surf, border_col, rect, 2, border_radius=radius)


def draw_bar(surf: pygame.Surface, x: int, y: int, w: int, h: int,
             current: float, maximum: float, color, bg=(40, 40, 40), label: str = ""):
    pygame.draw.rect(surf, bg, (x, y, w, h), border_radius=3)
    fill_w = int(w * max(0, current) / max(1, maximum))
    if fill_w > 0:
        pygame.draw.rect(surf, color, (x, y, fill_w, h), border_radius=3)
    pygame.draw.rect(surf, UI_BORDER, (x, y, w, h), 1, border_radius=3)
    if label:
        fnt = get_font(12)
        txt = fnt.render(label, True, WHITE)
        surf.blit(txt, (x + 4, y + (h - txt.get_height()) // 2))


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list:
    """Word-wrap *text* so every line fits within *max_width* pixels.
    Returns a list of line strings (at least one element)."""
    if not text:
        return [""]
    lines, current = [], ""
    for word in text.split(" "):
        candidate = (current + " " + word).strip()
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            # Force-break oversized single words character by character
            if font.size(word)[0] > max_width:
                chunk = ""
                for ch in word:
                    if font.size(chunk + ch)[0] <= max_width:
                        chunk += ch
                    else:
                        if chunk:
                            lines.append(chunk)
                        chunk = ch
                current = chunk
            else:
                current = word
    if current:
        lines.append(current)
    return lines or [""]


_font_cache: dict = {}
def get_font(size: int = 16) -> pygame.font.Font:
    if size not in _font_cache:
        try:
            _font_cache[size] = pygame.font.Font(None, size + 6)
        except Exception:
            _font_cache[size] = pygame.font.SysFont("monospace", size)
    return _font_cache[size]


def draw_text(surf: pygame.Surface, text: str, x: int, y: int, color=UI_TEXT,
              size: int = 16, shadow: bool = False):
    fnt = get_font(size)
    if shadow:
        s = fnt.render(text, True, BLACK)
        surf.blit(s, (x+1, y+1))
    t = fnt.render(text, True, color)
    surf.blit(t, (x, y))
    return t.get_width()


def draw_text_centered(surf: pygame.Surface, text: str, y: int, color=UI_TEXT,
                       size: int = 16, x_offset: int = 0, shadow: bool = False):
    fnt = get_font(size)
    t = fnt.render(text, True, color)
    x = (surf.get_width() - t.get_width()) // 2 + x_offset
    if shadow:
        s = fnt.render(text, True, BLACK)
        surf.blit(s, (x + 2, y + 2))
    surf.blit(t, (x, y))
    return x


def draw_rarity_badge(surf: pygame.Surface, rarity: str, x: int, y: int):
    col = RARITY_COLORS.get(rarity, LIGHT_GRAY)
    tag = rarity.upper()
    fnt = get_font(11)
    txt = fnt.render(tag, True, BLACK)
    w = txt.get_width() + 8
    h = txt.get_height() + 4
    pygame.draw.rect(surf, col, (x, y, w, h), border_radius=3)
    surf.blit(txt, (x + 4, y + 2))
    return w


class Button:
    def __init__(self, rect: pygame.Rect, label: str, color=UI_HIGHLIGHT,
                 text_color=WHITE, font_size: int = 16, enabled: bool = True):
        self.rect = rect
        self.label = label
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.enabled = enabled
        self.hovered = False

    def draw(self, surf: pygame.Surface):
        col = self.color if self.enabled else MID_GRAY
        if self.hovered and self.enabled:
            col = tuple(min(255, c + 30) for c in col)
        pygame.draw.rect(surf, col, self.rect, border_radius=5)
        pygame.draw.rect(surf, UI_BORDER, self.rect, 2, border_radius=5)
        fnt = get_font(self.font_size)
        txt = fnt.render(self.label, True, self.text_color if self.enabled else UI_DIM)
        tx = self.rect.x + (self.rect.w - txt.get_width()) // 2
        ty = self.rect.y + (self.rect.h - txt.get_height()) // 2
        surf.blit(txt, (tx, ty))

    def update(self, mouse_pos: tuple):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.enabled and self.rect.collidepoint(event.pos):
                return True
        # Android / SDL touch events — map normalised finger coords to screen space
        if event.type == pygame.FINGERDOWN:
            if self.enabled:
                import pygame as _pg
                scr = _pg.display.get_surface()
                if scr:
                    fx = int(event.x * scr.get_width())
                    fy = int(event.y * scr.get_height())
                    if self.rect.collidepoint(fx, fy):
                        return True
        return False


class ScrollList:
    """Scrollable list of items."""
    def __init__(self, rect: pygame.Rect, items: list, item_h: int = 32, font_size: int = 14):
        self.rect = rect
        self.items = items        # list of (label, value, color)
        self.item_h = item_h
        self.font_size = font_size
        self.scroll_y = 0
        self.selected = -1
        self.hovered  = -1

    def draw(self, surf: pygame.Surface):
        draw_panel(surf, self.rect)
        clip = surf.subsurface(self.rect)
        visible = self.rect.height // self.item_h
        fnt = get_font(self.font_size)
        for i in range(visible):
            idx = i + self.scroll_y
            if idx >= len(self.items):
                break
            label, val, color = self.items[idx][:3]
            row_rect = pygame.Rect(0, i * self.item_h, self.rect.width, self.item_h)
            if idx == self.selected:
                pygame.draw.rect(clip, UI_HIGHLIGHT, row_rect)
            elif idx == self.hovered:
                pygame.draw.rect(clip, (50, 50, 75), row_rect)
            pygame.draw.line(clip, UI_BORDER, (0, row_rect.bottom - 1), (self.rect.width, row_rect.bottom - 1))
            t = fnt.render(label, True, color)
            clip.blit(t, (6, row_rect.y + (self.item_h - t.get_height()) // 2))

    def handle_event(self, event: pygame.event.Event) -> int:
        """Returns clicked index or -1."""
        if event.type == pygame.MOUSEMOTION:
            rel = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
            if 0 <= rel[0] < self.rect.width and 0 <= rel[1] < self.rect.height:
                self.hovered = self.scroll_y + rel[1] // self.item_h
            else:
                self.hovered = -1
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 1:
                    rel_y = event.pos[1] - self.rect.y
                    idx = self.scroll_y + rel_y // self.item_h
                    if 0 <= idx < len(self.items):
                        self.selected = idx
                        return idx
                elif event.button == 4:   # scroll up
                    self.scroll_y = max(0, self.scroll_y - 1)
                elif event.button == 5:   # scroll down
                    max_scroll = max(0, len(self.items) - self.rect.height // self.item_h)
                    self.scroll_y = min(max_scroll, self.scroll_y + 1)
        elif event.type == pygame.FINGERDOWN:
            # Touch scroll support
            tx = int(event.x * SCREEN_W)
            ty = int(event.y * SCREEN_H)
            if self.rect.collidepoint(tx, ty):
                rel_y = ty - self.rect.y
                idx = self.scroll_y + rel_y // self.item_h
                if 0 <= idx < len(self.items):
                    self.selected = idx
                    return idx
        return -1


class DialogBox:
    """Story / NPC dialogue box."""
    def __init__(self, lines: list):
        self.lines = lines
        self.index = 0
        self.done = False
        self.rect = pygame.Rect(40, SCREEN_H - 200, SCREEN_W - 80, 180)
        self.btn = Button(pygame.Rect(SCREEN_W - 160, SCREEN_H - 60, 120, 36), "Next >")

    def draw(self, surf: pygame.Surface):
        draw_panel(surf, self.rect, border_col=GOLD)
        # Progress indicator (top-right corner)
        prog = f"({self.index + 1}/{len(self.lines)})"
        prog_w = get_font(13).size(prog)[0]
        draw_text(surf, prog, self.rect.right - prog_w - 10, self.rect.y + 10, color=UI_DIM, size=13)
        # Word-wrapped body text
        if self.index < len(self.lines):
            fnt   = get_font(15)
            pad   = 14
            max_w = self.rect.width - pad * 2 - prog_w - 20   # keep clear of the counter
            wrapped = wrap_text(self.lines[self.index], fnt, max_w)
            lh = fnt.get_linesize() + 3
            max_rows = max(1, (self.rect.height - 50) // lh)   # leave room for button
            for row, wline in enumerate(wrapped[:max_rows]):
                draw_text(surf, wline, self.rect.x + pad,
                          self.rect.y + 12 + row * lh, color=WHITE, size=15)
        self.btn.draw(surf)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True when dialogue is complete."""
        if self.btn.is_clicked(event) or (
            event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)
        ):
            self.index += 1
            if self.index >= len(self.lines):
                self.done = True
                return True
        return False
