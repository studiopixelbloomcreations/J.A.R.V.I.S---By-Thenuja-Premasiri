"""
Capability 55: Security Report Generation
Aggregates findings from posture assessments, vulnerability management, log analysis,
malware scans, file integrity monitoring, firewall audits, dependency scanners, and SAST.
Generates comprehensive executive summaries, compliance cross-walks (NIST CSF, CIS Controls, ISO 27001),
risk scorecards, and prioritized remediation roadmaps in Markdown and JSON formats.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ConsolidatedFinding:
    source_capability: str
    rule_or_id: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str
    description: str
    remediation: str
    cwe_or_cve: Optional[str] = None


class SecurityReportGenerator:
    """Consolidates cross-capability security findings into executive reports."""

    def __init__(self, organization_name: str = "JARVIS Secured Infrastructure"):
        self.organization_name = organization_name
        self.findings: List[ConsolidatedFinding] = []
        self.metadata: Dict[str, Any] = {}

    def add_finding(
        self,
        source: str,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        description: str,
        remediation: str,
        cwe_or_cve: Optional[str] = None,
    ):
        """Adds a security finding to the consolidation register."""
        self.findings.append(
            ConsolidatedFinding(
                source_capability=source,
                rule_or_id=finding_id,
                title=title,
                severity=severity.upper(),
                category=category,
                description=description,
                remediation=remediation,
                cwe_or_cve=cwe_or_cve,
            )
        )

    def calculate_overall_risk_score(self) -> int:
        """
        Calculates an overall security risk score from 0 (pristine) to 100 (critical danger).
        Weights: Critical=25, High=12, Medium=5, Low=1.
        """
        weights = {"CRITICAL": 25, "HIGH": 12, "MEDIUM": 5, "LOW": 1, "INFO": 0}
        total_points = sum(weights.get(f.severity, 0) for f in self.findings)
        return min(100, total_points)

    def calculate_posture_grade(self, risk_score: int) -> str:
        """Translates risk score into letter grade."""
        # Lower risk = Higher grade
        if risk_score <= 10:
            return "A"
        elif risk_score <= 25:
            return "B"
        elif risk_score <= 45:
            return "C"
        elif risk_score <= 70:
            return "D"
        else:
            return "F"

    def get_severity_counts(self) -> Dict[str, int]:
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in self.findings:
            if f.severity in counts:
                counts[f.severity] += 1
        return counts

    def generate_json_report(self) -> str:
        """Produces machine-readable structured JSON audit report."""
        risk = self.calculate_overall_risk_score()
        report_data = {
            "organization": self.organization_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_risk_score": risk,
            "posture_grade": self.calculate_posture_grade(risk),
            "severity_summary": self.get_severity_counts(),
            "total_findings": len(self.findings),
            "findings": [
                {
                    "source": f.source_capability,
                    "id": f.rule_or_id,
                    "title": f.title,
                    "severity": f.severity,
                    "category": f.category,
                    "description": f.description,
                    "remediation": f.remediation,
                    "reference": f.cwe_or_cve,
                }
                for f in self.findings
            ],
            "compliance_mapping": {
                "NIST_CSF": {
                    "Identify": [f.title for f in self.findings if "posture" in f.source_capability.lower() or "inventory" in f.source_capability.lower()],
                    "Protect": [f.title for f in self.findings if "firewall" in f.source_capability.lower() or "password" in f.source_capability.lower()],
                    "Detect": [f.title for f in self.findings if "malware" in f.source_capability.lower() or "fim" in f.source_capability.lower() or "log" in f.source_capability.lower()],
                    "Respond": [f.title for f in self.findings if "incident" in f.source_capability.lower()],
                }
            },
        }
        return json.dumps(report_data, indent=2)

    def generate_markdown_report(self, report_title: str = "J.A.R.V.I.S. Cybersecurity Intelligence Audit Report") -> str:
        """Produces a publication-ready GitHub-flavored Markdown security audit report."""
        risk = self.calculate_overall_risk_score()
        grade = self.calculate_posture_grade(risk)
        counts = self.get_severity_counts()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            f"# {report_title}",
            f"**Organization:** {self.organization_name} | **Audit Date:** {now}\n",
            "---",
            "## 1. Executive Summary & Posture Scorecard",
            f"- **Security Posture Grade:** `{grade}`",
            f"- **Composite Risk Index:** `{risk} / 100` (Lower is better)",
            f"- **Total Findings:** `{len(self.findings)}`",
            f"- **Breakdown:** 🔴 **Critical:** {counts['CRITICAL']} | 🟠 **High:** {counts['HIGH']} | 🟡 **Medium:** {counts['MEDIUM']} | 🔵 **Low:** {counts['LOW']}\n",
            "---",
            "## 2. Priority Findings Matrix",
            "| ID | Source | Severity | Reference | Title | Remediation |",
            "|---|---|---|---|---|---|",
        ]

        # Prioritize by severity
        order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        sorted_findings = sorted(self.findings, key=lambda x: order.get(x.severity, 5))

        for f in sorted_findings:
            ref = f.cwe_or_cve or "N/A"
            lines.append(
                f"| `{f.rule_or_id}` | {f.source_capability} | **{f.severity}** | {ref} | {f.title} | {f.remediation[:45]}... |"
            )

        lines.extend([
            "\n---",
            "## 3. Prioritized Remediation Roadmap",
            "### Immediate Actions (Next 24 Hours)",
        ])

        critical_remediations = [f for f in sorted_findings if f.severity == "CRITICAL"]
        if critical_remediations:
            for f in critical_remediations:
                lines.append(f"1. **[{f.rule_or_id}] {f.title}:** {f.remediation}")
        else:
            lines.append("- *No Critical zero-day issues requiring immediate lockdown.*")

        lines.extend([
            "\n### Short-Term Hardening (Next 7-14 Days)",
        ])
        high_remediations = [f for f in sorted_findings if f.severity == "HIGH"]
        if high_remediations:
            for f in high_remediations:
                lines.append(f"1. **[{f.rule_or_id}] {f.title}:** {f.remediation}")
        else:
            lines.append("- *No High-severity exposures identified.*")

        lines.extend([
            "\n---",
            "## 4. Compliance & Framework Cross-Walk",
            "| Framework | Control Family | Assessment Status |",
            "|---|---|---|",
            "| **NIST CSF 2.0** | Identify (ID.AM, ID.RA) | Assessed via Network Inventory & Vulnerability Tracking |",
            "| **NIST CSF 2.0** | Protect (PR.AC, PR.IP) | Assessed via Firewall, Password, & Secure Coding Audits |",
            "| **NIST CSF 2.0** | Detect (DE.CM, DE.AE) | Assessed via Log Analysis, FIM, & Malware Heuristics |",
            "| **NIST CSF 2.0** | Respond (RS.MA, RS.MI) | Governed via Incident Response Lifecycle Assistant |",
            "| **CIS Controls v8** | Control 4, 7, 10, 16 | Audited against Host Baselines & Secure Configuration |",
            "| **ISO/IEC 27001** | Annex A.8, A.12 | Evaluated for Malware Protection & Cryptographic Controls |",
            "\n*Report compiled autonomously by J.A.R.V.I.S. Cybersecurity Intelligence Specialist.*",
        ])

        return "\n".join(lines)
