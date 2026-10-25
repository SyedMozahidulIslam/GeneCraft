from __future__ import annotations
import json, logging, uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from engine.config_manager import ConfigManager
from engine.event_bus import EventBus

logger=logging.getLogger(__name__)

class SaveSystem:
    FORMAT_VERSION="1.0.0"
    def __init__(self,config,bus):
        self.config=config; self.bus=bus
        self.save_dir=Path(config.get("save.save_directory","saves"))
        self.max_slots=config.get("save.max_slots",5) or 5
        self.save_dir.mkdir(exist_ok=True)
        logger.info("SaveSystem initialised (dir=%s).",self.save_dir)

    def save(self,slot_name,data):
        payload={"format_version":self.FORMAT_VERSION,"save_id":str(uuid.uuid4()),
                 "slot_name":slot_name,"timestamp":datetime.utcnow().isoformat(),"data":data}
        path=self._slot_path(slot_name)
        try:
            with open(path,"w",encoding="utf-8") as fh: json.dump(payload,fh,indent=2)
            logger.info("SaveSystem: saved slot '%s'.",slot_name)
            self.bus.queue("save:saved",{"slot":slot_name}); return True
        except OSError as exc: logger.error("SaveSystem: failed: %s",exc); return False

    def load(self,slot_name):
        path=self._slot_path(slot_name)
        if not path.exists(): return None
        try:
            with open(path,"r",encoding="utf-8") as fh: payload=json.load(fh)
            logger.info("SaveSystem: loaded slot '%s'.",slot_name)
            self.bus.queue("save:loaded",{"slot":slot_name})
            return payload.get("data",{})
        except Exception as exc: logger.error("SaveSystem: read failed: %s",exc); return None

    def delete(self,slot_name):
        path=self._slot_path(slot_name)
        if path.exists(): path.unlink(); self.bus.queue("save:deleted",{"slot":slot_name}); return True
        return False

    def slot_info(self,slot_name):
        path=self._slot_path(slot_name)
        if not path.exists(): return None
        try:
            with open(path,"r") as fh: payload=json.load(fh)
            data=payload.get("data",{})
            return {"slot_name":slot_name,"timestamp":payload.get("timestamp",""),"world_tick":data.get("world_tick",0),
                    "game_mode":data.get("game_state",""),"species_count":len(data.get("species",[])),"size_kb":path.stat().st_size//1024}
        except: return None

    def list_slots(self): return [info for name in self._all_slot_names() if (info:=self.slot_info(name))]
    def quick_save(self,data): return self.save("__quicksave__",data)
    def quick_load(self): return self.load("__quicksave__")
    def auto_save(self,data): return self.save("__autosave__",data)
    def _slot_path(self,name): return self.save_dir/f"{name.replace('/','_')}.json"
    def _all_slot_names(self): return ["__autosave__","__quicksave__"]+[f"slot_{i}" for i in range(1,self.max_slots+1)]
