"""
Capability 23: Application Diagnostics Subsystem for J.A.R.V.I.S.
Performs deep process profiling: thread analysis, handle counts, memory metrics,
open network sockets, process ancestry trees, and GUI thread responsiveness pings.
"""
import time
import ctypes
import psutil
from typing import Dict, Any, List, Optional
from .windows import find_window

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

SMTO_ABORTIFHUNG = 0x0002
WM_NULL = 0x0000


class ApplicationDiagnostics:
    """Provides deep diagnostic inspection of desktop processes and GUI responsiveness."""

    def diagnose_process(self, pid: int) -> Dict[str, Any]:
        """Gathers granular telemetry for a specific process ID."""
        try:
            proc = psutil.Process(pid)
            with proc.oneshot():
                name = proc.name()
                exe = proc.exe() if hasattr(proc, 'exe') else ""
                status = proc.status()
                cpu_pct = proc.cpu_percent()
                mem_info = proc.memory_info()
                num_threads = proc.num_threads()
                create_time = proc.create_time()
                uptime_sec = time.time() - create_time

                # Handles (Windows specific)
                try:
                    num_handles = proc.num_handles()
                except Exception:
                    num_handles = -1

                # Network connections
                connections = []
                try:
                    for conn in proc.net_connections():
                        connections.append({
                            "type": str(conn.type),
                            "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                            "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                            "status": conn.status,
                        })
                except Exception:
                    pass

                # Child processes
                children = []
                try:
                    for child in proc.children(recursive=False):
                        children.append({"pid": child.pid, "name": child.name()})
                except Exception:
                    pass

                return {
                    "status": "success",
                    "pid": pid,
                    "name": name,
                    "executable": exe,
                    "process_status": status,
                    "cpu_percent": round(cpu_pct, 1),
                    "memory": {
                        "rss_mb": round(mem_info.rss / (1024 * 1024), 2),
                        "vms_mb": round(mem_info.vms / (1024 * 1024), 2),
                    },
                    "threads": num_threads,
                    "handles": num_handles,
                    "uptime_seconds": round(uptime_sec, 1),
                    "connections": connections[:10],
                    "children": children,
                }
        except psutil.NoSuchProcess:
            return {"status": "error", "message": f"Process PID {pid} does not exist"}
        except psutil.AccessDenied:
            return {"status": "error", "message": f"Access denied reading telemetry for PID {pid}"}

    def ping_window_responsiveness(self, window_identifier: Any, timeout_ms: int = 1000) -> Dict[str, Any]:
        """
        Sends WM_NULL message with SendMessageTimeoutW to measure GUI event loop responsiveness.
        """
        hwnd = find_window(window_identifier)
        if not hwnd:
            return {"status": "error", "message": f"Window not found: {window_identifier}"}

        result = ctypes.wintypes.DWORD()
        start = time.perf_counter()
        res = user32.SendMessageTimeoutW(
            hwnd,
            WM_NULL,
            0,
            0,
            SMTO_ABORTIFHUNG,
            timeout_ms,
            ctypes.byref(result),
        )
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        is_responsive = bool(res != 0)
        return {
            "status": "success",
            "hwnd": hwnd,
            "is_responsive": is_responsive,
            "latency_ms": elapsed_ms,
            "timeout_ms": timeout_ms,
        }


app_diagnostics = ApplicationDiagnostics()
