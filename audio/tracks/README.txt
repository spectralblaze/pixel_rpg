Custom Music Guide — Legends of the Cursed Realm
=================================================

Drop any .wav file into this folder with the exact filename listed below
to replace that track with your own music.  The game will use your file
automatically.  Delete a file to revert that track to the built-in chiptune.

HOW TO USE
----------
1. Find a .wav file you want to use (or export the defaults with
   python audio/export_tracks.py and edit them in Audacity / FL Studio).
2. Rename it to exactly match one of the filenames below (e.g. menu.wav).
3. Save it as 16-bit PCM .wav, stereo or mono — both work.
4. Launch the game. Your track plays instead of the generated one.

Tip: .ogg and .mp3 also work if you rename the file with a .wav extension
and Pygame can load that format on your OS.

──────────────────────────────────────────────────────────────────────────────
EXPLORATION TRACKS  (loop continuously while exploring each area)
──────────────────────────────────────────────────────────────────────────────
  menu.wav                  Main menu
  verdant_plains.wav        Verdant Plains
  whispering_forest.wav     Whispering Forest
  ancient_jungle.wav        Ancient Jungle
  scorching_desert.wav      Scorching Desert
  frozen_tundra.wav         Frozen Tundra
  murky_swamp.wav           Murky Swamp
  volcanic_highlands.wav    Volcanic Highlands
  haunted_ruins.wav         Haunted Ruins
  crystal_caverns.wav       Crystal Caverns
  skyreach_peaks.wav        Skyreach Peaks

──────────────────────────────────────────────────────────────────────────────
BATTLE TRACKS  (loop during normal combat in each biome)
──────────────────────────────────────────────────────────────────────────────
  battle_verdant_plains.wav Verdant Plains combat
  battle_forest.wav         Whispering Forest combat
  battle_jungle.wav         Ancient Jungle combat
  battle_desert.wav         Scorching Desert combat
  battle_tundra.wav         Frozen Tundra combat
  battle_swamp.wav          Murky Swamp combat
  battle_volcanic.wav       Volcanic Highlands combat
  battle_ruins.wav          Haunted Ruins combat
  battle_caverns.wav        Crystal Caverns combat
  battle_skyreach.wav       Skyreach Peaks combat

──────────────────────────────────────────────────────────────────────────────
BOSS TRACKS  (loop during each boss fight)
──────────────────────────────────────────────────────────────────────────────
  boss_golem_king.wav           Golem King
  boss_ancient_treant.wav       Ancient Treant
  boss_pharaoh_undead.wav       Pharaoh Undead
  boss_frost_dragon.wav         Frost Dragon
  boss_jungle_serpent_god.wav   Jungle Serpent God
  boss_swamp_serpent_lord.wav   Swamp Serpent Lord
  boss_volcanic_dragon_lord.wav Volcanic Dragon Lord
  boss_skeleton_king.wav        Skeleton King
  boss_crystal_hydra.wav        Crystal Hydra
  boss_aldrath.wav              Aldrath, King of Dragons

──────────────────────────────────────────────────────────────────────────────
SPECIAL / ONE-SHOT TRACKS  (play once, do not loop)
──────────────────────────────────────────────────────────────────────────────
  alpha.wav                 Alpha monster combat (intense — loops)
  victory.wav               Victory fanfare  (~15 sec)
  item_found.wav            Item / skill discovered  (~15 sec)
  gameover.wav              Game over  (~17 sec)

──────────────────────────────────────────────────────────────────────────────
EXPORT THE BUILT-IN TRACKS FOR EDITING
──────────────────────────────────────────────────────────────────────────────
Run this from the project root to generate all 35 default tracks as .wav:
  python audio/export_tracks.py

Then open any .wav in Audacity, FL Studio, GarageBand, etc., edit it,
save back with the same filename, and the game will use your version.
