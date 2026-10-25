from __future__ import annotations
import logging
from typing import List, Set
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus, GameEvent

logger=logging.getLogger(__name__)

class AchievementSystem:
    def __init__(self,config,bus):
        self.config=config; self.bus=bus
        self.unlocked:Set[str]=set()
        self.defs:dict=config.get_section("achievements") or {}
        bus.subscribe("species:extinct",self._check_all)
        bus.subscribe("species:speciation",self._check_all)
        bus.subscribe("evolution:adaptation",self._check_all)
        bus.subscribe("species:registered",self._check_all)
        logger.info("AchievementSystem initialised (%d defs).",len(self.defs))

    def tick(self,world_tick): pass

    def check(self,ach_id,**kwargs):
        if ach_id in self.unlocked: return False
        self.unlocked.add(ach_id); defn=self.defs.get(ach_id,{})
        logger.info("Achievement unlocked: %s — %s",ach_id,defn.get("name",""))
        self.bus.queue("achievement:unlocked",{"id":ach_id,"name":defn.get("name",""),"description":defn.get("description",""),"points":defn.get("points",0)})
        return True

    def _check_all(self,event):
        if event.name=="species:registered" and "ACH001" not in self.unlocked: self.check("ACH001")
        if event.name=="species:extinct" and "ACH006" not in self.unlocked: self.check("ACH006")
        if event.name=="species:speciation" and "ACH005" not in self.unlocked: self.check("ACH005")
        if event.name=="evolution:adaptation" and "ACH004" not in self.unlocked: self.check("ACH004")
        if event.name=="evolution:adaptation" and "ACH003" not in self.unlocked: self.check("ACH003")

    def serialise(self): return list(self.unlocked)
    def deserialise(self,data): self.unlocked=set(data)
