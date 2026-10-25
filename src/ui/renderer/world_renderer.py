from __future__ import annotations
import math
from typing import Optional, Tuple
import pygame
from engine.config_manager import ConfigManager
from species.species_registry import SpeciesRegistry
from utils.color_utils import lerp_color, health_color

_BIOME_COLORS={
    "forest":(34,85,34),"grassland":(120,160,40),"mountain":(100,90,80),
    "river":(30,100,180),"lake":(20,80,150),"desert":(200,160,80),
    "swamp":(40,80,40),"arctic":(200,215,230),
}

class WorldRenderer:
    MIN_ZOOM=0.4; MAX_ZOOM=8.0
    def __init__(self,config,registry,viewport):
        self.config=config; self.registry=registry; self.viewport=viewport
        self.tile_px=config.get("world.tile_size_px") or 8
        self.zoom=1.0; self.offset_x=0.0; self.offset_y=0.0
        self._panning=False; self._pan_start=None; self._pan_offset_start=None
        self.show_food_overlay=False; self.show_creature_dots=True; self.show_grid_lines=False
        self._world=None; self._tick=0

    def attach_world(self,world):
        self._world=world
        w=world.width*self.tile_px; h=world.height*self.tile_px
        self.offset_x=(self.viewport.width-w)/2
        self.offset_y=(self.viewport.height-h)/2

    def handle_event(self,event):
        if event.type==pygame.MOUSEWHEEL and self.viewport.collidepoint(pygame.mouse.get_pos()):
            self.zoom=max(self.MIN_ZOOM,min(self.MAX_ZOOM,self.zoom+event.y*0.15)); return True
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==2:
            if self.viewport.collidepoint(event.pos):
                self._panning=True; self._pan_start=event.pos
                self._pan_offset_start=(self.offset_x,self.offset_y); return True
        elif event.type==pygame.MOUSEBUTTONUP and event.button==2:
            self._panning=False
        elif event.type==pygame.MOUSEMOTION and self._panning:
            dx=event.pos[0]-self._pan_start[0]; dy=event.pos[1]-self._pan_start[1]
            self.offset_x=self._pan_offset_start[0]+dx; self.offset_y=self._pan_offset_start[1]+dy; return True
        return False

    def render(self,surface,tick):
        self._tick=tick
        if not self._world: return
        old_clip=surface.get_clip(); surface.set_clip(self.viewport)
        surface.fill((10,14,20),self.viewport)
        tpx=max(1,int(self.tile_px*self.zoom)); vp=self.viewport
        x_start=max(0,int(-self.offset_x/tpx)); y_start=max(0,int(-self.offset_y/tpx))
        x_end=min(self._world.width,x_start+vp.width//tpx+2)
        y_end=min(self._world.height,y_start+vp.height//tpx+2)
        for ty in range(y_start,y_end):
            for tx in range(x_start,x_end):
                tile=self._world.get_tile(tx,ty)
                if tile is None: continue
                px=vp.x+int(tx*tpx+self.offset_x); py=vp.y+int(ty*tpx+self.offset_y)
                color=self._tile_color(tile)
                pygame.draw.rect(surface,color,(px,py,tpx,tpx))
                if self.show_grid_lines and tpx>=12:
                    pygame.draw.rect(surface,(30,40,55),(px,py,tpx,tpx),1)
        if self.show_creature_dots and tpx>=2:
            self._render_creatures(surface,tpx,vp)
        surface.set_clip(old_clip)

    def _tile_color(self,tile):
        base=_BIOME_COLORS.get(tile.biome,(80,100,60))
        if self.show_food_overlay:
            return lerp_color((60,30,20),base,tile.food_ratio)
        var=tile.color_var
        return (max(0,min(255,int(base[0]+var*40))),max(0,min(255,int(base[1]+var*40))),max(0,min(255,int(base[2]+var*40))))

    def _render_creatures(self,surface,tpx,vp):
        dot_r=max(2,tpx//3)
        for species in self.registry.all_living():
            color=species.color
            for c in species.creatures:
                if not c.is_alive: continue
                px=vp.x+int(c.x*tpx+self.offset_x); py=vp.y+int(c.y*tpx+self.offset_y)
                if vp.x<=px<=vp.right and vp.y<=py<=vp.bottom:
                    pygame.draw.circle(surface,color,(px,py),dot_r)
                    if tpx>=10 and c.health_ratio<0.5:
                        pygame.draw.circle(surface,health_color(c.health_ratio),(px,py),dot_r+2,1)

    def world_to_screen(self,wx,wy):
        tpx=self.tile_px*self.zoom
        return (int(self.viewport.x+wx*tpx+self.offset_x),int(self.viewport.y+wy*tpx+self.offset_y))

    def screen_to_world(self,sx,sy):
        tpx=self.tile_px*self.zoom
        return ((sx-self.viewport.x-self.offset_x)/tpx,(sy-self.viewport.y-self.offset_y)/tpx)

    def center_on(self,wx,wy):
        tpx=self.tile_px*self.zoom
        self.offset_x=self.viewport.width/2-wx*tpx; self.offset_y=self.viewport.height/2-wy*tpx
