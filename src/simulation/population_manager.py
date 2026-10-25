"""
src/simulation/population_manager.py
======================================
PopulationManager — enforces population caps, manages spawning budgets,
and prevents single-species dominance.
"""
from __future__ import annotations
import logging
import random
from typing import Dict
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus

logger = logging.getLogger(__name__)


class PopulationManager:
    def __init__(self, config: ConfigManager, bus: EventBus) -> None:
        self.config = config
        self.bus = bus
        self.max_total      = config.get("simulation.max_creatures_total", 5000) or 5000
        self.max_per_species= config.get("simulation.max_creatures_per_species", 500) or 500
        logger.info("PopulationManager initialised (max=%d, per_sp=%d).",
                    self.max_total, self.max_per_species)

    def enforce_caps(self, registry, world_tick: int) -> int:
        """
        Cull excess creatures to stay within global population cap.
        Removes oldest/weakest individuals first.
        Returns number of creatures culled.
        """
        total = sum(s.population for s in registry.all_living())
        if total <= self.max_total:
            return 0

        culled = 0
        overage = total - self.max_total
        # Sort species by population descending — cull from most populous first
        living = sorted(registry.all_living(),
                        key=lambda s: s.population, reverse=True)
        for species in living:
            if overage <= 0:
                break
            if species.population <= 5:
                continue  # never cull below viable threshold
            # Cull up to half of overage from this species
            to_cull = min(overage, species.population // 4)
            # Mark weakest creatures as dead
            sorted_creatures = sorted(
                [c for c in species.creatures if c.is_alive],
                key=lambda c: c.energy + c.health
            )
            for c in sorted_creatures[:to_cull]:
                c.is_alive = False
                culled += 1
                overage -= 1
        if culled > 0:
            logger.debug("PopulationManager: culled %d creatures at tick %d.",
                         culled, world_tick)
        return culled

    def can_spawn(self, registry, species_id: str) -> bool:
        """Return True if a species is allowed to spawn more creatures."""
        total = sum(s.population for s in registry.all_living())
        if total >= self.max_total:
            return False
        sp = registry.get(species_id)
        if sp and sp.population >= self.max_per_species:
            return False
        return True
