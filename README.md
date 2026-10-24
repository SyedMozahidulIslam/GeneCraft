# 🧬 GeneCraft
### *Shape Genes. Control Evolution. Build a Living World.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Pygame](https://img.shields.io/badge/Pygame-2.5.2-green?logo=pygame)](https://pygame.org)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](CHANGELOG.md)

---

GeneCraft is a **professional-grade evolution and ecosystem simulation game** built with Python and Pygame. You play as an Evolution Architect — an unseen force that shapes the genetic makeup of species, alters environments, and guides the trajectory of life on a living, breathing planet.

No two worlds evolve the same way. Every ecosystem tells its own story.

---

## ✨ Features

| Feature | Description |
|---|---|
| **🧬 Genetics Engine** | Full DNA-based trait system with inheritance, mutation, and natural selection |
| **🌍 Living Ecosystem** | 8 distinct biomes with dynamic food chains, climate, and seasons |
| **🤖 AI Creatures** | Priority-based state machine AI — hunt, flee, reproduce, migrate, defend |
| **🔬 Research Tree** | 5-tier research system with 20+ unlockable tools and abilities |
| **⚗️ Gene Lab** | Design species from scratch with 20+ editable genetic traits |
| **⚡ Disaster System** | 7 natural + 7 player-triggered disasters reshape your world |
| **📊 Statistics** | Real-time population graphs, biodiversity index, evolution timeline |
| **🏆 Achievements** | 25 unlockable achievements across 10 categories |
| **💾 Save System** | Auto-save + 5 manual slots + quicksave |
| **🎵 Audio** | Procedural SFX synthesis + music system |
| **🗺️ Campaign** | 8-chapter structured campaign + unlimited sandbox mode |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/GeneCraft.git
cd GeneCraft

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Command-Line Options

```bash
python main.py              # Normal start
python main.py --debug      # Debug mode (verbose logging, FPS counter)
python main.py --fullscreen # Start fullscreen
python main.py --size large # Large world (400×400)
python main.py --skip-menu  # Jump straight into sandbox (dev mode)
```

---

## 🎮 How to Play

### Core Loop
1. **Create** a species in the Gene Lab
2. **Release** it into a biome
3. **Observe** natural selection, mutation, and adaptation
4. **Research** new tools to shape evolution
5. **React** to disasters, extinctions, and emergent behaviors
6. **Expand** your ecosystem across all 8 biomes

### Controls

| Key | Action |
|---|---|
| `Space` | Pause / Resume |
| `1–4` | Simulation speed |
| `F5` | Quick Save |
| `F9` | Quick Load |
| `Scroll Wheel` | Zoom world view |
| `Middle Mouse` | Pan world view |
| `Escape` | Menu |

### Bottom Bar Panels
| Button | Opens |
|---|---|
| 🧬 Gene Lab | Species designer |
| 🔬 Research | Research tree |
| 📊 Statistics | Analytics dashboard |
| 📖 Encyclopedia | Species compendium |
| ⚡ Events | Event log |
| 💾 Save | Save / Load screen |

---

## 🌍 Biomes

| Biome | Temperature | Key Challenge | Evolution Pressure |
|---|---|---|---|
| 🌲 Forest | 5–25°C | Dense cover, predator ambush | Camouflage ↑ |
| 🌾 Grassland | 5–35°C | Open exposure, seasonal drought | Speed ↑, Vision ↑ |
| ⛰️ Mountain | −10–15°C | Altitude, sparse food | Endurance ↑, Size ↓ |
| 🏞️ River | 5–28°C | Flooding, currents | Swimming ↑ |
| 🏔️ Lake | 4–26°C | Stratification, escape | Swimming ↑ |
| 🏜️ Desert | −5–50°C | Heat, dehydration | Heat resistance ↑ |
| 🌿 Swamp | 15–38°C | Disease, slow movement | Disease resistance ↑ |
| ❄️ Arctic | −50–5°C | Hypothermia, darkness | Cold resistance ↑ |

---

## 🧬 The Genetics System

Every species has a **Genome** with 4 gene categories:

