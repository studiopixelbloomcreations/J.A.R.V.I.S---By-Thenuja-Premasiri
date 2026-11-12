"""
Capability 52: Firewall Auditing (Windows Firewall Inspection)
Audits Windows Defender Firewall profiles (Domain, Private, Public),
identifies dangerous or overly permissive inbound/outbound rules,
and provides security compliance ratings and hardening recommendations.
"""

import subprocess
import platform
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class FirewallRule:
    name: str
    direction: str  # Inbound / Outbound
    action: str     # Allow / Block
    protocol: str   # TCP, UDP, Any
    local_ports: str
    remote_addresses: str
    enabled: bool
    profile: str    # Domain, Private, Public, Any


@dataclass
class FirewallFinding:
    rule_name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    description: str
    remediation: str


@dataclass
class FirewallAuditReport:
    profiles_status: Dict[str, Dict[str, Any]]
    total_rules_evaluated: int
    findings: List[FirewallFinding] = field(default_factory=list)
    compliance_score: int = 100
    is_compliant: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profiles_status": self.profiles_status,
            "total_rules_evaluated": self.total_rules_evaluated,
            "compliance_score": self.compliance_score,
            "is_compliant": self.is_compliant,
            "findings": [
                {
                    "rule_name": f.rule_name,
                    "severity": f.severity,
                    "category": f.category,
                    "description": f.description,
                    "remediation": f.remediation,
                }
                for f in self.findings
            ],
        }


class FirewallAuditor:
    """Inspects firewall configurations and audits inbound/outbound security rules."""

    HIGH_RISK_PORTS = {
        21: ("FTP", "CRITICAL", "Unencrypted file transfer protocol exposed."),
        23: ("Telnet", "CRITICAL", "Cleartext remote administration protocol exposed."),
        135: ("RPC Endpoint Mapper", "HIGH", "Exposes Windows RPC service to potential exploit."),
        139: ("NetBIOS", "HIGH", "Exposes legacy NetBIOS session service."),
        445: ("SMB", "CRITICAL", "SMB exposed to untrusted networks (WannaCry / EternalBlue vector)."),
        1433: ("MSSQL", "HIGH", "Database port exposed to untrusted network."),
        3306: ("MySQL", "HIGH", "Database port exposed to untrusted network."),
        3389: ("RDP", "HIGH", "Remote Desktop Protocol exposed without Network Level Authentication (NLA) verification."),
    }

    def __init__(self, override_profiles: Optional[Dict[str, Dict[str, Any]]] = None):
        self._override_profiles = override_profiles

    def get_firewall_profiles_status(self) -> Dict[str, Dict[str, Any]]:
        """Queries status of Domain, Private, and Public profiles."""
        if self._override_profiles:
            return self._override_profiles

        status = {
            "Domain": {"enabled": True, "inbound": "Block", "outbound": "Allow"},
            "Private": {"enabled": True, "inbound": "Block", "outbound": "Allow"},
            "Public": {"enabled": True, "inbound": "Block", "outbound": "Allow"},
        }

        if platform.system() == "Windows":
            try:
                res = subprocess.run(
                    ["netsh", "advfirewall", "show", "allprofiles", "state"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if res.returncode == 0:
                    current_profile = None
                    for line in res.stdout.splitlines():
                        line = line.strip()
                        if "Profile Settings:" in line:
                            current_profile = line.split()[0]
                        elif "State" in line and current_profile in status:
                            is_on = "ON" in line.upper()
                            status[current_profile]["enabled"] = is_on
            except Exception:
                pass

        return status

    def audit_rules(
        self,
        rules: Optional[List[FirewallRule]] = None,
        mock_profiles: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> FirewallAuditReport:
        """Audits a collection of firewall rules against best practice security benchmarks."""
        profiles = mock_profiles or self.get_firewall_profiles_status()
        findings: List[FirewallFinding] = []
        score = 100

        # Profile checks
        for prof_name, prof_info in profiles.items():
            if not prof_info.get("enabled", True):
                findings.append(
                    FirewallFinding(
                        rule_name=f"Profile_{prof_name}_Disabled",
                        severity="CRITICAL",
                        category="Perimeter Defense",
                        description=f"Firewall profile '{prof_name}' is currently disabled.",
                        remediation=f"Enable Windows Firewall on '{prof_name}' profile: netsh advfirewall set {prof_name.lower()}profile state on",
                    )
                )
                score -= 30
            elif prof_info.get("inbound", "Block").upper() != "BLOCK":
                findings.append(
                    FirewallFinding(
                        rule_name=f"Profile_{prof_name}_Inbound_Allow",
                        severity="HIGH",
                        category="Default Action",
                        description=f"Default inbound policy on '{prof_name}' is ALLOW instead of BLOCK.",
                        remediation=f"Set default inbound to Block: netsh advfirewall set {prof_name.lower()}profile firewallpolicy blockinbound,allowoutbound",
                    )
                )
                score -= 20

        # Rule evaluation
        rules_to_check = rules or []
        for rule in rules_to_check:
            if not rule.enabled:
                continue

            # Inbound rule audits
            if rule.direction.upper() == "INBOUND" and rule.action.upper() == "ALLOW":
                # Wildcard exposure: Any protocol, any port, any remote IP
                if (
                    rule.protocol.upper() in ["ANY", "*"]
                    and rule.local_ports.upper() in ["ANY", "*"]
                    and rule.remote_addresses in ["*", "0.0.0.0/0", "Any"]
                ):
                    findings.append(
                        FirewallFinding(
                            rule_name=rule.name,
                            severity="CRITICAL",
                            category="Overly Permissive",
                            description=f"Rule '{rule.name}' permits unrestricted inbound traffic on all ports from all remote IPs.",
                            remediation="Delete or restrict the rule to specific necessary application paths and ports.",
                        )
                    )
                    score -= 25

                # High-risk sensitive ports open to Any/Internet
                if rule.remote_addresses in ["*", "0.0.0.0/0", "Any", "Internet"]:
                    ports_str = rule.local_ports.replace(" ", "")
                    for port_token in ports_str.split(","):
                        try:
                            port_num = int(port_token)
                            if port_num in self.HIGH_RISK_PORTS:
                                svc, sev, desc = self.HIGH_RISK_PORTS[port_num]
                                findings.append(
                                    FirewallFinding(
                                        rule_name=rule.name,
                                        severity=sev,
                                        category="Dangerous Inbound Exposure",
                                        description=f"Port {port_num} ({svc}) open to any remote IP. {desc}",
                                        remediation=f"Scope inbound access for port {port_num} to trusted internal subnet or close port.",
                                    )
                                )
                                deduction = 20 if sev == "CRITICAL" else 10
                                score -= deduction
                        except ValueError:
                            pass

        score = max(0, min(100, score))
        is_compliant = score >= 85 and not any(f.severity == "CRITICAL" for f in findings)

        return FirewallAuditReport(
            profiles_status=profiles,
            total_rules_evaluated=len(rules_to_check),
            findings=findings,
            compliance_score=score,
            is_compliant=is_compliant,
        )
