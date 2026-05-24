#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# setup_android_wsl.sh
#
# Run this ONCE inside WSL2 (Ubuntu) to install all Android build tools, then
# builds the debug APK.
#
# Usage (from Windows Terminal / PowerShell):
#   wsl bash /mnt/c/Users/Owner/pixel_rpg/tools/setup_android_wsl.sh
#
# Or open a WSL2 terminal and run:
#   bash /mnt/c/Users/Owner/pixel_rpg/tools/setup_android_wsl.sh
#
# The finished APK will appear at:
#   /mnt/c/Users/Owner/pixel_rpg/bin/legendscursed-1.0-arm64-v8a-debug.apk
# ─────────────────────────────────────────────────────────────────────────────
set -e   # stop on first error

PROJECT_WIN="C:/Users/Owner/pixel_rpg"
PROJECT_WSL="/mnt/c/Users/Owner/pixel_rpg"

echo ""
echo "============================================================"
echo "  Legends of the Cursed Realm — Android build (WSL2)"
echo "============================================================"
echo ""

# ── 1. System dependencies ────────────────────────────────────────────────────
echo "[1/6] Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3 python3-pip python3-venv \
    git zip unzip wget curl \
    build-essential libssl-dev libffi-dev \
    libsqlite3-dev zlib1g-dev \
    openjdk-17-jdk \
    autoconf automake libtool \
    libltdl-dev pkg-config \
    lld clang

# ── 2. Python virtual environment ─────────────────────────────────────────────
echo "[2/6] Creating Python venv..."
cd "$PROJECT_WSL"

if [ ! -d ".venv_android" ]; then
    python3 -m venv .venv_android
fi
source .venv_android/bin/activate

pip install --upgrade pip --quiet
pip install --quiet \
    buildozer \
    cython \
    python-for-android

echo "  Buildozer $(buildozer --version 2>&1 | head -1)"

# ── 3. Android SDK / NDK (Buildozer downloads automatically) ──────────────────
echo "[3/6] Checking Android SDK/NDK..."
echo "  Buildozer will download the Android SDK and NDK on first build."
echo "  This is ~1-2 GB and takes 10-20 min on first run."

# ── 4. Accept Android SDK licenses ───────────────────────────────────────────
ANDROID_SDK="$HOME/.buildozer/android/platform/android-sdk"
if [ -d "$ANDROID_SDK/cmdline-tools" ]; then
    echo "[4/6] Accepting SDK licenses..."
    yes | "$ANDROID_SDK/cmdline-tools/latest/bin/sdkmanager" --licenses 2>/dev/null || true
else
    echo "[4/6] SDK not yet downloaded — licenses will be accepted during build."
fi

# ── 5. Build the APK ──────────────────────────────────────────────────────────
echo "[5/6] Building debug APK (this takes 15-30 min on first build)..."
echo "  Subsequent builds are much faster (2-5 min)."
echo ""

cd "$PROJECT_WSL"
buildozer android debug 2>&1 | tee build_android.log

# ── 6. Done ───────────────────────────────────────────────────────────────────
APK=$(find bin -name "*.apk" 2>/dev/null | head -1)
if [ -n "$APK" ]; then
    echo ""
    echo "============================================================"
    echo "  BUILD SUCCESSFUL!"
    echo "  APK: $PROJECT_WSL/$APK"
    echo "  Windows path: $PROJECT_WIN\\$(echo $APK | tr '/' '\\')"
    echo "============================================================"
    echo ""
    echo "To install on a connected Android device:"
    echo "  adb install $APK"
    echo ""
    echo "Or copy the APK to your phone and open it to sideload."
else
    echo ""
    echo "Build may have failed. Check build_android.log for details."
    exit 1
fi
