"""
Capability 125: Device Health Monitoring
Monitors host battery, thermal/CPU temperatures, memory/disk headroom,
connectivity health, and calculates a composite device health score (0-100).
"""

import os
import platform
import socket
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class BatteryStatus:
    has_battery: bool = True
    percent: float = 100.0
    power_plugged: bool = True
    seconds_left: Optional[int] = None
    charging_state: str = "Plugged In"  # Charging, Discharging, Full, Plugged In


@dataclass
class ThermalStatus:
    has_sensors: bool = True
    cpu_temp_c: float = 45.0
    max_core_temp_c: float = 48.0
    is_throttling: bool = False
    core_temps: Dict[str, float] = field(default_factory=dict)


@dataclass
class ConnectivityStatus:
    is_connected: bool = True
    gateway_reachable: bool = True
    dns_resolving: bool = True
    packet_loss_pct: float = 0.0


class DeviceHealthMonitor:
    """Monitors physical host health, power subsystem, thermals, and vitality scores."""

    def __init__(self):
        pass

    def get_battery_status(self) -> BatteryStatus:
        """Inspects host battery power state via psutil."""
        if not psutil:
            return BatteryStatus(has_battery=False, percent=100.0, power_plugged=True, charging_state="AC Desktop")

        try:
            batt = psutil.sensors_battery()
            if batt is None:
                # Desktop workstation without battery
                return BatteryStatus(
                    has_battery=False,
                    percent=100.0,
                    power_plugged=True,
                    seconds_left=None,
                    charging_state="AC Mains Connected"
                )

            charging_state = "Discharging"
            if batt.power_plugged:
                charging_state = "Charging" if batt.percent < 99 else "Full (Plugged)"

            return BatteryStatus(
                has_battery=True,
                percent=round(batt.percent, 1),
                power_plugged=batt.power_plugged,
                seconds_left=batt.secsleft if batt.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                charging_state=charging_state
            )
        except Exception:
            return BatteryStatus(has_battery=False, percent=100.0, power_plugged=True, charging_state="AC Desktop")

    def get_thermal_status(self) -> ThermalStatus:
        """Inspects CPU core temperatures or falls back to synthetic thermal model."""
        if not psutil:
            return ThermalStatus(has_sensors=False, cpu_temp_c=45.0)

        core_temps = {}
        max_t = 0.0
        avg_t = 0.0

        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            label = entry.label or name
                            core_temps[label] = entry.current
                            if entry.current > max_t:
                                max_t = entry.current

                    if core_temps:
                        avg_t = sum(core_temps.values()) / len(core_temps)
                        return ThermalStatus(
                            has_sensors=True,
                            cpu_temp_c=round(avg_t, 1),
                            max_core_temp_c=round(max_t, 1),
                            is_throttling=(max_t >= 85.0),
                            core_temps=core_temps
                        )
        except Exception:
            pass

        # Windows or non-ACPI thermal fallback based on CPU load
        try:
            cpu_load = psutil.cpu_percent(interval=0.05) if psutil else 15.0
            synthetic_temp = 42.0 + (cpu_load * 0.35)
            return ThermalStatus(
                has_sensors=False,
                cpu_temp_c=round(synthetic_temp, 1),
                max_core_temp_c=round(synthetic_temp + 3.0, 1),
                is_throttling=(synthetic_temp >= 85.0),
                core_temps={"synthetic_cpu": round(synthetic_temp, 1)}
            )
        except Exception:
            return ThermalStatus(has_sensors=False, cpu_temp_c=45.0)

    def check_connectivity(self) -> ConnectivityStatus:
        """Checks DNS resolution and gateway reachability."""
        dns_ok = False
        try:
            socket.gethostbyname("dns.google")
            dns_ok = True
        except Exception:
            dns_ok = False

        # Probe default outbound route
        gw_ok = False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            s.close()
            gw_ok = True
        except Exception:
            gw_ok = False

        return ConnectivityStatus(
            is_connected=(dns_ok or gw_ok),
            gateway_reachable=gw_ok,
            dns_resolving=dns_ok,
            packet_loss_pct=0.0 if (dns_ok and gw_ok) else (50.0 if (dns_ok or gw_ok) else 100.0)
        )

    def calculate_health_score(
        self,
        battery: BatteryStatus,
        thermal: ThermalStatus,
        connectivity: ConnectivityStatus,
        cpu_load_pct: float,
        mem_used_pct: float
    ) -> Tuple[int, str, List[str]]:
        """
        Computes weighted composite health score (0-100), rating, and alert warnings.
        """
        score = 100.0
        alerts = []

        # CPU load deduction
        if cpu_load_pct > 80.0:
            deduct = (cpu_load_pct - 80.0) * 0.5
            score -= deduct
            alerts.append(f"High CPU utilization: {cpu_load_pct}%")

        # Memory headroom deduction
        if mem_used_pct > 85.0:
            deduct = (mem_used_pct - 85.0) * 0.6
            score -= deduct
            alerts.append(f"Memory pressure elevated: {mem_used_pct}% used")

        # Thermal deduction
        if thermal.cpu_temp_c > 75.0:
            deduct = (thermal.cpu_temp_c - 75.0) * 1.0
            score -= deduct
            alerts.append(f"High CPU temperature: {thermal.cpu_temp_c}°C")
        if thermal.is_throttling:
            score -= 15.0
            alerts.append("Thermal throttling is ACTIVE")

        # Battery deduction
        if battery.has_battery:
            if battery.percent < 20.0 and not battery.power_plugged:
                score -= 20.0
                alerts.append(f"Low battery ({battery.percent}%) and discharging")
            elif battery.percent < 10.0:
                score -= 30.0
                alerts.append(f"Critical battery warning: {battery.percent}%")

        # Connectivity deduction
        if not connectivity.is_connected:
            score -= 25.0
            alerts.append("Network disconnected: no gateway or DNS access")
        elif connectivity.packet_loss_pct > 0.0:
            score -= 10.0
            alerts.append("Intermittent network connectivity")

        final_score = int(max(0.0, min(100.0, score)))

        if final_score >= 90:
            rating = "EXCELLENT"
        elif final_score >= 75:
            rating = "GOOD"
        elif final_score >= 60:
            rating = "FAIR"
        else:
            rating = "DEGRADED"

        return final_score, rating, alerts

    def get_health_dashboard(self) -> Dict[str, Any]:
        """Compiles complete hardware vitality dashboard."""
        battery = self.get_battery_status()
        thermal = self.get_thermal_status()
        connectivity = self.check_connectivity()

        cpu_pct = psutil.cpu_percent(interval=0.05) if psutil else 10.0
        mem = psutil.virtual_memory() if psutil else None
        mem_pct = mem.percent if mem else 40.0
        mem_free_mb = round((mem.available / (1024 * 1024)), 1) if mem else 4096.0

        disk = psutil.disk_usage("/") if (psutil and os.name != "nt") else (psutil.disk_usage("C:\\") if psutil else None)
        disk_free_gb = round(disk.free / (1024 ** 3), 1) if disk else 50.0

        score, rating, alerts = self.calculate_health_score(battery, thermal, connectivity, cpu_pct, mem_pct)

        return {
            "health_score": score,
            "health_rating": rating,
            "status": "nominal" if not alerts else ("warning" if score >= 60 else "critical"),
            "alerts": alerts,
            "vitals": {
                "cpu_percent": round(cpu_pct, 1),
                "memory_used_percent": round(mem_pct, 1),
                "memory_available_mb": mem_free_mb,
                "disk_free_gb": disk_free_gb,
                "platform": platform.platform(),
            },
            "battery": asdict(battery),
            "thermal": asdict(thermal),
            "connectivity": asdict(connectivity)
        }
