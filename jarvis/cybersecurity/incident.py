"""
Capability 58: Incident Response Assistant (NIST SP 800-61 Lifecycle Management)
Guides incident response workflows: triage, priority classification (P1-P4),
dynamic containment playbooks, forensic evidence logging with cryptographic chain-of-custody,
and post-incident timeline generation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib


@dataclass
class EvidenceArtifact:
    artifact_id: str
    artifact_type: str  # RAM_DUMP, DISK_IMAGE, LOG_FILE, NETWORK_PCAP, MALWARE_SAMPLE
    file_path: str
    sha256_hash: str
    collected_by: str
    collected_at: str
    chain_of_custody_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "file_path": self.file_path,
            "sha256_hash": self.sha256_hash,
            "collected_by": self.collected_by,
            "collected_at": self.collected_at,
            "chain_of_custody_notes": self.chain_of_custody_notes,
        }


@dataclass
class TimelineEntry:
    timestamp: str
    phase: str
    action: str
    actor: str
    details: str


@dataclass
class IncidentRecord:
    incident_id: str
    title: str
    incident_type: str  # RANSOMWARE, PHISHING, DATA_EXFILTRATION, MALWARE, UNAUTHORIZED_ACCESS, DOS
    impact_level: str   # CRITICAL, HIGH, MEDIUM, LOW
    urgency_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    priority: str       # P1, P2, P3, P4
    phase: str          # DETECTION, CONTAINMENT, ERADICATION, RECOVERY, LESSONS_LEARNED, CLOSED
    assigned_lead: str
    containment_playbook: List[str] = field(default_factory=list)
    evidence_items: List[EvidenceArtifact] = field(default_factory=list)
    timeline: List[TimelineEntry] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "incident_type": self.incident_type,
            "impact_level": self.impact_level,
            "urgency_level": self.urgency_level,
            "priority": self.priority,
            "phase": self.phase,
            "assigned_lead": self.assigned_lead,
            "containment_playbook": self.containment_playbook,
            "evidence_items": [e.to_dict() for e in self.evidence_items],
            "timeline": [
                {
                    "timestamp": t.timestamp,
                    "phase": t.phase,
                    "action": t.action,
                    "actor": t.actor,
                    "details": t.details,
                }
                for t in self.timeline
            ],
            "created_at": self.created_at,
        }


class IncidentResponseAssistant:
    """Orchestrates NIST SP 800-61 incident response lifecycles and evidence tracking."""

    # Dynamic containment playbooks tailored to incident type
    PLAYBOOK_TEMPLATES = {
        "RANSOMWARE": [
            "[CRITICAL] Immediately sever network connection (unplug Ethernet / disable Wi-Fi adapter) to stop lateral encryption spread.",
            "[FORENSIC] Do NOT power off or reboot system; preserve volatile RAM containing encryption keys.",
            "[ISOLATION] Execute network isolation command: netsh advfirewall set allprofiles state on",
            "[ACCOUNTS] Revoke active Kerberos tickets and disable compromised domain accounts / credentials.",
            "[BACKUPS] Verify offline / immutable backup status and disconnect backup targets.",
            "[TRIAGE] Identify encrypted extensions and check for known decryptors in NoMoreRansom database.",
        ],
        "PHISHING": [
            "[CONTAINMENT] Revoke compromised user active session tokens and force immediate password reset.",
            "[CONTAINMENT] Block offending malicious domain and sender IP on email gateway and perimeter firewall.",
            "[SEARCH] Query SIEM / mail exchange for other recipients of the same message ID or subject.",
            "[PURGE] Purge malicious email from all user mailboxes across tenant.",
            "[AUDIT] Inspect user mailbox for unauthorized forwarding rules or OAuth application consents.",
        ],
        "DATA_EXFILTRATION": [
            "[CONTAINMENT] Terminate active exfiltration socket connections: Get-NetTCPConnection | Where-Object RemotePort -in (443, 80) | ...",
            "[ISOLATION] Block destination IP and domain on egress proxies and boundary firewalls.",
            "[ACCOUNTS] Suspend API keys and service principal credentials associated with the exfiltration stream.",
            "[FORENSIC] Preserve egress proxy logs, NetFlow records, and host DNS cache for volume quantification.",
        ],
        "MALWARE": [
            "[CONTAINMENT] Terminate suspicious process PIDs and quarantine parent binaries.",
            "[ISOLATION] Isolate affected endpoint from internal LAN.",
            "[PRESERVATION] Capture file hash and memory dump for sandboxing before removal.",
            "[PERSISTENCE] Inspect and clean Run registry keys, Scheduled Tasks, and WMI event subscriptions.",
        ],
        "UNAUTHORIZED_ACCESS": [
            "[CONTAINMENT] Terminate all active interactive sessions: qwinsta / rwinsta",
            "[IDENTITY] Reset administrative passwords and enforce MFA re-enrollment.",
            "[AUDIT] Audit Windows Security Event 4624 (logon) and 4672 (special privileges) to trace entry point.",
            "[REMEDIATION] Patch exploited vulnerability or close exposed port (e.g. RDP 3389).",
        ],
    }

    def __init__(self):
        self.incidents: Dict[str, IncidentRecord] = {}

    @staticmethod
    def calculate_priority(impact: str, urgency: str) -> str:
        """Determines ITIL/NIST incident priority (P1 to P4)."""
        imp = impact.upper()
        urg = urgency.upper()

        if imp == "CRITICAL" and urg in ["CRITICAL", "HIGH"]:
            return "P1"
        if imp == "CRITICAL" or urg == "CRITICAL":
            return "P2"
        if imp == "HIGH" or urg == "HIGH":
            return "P2" if (imp == "HIGH" and urg == "HIGH") else "P3"
        if imp == "MEDIUM" or urg == "MEDIUM":
            return "P3"
        return "P4"

    def create_incident(
        self,
        title: str,
        incident_type: str,
        impact_level: str,
        urgency_level: str,
        lead: str = "SecOps Lead",
        incident_id: Optional[str] = None,
    ) -> IncidentRecord:
        """Initializes a new cybersecurity incident case."""
        iid = incident_id or f"INC-{len(self.incidents) + 1:04d}"
        itype = incident_type.upper()
        prio = self.calculate_priority(impact_level, urgency_level)
        playbook = list(self.PLAYBOOK_TEMPLATES.get(itype, self.PLAYBOOK_TEMPLATES["MALWARE"]))

        now = datetime.now(timezone.utc).isoformat()
        initial_entry = TimelineEntry(
            timestamp=now,
            phase="DETECTION",
            action="Incident Created & Triaged",
            actor=lead,
            details=f"Case opened with Priority {prio}. Type: {itype}. Impact: {impact_level}.",
        )

        record = IncidentRecord(
            incident_id=iid,
            title=title,
            incident_type=itype,
            impact_level=impact_level.upper(),
            urgency_level=urgency_level.upper(),
            priority=prio,
            phase="DETECTION",
            assigned_lead=lead,
            containment_playbook=playbook,
            timeline=[initial_entry],
        )
        self.incidents[iid] = record
        return record

    def transition_phase(self, incident_id: str, new_phase: str, actor: str, notes: str = "") -> bool:
        """Advances incident through NIST lifecycle phases."""
        valid_phases = ["DETECTION", "CONTAINMENT", "ERADICATION", "RECOVERY", "LESSONS_LEARNED", "CLOSED"]
        if new_phase not in valid_phases:
            raise ValueError(f"Invalid phase: {new_phase}. Must be one of {valid_phases}")

        if incident_id in self.incidents:
            inc = self.incidents[incident_id]
            inc.phase = new_phase
            inc.timeline.append(
                TimelineEntry(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    phase=new_phase,
                    action=f"Phase Transition to {new_phase}",
                    actor=actor,
                    details=notes or f"Advanced lifecycle phase to {new_phase}.",
                )
            )
            return True
        return False

    def log_evidence(
        self,
        incident_id: str,
        artifact_type: str,
        file_path: str,
        data_bytes: Optional[bytes] = None,
        collector: str = "SecOps Investigator",
        custody_note: str = "Initial forensic seizure",
    ) -> EvidenceArtifact:
        """Securely logs digital evidence with SHA-256 integrity hash."""
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found.")

        if data_bytes is not None:
            sha = hashlib.sha256(data_bytes).hexdigest()
        else:
            sha = hashlib.sha256(file_path.encode("utf-8")).hexdigest()

        artifact_id = f"EV-{len(self.incidents[incident_id].evidence_items) + 1:03d}"
        now = datetime.now(timezone.utc).isoformat()

        evidence = EvidenceArtifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type.upper(),
            file_path=file_path,
            sha256_hash=sha,
            collected_by=collector,
            collected_at=now,
            chain_of_custody_notes=[f"[{now}] Collected by {collector}: {custody_note}"],
        )

        self.incidents[incident_id].evidence_items.append(evidence)
        self.incidents[incident_id].timeline.append(
            TimelineEntry(
                timestamp=now,
                phase=self.incidents[incident_id].phase,
                action=f"Evidence Logged: {artifact_id}",
                actor=collector,
                details=f"Secured {artifact_type} ({file_path}) with SHA-256: {sha}",
            )
        )
        return evidence
