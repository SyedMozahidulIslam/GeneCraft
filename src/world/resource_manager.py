"""
src/world/resource_manager.py
================================
ResourceManager — manages global resource pools (food, water) across
the world and handles resource injection/removal by player actions.
"""
from __future__ import annotations
import logging
import random
from typing import Dict, List, Optional, Tuple
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Tracks global resource availability and lets the player
    inject or remove resources as a god-mode action.
    """

    def __init__(self, config: ConfigManager, bus: EventBus) -> None:
        self.config = config
        self.bus    = bus
        # List of player-placed food sources: [(x, y, amount, radius)]
        self._food_sources:  List[Tuple[int,int,float,int]] = []
        self._water_sources: List[Tuple[int,int,int]]       = []
        logger.info("ResourceManager initialised.")

    def add_food_source(self, world, cx: int, cy: int,
                        amount: float = 500.0, radius: int = 5) -> int:
        """Place a concentrated food source on the map. Returns tiles affected."""
        count = 0
        for tile in world.tiles_in_radius(cx, cy, radius):
            bonus = amount * (1.0 - (abs(tile.grid_x - cx) + abs(tile.grid_y - cy))
                              / max(1, radius * 2))
            tile.food_amount = min(tile.food_capacity,
                                   tile.food_amount + bonus)
            count += 1
        self._food_sources.append((cx, cy, amount, radius))
        logger.info("ResourceManager: food source placed at (%d,%d), %d tiles affected.",
                    cx, cy, count)
        self.bus.queue("resource:food_added", {"x": cx, "y": cy, "amount": amount})
        return count

    def remove_food_source(self, world, cx: int, cy: int, radius: int = 5) -> int:
        """Drain food from an area (simulate drought or resource depletion)."""
        count = 0
        for tile in world.tiles_in_radius(cx, cy, radius):
            tile.food_amount = max(0.0, tile.food_amount * 0.1)
            count += 1
        logger.info("ResourceManager: food removed around (%d,%d).", cx, cy)
        self.bus.queue("resource:food_removed", {"x": cx, "y": cy})
        return count

    def add_water_source(self, world, cx: int, cy: int, radius: int = 3) -> int:
        """Convert dry tiles to water-adjacent for hydration purposes."""
        count = 0
        for tile in world.tiles_in_radius(cx, cy, radius):
            tile.moisture = min(1.0, tile.moisture + 0.3)
            count += 1
        self._water_sources.append((cx, cy, radius))
        self.bus.queue("resource:water_added", {"x": cx, "y": cy})
        return count

    def tick(self, world_tick: int) -> None:
        """Periodic restock of player-placed sources."""
        if world_tick % 50 == 0:
            pass  # Future: decay player-placed sources
