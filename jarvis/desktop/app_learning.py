"""
Capability 28: Application Learning Subsystem for J.A.R.V.I.S.
Tracks user application usage frequencies, session durations, window layout habits,
and generates intelligent automated workflow recommendations.
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class ApplicationLearningEngine:
    """Learns user desktop preferences, frequent apps, and window layout habits."""

    def __init__(self, profile_path: Optional[str] = None):
        if profile_path is None:
            self.profile_path = Path("storage/app_learning_profile.json")
        else:
            self.profile_path = Path(profile_path)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        self._profile: Dict[str, Any] = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        if self.profile_path.exists():
            try:
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "app_frequencies": {},
            "window_preferences": {},
            "recent_launches": [],
            "learned_workflows": [],
        }

    def _save_profile(self):
        try:
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(self._profile, f, indent=2)
        except Exception:
            pass

    def record_app_launch(self, app_name: str) -> Dict[str, Any]:
        """Records an app launch event, incrementing frequency and timestamp."""
        app = app_name.lower().strip()
        freqs = self._profile.setdefault("app_frequencies", {})
        freqs[app] = freqs.get(app, 0) + 1

        launches = self._profile.setdefault("recent_launches", [])
        launches.append({"app": app, "timestamp": time.time()})
        if len(launches) > 100:
            launches.pop(0)

        self._save_profile()
        return {"status": "success", "app": app, "total_launches": freqs[app]}

    def record_window_placement(self, app_name: str, x: int, y: int, width: int, height: int):
        """Learns the user's preferred window dimensions for a given app."""
        app = app_name.lower().strip()
        prefs = self._profile.setdefault("window_preferences", {})
        prefs[app] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "updated_at": time.time(),
        }
        self._save_profile()
        return {"status": "success", "app": app, "geometry": prefs[app]}

    def get_preferred_geometry(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Returns the user's learned window geometry for an application if available."""
        app = app_name.lower().strip()
        return self._profile.get("window_preferences", {}).get(app)

    def get_top_frequent_apps(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns most frequently used applications."""
        freqs = self._profile.get("app_frequencies", {})
        sorted_apps = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        return [{"app": k, "launches": v} for k, v in sorted_apps[:limit]]

    def suggest_optimal_layout(self, active_apps: List[str]) -> Dict[str, Any]:
        """Recommends window layout based on learned user habits and active apps."""
        if len(active_apps) == 1:
            return {"recommended_preset": "maximize", "reason": "Single active application"}
        elif len(active_apps) == 2:
            return {"recommended_preset": "split_columns", "reason": "Two active applications - ideal for 50/50 dual workspace"}
        elif len(active_apps) >= 3:
            return {"recommended_preset": "grid_2x2", "reason": "Multi-tasking across 3+ applications"}
        return {"recommended_preset": "default", "reason": "No active applications"}


app_learning = ApplicationLearningEngine()
