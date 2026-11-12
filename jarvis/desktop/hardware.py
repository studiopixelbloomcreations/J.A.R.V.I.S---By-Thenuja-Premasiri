"""
Capability 22: Hardware Monitoring Subsystem for J.A.R.V.I.S.
Collects real-time hardware telemetry: CPU per-core utilization, RAM breakdown,
GPU configuration, storage partition capacities, disk I/O, and battery/power metrics.
"""
import psutil
import subprocess
from typing import Dict, Any, List


class HardwareMonitor:
    """Provides hardware metrics across CPU, RAM, GPU, Disks, and Battery."""

    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Returns overall and per-core CPU utilization and core counts."""
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        total = psutil.cpu_percent(interval=None)
        freq = psutil.cpu_freq()
        return {
            "utilization_percent": total,
            "per_core_percent": per_core,
            "physical_cores": psutil.cpu_count(logical=False) or 1,
            "logical_cores": psutil.cpu_count(logical=True) or 1,
            "current_frequency_mhz": round(freq.current, 1) if freq else None,
            "max_frequency_mhz": round(freq.max, 1) if freq else None,
        }

    def get_memory_metrics(self) -> Dict[str, Any]:
        """Returns virtual memory and swap allocation breakdown."""
        vmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total_gb": round(vmem.total / (1024 ** 3), 2),
            "available_gb": round(vmem.available / (1024 ** 3), 2),
            "used_gb": round(vmem.used / (1024 ** 3), 2),
            "used_percent": vmem.percent,
            "swap_total_gb": round(swap.total / (1024 ** 3), 2),
            "swap_used_gb": round(swap.used / (1024 ** 3), 2),
            "swap_percent": swap.percent,
        }

    def get_disk_metrics(self) -> Dict[str, Any]:
        """Returns disk partition capacities and I/O counters."""
        partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2),
                    "used_percent": usage.percent,
                })
            except (PermissionError, OSError):
                continue

        io_counters = psutil.disk_io_counters()
        io_metrics = {}
        if io_counters:
            io_metrics = {
                "read_bytes_mb": round(io_counters.read_bytes / (1024 * 1024), 2),
                "write_bytes_mb": round(io_counters.write_bytes / (1024 * 1024), 2),
                "read_count": io_counters.read_count,
                "write_count": io_counters.write_count,
            }

        return {
            "partitions": partitions,
            "io": io_metrics,
        }

    def get_gpu_metrics(self) -> Dict[str, Any]:
        """Interrogates graphics adapters using WMIC or PowerShell."""
        gpus = []
        try:
            cmd = ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion | ConvertTo-Json"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
            if res.returncode == 0 and res.stdout.strip():
                import json
                data = json.loads(res.stdout)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    name = item.get("Name", "Unknown GPU")
                    ram = item.get("AdapterRAM") or 0
                    vram_mb = round(ram / (1024 * 1024), 1) if ram else None
                    gpus.append({
                        "name": name,
                        "vram_mb": vram_mb,
                        "driver_version": item.get("DriverVersion", "N/A"),
                    })
        except Exception:
            pass

        if not gpus:
            gpus.append({"name": "Integrated / DirectX Display Adapter", "vram_mb": None, "driver_version": "N/A"})

        return {"adapters": gpus}

    def get_battery_metrics(self) -> Dict[str, Any]:
        """Returns battery charge, AC mainline connection, and estimated runtime."""
        bat = psutil.sensors_battery()
        if not bat:
            return {
                "has_battery": False,
                "percent": 100,
                "power_plugged": True,
                "status": "AC Mainline Connected",
                "seconds_remaining": -1,
            }
        return {
            "has_battery": True,
            "percent": int(bat.percent),
            "power_plugged": bool(bat.power_plugged),
            "status": "Charging" if bat.power_plugged else "Discharging",
            "seconds_remaining": bat.secsleft if bat.secsleft != psutil.POWER_TIME_UNLIMITED else -1,
        }

    def get_full_telemetry(self) -> Dict[str, Any]:
        """Aggregates comprehensive hardware telemetry in one call."""
        cpu = self.get_cpu_metrics()
        mem = self.get_memory_metrics()
        disk = self.get_disk_metrics()
        gpu = self.get_gpu_metrics()
        bat = self.get_battery_metrics()

        # Check threshold alerts
        alerts = []
        if cpu["utilization_percent"] > 90.0:
            alerts.append(f"High CPU utilization: {cpu['utilization_percent']}%")
        if mem["used_percent"] > 88.0:
            alerts.append(f"High RAM consumption: {mem['used_percent']}%")
        for part in disk["partitions"]:
            if part["used_percent"] > 90.0:
                alerts.append(f"Disk volume {part['mountpoint']} critically full ({part['used_percent']}%)")
        if bat["has_battery"] and not bat["power_plugged"] and bat["percent"] < 20:
            alerts.append(f"Low battery warning: {bat['percent']}% remaining")

        return {
            "cpu": cpu,
            "memory": mem,
            "disk": disk,
            "gpu": gpu,
            "battery": bat,
            "alerts": alerts,
            "status": "ALERT" if alerts else "NOMINAL",
        }


hardware_monitor = HardwareMonitor()
