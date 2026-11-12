"""
Capability 114: Resource Awareness & Throttling
Monitors live host CPU and memory pressure via psutil, applying dynamic concurrency
limits and execution pacing to prevent host lockup or system unresponsiveness.
"""
from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class ThrottleLevel(str, enum.Enum):
    NORMAL = "NORMAL"          # Normal concurrency (e.g. 4 workers, 0s delay)
    MODERATE = "MODERATE"      # Paced execution (2 workers, 0.25s delay)
    AGGRESSIVE = "AGGRESSIVE"  # Serialized execution (1 worker, 1.0s delay)
    PAUSED = "PAUSED"          # Temporarily halt task launch until headroom recovers


@dataclass
class ResourceMetrics:
    """Snapshot of host resource utilization."""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_percent: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResourceGuard:
    """
    Capability 114: Autonomous Resource Guard & Governor.
    Regulates background operations dynamically based on real hardware telemetry.
    """

    def __init__(self,
                 cpu_moderate_threshold: float = 75.0,
                 cpu_aggressive_threshold: float = 85.0,
                 cpu_pause_threshold: float = 95.0,
                 ram_moderate_threshold: float = 80.0,
                 ram_aggressive_threshold: float = 88.0,
                 ram_pause_threshold: float = 95.0):
        self.cpu_moderate = cpu_moderate_threshold
        self.cpu_aggressive = cpu_aggressive_threshold
        self.cpu_pause = cpu_pause_threshold
        self.ram_moderate = ram_moderate_threshold
        self.ram_aggressive = ram_aggressive_threshold
        self.ram_pause = ram_pause_threshold
        self._history: List[ResourceMetrics] = []

    def sample(self) -> ResourceMetrics:
        """Captures current host CPU, RAM, and Disk metrics."""
        if HAS_PSUTIL:
            try:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage("/")
                metrics = ResourceMetrics(
                    cpu_percent=round(cpu, 1),
                    memory_percent=round(mem.percent, 1),
                    memory_available_mb=round(mem.available / (1024 * 1024), 1),
                    disk_percent=round(disk.percent, 1)
                )
            except Exception:
                metrics = ResourceMetrics(cpu_percent=10.0, memory_percent=40.0, memory_available_mb=4096.0, disk_percent=50.0)
        else:
            # Fallback mock values if psutil not present
            metrics = ResourceMetrics(cpu_percent=15.0, memory_percent=45.0, memory_available_mb=4096.0, disk_percent=50.0)

        self._history.append(metrics)
        if len(self._history) > 100:
            self._history.pop(0)

        return metrics

    def get_throttle_level(self, metrics: Optional[ResourceMetrics] = None) -> ThrottleLevel:
        """Determines the appropriate operational throttle level for current conditions."""
        m = metrics or self.sample()

        if m.cpu_percent >= self.cpu_pause or m.memory_percent >= self.ram_pause:
            return ThrottleLevel.PAUSED
        if m.cpu_percent >= self.cpu_aggressive or m.memory_percent >= self.ram_aggressive:
            return ThrottleLevel.AGGRESSIVE
        if m.cpu_percent >= self.cpu_moderate or m.memory_percent >= self.ram_moderate:
            return ThrottleLevel.MODERATE
        return ThrottleLevel.NORMAL

    def get_recommended_concurrency(self, base_concurrency: int = 4) -> int:
        """Calculates safe concurrent worker count given current throttle status."""
        level = self.get_throttle_level()
        if level == ThrottleLevel.NORMAL:
            return base_concurrency
        elif level == ThrottleLevel.MODERATE:
            return max(1, base_concurrency // 2)
        elif level == ThrottleLevel.AGGRESSIVE:
            return 1
        else:  # PAUSED
            return 0

    def get_pacing_delay(self) -> float:
        """Returns recommended delay in seconds before launching next task."""
        level = self.get_throttle_level()
        if level == ThrottleLevel.NORMAL:
            return 0.0
        elif level == ThrottleLevel.MODERATE:
            return 0.25
        elif level == ThrottleLevel.AGGRESSIVE:
            return 1.0
        else:  # PAUSED
            return 3.0

    def wait_if_throttled(self, max_wait_seconds: float = 3.0) -> bool:
        """
        Pauses thread execution briefly if host resources are currently exhausted.
        Returns True if paused/delayed, False if headroom was immediately clear.
        """
        level = self.get_throttle_level()
        if level in (ThrottleLevel.AGGRESSIVE, ThrottleLevel.PAUSED):
            delay = min(self.get_pacing_delay(), max_wait_seconds)
            time.sleep(delay)
            return True
        return False
