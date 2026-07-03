# Eclipse Depths - Event Bus (publish / subscribe)

from __future__ import annotations
from collections import defaultdict
from typing import Callable, Any


class EventBus:
    """Decoupled pub/sub system used game-wide."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable) -> None:
        self._listeners[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        try:
            self._listeners[event].remove(callback)
        except ValueError:
            pass

    def publish(self, event: str, data: Any = None) -> None:
        for cb in list(self._listeners[event]):
            cb(data)
