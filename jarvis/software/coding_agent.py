"""
Capability 31: Autonomous Coding Agent
Provides code patch generation, AST-verified code modification, function/class creation,
and syntax verification for J.A.R.V.I.S.
"""

import ast
import difflib
import os
import pathlib
from typing import Dict, Any, Tuple, Optional, List


class AutonomousCodingAgent:
    """Autonomous Coding Agent for safe code manipulation and generation."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()

    def validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validates Python code syntax using ast.parse.
        Returns (is_valid, error_message).
        """
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"

    def generate_patch(self, original_code: str, modified_code: str, filename: str = "module.py") -> str:
        """
        Generates a unified diff patch between original and modified code.
        """
        orig_lines = original_code.splitlines(keepends=True)
        mod_lines = modified_code.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm="\n"
        )
        return "".join(diff)

    def apply_patch(self, original_code: str, patch_text: str) -> Tuple[bool, str, Optional[str]]:
        """
        Applies a unified diff patch to original_code string.
        Returns (success, new_code, error).
        """
        orig_lines = original_code.splitlines()
        patch_lines = patch_text.splitlines()
        
        # Simple hunk-based patch applier
        result_lines = list(orig_lines)
        hunk_pattern = None
        
        # We can also parse diff or apply line-by-line additions/deletions
        hunk_started = False
        new_lines = []
        i = 0
        
        # If patch is empty or identical
        if not patch_text.strip():
            return True, original_code, None

        # Check if patch looks like unified diff
        diff_lines = [l for l in patch_lines if not l.startswith("---") and not l.startswith("+++")]
        cur_orig_idx = 0
        
        try:
            # Reconstruct modified code by iterating through diff lines
            reconstructed = []
            for line in patch_lines:
                if line.startswith("---") or line.startswith("+++"):
                    continue
                if line.startswith("@@"):
                    hunk_started = True
                    continue
                if not hunk_started:
                    continue
                if line.startswith("-"):
                    # removed line
                    continue
                elif line.startswith("+"):
                    # added line
                    reconstructed.append(line[1:])
                elif line.startswith(" "):
                    # context line
                    reconstructed.append(line[1:])
                elif line == "":
                    reconstructed.append("")
            
            if reconstructed:
                candidate = "\n".join(reconstructed)
                valid, err = self.validate_syntax(candidate)
                if valid:
                    return True, candidate, None
                return False, original_code, f"Patched code failed syntax check: {err}"
            else:
                return False, original_code, "No diff hunks parsed."
        except Exception as e:
            return False, original_code, f"Failed applying patch: {str(e)}"

    def create_function(
        self,
        func_name: str,
        args: List[str],
        body: str,
        docstring: Optional[str] = None,
        return_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates and validates Python function code.
        """
        args_str = ", ".join(args)
        ret_annotation = f" -> {return_type}" if return_type else ""
        lines = [f"def {func_name}({args_str}){ret_annotation}:"]
        
        if docstring:
            lines.append(f'    """{docstring}"""')
        
        # Indent body
        body_lines = body.strip().splitlines()
        if not body_lines:
            lines.append("    pass")
        else:
            for bl in body_lines:
                lines.append(f"    {bl}")
        
        code = "\n".join(lines) + "\n"
        is_valid, err = self.validate_syntax(code)
        
        return {
            "name": func_name,
            "code": code,
            "valid": is_valid,
            "error": err
        }

    def create_class(
        self,
        class_name: str,
        methods: List[Dict[str, Any]],
        base_classes: Optional[List[str]] = None,
        docstring: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates and validates a complete Python class definition.
        """
        bases_str = f"({', '.join(base_classes)})" if base_classes else ""
        lines = [f"class {class_name}{bases_str}:"]
        
        if docstring:
            lines.append(f'    """{docstring}"""\n')
            
        if not methods:
            lines.append("    pass\n")
        else:
            for m in methods:
                m_name = m.get("name", "method")
                m_args = m.get("args", ["self"])
                m_body = m.get("body", "pass")
                m_doc = m.get("docstring")
                m_res = self.create_function(m_name, m_args, m_body, m_doc)
                
                for ml in m_res["code"].splitlines():
                    lines.append(f"    {ml}")
                lines.append("")
        
        code = "\n".join(lines).rstrip() + "\n"
        is_valid, err = self.validate_syntax(code)
        
        return {
            "name": class_name,
            "code": code,
            "valid": is_valid,
            "error": err
        }

    def safe_write_code(
        self,
        file_path: str,
        new_content: str,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Safely writes code to disk only if syntax validation passes.
        """
        target = pathlib.Path(file_path)
        if not target.is_absolute():
            target = self.root_dir / target

        # If it is python file, check syntax first
        if target.suffix == ".py":
            is_valid, err = self.validate_syntax(new_content)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Refusing to write invalid Python syntax: {err}",
                    "file": str(target)
                }

        backup_file = None
        if create_backup and target.exists():
            backup_file = target.with_suffix(target.suffix + ".bak")
            backup_file.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_content, encoding="utf-8")

        return {
            "success": True,
            "file": str(target),
            "bytes_written": len(new_content.encode("utf-8")),
            "backup_created": str(backup_file) if backup_file else None
        }
