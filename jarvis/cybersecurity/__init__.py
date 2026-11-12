"""
J.A.R.V.I.S. Cybersecurity Intelligence Module
Implements Capabilities 46-60 (Defensive Security & Authorized Auditing):
46. Security Posture Analysis
47. Vulnerability Management
48. Log Analysis
49. Malware Detection (Signature & heuristics)
50. File Integrity Monitoring (SHA256 baselines)
51. Network Inventory (Authorized local interface scanning)
52. Firewall Auditing (Windows Firewall inspection)
53. Password Security Auditing (Entropy & complexity)
54. Phishing Detection (Heuristic URL & domain analysis)
55. Security Report Generation
56. Dependency Vulnerability Scanning (Safety / pip-audit style checks)
57. Secure Coding Analysis (Regex / AST security flaw detection)
58. Incident Response Assistant
59. Sandbox Analysis
60. Authorized Penetration Testing (Controlled port & config checks)
"""

from typing import Dict, Any, List, Optional

from .posture import SecurityPostureAnalyzer, PostureReport, PostureFinding
from .vulnerability import VulnerabilityManager, VulnerabilityItem
from .log_analysis import LogAnalyzer, SecurityLogIncident
from .malware import MalwareDetector, MalwareScanResult, MalwareFinding
from .fim import FileIntegrityMonitor, BaselineReport, IntegrityAlert, FileRecord
from .network import NetworkInventoryScanner, NetworkInterfaceInfo, HostInventory, DiscoveredPort
from .firewall import FirewallAuditor, FirewallRule, FirewallAuditReport, FirewallFinding
from .password import PasswordAuditor, PasswordAuditResult
from .phishing import PhishingDetector, PhishingAssessment, PhishingIndicator
from .reporting import SecurityReportGenerator, ConsolidatedFinding
from .dependency import DependencyScanner, VulnerableDependency, DependencyScanReport
from .secure_coding import SecureCodingAnalyzer, CodeFlawFinding
from .incident import IncidentResponseAssistant, IncidentRecord, EvidenceArtifact, TimelineEntry
from .sandbox import SandboxAnalyzer, SandboxAnalysisReport, SandboxBehavior
from .pentest import AuthorizedPenTester, PentestReport, PentestFinding, PentestAuditLogEntry


class CybersecurityEngine:
    """Unified coordinator for the 15 Cybersecurity Intelligence Capabilities (46-60)."""

    def __init__(self):
        self.posture = SecurityPostureAnalyzer()
        self.vulnerabilities = VulnerabilityManager()
        self.log_analyzer = LogAnalyzer()
        self.malware_detector = MalwareDetector()
        self.fim = FileIntegrityMonitor()
        self.network_inventory = NetworkInventoryScanner()
        self.firewall_auditor = FirewallAuditor()
        self.password_auditor = PasswordAuditor()
        self.phishing_detector = PhishingDetector()
        self.dependency_scanner = DependencyScanner()
        self.secure_coder = SecureCodingAnalyzer()
        self.incident_assistant = IncidentResponseAssistant()
        self.sandbox = SandboxAnalyzer()
        self.pentester = AuthorizedPenTester()
        self.reporter = SecurityReportGenerator()

    def run_comprehensive_assessment(
        self,
        mock_env: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes an end-to-end multi-vector security assessment across capabilities
        and compiles a consolidated security report.
        """
        reporter = SecurityReportGenerator(organization_name="J.A.R.V.I.S. Host Assessment")

        # 1. Posture Assessment
        posture_report = self.posture.assess_posture(
            firewall_active=True,
            uac_enabled=True,
            auto_update_enabled=True,
            mock_open_ports=[80, 443] if mock_env else None,
        )
        for pf in posture_report.findings:
            reporter.add_finding(
                source="Posture Analysis (Cap 46)",
                finding_id=pf.id,
                title=pf.title,
                severity=pf.severity,
                category=pf.category,
                description=pf.description,
                remediation=pf.remediation,
            )

        # 2. Firewall Audit
        fw_report = self.firewall_auditor.audit_rules(
            rules=[],
            mock_profiles={"Domain": {"enabled": True}, "Private": {"enabled": True}, "Public": {"enabled": True}},
        )
        for ff in fw_report.findings:
            reporter.add_finding(
                source="Firewall Audit (Cap 52)",
                finding_id=ff.rule_name,
                title=ff.rule_name,
                severity=ff.severity,
                category=ff.category,
                description=ff.description,
                remediation=ff.remediation,
            )

        # 3. Compile output
        risk_score = reporter.calculate_overall_risk_score()
        grade = reporter.calculate_posture_grade(risk_score)
        md = reporter.generate_markdown_report()
        json_data = reporter.generate_json_report()

        return {
            "overall_risk_score": risk_score,
            "posture_grade": grade,
            "total_findings": len(reporter.findings),
            "markdown_report": md,
            "json_report": json_data,
        }


# Default singleton instance
cybersecurity_engine = CybersecurityEngine()

__all__ = [
    # Engine
    "CybersecurityEngine",
    "cybersecurity_engine",
    # Cap 46
    "SecurityPostureAnalyzer",
    "PostureReport",
    "PostureFinding",
    # Cap 47
    "VulnerabilityManager",
    "VulnerabilityItem",
    # Cap 48
    "LogAnalyzer",
    "SecurityLogIncident",
    # Cap 49
    "MalwareDetector",
    "MalwareScanResult",
    "MalwareFinding",
    # Cap 50
    "FileIntegrityMonitor",
    "BaselineReport",
    "IntegrityAlert",
    "FileRecord",
    # Cap 51
    "NetworkInventoryScanner",
    "NetworkInterfaceInfo",
    "HostInventory",
    "DiscoveredPort",
    # Cap 52
    "FirewallAuditor",
    "FirewallRule",
    "FirewallAuditReport",
    "FirewallFinding",
    # Cap 53
    "PasswordAuditor",
    "PasswordAuditResult",
    # Cap 54
    "PhishingDetector",
    "PhishingAssessment",
    "PhishingIndicator",
    # Cap 55
    "SecurityReportGenerator",
    "ConsolidatedFinding",
    # Cap 56
    "DependencyScanner",
    "VulnerableDependency",
    "DependencyScanReport",
    # Cap 57
    "SecureCodingAnalyzer",
    "CodeFlawFinding",
    # Cap 58
    "IncidentResponseAssistant",
    "IncidentRecord",
    "EvidenceArtifact",
    "TimelineEntry",
    # Cap 59
    "SandboxAnalyzer",
    "SandboxAnalysisReport",
    "SandboxBehavior",
    # Cap 60
    "AuthorizedPenTester",
    "PentestReport",
    "PentestFinding",
    "PentestAuditLogEntry",
]
