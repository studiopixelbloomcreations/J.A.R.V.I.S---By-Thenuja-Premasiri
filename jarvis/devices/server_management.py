"""
Capability 122: Local Server Management
Monitors TCP port health and response latency, detects port conflicts,
tracks background daemon and process vitals, and executes guarded service restarts.
"""

import os
import socket
import subprocess
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class PortHealth:
    port: int
    host: str = "127.0.0.1"
    is_open: bool = False
    latency_ms: Optional[float] = None
    service_name: Optional[str] = None
    pid: Optional[int] = None
    process_name: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ServiceStatus:
    name: str
    pid: Optional[int] = None
    is_running: bool = False
    cpu_percent: float = 0.0
    memory_rss_mb: float = 0.0
    threads: int = 0
    uptime_seconds: float = 0.0
    status: str = "STOPPED"  # HEALTHY, HIGH_RESOURCE, STOPPED, CRASHED


class LocalServerManager:
    """Manages local backend servers, microservices, port health, and restart handlers."""

    DEFAULT_SERVICES = {
        4700: "J.A.R.V.I.S. Core Server",
        8080: "Development HTTP Server",
        3000: "Frontend Dev Server",
        5432: "PostgreSQL Database",
        6379: "Redis Cache Server",
        1883: "MQTT Broker",
        8123: "Home Assistant",
        22: "SSH Daemon",
    }

    def __init__(self):
        self._restart_history: List[Dict[str, Any]] = []
        self._cooldown_seconds: float = 10.0

    def check_port_health(self, port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> PortHealth:
        """Probes a TCP socket port and measures connection handshake latency."""
        start = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        is_open = False
        err_msg = None
        try:
            res = sock.connect_ex((host, port))
            elapsed = (time.perf_counter() - start) * 1000.0
            if res == 0:
                is_open = True
            else:
                err_msg = f"Socket errno {res}"
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000.0
            err_msg = str(e)
        finally:
            try:
                sock.close()
            except Exception:
                pass

        owning_pid, proc_name = self.find_port_owner(port)

        return PortHealth(
            port=port,
            host=host,
            is_open=is_open,
            latency_ms=round(elapsed, 2) if is_open else None,
            service_name=self.DEFAULT_SERVICES.get(port, f"Port-{port}"),
            pid=owning_pid,
            process_name=proc_name,
            error=err_msg
        )

    def scan_common_ports(self, host: str = "127.0.0.1") -> List[PortHealth]:
        """Probes all standard Jarvis and dev service ports."""
        results = []
        for port in sorted(self.DEFAULT_SERVICES.keys()):
            results.append(self.check_port_health(port, host=host, timeout=0.2))
        return results

    def find_port_owner(self, port: int) -> Tuple[Optional[int], Optional[str]]:
        """Identifies which process ID and name owns an active listening port."""
        if not psutil:
            return (None, None)

        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.laddr and conn.laddr.port == port and conn.status == "LISTEN":
                    pid = conn.pid
                    if pid:
                        try:
                            proc = psutil.Process(pid)
                            return (pid, proc.name())
                        except Exception:
                            return (pid, "unknown")
        except Exception:
            pass

        return (None, None)

    def inspect_process(self, process_name_or_pid: Any) -> ServiceStatus:
        """Inspects runtime health, memory, and CPU usage for a designated service."""
        if not psutil:
            return ServiceStatus(name=str(process_name_or_pid), status="UNAVAILABLE")

        target_proc = None
        try:
            if isinstance(process_name_or_pid, int):
                target_proc = psutil.Process(process_name_or_pid)
            else:
                name_lower = str(process_name_or_pid).lower()
                for p in psutil.process_iter(["pid", "name"]):
                    if name_lower in p.info["name"].lower():
                        target_proc = p
                        break
        except Exception:
            pass

        if not target_proc or not target_proc.is_running():
            return ServiceStatus(name=str(process_name_or_pid), is_running=False, status="STOPPED")

        try:
            mem_info = target_proc.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            cpu_pct = target_proc.cpu_percent(interval=0.05)
            uptime = time.time() - target_proc.create_time()
            threads = target_proc.num_threads()

            status = "HEALTHY"
            if cpu_pct > 85.0 or mem_mb > 2048.0:
                status = "HIGH_RESOURCE"

            return ServiceStatus(
                name=target_proc.name(),
                pid=target_proc.pid,
                is_running=True,
                cpu_percent=round(cpu_pct, 1),
                memory_rss_mb=round(mem_mb, 2),
                threads=threads,
                uptime_seconds=round(uptime, 1),
                status=status
            )
        except Exception:
            return ServiceStatus(name=str(process_name_or_pid), is_running=False, status="CRASHED")

    def trigger_service_restart(
        self,
        service_name: str,
        restart_command: Optional[str] = None,
        verify_port: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes a guarded service restart with cooldown checking to prevent loops.
        """
        now = time.time()

        # Check cooldown
        recent = [
            r for r in self._restart_history
            if r["service"] == service_name and (now - r["timestamp"]) < self._cooldown_seconds
        ]
        if recent:
            return {
                "success": False,
                "error": f"Restart cooldown active ({round(self._cooldown_seconds - (now - recent[-1]['timestamp']), 1)}s remaining)",
                "service": service_name
            }

        restart_record = {
            "service": service_name,
            "timestamp": now,
            "command": restart_command,
            "success": True
        }

        # If a command was supplied, execute it safely
        if restart_command:
            try:
                subprocess.Popen(restart_command, shell=True)
            except Exception as e:
                restart_record["success"] = False
                restart_record["error"] = str(e)
                self._restart_history.append(restart_record)
                return restart_record

        # Post-restart port verification
        if verify_port:
            time.sleep(0.5)
            health = self.check_port_health(verify_port)
            restart_record["port_verified"] = health.is_open

        self._restart_history.append(restart_record)
        return restart_record

    def get_server_dashboard(self) -> Dict[str, Any]:
        """Generates unified local server monitoring report."""
        port_results = self.scan_common_ports()
        open_ports = [p for p in port_results if p.is_open]

        # Inspect python runtime itself
        current_proc = self.inspect_process(os.getpid())

        return {
            "status": "nominal" if open_ports else "degraded",
            "probed_ports_count": len(port_results),
            "open_ports_count": len(open_ports),
            "ports": [asdict(p) for p in port_results],
            "jarvis_process": asdict(current_proc),
            "restarts_executed": len(self._restart_history),
        }