```
Physical   → Speed, Size, Strength, Vision, Stamina, Camouflage, Armor, Bite Force
Behavioral → Aggression, Intelligence, Sociality, Migration, Curiosity, Territorial
Genetic    → Mutation Rate, Adaptability, Reproduction Rate, Lifespan, Disease Resistance
Metabolic  → Energy Efficiency, Water Need, Temperature Tolerance
```

**Natural Selection** evaluates fitness each generation based on:
- Food acquisition ratio
- Temperature compatibility
- Combat outcomes
- Physical robustness
- Biome-specific pressure bonuses

**Speciation** occurs when isolated sub-populations diverge genetically beyond a threshold. New species branch from existing ones automatically.

---

## 🏗️ Architecture

GeneCraft uses a clean **ECS-hybrid + OOP** architecture:

```
GameEngine (Singleton)
├── EventBus          ← Decoupled pub/sub messaging
├── SimulationEngine  ← Master tick coordinator
│   ├── World         ← Tile grid, biomes, climate
│   ├── GeneticsEngine← Natural selection, mutation
│   ├── SpeciesRegistry← All species management
│   └── BehaviorFSM  ← Creature AI state machine
├── Systems
│   ├── ResearchSystem
│   ├── DisasterSystem
│   ├── StatisticsSystem
│   ├── AchievementSystem
│   └── SaveSystem
├── UIEngine          ← All rendering
└── AudioManager      ← Sound + synthesis
```

All systems communicate through the **EventBus** (no direct references), enabling clean separation and future extensibility.

---

## 📁 Project Structure

```
GeneCraft/
├── main.py                  ← Entry point
├── requirements.txt
├── config/                  ← All JSON configuration
│   ├── settings.json
│   ├── biomes.json
│   ├── genes.json
│   ├── research_tree.json
│   └── achievements.json
├── src/                     ← All source code
│   ├── engine/              ← Core engine & event bus
│   ├── simulation/          ← Simulation tick engine
│   ├── genetics/            ← Genome & selection
│   ├── species/             ← Creature & species classes
│   ├── world/               ← World grid & biomes
│   ├── ai/                  ← Behavior state machine
│   ├── systems/             ← Research, disasters, stats, save
│   ├── ui/                  ← Complete UI system
│   └── audio/               ← Audio manager & synthesis
├── data/campaign/           ← Campaign chapter data
├── assets/                  ← Audio, fonts, images
├── saves/                   ← Save slot files
└── docs/                    ← Documentation
```

---

## 🗺️ Roadmap

### v1.1 (Next Release)
- [ ] Steam achievements integration
- [ ] Controller support
- [ ] 3 additional biomes (Volcanic, Deep Ocean, Cloud Forest)
- [ ] 20 new species templates
- [ ] Photo mode

### v2.0 (Major Expansion)
- [ ] Multiplayer ecosystem comparison
- [ ] Species export/import JSON sharing
- [ ] Mod support (species injection)
- [ ] Procedural soundtrack system

### v3.0 (Platform)
- [ ] Mobile port (touch-optimised)
- [ ] Cloud saves
- [ ] Steam Workshop

---

## 🔧 Development

### Running in Debug Mode
```bash
python main.py --debug
```
This enables:
- Verbose logging to `logs/genecraft.log`
- FPS counter in top bar
- Debug overlays

### Configuration
All game parameters are in `config/settings.json`. Key values:

```json
"simulation": {
  "tick_rate": 10,
  "max_creatures_total": 5000,
  "speeds": {"normal": 1, "fast": 3, "faster": 8, "ultra": 20}
}
```

---

## 📖 Documentation

| Document | Description |
|---|---|
| [GDD.md](docs/GDD.md) | Complete Game Design Document |
| [DEV_GUIDE.md](docs/DEV_GUIDE.md) | Developer architecture guide |
| [USER_GUIDE.md](docs/USER_GUIDE.md) | Full player guide |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Credits

Built with:
- [Python](https://python.org) — Core language
- [Pygame](https://pygame.org) — Graphics and audio
- [NumPy](https://numpy.org) — Tile data and sound synthesis

---

*"Life does not ask permission before it changes."*  
*— GeneCraft Research Tree, Behavioral Science node*
