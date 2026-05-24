@echo off
title Legends of the Cursed Realm — Build

:: Always run from the folder where this .bat lives
cd /d "%~dp0"

echo ============================================================
echo  Legends of the Cursed Realm  —  Windows Build Script
echo ============================================================
echo.

:: ── 1. Install / upgrade build tools ─────────────────────────────────────────
echo [1/4] Installing build dependencies...
pip install --quiet --upgrade pillow pyinstaller
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is on your PATH.
    pause
    exit /b 1
)
echo       Done.
echo.

:: ── 2. Generate icon ──────────────────────────────────────────────────────────
echo [2/4] Generating icon (build\icon.ico)...
python build\make_icon.py
if errorlevel 1 (
    echo ERROR: Icon generation failed.
    pause
    exit /b 1
)
echo.

:: ── 3. Run PyInstaller ────────────────────────────────────────────────────────
echo [3/4] Building executable with PyInstaller...
python -m PyInstaller --clean --noconfirm ^
    --workpath "_pyinstaller_work" ^
    --distpath "dist" ^
    LegendsCursedRealm.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)
echo.

:: ── 4. Post-build cleanup / extras ───────────────────────────────────────────
echo [4/4] Finalising output folder...

:: Create tracks folder and copy the README so players know the filenames
if not exist "dist\LegendsCursedRealm\audio\tracks" (
    mkdir "dist\LegendsCursedRealm\audio\tracks"
)
copy /y "audio\tracks\README.txt" "dist\LegendsCursedRealm\audio\tracks\README.txt" >nul

:: Drop a README next to the exe
(
echo Legends of the Cursed Realm
echo ===========================
echo Double-click LegendsCursedRealm.exe to play.
echo.
echo Save files are stored in:
echo   %%USERPROFILE%%\pixel_rpg_saves\
echo.
echo Custom music:
echo   Drop your own .wav files into audio\tracks\
echo   to replace any of the built-in chiptune tracks.
echo   See audio\tracks\README.txt for track names.
) > "dist\LegendsCursedRealm\README.txt"

echo.
echo ============================================================
echo  Build complete!
echo  Executable:  dist\LegendsCursedRealm\LegendsCursedRealm.exe
echo ============================================================
echo.
pause
