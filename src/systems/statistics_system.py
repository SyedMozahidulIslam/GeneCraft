from __future__ import annotations
import logging
from collections import defaultdict, deque
from typing import Any, Deque, Dict, List, Tuple
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus, GameEvent
from species.species_registry import SpeciesRegistry
from utils.math_utils import shannon_entropy

logger=logging.getLogger(__name__)
_HISTORY_LEN=500

class StatisticsSystem:
    def __init__(self,config,bus,registry):
        self.config=config; self.bus=bus; self.registry=registry
        self.population_history:Deque=deque(maxlen=_HISTORY_LEN)
        self.species_count_history:Deque=deque(maxlen=_HISTORY_LEN)
        self.biodiversity_history:Deque=deque(maxlen=_HISTORY_LEN)
        self.food_history:Deque=deque(maxlen=_HISTORY_LEN)
        self.extinction_events=0; self.evolution_events=0; self.speciation_events=0
        self.adaptation_events=0; self.predation_events=0; self.reproduction_events=0; self.disaster_events=0
        self.kills_by_species:Dict[str,int]=defaultdict(int)
        self.deaths_by_species:Dict[str,int]=defaultdict(int)
        self.last_snapshot:Dict[str,Any]={}
        bus.subscribe("species:extinct",self._on_extinct)
        bus.subscribe("evolution:adaptation",self._on_adaptation)
        bus.subscribe("species:speciation",self._on_speciation)
        bus.subscribe("creature:killed",self._on_kill)
        bus.subscribe("species:reproduced",self._on_reproduce)
        bus.subscribe("disaster:started",self._on_disaster)
        logger.info("StatisticsSystem initialised.")

    def tick(self,world_tick):
        living=self.registry.all_living()
        total_pop=sum(s.population for s in living); species_n=len(living)
        pop_counts={s.species_id:s.population for s in living if s.population>0}
        biodiversity=shannon_entropy(pop_counts)
        self.population_history.append((world_tick,total_pop))
        self.species_count_history.append((world_tick,species_n))
        self.biodiversity_history.append((world_tick,biodiversity))
        self.last_snapshot={
            "tick":world_tick,"total_population":total_pop,"species_count":species_n,
            "biodiversity":round(biodiversity,3),"extinction_events":self.extinction_events,
            "evolution_events":self.evolution_events,"speciation_events":self.speciation_events,
            "predation_events":self.predation_events,
            "species":[{"species_id":s.species_id,"name":s.name,"population":s.population,
                        "trophic_level":s.trophic_level,"generation":s.generation,
                        "color":list(s.color),"biomes":s.biomes,"fitness":0.0} for s in living]}

    def biodiversity_index(self): return self.biodiversity_history[-1][1] if self.biodiversity_history else 0.0
    def trophic_distribution(self):
        dist=defaultdict(int)
        for s in self.registry.all_living(): dist[s.trophic_level]+=s.population
        return dict(dist)
    def population_by_species(self): return {s.name:s.population for s in self.registry.all_living()}
    def ecosystem_health(self):
        bio=self.biodiversity_index(); trophic=self.trophic_distribution()
        has_prod=trophic.get(1,0)>0 or trophic.get(2,0)>0; has_cons=trophic.get(3,0)>0 or trophic.get(4,0)>0
        return round(bio*0.6+(0.5 if (has_prod and has_cons) else 0.0)*0.4,3)

    def _on_extinct(self,e): self.extinction_events+=1; self.evolution_events+=1
    def _on_adaptation(self,e): self.adaptation_events+=1; self.evolution_events+=1
    def _on_speciation(self,e): self.speciation_events+=1; self.evolution_events+=1
    def _on_kill(self,e):
        self.predation_events+=1; pred=e.data.get("predator_species",""); prey=e.data.get("prey_species","")
        if pred: self.kills_by_species[pred]+=1
        if prey: self.deaths_by_species[prey]+=1
    def _on_reproduce(self,e): self.reproduction_events+=1
    def _on_disaster(self,e): self.disaster_events+=1

    def serialise(self):
        return {"extinction_events":self.extinction_events,"evolution_events":self.evolution_events,
                "speciation_events":self.speciation_events,"adaptation_events":self.adaptation_events,
                "predation_events":self.predation_events,"reproduction_events":self.reproduction_events,
                "disaster_events":self.disaster_events,"kills_by_species":dict(self.kills_by_species),
                "deaths_by_species":dict(self.deaths_by_species),
                "population_history":list(self.population_history)[-200:],
                "species_count_history":list(self.species_count_history)[-200:],
                "biodiversity_history":list(self.biodiversity_history)[-200:]}

    def deserialise(self,data):
        self.extinction_events=data.get("extinction_events",0); self.evolution_events=data.get("evolution_events",0)
        self.speciation_events=data.get("speciation_events",0); self.adaptation_events=data.get("adaptation_events",0)
        self.predation_events=data.get("predation_events",0); self.reproduction_events=data.get("reproduction_events",0)
        self.disaster_events=data.get("disaster_events",0)
        for k,v in data.get("kills_by_species",{}).items(): self.kills_by_species[k]=v
        for k,v in data.get("deaths_by_species",{}).items(): self.deaths_by_species[k]=v
        for item in data.get("population_history",[]): self.population_history.append(tuple(item))
        for item in data.get("biodiversity_history",[]): self.biodiversity_history.append(tuple(item))
