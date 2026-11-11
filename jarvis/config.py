"""
J.A.R.V.I.S. Configuration and Path Management
"""
import os
import json
import pathlib

ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
CONFIG_FILE = ROOT_DIR / "config.json"
NOTES_DIR = ROOT_DIR / "notes"
VIEWER_DIR = ROOT_DIR / "viewer"
SCREENSHOTS_DIR = ROOT_DIR / "storage" / "screenshots"
DATA_DIR = ROOT_DIR / "storage" / "data"
PROFILE_FILE = ROOT_DIR / "JARVIS-User-Context-Profile.md"

# Ensure runtime directories exist
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "api_key": "",
    "model": "gemini-3.5-flash-lite",
    "fallback_models": ["gemini-3.5-flash", "gemini-2.5-flash"],
    "fish_audio": {
        "api_key": "",
        "model": "s2.1-pro-free",
        "reference_id": "05b36da8574341d0803391491850db20"
    },
    "port": 4700,
    "system_personality": "butler",
    "risk_level_threshold": "consequential"
}


def load_config():
    """Load configuration from config.json with fallback defaults."""
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
        return DEFAULT_CONFIG.copy()

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        merged = DEFAULT_CONFIG.copy()
        merged.update(data)
        return merged
    except Exception as e:
        print(f"  ⚠ Error reading config.json: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(new_config):
    """Save updated configuration to config.json."""
    CONFIG_FILE.write_text(json.dumps(new_config, indent=2), encoding="utf-8")
    return new_config


def load_user_profile():
    """Reads the JARVIS User Context Profile for grounding personal context."""
    if PROFILE_FILE.exists():
        return PROFILE_FILE.read_text(encoding="utf-8", errors="replace")
    return ""
