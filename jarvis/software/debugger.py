"""
Capability 33: Automated Debugging
Provides traceback parsing, exception root-cause classification,
and automated patch suggestions for J.A.R.V.I.S.
"""

import os
import re
import pathlib
import traceback
from typing import Dict, Any, List, Optional, Tuple


class AutomatedDebugger:
    """Parses stack traces, isolates bug locations, and formulates automated fixes."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()

    def parse_traceback(self, tb_text: str) -> Dict[str, Any]:
        """
        Parses a standard Python traceback into structured frames and exception details.
        """
        frames: List[Dict[str, Any]] = []
        lines = tb_text.strip().splitlines()
        
        # Regex for frame: File "...", line 123, in func_name
        frame_pattern = re.compile(r'File\s+"([^"]+)",\s+line\s+(\d+)(?:,\s+in\s+(.+))?')
        
        exc_type = "UnknownException"
        exc_message = ""
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            match = frame_pattern.search(line)
            if match:
                f_path = match.group(1)
                lineno = int(match.group(2))
                func_name = match.group(3) or "<module>"
                code_snippet = ""
                # Next line often contains the actual source code
                if i + 1 < len(lines) and not frame_pattern.search(lines[i + 1]) and not lines[i + 1].startswith("Traceback"):
                    code_snippet = lines[i + 1].strip()
                frames.append({
                    "file": f_path,
                    "line": lineno,
                    "function": func_name,
                    "code": code_snippet
                })
            i += 1

        # The last line typically contains ExceptionType: Exception message
        if lines:
            last_line = lines[-1].strip()
            if ":" in last_line:
                parts = last_line.split(":", 1)
                exc_type = parts[0].strip()
                exc_message = parts[1].strip()
            else:
                exc_type = last_line

        # Culprit frame is usually the last frame in the stack
        culprit = frames[-1] if frames else None

        return {
            "exception_type": exc_type,
            "exception_message": exc_message,
            "frames_count": len(frames),
            "frames": frames,
            "culprit_frame": culprit
        }

    def diagnose_error(
        self,
        exc_type: str,
        exc_message: str,
        code_context: str = ""
    ) -> Dict[str, Any]:
        """
        Classifies the error and suggests automated resolution strategies.
        """
        analysis = {
            "error_category": "Runtime Error",
            "probable_cause": "Unspecified runtime anomaly.",
            "recommended_fix": "Inspect variables in scope and apply safe checks.",
            "safe_pattern": ""
        }

        e_type = exc_type.lower()
        msg = exc_message.lower()

        if "attributeerror" in e_type:
            analysis["error_category"] = "Null or Missing Attribute"
            if "'nonetype' object has no attribute" in msg:
                analysis["probable_cause"] = "Attempted to access an attribute on a variable that evaluated to None."
                analysis["recommended_fix"] = "Add an explicit 'if target is not None:' guard or use safe navigation / fallback default."
                analysis["safe_pattern"] = "if var is not None:\n    res = var.attribute\nelse:\n    res = default"
            else:
                analysis["probable_cause"] = f"Object does not define the requested attribute ({exc_message})."
                analysis["recommended_fix"] = "Verify object type using isinstance() or hasattr() before accessing."
                analysis["safe_pattern"] = "if hasattr(obj, 'attr'):\n    res = getattr(obj, 'attr')"

        elif "keyerror" in e_type:
            analysis["error_category"] = "Missing Dictionary Key"
            analysis["probable_cause"] = f"Dictionary key {exc_message} was not found."
            analysis["recommended_fix"] = "Use dict.get(key, default) instead of direct indexing, or verify key in dictionary."
            analysis["safe_pattern"] = "val = my_dict.get(key, None)"

        elif "indexerror" in e_type:
            analysis["error_category"] = "List Index Out of Bounds"
            analysis["probable_cause"] = "Attempted to access a sequence index that does not exist."
            analysis["recommended_fix"] = "Check sequence length (len(seq) > index) before indexing."
            analysis["safe_pattern"] = "val = seq[idx] if idx < len(seq) else None"

        elif "typeerror" in e_type:
            analysis["error_category"] = "Type Mismatch / Signature Error"
            if "unsupported operand type" in msg:
                analysis["probable_cause"] = "Arithmetic or binary operation between incompatible types (e.g. str + int)."
                analysis["recommended_fix"] = "Cast operands to compatible types or validate types prior to operation."
            elif "missing" in msg and "argument" in msg:
                analysis["probable_cause"] = "Callable invoked with fewer arguments than expected."
                analysis["recommended_fix"] = "Check function signature and provide required arguments or default values."
            else:
                analysis["probable_cause"] = "Operation applied to object of inappropriate type."
                analysis["recommended_fix"] = "Assert or coerce types before operation."

        elif "modulenotfounderror" in e_type or "importerror" in e_type:
            analysis["error_category"] = "Missing Dependency or Circular Import"
            analysis["probable_cause"] = f"Required module or symbol could not be loaded: {exc_message}"
            analysis["recommended_fix"] = "Install package via pip or resolve circular dependency."
            analysis["safe_pattern"] = "pip install <package_name>"

        elif "zerodivisionerror" in e_type:
            analysis["error_category"] = "Division By Zero"
            analysis["probable_cause"] = "Denominator in division/modulo operation was zero."
            analysis["recommended_fix"] = "Check divisor != 0 before division."
            analysis["safe_pattern"] = "res = num / denom if denom != 0 else 0"

        elif "filenotfounderror" in e_type:
            analysis["error_category"] = "Missing File Path"
            analysis["probable_cause"] = f"File system path does not exist: {exc_message}"
            analysis["recommended_fix"] = "Verify file existence with path.exists() or create parent directories."
            analysis["safe_pattern"] = "if os.path.exists(path):\n    with open(path) as f: ..."

        return analysis

    def analyze_traceback(self, tb_text: str) -> Dict[str, Any]:
        """
        Complete end-to-end debugging pipeline for a traceback string.
        """
        parsed = self.parse_traceback(tb_text)
        diagnosis = self.diagnose_error(
            parsed["exception_type"],
            parsed["exception_message"],
            code_context=parsed["culprit_frame"]["code"] if parsed["culprit_frame"] else ""
        )
        return {
            "parsed_traceback": parsed,
            "diagnosis": diagnosis,
            "can_auto_fix": bool(diagnosis.get("safe_pattern")),
            "suggested_fix": diagnosis.get("recommended_fix"),
            "safe_snippet": diagnosis.get("safe_pattern")
        }
