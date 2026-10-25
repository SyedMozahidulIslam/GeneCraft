"""
src/simulation/climate_manager.py
===================================
ClimateManager — manages world-level climate state, seasonal transitions,
and applies temperature/weather effects to biomes.
"""
from __future__ import annotations
import logging
import random
import math
from typing import Dict, Optional
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus

logger = logging.getLogger(__name__)

_SEASON_TEMPS: Dict[str, float] = {
    "spring": 0.0, "summer": 8.0, "autumn": -2.0, "winter": -15.0
}


class ClimateManager:
    def __init__(self, config: ConfigManager, bus: EventBus) -> None:
        self.config = config
        self.bus    = bus
        self.season         = "spring"
        self.year           = 1
        self.day_of_year    = 1
        self.global_temp    = 15.0          # baseline °C
        self.temp_drift     = 0.0           # long-term drift
        self.rainfall       = 1.0           # multiplier
        self._ticks_per_season = config.get("simulation.ticks_per_season", 91) or 91
        logger.info("ClimateManager initialised.")

    def tick(self, world_tick: int) -> None:
        self.day_of_year = (world_tick % 365) + 1
        season_idx = (world_tick // self._ticks_per_season) % 4
        seasons    = ["spring", "summer", "autumn", "winter"]
        new_season = seasons[season_idx]

        if new_season != self.season:
            old = self.season
            self.season = new_season
            self.bus.queue("climate:season_change", {
                "old": old, "new": new_season,
                "year": self.year, "tick": world_tick,
            })
            if new_season == "spring":
                self.year += 1

        # Gentle long-term drift
        if world_tick % 1000 == 0 and world_tick > 0:
            self.temp_drift += random.gauss(0, 0.5)
            self.temp_drift  = max(-12.0, min(12.0, self.temp_drift))

        # Dynamic rainfall (sinusoidal + noise)
        base_rain   = 0.5 + 0.5 * math.sin(math.radians(self.day_of_year * 360 / 365))
        self.rainfall = max(0.1, base_rain + random.gauss(0, 0.05))

    @property
    def effective_temp(self) -> float:
        return self.global_temp + _SEASON_TEMPS.get(self.season, 0.0) + self.temp_drift

    @property
    def food_modifier(self) -> float:
        return {"spring": 1.3, "summer": 1.0, "autumn": 0.8, "winter": 0.2
                }.get(self.season, 1.0)

    def serialise(self) -> dict:
        return {"season": self.season, "year": self.year,
                "global_temp": self.global_temp, "temp_drift": self.temp_drift}

    def deserialise(self, data: dict) -> None:
        self.season      = data.get("season",      "spring")
        self.year        = data.get("year",         1)
        self.global_temp = data.get("global_temp",  15.0)
        self.temp_drift  = data.get("temp_drift",   0.0)
