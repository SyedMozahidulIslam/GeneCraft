"""
src/world/terrain_generator.py
================================
TerrainGenerator — produces elevation/moisture maps using Perlin noise
and applies river carving algorithms.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from utils.math_utils import PerlinNoise2D, clamp


class TerrainGenerator:
    """
    Generates 2D elevation and moisture grids for world creation.

    Usage
    -----
    gen = TerrainGenerator(seed=42)
    elev_map  = gen.elevation(width=200, height=200)
    moist_map = gen.moisture(width=200, height=200)
    rivers    = gen.rivers(elev_map, attempts=20)
    """

    def __init__(self, seed: int = 0) -> None:
        self.seed         = seed
        self._elev_noise  = PerlinNoise2D(seed=seed)
        self._moist_noise = PerlinNoise2D(seed=seed + 1000)
        self._rng         = random.Random(seed)

    def elevation(self, width: int, height: int,
                  scale: float = 0.008, octaves: int = 6) -> List[List[float]]:
        """Return width×height grid of elevation values in [0, 1]."""
        return [
            [self._elev_noise.octaves(x, y, octaves=octaves, scale=scale)
             for x in range(width)]
            for y in range(height)
        ]

    def moisture(self, width: int, height: int,
                 scale: float = 0.012, octaves: int = 4) -> List[List[float]]:
        """Return width×height grid of moisture values in [0, 1]."""
        return [
            [self._moist_noise.octaves(x, y, octaves=octaves, scale=scale)
             for x in range(width)]
            for y in range(height)
        ]

    def rivers(
        self,
        elev_map: List[List[float]],
        attempts: int = 20,
        min_length: int = 20,
        max_length: int = 80,
    ) -> List[List[Tuple[int, int]]]:
        """
        Generate river paths flowing downhill from high-elevation starting points.
        Returns a list of river paths, each a list of (x, y) tile coordinates.
        """
        height = len(elev_map)
        width  = len(elev_map[0]) if height > 0 else 0
        rivers = []

        # Candidate start points: high elevation tiles (mountains)
        high_tiles = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if elev_map[y][x] >= 0.65
        ]
        if not high_tiles:
            return rivers

        for _ in range(attempts):
            sx, sy = self._rng.choice(high_tiles)
            path   = []
            x, y   = float(sx), float(sy)
            length = self._rng.randint(min_length, max_length)

            for step in range(length):
                ix, iy = int(x), int(y)
                if not (0 <= ix < width and 0 <= iy < height):
                    break
                # Stop if we hit existing water (elevation very low)
                if elev_map[iy][ix] < 0.22:
                    break
                path.append((ix, iy))
                # Flow with slight downhill bias + random wander
                x += self._rng.uniform(-1.0, 1.0)
                y += self._rng.uniform(0.3, 1.8)

            if len(path) >= min_length // 2:
                rivers.append(path)

        return rivers
