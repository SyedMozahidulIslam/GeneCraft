"""
src/world/tile.py
=================
Tile — a single cell in the world grid.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

@dataclass
class Tile:
    grid_x:       int   = 0
    grid_y:       int   = 0
    biome:        str   = "grassland"
    elevation:    float = 0.3
    moisture:     float = 0.5
    temperature:  float = 18.0
    is_water:     bool  = False
    is_passable:  bool  = True
    food_amount:  float = 50.0
    food_capacity:float = 100.0
    food_regen_rate:float = 1.0
    nutrient_level:float = 0.0
    creature_ids: List[str] = field(default_factory=list)
    color_base:   tuple = (80, 120, 60)
    color_var:    float = 0.0

    # ── Food ──────────────────────────────────────────────────────────────
    def regen_food(self, season_modifier: float = 1.0) -> None:
        if self.is_water:
            return
        regen = self.food_regen_rate * season_modifier + self.nutrient_level * 0.1
        self.food_amount = min(self.food_capacity, self.food_amount + regen)
        self.nutrient_level = max(0.0, self.nutrient_level - 0.05)

    def consume_food(self, amount: float) -> float:
        consumed = min(self.food_amount, max(0.0, amount))
        self.food_amount -= consumed
        return consumed

    def add_nutrient(self, amount: float) -> None:
        self.nutrient_level = min(10.0, self.nutrient_level + amount)

    @property
    def food_ratio(self) -> float:
        return self.food_amount / self.food_capacity if self.food_capacity > 0 else 0.0

    @property
    def is_fertile(self) -> bool:
        return self.food_ratio > 0.3 and not self.is_water

    # ── Occupants ─────────────────────────────────────────────────────────
    def add_creature(self, creature_id: str) -> None:
        if creature_id not in self.creature_ids:
            self.creature_ids.append(creature_id)

    def remove_creature(self, creature_id: str) -> None:
        if creature_id in self.creature_ids:
            self.creature_ids.remove(creature_id)

    @property
    def occupant_count(self) -> int:
        return len(self.creature_ids)

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "grid_x": self.grid_x, "grid_y": self.grid_y,
            "biome": self.biome, "elevation": self.elevation,
            "moisture": self.moisture, "temperature": self.temperature,
            "is_water": self.is_water, "is_passable": self.is_passable,
            "food_amount": self.food_amount, "food_capacity": self.food_capacity,
            "food_regen_rate": self.food_regen_rate,
            "nutrient_level": self.nutrient_level,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Tile":
        return cls(
            grid_x=d.get("grid_x", 0), grid_y=d.get("grid_y", 0),
            biome=d.get("biome", "grassland"),
            elevation=d.get("elevation", 0.3), moisture=d.get("moisture", 0.5),
            temperature=d.get("temperature", 18.0),
            is_water=d.get("is_water", False), is_passable=d.get("is_passable", True),
            food_amount=d.get("food_amount", 50.0),
            food_capacity=d.get("food_capacity", 100.0),
            food_regen_rate=d.get("food_regen_rate", 1.0),
            nutrient_level=d.get("nutrient_level", 0.0),
        )

    def __repr__(self) -> str:
        return (f"Tile({self.grid_x},{self.grid_y}, biome={self.biome}, "
                f"food={self.food_amount:.0f}/{self.food_capacity:.0f}, "
                f"occupants={self.occupant_count})")
