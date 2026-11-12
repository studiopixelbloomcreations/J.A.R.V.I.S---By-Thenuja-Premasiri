"""
Capability 59: Sandbox Analysis
Simulated behavioral analysis and static artifact extraction for suspicious files/scripts.
Detects persistence mechanisms (Registry Run keys, Scheduled Tasks), defense evasion
(anti-VM, anti-debugging, sleep delays, AMSI bypass), credential harvesting (LSASS dumps, SAM),
and decodes embedded base64 payloads to extract Indicators of Compromise (IOCs).
"""

import re
import base64
import hashlib
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class SandboxBehavior:
    category: str  # PERSISTENCE, EVASION, CREDENTIAL_THEFT, NETWORK_C2, EXECUTION
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    name: str
    description: str
    matched_text: str


@dataclass
class SandboxAnalysisReport:
    sample_name: str
    sample_sha256: str
    verdict: str  # BENIGN, SUSPICIOUS, MALICIOUS
    threat_score: int  # 0 to 100
    behaviors: List[SandboxBehavior] = field(default_factory=list)
    extracted_urls: List[str] = field(default_factory=list)
    extracted_ips: List[str] = field(default_factory=list)
    extracted_registry_keys: List[str] = field(default_factory=list)
    decoded_payloads: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_name": self.sample_name,
            "sample_sha256": self.sample_sha256,
            "verdict": self.verdict,
            "threat_score": self.threat_score,
            "behaviors": [
                {
                    "category": b.category,
                    "severity": b.severity,
                    "name": b.name,
                    "description": b.description,
                    "matched_text": b.matched_text,
                }
                for b in self.behaviors
            ],
            "extracted_urls": self.extracted_urls,
            "extracted_ips": self.extracted_ips,
            "extracted_registry_keys": self.extracted_registry_keys,
            "decoded_payloads": self.decoded_payloads,
        }


