from __future__ import annotations
import logging
from typing import Dict, List, Optional, Set
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus, GameEvent

logger=logging.getLogger(__name__)

class ResearchSystem:
    def __init__(self,config,bus):
        self.config=config; self.bus=bus
        self.points:float=0.0; self.unlocked:Set[str]=set()
        self.tree:dict=config.get_section("research_tree") or {}
        self._base_rp_per_tick=config.get("research.base_rp_per_tick",1.0) or 1.0
        self._milestone_bonus=config.get("research.milestone_rp_bonus",50) or 50
        self._evo_bonus=config.get("research.evolution_event_rp",25) or 25
        self._diversity_bonus=config.get("research.species_diversity_bonus_rp",10) or 10
        bus.subscribe("evolution:adaptation",self._on_evolution)
        bus.subscribe("species:speciation",self._on_evolution)
        bus.subscribe("species:registered",self._on_species_registered)
        bus.subscribe("chapter:complete",self._on_milestone)
        logger.info("ResearchSystem initialised.")

    def tick(self,world_tick): self.points+=self._base_rp_per_tick

    def can_unlock(self,node_id):
        node=self._get_node(node_id)
        if node is None or node_id in self.unlocked: return False
        if not all(p in self.unlocked for p in node.get("prerequisites",[])): return False
        return self.points>=node.get("cost",9999)

    def unlock(self,node_id):
        if not self.can_unlock(node_id): return False
        node=self._get_node(node_id); cost=node.get("cost",9999)
        self.points-=cost; self.unlocked.add(node_id)
        logger.info("ResearchSystem: unlocked '%s' (remaining RP=%.0f)",node_id,self.points)
        self.bus.queue("research:unlocked",{"node_id":node_id,"name":node.get("name",node_id),"unlocks":node.get("unlocks",{})})
        return True

    def is_unlocked(self,node_id): return node_id in self.unlocked

    def get_available_nodes(self):
        available=[]
        for tier_data in self.tree.values():
            if not isinstance(tier_data,dict): continue
            for node_id,node in tier_data.get("nodes",{}).items():
                if node_id not in self.unlocked and all(p in self.unlocked for p in node.get("prerequisites",[])):
                    available.append(node_id)
        return available

    def get_all_nodes(self):
        nodes=[]
        for tier_key,tier_data in self.tree.items():
            if not isinstance(tier_data,dict): continue
            tier_label=tier_data.get("label",tier_key); tier_color=tier_data.get("color",[200,200,200])
            for node_id,node in tier_data.get("nodes",{}).items():
                prereqs=node.get("prerequisites",[]); prereqs_met=all(p in self.unlocked for p in prereqs)
                nodes.append({**node,"node_id":node_id,"tier_label":tier_label,"tier_color":tier_color,
                               "is_unlocked":node_id in self.unlocked,"is_available":prereqs_met and node_id not in self.unlocked,
                               "is_locked":not prereqs_met,"can_afford":self.points>=node.get("cost",9999)})
        return nodes

    def add_points(self,amount,reason=""): self.points+=amount

    def _get_node(self,node_id):
        for tier_data in self.tree.values():
            if not isinstance(tier_data,dict): continue
            node=tier_data.get("nodes",{}).get(node_id)
            if node: return node
        return None

    def _on_evolution(self,e): self.add_points(self._evo_bonus,f"evolution:{e.name}")
    def _on_species_registered(self,e): self.add_points(20.0,"new_species")
    def _on_milestone(self,e): self.add_points(self._milestone_bonus,"chapter_complete")

    def serialise(self): return {"points":self.points,"unlocked":list(self.unlocked)}
    def deserialise(self,data):
        self.points=data.get("points",0.0); self.unlocked=set(data.get("unlocked",[]))
