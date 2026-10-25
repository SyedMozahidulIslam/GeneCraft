from __future__ import annotations
import logging, random, uuid
from typing import Dict, List, Optional, Tuple
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus
from genetics.genome import Genome
from utils.math_utils import clamp

logger = logging.getLogger(__name__)

class GeneticsEngine:
    def __init__(self,config,bus):
        self.config=config; self.bus=bus
        cfg=config.get_section("genetics") or {}
        self.speciation_divergence=cfg.get("speciation_genome_divergence",3.0)
        self.speciation_min_gens=cfg.get("speciation_min_generations",20)
        self.adaptation_threshold=cfg.get("adaptation_threshold",0.6)
        self.adaptation_boost=cfg.get("adaptation_boost",0.15)
        self.extinction_pop_thresh=cfg.get("extinction_population_threshold",3)
        self.extinction_starve_ticks=cfg.get("extinction_starvation_ticks",5)
        self.fitness_eval_interval=cfg.get("fitness_eval_interval",10)
        self._starvation_counter: Dict[str,int]={}
        self._last_fitness: Dict[str,float]={}
        logger.info("GeneticsEngine initialised.")

    def process_species(self,species_id,genomes,population,food_ratio,temperature,biome_pressure=None,generation=0,tick=0):
        events=[]
        if not genomes or population<=0: return genomes,events
        scored=[(g,g.fitness_score(food_ratio,temperature,biome_pressure)) for g in genomes]
        scored.sort(key=lambda x:x[1],reverse=True)
        avg_fitness=sum(s for _,s in scored)/len(scored)
        self._last_fitness[species_id]=avg_fitness
        if self._check_extinction(species_id,population,food_ratio,tick):
            events.append("extinct"); return [],events
        keep_n=max(1,int(len(scored)*0.7))
        survivors=[g for g,_ in scored[:keep_n]]
        new_genomes=list(survivors)
        if len(survivors)>=2 and food_ratio>0.3:
            offspring_count=self._offspring_count(survivors[0],food_ratio)
            for _ in range(offspring_count):
                pa=random.choice(survivors[:max(2,keep_n//2)])
                pb=random.choice(survivors)
                new_genomes.append(pa.crossover(pb))
        if len(new_genomes)>20: new_genomes=new_genomes[:20]
        if tick%self.fitness_eval_interval==0:
            adapted=self._detect_adaptation(new_genomes,biome_pressure or {})
            if adapted:
                events.append(f"adaptation:{adapted}")
                self._apply_adaptation_boost(new_genomes,adapted)
        if len(new_genomes)>=4 and generation>=self.speciation_min_gens:
            if self._check_speciation(new_genomes): events.append("speciation")
        return new_genomes,events

    def _offspring_count(self,genome,food_ratio):
        base=genome.genetic.reproduction_rate
        count=int(base*food_ratio*random.uniform(0.5,1.5))
        return clamp(count,0,5)

    def _check_extinction(self,species_id,population,food_ratio,tick):
        if population<=0: return True
        if population<=self.extinction_pop_thresh and food_ratio<0.2:
            self._starvation_counter[species_id]=self._starvation_counter.get(species_id,0)+1
            if self._starvation_counter[species_id]>=self.extinction_starve_ticks: return True
        else:
            self._starvation_counter[species_id]=0
        return False

    def _detect_adaptation(self,genomes,biome_pressure):
        if not biome_pressure or len(genomes)<3: return None
        for gene,pressure in biome_pressure.items():
            values=[g.get(gene) for g in genomes if g.get(gene) is not None]
            if len(values)<3: continue
            mid=5.0
            if pressure>0:
                if sum(1 for v in values if v>mid)/len(values)>=self.adaptation_threshold: return gene
            else:
                if sum(1 for v in values if v<mid)/len(values)>=self.adaptation_threshold: return gene
        return None

    def _apply_adaptation_boost(self,genomes,gene):
        values=[g.get(gene) for g in genomes if g.get(gene) is not None]
        if not values: return
        avg=sum(values)/len(values)
        direction=1.0 if avg>=5.0 else -1.0
        boost=self.adaptation_boost*direction
        for g in genomes:
            cur=g.get(gene)
            if cur is not None: g.set(gene,cur+boost)

    def _check_speciation(self,genomes):
        half=len(genomes)//2
        top=genomes[:half]; bot=genomes[half:]
        if not top or not bot: return False
        return top[0].divergence(bot[0])>=self.speciation_divergence

    def create_from_template(self,template):
        genome=Genome.from_dict({"genome_id":str(uuid.uuid4())[:8],**template})
        for gene,val in genome.all_genes().items():
            genome.set(gene,val+random.gauss(0,0.1))
        return genome

    def create_random(self,trophic_level=2):
        g=Genome()
        if trophic_level>=4:
            g.physical.speed=random.uniform(5,9); g.physical.strength=random.uniform(5,9)
            g.behavioral.aggression=random.uniform(5,8); g.behavioral.fearfulness=random.uniform(1,3)
        elif trophic_level==2:
            g.behavioral.fearfulness=random.uniform(5,9); g.behavioral.social_behavior=random.uniform(5,9)
            g.physical.speed=random.uniform(3,7)
        return g

    def get_fitness(self,species_id): return self._last_fitness.get(species_id,0.0)

    def genome_diversity(self,genomes):
        if len(genomes)<2: return 0.0
        sample=genomes[:min(10,len(genomes))]
        dists=[sample[i].divergence(sample[j]) for i in range(len(sample)) for j in range(i+1,len(sample))]
        return min(1.0,sum(dists)/len(dists)/self.speciation_divergence) if dists else 0.0

    def serialise(self): return {"starvation_counter":self._starvation_counter,"last_fitness":self._last_fitness}
    def deserialise(self,data):
        self._starvation_counter=data.get("starvation_counter",{})
        self._last_fitness=data.get("last_fitness",{})
