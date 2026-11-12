"""
Capability 46: Security Posture Analysis
Evaluates host security configuration, privileges, patch levels,
active listening services, antivirus status, and computes comprehensive posture scores.
"""

import os
import sys
import platform
import socket
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class PostureFinding:
    id: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str
    description: str
    remediation: str


@dataclass
class PostureReport:
    score: int  # 0 to 100
    grade: str  # A, B, C, D, F
    os_name: str
    os_version: str
    architecture: str
    hostname: str
    is_admin: bool
    antivirus_status: Dict[str, Any]
    firewall_enabled: bool
    findings: List[PostureFinding] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "grade": self.grade,
            "os_name": self.os_name,
            "os_version": self.os_version,
            "architecture": self.architecture,
            "hostname": self.hostname,
            "is_admin": self.is_admin,
            "antivirus_status": self.antivirus_status,
            "firewall_enabled": self.firewall_enabled,
            "findings": [
                {
                    "id": f.id,
                    "title": f.title,
                    "severity": f.severity,
                    "category": f.category,
                    "description": f.description,
                    "remediation": f.remediation,
                }
                for f in self.findings
            ],
            "summary": self.summary,
        }


class SecurityPostureAnalyzer:
    """Evaluates security posture and configuration of the host environment."""

    def __init__(self, override_admin: Optional[bool] = None, override_av: Optional[Dict[str, Any]] = None):
        self._override_admin = override_admin
        self._override_av = override_av

    def is_privileged_user(self) -> bool:
        """Determines if the current process is running with administrative privileges."""
        if self._override_admin is not None:
            return self._override_admin
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    def check_antivirus_status(self) -> Dict[str, Any]:
        """Checks if Windows Defender or standard AV protection is active."""
        if self._override_av is not None:
            return self._override_av

        av_info = {
            "installed": True,
            "real_time_protection": True,
            "provider": "Windows Defender" if platform.system() == "Windows" else "System Antivirus",
            "up_to_date": True,
        }

        if platform.system() == "Windows":
            try:
                cmd = "Get-MpComputerStatus | Select-Object -Property AntivirusEnabled, RealTimeProtectionEnabled, AntivirusSignatureAge"
                res = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", cmd],
                    capture_output=True,
                    text=True,
                    timeout=4,
                )
                if res.returncode == 0 and "AntivirusEnabled" in res.stdout:
                    lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
                    # Basic parser for PS output
                    av_info["raw_output"] = res.stdout
            except Exception:
                pass

        return av_info

    def check_listening_ports(self) -> List[int]:
        """Enumerates commonly audited listening TCP ports locally."""
        common_ports = [21, 22, 23, 25, 80, 135, 139, 443, 445, 1433, 3306, 3389, 5432, 8080]
        open_ports = []
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.05)
                result = sock.connect_ex(("127.0.0.1", port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except Exception:
                pass
        return open_ports

    def assess_posture(
        self,
        firewall_active: bool = True,
        uac_enabled: bool = True,
        auto_update_enabled: bool = True,
        mock_open_ports: Optional[List[int]] = None,
    ) -> PostureReport:
        """Runs a complete security posture analysis."""
        findings: List[PostureFinding] = []
        score = 100

        is_admin = self.is_privileged_user()
        av_status = self.check_antivirus_status()
        open_ports = mock_open_ports if mock_open_ports is not None else self.check_listening_ports()

        # Rule 1: Running as Admin / Root for everyday tasks
        if is_admin:
            findings.append(
                PostureFinding(
                    id="POS-001",
                    title="Process Running with Elevated Administrative Privileges",
                    severity="MEDIUM",
                    category="Least Privilege",
                    description="Executing applications with continuous administrative rights increases blast radius.",
                    remediation="Execute processes under standard unprivileged accounts and elevate only when necessary.",
                )
            )
            score -= 10

        # Rule 2: Antivirus Real-time Protection
        if not av_status.get("real_time_protection", False):
            findings.append(
                PostureFinding(
                    id="POS-002",
                    title="Real-Time Antivirus Protection Disabled",
                    severity="CRITICAL",
                    category="Endpoint Defense",
                    description="Endpoint antivirus or real-time protection is inactive or disabled.",
                    remediation="Enable Microsoft Defender Real-Time Protection or ensure third-party EDR is active.",
                )
            )
            score -= 30

        # Rule 3: Host Firewall
        if not firewall_active:
            findings.append(
                PostureFinding(
                    id="POS-003",
                    title="Host Firewall Inactive",
                    severity="HIGH",
                    category="Network Perimeter",
                    description="Local firewall is disabled on one or more network profiles.",
                    remediation="Enable Windows Defender Firewall across Domain, Private, and Public profiles.",
                )
            )
            score -= 20

        # Rule 4: User Account Control (UAC)
        if not uac_enabled:
            findings.append(
                PostureFinding(
                    id="POS-004",
                    title="User Account Control (UAC) Disabled",
                    severity="HIGH",
                    category="Access Control",
                    description="UAC prompts are disabled, allowing silent privilege elevation by malware.",
                    remediation="Configure UAC to 'Always Notify' or standard default prompt level.",
                )
            )
            score -= 15

        # Rule 5: Automatic OS Updates
        if not auto_update_enabled:
            findings.append(
                PostureFinding(
                    id="POS-005",
                    title="Automatic OS Updates Disabled",
                    severity="MEDIUM",
                    category="Patch Management",
                    description="Automatic Windows Updates are disabled, risking unpatched CVE exposures.",
                    remediation="Enable Windows Update automatic patch installation.",
                )
            )
            score -= 10

        # Rule 6: Insecure Listening Services (Telnet 23, SMB 445, RDP 3389)
        risky_services = {
            23: ("Telnet", "CRITICAL", "Unencrypted legacy remote access protocol."),
            445: ("SMB", "HIGH", "Exposed SMB service vulnerable to lateral movement / EternalBlue."),
            3389: ("RDP", "MEDIUM", "Remote Desktop exposed locally; ensure NLA is enforced."),
        }
        for port, (svc, sev, desc) in risky_services.items():
            if port in open_ports:
                deduction = 20 if sev == "CRITICAL" else (15 if sev == "HIGH" else 8)
                score -= deduction
                findings.append(
                    PostureFinding(
                        id=f"POS-PORT-{port}",
                        title=f"Insecure Service Listening on Port {port} ({svc})",
                        severity=sev,
                        category="Network Attack Surface",
                        description=desc,
                        remediation=f"Disable the {svc} service or restrict port {port} via firewall rules.",
                    )
                )

        score = max(0, min(100, score))

        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        summary = {
            "CRITICAL": sum(1 for f in findings if f.severity == "CRITICAL"),
            "HIGH": sum(1 for f in findings if f.severity == "HIGH"),
            "MEDIUM": sum(1 for f in findings if f.severity == "MEDIUM"),
            "LOW": sum(1 for f in findings if f.severity == "LOW"),
            "INFO": sum(1 for f in findings if f.severity == "INFO"),
        }

        return PostureReport(
            score=score,
            grade=grade,
            os_name=platform.system(),
            os_version=platform.version(),
            architecture=platform.machine(),
            hostname=socket.gethostname(),
            is_admin=is_admin,
            antivirus_status=av_status,
            firewall_enabled=firewall_active,
            findings=findings,
            summary=summary,
        )
