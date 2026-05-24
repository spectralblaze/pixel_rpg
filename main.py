"""Entry point for Legends of the Cursed Realm."""
import sys
import os
import traceback

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Android crash logger ───────────────────────────────────────────────────────
# If the game throws any exception at startup, catch it, show it on-screen
# (so you can read the error directly on the device), and write crash.log to
# ANDROID_PRIVATE so you can pull it with adb later.
def _show_crash(err_text: str) -> None:
    """Render the crash traceback to the pygame surface and wait for a tap."""
    try:
        import pygame
        if not pygame.get_init():
            pygame.init()
        scr = pygame.display.get_surface()
        if scr is None:
            scr = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        scr.fill((10, 0, 20))
        font = pygame.font.SysFont(None, 22)
        title = pygame.font.SysFont(None, 32).render(
            "STARTUP CRASH  (tap to close)", True, (255, 80, 80))
        scr.blit(title, (10, 8))
        y = 46
        for line in err_text.splitlines():
            # Wrap long lines
            while len(line) > 90:
                surf = font.render(line[:90], True, (255, 200, 200))
                scr.blit(surf, (10, y))
                y += 22
                line = "  " + line[90:]
            surf = font.render(line, True, (255, 200, 200))
            scr.blit(surf, (10, y))
            y += 22
            if y > scr.get_height() - 30:
                break
        hint = font.render("Crash log written to app storage", True, (160, 160, 160))
        scr.blit(hint, (10, scr.get_height() - 26))
        pygame.display.flip()
        # Wait for tap / keypress before closing
        clock = pygame.time.Clock()
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type in (pygame.QUIT, pygame.KEYDOWN,
                               pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    waiting = False
            clock.tick(30)
    except Exception:
        pass  # if even the crash screen fails, just exit


def _write_crash_log(err_text: str) -> None:
    android_private = os.environ.get("ANDROID_PRIVATE", "")
    log_dir = android_private if android_private else os.path.dirname(
        os.path.abspath(__file__))
    try:
        with open(os.path.join(log_dir, "crash.log"), "w") as f:
            f.write(err_text)
    except Exception:
        pass


# ── Mixer pre-init (best-effort — some Android devices deny audio at boot) ─────
try:
    import pygame
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
except Exception:
    pass  # audio will still be attempted inside Game.__init__; fail gracefully


# ── Main entry point ───────────────────────────────────────────────────────────
def main():
    try:
        from game import Game
        game = Game()
        game.run()
    except Exception:
        err = traceback.format_exc()
        _write_crash_log(err)
        _show_crash(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
