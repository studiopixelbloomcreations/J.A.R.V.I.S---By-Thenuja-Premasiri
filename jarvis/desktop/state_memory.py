"""
Capability 26: Desktop State Memory Subsystem for J.A.R.V.I.S.
Records desktop workspace snapshots, persists state histories, calculates diffs
between sessions, and restores window coordinates on demand.
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from .windows import list_windows, get_active_window, move_resize_window, get_screen_geometry
from .mouse import get_cursor_position


class DesktopStateMemory:
    """Captures, stores, compares, and restores complete desktop arrangements."""

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir is None:
            self.storage_dir = Path("storage/desktop_states")
        else:
            self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Dict[str, Any]] = {}

    def capture_snapshot(self, snapshot_name: str) -> Dict[str, Any]:
        """Captures full current desktop state."""
        wins = list_windows()
        act = get_active_window()
        cur_x, cur_y = get_cursor_position()
        geo = get_screen_geometry()

        snapshot = {
            "name": snapshot_name,
            "timestamp": time.time(),
            "cursor": {"x": cur_x, "y": cur_y},
            "active_window": act,
            "geometry": geo,
            "windows": wins,
            "window_count": len(wins),
        }

        self._memory_cache[snapshot_name] = snapshot
        # Persist to disk
        out_file = self.storage_dir / f"{snapshot_name}.json"
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
        except Exception:
            pass

        return snapshot

    def load_snapshot(self, snapshot_name: str) -> Optional[Dict[str, Any]]:
        """Loads snapshot from in-memory cache or JSON storage."""
        if snapshot_name in self._memory_cache:
            return self._memory_cache[snapshot_name]

        out_file = self.storage_dir / f"{snapshot_name}.json"
        if out_file.exists():
            try:
                with open(out_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._memory_cache[snapshot_name] = data
                    return data
            except Exception:
                pass
        return None

    def list_snapshots(self) -> List[str]:
        """Lists names of all saved snapshots."""
        names = set(self._memory_cache.keys())
        for f in self.storage_dir.glob("*.json"):
            names.add(f.stem)
        return sorted(list(names))

    def diff_snapshots(self, snap1_name_or_data: Any, snap2_name_or_data: Any) -> Dict[str, Any]:
        """Calculates differences between two snapshots."""
        s1 = self._resolve_snapshot(snap1_name_or_data)
        s2 = self._resolve_snapshot(snap2_name_or_data)

        if not s1 or not s2:
            return {"status": "error", "message": "Could not resolve both snapshots for comparison"}

        w1_map = {w["title"]: w for w in s1.get("windows", [])}
        w2_map = {w["title"]: w for w in s2.get("windows", [])}

        closed_windows = [t for t in w1_map if t not in w2_map]
        new_windows = [t for t in w2_map if t not in w1_map]
        moved_windows = []

        for t in w1_map:
            if t in w2_map:
                w1 = w1_map[t]
                w2 = w2_map[t]
                if (w1["x"], w1["y"], w1["width"], w1["height"]) != (w2["x"], w2["y"], w2["width"], w2["height"]):
                    moved_windows.append({
                        "title": t,
                        "before": {"x": w1["x"], "y": w1["y"], "w": w1["width"], "h": w1["height"]},
                        "after": {"x": w2["x"], "y": w2["y"], "w": w2["width"], "h": w2["height"]},
                    })

        return {
            "status": "success",
            "closed_count": len(closed_windows),
            "closed_windows": closed_windows,
            "new_count": len(new_windows),
            "new_windows": new_windows,
            "moved_count": len(moved_windows),
            "moved_windows": moved_windows,
        }

    def restore_snapshot(self, snapshot_name: str) -> Dict[str, Any]:
        """Restores window positions recorded in the snapshot."""
        snap = self.load_snapshot(snapshot_name)
        if not snap:
            return {"status": "error", "message": f"Snapshot '{snapshot_name}' not found"}

        restored = []
        for w in snap.get("windows", []):
            res = move_resize_window(w["hwnd"], w["x"], w["y"], w["width"], w["height"])
            if res.get("status") == "success":
                restored.append(w["title"])

        return {
            "status": "success",
            "snapshot": snapshot_name,
            "restored_count": len(restored),
            "windows": restored,
        }

    def _resolve_snapshot(self, item: Any) -> Optional[Dict[str, Any]]:
        if isinstance(item, dict):
            return item
        if isinstance(item, str):
            return self.load_snapshot(item)
        return None


desktop_state_memory = DesktopStateMemory()
