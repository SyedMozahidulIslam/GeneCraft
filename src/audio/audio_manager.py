from __future__ import annotations
import logging, math, random
from pathlib import Path
from typing import Dict, Optional
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus, GameEvent

logger=logging.getLogger(__name__)
SAMPLE_RATE=44100

class AudioManager:
    def __init__(self,config,bus):
        self.config=config; self.bus=bus
        self.enabled=config.get("audio.enabled",True)
        self.master_vol=config.get("audio.master_volume",0.8) or 0.8
        self.music_vol=config.get("audio.music_volume",0.4) or 0.4
        self.sfx_vol=config.get("audio.sfx_volume",0.7) or 0.7
        self.ui_vol=config.get("audio.ui_volume",0.5) or 0.5
        self._assets_dir=Path(config.get("paths.assets","assets"))
        self._current_music=None
        self._sound_cache:Dict={}
        self._pygame_ok=False
        if self.enabled: self._init_mixer()
        bus.subscribe("research:unlocked",lambda e:self.play_sfx("research_unlock"))
        bus.subscribe("species:extinct",lambda e:self.play_sfx("extinction"))
        bus.subscribe("evolution:adaptation",lambda e:self.play_sfx("evolution"))
        bus.subscribe("achievement:unlocked",lambda e:self.play_sfx("achievement"))
        bus.subscribe("disaster:started",lambda e:self.play_sfx("disaster_alert"))
        bus.subscribe("species:speciation",lambda e:self.play_sfx("speciation"))
        logger.info("AudioManager initialised (enabled=%s).",self.enabled)

    def _init_mixer(self):
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE,size=-16,channels=2,buffer=512)
            pygame.mixer.set_num_channels(8)
            self._pygame_ok=True
        except Exception as exc:
            logger.warning("AudioManager: mixer init failed: %s",exc); self.enabled=False

    def play_music(self,track_name,loop=True):
        if not self.enabled or not self._pygame_ok or track_name==self._current_music: return
        import pygame
        for ext in (".ogg",".mp3",".wav"):
            path=self._assets_dir/"audio"/"music"/f"{track_name}{ext}"
            if path.exists():
                try:
                    pygame.mixer.music.load(str(path))
                    pygame.mixer.music.set_volume(self.music_vol*self.master_vol)
                    pygame.mixer.music.play(-1 if loop else 0)
                    self._current_music=track_name; return
                except: pass
        logger.debug("AudioManager: music '%s' not found.",track_name)

    def stop_music(self):
        if self.enabled and self._pygame_ok:
            import pygame; pygame.mixer.music.fadeout(2000)
            self._current_music=None

    def play_sfx(self,sfx_name):
        if not self.enabled or not self._pygame_ok: return
        sound=self._get_sound(sfx_name)
        if sound:
            try: sound.play()
            except: pass

    def play_ui(self,ui_name="click"): self.play_sfx(ui_name)

    def _get_sound(self,name):
        if name in self._sound_cache: return self._sound_cache[name]
        import pygame
        for ext in (".ogg",".wav",".mp3"):
            path=self._assets_dir/"audio"/"sfx"/f"{name}{ext}"
            if path.exists():
                try:
                    snd=pygame.mixer.Sound(str(path)); self._sound_cache[name]=snd; return snd
                except: pass
        snd=self._synthesise(name)
        if snd: self._sound_cache[name]=snd
        return snd

    def _synthesise(self,name):
        if not self.enabled or not self._pygame_ok: return None
        try:
            import pygame, numpy as np
            profiles={"click":(440,0.05,0.3),"research_unlock":(880,0.3,0.5),"extinction":(220,0.5,0.4),
                      "evolution":(660,0.35,0.5),"achievement":(1046,0.4,0.6),"disaster_alert":(330,0.4,0.6),
                      "speciation":(528,0.3,0.4),"hover":(300,0.04,0.15)}
            freq,dur,vol=profiles.get(name,(440,0.1,0.3))
            n=int(SAMPLE_RATE*dur); t=np.linspace(0,dur,n,dtype=np.float32)
            wave=np.sin(2*np.pi*freq*t)
            env=np.ones(n,dtype=np.float32)
            atk=min(int(0.01*SAMPLE_RATE),n//4); rel=min(int(0.05*SAMPLE_RATE),n//4)
            env[:atk]=np.linspace(0,1,atk); env[-rel:]=np.linspace(1,0,rel)
            wave=(wave*env*32767).astype(np.int16)
            stereo=np.column_stack([wave,wave])
            snd=pygame.sndarray.make_sound(stereo); snd.set_volume(vol); return snd
        except Exception as exc:
            logger.debug("AudioManager: synthesis failed for '%s': %s",name,exc); return None

    def set_master_volume(self,vol):
        self.master_vol=max(0.0,min(1.0,vol))
        if self.enabled and self._pygame_ok:
            import pygame; pygame.mixer.music.set_volume(self.music_vol*self.master_vol)

    def tick(self,world_tick): pass

    def shutdown(self):
        if self.enabled and self._pygame_ok:
            import pygame; pygame.mixer.music.stop(); pygame.mixer.stop()
