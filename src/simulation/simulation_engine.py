from __future__ import annotations
import logging, random
from typing import Dict, List, Optional, Tuple
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus
from genetics.genetics_engine import GeneticsEngine
from species.creature import BehaviorState, Creature
from species.species_registry import SpeciesRegistry
from utils.math_utils import clamp, distance, distance_sq

logger=logging.getLogger(__name__)
_GRID_CELL=20

class SimulationEngine:
    def __init__(self,config,bus,world,genetics,species_registry,ai_engine):
        self.config=config; self.bus=bus; self.world=world
        self.genetics=genetics; self.registry=species_registry; self.ai=ai_engine
        self.max_total=config.get("simulation.max_creatures_total",5000)
        self.max_per_species=config.get("simulation.max_creatures_per_species",500)
        self.ai_batch_size=config.get("simulation.ai_batch_size",100)
        self.gen_eval_interval=config.get("genetics.fitness_eval_interval",10) or 10
        self._spatial:Dict[Tuple[int,int],List[str]]={}
        self._creature_map:Dict[str,Creature]={}
        logger.info("SimulationEngine initialised.")

    def tick(self,world_tick):
        self.world.tick(world_tick)
        self._rebuild_spatial()
        self._run_ai(world_tick)
        self._apply_movement()
        self._resolve_interactions(world_tick)
        self._tick_creatures()
        self._cleanup(world_tick)
        if world_tick%self.gen_eval_interval==0: self._run_genetics(world_tick)
        self._ensure_minimum_populations(world_tick)

    def _cell_key(self,x,y): return (int(x)//_GRID_CELL,int(y)//_GRID_CELL)

    def _rebuild_spatial(self):
        self._spatial.clear(); self._creature_map.clear()
        for species in self.registry.all_living():
            for c in species.creatures:
                if c.is_alive:
                    key=self._cell_key(c.x,c.y)
                    self._spatial.setdefault(key,[]).append(c.creature_id)
                    self._creature_map[c.creature_id]=c

    def _nearby_creatures(self,x,y,radius,exclude_id=None):
        cell_r=int(radius//_GRID_CELL)+1; cx,cy=int(x)//_GRID_CELL,int(y)//_GRID_CELL
        result=[]; r2=radius*radius
        for dy in range(-cell_r,cell_r+1):
            for dx in range(-cell_r,cell_r+1):
                for cid in self._spatial.get((cx+dx,cy+dy),[]):
                    if cid==exclude_id: continue
                    c=self._creature_map.get(cid)
                    if c and distance_sq(x,y,c.x,c.y)<=r2: result.append(c)
        return result

    def _run_ai(self,tick):
        all_alive=list(self._creature_map.values())
        if not all_alive: return
        start=(tick*self.ai_batch_size)%max(1,len(all_alive))
        end=start+self.ai_batch_size
        batch=all_alive[start:end]
        if end>len(all_alive): batch+=all_alive[:end-len(all_alive)]
        for c in batch:
            if not c.is_alive: continue
            nearby=self._nearby_creatures(c.x,c.y,c.vision_range,exclude_id=c.creature_id)
            tile=self.world.get_tile(int(c.x),int(c.y))
            self.ai.decide(c,nearby,tile,tick)

    def _apply_movement(self):
        for c in self._creature_map.values():
            if not c.is_alive or c.behavior==BehaviorState.SLEEP: continue
            if c.target_x is None or c.target_y is None: continue
            dx=c.target_x-c.x; dy=c.target_y-c.y
            dist=(dx*dx+dy*dy)**0.5; step=c.speed*0.5
            if dist<=step: c.x,c.y=c.target_x,c.target_y
            else: c.x+=dx/dist*step; c.y+=dy/dist*step
            c.x=clamp(c.x,0,self.world.width-1); c.y=clamp(c.y,0,self.world.height-1)

    def _resolve_interactions(self,tick):
        for c in list(self._creature_map.values()):
            if not c.is_alive: continue
            b=c.behavior
            if b==BehaviorState.EAT: self._do_eat(c,tick)
            elif b==BehaviorState.HUNT and c.target_id: self._do_hunt(c,tick)
            elif b==BehaviorState.REPRODUCE: self._do_reproduce(c,tick)

    def _do_eat(self,c,tick):
        tile=self.world.get_tile(int(c.x),int(c.y))
        if tile and tile.food_amount>0:
            eff=c.genome.metabolic.energy_efficiency if c.genome else 1.0
            gained=tile.consume_food(min(5.0,tile.food_amount))*10.0*eff
            c.eat(gained)

    def _do_hunt(self,c,tick):
        prey=self._creature_map.get(c.target_id)
        if not prey or not prey.is_alive: c.target_id=None; return
        if distance(c.x,c.y,prey.x,prey.y)>1.5: return
        atk=c.attack_power*random.uniform(0.7,1.3)
        prey.take_damage(max(0,atk-prey.defense)*15.0)
        if not prey.is_alive:
            size_b=(prey.genome.physical.size if prey.genome else 1.0)
            c.eat(size_b*30.0)
            tile=self.world.get_tile(int(prey.x),int(prey.y))
            if tile: tile.add_nutrient(size_b)
            c.target_id=None
            self.bus.queue("creature:killed",{"predator_species":c.species_id,"prey_species":prey.species_id,"tick":tick})

    def _do_reproduce(self,c,tick):
        if not c.can_reproduce: return
        species=self.registry.get(c.species_id)
        if not species or species.population>=self.max_per_species: return
        nearby=self._nearby_creatures(c.x,c.y,5.0,exclude_id=c.creature_id)
        from species.creature import LifeStage
        mates=[n for n in nearby if n.species_id==c.species_id and n.can_reproduce and n.life_stage==LifeStage.ADULT]
        if not mates: return
        mate=random.choice(mates)
        child_genome=c.genome.crossover(mate.genome) if (c.genome and mate.genome) else species.representative_genome.clone()
        child=species.spawn_creature(c.x,c.y,tick)
        child.genome=child_genome; child.generation=c.generation+1
        cd=int(100/max(0.1,c.genome.genetic.reproduction_rate if c.genome else 1))
        c.reproduce_cooldown=cd; mate.reproduce_cooldown=cd
        c.energy-=20.0; mate.energy-=20.0
        species.increment_generation()
        self.bus.queue("species:reproduced",{"species_id":c.species_id,"tick":tick})

    def _tick_creatures(self):
        for c in self._creature_map.values():
            if c.is_alive: c.tick()

    def _cleanup(self,tick):
        for species in self.registry.all_living():
            species.remove_dead(); species.record_population(tick)
            if species.population==0: self.registry.mark_extinct(species.species_id,tick,"population_zero")

    def _run_genetics(self,tick):
        biomes_cfg=self.config.get_section("biomes")
        for species in self.registry.all_living():
            if not species.genome_pool: continue
            biome=species.biomes[0] if species.biomes else "grassland"
            biome_data=biomes_cfg.get(biome,{})
            biome_pressure=biome_data.get("biome_pressure",{})
            temp=self.world.temperature_at(self.world.width//2,self.world.height//2)
            new_pool,events=self.genetics.process_species(
                species_id=species.species_id,genomes=species.genome_pool,
                population=species.population,food_ratio=species.food_ratio,
                temperature=temp,biome_pressure=biome_pressure,generation=species.generation,tick=tick)
            if "extinct" in events: self.registry.mark_extinct(species.species_id,tick,"fitness_collapse"); continue
            species.genome_pool=new_pool
            for ev in events:
                if ev.startswith("adaptation:"):
                    gene=ev.split(":")[1]
                    species.log_event(tick,"adaptation",f"{species.name} adapting '{gene}'",gene=gene)
                    self.bus.queue("evolution:adaptation",{"species_id":species.species_id,"gene":gene,"tick":tick})
                elif ev=="speciation" and len(species.genome_pool)>=2:
                    new_name=f"{species.name} Mk.II"
                    child_g=species.genome_pool[-1].clone()
                    self.registry.speciate(species.species_id,new_name,child_g,tick)

    def _ensure_minimum_populations(self,tick):
        for species in self.registry.all_living():
            if species.population==0 and tick-species.created_tick<10:
                biome=species.biomes[0] if species.biomes else None
                tile=(self.world.random_tile_in_biome(biome) if biome else self.world.random_passable_tile())
                if tile:
                    initial=max(5,int(species.representative_genome.genetic.reproduction_rate*3))
                    for _ in range(min(initial,20)): species.spawn_creature(tile.grid_x,tile.grid_y,tick)

    def total_creatures(self): return sum(s.population for s in self.registry.all_living())
    def get_creature(self,cid): return self._creature_map.get(cid)
