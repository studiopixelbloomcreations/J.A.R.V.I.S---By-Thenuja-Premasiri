"""
Capability 50: File Integrity Monitoring (FIM)
Establishes cryptographic SHA-256 baselines across critical filesystem paths,
detects unauthorized file modifications, additions, and deletions,
and generates structured integrity violation alerts.
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class FileRecord:
    path: str
    sha256: str
    size_bytes: int
    mtime: float
    recorded_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "mtime": self.mtime,
            "recorded_at": self.recorded_at,
        }


@dataclass
class IntegrityAlert:
    change_type: str  # MODIFIED, ADDED, DELETED, METADATA_CHANGED
    severity: str     # CRITICAL, HIGH, MEDIUM, LOW
    path: str
    description: str
    baseline_hash: Optional[str] = None
    current_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_type": self.change_type,
            "severity": self.severity,
            "path": self.path,
            "description": self.description,
            "baseline_hash": self.baseline_hash,
            "current_hash": self.current_hash,
        }


@dataclass
class BaselineReport:
    name: str
    created_at: str
    file_count: int
    files: Dict[str, FileRecord] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "file_count": self.file_count,
            "files": {p: rec.to_dict() for p, rec in self.files.items()},
        }


class FileIntegrityMonitor:
    """Monitors and verifies file integrity against SHA-256 baseline snapshots."""

    def __init__(self):
        self.baselines: Dict[str, BaselineReport] = {}

    @staticmethod
    def calculate_file_hash(path: str) -> str:
        """Calculates SHA-256 digest of a given file."""
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def create_baseline(
        self,
        targets: List[str],
        baseline_name: str = "default",
        recursive: bool = True,
    ) -> BaselineReport:
        """Scans specified files and directories and records SHA-256 baselines."""
        records: Dict[str, FileRecord] = {}
        now_iso = datetime.now(timezone.utc).isoformat()

        def add_file(p: str):
            try:
                norm_p = os.path.normpath(os.path.abspath(p))
                stat = os.stat(norm_p)
                sha = self.calculate_file_hash(norm_p)
                records[norm_p] = FileRecord(
                    path=norm_p,
                    sha256=sha,
                    size_bytes=stat.st_size,
                    mtime=stat.st_mtime,
                    recorded_at=now_iso,
                )
            except Exception:
                pass

        for target in targets:
            norm_target = os.path.normpath(os.path.abspath(target))
            if os.path.isfile(norm_target):
                add_file(norm_target)
            elif os.path.isdir(norm_target):
                if recursive:
                    for root, _, files in os.walk(norm_target):
                        for f in files:
                            add_file(os.path.join(root, f))
                else:
                    for f in os.listdir(norm_target):
                        fp = os.path.join(norm_target, f)
                        if os.path.isfile(fp):
                            add_file(fp)

        report = BaselineReport(
            name=baseline_name,
            created_at=now_iso,
            file_count=len(records),
            files=records,
        )
        self.baselines[baseline_name] = report
        return report

    def save_baseline_to_file(self, baseline_name: str, out_json_path: str) -> None:
        """Exports baseline to JSON file on disk."""
        if baseline_name not in self.baselines:
            raise ValueError(f"Baseline {baseline_name} does not exist.")
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(self.baselines[baseline_name].to_dict(), f, indent=2)

    def load_baseline_from_file(self, in_json_path: str) -> BaselineReport:
        """Imports baseline from JSON file."""
        with open(in_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        files = {}
        for p, rec_data in data.get("files", {}).items():
            files[p] = FileRecord(
                path=rec_data["path"],
                sha256=rec_data["sha256"],
                size_bytes=rec_data["size_bytes"],
                mtime=rec_data["mtime"],
                recorded_at=rec_data["recorded_at"],
            )

        report = BaselineReport(
            name=data["name"],
            created_at=data["created_at"],
            file_count=len(files),
            files=files,
        )
        self.baselines[report.name] = report
        return report

    def verify_integrity(
        self,
        baseline_name: str = "default",
        check_directories: Optional[List[str]] = None,
    ) -> List[IntegrityAlert]:
        """
        Audits current filesystem state against the baseline.
        Detects MODIFIED, DELETED, and optionally ADDED files.
        """
        if baseline_name not in self.baselines:
            raise ValueError(f"Baseline {baseline_name} not found.")

        base = self.baselines[baseline_name]
        alerts: List[IntegrityAlert] = []

        # 1. Check all files in baseline for modifications or deletions
        for path, rec in base.files.items():
            if not os.path.exists(path):
                alerts.append(
                    IntegrityAlert(
                        change_type="DELETED",
                        severity="HIGH",
                        path=path,
                        description=f"Monitored file was deleted from disk: {path}",
                        baseline_hash=rec.sha256,
                        current_hash=None,
                    )
                )
                continue

            try:
                curr_hash = self.calculate_file_hash(path)
                if curr_hash != rec.sha256:
                    alerts.append(
                        IntegrityAlert(
                            change_type="MODIFIED",
                            severity="CRITICAL",
                            path=path,
                            description=f"Cryptographic hash mismatch. File contents have been modified: {path}",
                            baseline_hash=rec.sha256,
                            current_hash=curr_hash,
                        )
                    )
            except Exception as e:
                alerts.append(
                    IntegrityAlert(
                        change_type="ERROR",
                        severity="MEDIUM",
                        path=path,
                        description=f"Error reading file during integrity check: {e}",
                    )
                )

        # 2. Check for newly added files in monitored directories
        if check_directories:
            for d in check_directories:
                norm_d = os.path.normpath(os.path.abspath(d))
                if not os.path.isdir(norm_d):
                    continue
                for root, _, files in os.walk(norm_d):
                    for f in files:
                        fp = os.path.normpath(os.path.abspath(os.path.join(root, f)))
                        if fp not in base.files:
                            try:
                                h = self.calculate_file_hash(fp)
                            except Exception:
                                h = None
                            alerts.append(
                                IntegrityAlert(
                                    change_type="ADDED",
                                    severity="MEDIUM",
                                    path=fp,
                                    description=f"New unbaselined file detected in monitored directory: {fp}",
                                    baseline_hash=None,
                                    current_hash=h,
                                )
                            )

        return alerts
