"""
Source Provenance & Citation Tracking Engine for J.A.R.V.I.S.
Capability 99: Source Provenance

Maintains verifiable data lineage, confidence scores, origin metadata,
transformation audit logs, and formatted citations for all knowledge items,
facts, memories, and research documents.
"""

import os
import json
import time
import uuid
import pathlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..config import DATA_DIR

PROVENANCE_FILE = DATA_DIR / "provenance_ledger.json"


class SourceProvenanceTracker:
    """
    Tracks complete lineage, source provenance, verification history,
    and formal citations across the knowledge and memory subsystems.
    """

    ORIGIN_TYPES = {
        "user_explicit": 1.0,
        "authoritative_doc": 0.95,
        "web_research": 0.85,
        "system_learned": 0.80,
        "ocr_capture": 0.75,
        "inferred": 0.65
    }

    def __init__(self, storage_path: Optional[pathlib.Path] = None):
        self.storage_path = storage_path or PROVENANCE_FILE
        self.records: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        """Loads provenance ledger from persistent storage."""
        if self.storage_path and self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self.records = data.get("records", {})
            except Exception:
                self.records = {}
        else:
            self.records = {}

    def save(self):
        """Persists provenance ledger to disk."""
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "total_records": len(self.records),
                "records": self.records
            }
            self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def register_provenance(
        self,
        target_id: str,
        origin_type: str = "user_explicit",
        origin_uri: str = "notes/captures",
        author: str = "Thenuja Premasiri",
        confidence: Optional[float] = None,
        notes: str = "",
        verification_status: str = "verified"
    ) -> Dict[str, Any]:
        """
        Creates or updates a provenance record for a specific knowledge node or fact.
        """
        now_iso = datetime.now().isoformat()
        assigned_confidence = confidence if confidence is not None else self.ORIGIN_TYPES.get(origin_type, 0.8)

        record_id = self.records.get(target_id, {}).get("record_id", str(uuid.uuid4())[:8])
        history = self.records.get(target_id, {}).get("transformation_history", [])

        history.append({
            "action": "registered" if not history else "updated",
            "timestamp": now_iso,
            "operator": author,
            "notes": notes or f"Registered via {origin_type}"
        })

        record = {
            "record_id": record_id,
            "target_id": target_id,
            "origin_type": origin_type,
            "origin_uri": origin_uri,
            "author": author,
            "created_at": self.records.get(target_id, {}).get("created_at", now_iso),
            "last_modified": now_iso,
            "confidence_score": round(max(0.0, min(1.0, assigned_confidence)), 2),
            "verification_status": verification_status,
            "transformation_history": history
        }

        self.records[target_id] = record
        self.save()
        return record

    def get_provenance(self, target_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves provenance record for a given target."""
        return self.records.get(target_id)

    def verify_source(self, target_id: str, status: str = "verified", verifier: str = "J.A.R.V.I.S.") -> bool:
        """Updates verification status and records an audit step."""
        if target_id not in self.records:
            return False

        rec = self.records[target_id]
        rec["verification_status"] = status
        rec["transformation_history"].append({
            "action": f"status_change_{status}",
            "timestamp": datetime.now().isoformat(),
            "operator": verifier,
            "notes": f"Verification status updated to {status}"
        })
        self.save()
        return True

    def record_transformation(self, target_id: str, action: str, operator: str, notes: str = ""):
        """Appends a transformation or modification event to the lineage trail."""
        if target_id in self.records:
            self.records[target_id]["transformation_history"].append({
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "operator": operator,
                "notes": notes
            })
            self.records[target_id]["last_modified"] = datetime.now().isoformat()
            self.save()

    def format_citation(self, target_id: str, style: str = "inline") -> str:
        """
        Formats a citation for the knowledge item in inline, footnote, or academic style.
        """
        rec = self.records.get(target_id)
        if not rec:
            return f"[{target_id}]"

        author = rec.get("author", "Unknown")
        uri = rec.get("origin_uri", "")
        origin = rec.get("origin_type", "doc")

        if style == "footnote":
            return f"[^{rec['record_id']}]: {author}. \"{target_id}\" ({origin}). Source: {uri}."
        elif style == "academic":
            year = rec.get("created_at", "")[:4] or "2026"
            return f"{author} ({year}). {target_id}. Lineage Ref: {rec['record_id']} [{uri}]."
        else:  # inline
            return f"[{rec['record_id']}: {target_id}]"

    def get_audit_trail(self, target_id: str) -> List[Dict[str, Any]]:
        """Returns the complete transformation and verification audit trail."""
        rec = self.records.get(target_id)
        return rec.get("transformation_history", []) if rec else []

    def get_summary_stats(self) -> Dict[str, Any]:
        """Returns statistics on verified vs unverified items and avg confidence."""
        if not self.records:
            return {"total_records": 0, "avg_confidence": 0.0, "status_breakdown": {}}

        total = len(self.records)
        avg_conf = sum(r.get("confidence_score", 0.8) for r in self.records.values()) / total
        statuses: Dict[str, int] = {}
        for r in self.records.values():
            s = r.get("verification_status", "unverified")
            statuses[s] = statuses.get(s, 0) + 1

        return {
            "total_records": total,
            "avg_confidence": round(avg_conf, 3),
            "status_breakdown": statuses
        }


# Module singleton
source_provenance = SourceProvenanceTracker()
