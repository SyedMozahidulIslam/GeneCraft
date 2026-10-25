from __future__ import annotations
import uuid, random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Any

class LifeStage(Enum):
    JUVENILE=auto(); ADULT=auto(); ELDER=auto()

class BehaviorState(Enum):
    IDLE=auto(); EXPLORE=auto(); HUNT=auto(); EAT=auto(); FLEE=auto()
    SLEEP=auto(); REPRODUCE=auto(); MIGRATE=auto(); DEFEND=auto()

@dataclass
class Creature:
    creature_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    species_id:  str = ""
    species_name:str = "Unknown"
    x:    float = 0.0
    y:    float = 0.0
    genome: Any = field(default=None)    # Optional[Genome] — Any to avoid circular
    energy:     float = 100.0
    max_energy: float = 100.0
    health:     float = 100.0
    age:        int   = 0
    generation: int   = 0
    behavior:   BehaviorState = BehaviorState.IDLE
    life_stage: LifeStage     = LifeStage.JUVENILE
    target_x:   Optional[float] = None
    target_y:   Optional[float] = None
    target_id:  Optional[str]   = None
    reproduce_cooldown: int  = 0
    sleep_counter:      int  = 0
    is_alive:   bool = True
    in_group:   bool = False
    group_id:   Optional[str] = None

    @property
    def speed(self):
        if self.genome is None: return 1.0
        base = self.genome.physical.speed
        if self.life_stage == LifeStage.JUVENILE: base *= 0.6
        elif self.life_stage == LifeStage.ELDER:  base *= 0.75
        if self.energy_ratio < 0.3: base *= 0.7
        return max(0.1, base)

    @property
    def vision_range(self):
        if self.genome is None: return 3.0
        return self.genome.physical.vision * 2.0

    @property
    def attack_power(self):
        if self.genome is None: return 1.0
        return self.genome.physical.strength * 0.6 + self.genome.physical.bite_force * 0.4

    @property
    def defense(self):
        if self.genome is None: return 0.0
        return self.genome.physical.armor * 0.5

    @property
    def energy_ratio(self): return self.energy / self.max_energy if self.max_energy > 0 else 0.0
    @property
    def health_ratio(self): return self.health / 100.0
    @property
    def is_hungry(self): return self.energy_ratio < 0.4
    @property
    def is_critical(self): return self.energy_ratio < 0.15 or self.health_ratio < 0.2
    @property
    def can_reproduce(self):
        return (self.life_stage == LifeStage.ADULT and self.reproduce_cooldown <= 0
                and self.energy_ratio > 0.6 and self.is_alive)

    def tick(self):
        self.age += 1
        if self.reproduce_cooldown > 0: self.reproduce_cooldown -= 1
        if self.sleep_counter > 0:      self.sleep_counter -= 1
        self._metabolic_drain()
        self._update_life_stage()
        if self.genome and self.age >= self.genome.genetic.lifespan: self.is_alive = False
        if self.energy <= 0 or self.health <= 0: self.is_alive = False

    def _metabolic_drain(self):
        if self.genome is None:
            base_cost = 1.0
        else:
            eff = self.genome.metabolic.energy_efficiency
            base_cost = (1.0 + self.genome.physical.size * 0.08
                         + self.genome.physical.speed * 0.04
                         + self.genome.behavioral.intelligence * 0.03) / eff
        mods = {BehaviorState.SLEEP:0.3, BehaviorState.IDLE:0.5, BehaviorState.EXPLORE:0.8,
                BehaviorState.EAT:0.6, BehaviorState.REPRODUCE:1.2, BehaviorState.HUNT:1.5,
                BehaviorState.FLEE:1.8, BehaviorState.DEFEND:1.4, BehaviorState.MIGRATE:1.0}
        self.energy = max(0.0, self.energy - base_cost * mods.get(self.behavior, 1.0))

    def _update_life_stage(self):
        if self.genome is None: return
        ls = self.genome.genetic.lifespan
        if self.age < ls * 0.15:  self.life_stage = LifeStage.JUVENILE
        elif self.age < ls * 0.75: self.life_stage = LifeStage.ADULT
        else:                       self.life_stage = LifeStage.ELDER

    def eat(self, food_energy):        self.energy = min(self.max_energy, self.energy + food_energy)
    def take_damage(self, damage):
        eff = max(0.0, damage - self.defense); self.health = max(0.0, self.health - eff)
        if self.health <= 0: self.is_alive = False
    def heal(self, amount):            self.health = min(100.0, self.health + amount)
    def move_to(self, nx, ny):         self.x = nx; self.y = ny

    def to_dict(self):
        return {"creature_id":self.creature_id, "species_id":self.species_id,
                "species_name":self.species_name, "x":self.x, "y":self.y,
                "genome":self.genome.to_dict() if self.genome else None,
                "energy":self.energy, "health":self.health, "age":self.age,
                "generation":self.generation, "behavior":self.behavior.name,
                "life_stage":self.life_stage.name, "is_alive":self.is_alive}

    @classmethod
    def from_dict(cls, d):
        from genetics.genome import Genome
        c = cls(creature_id=d.get("creature_id", str(uuid.uuid4())[:12]),
                species_id=d.get("species_id",""), species_name=d.get("species_name",""),
                x=d.get("x",0.0), y=d.get("y",0.0),
                energy=d.get("energy",100.0), health=d.get("health",100.0),
                age=d.get("age",0), generation=d.get("generation",0),
                is_alive=d.get("is_alive",True))
        if d.get("genome"): c.genome = Genome.from_dict(d["genome"])
        try:
            c.behavior   = BehaviorState[d.get("behavior","IDLE")]
            c.life_stage = LifeStage[d.get("life_stage","JUVENILE")]
        except KeyError: pass
        return c

    def __repr__(self):
        return f"Creature({self.species_name}#{self.creature_id[:6]},pos=({self.x:.0f},{self.y:.0f}),E={self.energy:.0f})"
