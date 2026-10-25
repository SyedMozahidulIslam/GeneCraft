from __future__ import annotations
import logging, random, math
from typing import List, Optional
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus

logger=logging.getLogger(__name__)

class BehaviorFSM:
    def __init__(self,config,bus):
        self.config=config; self.bus=bus

    def decide(self,creature,nearby,tile,tick):
        from species.creature import BehaviorState, LifeStage
        if not creature.is_alive or creature.genome is None:
            creature.behavior=BehaviorState.IDLE; return
        g=creature.genome

        threats=[c for c in nearby if c.species_id!=creature.species_id and c.genome
                 and c.genome.physical.size>g.physical.size*1.2 and c.genome.behavioral.aggression>5.0]
        prey_candidates=[c for c in nearby if c.species_id!=creature.species_id and c.genome
                         and c.genome.physical.size<=g.physical.size*1.3 and g.behavioral.aggression>5.0]
        mates=[c for c in nearby if c.species_id==creature.species_id and c.can_reproduce]

        # Priority 1: Flee from threat
        if threats and g.behavioral.fearfulness>3.0:
            creature.behavior=BehaviorState.FLEE
            t=threats[0]; dx=creature.x-t.x; dy=creature.y-t.y
            dist=max(0.01,(dx*dx+dy*dy)**0.5); fd=creature.vision_range*1.5
            creature.target_x=creature.x+(dx/dist)*fd; creature.target_y=creature.y+(dy/dist)*fd
            creature.target_id=None; return

        # Priority 2: Eat if on food and hungry
        if tile and tile.food_amount>2.0 and creature.is_hungry and g.behavioral.aggression<6.0:
            creature.behavior=BehaviorState.EAT
            creature.target_x=creature.x; creature.target_y=creature.y; creature.target_id=None; return

        # Priority 3: Hunt if carnivore and hungry
        if creature.is_hungry and g.behavioral.aggression>4.0 and prey_candidates and g.physical.strength>2.0:
            prey=min(prey_candidates,key=lambda c:(c.x-creature.x)**2+(c.y-creature.y)**2)
            creature.behavior=BehaviorState.HUNT
            creature.target_x=prey.x; creature.target_y=prey.y; creature.target_id=prey.creature_id; return

        # Priority 4: Critical - seek food
        if creature.is_critical:
            creature.behavior=BehaviorState.EXPLORE
            creature.target_x=creature.x+random.uniform(-8,8); creature.target_y=creature.y+random.uniform(-8,8)
            creature.target_id=None; return

        # Priority 5: Reproduce
        if creature.can_reproduce and mates:
            creature.behavior=BehaviorState.REPRODUCE
            mate=random.choice(mates)
            creature.target_x=mate.x; creature.target_y=mate.y; creature.target_id=mate.creature_id; return

        # Priority 6: Defend territory
        intruders=[c for c in nearby if c.species_id!=creature.species_id and c not in threats]
        if g.behavioral.territorial>6.0 and intruders and creature.life_stage==LifeStage.ADULT:
            intruder=intruders[0]
            creature.behavior=BehaviorState.DEFEND
            creature.target_x=intruder.x; creature.target_y=intruder.y; creature.target_id=intruder.creature_id; return

        # Priority 7: Migrate seasonally
        if g.behavioral.migration_instinct>5.0 and tick%91<5 and random.random()<g.behavioral.migration_instinct/30.0:
            creature.behavior=BehaviorState.MIGRATE
            angle=(hash(creature.species_id)%360)*0.01745
            creature.target_x=creature.x+math.cos(angle)*40; creature.target_y=creature.y+math.sin(angle)*40
            creature.target_id=None; return

        # Priority 8: Sleep if low energy
        if creature.energy_ratio<0.25 and creature.sleep_counter<=0:
            creature.behavior=BehaviorState.SLEEP; creature.sleep_counter=5
            creature.target_x=creature.x; creature.target_y=creature.y; return

        # Priority 9: Explore
        if creature.target_x is None or random.random()<0.05*g.behavioral.curiosity:
            creature.behavior=BehaviorState.EXPLORE
            radius=g.behavioral.curiosity*3.0
            creature.target_x=creature.x+random.uniform(-radius,radius)
            creature.target_y=creature.y+random.uniform(-radius,radius); creature.target_id=None; return

        # Priority 10: Idle
        creature.behavior=BehaviorState.IDLE
