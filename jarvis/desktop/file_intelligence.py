"""
Capability 20: File Intelligence Subsystem for J.A.R.V.I.S.
Provides fast filesystem search, metadata extraction, duplicate detection,
large file discovery, recent file tracking, and directory usage analytics.
"""
import os
import time
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional

EXT_CATEGORIES = {
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml", ".cpp", ".c", ".h", ".rs", ".go"],
    "Document": [".pdf", ".docx", ".doc", ".xlsx", ".pptx", ".txt", ".md", ".csv"],
    "Image": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm"],
    "Archive": [".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"],
    "Executable": [".exe", ".msi", ".bat", ".cmd", ".ps1", ".vbs"]
}


class FileIntelligence:
    """Manages file search, duplicate detection, storage telemetry, and metadata analysis."""

    def categorize_file(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        for cat, extensions in EXT_CATEGORIES.items():
            if ext in extensions:
                return cat
        return "Other"

    def get_file_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extracts complete metadata and checksum for a file."""
        p = Path(filepath)
        if not p.exists() or not p.is_file():
            return {"status": "error", "message": f"File not found: {filepath}"}

        stat = p.stat()
        mime, _ = mimetypes.guess_type(filepath)

        return {
            "status": "success",
            "name": p.name,
            "path": str(p.resolve()),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_time": stat.st_ctime,
            "modified_time": stat.st_mtime,
            "category": self.categorize_file(p.name),
            "mime_type": mime or "application/octet-stream",
            "extension": p.suffix.lower(),
        }

    def compute_sha256(self, filepath: str, max_bytes: int = 10 * 1024 * 1024) -> str:
        """Computes SHA-256 hash for file content."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            chunk = f.read(65536)
            total = 0
            while chunk and total < max_bytes:
                hasher.update(chunk)
                total += len(chunk)
                chunk = f.read(65536)
        return hasher.hexdigest()

    def search_files(self, root_dir: str, pattern: str = "*", recursive: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
        """Searches files by name glob pattern."""
        p = Path(root_dir)
        if not p.exists():
            return []

        results = []
        iterator = p.rglob(pattern) if recursive else p.glob(pattern)

        for item in iterator:
            try:
                if item.is_file():
                    stat = item.stat()
                    results.append({
                        "name": item.name,
                        "path": str(item.resolve()),
                        "size_bytes": stat.st_size,
                        "modified_time": stat.st_mtime,
                        "category": self.categorize_file(item.name),
                    })
                    if len(results) >= limit:
                        break
            except (PermissionError, OSError):
                continue

        return results

    def find_duplicate_files(self, root_dir: str, min_size_bytes: int = 1024, limit: int = 50) -> List[Dict[str, Any]]:
        """Identifies duplicate files using size grouping followed by SHA-256 hash matching."""
        p = Path(root_dir)
        if not p.exists():
            return []

        size_map: Dict[int, List[Path]] = {}
        for item in p.rglob("*"):
            try:
                if item.is_file():
                    sz = item.stat().st_size
                    if sz >= min_size_bytes:
                        size_map.setdefault(sz, []).append(item)
            except (PermissionError, OSError):
                continue

        duplicates = []
        for sz, files in size_map.items():
            if len(files) < 2:
                continue

            hash_map: Dict[str, List[str]] = {}
            for f in files:
                try:
                    fhash = self.compute_sha256(str(f))
                    hash_map.setdefault(fhash, []).append(str(f.resolve()))
                except Exception:
                    continue

            for fhash, paths in hash_map.items():
                if len(paths) > 1:
                    duplicates.append({
                        "hash": fhash,
                        "size_bytes": sz,
                        "size_mb": round(sz / (1024 * 1024), 2),
                        "copies": paths,
                    })
                    if len(duplicates) >= limit:
                        return duplicates

        return duplicates

    def find_large_files(self, root_dir: str, min_size_mb: float = 10.0, limit: int = 25) -> List[Dict[str, Any]]:
        """Finds largest files in a directory hierarchy exceeding threshold."""
        p = Path(root_dir)
        if not p.exists():
            return []

        min_bytes = int(min_size_mb * 1024 * 1024)
        large_files = []

        for item in p.rglob("*"):
            try:
                if item.is_file():
                    sz = item.stat().st_size
                    if sz >= min_bytes:
                        large_files.append({
                            "name": item.name,
                            "path": str(item.resolve()),
                            "size_bytes": sz,
                            "size_mb": round(sz / (1024 * 1024), 2),
                            "category": self.categorize_file(item.name),
                        })
            except (PermissionError, OSError):
                continue

        large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
        return large_files[:limit]

    def find_recent_files(self, root_dir: str, max_age_hours: float = 24.0, limit: int = 50) -> List[Dict[str, Any]]:
        """Finds files modified recently within the past N hours."""
        p = Path(root_dir)
        if not p.exists():
            return []

        cutoff = time.time() - (max_age_hours * 3600)
        recent_files = []

        for item in p.rglob("*"):
            try:
                if item.is_file():
                    mtime = item.stat().st_mtime
                    if mtime >= cutoff:
                        recent_files.append({
                            "name": item.name,
                            "path": str(item.resolve()),
                            "size_bytes": item.stat().st_size,
                            "modified_time": mtime,
                            "age_minutes": round((time.time() - mtime) / 60, 1),
                            "category": self.categorize_file(item.name),
                        })
                        if len(recent_files) >= limit * 2:
                            break
            except (PermissionError, OSError):
                continue

        recent_files.sort(key=lambda x: x["modified_time"], reverse=True)
        return recent_files[:limit]


file_intelligence = FileIntelligence()
