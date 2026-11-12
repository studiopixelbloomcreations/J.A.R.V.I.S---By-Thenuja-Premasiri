"""
Capability 24: Environment Configuration Subsystem for J.A.R.V.I.S.
Inspects system and user environment variables, audits and validates PATH entries,
identifies active Python/development environments, and queries display configurations.
"""
import os
import sys
import platform
import winreg
from pathlib import Path
from typing import Dict, Any, List, Optional
from .windows import get_screen_geometry


class EnvironmentConfiguration:
    """Audits and manages OS environment configurations, PATH integrity, and runtimes."""

    def get_os_telemetry(self) -> Dict[str, Any]:
        """Returns OS version, architecture, and machine identification."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "processor": platform.processor(),
            "node": platform.node(),
            "python_version": sys.version.split()[0],
            "python_executable": sys.executable,
        }

    def audit_path_variable(self) -> Dict[str, Any]:
        """
        Audits the PATH environment variable for duplicate or nonexistent directories.
        """
        raw_path = os.environ.get("PATH", "")
        entries = [e.strip() for e in raw_path.split(os.pathsep) if e.strip()]

        valid_entries = []
        dead_entries = []
        duplicates = []
        seen = set()

        for entry in entries:
            norm = os.path.normpath(entry.lower())
            if norm in seen:
                duplicates.append(entry)
            else:
                seen.add(norm)

            if Path(entry).exists():
                valid_entries.append(entry)
            else:
                dead_entries.append(entry)

        return {
            "total_entries": len(entries),
            "valid_count": len(valid_entries),
            "dead_count": len(dead_entries),
            "dead_entries": dead_entries,
            "duplicate_count": len(duplicates),
            "duplicates": duplicates,
            "is_clean": (len(dead_entries) == 0 and len(duplicates) == 0),
        }

    def get_python_environment(self) -> Dict[str, Any]:
        """Detects if Python is running in a virtualenv or conda environment."""
        is_venv = (
            hasattr(sys, "real_prefix") or
            (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        )
        is_conda = "CONDA_PREFIX" in os.environ

        return {
            "executable": sys.executable,
            "prefix": sys.prefix,
            "is_virtualenv": is_venv,
            "is_conda": is_conda,
            "environment_path": os.environ.get("CONDA_PREFIX") or (sys.prefix if is_venv else None),
        }

    def get_display_environment(self) -> Dict[str, Any]:
        """Returns desktop display configuration and virtual screen geometry."""
        geo = get_screen_geometry()
        return {
            "primary_resolution": f"{geo['primary']['width']}x{geo['primary']['height']}",
            "virtual_desktop": geo["virtual"],
        }

    def get_environment_variable(self, name: str) -> Optional[str]:
        return os.environ.get(name)


env_config = EnvironmentConfiguration()
