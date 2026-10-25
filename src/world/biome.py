"""
src/world/biome.py
===================
Biome data container and helper functions.
Loads biome definitions from config and provides typed access.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class BiomeClimate:
    temp_min:     float = 0.0
    temp_max:     float = 30.0
    temp_avg:     float = 15.0
    moisture_min: float = 0.2
    moisture_max: float = 0.8
    moisture_avg: float = 0.5


@dataclass
class Biome:
    """Typed container for a biome definition loaded from biomes.json."""
    id:           str
    name:         str
    color_base:   Tuple[int, int, int] = (80, 120, 60)
    climate:      BiomeClimate         = field(default_factory=BiomeClimate)
    food_capacity:float                = 60.0
    food_regen:   float                = 1.0
    movement_cost:float                = 1.0
    visibility:   float                = 1.0
    biome_pressure: Dict[str, float]   = field(default_factory=dict)
    seasonal_modifier: Dict[str, float]= field(default_factory=dict)

    @classmethod
    def from_dict(cls, biome_id: str, d: dict) -> "Biome":
        climate_d = d.get("climate", {})
        food_d    = d.get("food",    {})
        terrain_d = d.get("terrain", {})
        color_raw = d.get("color_base", [80, 120, 60])
        return cls(
            id            = biome_id,
            name          = d.get("name", biome_id.title()),
            color_base    = tuple(color_raw),
            climate       = BiomeClimate(
                temp_min     = climate_d.get("temp_min",     0.0),
                temp_max     = climate_d.get("temp_max",     30.0),
                temp_avg     = climate_d.get("temp_avg",     15.0),
                moisture_min = climate_d.get("moisture_min", 0.2),
                moisture_max = climate_d.get("moisture_max", 0.8),
                moisture_avg = climate_d.get("moisture_avg", 0.5),
            ),
            food_capacity  = food_d.get("plant_capacity",      60.0),
            food_regen     = food_d.get("plant_regen_rate",     1.0),
            movement_cost  = terrain_d.get("movement_cost",    1.0),
            visibility     = terrain_d.get("visibility_range", 1.0),
            biome_pressure = d.get("biome_pressure", {}),
            seasonal_modifier = food_d.get("seasonal_modifier", {}),
        )

    def is_aquatic(self) -> bool:
        return self.id in ("river", "lake")

    def season_food_modifier(self, season: str) -> float:
        return self.seasonal_modifier.get(season, 1.0)

    def temp_at_season(self, season: str) -> float:
        offsets = {"spring": 2.0, "summer": 8.0, "autumn": -2.0, "winter": -12.0}
        return self.climate.temp_avg + offsets.get(season, 0.0)


class BiomeRegistry:
    """Loads and provides typed Biome objects from config."""

    def __init__(self) -> None:
        self._biomes: Dict[str, Biome] = {}

    def load_from_config(self, config) -> None:
        raw = config.get_section("biomes")
        for biome_id, data in raw.items():
            if isinstance(data, dict):
                self._biomes[biome_id] = Biome.from_dict(biome_id, data)

    def get(self, biome_id: str) -> Optional[Biome]:
        return self._biomes.get(biome_id)

    def all_ids(self) -> List[str]:
        return list(self._biomes.keys())

    def __len__(self) -> int:
        return len(self._biomes)
