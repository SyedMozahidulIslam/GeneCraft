from __future__ import annotations
import logging, random
from typing import Dict, List, Optional, Tuple
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus
from utils.math_utils import PerlinNoise2D, clamp
from world.tile import Tile

logger=logging.getLogger(__name__)

_BIOME_MATRIX=[
    (0.0,0.25,0.0,1.0,"lake"),(0.25,0.45,0.0,0.2,"desert"),
    (0.25,0.45,0.2,0.5,"grassland"),(0.25,0.45,0.5,0.75,"forest"),
    (0.25,0.45,0.75,1.0,"swamp"),(0.45,0.65,0.0,0.3,"grassland"),
    (0.45,0.65,0.3,0.7,"forest"),(0.45,0.65,0.7,1.0,"river"),
    (0.65,0.80,0.0,1.0,"mountain"),(0.80,1.00,0.0,1.0,"arctic"),
]
_BIOME_TEMPS={"forest":15.0,"grassland":18.0,"mountain":5.0,"river":16.0,"lake":14.0,"desert":32.0,"swamp":28.0,"arctic":-15.0}
_BIOME_FOOD_CAP={"forest":90.0,"grassland":100.0,"mountain":40.0,"river":80.0,"lake":70.0,"desert":25.0,"swamp":85.0,"arctic":20.0}
_BIOME_REGEN={"forest":1.2,"grassland":1.5,"mountain":0.6,"river":1.8,"lake":1.4,"desert":0.3,"swamp":2.0,"arctic":0.2}
_BIOME_COLORS={"forest":(34,85,34),"grassland":(120,160,40),"mountain":(100,90,80),"river":(30,100,180),"lake":(20,80,150),"desert":(200,160,80),"swamp":(40,80,40),"arctic":(200,215,230)}

