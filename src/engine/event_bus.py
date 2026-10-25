from __future__ import annotations
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class GameEvent:
    name:   str
    data:   Dict[str, Any] = field(default_factory=dict)
    tick:   int = 0
    source: Optional[str] = None

class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._queue: List[GameEvent] = []
        self._wildcard: List[Callable] = []
        self.total_published = 0
        self.total_delivered = 0

    def subscribe(self, event_name: str, handler: Callable) -> None:
        if event_name == "*":
            self._wildcard.append(handler)
        else:
            self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        if event_name == "*":
            if handler in self._wildcard: self._wildcard.remove(handler)
        else:
            lst = self._handlers.get(event_name, [])
            if handler in lst: lst.remove(handler)

    def publish(self, event_name: str, data=None, tick: int = 0, source=None) -> None:
        self._deliver(GameEvent(name=event_name, data=data or {}, tick=tick, source=source))

    def queue(self, event_name: str, data=None, tick: int = 0, source=None) -> None:
        self._queue.append(GameEvent(name=event_name, data=data or {}, tick=tick, source=source))

    def flush(self, current_tick: int = 0) -> int:
        delivered = 0
        events, self._queue = self._queue, []
        for event in events:
            event.tick = event.tick or current_tick
            self._deliver(event)
            delivered += 1
        return delivered

    def clear_queue(self) -> None:
        self._queue.clear()

    @property
    def queue_length(self) -> int:
        return len(self._queue)

    def _deliver(self, event: GameEvent) -> None:
        self.total_published += 1
        targets = self._handlers.get(event.name, []) + self._wildcard
        for handler in targets:
            try:
                handler(event)
                self.total_delivered += 1
            except Exception as exc:
                logger.error("EventBus handler error on '%s': %s", event.name, exc, exc_info=True)
