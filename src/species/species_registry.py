from __future__ import annotations
import logging, uuid
from typing import Dict, Iterator, List, Optional
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus
from genetics.genome import Genome
from species.species import Species, SpeciesStatus

logger = logging.getLogger(__name__)

class SpeciesRegistry:
    def __init__(self,config,bus):
        self.config=config; self.bus=bus
        self._species:Dict[str,Species]={}
        self._id_by_name:Dict[str,str]={}

    def register(self,species):
        self._species[species.species_id]=species
        self._id_by_name[species.name]=species.species_id
        logger.info("SpeciesRegistry: registered '%s' (id=%s,trophic=%d)",species.name,species.species_id,species.trophic_level)
        self.bus.queue("species:registered",{"species_id":species.species_id,"name":species.name,"trophic_level":species.trophic_level})
        return species

    def create_and_register(self,name,trophic_level,genome,biomes=None,ancestor_id=None,created_tick=0):
        sp=Species(name=name,trophic_level=trophic_level,genome=genome,biomes=biomes or ["grassland"],ancestor_id=ancestor_id,created_tick=created_tick)
        return self.register(sp)

    def get(self,species_id): return self._species.get(species_id)
    def get_by_name(self,name):
        sid=self._id_by_name.get(name); return self._species.get(sid) if sid else None
    def all_living(self): return [s for s in self._species.values() if s.status==SpeciesStatus.ALIVE]
    def all_extinct(self): return [s for s in self._species.values() if s.status==SpeciesStatus.EXTINCT]
    def all(self): return list(self._species.values())
    def count_living(self): return sum(1 for s in self._species.values() if s.status==SpeciesStatus.ALIVE)
    def total_population(self): return sum(s.population for s in self.all_living())
    def by_trophic_level(self,level): return [s for s in self.all_living() if s.trophic_level==level]
    def in_biome(self,biome): return [s for s in self.all_living() if biome in s.biomes]

    def mark_extinct(self,species_id,tick,cause="unknown"):
        sp=self.get(species_id)
        if sp and not sp.is_extinct():
            sp.mark_extinct(tick,cause)
            logger.info("SpeciesRegistry: '%s' went extinct at tick %d (%s)",sp.name,tick,cause)
            self.bus.queue("species:extinct",{"species_id":species_id,"name":sp.name,"cause":cause,"tick":tick,"generation":sp.generation})

    def speciate(self,parent_id,new_name,child_genome,tick=0):
        parent=self.get(parent_id)
        if parent is None: return None
        child=Species(name=new_name,trophic_level=parent.trophic_level,genome=child_genome,
                      biomes=list(parent.biomes),ancestor_id=parent_id,created_tick=tick)
        self.register(child)
        parent.log_event(tick,"speciation",f"Speciated into '{new_name}'")
        child.log_event(tick,"speciation",f"Branched from '{parent.name}'")
        logger.info("SpeciesRegistry: speciation '%s' -> '%s' at tick %d",parent.name,new_name,tick)
        self.bus.queue("species:speciation",{"parent_id":parent_id,"child_id":child.species_id,"parent_name":parent.name,"child_name":new_name,"tick":tick})
        return child

    def serialise(self): return [s.to_dict() for s in self._species.values()]
    def deserialise(self,data):
        self._species.clear(); self._id_by_name.clear()
        for d in data:
            sp=Species.from_dict(d); self._species[sp.species_id]=sp; self._id_by_name[sp.name]=sp.species_id
        logger.info("SpeciesRegistry: loaded %d species.",len(self._species))

    def __iter__(self): return iter(self._species.values())
    def __len__(self): return len(self._species)
    def __repr__(self): return f"SpeciesRegistry(living={self.count_living()},total={len(self._species)})"
