# GeneCraft — Developer Guide

## Architecture Overview

GeneCraft uses a **ECS-hybrid + OOP** architecture with a central **EventBus**
for decoupled inter-system communication.

```
GameEngine (Singleton)
├── EventBus              ← All inter-system messaging
├── SimulationEngine      ← Master tick coordinator
│   ├── World             ← Tile grid, biomes, terrain
│   ├── GeneticsEngine    ← Natural selection, mutation
│   ├── BehaviorFSM       ← Creature AI state machine
│   └── SpeciesRegistry   ← All species management
├── EcosystemManager      ← Trophic balance, cascade detection
├── PopulationManager     ← Cap enforcement
├── ClimateManager        ← Season, weather, drift
├── FoodChainManager      ← Energy flow, trophic ratios
├── ResearchSystem        ← Research tree, RP economy
├── DisasterSystem        ← Event lifecycle
├── StatisticsSystem      ← Metrics, graphs
├── AchievementSystem     ← Unlock tracking
├── SaveSystem            ← JSON persistence
└── UIEngine              ← Rendering, panels, overlays
```

## Key Design Patterns

### EventBus (Pub/Sub)
All systems communicate via events. No direct cross-system references.

```python
# Publishing an event
bus.queue("species:extinct", {"species_id": sid, "cause": "starvation"})

# Subscribing
bus.subscribe("species:extinct", self._handle_extinction)
```

### Genome Data Class
Each creature has a `Genome` with 4 categories of genes.
Genes are accessed by flat name across all categories:

```python
genome.get("speed")           # → float
genome.set("speed", 7.5)      # clamped to valid range
genome.all_genes()            # → {name: value} flat dict
child = g1.crossover(g2)      # inheritance + mutation
```

### Natural Selection Loop (every `fitness_eval_interval` ticks)
```
for each living species:
    score each genome in pool by fitness_score()
    cull bottom 30%
    reproduce top 70% × food_ratio
    apply mutation
    check adaptation events
    check speciation
    check extinction
```

## Adding a New Gene

1. Add to `_GENE_RANGES` in `src/genetics/genome.py`
2. Add field to the appropriate `@dataclass` (Physical/Behavioral/Genetic/Metabolic)
3. Add entry to `config/genes.json` under the correct category
4. Gene automatically participates in crossover, mutation, and fitness scoring

## Adding a New Biome

1. Add entry to `config/biomes.json` with all required fields
2. Add to `_BIOME_MATRIX` in `src/world/world.py` (elev/moisture thresholds)
3. Add color to `_BIOME_COLORS` in `src/world/world.py`
4. Add to `_BIOME_TEMPS`, `_BIOME_FOOD_CAP`, `_BIOME_REGEN` dicts

## Adding a New Research Node

1. Add node entry to `config/research_tree.json` in the appropriate tier
2. Define `prerequisites`, `cost`, `unlocks` dict
3. The `ResearchSystem` automatically loads and serves it
4. Check `is_unlocked("node_id")` in relevant systems

## Adding a New Achievement

1. Add entry to `config/achievements.json`
2. Add condition check to `AchievementSystem._check_all()` or call
   `ach.check("ACH_ID")` from the appropriate system event handler

## Running Tests

```bash
cd GeneCraft
python -m pytest tests/          # (if test suite added)
# Or run the built-in integration test:
python tests/integration_test.py
```

## Debug Mode

```bash
python main.py --debug
```

Enables:
- Verbose logging to `logs/genecraft.log`
- FPS counter in top bar
- Extended simulation statistics

## Performance Profiling

```bash
python main.py --profile
```

Uses `src/utils/profiler.py` to time each simulation sub-system.
Report logged at session end.

## Project Structure Quick Reference

```
src/
├── engine/          GameEngine, EventBus, ConfigManager
├── genetics/        Genome, GeneticsEngine, GenomeFactory, MutationProcessor
├── species/         Creature, Species, SpeciesRegistry, LifeStage
├── world/           World, Tile, Biome, TerrainGenerator, ResourceManager
├── ai/              BehaviorFSM, Pathfinding, GroupBehavior
├── simulation/      SimulationEngine, EcosystemManager, PopulationManager,
│                    ClimateManager, FoodChainManager
├── systems/         Research, Disasters, Statistics, Achievements, Save
├── ui/              UIEngine, WorldRenderer, CreatureRenderer, UIRenderer
├── audio/           AudioManager
├── database/        DBManager, schema.sql
└── utils/           Math, Colors, Logger, Profiler
```
