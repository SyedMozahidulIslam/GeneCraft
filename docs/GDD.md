# 🧬 GeneCraft — Game Design Document (GDD)
**Version:** 1.0.0  
**Status:** Approved for Development  
**Classification:** Commercial Indie Simulation Game  
**Engine:** Python + Pygame  
**Target Platform:** Windows / macOS / Linux  

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Game Overview](#2-game-overview)
3. [Core Design Pillars](#3-core-design-pillars)
4. [Player Experience Vision](#4-player-experience-vision)
5. [Game Modes](#5-game-modes)
6. [World System](#6-world-system)
7. [Creature System](#7-creature-system)
8. [Genetics & Evolution Engine](#8-genetics--evolution-engine)
9. [AI Behavior System](#9-ai-behavior-system)
10. [Food Chain System](#10-food-chain-system)
11. [Research Tree System](#11-research-tree-system)
12. [Gene Lab System](#12-gene-lab-system)
13. [Disaster & Event System](#13-disaster--event-system)
14. [Statistics & Analytics System](#14-statistics--analytics-system)
15. [Achievement System](#15-achievement-system)
16. [Campaign Mode Design](#16-campaign-mode-design)
17. [Sandbox Mode Design](#17-sandbox-mode-design)
18. [User Interface Design](#18-user-interface-design)
19. [Audio Design](#19-audio-design)
20. [Save System Design](#20-save-system-design)
21. [Technical Architecture](#21-technical-architecture)
22. [Project Structure](#22-project-structure)
23. [Data Schemas](#23-data-schemas)
24. [Performance Targets](#24-performance-targets)
25. [Future Roadmap](#25-future-roadmap)

---

## 1. EXECUTIVE SUMMARY

**Title:** GeneCraft  
**Tagline:** *"Shape Genes. Control Evolution. Build a Living World."*  
**Genre:** Evolution Simulation / Strategy / Sandbox  
**Target Audience:** Fans of Spore, Civilization, Planet Zoo, Jurassic World Evolution  
**Tone:** Scientific, Futuristic, Professional, Emergent  
**Core Fantasy:** You are a god of evolution — not controlling creatures directly, but shaping the invisible forces that determine which traits survive and which vanish.

GeneCraft is a **living ecosystem simulation** where the player acts as an Evolution Architect. You craft organisms at the genetic level, release them into procedurally generated biomes, observe emergent behavior, and guide the trajectory of life itself. No two playthroughs evolve identically. The world is deterministically chaotic — small genetic changes cascade into massive ecological shifts.

---

## 2. GAME OVERVIEW

### Elevator Pitch
GeneCraft puts you in the role of an unseen evolutionary force. You don't pilot creatures — you shape the rules they live by. Tweak a gene here, trigger a climate event there, and watch an entire food chain reorganize itself. The simulation runs continuously, evolving creatures based on environmental pressure, competition, and genetic inheritance. Your job is to guide this living world toward complexity, stability, and eventually — a thriving biosphere.

### High-Level Features
| Feature | Description |
|---|---|
| Living Ecosystem | Real-time simulation of species, food chains, climate |
| Genetics Engine | Full DNA-based trait system with mutation and inheritance |
| Evolution AI | Species adapt over generations using natural selection |
| Gene Lab | Flagship feature: design organisms from scratch |
| Research Tree | Unlock advanced tools and ecosystem engineering |
| Biome System | 8 distinct biomes with unique physics and food sources |
| Campaign Mode | 8 structured chapters with escalating challenges |
| Sandbox Mode | Unlimited free-form evolution simulation |
| Statistics Dashboard | Real-time analytics, population graphs, extinction events |
| Disaster System | Natural and player-triggered catastrophic events |
| Achievement System | 30+ unlockable achievements |
| Save System | Auto-save + manual slots + slot management |

---

## 3. CORE DESIGN PILLARS

### Pillar 1: Emergent Complexity
The game's most interesting outcomes must emerge naturally from simple rules. The player never scripted a "wolf that developed pack hunting" — the simulation produced it. Every ecosystem should tell its own story.

### Pillar 2: Meaningful Player Agency
The player must feel powerful even without direct control. Every action (gene modification, biome change, disaster trigger) must produce visible, traceable consequences in the ecosystem.

### Pillar 3: Scientific Authenticity
Evolution, genetics, and ecology should follow real biological logic (simplified for gameplay). Players should feel they're learning real concepts while playing.

### Pillar 4: Visual Clarity
The simulation must be readable at a glance. Population trends, territorial dynamics, and species health must be communicable through clean visual design without overwhelming the player.

### Pillar 5: Endless Replayability
No world should evolve the same way twice. Procedural generation + emergent AI + player choice = infinite unique playthroughs.

---

## 4. PLAYER EXPERIENCE VISION

### Emotional Arc
```
Curiosity → Wonder → Investment → Crisis → Mastery → Pride
```

- **Curiosity:** "What happens if I make this creature faster?"
- **Wonder:** "I never expected the herbivores to develop herding behavior."
- **Investment:** "My apex predator species is evolving a new sensory organ."
- **Crisis:** "A disease is wiping out my food chain base — I need to intervene."
- **Mastery:** "I know exactly which gene to tweak to stabilize this ecosystem."
- **Pride:** "I built a thriving, self-sustaining biosphere from nothing."

### What Players Do Each Session
1. Review ecosystem health dashboard
2. Observe evolution events from previous session
3. Spend research points on tree upgrades
4. Modify one or two species in the Gene Lab
5. Trigger or respond to a world event
6. Watch consequences unfold
7. Note new evolution pressures for next session

---

## 5. GAME MODES

### 5.1 Campaign Mode
**Structure:** 8 Chapters (+ Final Chapter)  
**Pacing:** Linear progression with unlocking mechanics  
**Objective:** Build a Perfect Ecosystem as defined per chapter  
**Difficulty:** Escalates across chapters  

### 5.2 Sandbox Mode
**Structure:** Unlimited, player-defined  
**Pacing:** Self-directed  
**Objective:** None — pure exploration and experimentation  
**Features:** All tools available from start (configurable), time controls, god mode  

### 5.3 Challenge Mode (Future)
**Structure:** Timed scenarios with specific conditions  
**Examples:** Survive an Ice Age, Build a food chain in a Desert, Prevent extinction  

---

## 6. WORLD SYSTEM

### 6.1 World Generation
Worlds are procedurally generated using:
- Noise-based terrain (Perlin noise simulation)
- Biome placement rules (temperature × moisture matrix)
- River/lake generation (elevation flow simulation)
- Resource distribution (clustered placement with variation)

**World Sizes:**
| Size | Grid | Biome Count | Max Species |
|---|---|---|---|
| Small | 100×100 | 3–4 | 12 |
| Medium | 200×200 | 5–6 | 25 |
| Large | 400×400 | 7–8 | 50 |

### 6.2 Biomes

#### Forest
- **Temperature:** Mild (10–25°C)
- **Moisture:** High
- **Food Sources:** Berries, nuts, insects, small mammals
- **Challenges:** Limited visibility, dense competition
- **Unique Mechanic:** Canopy layers create micro-ecosystems
- **Colors:** Deep greens, browns

#### Grassland
- **Temperature:** Variable (5–35°C)
- **Moisture:** Moderate
- **Food Sources:** Grass, seeds, grazing animals
- **Challenges:** Exposure to predators, seasonal drought
- **Unique Mechanic:** Herd dynamics, open sight lines favor fast predators
- **Colors:** Yellows, light greens

#### Mountains
- **Temperature:** Cold (−10–15°C)
- **Moisture:** Low–Moderate
- **Food Sources:** Sparse vegetation, mountain goats, rock prey
- **Challenges:** Altitude pressure, low oxygen, harsh winters
- **Unique Mechanic:** Altitude zones — different species dominate at each level
- **Colors:** Grays, whites, purples

#### Rivers
- **Temperature:** Moderate
- **Moisture:** Very High
- **Food Sources:** Fish, amphibians, riverside plants
- **Challenges:** Flooding, current dynamics, predator access points
- **Unique Mechanic:** Seasonal water level changes
- **Colors:** Blues, teals

#### Lakes
- **Temperature:** Moderate
- **Moisture:** Very High
- **Food Sources:** Fish, algae, water insects
- **Challenges:** Oxygen stratification, limited escape routes
- **Unique Mechanic:** Deep/shallow zone specialization
- **Colors:** Dark blues, greens

#### Desert
- **Temperature:** Extreme (−5–50°C, day/night swing)
- **Moisture:** Very Low
- **Food Sources:** Cacti, insects, burrowing animals
- **Challenges:** Heat stress, dehydration, sparse food
- **Unique Mechanic:** Nocturnal bonus — creatures active at night gain efficiency
- **Colors:** Oranges, tans, reds

#### Swamp
- **Temperature:** Warm (15–35°C)
- **Moisture:** Extreme
- **Food Sources:** Fish, insects, amphibians, water plants
- **Challenges:** Disease pressure, slow movement, ambush predators
- **Unique Mechanic:** Camouflage bonus in water, disease spread mechanic
- **Colors:** Dark greens, murky browns

#### Arctic
- **Temperature:** Extreme Cold (−50–0°C)
- **Moisture:** High (as ice/snow)
- **Food Sources:** Fish, seals, polar prey
- **Challenges:** Hypothermia, seasonal darkness, ice movement
- **Unique Mechanic:** White coloration gives camouflage bonus
- **Colors:** Whites, ice blues, grays

### 6.3 Climate System
- **Day/Night Cycle:** Affects creature behavior, temperature, visibility
- **Seasons:** Spring, Summer, Autumn, Winter — affect food availability
- **Weather Events:** Rain, drought, snow, heatwave — temporary biome modifiers
- **Climate Drift:** Long-term world temperature changes over time

### 6.4 Resources
| Resource Type | Found In | Replenishment |
|---|---|---|
| Plant Matter | All biomes | Seasonal regeneration |
| Water | Rivers, Lakes, Swamps | Rainfall-dependent |
| Prey Animals | All biomes | Population-based |
| Minerals | Mountains, Desert | Static |

---

## 7. CREATURE SYSTEM

### 7.1 Creature Anatomy
Every creature is an object with full attribute resolution. No two creatures are identical due to genetic variance.

### 7.2 Physical Attributes
| Attribute | Range | Effect |
|---|---|---|
| Size | 0.1–10.0 | Affects strength, stamina, visibility, food need |
| Weight | 0.5–1000.0 kg | Affects speed, energy cost, combat |
| Speed | 0.1–10.0 | Movement rate, escape/pursuit capability |
| Vision | 1–10 | Detection range, prey/predator awareness |
| Strength | 1–10 | Combat power, ability to take down larger prey |
| Stamina | 1–10 | Energy reserves, sustained activity duration |
| Camouflage | 0–10 | Detection reduction, stealth hunting |
| Bite Force | 1–10 | Predation effectiveness |
| Armor | 0–10 | Damage reduction in combat |

### 7.3 Behavioral Attributes
| Attribute | Range | Effect |
|---|---|---|
| Aggression | 0–10 | Willingness to attack, territory defense |
| Intelligence | 1–10 | Problem-solving, tool use, group coordination |
| Curiosity | 0–10 | Exploration range, resource discovery |
| Social Behavior | 0–10 | Pack/herd formation tendency |
| Migration Instinct | 0–10 | Seasonal movement probability |
| Territorial | 0–10 | Defense of home range |
| Fearfulness | 0–10 | Response to threat, escape trigger threshold |

### 7.4 Genetic Attributes
| Attribute | Range | Effect |
|---|---|---|
| Mutation Rate | 0.01–0.5 | Probability of offspring genetic variance |
| Adaptability | 0–10 | Speed of environmental adaptation |
| Reproduction Rate | 0.1–10 | Offspring count per cycle |
| Lifespan | 1–100 | Generations before natural death |
| Disease Resistance | 0–10 | Survival chance during outbreak events |

### 7.5 Metabolic System
- **Energy System:** Every creature has energy. Actions cost energy. Eating restores energy.
- **Hunger Meter:** Drives feeding behavior AI
- **Hydration Meter:** Water dependency (Desert/Arctic biomes critical)
- **Temperature Tolerance:** Species have preferred temperature ranges; outside = penalty

### 7.6 Life Stages
```
Egg/Birth → Juvenile → Adult → Elder → Death
```
Each stage has modified stats. Juveniles are vulnerable; elders reproduce less.

### 7.7 Species Classification
| Tier | Role | Examples |
|---|---|---|
| Producer | Plant/Algae | Grass, Trees, Algae |
| Primary Consumer | Herbivore | Deer analog, Rabbit analog |
| Secondary Consumer | Omnivore/Small Predator | Fox analog, Small fish |
| Tertiary Consumer | Carnivore | Wolf analog, Eagle analog |
| Apex Predator | Top of chain | T-Rex analog, Shark analog |

---

## 8. GENETICS & EVOLUTION ENGINE

### 8.1 DNA Representation
Each species has a **Genome** — a dictionary of gene loci with allele values:

```
Genome = {
  "physical": {
    "speed": float,        # 0.0–10.0
    "size": float,         # 0.1–10.0
    "strength": float,     # 0–10
    "vision": float,       # 1–10
    "stamina": float,      # 1–10
    "camouflage": float,   # 0–10
    "armor": float,        # 0–10
  },
  "behavioral": {
    "aggression": float,
    "intelligence": float,
    "social": float,
    "migration": float,
    "curiosity": float,
  },
  "genetic": {
    "mutation_rate": float,  # 0.01–0.5
    "adaptability": float,
    "reproduction_rate": float,
    "lifespan": int,
    "disease_resistance": float,
  },
  "metabolic": {
    "energy_efficiency": float,  # calories per kg per move
    "water_need": float,
    "temperature_tolerance": tuple,  # (min, max) °C
  }
}
```

### 8.2 Inheritance System
When two creatures reproduce:
1. Each gene locus: 50% chance from parent A, 50% from parent B
2. Apply mutation: `gene += random.gauss(0, mutation_rate)`
3. Clamp to valid range
4. Result: Offspring genome with parental traits + variance

### 8.3 Natural Selection Algorithm
Each generation tick:
1. **Fitness Score** calculated per creature based on:
   - Food acquired / food needed (survival)
   - Combat outcomes (predator success / prey escape rate)
   - Reproduction events
   - Biome compatibility (temperature match, terrain bonus)
2. **High-fitness creatures** reproduce more
3. **Low-fitness creatures** die earlier
4. **Population pressure:** If over capacity, weakest die first

### 8.4 Adaptation System
Species-level adaptation (separate from individual mutation):
- If 60%+ of a population shares a pressured trait → species pressure flag set
- Next generation gets +adaptation boost toward that trait
- Visual event triggered: "Evolution Observed: [Species] is developing [Trait]"

### 8.5 Speciation
If a sub-population is geographically isolated for N generations AND their genomes diverge by threshold T:
- A new species spawns as a fork of the original
- Player notification: "New Species Detected: [Name]"
- Encyclopedia entry auto-generated

### 8.6 Extinction Conditions
A species goes extinct when:
- Population drops to 0
- Population < 3 AND food availability < threshold for 5 consecutive ticks
- Disease kills last survivors

Extinction triggers:
- Encyclopedia entry marked "EXTINCT"
- Evolution event logged
- Achievement check

---

## 9. AI BEHAVIOR SYSTEM

### 9.1 Behavior Architecture
Creatures use a **Priority-Based State Machine**:

```
States: IDLE, HUNT, FLEE, EAT, SLEEP, EXPLORE, MIGRATE, REPRODUCE, DEFEND
```

Priority Resolution (each tick):
1. Is health critical? → FLEE (highest priority)
2. Is a predator nearby (within vision range)? → FLEE
3. Is hunger critical? → HUNT or EAT
4. Is a mate nearby AND reproduction cooldown ready? → REPRODUCE
5. Is territory being invaded? → DEFEND (if high territorial)
6. Is migration season? → MIGRATE (if high migration instinct)
7. Is energy low? → SLEEP
8. Default → EXPLORE or IDLE

### 9.2 Pathfinding
- Grid-based A* pathfinding (optimized with binary heap)
- Biome cost modifiers (swamp = slow, grassland = fast)
- Dynamic obstacle avoidance

### 9.3 Group Behavior
- **Herding:** Social > 6 → creatures aggregate, flee together, improved detection
- **Pack Hunting:** Intelligence > 7 AND Aggression > 6 → coordinate ambush
- **Migration Flocks:** Migration > 7 → synchronized seasonal movement

### 9.4 Predator/Prey Dynamics
**Pursuit Algorithm:**
- Predator tracks prey within vision cone
- Prey uses escape algorithm: move perpendicular then away
- Stamina degrades during chase
- Outcome probabilistic: strength ratio + stamina + random variance

**Ambush System:**
- Camouflage > 7 AND Intelligence > 5 → Ambush state
- Predator waits stationary until prey enters attack range
- Detection check for prey: vision vs camouflage

### 9.5 Territory System
- High territorial creatures establish a home range radius
- Intruders trigger defend behavior
- Multiple high-territorial species create contested zones (dynamic borders)

---

## 10. FOOD CHAIN SYSTEM

### 10.1 Trophic Architecture
```
Level 0: Abiotic Resources (Sunlight, Minerals, Water)
Level 1: Producers (Plants, Algae, Fungi)
Level 2: Primary Consumers (Herbivores)
Level 3: Secondary Consumers (Omnivores, Small Carnivores)
Level 4: Tertiary Consumers (Large Carnivores)
Level 5: Apex Predators
Level 6: Decomposers (Return nutrients to Level 0)
```

### 10.2 Trophic Cascade
If any level's population drops by >40%:
- **Bottom-up cascade:** Plant boom → herbivore boom → predator boom
- **Top-down cascade:** Apex removed → prey population explosion → plant collapse
- System automatically adjusts food availability per tile per tick

### 10.3 Energy Flow
- 10% efficiency rule: Only 10% of energy transfers between trophic levels
- Modifiable via gene "energy_efficiency"
- Creates inherent population ratio constraints

### 10.4 Decomposition
- Dead creatures leave nutrient markers on tiles
- Decomposers (fungi, bacteria — abstract) convert nutrients to plant food
- Scavengers gain food from corpses (high intelligence + opportunistic trait)

---

## 11. RESEARCH TREE SYSTEM

### 11.1 Research Points
- Earned by: Time passing + ecosystem milestones + achievements
- Bonus from: Stable food chains, evolution events, species diversity

### 11.2 Research Tree Structure
```
TIER 1 — Foundation
├── Basic Genetics          (cost: 100) → Unlock: Gene Lab basic traits
├── Ecosystem Observation   (cost: 100) → Unlock: Statistics Dashboard
└── Environmental Basics    (cost: 150) → Unlock: Biome info panel

TIER 2 — Applied Biology
├── Advanced Genetics       (cost: 300) → Unlock: Gene Lab advanced traits
│   └── Genetic Splicing    (cost: 500) → Unlock: Cross-species trait mixing
├── Behavioral Science      (cost: 250) → Unlock: Behavior trait editing
│   └── Neural Mapping      (cost: 400) → Unlock: Intelligence boost tools
└── Ecology                 (cost: 300) → Unlock: Food chain visualization

TIER 3 — Environmental Engineering
├── Climate Control         (cost: 600) → Unlock: Weather manipulation
│   ├── Terraforming        (cost: 800) → Unlock: Biome modification
│   └── Ice Age Trigger     (cost: 1000) → Unlock: Disaster: Ice Age
├── Resource Engineering    (cost: 500) → Unlock: Place/remove food sources
└── Disease Lab             (cost: 700) → Unlock: Targeted disease events

TIER 4 — Advanced Simulation
├── Genome Sequencing       (cost: 1500) → Unlock: Full genome view + edit
├── Synthetic Life          (cost: 2000) → Unlock: Create artificial organisms
└── Ecosystem Prediction    (cost: 1200) → Unlock: Future state modeling tool

TIER 5 — Mastery
├── Perfect Evolution        (cost: 3000) → Unlock: Guide evolution directly
├── Planet Architecture      (cost: 5000) → Unlock: Full biome control
└── Genesis Protocol         (cost: 8000) → Unlock: Reset and seed new world
```

### 11.3 Research UI
- Node-based visual tree with connecting lines
- Locked nodes: dark, grayed out with padlock icon
- Available nodes: highlighted border, pulsing glow
- Completed nodes: bright accent color, checkmark
- Tooltip on hover: description, cost, unlock effect

---

## 12. GENE LAB SYSTEM

### 12.1 Design Principles
The Gene Lab is the **flagship feature**. It must feel premium and scientific.

### 12.2 Species Creator Workflow
```
Step 1: Name Species + Select Base Template (or start from scratch)
Step 2: Set Classification (Herbivore / Omnivore / Carnivore / Apex)
Step 3: Adjust Physical Traits (sliders with real-time cost feedback)
Step 4: Adjust Behavioral Traits
Step 5: Adjust Genetic Traits (mutation rate, lifespan, etc.)
Step 6: Assign Biome Compatibility
Step 7: Preview: Evolutionary Pressure Analysis
Step 8: Cost Summary + Confirm Creation
```

### 12.3 Trait Sliders
Each trait has:
- Slider (0–10 range)
- Numeric value display
- Cost indicator (complex traits cost more research points)
- Tooltip: biological explanation + in-game effect
- Warning if trait combo is ecologically unstable

### 12.4 Stability Analysis
Before finalizing, the system runs a **compatibility check**:
- Energy cost vs reproduction rate (can they eat enough to sustain population?)
- Predator/prey role consistency (carnivores need prey available)
- Biome match (desert creature won't survive arctic)
- Warning level: Green / Yellow / Red

### 12.5 Gene Templates
Pre-built species templates (unlockable):
- Herbivore Starter, Fast Predator, Ambush Hunter, Colonial Insectoid, Aquatic Apex, etc.

---

## 13. DISASTER & EVENT SYSTEM

### 13.1 Natural Events (Random/Seasonal)
| Event | Trigger | Effect | Duration |
|---|---|---|---|
| Wildfire | Dry season + heat | Destroys vegetation, kills slow creatures | 3–10 ticks |
| Flood | High rainfall | Reduces land area, drowns land creatures | 5–15 ticks |
| Drought | Low rainfall | Reduces water/plant food | 10–30 ticks |
| Disease | High population density | Species-specific mortality | 5–20 ticks |
| Volcanic Eruption | Random / Rare | Mass extinction event, ash layer | 20–50 ticks |
| Ice Age | Climate drift | Temperature drops, biome shifts | 50–200 ticks |
| Meteor Strike | Ultra-rare | Massive area destruction | Instant + dust |

### 13.2 Player-Triggered Events
| Event | Cost | Effect |
|---|---|---|
| Controlled Mutation | 200 RP | Force mutation in target species |
| Environmental Shift | 300 RP | Change biome type in a zone |
| Population Control | 150 RP | Remove % of a species |
| Disease Release | 400 RP | Introduce targeted disease |
| Forced Migration | 100 RP | Displace species to new area |
| Food Injection | 50 RP | Add temporary food source |
| Species Introduction | 500 RP | Add new player-designed species |

### 13.3 Event Notification System
- On-screen event banner (non-blocking)
- Event logged to Event Timeline
- Camera can focus on event location (F key)
- Statistics update in real-time during event

---

## 14. STATISTICS & ANALYTICS SYSTEM

### 14.1 Real-Time Metrics
- Population per species (live count)
- Total species count
- Extinction events (cumulative)
- Evolution events (cumulative)
- Trophic balance ratio
- Biodiversity index (Shannon entropy of species distribution)
- Climate metrics (avg temperature, rainfall)

### 14.2 Graphs & Charts
| Chart | Type | X-Axis | Y-Axis |
|---|---|---|---|
| Population History | Line multi-series | Time (ticks) | Population |
| Trophic Distribution | Stacked bar | Trophic level | Biomass |
| Evolution Events | Timeline bar | Time | Event count |
| Extinction Map | Timeline | Time | Extinction count |
| Biodiversity | Line | Time | Shannon index |
| Climate | Dual-axis line | Time | Temp + Rainfall |

### 14.3 Species Encyclopedia
- Entry per species (auto-generated)
- Shows: Name, Traits, Population history, Biome, Trophic level, Status
- Extinct species shown with red EXTINCT badge
- Evolution tree showing species lineage

### 14.4 Evolution Event Log
Timestamped log of:
- Mutations above threshold
- Speciation events
- Extinction events
- Adaptation milestones
- Disaster impacts on species

---

## 15. ACHIEVEMENT SYSTEM

### 15.1 Achievement List

| ID | Name | Description | Category |
|---|---|---|---|
| ACH001 | First Breath | Release your first species | Foundation |
| ACH002 | Chain of Life | Build a complete 4-level food chain | Ecology |
| ACH003 | First Evolution | Observe a natural mutation event | Evolution |
| ACH004 | Adaptation | A species adapts a new trait under pressure | Evolution |
| ACH005 | Speciation | A new species branches from an existing one | Evolution |
| ACH006 | Extinction | Let a species go extinct | Evolution |
| ACH007 | Survival Master | A species survives 100 generations | Longevity |
| ACH008 | Biodiversity | Maintain 10+ species simultaneously | Ecology |
| ACH009 | Apex Creator | Create and sustain an Apex Predator | Genetics |
| ACH010 | Master Geneticist | Fully unlock the Gene Lab | Research |
| ACH011 | Disaster Survivor | A species survives a volcanic eruption | Survival |
| ACH012 | Planet Builder | Fill all 8 biomes with life | World |
| ACH013 | Ecosystem Architect | Maintain ecological balance for 500 ticks | Balance |
| ACH014 | Research Pioneer | Complete full research tree | Research |
| ACH015 | Genesis | Create a self-sustaining ecosystem | Mastery |
| ACH016 | Comeback Story | A species recovers from near-extinction | Drama |
| ACH017 | Pandemonium | Trigger 5 disasters in one session | Chaos |
| ACH018 | Perfect Biome | A biome reaches 100% ecological health | Excellence |
| ACH019 | Ancient Lineage | A species lasts 500+ generations | Longevity |
| ACH020 | Living Planet | Reach 50 simultaneous species | Mega |

---

## 16. CAMPAIGN MODE DESIGN

### Chapter 1: Birth of Life
**Objective:** Create 3 species and establish a basic food chain  
**Unlocks:** Basic Gene Lab, Basic Research Tree  
**Biome:** Grassland only  
**Challenges:** None — tutorial environment  
**Completion Condition:** Population > 100 total for 10 consecutive ticks

### Chapter 2: Survival Basics
**Objective:** Maintain a species for 50 generations  
**Unlocks:** Statistics Dashboard, Environmental panel  
**Biome:** Grassland + Forest  
**Challenges:** First seasonal drought introduced  
**Completion Condition:** One species completes 50 generations

### Chapter 3: Predator vs Prey
**Objective:** Build a stable predator/prey dynamic  
**Unlocks:** Food Chain visualization, Behavioral trait editing  
**Biome:** Grassland + Forest + Rivers  
**Challenges:** Predators introduced mid-chapter  
**Completion Condition:** Predator/prey ratio stable for 30 ticks

### Chapter 4: Climate Crisis
**Objective:** Help a species survive a climate event  
**Unlocks:** Climate monitoring, Environmental events panel  
**Biome:** All biomes introduced  
**Challenges:** Forced drought event, temperature shift  
**Completion Condition:** At least one species survives the event with mutation

### Chapter 5: Advanced Evolution
**Objective:** Trigger speciation 3 times  
**Unlocks:** Speciation monitoring, Advanced Genetics research  
**Biome:** Full world map  
**Challenges:** Competition pressure between species  
**Completion Condition:** 3 confirmed speciation events

### Chapter 6: Genetic Engineering
**Objective:** Design and sustain a synthetic organism  
**Unlocks:** Full Gene Lab, Genome Sequencing research  
**Biome:** Full world map  
**Challenges:** Synthetic species must outcompete a natural analog  
**Completion Condition:** Synthetic species reaches 50 population

### Chapter 7: Planet Management
**Objective:** Maintain all 8 biomes simultaneously with life  
**Unlocks:** Environmental Engineering tools, Biome modification  
**Biome:** All 8 required  
**Challenges:** Multiple simultaneous disasters  
**Completion Condition:** All 8 biomes have stable populations

### Final Chapter: Perfect Ecosystem
**Objective:** Achieve biodiversity index > 0.85 for 100 consecutive ticks  
**Unlocks:** Genesis Protocol (sandbox reward)  
**Biome:** Full world  
**Challenges:** Max disaster pressure, climate drift active  
**Completion Condition:** Shannon biodiversity index ≥ 0.85 sustained

---

## 17. SANDBOX MODE DESIGN

### Starting Options
| Option | Description |
|---|---|
| Empty World | Blank canvas, all tools available |
| Seeded World | Procedurally populated starter ecosystem |
| Custom Template | Player-saved world state as starting point |
| Challenge Seed | Specific world state with a survival challenge |

### Time Controls
| Control | Effect |
|---|---|
| Pause | Freeze simulation |
| 1× | Normal speed |
| 2× | 2x simulation speed |
| 5× | 5x simulation speed |
| 10× | 10x simulation speed (capped for stability) |

### God Mode Tools
- Place food sources anywhere
- Teleport species to any location
- Freeze a species (immune to death temporarily)
- Clone a species population
- Instant biome conversion

---

## 18. USER INTERFACE DESIGN

### 18.1 Design Language
- **Color Palette:** Dark mode — near-black backgrounds (#0D1117), accent green (#00FF88), accent blue (#00AAFF), warning amber (#FFAA00), danger red (#FF4444)
- **Typography:** Clean monospace for data, sans-serif for labels
- **Visual Feel:** Bioluminescent — glowing borders, pulsing indicators, clean data panels
- **Animations:** Smooth transitions, pulsing species dots, wave effects on water tiles

### 18.2 Screen Layout
```
┌─────────────────────────────────────────────────────────────┐
│  [GeneCraft Logo]  [Chapter/Mode]     [Clock] [Speed] [Menu]│  ← Top Bar (40px)
├──────────────────────────┬──────────────────────────────────┤
│                          │ ┌──────────────────────────────┐ │
│                          │ │   STATISTICS MINI PANEL       │ │
│     WORLD MAP /          │ │   Pop: 1,204 | Species: 12   │ │
│     ECOSYSTEM VIEW       │ │   Biodiversity: 0.73          │ │
│     (Main Viewport)      │ └──────────────────────────────┘ │
│                          │ ┌──────────────────────────────┐ │
│                          │ │   ACTIVE SPECIES LIST        │ │
│                          │ │   [Icon] Wolf Analog  (x82)  │ │
│                          │ │   [Icon] Deer Analog  (x245) │ │
│                          │ └──────────────────────────────┘ │
├──────────────────────────┴──────────────────────────────────┤
│  [Gene Lab] [Research] [Events] [Stats] [Encyclopedia] [Menu]│  ← Bottom Bar (50px)
└─────────────────────────────────────────────────────────────┘
```

### 18.3 Panel Designs

**Gene Lab Panel** — Slides in from left, 40% width overlay  
**Research Tree** — Full screen overlay, node-graph visualization  
**Statistics Dashboard** — Full screen overlay, multi-chart layout  
**Event Log** — Right-side slide-in panel  
**Encyclopedia** — Full screen overlay, scrollable species list  
**Settings** — Center modal  

### 18.4 HUD Elements
- Mini-map (bottom-right corner)
- Time display (current world tick / season / year)
- Research points counter (top bar)
- Active event banner (top center, auto-dismiss)
- Species health indicators on hover

---

## 19. AUDIO DESIGN

### 19.1 Audio Architecture
- Audio Manager singleton
- Channel separation: Music, Ambient, SFX, UI
- Volume controls per channel
- Graceful degradation if audio files missing

### 19.2 Music
| Track | Mood | When |
|---|---|---|
| main_theme | Epic, scientific | Main menu |
| ecosystem_ambient | Calm, alive | Simulation running (slow tick) |
| evolution_discovery | Wonder, ascending | Evolution event |
| crisis_mode | Tense | Disaster active |
| research_lab | Focus, electronic | Gene Lab / Research open |
| victory | Triumphant | Chapter completion |

### 19.3 Ambient Sounds
- Forest ambience (birds, wind, leaves)
- Grassland ambience (wind, insects)
- River/water ambience (water flow)
- Arctic ambience (wind, ice)
- Desert ambience (heat, distant calls)

### 19.4 SFX Events
- Evolution event (chime, ascending tone)
- Extinction (somber drop)
- Disaster trigger (sharp alert)
- Research unlock (satisfying pop)
- Species created (synthesizer bloom)
- Gene Lab interaction (click, slider move)
- Population milestone (notification)

### 19.5 Implementation
- Use `pygame.mixer` for all audio
- Procedurally generated sounds via math where no asset exists
- Synthesized tones as fallback for all events

---

## 20. SAVE SYSTEM DESIGN

### 20.1 Save Architecture
- **Format:** JSON (human-readable, version-tagged)
- **Location:** `saves/` directory
- **Auto-save:** Every 5 minutes + every chapter completion
- **Manual slots:** 5 named save slots
- **Quick save:** F5 / F9 quicksave/quickload

### 20.2 Save File Contents
```json
{
  "version": "1.0.0",
  "save_id": "uuid",
  "timestamp": "ISO datetime",
  "game_mode": "campaign|sandbox",
  "campaign_chapter": 3,
  "world_tick": 10482,
  "world_config": { ... },
  "species": [ ... full species list with genomes ... ],
  "population": { "species_id": count },
  "events_log": [ ... ],
  "research": { "unlocked": [], "points": 1250 },
  "achievements": [ ... ],
  "statistics_history": { ... },
  "world_state": { "biomes": [], "climate": {} }
}
```

### 20.3 Save Slot UI
- Slot name, timestamp, chapter/mode, world age, species count thumbnail
- "New Game," "Load," "Delete," "Rename" actions per slot

---

## 21. TECHNICAL ARCHITECTURE

### 21.1 Engine Architecture Pattern
**Pattern:** Entity-Component-System (ECS) hybrid with OOP layering

```
GameEngine (Singleton)
├── EventBus          ← Decoupled inter-system communication
├── SimulationEngine  ← Core tick loop, physics, AI dispatch
│   ├── EcosystemManager
│   ├── PopulationManager
│   ├── ClimateManager
│   └── FoodChainManager
├── GeneticsEngine    ← Genome processing, mutation, selection
│   ├── GenomeFactory
│   ├── MutationProcessor
│   └── SelectionAlgorithm
├── AIEngine          ← Creature behavior processing
│   ├── BehaviorStateMachine
│   ├── PathfindingSystem
│   └── GroupBehaviorSystem
├── WorldEngine       ← World state, biomes, terrain
│   ├── BiomeManager
│   ├── TerrainGenerator
│   └── ResourceManager
├── UIEngine          ← All UI rendering
│   ├── PanelManager
│   ├── WidgetSystem
│   └── AnimationSystem
├── ResearchSystem    ← Research tree, unlocks
├── DisasterSystem    ← Events, disasters
├── StatisticsSystem  ← Data collection, graphs
├── AchievementSystem ← Achievement tracking
├── SaveSystem        ← Serialization/deserialization
└── AudioSystem       ← Sound management
```

### 21.2 Update Loop
```
Main Loop (60 FPS target):
  ├── process_events()          ← Input, pygame events
  ├── simulation_tick()         ← Every N frames (configurable)
  │   ├── climate_update()
  │   ├── resource_update()
  │   ├── ai_update()           ← All creature decisions
  │   ├── movement_update()     ← Apply movements
  │   ├── interaction_update()  ← Predation, eating, reproduction
  │   ├── genetics_update()     ← Mutation, death, birth
  │   ├── disaster_update()     ← Active event processing
  │   └── statistics_update()   ← Metrics collection
  ├── render()                  ← Draw world + UI
  └── audio_update()            ← Music transitions, SFX queue
```

### 21.3 Configuration System
All game parameters in `config/settings.json`:
- Simulation speed tiers
- Max population per species
- Mutation rate bounds
- Biome parameters
- UI color palette
- Audio volumes
- Save paths

---

## 22. PROJECT STRUCTURE

```
GeneCraft/
├── main.py                     ← Entry point
├── requirements.txt            ← Python dependencies
├── config/
│   ├── settings.json           ← Game configuration
│   ├── biomes.json             ← Biome definitions
│   ├── genes.json              ← Gene definitions + ranges
│   ├── research_tree.json      ← Research tree data
│   └── achievements.json       ← Achievement definitions
├── assets/
│   ├── audio/
│   │   ├── music/
│   │   └── sfx/
│   ├── fonts/
│   ├── images/
│   │   ├── ui/
│   │   ├── creatures/
│   │   ├── biomes/
│   │   └── icons/
│   └── data/
│       └── species_templates.json
├── src/
│   ├── __init__.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── game_engine.py      ← Core engine singleton
│   │   ├── event_bus.py        ← Event system
│   │   └── config_manager.py  ← Config loading
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── simulation_engine.py
│   │   ├── ecosystem_manager.py
│   │   ├── population_manager.py
│   │   ├── climate_manager.py
│   │   └── food_chain_manager.py
│   ├── genetics/
│   │   ├── __init__.py
│   │   ├── genome.py           ← Genome data class
│   │   ├── genetics_engine.py  ← Selection, mutation
│   │   ├── genome_factory.py   ← Species template creation
│   │   └── mutation_processor.py
│   ├── species/
│   │   ├── __init__.py
│   │   ├── creature.py         ← Individual creature
│   │   ├── species.py          ← Species class
│   │   ├── life_stage.py       ← Life stage system
│   │   └── species_registry.py ← All active species
│   ├── world/
│   │   ├── __init__.py
│   │   ├── world.py            ← World state
│   │   ├── biome.py            ← Biome definitions
│   │   ├── terrain_generator.py
│   │   ├── tile.py             ← Individual world tile
│   │   └── resource_manager.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── behavior_fsm.py     ← Finite state machine
│   │   ├── pathfinding.py      ← A* pathfinding
│   │   └── group_behavior.py   ← Herd/pack behavior
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── research_system.py
│   │   ├── disaster_system.py
│   │   ├── statistics_system.py
│   │   ├── achievement_system.py
│   │   └── save_system.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── ui_engine.py        ← Main UI controller
│   │   ├── screens/
│   │   │   ├── main_menu.py
│   │   │   ├── game_screen.py
│   │   │   ├── campaign_select.py
│   │   │   └── save_screen.py
│   │   ├── panels/
│   │   │   ├── gene_lab_panel.py
│   │   │   ├── research_panel.py
│   │   │   ├── statistics_panel.py
│   │   │   ├── encyclopedia_panel.py
│   │   │   ├── event_log_panel.py
│   │   │   └── species_list_panel.py
│   │   ├── widgets/
│   │   │   ├── button.py
│   │   │   ├── slider.py
│   │   │   ├── tooltip.py
│   │   │   ├── panel.py
│   │   │   ├── graph.py
│   │   │   └── minimap.py
│   │   └── renderer/
│   │       ├── world_renderer.py
│   │       ├── creature_renderer.py
│   │       └── ui_renderer.py
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── audio_manager.py
│   │   └── sound_synthesizer.py  ← Procedural SFX
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py      ← SQLite interface
│   │   └── schema.sql
│   └── utils/
│       ├── __init__.py
│       ├── math_utils.py
│       ├── color_utils.py
│       ├── logger.py
│       └── profiler.py
├── saves/
│   └── .gitkeep
├── data/
│   └── campaign/
│       ├── chapter_01.json
│       ├── chapter_02.json
│       └── ...
├── docs/
│   ├── GDD.md                  ← This document
│   ├── README.md
│   ├── INSTALL.md
│   ├── USER_GUIDE.md
│   ├── DEV_GUIDE.md
│   └── ROADMAP.md
├── screenshots/
│   └── .gitkeep
└── README.md
```

---

## 23. DATA SCHEMAS

### 23.1 Species JSON Schema
```json
{
  "species_id": "uuid",
  "name": "String",
  "created_tick": 0,
  "trophic_level": 2,
  "biome_compatibility": ["forest", "grassland"],
  "genome": {
    "physical": {},
    "behavioral": {},
    "genetic": {},
    "metabolic": {}
  },
  "population": 0,
  "generation": 0,
  "ancestor_id": null,
  "status": "alive|extinct",
  "extinction_tick": null,
  "color": [r, g, b]
}
```

### 23.2 World Tile JSON Schema
```json
{
  "x": 0, "y": 0,
  "biome": "forest",
  "elevation": 0.5,
  "moisture": 0.7,
  "temperature": 20.0,
  "food_amount": 80,
  "food_capacity": 100,
  "occupants": ["creature_id_1", "creature_id_2"]
}
```

---

## 24. PERFORMANCE TARGETS

| Metric | Target | Critical Maximum |
|---|---|---|
| Frame Rate | 60 FPS | 30 FPS minimum |
| Simulation Tick | 100ms | 500ms maximum |
| Max Simultaneous Creatures | 5,000 | 2,000 minimum |
| Max Species | 50 | 25 minimum |
| Memory Usage | <512 MB | 1 GB maximum |
| Save File Size | <5 MB | 20 MB maximum |
| Load Time | <3 seconds | 10 seconds maximum |

### Optimization Strategies
- Spatial partitioning (grid cells) for creature queries
- Only update visible tiles in renderer
- Batch AI updates (not every creature every frame)
- LOD system: distant creatures = simplified behavior
- Object pooling for creature instances
- Numpy arrays for tile data where applicable

---

## 25. FUTURE ROADMAP

### v1.1 — Post-Launch Polish
- Steam achievements integration
- Controller support
- Additional biomes (Volcanic, Deep Ocean, Cloud Forest)
- 20 new species templates

### v1.2 — Content Expansion
- Additional campaign chapters (9–12)
- Challenge mode with leaderboards
- Photo mode (screenshot system)
- Species sharing via export/import JSON

### v2.0 — Major Expansion
- Multiplayer: Ecosystem comparison / planet exchange
- Procedural soundtrack (generative music system)
- Mod support (species JSON injection)
- Full Steam Workshop integration

### v3.0 — Platform Evolution
- Mobile port (touch-optimized UI)
- Cloud saves
- Cross-platform species sharing

---

## APPENDIX A — Gene Cost Table

| Trait | Min Cost | Max Cost | Notes |
|---|---|---|---|
| Speed | 10 RP | 100 RP | Expensive at high values |
| Size | 5 RP | 80 RP | Large size has food cost penalty |
| Strength | 8 RP | 90 RP | |
| Intelligence | 20 RP | 200 RP | Most expensive trait |
| Camouflage | 15 RP | 120 RP | |
| Reproduction Rate | 5 RP | 50 RP | High rate has population risk |
| Disease Resistance | 10 RP | 80 RP | |
| Lifespan | 5 RP | 100 RP | |

---

## APPENDIX B — Ecological Stability Metrics

| Metric | Healthy Range | Warning | Critical |
|---|---|---|---|
| Predator/Prey Ratio | 1:5 to 1:20 | 1:3 or 1:30 | 1:1 or 1:50+ |
| Trophic Coverage | 3–5 levels | 2 levels | 1 level only |
| Species Diversity | 0.6–0.9 | 0.4–0.6 | <0.4 |
| Food Availability | >50% | 20–50% | <20% |
| Population Variance | <30% swing | 30–50% | >50% |

---

*Document Version: 1.0.0 | GeneCraft Game Design Document | Classification: Development Internal*
*This GDD governs all development decisions. Any divergence must be approved and documented.*
