from __future__ import annotations
import copy, random, uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

def clamp(v,lo,hi): return max(lo,min(hi,v))

_GENE_RANGES: Dict[str,Tuple[float,float]] = {
    "speed":(0.1,10.0),"size":(0.1,10.0),"strength":(0.1,10.0),"vision":(1.0,10.0),
    "stamina":(1.0,10.0),"camouflage":(0.0,10.0),"armor":(0.0,10.0),"bite_force":(0.0,10.0),
    "aggression":(0.0,10.0),"intelligence":(1.0,10.0),"social_behavior":(0.0,10.0),
    "migration_instinct":(0.0,10.0),"curiosity":(0.0,10.0),"territorial":(0.0,10.0),"fearfulness":(0.0,10.0),
    "mutation_rate":(0.001,0.5),"adaptability":(0.0,10.0),"reproduction_rate":(0.1,10.0),
    "lifespan":(10,500),"disease_resistance":(0.0,10.0),
    "energy_efficiency":(0.1,3.0),"water_need":(0.1,3.0),
    "temp_tolerance_min":(-60.0,20.0),"temp_tolerance_max":(10.0,60.0),
}

@dataclass
class PhysicalGenes:
    speed:float=3.0; size:float=3.0; strength:float=3.0; vision:float=4.0
    stamina:float=4.0; camouflage:float=2.0; armor:float=1.0; bite_force:float=2.0
    def to_dict(self): return {"speed":self.speed,"size":self.size,"strength":self.strength,"vision":self.vision,"stamina":self.stamina,"camouflage":self.camouflage,"armor":self.armor,"bite_force":self.bite_force}
    @classmethod
    def from_dict(cls,d): return cls(**{k:v for k,v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class BehavioralGenes:
    aggression:float=3.0; intelligence:float=3.0; social_behavior:float=3.0
    migration_instinct:float=2.0; curiosity:float=3.0; territorial:float=3.0; fearfulness:float=4.0
    def to_dict(self): return {"aggression":self.aggression,"intelligence":self.intelligence,"social_behavior":self.social_behavior,"migration_instinct":self.migration_instinct,"curiosity":self.curiosity,"territorial":self.territorial,"fearfulness":self.fearfulness}
    @classmethod
    def from_dict(cls,d): return cls(**{k:v for k,v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class GeneticGenes:
    mutation_rate:float=0.05; adaptability:float=4.0; reproduction_rate:float=2.0
    lifespan:float=100.0; disease_resistance:float=3.0
    def to_dict(self): return {"mutation_rate":self.mutation_rate,"adaptability":self.adaptability,"reproduction_rate":self.reproduction_rate,"lifespan":self.lifespan,"disease_resistance":self.disease_resistance}
    @classmethod
    def from_dict(cls,d): return cls(**{k:v for k,v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class MetabolicGenes:
    energy_efficiency:float=1.0; water_need:float=1.0
    temp_tolerance_min:float=-5.0; temp_tolerance_max:float=35.0
    def to_dict(self): return {"energy_efficiency":self.energy_efficiency,"water_need":self.water_need,"temp_tolerance_min":self.temp_tolerance_min,"temp_tolerance_max":self.temp_tolerance_max}
    @classmethod
    def from_dict(cls,d): return cls(**{k:v for k,v in d.items() if k in cls.__dataclass_fields__})

class Genome:
    __slots__=("physical","behavioral","genetic","metabolic","genome_id")
    def __init__(self,physical=None,behavioral=None,genetic=None,metabolic=None):
        self.physical=physical or PhysicalGenes()
        self.behavioral=behavioral or BehavioralGenes()
        self.genetic=genetic or GeneticGenes()
        self.metabolic=metabolic or MetabolicGenes()
        self.genome_id=str(uuid.uuid4())[:8]

    def get(self,gene_name):
        for cat in (self.physical,self.behavioral,self.genetic,self.metabolic):
            if hasattr(cat,gene_name): return getattr(cat,gene_name)
        return None

    def set(self,gene_name,value):
        lo,hi=_GENE_RANGES.get(gene_name,(0.0,10.0))
        value=clamp(value,lo,hi)
        for cat in (self.physical,self.behavioral,self.genetic,self.metabolic):
            if hasattr(cat,gene_name): setattr(cat,gene_name,value); return

    def all_genes(self):
        d={}
        d.update(self.physical.to_dict()); d.update(self.behavioral.to_dict())
        d.update(self.genetic.to_dict()); d.update(self.metabolic.to_dict())
        return d

    def crossover(self,other):
        child=Genome(); genes=self.all_genes(); og=other.all_genes()
        for gene in genes: child.set(gene, genes[gene] if random.random()<0.5 else og[gene])
        child._mutate(); child.genome_id=str(uuid.uuid4())[:8]
        return child

    def _mutate(self):
        rate=self.genetic.mutation_rate
        for gene,value in self.all_genes().items():
            if random.random()<rate:
                lo,hi=_GENE_RANGES.get(gene,(0.0,10.0))
                self.set(gene,value+random.gauss(0,(hi-lo)*0.05))

    def clone(self):
        c=copy.deepcopy(self); c.genome_id=str(uuid.uuid4())[:8]; return c

    def divergence(self,other):
        mine=self.all_genes(); theirs=other.all_genes(); total=0.0
        for gene in mine:
            lo,hi=_GENE_RANGES.get(gene,(0.0,10.0)); span=hi-lo or 1.0
            total+=abs(mine[gene]-theirs.get(gene,mine[gene]))/span
        return total

    def fitness_score(self,food_ratio=1.0,temp_current=20.0,biome_pressures=None):
        score=food_ratio*0.4
        t_min=self.metabolic.temp_tolerance_min; t_max=self.metabolic.temp_tolerance_max
        if t_min<=temp_current<=t_max: temp_score=1.0
        else:
            dist=min(abs(temp_current-t_min),abs(temp_current-t_max))
            temp_score=max(0.0,1.0-dist/20.0)
        score+=temp_score*0.3
        phys=(self.physical.speed+self.physical.stamina+self.physical.strength)/30.0
        score+=phys*0.2; score+=(self.genetic.adaptability/10.0)*0.1
        if biome_pressures:
            for gene,mod in biome_pressures.items():
                val=self.get(gene)
                if val is not None: score+=(val/10.0)*mod*0.05
        return clamp(score,0.0,1.0)

    def to_dict(self):
        return {"genome_id":self.genome_id,"physical":self.physical.to_dict(),"behavioral":self.behavioral.to_dict(),"genetic":self.genetic.to_dict(),"metabolic":self.metabolic.to_dict()}

    @classmethod
    def from_dict(cls,d):
        g=cls(physical=PhysicalGenes.from_dict(d.get("physical",{})),behavioral=BehavioralGenes.from_dict(d.get("behavioral",{})),genetic=GeneticGenes.from_dict(d.get("genetic",{})),metabolic=MetabolicGenes.from_dict(d.get("metabolic",{})))
        g.genome_id=d.get("genome_id",g.genome_id); return g

    def __repr__(self):
        return f"Genome(id={self.genome_id},spd={self.physical.speed:.1f},sz={self.physical.size:.1f},int={self.behavioral.intelligence:.1f})"
