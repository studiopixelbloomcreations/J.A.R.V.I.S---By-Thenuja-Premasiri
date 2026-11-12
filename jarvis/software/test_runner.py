"""
Capability 35: Test Execution
Executes unit tests, tracks test results, parses failures,
and generates structured metrics for J.A.R.V.I.S.
"""

import os
import re
import sys
import time
import subprocess
import tempfile
import pathlib
from typing import Dict, Any, List, Optional


class TestRunner:
    """Executes Python unit tests and parses results."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()

    def run_tests(
        self,
        test_path: Optional[str] = None,
        pattern: str = "test_*.py",
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Executes unittests via python -m unittest.
        """
        start_time = time.time()
        cmd = [sys.executable, "-m", "unittest"]

        if test_path:
            p = pathlib.Path(test_path)
            if not p.is_absolute():
                p = self.root_dir / p
            if p.is_file():
                cmd.extend(["discover", "-s", str(p.parent), "-p", p.name])
            else:
                cmd.extend(["discover", "-s", str(p), "-p", pattern])
        else:
            cmd.extend(["discover", "-s", str(self.root_dir / "tests"), "-p", pattern])

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            duration = round(time.time() - start_time, 3)
            parsed = self.parse_unittest_output(proc.stdout, proc.stderr, proc.returncode)
            parsed["duration_seconds"] = duration
            parsed["command"] = " ".join(cmd)
            return parsed
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "error": f"Test execution timed out after {timeout} seconds.",
                "duration_seconds": timeout,
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "error": str(e),
                "duration_seconds": 0,
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1
            }

    def run_test_string(self, test_code: str, timeout: int = 15) -> Dict[str, Any]:
        """
        Runs an ad-hoc unit test code string safely in a temporary file.
        """
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
            tf.write(test_code)
            temp_path = tf.name

        try:
            return self.run_tests(test_path=temp_path, timeout=timeout)
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def parse_unittest_output(self, stdout: str, stderr: str, returncode: int) -> Dict[str, Any]:
        """
        Parses standard unittest CLI output from stderr/stdout.
        Unittest prints dot/F/E stream and summaries to stderr.
        """
        combined = (stderr + "\n" + stdout).strip()

        # Match "Ran X tests in Ys"
        ran_match = re.search(r"Ran\s+(\d+)\s+tests?\s+in\s+([0-9.]+)s", combined)
        tests_run = int(ran_match.group(1)) if ran_match else 0
        reported_time = float(ran_match.group(2)) if ran_match else 0.0

        # Match "OK" or "FAILED (failures=X, errors=Y, skipped=Z)"
        failures = 0
        errors = 0
        skipped = 0

        fail_match = re.search(r"FAILED\s*\((.*?)\)", combined)
        if fail_match:
            detail = fail_match.group(1)
            f_m = re.search(r"failures=(\d+)", detail)
            if f_m:
                failures = int(f_m.group(1))
            e_m = re.search(r"errors=(\d+)", detail)
            if e_m:
                errors = int(e_m.group(1))
            s_m = re.search(r"skipped=(\d+)", detail)
            if s_m:
                skipped = int(s_m.group(1))
        elif "OK" in combined:
            failures = 0
            errors = 0

        passed = max(0, tests_run - failures - errors - skipped)

        # Extract individual failure summaries
        failure_details = []
        pattern = re.compile(r"={70}\n(?:FAIL|ERROR):\s+(.+?)\n-{70}\n(.*?)(?=\n={70}|\n-{70}|$)", re.DOTALL)
        for match in pattern.finditer(combined):
            test_id = match.group(1).strip()
            tb = match.group(2).strip()
            failure_details.append({
                "test": test_id,
                "traceback": tb
            })

        return {
            "success": returncode == 0 and failures == 0 and errors == 0,
            "returncode": returncode,
            "tests_run": tests_run,
            "passed": passed,
            "failed": failures,
            "errors": errors,
            "skipped": skipped,
            "failure_details": failure_details,
            "raw_output": combined
        }