class SandboxAnalyzer:
    """Performs deep heuristic and behavioral sandbox analysis on files and scripts."""

    BEHAVIOR_PATTERNS = [
        # Persistence
        (
            r"(?i)(CurrentVersion\\Run|CurrentVersion\\RunOnce)",
            "PERSISTENCE",
            "HIGH",
            "Registry Run Key Persistence",
            "Attempts to achieve persistence by adding executable to Windows Registry Run keys.",
        ),
        (
            r"(?i)(schtasks(\.exe)?\s+/create)",
            "PERSISTENCE",
            "HIGH",
            "Scheduled Task Creation",
            "Attempts to establish persistence via Windows Scheduled Tasks.",
        ),
        (
            r"(?i)(sc(\.exe)?\s+create\b)",
            "PERSISTENCE",
            "HIGH",
            "Windows Service Installation",
            "Attempts to install a new persistent Windows background service.",
        ),

        # Defense Evasion
        (
            r"(?i)(amsiInitFailed|AmsiUtils)",
            "EVASION",
            "CRITICAL",
            "AMSI Memory Patching / Bypass",
            "Attempts to patch Antimalware Scan Interface (AMSI) in process memory.",
        ),
        (
            r"(?i)(vmware|virtualbox|vbox|qemu|wine_get_version)",
            "EVASION",
            "MEDIUM",
            "Virtual Machine / Sandbox Detection",
            "Checks for virtualization artifacts to evade analysis environments.",
        ),
        (
            r"(?i)(isdebuggerpresent|checkremotedebuggerpresent)",
            "EVASION",
            "MEDIUM",
            "Anti-Debugging Check",
            "Queries debugger status to alter execution behavior when inspected.",
        ),
        (
            r"(?i)(start-sleep\s+-s(econds)?\s+([3-9]\d{2,}|\d{4,})|sleep\s+([3-9]\d{2,}|\d{4,}))",
            "EVASION",
            "MEDIUM",
            "Extended Sleep Delay Evasion",
            "Introduces multi-minute sleep delays to exhaust automated sandbox timeouts.",
        ),

        # Credential Theft
        (
            r"(?i)(procdump(\.exe)?.*lsass|comsvcs\.dll.*#24|minidump.*lsass)",
            "CREDENTIAL_THEFT",
            "CRITICAL",
            "LSASS Process Memory Dumping",
            "Attempts to dump LSASS memory to extract cleartext passwords and Kerberos tickets.",
        ),
        (
            r"(?i)(reg(\.exe)?\s+save\s+hklm\\(sam|system))",
            "CREDENTIAL_THEFT",
            "CRITICAL",
            "SAM Hive Extraction",
            "Attempts to export the Windows SAM database containing local NTLM password hashes.",
        ),
        (
            r"(?i)(sekurlsa::logonpasswords|privilege::debug)",
            "CREDENTIAL_THEFT",
            "CRITICAL",
            "Mimikatz Credential Harvesting Signature",
            "Known Mimikatz post-exploitation commands detected.",
        ),

        # Network C2 & Download
        (
            r"(?i)(downloadstring\s*\(|downloadfile\s*\(|certutil.*-urlcache)",
            "NETWORK_C2",
            "HIGH",
            "Remote File Download Cradle",
            "Downloads secondary stage payload from remote infrastructure.",
        ),
    ]

    def extract_strings(self, data: bytes, min_length: int = 4) -> List[str]:
        """Extracts printable ASCII and UTF-16 strings from binary payload."""
        result = []
        ascii_pat = rb"[\x20-\x7E]{" + str(min_length).encode() + rb",}"
        for match in re.finditer(ascii_pat, data):
            result.append(match.group().decode("latin-1"))

        # Basic wide char UTF-16 extraction
        utf16_pat = rb"(?:[\x20-\x7E]\x00){" + str(min_length).encode() + rb",}"
        for match in re.finditer(utf16_pat, data):
            try:
                result.append(match.group().decode("utf-16le"))
            except Exception:
                pass
        return result

    def decode_base64_blobs(self, text: str) -> List[str]:
        """Finds and decodes candidate base64 strings in payload."""
        decoded_items: List[str] = []
        # Match candidate base64 sequences of 24+ characters
        candidates = re.findall(r"[A-Za-z0-9+/]{24,}={0,2}", text)
        for cand in candidates:
            try:
                b = base64.b64decode(cand)
                # If decoded bytes contain mostly printable chars
                if len(b) > 10 and any(c in b for c in [b"http", b"powershell", b"cmd", b"iex", b"reg"]):
                    decoded_items.append(b.decode("latin-1", errors="ignore"))
            except Exception:
                pass
        return decoded_items

    def analyze_payload(self, data: bytes, name: str = "sample.bin") -> SandboxAnalysisReport:
        """Executes full static and behavioral simulation audit on sample data."""
        sha256 = hashlib.sha256(data).hexdigest()
        raw_text = data.decode("latin-1", errors="ignore")
        extracted_strings = self.extract_strings(data)
        decoded = self.decode_base64_blobs(raw_text)

        all_text = raw_text + "\n" + "\n".join(decoded)

        # IOC extraction
        urls = list(set(re.findall(r"https?://[A-Za-z0-9\.\-_/]+", all_text)))
        ips = list(set(re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", all_text)))
        # Filter local loopback / 0.0.0.0 from IOCs
        ips = [ip for ip in ips if ip not in ["127.0.0.1", "0.0.0.0", "255.255.255.255"]]

        reg_keys = list(set(re.findall(r"(?i)(HKLM\\[A-Za-z0-9_\\]+|HKCU\\[A-Za-z0-9_\\]+)", all_text)))

        behaviors: List[SandboxBehavior] = []
        threat_score = 0

        for pat, cat, sev, title, desc in self.BEHAVIOR_PATTERNS:
            match = re.search(pat, all_text)
            if match:
                behaviors.append(
                    SandboxBehavior(
                        category=cat,
                        severity=sev,
                        name=title,
                        description=desc,
                        matched_text=match.group(0)[:100],
                    )
                )
                deduction = 40 if sev == "CRITICAL" else (25 if sev == "HIGH" else 15)
                threat_score += deduction

        threat_score = min(100, threat_score)

        if threat_score >= 60 or any(b.severity == "CRITICAL" for b in behaviors):
            verdict = "MALICIOUS"
        elif threat_score >= 25 or len(behaviors) > 0:
            verdict = "SUSPICIOUS"
        else:
            verdict = "BENIGN"

        return SandboxAnalysisReport(
            sample_name=name,
            sample_sha256=sha256,
            verdict=verdict,
            threat_score=threat_score,
            behaviors=behaviors,
            extracted_urls=urls,
            extracted_ips=ips,
            extracted_registry_keys=reg_keys,
            decoded_payloads=decoded,
        )
