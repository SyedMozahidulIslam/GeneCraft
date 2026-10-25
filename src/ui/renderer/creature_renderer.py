"""
src/ui/renderer/creature_renderer.py
======================================
CreatureRenderer — draws individual creatures with state indicators,
health rings, behavior icons, and selection highlight.
"""
from __future__ import annotations
from typing import Optional, Tuple
import pygame
from species.creature import BehaviorState, LifeStage
from utils.color_utils import health_color, pulse_alpha

_BEHAVIOR_COLORS = {
    BehaviorState.IDLE:      (100, 100, 100),
    BehaviorState.EXPLORE:   (80,  160, 255),
    BehaviorState.HUNT:      (255,  60,  60),
    BehaviorState.EAT:       (80,  220,  80),
    BehaviorState.FLEE:      (255, 200,   0),
    BehaviorState.SLEEP:     ( 80,  80, 160),
    BehaviorState.REPRODUCE: (255, 120, 200),
    BehaviorState.MIGRATE:   (180, 255, 180),
    BehaviorState.DEFEND:    (255, 140,   0),
}


class CreatureRenderer:
    """
    Renders creature dots with progressive detail at higher zoom levels.

    Zoom thresholds
    ---------------
    < 2px  : single pixel dot (species color)
    2–5px  : filled circle (species color)
    5–10px : circle + health ring
    > 10px : full detail: circle + health ring + behavior color + life stage marker
    """

    def render_creature(
        self,
        surface:    pygame.Surface,
        px:         int,
        py:         int,
        creature,
        tpx:        int,       # tile size in pixels at current zoom
        selected:   bool = False,
        tick:       int  = 0,
    ) -> None:
        species_color = getattr(creature, '_species_color', (200, 200, 200))
        dot_r         = max(1, tpx // 3)

        if tpx < 2:
            surface.set_at((px, py), species_color)
            return

        # Base dot
        pygame.draw.circle(surface, species_color, (px, py), dot_r)

        if tpx >= 5:
            # Health ring
            hr    = creature.health_ratio
            if hr < 1.0:
                hcol = health_color(hr)
                pygame.draw.circle(surface, hcol, (px, py), dot_r + 2, 1)

        if tpx >= 10:
            # Behavior color inner dot
            bcol = _BEHAVIOR_COLORS.get(creature.behavior, (200, 200, 200))
            pygame.draw.circle(surface, bcol, (px, py), max(1, dot_r // 2))

            # Life stage marker (juvenile = small cross)
            if creature.life_stage == LifeStage.JUVENILE:
                s = dot_r + 3
                pygame.draw.line(surface, (255, 255, 100), (px-s, py), (px+s, py), 1)
                pygame.draw.line(surface, (255, 255, 100), (px, py-s), (px, py+s), 1)

        if selected:
            alpha = pulse_alpha(tick, period=40, min_a=160, max_a=255)
            sel_surf = pygame.Surface((dot_r*4, dot_r*4), pygame.SRCALPHA)
            pygame.draw.circle(sel_surf, (0, 255, 136, alpha),
                               (dot_r*2, dot_r*2), dot_r*2, 2)
            surface.blit(sel_surf, (px - dot_r*2, py - dot_r*2))
