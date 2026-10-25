from __future__ import annotations
import logging, sys, time
from enum import Enum, auto
from typing import Optional
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus

logger=logging.getLogger(__name__)

class GameState(Enum):
    MAIN_MENU=auto(); CAMPAIGN_SELECT=auto(); SANDBOX_SELECT=auto(); LOADING=auto()
    PLAYING=auto(); PAUSED=auto(); GENE_LAB=auto(); RESEARCH=auto(); STATISTICS=auto()
    ENCYCLOPEDIA=auto(); SETTINGS=auto(); SAVE_SCREEN=auto(); GAME_OVER=auto(); QUIT=auto()

class GameEngine:
    def __init__(self,config,skip_menu=False):
        self.config=config; self.bus=EventBus(); self.skip_menu=skip_menu
        self.state=GameState.MAIN_MENU; self.running=False
        self.world_tick=0; self.session_start_time=0.0; self._sim_speed=1; self._tick_accum=0.0
        self.simulation=None; self.world=None; self.genetics=None; self.ai_engine=None
        self.research=None; self.disasters=None; self.statistics=None; self.achievements=None
        self.save_system=None; self.audio=None; self.ui_engine=None; self.species_registry=None
        self.screen=None; self.clock=None
        self._target_fps=config.get("game.target_fps",60) or 60

    def run(self):
        try:
            self._init_pygame(); self._init_systems(); self._post_init()
            self.running=True; self.session_start_time=time.time()
            logger.info("GameEngine: entering main loop.")
            self._loop()
        finally:
            self._shutdown()

    def _init_pygame(self):
        import pygame
        pygame.init()
        try: pygame.mixer.init(frequency=44100,size=-16,channels=2,buffer=512)
        except: pass
        pygame.display.set_caption(self.config.get("window.title_bar","GeneCraft"))
        flags=0
        if self.config.get("window.resizable",True): flags|=pygame.RESIZABLE
        if self.config.get("window.fullscreen",False): flags|=pygame.FULLSCREEN
        w=self.config.get("window.width",1280) or 1280
        h=self.config.get("window.height",720) or 720
        self.screen=pygame.display.set_mode((w,h),flags)
        self.clock=pygame.time.Clock()
        logger.info("GameEngine: pygame window created (%dx%d).",w,h)

    def _init_systems(self):
        logger.info("GameEngine: initialising sub-systems…")
        from audio.audio_manager import AudioManager
        self.audio=AudioManager(self.config,self.bus)
        from world.world import World
        self.world=World(self.config,self.bus)
        from genetics.genetics_engine import GeneticsEngine
        self.genetics=GeneticsEngine(self.config,self.bus)
        from species.species_registry import SpeciesRegistry
        self.species_registry=SpeciesRegistry(self.config,self.bus)
        from ai.behavior_fsm import BehaviorFSM
        self.ai_engine=BehaviorFSM(self.config,self.bus)
        from simulation.simulation_engine import SimulationEngine
        self.simulation=SimulationEngine(config=self.config,bus=self.bus,world=self.world,
            genetics=self.genetics,species_registry=self.species_registry,ai_engine=self.ai_engine)
        from systems.research_system import ResearchSystem
        from systems.disaster_system import DisasterSystem
        from systems.statistics_system import StatisticsSystem
        from systems.achievement_system import AchievementSystem
        from systems.save_system import SaveSystem
        self.research=ResearchSystem(self.config,self.bus)
        self.disasters=DisasterSystem(self.config,self.bus,self.world)
        self.statistics=StatisticsSystem(self.config,self.bus,self.species_registry)
        self.achievements=AchievementSystem(self.config,self.bus)
        self.save_system=SaveSystem(self.config,self.bus)
        from ui.ui_engine import UIEngine
        self.ui_engine=UIEngine(config=self.config,bus=self.bus,screen=self.screen,engine=self)
        logger.info("GameEngine: all sub-systems initialised.")

    def _post_init(self):
        self.bus.subscribe("engine:quit",self._on_quit)
        self.bus.subscribe("engine:change_state",self._on_change_state)
        self.bus.subscribe("engine:set_speed",self._on_set_speed)
        if self.skip_menu:
            self._change_state(GameState.PLAYING); self.world.generate()
            if self.audio: self.audio.play_music("ecosystem_ambient")
        else:
            self._change_state(GameState.MAIN_MENU)
            if self.audio: self.audio.play_music("main_theme")

    def _loop(self):
        while self.running:
            dt_ms=self.clock.tick(self._target_fps); dt=dt_ms/1000.0
            self._process_events()
            if self.state==GameState.PLAYING: self._update_simulation(dt)
            self._render(); self.bus.flush(current_tick=self.world_tick)

    def _process_events(self):
        import pygame
        for event in pygame.event.get():
            if event.type==pygame.QUIT: self.running=False
            elif event.type==pygame.VIDEORESIZE:
                self.screen=pygame.display.get_surface()
                if self.ui_engine: self.ui_engine.on_resize(event.w,event.h)
            elif event.type==pygame.KEYDOWN: self._handle_keydown(event)
            if self.ui_engine: self.ui_engine.handle_event(event)

    def _handle_keydown(self,event):
        import pygame
        if event.key==pygame.K_ESCAPE:
            if self.state==GameState.PLAYING: self._change_state(GameState.PAUSED)
            elif self.state==GameState.PAUSED: self._change_state(GameState.PLAYING)
        elif event.key==pygame.K_F5: self.save_system.quick_save(self._build_save_data())
        elif event.key==pygame.K_F9:
            data=self.save_system.quick_load()
            if data: self._apply_save_data(data)
        elif event.key==pygame.K_SPACE: self._toggle_pause()
        elif event.key==pygame.K_1: self.bus.publish("engine:set_speed",{"speed":"normal"})
        elif event.key==pygame.K_2: self.bus.publish("engine:set_speed",{"speed":"fast"})
        elif event.key==pygame.K_3: self.bus.publish("engine:set_speed",{"speed":"faster"})
        elif event.key==pygame.K_4: self.bus.publish("engine:set_speed",{"speed":"ultra"})

    def _update_simulation(self,dt):
        speeds=self.config.get("simulation.speeds") or {}
        speed_names=list(speeds.keys())
        if speed_names and self._sim_speed<len(speed_names):
            speed_key=speed_names[self._sim_speed]; tps=speeds.get(speed_key,1)
        else: tps=1
        self._tick_accum+=tps*dt; ticks_to_run=int(self._tick_accum); self._tick_accum-=ticks_to_run
        for _ in range(max(1,ticks_to_run)):
            self.simulation.tick(self.world_tick); self.research.tick(self.world_tick)
            self.disasters.tick(self.world_tick); self.statistics.tick(self.world_tick)
            self.achievements.tick(self.world_tick); self.audio.tick(self.world_tick)
            self.world_tick+=1

    def _render(self):
        import pygame
        bg=self.config.get_color("colors.background") or (13,17,23)
        self.screen.fill(bg)
        if self.ui_engine: self.ui_engine.render(self.state,self.world_tick)
        pygame.display.flip()

    def _change_state(self,new_state):
        old=self.state; self.state=new_state
        logger.debug("GameEngine: %s -> %s",old.name,new_state.name)
        if self.ui_engine: self.ui_engine.on_state_change(old,new_state)
        self.bus.queue("engine:state_changed",{"old":old.name,"new":new_state.name})

    def _toggle_pause(self):
        if self.state==GameState.PLAYING: self._change_state(GameState.PAUSED)
        elif self.state==GameState.PAUSED: self._change_state(GameState.PLAYING)

    def _on_quit(self,_): self.running=False
    def _on_change_state(self,event):
        target=event.data.get("state")
        try: self._change_state(GameState[target])
        except KeyError: logger.warning("Unknown state: %s",target)
    def _on_set_speed(self,event):
        speeds=self.config.get("simulation.speeds") or {}; speed_names=list(speeds.keys())
        name=event.data.get("speed","normal")
        if name in speed_names: self._sim_speed=speed_names.index(name)

    def _build_save_data(self):
        return {"world_tick":self.world_tick,"game_state":self.state.name,
                "world":self.world.serialise() if self.world else {},
                "species":self.species_registry.serialise() if self.species_registry else [],
                "research":self.research.serialise() if self.research else {},
                "statistics":self.statistics.serialise() if self.statistics else {},
                "achievements":self.achievements.serialise() if self.achievements else []}

    def _apply_save_data(self,data):
        self.world_tick=data.get("world_tick",0)
        if self.world and "world" in data: self.world.deserialise(data["world"])
        if self.species_registry and "species" in data: self.species_registry.deserialise(data["species"])
        if self.research and "research" in data: self.research.deserialise(data["research"])
        if self.statistics and "statistics" in data: self.statistics.deserialise(data["statistics"])
        if self.achievements and "achievements" in data: self.achievements.deserialise(data["achievements"])
        logger.info("GameEngine: save data applied (tick=%d).",self.world_tick)

    def _shutdown(self):
        logger.info("GameEngine: shutting down…")
        if self.audio: self.audio.shutdown()
        import pygame; pygame.quit()
        logger.info("GameEngine: session duration %.1f s.",time.time()-self.session_start_time)

    @property
    def screen_size(self):
        if self.screen: return self.screen.get_size()
        return (self.config.get("window.width",1280) or 1280, self.config.get("window.height",720) or 720)
