"""
src/species/life_stage.py
==========================
LifeStage system constants and helper functions.
The LifeStage enum lives in creature.py to avoid circular imports;
this module provides utilities for stage-based calculations.
"""
from __future__ import annotations
from typing import Dict, Tuple
from species.creature import LifeStage


# Stat multipliers per life stage
_STAGE_MODIFIERS: Dict[LifeStage, Dict[str, float]] = {
    LifeStage.JUVENILE: {
        "speed":            0.60,
        "strength":         0.40,
        "vision":           0.70,
        "stamina":          0.60,
        "energy_capacity":  0.60,
        "metabolic_cost":   0.70,
        "reproduction":     0.00,   # cannot reproduce
    },
    LifeStage.ADULT: {
        "speed":            1.00,
        "strength":         1.00,
        "vision":           1.00,
        "stamina":          1.00,
        "energy_capacity":  1.00,
        "metabolic_cost":   1.00,
        "reproduction":     1.00,
    },
    LifeStage.ELDER: {
        "speed":            0.75,
        "strength":         0.80,
        "vision":           0.85,
        "stamina":          0.70,
        "energy_capacity":  0.85,
        "metabolic_cost":   0.90,
        "reproduction":     0.40,   # reduced but possible
    },
}


def get_modifier(stage: LifeStage, stat: str) -> float:
    """Return the stat multiplier for a given life stage."""
    return _STAGE_MODIFIERS.get(stage, _STAGE_MODIFIERS[LifeStage.ADULT]).get(stat, 1.0)


def stage_from_age(age: int, lifespan: float) -> LifeStage:
    """Determine life stage from age and species lifespan."""
    if lifespan <= 0:
        return LifeStage.ADULT
    ratio = age / lifespan
    if ratio < 0.15:
        return LifeStage.JUVENILE
    elif ratio < 0.75:
        return LifeStage.ADULT
    return LifeStage.ELDER


def stage_label(stage: LifeStage) -> str:
    return {
        LifeStage.JUVENILE: "Juvenile",
        LifeStage.ADULT:    "Adult",
        LifeStage.ELDER:    "Elder",
    }.get(stage, "Unknown")
