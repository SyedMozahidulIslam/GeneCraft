from __future__ import annotations
import random, uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
from genetics.genome import Genome
from species.creature import Creature
from utils.color_utils import species_color
from utils.math_utils import clamp

class SpeciesStatus(Enum):
    ALIVE=auto(); EXTINCT=auto()

@dataclass
class EvolutionEvent:
    tick:int; event_type:str; description:str
    gene:Optional[str]=None; value_delta:Optional[float]=None

class Species:
    def __init__(self,name,trophic_level,genome,biomes=None,species_id=None,ancestor_id=None,created_tick=0):
        self.species_id=species_id or str(uuid.uuid4())[:12]
        self.name=name
        self.trophic_level=clamp(trophic_level,1,5)
        self.genome_pool=[genome]
        self.creatures:List[Creature]=[]
        self.biomes=biomes or ["grassland"]
        self.ancestor_id=ancestor_id
        self.created_tick=created_tick
        self.status=SpeciesStatus.ALIVE
        self.extinction_tick:Optional[int]=None
        self.generation=0
        self.color=species_color(self.species_id)
        self.population_history:List[Tuple[int,int]]=[]
        self.evolution_events:List[EvolutionEvent]=[]
        self.total_born=0; self.total_died=0; self.peak_population=0
        self._food_acquired_this_tick=0.0; self._food_needed_this_tick=0.0

    @property
    def population(self): return len([c for c in self.creatures if c.is_alive])

    @property
    def food_ratio(self):
        if self._food_needed_this_tick<=0: return 1.0
        return clamp(self._food_acquired_this_tick/self._food_needed_this_tick,0.0,1.0)

    def is_extinct(self): return self.status==SpeciesStatus.EXTINCT

    @property
    def representative_genome(self): return self.genome_pool[0] if self.genome_pool else Genome()

    def add_genome(self,genome):
        self.genome_pool.append(genome)
        if len(self.genome_pool)>20: self.genome_pool=self.genome_pool[:20]

    def spawn_creature(self,x,y,tick=0):
        parent=random.choice(self.genome_pool)
        child_genome=parent.clone()
        for gene,val in child_genome.all_genes().items():
            child_genome.set(gene,val+random.gauss(0,0.05))
        c=Creature(species_id=self.species_id,species_name=self.name,
                   x=x+random.uniform(-2,2),y=y+random.uniform(-2,2),
                   genome=child_genome,generation=self.generation)
        c.max_energy=80.0+child_genome.physical.size*10.0
        c.energy=c.max_energy*0.8
        self.creatures.append(c); self.total_born+=1
        self.peak_population=max(self.peak_population,self.population)
        return c

    def remove_dead(self):
        dead=[c for c in self.creatures if not c.is_alive]
        self.total_died+=len(dead)
        self.creatures=[c for c in self.creatures if c.is_alive]
        return len(dead)

    def record_population(self,tick):
        self.population_history.append((tick,self.population))
        if len(self.population_history)>1000: self.population_history=self.population_history[-1000:]

    def log_event(self,tick,event_type,description,gene=None,delta=None):
        ev=EvolutionEvent(tick=tick,event_type=event_type,description=description,gene=gene,value_delta=delta)
        self.evolution_events.append(ev)
        if len(self.evolution_events)>500: self.evolution_events=self.evolution_events[-500:]
        return ev

    def mark_extinct(self,tick,cause="unknown"):
        self.status=SpeciesStatus.EXTINCT; self.extinction_tick=tick
        self.creatures.clear(); self.log_event(tick,"extinction",f"Extinct: {cause}")

    def increment_generation(self): self.generation+=1

    @property
    def is_plant(self): return self.trophic_level==1
    @property
    def is_herbivore(self): return self.trophic_level==2
    @property
    def is_predator(self): return self.trophic_level in (3,4)
    @property
    def is_apex(self): return self.trophic_level==5
    @property
    def trophic_label(self):
        return {1:"Producer",2:"Herbivore",3:"Omnivore",4:"Carnivore",5:"Apex Predator"}.get(self.trophic_level,"Unknown")

    def to_dict(self):
        return {"species_id":self.species_id,"name":self.name,"trophic_level":self.trophic_level,
                "biomes":self.biomes,"ancestor_id":self.ancestor_id,"created_tick":self.created_tick,
                "status":self.status.name,"extinction_tick":self.extinction_tick,"generation":self.generation,
                "color":list(self.color),"genome_pool":[g.to_dict() for g in self.genome_pool],
                "population_history":self.population_history[-100:],
                "total_born":self.total_born,"total_died":self.total_died,"peak_population":self.peak_population}

    @classmethod
    def from_dict(cls,d):
        genome=Genome.from_dict(d["genome_pool"][0]) if d.get("genome_pool") else Genome()
        sp=cls(name=d["name"],trophic_level=d.get("trophic_level",2),genome=genome,
               biomes=d.get("biomes",["grassland"]),species_id=d.get("species_id"),
               ancestor_id=d.get("ancestor_id"),created_tick=d.get("created_tick",0))
        sp.generation=d.get("generation",0); sp.color=tuple(d.get("color",[200,200,200]))
        sp.total_born=d.get("total_born",0); sp.total_died=d.get("total_died",0)
        sp.peak_population=d.get("peak_population",0)
        if d.get("status")=="EXTINCT":
            sp.status=SpeciesStatus.EXTINCT; sp.extinction_tick=d.get("extinction_tick")
        for g_dict in d.get("genome_pool",[])[1:]:
            sp.genome_pool.append(Genome.from_dict(g_dict))
        return sp

    def __repr__(self):
        return f"Species({self.name!r},pop={self.population},gen={self.generation},trophic={self.trophic_level})"
