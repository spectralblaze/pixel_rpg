"""Entry point for Legends of the Cursed Realm."""
import sys
import os
import traceback

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────────────────────
# Crash helpers — called when an exception escapes Game.run()
# ─────────────────────────────────────────────────────────────────────────────

def _write_crash_log(err_text: str) -> None:
    """Write crash.log to the first writable location we can find."""
    candidates = [
        os.environ.get("ANDROID_PRIVATE", ""),
        os.environ.get("ANDROID_ARGUMENT", ""),
        "/sdcard",
        os.path.dirname(os.path.abspath(__file__)),
    ]
    for folder in candidates:
        if not folder:
            continue
        try:
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, "crash.log")
            with open(path, "w") as f:
                f.write(err_text)
            print("crash.log written to:", path)   # goes to adb logcat
            return
        except Exception:
            continue


def _show_crash(err_text: str) -> None:
    """Best-effort: render the traceback to the pygame surface."""
    try:
        import pygame
        if not pygame.get_init():
            pygame.init()

        # Try to get an existing surface; if none, create one.
        scr = pygame.display.get_surface()
        if scr is None:
            # Try without FULLSCREEN first — safer on Android
            for mode_args in [((0, 0),), ((480, 320),)]:
                try:
                    scr = pygame.display.set_mode(*mode_args)
                    break
                except Exception:
                    continue

        if scr is None:
            return  # display completely unavailable; crash.log is the fallback

        W, H = scr.get_size()
        scr.fill((10, 0, 20))

        try:
            big   = pygame.font.SysFont(None, 30)
            small = pygame.font.SysFont(None, 22)
        except Exception:
            return  # font system broken; give up

        scr.blit(big.render("CRASH — tap / press to close", True, (255, 80, 80)),
                 (10, 8))
        scr.blit(small.render("crash.log saved to app storage", True,
                               (160, 160, 160)), (10, H - 24))

        y = 44
        for raw_line in err_text.splitlines():
            # hard-wrap long lines
            while raw_line:
                chunk, raw_line = raw_line[:85], raw_line[85:]
                surf = small.render(chunk, True, (255, 200, 200))
                scr.blit(surf, (10, y))
                y += 21
                if y > H - 30:
                    break
            if y > H - 30:
                break

        pygame.display.flip()

        # Wait for a tap / keypress before exiting
        clock = pygame.time.Clock()
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type in (pygame.QUIT, pygame.KEYDOWN,
                               pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    waiting = False
            clock.tick(30)
    except Exception:
        pass  # crash screen itself failed — crash.log is the only output


# ─────────────────────────────────────────────────────────────────────────────
# Mixer pre-init (best-effort — some Android devices deny audio at boot)
# ─────────────────────────────────────────────────────────────────────────────
try:
    import pygame
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
except Exception:
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    try:
        from game import Game
        game = Game()
        game.run()
    except Exception:
        err = traceback.format_exc()
        print(err)               # always goes to adb logcat
        _write_crash_log(err)    # write BEFORE touching the display
        _show_crash(err)         # show on-screen if possible
        sys.exit(1)


# p4a may import this as a module (__name__ == 'main') rather than running it
# as __main__, so we handle both cases.
if __name__ in ("__main__", "main"):
    main()