class World:
    def __init__(self,config,bus):
        self.config=config; self.bus=bus
        size_key=config.get("world.default_size","medium")
        size_cfg=config.get(f"world.{size_key}") or {}
        self.width=size_cfg.get("width",100); self.height=size_cfg.get("height",100)
        self.tiles:List[List[Tile]]=[]
        self.biome_map:Dict[str,List[Tuple[int,int]]]={}
        self.season="spring"; self.season_tick=0; self.world_age=0
        self.avg_temp=15.0; self.global_temp_offset=0.0
        self._seed=random.randint(0,999999)
        logger.info("World: %dx%d grid (seed=%d).",self.width,self.height,self._seed)

    def generate(self,seed=None):
        if seed is not None: self._seed=seed
        rng=random.Random(self._seed)
        elev_noise=PerlinNoise2D(seed=self._seed)
        moist_noise=PerlinNoise2D(seed=self._seed+1000)
        logger.info("World: generating %dx%d terrain…",self.width,self.height)
        self.tiles=[]; self.biome_map={}
        for y in range(self.height):
            row=[]
            for x in range(self.width):
                elev=elev_noise.octaves(x,y,octaves=6,scale=0.008)
                moist=moist_noise.octaves(x,y,octaves=4,scale=0.012)
                biome=self._assign_biome(elev,moist)
                temp=_BIOME_TEMPS.get(biome,15.0)+rng.uniform(-3,3)
                cap=_BIOME_FOOD_CAP.get(biome,60.0); regen=_BIOME_REGEN.get(biome,1.0)
                color=_BIOME_COLORS.get(biome,(80,120,60))
                tile=Tile(grid_x=x,grid_y=y,biome=biome,elevation=elev,moisture=moist,
                          temperature=temp,is_water=(biome in ("lake","river")),
                          food_amount=cap*rng.uniform(0.5,1.0),food_capacity=cap,
                          food_regen_rate=regen,color_base=color,color_var=rng.uniform(-0.08,0.08))
                row.append(tile); self.biome_map.setdefault(biome,[]).append((x,y))
            self.tiles.append(row)
        self._carve_rivers(rng)
        self.bus.queue("world:generated",{"seed":self._seed,"width":self.width,"height":self.height})
        logger.info("World: generation complete. Biomes: %s",{b:len(v) for b,v in self.biome_map.items()})

    def _assign_biome(self,elev,moist):
        for e0,e1,m0,m1,biome in _BIOME_MATRIX:
            if e0<=elev<e1 and m0<=moist<=m1: return biome
        return "grassland"

    def _carve_rivers(self,rng):
        for _ in range(15):
            mtn=self.biome_map.get("mountain",[])
            if not mtn: break
            sx,sy=rng.choice(mtn); x,y=float(sx),float(sy)
            for step in range(rng.randint(20,60)):
                ix,iy=int(x),int(y)
                if not self._in_bounds(ix,iy): break
                tile=self.tiles[iy][ix]
                if tile.biome in ("lake","arctic"): break
                tile.biome="river"; tile.is_water=True
                tile.temperature=_BIOME_TEMPS["river"]; tile.food_capacity=_BIOME_FOOD_CAP["river"]
                tile.food_regen_rate=_BIOME_REGEN["river"]; tile.color_base=_BIOME_COLORS["river"]
                self.biome_map.setdefault("river",[]).append((ix,iy))
                x+=rng.uniform(-1,1); y+=rng.uniform(0.5,1.5)

    def tick(self,world_tick):
        self.world_age=world_tick; self.season_tick+=1
        tps=self.config.get("simulation.ticks_per_season",91)
        self._update_season(world_tick,tps)
        season_mod={"spring":1.3,"summer":1.0,"autumn":0.8,"winter":0.2}.get(self.season,1.0)
        for row in self.tiles:
            for tile in row: tile.regen_food(season_mod)
        if world_tick%500==0:
            self.global_temp_offset+=random.gauss(0,0.1)
            self.global_temp_offset=clamp(self.global_temp_offset,-10,10)

    def _update_season(self,tick,tps):
        seasons=["spring","summer","autumn","winter"]
        idx=(tick//tps)%4; new_season=seasons[idx]
        if new_season!=self.season:
            old=self.season; self.season=new_season
            self.bus.queue("world:season_change",{"old":old,"new":new_season,"tick":tick})

    def get_tile(self,x,y):
        if self._in_bounds(x,y): return self.tiles[y][x]
        return None

    def _in_bounds(self,x,y): return 0<=x<self.width and 0<=y<self.height

    def tiles_in_radius(self,cx,cy,radius):
        result=[]; r2=radius*radius
        for dy in range(-radius,radius+1):
            for dx in range(-radius,radius+1):
                if dx*dx+dy*dy<=r2:
                    t=self.get_tile(cx+dx,cy+dy)
                    if t: result.append(t)
        return result

    def random_tile_in_biome(self,biome):
        tiles=self.biome_map.get(biome,[])
        if not tiles: return None
        x,y=random.choice(tiles); return self.get_tile(x,y)

    def random_passable_tile(self):
        for _ in range(100):
            x=random.randint(0,self.width-1); y=random.randint(0,self.height-1)
            t=self.get_tile(x,y)
            if t and t.is_passable and not t.is_water: return t
        return None

    def biomes_present(self): return [b for b,tiles in self.biome_map.items() if tiles]
    def temperature_at(self,x,y):
        tile=self.get_tile(x,y)
        return (tile.temperature+self.global_temp_offset) if tile else 15.0
    def food_available_at(self,x,y):
        tile=self.get_tile(x,y); return tile.food_amount if tile else 0.0

    def apply_fire(self,cx,cy,radius):
        count=0
        for tile in self.tiles_in_radius(cx,cy,radius):
            if not tile.is_water: tile.food_amount=0.0; tile.nutrient_level+=2.0; count+=1
        return count

    def apply_flood(self,cx,cy,radius):
        count=0
        for tile in self.tiles_in_radius(cx,cy,radius):
            if not tile.is_water and tile.elevation<0.5:
                tile.is_water=True; tile.is_passable=False; count+=1
        return count

    def apply_drought(self,cx,cy,radius,severity):
        count=0
        for tile in self.tiles_in_radius(cx,cy,radius):
            tile.food_amount*=(1.0-severity); tile.food_capacity*=(1.0-severity*0.3); count+=1
        return count

    def apply_ash_layer(self):
        for row in self.tiles:
            for tile in row: tile.food_amount*=0.3; tile.food_capacity*=0.7

    def serialise(self):
        tiles_data=[tile.to_dict() for row in self.tiles for tile in row
                    if tile.food_amount<tile.food_capacity*0.95 or tile.nutrient_level>0.1]
        return {"seed":self._seed,"width":self.width,"height":self.height,"season":self.season,
                "world_age":self.world_age,"global_temp_offset":self.global_temp_offset,"tiles_delta":tiles_data}

    def deserialise(self,data):
        self._seed=data.get("seed",self._seed); self.season=data.get("season","spring")
        self.world_age=data.get("world_age",0); self.global_temp_offset=data.get("global_temp_offset",0.0)
        self.generate(self._seed)
        for td in data.get("tiles_delta",[]):
            tile=self.get_tile(td["grid_x"],td["grid_y"])
            if tile:
                tile.food_amount=td.get("food_amount",tile.food_amount)
                tile.nutrient_level=td.get("nutrient_level",tile.nutrient_level)

    def __repr__(self): return f"World({self.width}x{self.height},seed={self._seed},season={self.season})"
