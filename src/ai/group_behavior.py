"""
src/ai/group_behavior.py
==========================
GroupBehavior — manages herd/pack formation and coordinated behaviours
for social species (social_behavior > 6).
"""
from __future__ import annotations
import logging
import random
import uuid
from typing import Dict, List, Optional, Set
from species.creature import BehaviorState, Creature, LifeStage

logger = logging.getLogger(__name__)

_HERD_FORMATION_THRESHOLD  = 6.0
_PACK_HUNTING_THRESHOLD    = 7.0
_PACK_INTEL_THRESHOLD      = 7.0
_MIN_GROUP_SIZE            = 3
_MAX_GROUP_SIZE            = 30


class Group:
    """A collection of creatures acting in a coordinated way."""
    __slots__ = ("group_id", "species_id", "member_ids", "mode",
                 "target_x", "target_y", "target_creature_id")

    def __init__(self, species_id: str, mode: str = "herd") -> None:
        self.group_id          = str(uuid.uuid4())[:8]
        self.species_id        = species_id
        self.member_ids:  Set[str] = set()
        self.mode              = mode   # "herd" | "pack"
        self.target_x:    Optional[float] = None
        self.target_y:    Optional[float] = None
        self.target_creature_id: Optional[str] = None

    def add(self, creature_id: str) -> None:
        self.member_ids.add(creature_id)

    def remove(self, creature_id: str) -> None:
        self.member_ids.discard(creature_id)

    @property
    def size(self) -> int:
        return len(self.member_ids)


class GroupBehaviorSystem:
    """
    Manages group formation and applies coordinated behaviors.
    Called once per tick from SimulationEngine.
    """

    def __init__(self) -> None:
        self._groups: Dict[str, Group] = {}  # group_id → Group
        logger.info("GroupBehaviorSystem initialised.")

    def tick(
        self,
        creature_map: Dict[str, Creature],
        species_registry,
        world_tick: int,
    ) -> None:
        # Refresh groups
        self._disband_empty_groups(creature_map)
        self._form_groups(creature_map, species_registry)
        self._apply_group_behaviors(creature_map)

    def _form_groups(self, creature_map, registry) -> None:
        for species in registry.all_living():
            genome = species.representative_genome
            social = genome.behavioral.social_behavior
            intel  = genome.behavioral.intelligence

            if social < _HERD_FORMATION_THRESHOLD:
                continue

            # Collect ungrouped adult creatures of this species
            ungrouped = [
                c for c in species.creatures
                if c.is_alive and c.in_group is False
                and c.life_stage == LifeStage.ADULT
            ]
            if len(ungrouped) < _MIN_GROUP_SIZE:
                continue

            # Determine group mode
            mode = "pack" if (intel >= _PACK_INTEL_THRESHOLD
                              and genome.behavioral.aggression >= 5.0) else "herd"

            # Form a new group
            group = Group(species_id=species.species_id, mode=mode)
            for c in ungrouped[:_MAX_GROUP_SIZE]:
                group.add(c.creature_id)
                c.in_group  = True
                c.group_id  = group.group_id
            self._groups[group.group_id] = group

    def _apply_group_behaviors(self, creature_map: Dict[str, Creature]) -> None:
        for group in self._groups.values():
            if group.mode == "herd":
                self._herd_cohesion(group, creature_map)
            elif group.mode == "pack":
                self._pack_hunt_coordination(group, creature_map)

    def _herd_cohesion(self, group: Group, creature_map: Dict[str, Creature]) -> None:
        """Move scattered herd members toward the group centroid."""
        members = [creature_map[cid] for cid in group.member_ids
                   if cid in creature_map and creature_map[cid].is_alive]
        if len(members) < 2:
            return
        cx = sum(c.x for c in members) / len(members)
        cy = sum(c.y for c in members) / len(members)
        # Stragglers (far from centroid) redirect toward it
        for c in members:
            dist = ((c.x-cx)**2 + (c.y-cy)**2) ** 0.5
            if dist > 15.0 and c.behavior == BehaviorState.EXPLORE:
                c.behavior  = BehaviorState.EXPLORE
                c.target_x  = cx + random.uniform(-3, 3)
                c.target_y  = cy + random.uniform(-3, 3)

    def _pack_hunt_coordination(self, group: Group, creature_map) -> None:
        """Point all pack members toward the same prey target."""
        if group.target_creature_id and group.target_creature_id in creature_map:
            prey = creature_map[group.target_creature_id]
            if prey.is_alive:
                for cid in group.member_ids:
                    c = creature_map.get(cid)
                    if c and c.is_alive and c.behavior == BehaviorState.EXPLORE:
                        c.behavior         = BehaviorState.HUNT
                        c.target_x         = prey.x
                        c.target_y         = prey.y
                        c.target_id        = prey.creature_id
            else:
                group.target_creature_id = None

    def _disband_empty_groups(self, creature_map: Dict[str, Creature]) -> None:
        to_remove = []
        for gid, group in self._groups.items():
            # Remove dead members
            dead = {cid for cid in group.member_ids
                    if cid not in creature_map or not creature_map[cid].is_alive}
            for cid in dead:
                group.remove(cid)
                if cid in creature_map:
                    creature_map[cid].in_group = False
            if group.size < _MIN_GROUP_SIZE:
                for cid in group.member_ids:
                    if cid in creature_map:
                        creature_map[cid].in_group = False
                to_remove.append(gid)
        for gid in to_remove:
            del self._groups[gid]
