"""
Capability 40: Git Intelligence
Provides repository status inspection, diff viewing, commit history,
branch tracking, and checkpointing for J.A.R.V.I.S.
"""

import os
import pathlib
import subprocess
import time
from typing import Dict, Any, List, Optional, Tuple


class GitIntelligence:
    """Interfaces with local Git repository to extract telemetry and manage checkpoints."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()

    def _run_git(self, args: List[str], cwd: Optional[pathlib.Path] = None) -> Tuple[int, str, str]:
        work_dir = cwd or self.root_dir
        cmd = ["git"] + args
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=15
            )
            return proc.returncode, proc.stdout, proc.stderr
        except FileNotFoundError:
            return -1, "", "git executable not found in PATH."
        except Exception as e:
            return -1, "", str(e)

    def is_git_repo(self) -> bool:
        """Checks if current directory is inside a Git repository."""
        ret, stdout, _ = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return ret == 0 and "true" in stdout.lower()

    def get_status(self) -> Dict[str, Any]:
        """
        Returns structured git status (staged, unstaged, untracked).
        """
        if not self.is_git_repo():
            return {
                "is_repo": False,
                "clean": True,
                "staged": [],
                "unstaged": [],
                "untracked": []
            }

        ret, stdout, stderr = self._run_git(["status", "--porcelain"])
        if ret != 0:
            return {"is_repo": True, "error": stderr, "clean": True}

        staged = []
        unstaged = []
        untracked = []

        for line in stdout.splitlines():
            if len(line) < 3:
                continue
            x = line[0]
            y = line[1]
            file_path = line[3:].strip()

            if x == "?" and y == "?":
                untracked.append(file_path)
            else:
                if x in ("M", "A", "D", "R", "C"):
                    staged.append({"file": file_path, "status": x})
                if y in ("M", "D"):
                    unstaged.append({"file": file_path, "status": y})

        clean = (len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0)

        # Get current branch
        _, branch_out, _ = self._run_git(["branch", "--show-current"])
        current_branch = branch_out.strip() or "HEAD"

        return {
            "is_repo": True,
            "branch": current_branch,
            "clean": clean,
            "staged_count": len(staged),
            "unstaged_count": len(unstaged),
            "untracked_count": len(untracked),
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked
        }

    def get_diff(self, cached: bool = False, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns unified git diff.
        """
        args = ["diff"]
        if cached:
            args.append("--cached")
        if file_path:
            args.extend(["--", file_path])

        ret, stdout, stderr = self._run_git(args)
        return {
            "success": ret == 0,
            "cached": cached,
            "file": file_path,
            "diff": stdout,
            "error": stderr if ret != 0 else None
        }

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Returns recent commit history with hash, author, date, and subject.
        """
        if not self.is_git_repo():
            return []

        # Format: %H|%an|%ad|%s
        args = ["log", f"-n{limit}", "--pretty=format:%H|%an|%ad|%s", "--date=short"]
        ret, stdout, _ = self._run_git(args)
        if ret != 0:
            return []

        commits = []
        for line in stdout.splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "short_hash": parts[0][:8],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3]
                })

        return commits

    def create_checkpoint(self, message: str, stage_all: bool = True) -> Dict[str, Any]:
        """
        Stages changes and creates a local commit checkpoint.
        """
        if not self.is_git_repo():
            return {"success": False, "error": "Not a git repository."}

        if stage_all:
            ret, _, err = self._run_git(["add", "-A"])
            if ret != 0:
                return {"success": False, "error": f"Failed to stage files: {err}"}

        full_msg = f"[checkpoint] {message}"
        ret, stdout, stderr = self._run_git(["commit", "-m", full_msg])
        if ret != 0:
            # Check if there was nothing to commit
            if "nothing to commit" in stdout or "nothing to commit" in stderr:
                return {"success": True, "message": "Working tree clean, no new changes to checkpoint.", "commit": None}
            return {"success": False, "error": stderr or stdout}

        # Retrieve commit hash
        _, hash_out, _ = self._run_git(["rev-parse", "HEAD"])
        return {
            "success": True,
            "commit": hash_out.strip()[:8],
            "message": full_msg
        }
