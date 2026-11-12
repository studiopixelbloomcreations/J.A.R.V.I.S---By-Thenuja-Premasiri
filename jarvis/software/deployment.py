"""
Capability 41: Deployment Assistant
Performs pre-flight readiness checks, environment verification,
and deployment gating for J.A.R.V.I.S.
"""

import os
import socket
import pathlib
import sys
from typing import Dict, Any, List, Optional
from .coding_agent import AutonomousCodingAgent
from .test_runner import TestRunner
from .git_intelligence import GitIntelligence


class DeploymentAssistant:
    """Evaluates workspace health, tests, and configurations to gate deployments."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()
        self.coding_agent = AutonomousCodingAgent(str(self.root_dir))
        self.test_runner = TestRunner(str(self.root_dir))
        self.git = GitIntelligence(str(self.root_dir))

    def check_port_open(self, host: str = "127.0.0.1", port: int = 4700) -> bool:
        """Checks if a network port is currently open and accepting connections."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            res = s.connect_ex((host, port))
            return res == 0
        except Exception:
            return False
        finally:
            s.close()

    def run_preflight(
        self,
        target_port: int = 4700,
        run_full_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Executes complete pre-flight checklist for deployment.
        """
        checks: List[Dict[str, Any]] = []
        is_blocked = False
        has_warnings = False

        # 1. Syntax Validation across repository
        syntax_errors = []
        for py_path in self.root_dir.rglob("*.py"):
            if any(p in py_path.parts for p in [".git", "__pycache__", "node_modules", ".venv", "venv"]):
                continue
            valid, err = self.coding_agent.validate_syntax(py_path.read_text(encoding="utf-8", errors="ignore"))
            if not valid:
                syntax_errors.append({"file": str(py_path.relative_to(self.root_dir)), "error": err})

        if syntax_errors:
            checks.append({
                "check": "Syntax Integrity",
                "status": "FAIL",
                "severity": "BLOCKER",
                "message": f"{len(syntax_errors)} files failed Python AST syntax validation.",
                "details": syntax_errors
            })
            is_blocked = True
        else:
            checks.append({
                "check": "Syntax Integrity",
                "status": "PASS",
                "severity": "INFO",
                "message": "All Python source files passed AST syntax compilation."
            })

        # 2. Configuration and Storage Check
        core_dirs = ["storage", "notes", "viewer"]
        missing_dirs = [d for d in core_dirs if not (self.root_dir / d).exists()]
        if missing_dirs:
            checks.append({
                "check": "Workspace Directory Structure",
                "status": "WARN",
                "severity": "WARNING",
                "message": f"Expected project directories missing: {', '.join(missing_dirs)}"
            })
            has_warnings = True
        else:
            checks.append({
                "check": "Workspace Directory Structure",
                "status": "PASS",
                "severity": "INFO",
                "message": "All required project directories exist."
            })

        # 3. Git Status Check
        git_status = self.git.get_status()
        if git_status.get("is_repo"):
            if not git_status.get("clean"):
                checks.append({
                    "check": "Git Working Tree Cleanliness",
                    "status": "WARN",
                    "severity": "WARNING",
                    "message": f"Working tree has uncommitted modifications ({git_status.get('unstaged_count')} unstaged, {git_status.get('untracked_count')} untracked)."
                })
                has_warnings = True
            else:
                checks.append({
                    "check": "Git Working Tree Cleanliness",
                    "status": "PASS",
                    "severity": "INFO",
                    "message": f"Git working tree is completely clean on branch '{git_status.get('branch')}'."
                })

        # 4. Unit Test Suite Execution
        if run_full_tests:
            test_res = self.test_runner.run_tests(timeout=30)
            if not test_res.get("success"):
                checks.append({
                    "check": "Unit Test Suite",
                    "status": "FAIL",
                    "severity": "BLOCKER",
                    "message": f"Test suite failed ({test_res.get('failed')} failures, {test_res.get('errors')} errors out of {test_res.get('tests_run')} tests).",
                    "details": test_res.get("failure_details")
                })
                is_blocked = True
            else:
                checks.append({
                    "check": "Unit Test Suite",
                    "status": "PASS",
                    "severity": "INFO",
                    "message": f"All {test_res.get('tests_run')} automated tests passed cleanly in {test_res.get('duration_seconds')}s."
                })

        # 5. Port Telemetry
        port_in_use = self.check_port_open("127.0.0.1", target_port)
        checks.append({
            "check": f"Target Server Port ({target_port})",
            "status": "INFO",
            "severity": "INFO",
            "message": f"Port {target_port} is {'already in use / live' if port_in_use else 'available for binding'}."
        })

        # Overall Status
        if is_blocked:
            overall_verdict = "BLOCKED"
        elif has_warnings:
            overall_verdict = "WARNING"
        else:
            overall_verdict = "READY"

        return {
            "verdict": overall_verdict,
            "ready_to_deploy": overall_verdict in ("READY", "WARNING"),
            "total_checks": len(checks),
            "checks": checks
        }
