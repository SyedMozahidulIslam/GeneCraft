from __future__ import annotations
import json, logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)
_CONFIG_FILES = ["settings.json","biomes.json","genes.json","research_tree.json","achievements.json"]

class ConfigManager:
    def __init__(self, config_dir: str = "config") -> None:
        self._config_dir = Path(config_dir)
        self._data: Dict[str, Any] = {}
        self._loaded = False

    def load_all(self) -> None:
        for filename in _CONFIG_FILES:
            path = self._config_dir / filename
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    raw = json.load(fh)
                raw = {k: v for k, v in raw.items() if not k.startswith("_")}
                self._data.update(raw)
                logger.debug("Loaded config: %s", path)
            except FileNotFoundError:
                logger.warning("Config file not found: %s", path)
            except json.JSONDecodeError as exc:
                logger.error("JSON parse error in %s: %s", path, exc)
        self._loaded = True
        logger.info("ConfigManager: loaded (%d top-level keys).", len(self._data))

    def get(self, key: str, default: Any = None) -> Any:
        parts = key.split(".")
        node: Any = self._data
        for part in parts:
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    def set(self, key: str, value: Any) -> None:
        parts = key.split(".")
        node = self._data
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value

    def get_section(self, section: str) -> Dict[str, Any]:
        return self._data.get(section, {})

    def get_color(self, key: str) -> tuple:
        val = self.get(key)
        if isinstance(val, (list, tuple)) and len(val) >= 3:
            return tuple(int(c) for c in val[:3])
        return (255, 255, 255)

    def all_keys(self) -> list:
        return list(self._flatten(self._data))

    def _flatten(self, d: Dict, prefix: str = "") -> list:
        keys = []
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(self._flatten(v, full))
            else:
                keys.append(full)
        return keys
