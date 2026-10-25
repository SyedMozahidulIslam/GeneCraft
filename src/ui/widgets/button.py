"""
src/ui/widgets/button.py  (also contains Slider, Panel, Tooltip, Graph)
========================================================================
Core UI widget library for GeneCraft.
All widgets are pure-draw objects — they hold state and render themselves
onto a target surface, returning events via a simple callback system.
"""
from __future__ import annotations

import math
from typing import Any, Callable, List, Optional, Tuple

import pygame

Color = Tuple[int, int, int]
ColorA = Tuple[int, int, int, int]


# ═══════════════════════════════════════════════════════════════════════════
# Base Widget
# ═══════════════════════════════════════════════════════════════════════════

class Widget:
    """Base class for all UI widgets."""

    def __init__(self, rect: pygame.Rect) -> None:
        self.rect    = rect
        self.visible = True
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if event was consumed."""
        return False

    def render(self, surface: pygame.Surface) -> None:
        pass

    def contains(self, pos: Tuple[int,int]) -> bool:
        return self.rect.collidepoint(pos)


# ═══════════════════════════════════════════════════════════════════════════
# Button
# ═══════════════════════════════════════════════════════════════════════════

class Button(Widget):
    """
    Stylised dark-theme button with hover/active states.

    Parameters
    ----------
    rect       : pygame.Rect
    label      : Button text
    on_click   : Callable called with no args on click
    color      : Base fill color (defaults to dark surface)
    accent     : Highlight/border color (defaults to accent green)
    font       : pygame.Font or None (uses default)
    icon       : Optional pygame.Surface drawn left of text
    """

    def __init__(
        self,
        rect:      pygame.Rect,
        label:     str,
        on_click:  Optional[Callable] = None,
        color:     Color = (30, 37, 46),
        accent:    Color = (0, 255, 136),
        font:      Optional[pygame.font.Font] = None,
        icon:      Optional[pygame.Surface]   = None,
        tooltip:   str  = "",
    ) -> None:
        super().__init__(rect)
        self.label    = label
        self.on_click = on_click
        self.color    = color
        self.accent   = accent
        self._font    = font or _default_font(14)
        self.icon     = icon
        self.tooltip  = tooltip

        self._hovered  = False
        self._pressed  = False
        self._disabled = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self._pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(pos):
                self._pressed = False
                if self.on_click:
                    self.on_click()
                return True
            self._pressed = False
        return False

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        r = self.rect

        # Background
        if self._pressed:
            bg = _darken(self.accent, 0.6)
        elif self._hovered:
            bg = _lighten(self.color, 1.6)
        else:
            bg = self.color

        pygame.draw.rect(surface, bg, r, border_radius=6)

        # Border — accent when hovered
        border_col = self.accent if (self._hovered or self._pressed) else _darken(self.accent, 0.4)
        pygame.draw.rect(surface, border_col, r, width=1, border_radius=6)

        # Glow on hover
        if self._hovered:
            glow = pygame.Surface((r.width+8, r.height+8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*self.accent, 40), glow.get_rect(), border_radius=8)
            surface.blit(glow, (r.x-4, r.y-4))

        # Icon + text
        x_off = r.x + 10
        if self.icon:
            surface.blit(self.icon, (x_off, r.centery - self.icon.get_height()//2))
            x_off += self.icon.get_width() + 6

        text_col = (230,237,243) if not self._disabled else (80,90,105)
        txt = self._font.render(self.label, True, text_col)
        surface.blit(txt, (x_off, r.centery - txt.get_height()//2))


# ═══════════════════════════════════════════════════════════════════════════
# Slider
# ═══════════════════════════════════════════════════════════════════════════

class Slider(Widget):
    """Horizontal slider for gene/trait editing."""

    def __init__(
        self,
        rect:      pygame.Rect,
        min_val:   float = 0.0,
        max_val:   float = 10.0,
        value:     float = 5.0,
        label:     str   = "",
        on_change: Optional[Callable[[float], None]] = None,
        accent:    Color = (0, 255, 136),
        font:      Optional[pygame.font.Font] = None,
        fmt:       str   = "%.1f",
    ) -> None:
        super().__init__(rect)
        self.min_val   = min_val
        self.max_val   = max_val
        self.value     = value
        self.label     = label
        self.on_change = on_change
        self.accent    = accent
        self._font     = font or _default_font(12)
        self.fmt       = fmt
        self._dragging = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self._dragging = True
                self._update_value(pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            self._update_value(pos[0])
            return True
        return False

    def _update_value(self, mouse_x: int) -> None:
        track_start = self.rect.x + 8
        track_end   = self.rect.right - 8
        ratio = (mouse_x - track_start) / max(1, track_end - track_start)
        ratio = max(0.0, min(1.0, ratio))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        if self.on_change:
            self.on_change(self.value)

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        r = self.rect
        cy = r.centery

        # Label
        if self.label:
            lbl = self._font.render(self.label, True, (139,148,158))
            surface.blit(lbl, (r.x, r.y - 18))

        # Track
        track_rect = pygame.Rect(r.x+8, cy-3, r.width-16, 6)
        pygame.draw.rect(surface, (40,50,65), track_rect, border_radius=3)

        # Fill
        ratio = (self.value - self.min_val) / max(0.001, self.max_val - self.min_val)
        fill_w = int(ratio * (r.width-16))
        if fill_w > 0:
            fill_rect = pygame.Rect(r.x+8, cy-3, fill_w, 6)
            pygame.draw.rect(surface, self.accent, fill_rect, border_radius=3)

        # Thumb
        thumb_x = r.x + 8 + fill_w
        pygame.draw.circle(surface, self.accent, (thumb_x, cy), 8)
        pygame.draw.circle(surface, (230,237,243), (thumb_x, cy), 4)

        # Value label
        val_txt = self._font.render(self.fmt % self.value, True, (230,237,243))
        surface.blit(val_txt, (r.right - val_txt.get_width() - 2, r.y - 18))


# ═══════════════════════════════════════════════════════════════════════════
# Panel
# ═══════════════════════════════════════════════════════════════════════════

class Panel(Widget):
    """
    Dark-themed panel with optional header bar, border glow, and scroll.
    Children widgets render inside the panel's clip area.
    """

    def __init__(
        self,
        rect:        pygame.Rect,
        title:       str   = "",
        bg_color:    Color = (16, 22, 30),
        border_color:Color = (48, 58, 72),
        accent:      Color = (0, 255, 136),
        font:        Optional[pygame.font.Font] = None,
        closeable:   bool  = False,
        on_close:    Optional[Callable] = None,
    ) -> None:
        super().__init__(rect)
        self.title        = title
        self.bg_color     = bg_color
        self.border_color = border_color
        self.accent       = accent
        self._font        = font or _default_font(15)
        self.closeable    = closeable
        self.on_close     = on_close
        self.children:    List[Widget] = []
        self._close_btn:  Optional[Button] = None
        self._scroll_y    = 0
        self._content_h   = 0

        self._header_h = 36 if title else 0
        if closeable and title:
            close_r = pygame.Rect(rect.right-30, rect.y+4, 26, 26)
            self._close_btn = Button(close_r, "✕",
                                     on_click=on_close or self._default_close,
                                     color=(40,20,20), accent=(255,68,68))

    def _default_close(self) -> None:
        self.visible = False

    def add_child(self, widget: Widget) -> None:
        self.children.append(widget)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        consumed = False
        if self._close_btn:
            consumed = self._close_btn.handle_event(event)
        if not consumed:
            for child in self.children:
                if child.handle_event(event):
                    consumed = True
                    break
        # Scroll
        if (event.type == pygame.MOUSEWHEEL
                and self.rect.collidepoint(pygame.mouse.get_pos())):
            self._scroll_y = max(0, min(
                max(0, self._content_h - self.rect.height + self._header_h),
                self._scroll_y - event.y * 20,
            ))
            consumed = True
        return consumed

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        r = self.rect

        # Background
        pygame.draw.rect(surface, self.bg_color, r, border_radius=8)
        pygame.draw.rect(surface, self.border_color, r, width=1, border_radius=8)

        # Accent top edge
        pygame.draw.line(surface, self.accent, (r.x+8, r.y), (r.right-8, r.y), 2)

        # Header
        if self.title:
            hdr_r = pygame.Rect(r.x, r.y, r.width, self._header_h)
            pygame.draw.rect(surface, (20,28,38), hdr_r,
                             border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.line(surface, self.border_color,
                             (r.x, r.y+self._header_h), (r.right, r.y+self._header_h))
            title_txt = self._font.render(self.title, True, (230,237,243))
            surface.blit(title_txt, (r.x+12, r.y + (self._header_h-title_txt.get_height())//2))
            if self._close_btn:
                self._close_btn.render(surface)

        # Clip children
        clip_rect = pygame.Rect(r.x+1, r.y+self._header_h+1,
                                r.width-2, r.height-self._header_h-2)
        old_clip  = surface.get_clip()
        surface.set_clip(clip_rect)

        offset_y = -self._scroll_y
        for child in self.children:
            if child.visible:
                orig_y = child.rect.y
                child.rect.y += offset_y
                child.render(surface)
                child.rect.y = orig_y

        surface.set_clip(old_clip)


# ═══════════════════════════════════════════════════════════════════════════
# MiniGraph — sparkline-style graph
# ═══════════════════════════════════════════════════════════════════════════

class MiniGraph(Widget):
    """
    Compact line graph for population/biodiversity history.
    """

    def __init__(
        self,
        rect:    pygame.Rect,
        label:   str   = "",
        color:   Color = (0, 255, 136),
        bg:      Color = (16, 22, 30),
        font:    Optional[pygame.font.Font] = None,
        max_pts: int   = 300,
    ) -> None:
        super().__init__(rect)
        self.label    = label
        self.color    = color
        self.bg       = bg
        self._font    = font or _default_font(11)
        self.max_pts  = max_pts
        self.data:    List[float] = []

    def push(self, value: float) -> None:
        self.data.append(value)
        if len(self.data) > self.max_pts:
            self.data.pop(0)

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        r = self.rect
        pygame.draw.rect(surface, self.bg, r, border_radius=4)
        pygame.draw.rect(surface, (40,50,65), r, width=1, border_radius=4)

        if len(self.data) < 2:
            return

        max_v = max(self.data) or 1
        min_v = min(self.data)
        span  = max_v - min_v or 1

        pts = []
        for i, v in enumerate(self.data):
            x = r.x + int(i / (len(self.data)-1) * (r.width-4)) + 2
            y = r.bottom - 4 - int((v - min_v) / span * (r.height - 16))
            pts.append((x, y))

        if len(pts) >= 2:
            pygame.draw.lines(surface, self.color, False, pts, 2)

        # Label + latest value
        if self.label:
            lbl = self._font.render(self.label, True, (139,148,158))
            surface.blit(lbl, (r.x+4, r.y+3))
        val_txt = self._font.render(f"{self.data[-1]:.1f}", True, self.color)
        surface.blit(val_txt, (r.right - val_txt.get_width() - 4, r.y+3))


# ═══════════════════════════════════════════════════════════════════════════
# Tooltip
# ═══════════════════════════════════════════════════════════════════════════

class Tooltip:
    """Floating tooltip rendered at cursor position."""

    def __init__(self, font: Optional[pygame.font.Font] = None) -> None:
        self._font    = font or _default_font(12)
        self._text    = ""
        self._visible = False

    def show(self, text: str) -> None:
        self._text    = text
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def render(self, surface: pygame.Surface) -> None:
        if not self._visible or not self._text:
            return
        pos   = pygame.mouse.get_pos()
        lines = self._text.split("\n")
        w     = max(self._font.size(l)[0] for l in lines) + 16
        h     = len(lines) * (self._font.get_height() + 2) + 10

        # Keep on screen
        sx, sy = surface.get_size()
        tx = min(pos[0]+14, sx - w - 4)
        ty = min(pos[1]+14, sy - h - 4)

        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((16, 22, 30, 220))
        surface.blit(bg, (tx, ty))
        pygame.draw.rect(surface, (0,255,136), pygame.Rect(tx,ty,w,h), width=1, border_radius=4)

        for i, line in enumerate(lines):
            col = (230,237,243) if i > 0 else (0,255,136)
            txt = self._font.render(line, True, col)
            surface.blit(txt, (tx+8, ty+5 + i*(self._font.get_height()+2)))


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

_font_cache: dict = {}

def _default_font(size: int) -> pygame.font.Font:
    if size not in _font_cache:
        try:
            _font_cache[size] = pygame.font.SysFont("consolas,monospace", size)
        except Exception:
            _font_cache[size] = pygame.font.Font(None, size + 4)
    return _font_cache[size]


def _darken(c: Color, f: float) -> Color:
    return (int(c[0]*f), int(c[1]*f), int(c[2]*f))

def _lighten(c: Color, f: float) -> Color:
    return (min(255,int(c[0]*f)), min(255,int(c[1]*f)), min(255,int(c[2]*f)))
