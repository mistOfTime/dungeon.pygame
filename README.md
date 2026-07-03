# 🌑 Eclipse Depths

[![Build & Release](https://github.com/mistOfTime/dungeon.pygame/actions/workflows/build-release.yml/badge.svg)](https://github.com/mistOfTime/dungeon.pygame/actions/workflows/build-release.yml)
[![Latest Release](https://img.shields.io/github/v/release/mistOfTime/dungeon.pygame?label=download)](https://github.com/mistOfTime/dungeon.pygame/releases/latest)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](https://python.org)
[![pygame-ce](https://img.shields.io/badge/pygame--ce-2.5%2B-green)](https://pyga.me)

> **This is my first Pygame project** — a fully hand-crafted 2D roguelike dungeon crawler built entirely in Python. No game engine, no tilemap editor, no pre-made assets. Everything you see — the stone walls, the flickering torches, the animated enemies, the procedural dungeons — is drawn in code from scratch.

---

## 🎮 About the Game

Eclipse Depths is a top-down roguelike dungeon crawler inspired by *Hades*, *Enter the Gungeon*, and *Moonlighter*. Every run generates a completely new dungeon. Fight through floors of monsters, loot treasure chests, cast spells, defeat powerful bosses, and descend ever deeper into the darkness.

---

## ✨ Features

- **Procedural dungeon generation** — unique layout every run with spawn, normal, elite, treasure, shop, boss, secret, puzzle, and exit rooms
- **9 enemy types** — Slime, Goblin, Skeleton, Archer, Bat, Wizard, Ghost, Giant Spider, Dark Knight — each with A\* pathfinding and hand-crafted state machines
- **5 unique bosses** — Skeleton King, Fire Dragon, Ancient Golem, Shadow Knight, Abyss Mage — with multiple phases and special attack patterns
- **7 spells** — Fireball, Ice Blast, Lightning Bolt, Poison Cloud, Heal, Magic Shield, Dash Spell
- **Full loot system** — 6 rarity tiers (Common → Mythic) with randomised stats
- **Drag-and-drop inventory** — equipment slots, hotbar, item tooltips with rarity glow
- **Quest system** — main quests, side quests, daily challenges, achievements
- **Save system** — JSON character saves + SQLite run statistics
- **Particle engine** — custom-built with blood, sparks, healing, level-up, and trail effects
- **Fog of war** — rooms revealed as you explore, minimap updates in real time
- **Cinematic main menu** — hand-drawn stone dungeon background with flickering torches and animated dust

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13+ |
| Game Engine | [Pygame Community Edition (pygame-ce)](https://pyga.me/) |
| Pathfinding | Custom A\* implementation |
| Particle System | Custom engine (no external lib) |
| Data Storage | JSON (saves) + SQLite (stats & achievements) |
| Animation | Sprite sheets + pytweening |
| Audio | pygame.mixer |
| Version Control | Git + GitHub |

---

## 📁 Project Structure

```
eclipse_depths/
├── assets/
│   ├── sprites/       # PNG sprites (drop Kenney/CraftPix assets here)
│   ├── tiles/         # Tilesets
│   ├── ui/            # UI elements
│   ├── fonts/         # pixel.ttf (optional)
│   └── audio/         # .ogg / .wav sound files
├── src/
│   ├── core/          # Game loop, camera, constants, asset manager
│   ├── player/        # Player entity, sprite drawing
│   ├── enemies/       # All 9 enemy types + base class
│   ├── bosses/        # All 5 bosses + base class
│   ├── combat/        # Projectiles, melee hitboxes
│   ├── spells/        # Spell manager + 7 spells
│   ├── inventory/     # Inventory grid, equipment slots, hotbar
│   ├── items/         # Item data, loot generation, rarity system
│   ├── dungeon/       # Procedural generator + realistic renderer
│   ├── world/         # GameWorld orchestrator, loot drops, chests, NPCs
│   ├── effects/       # Particle engine, floating damage numbers
│   ├── quests/        # Quest manager, main/side/daily/achievement quests
│   ├── ui/            # All screens: HUD, menus, inventory, map, settings
│   ├── save/          # JSON save + SQLite stats
│   ├── settings/      # Settings manager + key bindings
│   └── audio/         # Audio manager
└── main.py
```

---

## 🚀 Getting Started

### ⬇️ Download & Play (No Python needed)
Go to the [**Releases page**](https://github.com/mistOfTime/dungeon.pygame/releases/latest), download `EclipseDepths-Windows.zip`, extract it, and double-click `EclipseDepths.exe`.

### 🛠 Run from Source

### Requirements
- Python 3.13+
- pip

### Install & Run

```bash
git clone https://github.com/mistOfTime/dungeon.pygame.git
cd dungeon.pygame
pip install -r requirements.txt
python main.py
```

### requirements.txt
```
pygame-ce>=2.4.0
pygame_gui>=0.6.9
pytweening>=1.2.0
```

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `WASD` | Move |
| `Mouse` | Aim |
| `Left Click` | Melee attack |
| `Right Click` | Ranged attack (bow/staff) |
| `Space` | Dodge roll (i-frames) |
| `Shift` | Sprint |
| `Z / X / C / V` | Cast spells 1–4 |
| `E` | Interact / Open chest / Descend |
| `I` | Inventory |
| `M` | Dungeon map |
| `Q` | Quest log |
| `Esc` | Pause |
| `1 / 2 / 3 / 4` | Use hotbar item |

---

---

## 🗺 Roadmap

- [ ] Real pixel art sprites (Kenney.nl / CraftPix)
- [ ] Multiplayer co-op (local)
- [ ] More boss types and floors
- [ ] Skill tree UI
- [ ] PyInstaller standalone build
- [ ] Web demo (Pygbag / WebAssembly)

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

**mistOfTime**
- GitHub: [@mistOfTime](https://github.com/mistOfTime)

---

*Built with ❤️ and Python. The darkness hungers — will you descend?*
