"""
Capability 112: Event Monitoring
Thread-safe publish/subscribe event bus providing topic filtering,
pattern-based subscriptions, audit trailing, and historical replay.
"""
from __future__ import annotations

import fnmatch
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable


@dataclass
class Event:
    """Discrete system or autonomy event."""
    event_id: str
    topic: str
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, CRITICAL
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutonomousEventBus:
    """
    Capability 112: Autonomous Event Bus & Monitor.
    Enables loosely coupled, asynchronous communication across autonomy subsystems.
    """

    def __init__(self, max_history: int = 1000):
        self._subscriptions: Dict[str, Tuple[str, Callable[[Event], None]]] = {}  # sub_id -> (pattern, handler)
        self._history: List[Event] = []
        self._lock = threading.Lock()
        self.max_history = max_history

    def subscribe(self, pattern: str, handler: Callable[[Event], None]) -> str:
        """Subscribes a callable to events matching glob-style pattern (e.g. 'task.*', '*')."""
        sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        with self._lock:
            self._subscriptions[sub_id] = (pattern, handler)
        return sub_id

    def unsubscribe(self, sub_id: str) -> bool:
        """Removes an active subscription."""
        with self._lock:
            if sub_id in self._subscriptions:
                del self._subscriptions[sub_id]
                return True
        return False

    def publish(self, topic: str, source: str, payload: Optional[Dict[str, Any]] = None,
                priority: str = "NORMAL") -> Event:
        """Publishes an event to matching subscribers and logs it to audit history."""
        evt = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            topic=topic,
            source=source,
            payload=payload or {},
            priority=priority,
            timestamp=time.time()
        )

        with self._lock:
            self._history.append(evt)
            if len(self._history) > self.max_history:
                self._history.pop(0)
            subs_snapshot = list(self._subscriptions.values())

        # Dispatch to matching subscribers
        for pattern, handler in subs_snapshot:
            if fnmatch.fnmatch(topic, pattern):
                try:
                    handler(evt)
                except Exception:
                    pass  # Keep bus decoupled from subscriber errors

        return evt

    def get_history(self, pattern: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Queries historical events matching pattern."""
        with self._lock:
            events = list(self._history)

        if pattern:
            events = [e for e in events if fnmatch.fnmatch(e.topic, pattern)]

        return [e.to_dict() for e in events[-limit:]]

    def clear(self) -> None:
        """Clears subscriber list and history."""
        with self._lock:
            self._subscriptions.clear()
            self._history.clear()
