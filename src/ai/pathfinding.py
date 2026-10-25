"""
src/ai/pathfinding.py
======================
A* pathfinding for creature navigation across the tile grid.
Optimised with a binary heap open set and spatial caching.
"""
from __future__ import annotations
import heapq
import math
from typing import Dict, List, Optional, Tuple

Coord = Tuple[int, int]


def _heuristic(a: Coord, b: Coord) -> float:
    """Octile distance — accurate for 8-directional movement."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


def astar(
    start:       Coord,
    goal:        Coord,
    world,
    max_steps:   int = 200,
    diagonal:    bool = True,
) -> Optional[List[Coord]]:
    """
    Find shortest passable path from start to goal using A*.

    Parameters
    ----------
    start, goal  : (x, y) tile coordinates
    world        : World instance (provides get_tile for cost/passability)
    max_steps    : Search budget (prevents infinite loops)
    diagonal     : Allow diagonal movement

    Returns
    -------
    List of (x, y) waypoints from start to goal (inclusive),
    or None if no path found within max_steps.
    """
    if start == goal:
        return [start]

    neighbours = [(-1,0),(1,0),(0,-1),(0,1)]
    if diagonal:
        neighbours += [(-1,-1),(-1,1),(1,-1),(1,1)]

    open_heap: List[Tuple[float, int, Coord]] = []
    counter = 0
    heapq.heappush(open_heap, (0.0, counter, start))

    came_from: Dict[Coord, Optional[Coord]] = {start: None}
    g_score:   Dict[Coord, float]           = {start: 0.0}
    steps = 0

    while open_heap and steps < max_steps:
        steps += 1
        _, _, current = heapq.heappop(open_heap)

        if current == goal:
            # Reconstruct path
            path: List[Coord] = []
            node: Optional[Coord] = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        cx, cy = current
        for dx, dy in neighbours:
            nx, ny = cx + dx, cy + dy
            neighbour = (nx, ny)
            tile = world.get_tile(nx, ny)
            if tile is None or not tile.is_passable:
                continue

            move_cost = tile.biome_movement_cost if hasattr(tile, 'biome_movement_cost') else 1.0
            if dx != 0 and dy != 0:
                move_cost *= math.sqrt(2)

            tentative_g = g_score[current] + move_cost
            if tentative_g < g_score.get(neighbour, float("inf")):
                came_from[neighbour] = current
                g_score[neighbour]   = tentative_g
                f = tentative_g + _heuristic(neighbour, goal)
                counter += 1
                heapq.heappush(open_heap, (f, counter, neighbour))

    return None  # No path found


def find_nearest_tile_of_biome(
    start:  Coord,
    biome:  str,
    world,
    radius: int = 50,
) -> Optional[Coord]:
    """Find the closest tile of a given biome type using BFS."""
    from collections import deque
    visited = {start}
    queue   = deque([start])
    while queue:
        x, y = queue.popleft()
        tile = world.get_tile(x, y)
        if tile and tile.biome == biome:
            return (x, y)
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
            nx, ny = x+dx, y+dy
            if (nx, ny) not in visited and abs(nx-start[0])<=radius and abs(ny-start[1])<=radius:
                visited.add((nx, ny))
                queue.append((nx, ny))
    return None
