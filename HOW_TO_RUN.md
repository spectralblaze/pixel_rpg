# Legends of the Cursed Realm — How to Run

## On PC (Windows/Mac/Linux)

```
pip install pygame
python main.py
```

## Controls
| Input | Action |
|-------|--------|
| WASD / Arrow Keys | Move |
| Mouse click / Touch | All menus and buttons |
| On-screen D-pad | Move (touch/mobile) |
| ESC | Back / Pause |

## Android (APK)

Install Buildozer on Linux/WSL then:
```
buildozer android debug deploy run
```
The game has full touch support and on-screen D-pad.

## Game Guide

### Story
Your parent has the Dragon's Blight. Only the Celestial Bloom
(held by Aldrath, King of Dragons in Skyreach Peaks) can cure them.
Travel through 9 lands, grow strong, and defeat Aldrath.

### Classes (5 base → 3 subclasses each at level 20)
- **Warrior** → Knight / Berserker / Paladin
- **Mage** → Wizard / Warlock / Elementalist
- **Rogue** → Assassin / Ranger / Shadow
- **Healer** → Priest / Druid / Oracle
- **Summoner** → Beastmaster / Necromancer / Spirit Caller

### 9 Biomes (in order)
1. Verdant Plains (Lv 1–15)
2. Whispering Forest (Lv 10–25)
3. Scorching Desert (Lv 20–35)
4. Frozen Tundra (Lv 30–45)
5. Murky Swamp (Lv 40–55)
6. Volcanic Highlands (Lv 50–65)
7. Haunted Ruins (Lv 60–75)
8. Crystal Caverns (Lv 70–85)
9. Skyreach Peaks (Lv 80–100) ← Final Boss

### Rarity System
Common → Uncommon → Rare → Epic → Legendary → Mythical

### Monster Variants
- **Alpha** (6% chance): 2× HP, 2× ATK — uncapturable
- **Evolved** (4% chance): spawns the next-form monster

### Pets
- Use a **Capture Net** in battle when enemy HP is low
- Beastmaster class has higher capture rates
- Pets level up, evolve at 50% and 85% of max level

### Skills
- Level-up skills: earned automatically when leveling
- **Found skills** (marked GOLD): hidden in ? cave tiles on each map

### Villages
Each biome has a village with:
- **Inn**: Full heal + auto-save
- **Shop**: Buy/sell items
- **Blacksmith**: Upgrade equipped gear (+10% stats, 500g)
- **Pet Stable**: Manage stored pets
- **Fast Travel**: Jump to any unlocked biome (20g)

### Save Files
Saves stored in: `~/pixel_rpg_saves/`
Auto-save at inns. Up to 99 manual save slots.
