"""Export all synthesised music tracks as editable .wav files.

Run this script once from the project root:
    python audio/export_tracks.py

Each track is saved to:
    audio/tracks/<track_name>.wav

How to use your own music
─────────────────────────
1.  Run this script to generate all the default .wav files.
2.  Open any .wav file in Audacity, FL Studio, GarageBand, etc. and edit it.
    (Or replace it entirely with a recording / purchased track.)
3.  Save it back as a 16-bit PCM .wav file with the SAME filename.
4.  Launch the game — it will automatically use your file instead of the
    generated version.

Track names
───────────
  Exploration (looping ~2 min each)
    menu                     Main menu loop
    verdant_plains           Verdant Plains exploration
    whispering_forest        Whispering Forest exploration
    ancient_jungle           Ancient Jungle exploration
    scorching_desert         Scorching Desert exploration
    frozen_tundra            Frozen Tundra exploration
    murky_swamp              Murky Swamp exploration
    volcanic_highlands       Volcanic Highlands exploration
    haunted_ruins            Haunted Ruins exploration
    crystal_caverns          Crystal Caverns exploration
    skyreach_peaks           Skyreach Peaks exploration

  Battle (looping ~2 min each, unique per biome)
    battle_verdant_plains    Verdant Plains combat
    battle_forest            Whispering Forest combat
    battle_jungle            Ancient Jungle combat
    battle_desert            Scorching Desert combat
    battle_tundra            Frozen Tundra combat
    battle_swamp             Murky Swamp combat
    battle_volcanic          Volcanic Highlands combat
    battle_ruins             Haunted Ruins combat
    battle_caverns           Crystal Caverns combat
    battle_skyreach          Skyreach Peaks combat

  Boss (looping ~2 min each, unique per boss)
    boss_golem_king          Golem King
    boss_ancient_treant      Ancient Treant
    boss_pharaoh_undead      Pharaoh Undead
    boss_frost_dragon        Frost Dragon
    boss_jungle_serpent_god  Jungle Serpent God
    boss_swamp_serpent_lord  Swamp Serpent Lord
    boss_volcanic_dragon_lord Volcanic Dragon Lord
    boss_skeleton_king       Skeleton King
    boss_crystal_hydra       Crystal Hydra
    boss_aldrath             Aldrath, King of Dragons

  Special
    alpha                    Alpha-variant monster combat (intense)
    victory                  Victory fanfare (~15 s, plays once)
    item_found               Item/skill discovered (~15 s, plays once)
    gameover                 Game over (~17 s, plays once)

Tips
────
• Any format Pygame can load (.wav, .ogg, .mp3*) works — just keep the
  extension as .wav in the filename OR change the extension check in music.py.
• Stereo or mono both work; Pygame handles the conversion.
• To revert a track to the generated version, simply delete its .wav file.
• The game streams file-based tracks through the melody channel; the separate
  bass channel is silenced when a file is in use.

* .mp3 support depends on your Pygame build and OS.
"""

import array
import math
import os
import sys
import wave

# Allow running from project root or from audio/ folder
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))

from audio.music import TRACKS, SR, GAP, A_MEL, A_BASS, A_CTR
from audio.music import _render   # noqa – internal helper, safe to import directly

OUT_DIR = os.path.join(_HERE, "tracks")


def _export_one(key: str, td: dict) -> None:
    bpm    = td["bpm"]
    mel_w  = td.get("mel_w",  "triangle")
    bass_w = td.get("bass_w", "triangle")
    ctr_w  = td.get("ctr_w",  "sine")

    if "sections" in td:
        # ── Multi-section looping track ──────────────────────────────────────
        all_mel: list = []
        all_bass: list = []
        for sec in td["sections"]:
            sw = sec.get("mel_w",  mel_w)
            bw = sec.get("bass_w", bass_w)
            cw = sec.get("ctr_w",  ctr_w)
            beats   = sum(b for _, b in sec["mel"])
            total_n = int(beats * 60.0 / bpm * SR)
            mel_raw  = _render(sec["mel"],  bpm, sw, A_MEL,  total_n, articulation=0.82)
            bass_raw = _render(sec["bass"], bpm, bw, A_BASS, total_n, articulation=0.94)
            if "ctr" in sec:
                ctr_raw = _render(sec["ctr"], bpm, cw, A_CTR, total_n, articulation=0.88)
                for i in range(len(mel_raw)):
                    v = mel_raw[i] + ctr_raw[i]
                    if   v >  32000: v =  32000
                    elif v < -32000: v = -32000
                    all_mel.append(v)
            else:
                all_mel.extend(mel_raw)
            all_bass.extend(bass_raw)
        gap_samples = [0] * int(GAP * SR)
        all_mel.extend(gap_samples)
        all_bass.extend(gap_samples)
        total_n   = len(all_mel)
        mel_list  = all_mel
        bass_list = all_bass
        ctr_list  = None

    else:
        # ── Flat single-block track (victory / item_found / gameover) ────────
        beats   = sum(b for _, b in td["mel"])
        total_n = int((beats * 60.0 / bpm + GAP) * SR)
        mel_list  = _render(td["mel"],  bpm, mel_w,  A_MEL,  total_n, articulation=0.82)
        bass_list = _render(td["bass"], bpm, bass_w, A_BASS, total_n, articulation=0.94)
        ctr_list  = (_render(td["ctr"], bpm, ctr_w, A_CTR, total_n, articulation=0.88)
                     if "ctr" in td else None)

    # ── Additive mix (same clamp logic as MusicManager._build) ───────────────
    mixed = [0] * total_n
    for i in range(total_n):
        v = mel_list[i] + bass_list[i] + (ctr_list[i] if ctr_list else 0)
        if   v >  32000: v =  32000
        elif v < -32000: v = -32000
        mixed[i] = v

    # ── Write 16-bit stereo PCM .wav (duplicate mono → L + R) ────────────────
    out_path = os.path.join(OUT_DIR, f"{key}.wav")
    stereo = array.array("h", [0] * (total_n * 2))
    stereo[::2]  = array.array("h", mixed)
    stereo[1::2] = array.array("h", mixed)

    with wave.open(out_path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(SR)
        wf.writeframes(stereo.tobytes())

    dur     = total_n / SR
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  {key:<32}  {dur:5.1f}s  {size_kb:>5} KB")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Exporting {len(TRACKS)} tracks to:")
    print(f"  {OUT_DIR}")
    print()

    for key, td in TRACKS.items():
        try:
            _export_one(key, td)
        except Exception as exc:
            print(f"  ERROR exporting '{key}': {exc}")

    print()
    print("Done!")
    print()
    print("Edit any .wav file with Audacity, FL Studio, etc., then save it back")
    print("with the same filename.  The game will use your version automatically.")
    print("Delete a .wav file to revert that track to the generated chiptune.")


if __name__ == "__main__":
    main()
