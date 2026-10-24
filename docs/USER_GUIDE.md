# GeneCraft — User Guide

## Getting Started

### Main Menu
| Option | Description |
|---|---|
| New Campaign | 8-chapter structured story mode |
| Sandbox Mode | Unlimited free-form simulation |
| Load Game | Resume from a save slot |

### Your Role: Evolution Architect
You **cannot** directly control creatures. Instead you:
- Design species in the **Gene Lab**
- Unlock tools via the **Research Tree**
- Trigger events via the **Disaster System**
- Observe and react to the living world

---

## Core Controls

| Key | Action |
|---|---|
| `Space` | Pause / Resume |
| `1` | Normal speed (1×) |
| `2` | Fast speed (3×) |
| `3` | Faster speed (8×) |
| `4` | Ultra speed (20×) |
| `F5` | Quick Save |
| `F9` | Quick Load |
| `Escape` | Pause menu |
| Scroll Wheel | Zoom world view |
| Middle Mouse | Pan world view |

---

## The Gene Lab

Access via the **🧬 Gene Lab** button in the bottom bar.

### Trait Categories
| Category | Traits |
|---|---|
| Physical | Speed, Size, Strength, Vision, Stamina, Camouflage, Armor, Bite Force |
| Behavioral | Aggression, Intelligence, Sociality, Migration, Curiosity, Territorial, Fearfulness |
| Genetic | Mutation Rate, Adaptability, Reproduction Rate, Lifespan, Disease Resistance |
| Metabolic | Energy Efficiency, Water Need, Temperature Tolerance |

### Trait Tips
- **High Speed + High Size** → penalised (biologically inconsistent)
- **High Intelligence** → expensive energy cost
- **High Reproduction Rate** → needs more food
- **High Mutation Rate (>0.3)** → population instability

### Trophic Levels
| Level | Role | Diet |
|---|---|---|
| 1 | Producer | Sunlight / Minerals |
| 2 | Herbivore | Plants |
| 3 | Omnivore | Plants + Small animals |
| 4 | Carnivore | Other animals |
| 5 | Apex Predator | Large prey, no natural predators |

---

## Research Tree

5 tiers of research. Unlock nodes by spending Research Points (RP).

**Earn RP by:**
- Passage of time (1 RP/tick base)
- Evolution events (+25 RP each)
- New species registered (+20 RP each)
- Chapter completions (+50 RP bonus)

**Key unlocks:**
- `basic_genetics` → Gene Lab physical traits
- `behavioral_science` → behavioral trait editing
- `climate_control` → weather manipulation
- `genome_sequencing` → full genome editor
- `genesis_protocol` → prestige new world

---

## Biomes

| Biome | Key Trait Pressure | Special |
|---|---|---|
| 🌲 Forest | Camouflage ↑ | Canopy layers, ambush bonus |
| 🌾 Grassland | Speed ↑, Vision ↑ | Herd dynamics |
| ⛰️ Mountain | Endurance ↑ | Altitude zones |
| 🏞️ River | Swimming ↑ | Seasonal flooding |
| 🏔️ Lake | Swimming ↑ | Depth stratification |
| 🏜️ Desert | Heat resistance ↑ | Nocturnal bonus |
| 🌿 Swamp | Disease resistance ↑ | Camouflage in water |
| ❄️ Arctic | Cold resistance ↑ | White camouflage |

---

## Ecosystem Health

Monitor via the **📊 Statistics** panel.

| Metric | Healthy Range | Warning |
|---|---|---|
| Biodiversity Index | 0.60–0.90 | < 0.40 |
| Predator/Prey Ratio | 1:5 to 1:20 | 1:1 or 1:50+ |
| Trophic Levels | 3–5 active | < 2 |

---

## Disasters

**Natural disasters** occur randomly based on world conditions.
**Player-triggered events** cost Research Points.

| Disaster | Effect |
|---|---|
| Wildfire | Burns vegetation, kills slow creatures |
| Flood | Waterloggs land, drowns non-swimmers |
| Drought | Reduces food capacity |
| Disease | Species-targeted mortality |
| Volcanic Eruption | Global ash layer, mass extinction pressure |
| Ice Age | Temperature crash, biome shift |
| Meteor Strike | Localised devastation |

---

## Save System

| Method | Key | Location |
|---|---|---|
| Quick Save | F5 | `saves/__quicksave__.json` |
| Quick Load | F9 | — |
| Auto Save | Every 5 min | `saves/__autosave__.json` |
| Manual | 💾 Save button | `saves/slot_1.json` … `slot_5.json` |

---

## Achievements

25 achievements across 10 categories. Highlights:

| Achievement | Unlock Condition |
|---|---|
| First Breath | Release your first species |
| The Branching | Witness a speciation event |
| Apex Creator | Sustain an apex predator (pop > 20) |
| Planet Builder | Populate all 8 biomes |
| Genesis | Self-sustaining ecosystem for 200 ticks |
| Living Planet | 50 simultaneous species |
