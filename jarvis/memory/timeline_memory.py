"""
Timeline Memory Management Engine for J.A.R.V.I.S.
Capability 97: Timeline Memory

Provides temporal indexing of events, project milestones, note updates,
and personal context snapshots with time-window filtering and causality sequences.
"""

import json
import time
import uuid
import pathlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from ..config import DATA_DIR

TIMELINE_MEMORY_FILE = DATA_DIR / "timeline_memory.json"


class TimelineMemoryManager:
    """
    Chronological indexer for temporal events, life milestones,
    engineering releases, and operational activities.
    """

    def __init__(self, storage_path: Optional[pathlib.Path] = None):
        self.storage_path = storage_path or TIMELINE_MEMORY_FILE
        self.events: List[Dict[str, Any]] = []
        self.load()
        if not self.events:
            self._seed_default_events()

    def record_event(
        self,
        title: str,
        description: str,
        category: str = "general",
        timestamp: Optional[str] = None,
        importance: int = 3,
        entities: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Records a new temporal event in the timeline."""
        now_dt = datetime.now()
        iso_ts = timestamp or now_dt.isoformat()
        try:
            # Parse epoch
            epoch_val = datetime.fromisoformat(iso_ts).timestamp()
        except Exception:
            epoch_val = time.time()

        event = {
            "id": f"evt_{uuid.uuid4().hex[:8]}",
            "timestamp": iso_ts,
            "epoch": epoch_val,
            "title": title,
            "description": description,
            "category": category,
            "importance": max(1, min(5, importance)),
            "entities": entities or [],
            "tags": tags or [],
            "recorded_at": datetime.now().isoformat()
        }

        self.events.append(event)
        self._sort_events()
        self.save()
        return event

    def _sort_events(self):
        """Sorts events chronologically (oldest to newest)."""
        self.events.sort(key=lambda x: x.get("epoch", 0.0))

    def get_recent(self, limit: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns the most recent events, optionally filtered by category."""
        filtered = [e for e in self.events if not category or e.get("category", "").lower() == category.lower()]
        return list(reversed(filtered))[:limit]

    def query_range(self, start_epoch: float, end_epoch: float, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries events within a specific epoch time window."""
        results = []
        for e in self.events:
            if start_epoch <= e.get("epoch", 0.0) <= end_epoch:
                if not category or e.get("category", "").lower() == category.lower():
                    results.append(e)
        return results

    def get_events_for_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """Retrieves all timeline events associated with a specific entity."""
        e_clean = entity_id.lower().strip()
        results = []
        for e in self.events:
            ent_list = [x.lower() for x in e.get("entities", [])]
            if e_clean in ent_list:
                results.append(e)
        return results

    def export_timeline_markdown(self, limit: int = 20) -> str:
        """Formats events into a clean chronological Markdown ledger."""
        recent_events = self.get_recent(limit)
        # Present in chronological order
        chronological = list(reversed(recent_events))

        lines = [
            "# ⏱️ J.A.R.V.I.S. Chronological Timeline Memory",
            f"**Total Events Tracked:** {len(self.events)} | **Showing:** {len(chronological)}",
            ""
        ]

        for e in chronological:
            date_str = e["timestamp"][:10]
            stars = "★" * e.get("importance", 3)
            tags_str = f" `{'` `'.join(e.get('tags', []))}`" if e.get("tags") else ""
            lines.append(f"### {date_str} — {e['title']} ({stars})")
            lines.append(f"*{e.get('category', 'general').capitalize()} Sector*{tags_str}")
            lines.append(f"{e['description']}")
            if e.get("entities"):
                lines.append(f"**Linked Entities:** {', '.join(e['entities'])}")
            lines.append("")

        return "\n".join(lines)

    def _seed_default_events(self):
        """Seeds initial chronological baseline from user profile context."""
        self.record_event(
            "J.A.R.V.I.S. 2.0 Multi-Agent Swarm Inception",
            "Architected native swarm coordination with zero-polling wakeups and 150-skill dispatcher.",
            "project",
            "2026-11-12T10:00:00",
            5,
            ["jarvis", "thenuja"],
            ["swarm", "architecture", "v2"]
        )
        self.record_event(
            "User Context Profile Baseline Finalized",
            "Prepared comprehensive context documentation grounding assistance in Grade 10 education, VFX goals, and local system safety.",
            "personal",
            "2026-11-11T12:00:00",
            4,
            ["thenuja"],
            ["profile", "grounding"]
        )
        self.record_event(
            "Pixel Bloom Studios Character Continuity Milestone",
            "Drafted visual continuity pipeline for AI short films with DaVinci Resolve color consistency.",
            "creative",
            "2026-11-08T15:30:00",
            4,
            ["pixel_bloom", "vfx_short_films"],
            ["vfx", "continuity", "production"]
        )
        self.record_event(
            "St. Anne's Debating Circle Session",
            "Conducted preparation debate on ethical AI governance with St. Anne's College English Debating circle.",
            "school",
            "2026-11-05T14:00:00",
            3,
            ["st_annes_college", "english_debating"],
            ["debating", "education"]
        )
        self.save()

    def load(self):
        """Loads events from disk."""
        if self.storage_path and self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self.events = data.get("events", [])
                self._sort_events()
            except Exception:
                self.events = []

    def save(self):
        """Saves events to disk."""
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "event_count": len(self.events),
                "events": self.events
            }
            self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# Module singleton
timeline_memory = TimelineMemoryManager()
