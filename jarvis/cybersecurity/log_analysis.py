"""
Capability 48: Log Analysis
Multi-source security log parsing (Windows Event Logs, Web Server Access Logs, Syslog)
with heuristic detection of brute-force attacks, SQL injection, path traversal,
XSS, suspicious PowerShell executions, and log clearing tampering.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


@dataclass
class SecurityLogIncident:
    rule_id: str
    rule_name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    timestamp: str
    source_ip: Optional[str]
    user: Optional[str]
    description: str
    evidence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "source_ip": self.source_ip,
            "user": self.user,
            "description": self.description,
            "evidence": self.evidence,
        }


class LogAnalyzer:
    """Security log parser and threat detection engine."""

    # Regex signatures for web attack patterns
    SQLI_PATTERNS = [
        r"(?i)(\bunion\s+select\b)",
        r"(?i)('\s*or\s*'1'\s*=\s*'1)",
        r"(?i)(\bexec\s*\(|\bxp_cmdshell\b)",
        r"(?i)(--\s*$|\bwaitfor\s+delay\b|\bsleep\s*\(\d+\))",
        r"(?i)(\bor\s+1=1\b)",
    ]
    XSS_PATTERNS = [
        r"(?i)(<script[^>]*>.*?</script>)",
        r"(?i)(javascript\s*:)",
        r"(?i)(onerror\s*=|onload\s*=|alert\s*\()",
    ]
    TRAVERSAL_PATTERNS = [
        r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/)",
        r"(/etc/passwd|/windows/win\.ini|/windows/system32)",
    ]
    POWERSHELL_SUSPICIOUS = [
        r"(?i)(-enc\b|-encodedcommand\b)",
        r"(?i)(downloadstring|downloadfile)",
        r"(?i)(\biex\b|invoke-expression)",
        r"(?i)(-executionpolicy\s+bypass)",
        r"(?i)(-windowstyle\s+hidden)",
    ]

    def __init__(self, brute_force_threshold: int = 5):
        self.brute_force_threshold = brute_force_threshold

    def parse_web_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parses standard Apache/Nginx Combined Log Format, accommodating URLs with query spaces."""
        pattern = r'^(\S+) \S+ (\S+) \[(.*?)\] "(GET|POST|PUT|DELETE|HEAD|OPTIONS)\s+(.*?)(?:\s+[A-Z0-9/\.]+)?\" (\d{3}) (\d+|-)'
        match = re.match(pattern, line)
        if match:
            return {
                "source_ip": match.group(1),
                "user": match.group(2) if match.group(2) != "-" else None,
                "timestamp": match.group(3),
                "method": match.group(4),
                "url": match.group(5),
                "status_code": int(match.group(6)),
                "raw": line,
            }
        return None

    def analyze_web_logs(self, log_lines: List[str]) -> List[SecurityLogIncident]:
        """Analyzes web server access logs for SQLi, XSS, and traversal attempts."""
        incidents: List[SecurityLogIncident] = []
        for line in log_lines:
            entry = self.parse_web_log_line(line)
            if not entry:
                continue

            url = entry["url"]
            ts = entry["timestamp"]
            ip = entry["source_ip"]

            # SQL Injection check
            for pat in self.SQLI_PATTERNS:
                if re.search(pat, url):
                    incidents.append(
                        SecurityLogIncident(
                            rule_id="LOG-WEB-SQLI",
                            rule_name="SQL Injection Attempt Detected",
                            severity="HIGH",
                            timestamp=ts,
                            source_ip=ip,
                            user=entry["user"],
                            description=f"Potential SQL injection detected in request path: {url}",
                            evidence=line,
                        )
                    )
                    break

            # XSS check
            for pat in self.XSS_PATTERNS:
                if re.search(pat, url):
                    incidents.append(
                        SecurityLogIncident(
                            rule_id="LOG-WEB-XSS",
                            rule_name="Cross-Site Scripting (XSS) Attempt Detected",
                            severity="MEDIUM",
                            timestamp=ts,
                            source_ip=ip,
                            user=entry["user"],
                            description=f"Potential XSS payload detected in request path: {url}",
                            evidence=line,
                        )
                    )
                    break

            # Path Traversal check
            for pat in self.TRAVERSAL_PATTERNS:
                if re.search(pat, url):
                    incidents.append(
                        SecurityLogIncident(
                            rule_id="LOG-WEB-TRAVERSAL",
                            rule_name="Directory Traversal Attempt Detected",
                            severity="HIGH",
                            timestamp=ts,
                            source_ip=ip,
                            user=entry["user"],
                            description=f"Directory traversal pattern detected in request path: {url}",
                            evidence=line,
                        )
                    )
                    break

        return incidents

    def analyze_windows_events(self, events: List[Dict[str, Any]]) -> List[SecurityLogIncident]:
        """
        Analyzes Windows Security Events (represented as dictionaries with EventID, TimeCreated, Data/Details).
        """
        incidents: List[SecurityLogIncident] = []
        failed_logons_by_ip: Dict[str, List[Dict[str, Any]]] = {}

        for evt in events:
            eid = int(evt.get("EventID", 0))
            ts = evt.get("TimeCreated", datetime.now().isoformat())
            data = evt.get("Data", {})

            # Event 4625: An account failed to log on
            if eid == 4625:
                ip = data.get("IpAddress", "Unknown")
                user = data.get("TargetUserName", "Unknown")
                if ip not in failed_logons_by_ip:
                    failed_logons_by_ip[ip] = []
                failed_logons_by_ip[ip].append({"timestamp": ts, "user": user, "event": evt})

            # Event 1102: The audit log was cleared (Tampering)
            elif eid == 1102:
                incidents.append(
                    SecurityLogIncident(
                        rule_id="LOG-WIN-1102",
                        rule_name="Audit Log Cleared (Potential Tampering)",
                        severity="CRITICAL",
                        timestamp=ts,
                        source_ip=data.get("IpAddress"),
                        user=data.get("SubjectUserName", "Unknown"),
                        description="Security event log was cleared by an administrator or attacker.",
                        evidence=str(evt),
                    )
                )

            # Event 4688: Process creation (Inspect for suspicious command lines)
            elif eid == 4688:
                cmdline = data.get("CommandLine", "")
                for pat in self.POWERSHELL_SUSPICIOUS:
                    if re.search(pat, cmdline):
                        incidents.append(
                            SecurityLogIncident(
                                rule_id="LOG-WIN-4688-PS",
                                rule_name="Suspicious PowerShell Process Execution",
                                severity="HIGH",
                                timestamp=ts,
                                source_ip=None,
                                user=data.get("SubjectUserName"),
                                description=f"Suspicious command-line flags observed in process creation: {cmdline}",
                                evidence=cmdline,
                            )
                        )
                        break

            # Event 4104: PowerShell Script Block Logging
            elif eid == 4104:
                script_text = data.get("ScriptBlockText", "")
                for pat in self.POWERSHELL_SUSPICIOUS:
                    if re.search(pat, script_text):
                        incidents.append(
                            SecurityLogIncident(
                                rule_id="LOG-WIN-4104-PS",
                                rule_name="Suspicious PowerShell Script Block Detected",
                                severity="HIGH",
                                timestamp=ts,
                                source_ip=None,
                                user=data.get("UserId"),
                                description="PowerShell script block contains known obfuscation or download cradles.",
                                evidence=script_text[:200],
                            )
                        )
                        break

        # Check brute force thresholds
        for ip, attempts in failed_logons_by_ip.items():
            if len(attempts) >= self.brute_force_threshold:
                usernames = list({a["user"] for a in attempts})
                incidents.append(
                    SecurityLogIncident(
                        rule_id="LOG-BRUTE-FORCE",
                        rule_name="Authentication Brute-Force Attack Detected",
                        severity="HIGH",
                        timestamp=attempts[-1]["timestamp"],
                        source_ip=ip,
                        user=", ".join(usernames),
                        description=f"{len(attempts)} failed login attempts detected from {ip} targeting users {usernames}.",
                        evidence=f"Attempt count: {len(attempts)}",
                    )
                )

        return incidents

    def analyze_syslog(self, lines: List[str]) -> List[SecurityLogIncident]:
        """Analyzes standard Linux / Unix Syslog and auth.log messages."""
        incidents: List[SecurityLogIncident] = []
        sshd_fail_pattern = r"(?i)(\w+\s+\d+\s+[\d:]+)\s+(\S+)\s+sshd\[\d+\]:\s+Failed\s+password\s+for\s+(invalid user\s+)?(\S+)\s+from\s+(\S+)\s+port\s+\d+"
        sudo_fail_pattern = r"(?i)(\w+\s+\d+\s+[\d:]+)\s+(\S+)\s+sudo:\s+(\S+)\s+:\s+\d+\s+incorrect\s+password\s+attempts"

        failed_ssh_counts: Dict[str, int] = {}
        last_seen_ts: Dict[str, str] = {}

        for line in lines:
            m_ssh = re.search(sshd_fail_pattern, line)
            if m_ssh:
                ts = m_ssh.group(1)
                user = m_ssh.group(4)
                ip = m_ssh.group(5)
                failed_ssh_counts[ip] = failed_ssh_counts.get(ip, 0) + 1
                last_seen_ts[ip] = ts

            m_sudo = re.search(sudo_fail_pattern, line)
            if m_sudo:
                incidents.append(
                    SecurityLogIncident(
                        rule_id="LOG-SYS-SUDO-FAIL",
                        rule_name="Sudo Authentication Failure",
                        severity="MEDIUM",
                        timestamp=m_sudo.group(1),
                        source_ip=None,
                        user=m_sudo.group(3),
                        description=f"Repeated incorrect sudo password attempts for user {m_sudo.group(3)}.",
                        evidence=line,
                    )
                )

        for ip, count in failed_ssh_counts.items():
            if count >= self.brute_force_threshold:
                incidents.append(
                    SecurityLogIncident(
                        rule_id="LOG-SSH-BRUTE-FORCE",
                        rule_name="SSH Brute-Force Attack Detected",
                        severity="HIGH",
                        timestamp=last_seen_ts.get(ip, "Unknown"),
                        source_ip=ip,
                        user=None,
                        description=f"{count} SSH authentication failures detected from {ip}.",
                        evidence=f"Failed attempts: {count}",
                    )
                )

        return incidents
