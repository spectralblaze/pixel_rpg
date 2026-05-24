[app]

# ── Basic identity ─────────────────────────────────────────────────────────────
title        = Legends of the Cursed Realm
package.name = legendscursed
package.domain = com.pixelrpg
version      = 1.0

# ── Source ─────────────────────────────────────────────────────────────────────
source.dir  = .
source.include_exts = py,png,jpg,jpeg,json,ttf,otf,ogg,mp3,wav,atlas,kv

# Exclude build artifacts, dev tools, and OS noise
source.exclude_dirs =
    .buildozer,
    .git,
    __pycache__,
    tools,
    dist,
    build,
    _pyinstaller_work,
    bin,
    saves

source.exclude_patterns =
    *.spec,
    *.bat,
    *.md,
    HOW_TO_RUN*,
    requirements.txt

# ── Display ────────────────────────────────────────────────────────────────────
orientation  = landscape
fullscreen   = 1

# ── Images ────────────────────────────────────────────────────────────────────
icon.filename      = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
presplash.lottie   =

# ── Dependencies ──────────────────────────────────────────────────────────────
# python3  — interpreter
# pygame   — graphics / sound / input (python-for-android pygame2 recipe)
requirements = python3,pygame

# ── Android SDK/NDK ───────────────────────────────────────────────────────────
android.api     = 33
android.minapi  = 24
android.ndk     = 25b
android.ndk_api = 24
android.archs   = arm64-v8a

# Accept the Android SDK license automatically during CI builds
android.accept_sdk_license = True

# Keep the APK smaller — strip debug symbols
android.release_artifact = apk

# ── Permissions ───────────────────────────────────────────────────────────────
# INTERNET       — multiplayer TCP
# VIBRATE        — optional controller feedback (harmless if unused)
android.permissions =
    INTERNET,
    VIBRATE

# ── App entry point ───────────────────────────────────────────────────────────
# main.py is the standard entry point
android.entrypoint = org.kivy.android.PythonActivity

# ── Python-for-android bootstrap ──────────────────────────────────────────────
# 'sdl2' bootstrap provides a pygame-compatible SDL2 window
p4a.bootstrap = sdl2

# ── Buildozer logging ─────────────────────────────────────────────────────────
[buildozer]
log_level    = 2
warn_on_root = 0
