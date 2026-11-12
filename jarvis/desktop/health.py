"""
Capability 30: System Health Reporting Subsystem for J.A.R.V.I.S.
Computes a composite system health index (0-100), identifies critical performance
bottlenecks, and synthesizes structured JSON and executive Markdown health reports.
"""
import time
from typing import Dict, Any, List
from .hardware import hardware_monitor
from .troubleshooting import troubleshooter


class SystemHealthReporter:
    """Evaluates OS and hardware telemetry to synthesize comprehensive health reports."""

    def compute_health_score(self) -> Dict[str, Any]:
        """
        Calculates a composite score from 0 (Critical Failure) to 100 (Optimal).
        Deducts points based on hardware pressure and OS stability issues.
        """
        score = 100.0
        deductions = []

        hw = hardware_monitor.get_full_telemetry()
        tb = troubleshooter.run_troubleshooting_scan()

        # 1. CPU pressure
        cpu_pct = hw["cpu"]["utilization_percent"]
        if cpu_pct > 90:
            deduct = 25.0
            deductions.append(f"CPU critical utilization ({cpu_pct}%): -{deduct}")
            score -= deduct
        elif cpu_pct > 75:
            deduct = 12.0
            deductions.append(f"CPU high load ({cpu_pct}%): -{deduct}")
            score -= deduct

        # 2. Memory pressure
        mem_pct = hw["memory"]["used_percent"]
        if mem_pct > 90:
            deduct = 25.0
            deductions.append(f"RAM critical exhaustion ({mem_pct}%): -{deduct}")
            score -= deduct
        elif mem_pct > 80:
            deduct = 12.0
            deductions.append(f"RAM elevated usage ({mem_pct}%): -{deduct}")
            score -= deduct

        # 3. Disk space
        for part in hw["disk"]["partitions"]:
            if part["used_percent"] > 95:
                deduct = 20.0
                deductions.append(f"Disk partition {part['mountpoint']} critically full ({part['used_percent']}%): -{deduct}")
                score -= deduct
            elif part["used_percent"] > 88:
                deduct = 8.0
                deductions.append(f"Disk partition {part['mountpoint']} high usage ({part['used_percent']}%): -{deduct}")
                score -= deduct

        # 4. Hung windows
        hung_count = len(tb["unresponsive_windows"])
        if hung_count > 0:
            deduct = min(30.0, hung_count * 15.0)
            deductions.append(f"{hung_count} hung/unresponsive window(s): -{deduct}")
            score -= deduct

        # 5. Low battery
        bat = hw["battery"]
        if bat["has_battery"] and not bat["power_plugged"] and bat["percent"] < 15:
            deduct = 15.0
            deductions.append(f"Battery critically low ({bat['percent']}% on battery): -{deduct}")
            score -= deduct

        final_score = max(0.0, min(100.0, round(score, 1)))
        status = "HEALTHY" if final_score >= 80 else ("WARNING" if final_score >= 50 else "CRITICAL")

        return {
            "health_score": final_score,
            "status": status,
            "deductions": deductions,
            "hardware": hw,
            "troubleshooting": tb,
            "timestamp": time.time(),
        }

    def generate_markdown_report(self) -> str:
        """Generates an executive system health diagnostic report in Markdown."""
        data = self.compute_health_score()
        score = data["health_score"]
        status = data["status"]
        hw = data["hardware"]
        tb = data["troubleshooting"]

        badge_map = {
            "HEALTHY": "🟢 [OPTIMAL / HEALTHY]",
            "WARNING": "🟡 [CAUTION / DEGRADED]",
            "CRITICAL": "🔴 [CRITICAL / ACTION REQUIRED]",
        }

        md = []
        md.append("# 🖥️ J.A.R.V.I.S. System Health & OS Diagnostic Report")
        md.append(f"**Status:** {badge_map.get(status, status)} | **Composite Health Index:** `{score} / 100`\n")

        md.append("## 1. Hardware Performance Telemetry")
        md.append(f"- **CPU:** `{hw['cpu']['utilization_percent']}%` utilization across `{hw['cpu']['logical_cores']}` logical cores (`{hw['cpu']['physical_cores']}` physical)")
        md.append(f"- **RAM:** `{hw['memory']['used_gb']} GB / {hw['memory']['total_gb']} GB` (`{hw['memory']['used_percent']}%` used, `{hw['memory']['available_gb']} GB` available)")
        for part in hw["disk"]["partitions"]:
            md.append(f"- **Storage ({part['mountpoint']}):** `{part['used_gb']} GB / {part['total_gb']} GB` (`{part['used_percent']}%` used, `{part['free_gb']} GB` free)")
        bat = hw["battery"]
        if bat["has_battery"]:
            md.append(f"- **Battery:** `{bat['percent']}%` ({bat['status']})")
        else:
            md.append("- **Power:** Mainline AC Connected (No battery detected)")

        md.append("\n## 2. Desktop & OS Stability")
        md.append(f"- **Unresponsive Windows:** `{len(tb['unresponsive_windows'])}` detected")
        for hw_win in tb["unresponsive_windows"]:
            md.append(f"  - ⚠️ `{hw_win['title']}` (PID: {hw_win['pid']})")
        md.append(f"- **Runaway Processes:** `{len(tb['runaway_processes'])}` detected")
        for rp in tb["runaway_processes"]:
            md.append(f"  - ⚠️ `{rp['name']}` (PID: {rp['pid']}, CPU: {rp['cpu_percent']}%, RAM: {rp['memory_percent']}%)")

        if data["deductions"]:
            md.append("\n## 3. Score Deductions & Bottlenecks")
            for d in data["deductions"]:
                md.append(f"- {d}")

        md.append("\n## 4. Prioritized Recommendations")
        for rec in tb["recommended_actions"]:
            md.append(f"- {rec}")

        return "\n".join(md)


system_health_reporter = SystemHealthReporter()
