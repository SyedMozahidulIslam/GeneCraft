"""
src/simulation/ecosystem_manager.py
=====================================
EcosystemManager — tracks overall ecosystem health, trophic balance,
food chain integrity, and biodiversity metrics each tick.
"""
from __future__ import annotations
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from engine.event_bus import EventBus
from engine.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class EcosystemManager:
    """
    Aggregates ecosystem-level metrics not tracked by individual systems.
    Detects trophic cascades, food chain collapse, and ecological balance.
    """

    def __init__(self, config: ConfigManager, bus: EventBus) -> None:
        self.config = config
        self.bus    = bus
        # Trophic population snapshot: {trophic_level: population}
        self.trophic_snapshot: Dict[int, int] = {}
        # Historical ratios for cascade detection
        self._prev_snapshot: Dict[int, int] = {}
        # Cascade detection threshold (40% swing triggers event)
        self._cascade_threshold = 0.40
        self._tick = 0
        logger.info("EcosystemManager initialised.")

    def tick(self, registry, world_tick: int) -> None:
        """Update ecosystem metrics from current species registry state."""
        self._tick = world_tick
        self._prev_snapshot = dict(self.trophic_snapshot)
        self.trophic_snapshot.clear()

        for species in registry.all_living():
            lvl = species.trophic_level
            self.trophic_snapshot[lvl] = \
                self.trophic_snapshot.get(lvl, 0) + species.population

        self._detect_cascade(world_tick)

    def _detect_cascade(self, tick: int) -> None:
        if not self._prev_snapshot:
            return
        for level, prev_pop in self._prev_snapshot.items():
            curr_pop = self.trophic_snapshot.get(level, 0)
            if prev_pop == 0:
                continue
            change = abs(curr_pop - prev_pop) / prev_pop
            if change >= self._cascade_threshold:
                direction = "collapse" if curr_pop < prev_pop else "explosion"
                logger.info(
                    "EcosystemManager: trophic cascade detected at level %d "
                    "(%s, %.0f%% change)", level, direction, change * 100)
                self.bus.queue("ecosystem:trophic_cascade", {
                    "level":     level,
                    "direction": direction,
                    "prev_pop":  prev_pop,
                    "curr_pop":  curr_pop,
                    "tick":      tick,
                })

    def health_score(self) -> float:
        """Return overall ecosystem health 0–1."""
        if not self.trophic_snapshot:
            return 0.0
        # Need at least producers + consumers
        has_base = self.trophic_snapshot.get(1, 0) + self.trophic_snapshot.get(2, 0) > 0
        has_cons = any(self.trophic_snapshot.get(l, 0) > 0 for l in (3, 4, 5))
        levels_filled = sum(1 for l in (1,2,3,4,5) if self.trophic_snapshot.get(l, 0) > 0)
        structure = levels_filled / 5.0
        return round(0.6 * structure + 0.4 * (1.0 if has_base and has_cons else 0.3), 3)

    def trophic_balance_ratio(self) -> float:
        """Return predator-to-prey ratio. Healthy: 0.05–0.20."""
        prey = self.trophic_snapshot.get(2, 0)
        pred = sum(self.trophic_snapshot.get(l, 0) for l in (3, 4, 5))
        if prey == 0:
            return 0.0
        return round(pred / prey, 4)

    def serialise(self) -> dict:
        return {"trophic_snapshot": self.trophic_snapshot}

    def deserialise(self, data: dict) -> None:
        self.trophic_snapshot = data.get("trophic_snapshot", {})
