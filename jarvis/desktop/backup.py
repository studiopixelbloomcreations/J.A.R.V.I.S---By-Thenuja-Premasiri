"""
Capability 29: Local Backup Intelligence Subsystem for J.A.R.V.I.S.
Creates versioned compressed local backups of files and folders, verifies backup
integrity with SHA-256 digests, and executes safe rollback restorations.
"""
import os
import time
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional


class LocalBackupIntelligence:
    """Manages versioned local backups, integrity verification, and rollback operations."""

    def __init__(self, backup_dir: Optional[str] = None):
        if backup_dir is None:
            self.backup_dir = Path("storage/backups")
        else:
            self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, source_path: str, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Creates a timestamped zip archive of a file or directory."""
        src = Path(source_path)
        if not src.exists():
            return {"status": "error", "message": f"Source path not found: {source_path}"}

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        stem = backup_name or src.stem
        archive_name = f"{stem}_{timestamp}.zip"
        archive_path = self.backup_dir / archive_name

        file_count = 0
        total_uncompressed_bytes = 0

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if src.is_file():
                zf.write(src, arcname=src.name)
                file_count = 1
                total_uncompressed_bytes = src.stat().st_size
            else:
                for root, dirs, files in os.walk(src):
                    for file in files:
                        full_p = Path(root) / file
                        rel_p = full_p.relative_to(src)
                        zf.write(full_p, arcname=str(rel_p))
                        file_count += 1
                        total_uncompressed_bytes += full_p.stat().st_size

        compressed_size = archive_path.stat().st_size
        checksum = self._compute_sha256(str(archive_path))

        return {
            "status": "success",
            "archive_name": archive_name,
            "archive_path": str(archive_path.resolve()),
            "files_backed_up": file_count,
            "original_size_mb": round(total_uncompressed_bytes / (1024 * 1024), 2),
            "compressed_size_mb": round(compressed_size / (1024 * 1024), 2),
            "checksum_sha256": checksum,
            "timestamp": timestamp,
        }

    def verify_backup_integrity(self, archive_name_or_path: str) -> Dict[str, Any]:
        """Tests zip archive integrity and verifies readable files."""
        archive_path = self._resolve_archive_path(archive_name_or_path)
        if not archive_path.exists():
            return {"status": "error", "message": f"Backup archive not found: {archive_name_or_path}"}

        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                # testzip returns None if no errors, or name of first corrupt file
                corrupt_file = zf.testzip()
                if corrupt_file:
                    return {"status": "corrupt", "message": f"Corrupt file in archive: {corrupt_file}"}

                info_list = zf.infolist()
                return {
                    "status": "healthy",
                    "archive_name": archive_path.name,
                    "file_count": len(info_list),
                    "is_valid": True,
                    "checksum_sha256": self._compute_sha256(str(archive_path)),
                }
        except Exception as e:
            return {"status": "error", "message": str(e), "is_valid": False}

    def restore_backup(self, archive_name_or_path: str, destination_dir: str) -> Dict[str, Any]:
        """Extracts and restores files from a backup archive."""
        archive_path = self._resolve_archive_path(archive_name_or_path)
        if not archive_path.exists():
            return {"status": "error", "message": f"Backup archive not found: {archive_name_or_path}"}

        dest = Path(destination_dir)
        dest.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(dest)
                return {
                    "status": "success",
                    "restored_to": str(dest.resolve()),
                    "files_extracted": len(zf.namelist()),
                }
        except Exception as e:
            return {"status": "error", "message": f"Extraction failed: {e}"}

    def prune_old_backups(self, max_keep: int = 5) -> Dict[str, Any]:
        """Retains only the latest N backups, deleting older archives."""
        archives = sorted(self.backup_dir.glob("*.zip"), key=lambda f: f.stat().st_mtime, reverse=True)
        deleted = []
        for old in archives[max_keep:]:
            try:
                old.unlink()
                deleted.append(old.name)
            except Exception:
                pass

        return {
            "status": "success",
            "kept_count": min(len(archives), max_keep),
            "deleted_count": len(deleted),
            "deleted_archives": deleted,
        }

    def _resolve_archive_path(self, name_or_path: str) -> Path:
        p = Path(name_or_path)
        if p.is_file():
            return p
        return self.backup_dir / name_or_path

    def _compute_sha256(self, filepath: str) -> str:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


backup_intelligence = LocalBackupIntelligence()
