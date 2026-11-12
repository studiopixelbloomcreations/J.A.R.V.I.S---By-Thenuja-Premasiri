"""
Capability 21: Automated Troubleshooting Subsystem for J.A.R.V.I.S.
Detects hung/unresponsive windows, identifies runaway CPU/memory processes,
and executes safe automated remediation routines.
"""
import os
import shutil
import tempfile
import subprocess
import ctypes
import psutil
from typing import List, Dict, Any, Optional
from .windows import list_windows, is_window_hung

user32 = ctypes.windll.user32


class AutomatedTroubleshooter:
    """Diagnoses desktop issues, hanging processes, and runs automated repairs."""

    def detect_unresponsive_windows(self) -> List[Dict[str, Any]]:
        """Checks all visible desktop windows for unresponsiveness."""
        windows = list_windows()
        hung = []
        for w in windows:
            hwnd = w["hwnd"]
            try:
                if user32.IsHungAppWindow(hwnd):
                    # Get PID for hung window
                    pid = ctypes.wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    hung.append({
                        "hwnd": hwnd,
                        "title": w["title"],
                        "pid": pid.value,
                        "severity": "CRITICAL",
                        "issue": "Application window is not responding to Windows messages",
                    })
            except Exception:
                continue
        return hung

    def detect_runaway_processes(self, cpu_threshold: float = 75.0, mem_threshold: float = 25.0) -> List[Dict[str, Any]]:
        """Finds processes consuming excessive CPU or RAM."""
        runaways = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                cpu = info.get('cpu_percent') or 0.0
                mem = info.get('memory_percent') or 0.0
                if cpu >= cpu_threshold or mem >= mem_threshold:
                    runaways.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "cpu_percent": round(cpu, 1),
                        "memory_percent": round(mem, 1),
                        "severity": "HIGH",
                        "issue": f"Resource exhaustion: CPU {cpu:.1f}%, RAM {mem:.1f}%",
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return runaways

    def run_troubleshooting_scan(self) -> Dict[str, Any]:
        """Runs comprehensive desktop diagnostics for issues."""
        hung_wins = self.detect_unresponsive_windows()
        runaway_procs = self.detect_runaway_processes()

        issues = []
        issues.extend(hung_wins)
        issues.extend(runaway_procs)

        status = "HEALTHY"
        if any(i.get("severity") == "CRITICAL" for i in issues):
            status = "CRITICAL"
        elif issues:
            status = "WARNING"

        return {
            "status": status,
            "total_issues": len(issues),
            "unresponsive_windows": hung_wins,
            "runaway_processes": runaway_procs,
            "recommended_actions": self._generate_recommendations(issues),
        }

    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        recs = []
        for issue in issues:
            if "not responding" in issue.get("issue", ""):
                recs.append(f"Terminate hung window '{issue.get('title')}' (PID: {issue.get('pid')})")
            if "Resource exhaustion" in issue.get("issue", ""):
                recs.append(f"Inspect or throttle high-load process '{issue.get('name')}' (PID: {issue.get('pid')})")
        if not recs:
            recs.append("All desktop windows and system processes operating within nominal parameters.")
        return recs

    def kill_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """Safely terminates a process."""
        try:
            p = psutil.Process(pid)
            name = p.name()
            if force:
                p.kill()
            else:
                p.terminate()
            return {"status": "success", "action": "terminated", "pid": pid, "name": name}
        except psutil.NoSuchProcess:
            return {"status": "error", "message": f"Process PID {pid} not found"}
        except psutil.AccessDenied:
            return {"status": "error", "message": f"Access denied to terminate PID {pid}"}

    def flush_dns(self) -> Dict[str, Any]:
        """Flushes the Windows local DNS resolver cache."""
        try:
            res = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, timeout=5)
            return {"status": "success", "output": res.stdout.strip()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def clean_temp_files(self, dry_run: bool = True) -> Dict[str, Any]:
        """Cleans temporary files from user temp directory."""
        temp_dir = tempfile.gettempdir()
        freed_bytes = 0
        cleaned_count = 0
        errors = 0

        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                fpath = os.path.join(root, f)
                try:
                    sz = os.path.getsize(fpath)
                    if not dry_run:
                        os.remove(fpath)
                    freed_bytes += sz
                    cleaned_count += 1
                except Exception:
                    errors += 1
            if not dry_run:
                break  # Only clean top level in actual run for safety

        return {
            "status": "success",
            "dry_run": dry_run,
            "temp_dir": temp_dir,
            "files_evaluated": cleaned_count,
            "reclaimable_mb": round(freed_bytes / (1024 * 1024), 2),
            "errors": errors,
        }


troubleshooter = AutomatedTroubleshooter()
