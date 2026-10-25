"""
src/ui/renderer/ui_renderer.py
================================
UIRenderer — shared drawing primitives used by all UI panels.
Provides consistent styling across the entire interface.
"""
from __future__ import annotations
from typing import Optional, Tuple
import pygame

Color  = Tuple[int, int, int]
ColorA = Tuple[int, int, int, int]

# Design tokens (dark theme)
BG        = (13,  17,  23)
SURFACE   = (22,  27,  34)
BORDER    = (48,  58,  72)
ACCENT    = (0,  255, 136)
ACCENT_B  = (0,  170, 255)
TEXT      = (230, 237, 243)
MUTED     = (139, 148, 158)
RED       = (255,  68,  68)
AMBER     = (255, 170,   0)


class UIRenderer:
    """Static drawing helpers used by all panels and widgets."""

    @staticmethod
    def panel_bg(surface: pygame.Surface, rect: pygame.Rect,
                 color: Color = SURFACE, radius: int = 8) -> None:
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        pygame.draw.rect(surface, BORDER, rect, width=1, border_radius=radius)
        pygame.draw.line(surface, ACCENT, (rect.x+8, rect.y), (rect.right-8, rect.y), 2)

    @staticmethod
    def panel_header(surface: pygame.Surface, rect: pygame.Rect,
                     title: str, font: pygame.font.Font,
                     height: int = 36) -> None:
        hdr = pygame.Rect(rect.x, rect.y, rect.width, height)
        pygame.draw.rect(surface, (20, 28, 38), hdr,
                         border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(surface, BORDER, (rect.x, rect.y+height),
                         (rect.right, rect.y+height))
        txt = font.render(title, True, TEXT)
        surface.blit(txt, (rect.x+12, rect.y + (height-txt.get_height())//2))

    @staticmethod
    def progress_bar(surface: pygame.Surface, rect: pygame.Rect,
                     ratio: float, color: Color = ACCENT,
                     bg: Color = (40, 50, 65)) -> None:
        pygame.draw.rect(surface, bg, rect, border_radius=3)
        if ratio > 0:
            fill_w = max(1, int(ratio * rect.width))
            fill   = pygame.Rect(rect.x, rect.y, fill_w, rect.height)
            pygame.draw.rect(surface, color, fill, border_radius=3)

    @staticmethod
    def glow_rect(surface: pygame.Surface, rect: pygame.Rect,
                  color: Color = ACCENT, layers: int = 4) -> None:
        for i in range(layers, 0, -1):
            gs = pygame.Surface((rect.width+i*2, rect.height+i*2), pygame.SRCALPHA)
            alpha = 12 * i
            pygame.draw.rect(gs, (*color, alpha), gs.get_rect(), border_radius=8+i)
            surface.blit(gs, (rect.x-i, rect.y-i))

    @staticmethod
    def badge(surface: pygame.Surface, text: str, x: int, y: int,
              color: Color = ACCENT, font: Optional[pygame.font.Font] = None) -> None:
        if font is None:
            try:    font = pygame.font.SysFont("consolas", 10)
            except: font = pygame.font.Font(None, 14)
        txt    = font.render(text, True, BG)
        pad    = 4
        width  = txt.get_width() + pad*2
        height = txt.get_height() + pad
        r      = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, color, r, border_radius=3)
        surface.blit(txt, (x+pad, y+pad//2))

    @staticmethod
    def sparkline(surface: pygame.Surface, rect: pygame.Rect,
                  data: list, color: Color = ACCENT) -> None:
        if len(data) < 2:
            return
        max_v = max(data) or 1
        pts   = []
        for i, v in enumerate(data):
            px = rect.x + int(i / (len(data)-1) * rect.width)
            py = rect.bottom - int(v / max_v * rect.height)
            pts.append((px, py))
        pygame.draw.lines(surface, color, False, pts, 1)
