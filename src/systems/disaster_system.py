from __future__ import annotations
import logging, random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus, GameEvent

logger=logging.getLogger(__name__)

class DisasterType(Enum):
    WILDFIRE=auto(); FLOOD=auto(); DROUGHT=auto(); DISEASE=auto()
    VOLCANIC_ERUPTION=auto(); ICE_AGE=auto(); METEOR_STRIKE=auto()

@dataclass
class ActiveDisaster:
    disaster_type:DisasterType; start_tick:int; duration:int
    center_x:int; center_y:int; radius:int; severity:float=0.5
    ticks_elapsed:int=0; is_active:bool=True

_ODDS:Dict[DisasterType,float]={DisasterType.WILDFIRE:0.001,DisasterType.FLOOD:0.0008,
    DisasterType.DROUGHT:0.0005,DisasterType.DISEASE:0.0006,
    DisasterType.VOLCANIC_ERUPTION:0.00005,DisasterType.METEOR_STRIKE:0.00001}

class DisasterSystem:
    def __init__(self,config,bus,world):
        self.config=config; self.bus=bus; self.world=world
        self.active:List[ActiveDisaster]=[]; self.history:List[dict]=[]; self._enabled=True
        logger.info("DisasterSystem initialised.")

    def tick(self,world_tick):
        if not self._enabled: return
        for dtype,prob in _ODDS.items():
            if random.random()<prob: self._trigger(dtype,world_tick)
        for d in list(self.active):
            d.ticks_elapsed+=1; self._apply_tick(d,world_tick)
            if d.ticks_elapsed>=d.duration: self._resolve(d,world_tick)
        self.active=[d for d in self.active if d.is_active]

    def _trigger(self,dtype,tick,cx=None,cy=None,severity=0.5):
        cx=cx or random.randint(0,self.world.width-1); cy=cy or random.randint(0,self.world.height-1)
        params={DisasterType.WILDFIRE:dict(duration=random.randint(3,10),radius=random.randint(5,20)),
                DisasterType.FLOOD:dict(duration=random.randint(5,15),radius=random.randint(8,25)),
                DisasterType.DROUGHT:dict(duration=random.randint(10,30),radius=random.randint(20,50)),
                DisasterType.DISEASE:dict(duration=random.randint(5,20),radius=random.randint(15,40)),
                DisasterType.VOLCANIC_ERUPTION:dict(duration=random.randint(20,50),radius=random.randint(10,30)),
                DisasterType.ICE_AGE:dict(duration=random.randint(50,200),radius=self.world.width),
                DisasterType.METEOR_STRIKE:dict(duration=1,radius=random.randint(3,10))}.get(dtype,dict(duration=10,radius=10))
        d=ActiveDisaster(disaster_type=dtype,start_tick=tick,center_x=cx,center_y=cy,severity=severity,**params)
        self.active.append(d)
        self.bus.queue("disaster:started",{"type":dtype.name,"x":cx,"y":cy,"severity":severity,"tick":tick})
        logger.info("DisasterSystem: %s triggered.",dtype.name)
        return d

    def _apply_tick(self,d,tick):
        if d.disaster_type==DisasterType.WILDFIRE and d.ticks_elapsed==1: self.world.apply_fire(d.center_x,d.center_y,d.radius)
        elif d.disaster_type==DisasterType.FLOOD and d.ticks_elapsed==1: self.world.apply_flood(d.center_x,d.center_y,d.radius)
        elif d.disaster_type==DisasterType.DROUGHT and d.ticks_elapsed%5==0: self.world.apply_drought(d.center_x,d.center_y,d.radius,0.05)
        elif d.disaster_type==DisasterType.VOLCANIC_ERUPTION and d.ticks_elapsed==1: self.world.apply_ash_layer()
        elif d.disaster_type==DisasterType.METEOR_STRIKE: self.world.apply_fire(d.center_x,d.center_y,d.radius)

    def _resolve(self,d,tick):
        d.is_active=False
        self.history.append({"type":d.disaster_type.name,"start_tick":d.start_tick,"end_tick":tick})
        self.bus.queue("disaster:ended",{"type":d.disaster_type.name,"tick":tick})

    def player_trigger(self,dtype_name,cx,cy,tick,severity=0.7):
        try: dtype=DisasterType[dtype_name.upper()]
        except KeyError: return None
        return self._trigger(dtype,tick,cx,cy,severity)

    def serialise(self): return self.history[-50:]
    def deserialise(self,data): self.history=data
