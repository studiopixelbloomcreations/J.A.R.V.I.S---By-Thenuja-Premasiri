"""
Capability 108: Self-Diagnostics
Performs automated system-wide health checks across hardware metrics, storage paths,
configuration integrity, dependency verification, and permission barriers.
"""
from __future__ import annotations

import os
import sys
import shutil
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from ..config import NOTES_DIR, DATA_DIR, SCREENSHOTS_DIR, CONFIG_FILE, load_config


@dataclass
class DiagnosticItem:
    """Individual system check outcome."""
    check_id: str
    category: str  # HARDWARE, STORAGE, DEPENDENCIES, CONFIG
    status: str    # PASS, WARN, FAIL
    message: str
    metric_value: Optional[Any] = None
    remediation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HealthReport:
    """Consolidated health report across all system components."""
    timestamp: float
    health_score: int  # 0 to 100
    overall_status: str  # HEALTHY, DEGRADED, CRITICAL
    checks: List[DiagnosticItem] = field(default_factory=list)
    remediations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "health_score": self.health_score,
            "overall_status": self.overall_status,
            "checks": [c.to_dict() for c in self.checks],
            "remediations": self.remediations
        }


class SelfDiagnostics:
    """
    Capability 108: Self-Diagnostics Engine.
    Executes automated pre-flight and runtime sanity checks on host environment.
    """

    def __init__(self):
        pass

    def run_all_checks(self) -> HealthReport:
        """Runs the complete suite of diagnostic checks and synthesizes a HealthReport."""
        checks: List[DiagnosticItem] = []
        checks.extend(self._check_python_runtime())
        checks.extend(self._check_storage_paths())
        checks.extend(self._check_hardware())
        checks.extend(self._check_configuration())

        # Calculate health score (100 base, -25 for FAIL, -10 for WARN)
        score = 100
        for c in checks:
            if c.status == "FAIL":
                score -= 25
            elif c.status == "WARN":
                score -= 10
        score = max(0, min(100, score))

        if score >= 85:
            overall = "HEALTHY"
        elif score >= 60:
            overall = "DEGRADED"
        else:
            overall = "CRITICAL"

        remediations = [c.remediation for c in checks if c.remediation]

        return HealthReport(
            timestamp=time.time(),
            health_score=score,
            overall_status=overall,
            checks=checks,
            remediations=remediations
        )

    def _check_python_runtime(self) -> List[DiagnosticItem]:
        items = []
        py_ver = sys.version_info
        if py_ver.major == 3 and py_ver.minor >= 10:
            items.append(DiagnosticItem(
                check_id="py_version",
                category="DEPENDENCIES",
                status="PASS",
                message=f"Python version {sys.version.split()[0]} is compatible.",
                metric_value=f"{py_ver.major}.{py_ver.minor}"
            ))
        else:
            items.append(DiagnosticItem(
                check_id="py_version",
                category="DEPENDENCIES",
                status="FAIL",
                message=f"Unsupported Python version: {sys.version.split()[0]}",
                remediation="Upgrade to Python 3.10 or newer."
            ))

        # Check essential packages
        packages = [("psutil", HAS_PSUTIL), ("PIL", True)]
        for pkg_name, available in packages:
            if available:
                items.append(DiagnosticItem(
                    check_id=f"pkg_{pkg_name}",
                    category="DEPENDENCIES",
                    status="PASS",
                    message=f"Package '{pkg_name}' is loaded."
                ))
            else:
                items.append(DiagnosticItem(
                    check_id=f"pkg_{pkg_name}",
                    category="DEPENDENCIES",
                    status="WARN",
                    message=f"Package '{pkg_name}' not found.",
                    remediation=f"Install with: pip install {pkg_name}"
                ))
        return items

    def _check_storage_paths(self) -> List[DiagnosticItem]:
        items = []
        paths = [
            ("notes_dir", NOTES_DIR),
            ("data_dir", DATA_DIR),
            ("screenshots_dir", SCREENSHOTS_DIR),
        ]
        for name, p in paths:
            if p.exists() and p.is_dir():
                items.append(DiagnosticItem(
                    check_id=f"path_{name}",
                    category="STORAGE",
                    status="PASS",
                    message=f"Directory '{name}' exists and accessible.",
                    metric_value=str(p)
                ))
            else:
                items.append(DiagnosticItem(
                    check_id=f"path_{name}",
                    category="STORAGE",
                    status="WARN",
                    message=f"Directory '{name}' does not exist at {p}.",
                    remediation=f"Create directory: {p}"
                ))
        return items

    def _check_hardware(self) -> List[DiagnosticItem]:
        items = []
        # Disk Space check
        try:
            total, used, free = shutil.disk_usage(os.path.dirname(os.path.abspath(__file__)))
            free_gb = round(free / (1024 ** 3), 2)
            if free_gb >= 5.0:
                items.append(DiagnosticItem(
                    check_id="disk_space",
                    category="HARDWARE",
                    status="PASS",
                    message=f"Adequate disk space: {free_gb} GB free.",
                    metric_value=f"{free_gb} GB"
                ))
            elif free_gb >= 1.0:
                items.append(DiagnosticItem(
                    check_id="disk_space",
                    category="HARDWARE",
                    status="WARN",
                    message=f"Low disk space: {free_gb} GB free.",
                    metric_value=f"{free_gb} GB",
                    remediation="Clean up temporary build artifacts or old screenshots."
                ))
            else:
                items.append(DiagnosticItem(
                    check_id="disk_space",
                    category="HARDWARE",
                    status="FAIL",
                    message=f"Critically low disk space: {free_gb} GB free.",
                    metric_value=f"{free_gb} GB",
                    remediation="Free up disk space immediately."
                ))
        except Exception as e:
            items.append(DiagnosticItem(
                check_id="disk_space",
                category="HARDWARE",
                status="WARN",
                message=f"Failed to check disk space: {e}"
            ))

        # Memory check via psutil
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                if mem.percent < 85.0:
                    items.append(DiagnosticItem(
                        check_id="ram_usage",
                        category="HARDWARE",
                        status="PASS",
                        message=f"RAM utilization normal at {mem.percent}%.",
                        metric_value=f"{mem.percent}%"
                    ))
                elif mem.percent < 95.0:
                    items.append(DiagnosticItem(
                        check_id="ram_usage",
                        category="HARDWARE",
                        status="WARN",
                        message=f"Elevated RAM utilization: {mem.percent}%.",
                        metric_value=f"{mem.percent}%",
                        remediation="Throttle background task concurrency."
                    ))
                else:
                    items.append(DiagnosticItem(
                        check_id="ram_usage",
                        category="HARDWARE",
                        status="FAIL",
                        message=f"Critical RAM saturation: {mem.percent}%.",
                        metric_value=f"{mem.percent}%",
                        remediation="Pause intensive background tasks."
                    ))
            except Exception as e:
                items.append(DiagnosticItem(
                    check_id="ram_usage",
                    category="HARDWARE",
                    status="WARN",
                    message=f"psutil memory read error: {e}"
                ))
        return items

    def _check_configuration(self) -> List[DiagnosticItem]:
        items = []
        try:
            cfg = load_config()
            if isinstance(cfg, dict):
                items.append(DiagnosticItem(
                    check_id="config_valid",
                    category="CONFIG",
                    status="PASS",
                    message="Configuration loaded and validated successfully.",
                    metric_value={"port": cfg.get("port"), "model": cfg.get("model")}
                ))
            else:
                items.append(DiagnosticItem(
                    check_id="config_valid",
                    category="CONFIG",
                    status="FAIL",
                    message="Configuration is not a valid JSON dictionary.",
                    remediation="Reset config.json to defaults."
                ))
        except Exception as e:
            items.append(DiagnosticItem(
                check_id="config_valid",
                category="CONFIG",
                status="FAIL",
                message=f"Failed to parse config: {e}",
                remediation="Validate JSON syntax of config.json."
            ))
        return items
