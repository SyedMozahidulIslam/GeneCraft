"""
src/simulation/food_chain_manager.py
======================================
FoodChainManager — models trophic energy flow and detects ecological
imbalances across the food chain.
"""
from __future__ import annotations
import logging
from typing import Dict, List, Tuple
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus

logger = logging.getLogger(__name__)

# Energy transfer efficiency between trophic levels (10% rule)
TROPHIC_EFFICIENCY = 0.10


class FoodChainManager:
    def __init__(self, config: ConfigManager, bus: EventBus) -> None:
        self.config = config
        self.bus    = bus
        # {trophic_level: total_biomass_this_tick}
        self.biomass: Dict[int, float] = {}
        self._tick = 0
        logger.info("FoodChainManager initialised.")

    def tick(self, registry, world_tick: int) -> None:
        self._tick = world_tick
        self.biomass.clear()

        for species in registry.all_living():
            lvl = species.trophic_level
            # Biomass proxy: population × average body size
            avg_size = (species.representative_genome.physical.size
                        if species.genome_pool else 1.0)
            self.biomass[lvl] = self.biomass.get(lvl, 0.0) + species.population * avg_size

        self._check_imbalances(world_tick)

    def _check_imbalances(self, tick: int) -> None:
        """Emit events when trophic ratios are ecologically unstable."""
        prey_biomass = self.biomass.get(2, 0)
        pred_biomass = sum(self.biomass.get(l, 0) for l in (3, 4, 5))

        if prey_biomass > 0 and pred_biomass > 0:
            ratio = pred_biomass / prey_biomass
            # Healthy: 0.02–0.15 (10% efficiency rule)
            if ratio > 0.4:
                self.bus.queue("food_chain:overpredation", {
                    "ratio": ratio, "tick": tick,
                    "message": "Predator biomass critically high — prey collapse risk",
                })
            elif ratio < 0.005 and pred_biomass > 0:
                self.bus.queue("food_chain:underpredation", {
                    "ratio": ratio, "tick": tick,
                    "message": "Prey explosion — predator population too low",
                })

    def energy_at_level(self, trophic_level: int) -> float:
        """Available energy at a trophic level based on biomass below it."""
        lower = self.biomass.get(trophic_level - 1, 0.0)
        return lower * TROPHIC_EFFICIENCY

    def food_web_summary(self) -> List[Tuple[int, float]]:
        return sorted(self.biomass.items())

    def serialise(self) -> dict:
        return {"biomass": self.biomass}

    def deserialise(self, data: dict) -> None:
        self.biomass = data.get("biomass", {})
