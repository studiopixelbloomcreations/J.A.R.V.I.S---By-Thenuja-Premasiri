"""
Capability 45: Refactoring Agent
Provides identifier renaming, constant extraction, unused import elimination,
and syntax-verified code transformations for J.A.R.V.I.S.
"""

import ast
import re
import tokenize
import io
from typing import Dict, Any, List, Tuple, Optional


class RefactoringAgent:
    """Performs AST-guided and token-level code transformations with syntax safety guarantees."""

    def __init__(self):
        pass

    def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """Verifies that code parses cleanly with ast.parse."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"SyntaxError at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def rename_symbol(
        self,
        source_code: str,
        old_name: str,
        new_name: str
    ) -> Dict[str, Any]:
        """
        Renames an identifier using Python tokenize to avoid renaming inside strings or comments.
        Verifies syntax before and after.
        """
        valid_orig, err = self.validate_code(source_code)
        if not valid_orig:
            return {"success": False, "error": f"Initial code has invalid syntax: {err}"}

        tokens = []
        replaced_count = 0
        b_stream = io.BytesIO(source_code.encode("utf-8")).readline

        try:
            for tok in tokenize.tokenize(b_stream):
                if tok.type == tokenize.NAME and tok.string == old_name:
                    tokens.append((tok.type, new_name, tok.start, tok.end, tok.line))
                    replaced_count += 1
                else:
                    tokens.append((tok.type, tok.string, tok.start, tok.end, tok.line))
            
            raw_untokenized = tokenize.untokenize(tokens)
            refactored_code = raw_untokenized.decode("utf-8") if isinstance(raw_untokenized, bytes) else raw_untokenized
        except Exception as e:
            return {"success": False, "error": f"Tokenization error: {str(e)}"}

        valid_new, err_new = self.validate_code(refactored_code)
        if not valid_new:
            return {
                "success": False,
                "error": f"Refactored code failed syntax validation: {err_new}",
                "code": source_code
            }

        return {
            "success": True,
            "replacements": replaced_count,
            "old_name": old_name,
            "new_name": new_name,
            "code": refactored_code
        }

    def extract_constant(
        self,
        source_code: str,
        literal_value: str,
        constant_name: str
    ) -> Dict[str, Any]:
        """
        Extracts repeated string/numeric literals into a defined uppercase constant.
        """
        valid_orig, err = self.validate_code(source_code)
        if not valid_orig:
            return {"success": False, "error": f"Initial code invalid: {err}"}

        # Check if constant name is uppercase
        c_name = constant_name.upper()
        
        # Replace occurrences of literal (quoted string or value)
        pattern = re.compile(rf'"{re.escape(literal_value)}"|\'{re.escape(literal_value)}\'')
        matches = list(pattern.finditer(source_code))
        if not matches:
            return {"success": False, "error": f"Literal '{literal_value}' not found in code."}

        # Substitute literal with constant name
        new_code = pattern.sub(c_name, source_code)
        
        # Prepend or insert constant definition at the top
        const_def = f'{c_name} = "{literal_value}"\n'
        new_code = const_def + new_code

        valid_new, err_new = self.validate_code(new_code)
        if not valid_new:
            return {"success": False, "error": f"Refactored code failed syntax validation: {err_new}"}

        return {
            "success": True,
            "constant_name": c_name,
            "extracted_count": len(matches),
            "code": new_code
        }

    def remove_unused_imports(self, source_code: str) -> Dict[str, Any]:
        """
        Finds imported names that are never referenced in the source AST and removes them.
        """
        try:
            tree = ast.parse(source_code)
        except Exception as e:
            return {"success": False, "error": f"AST parse error: {str(e)}"}

        # Collect imported names and their line numbers
        imported_symbols = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_symbols[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != "*":
                        name = alias.asname or alias.name
                        imported_symbols[name] = node.lineno

        # Collect referenced identifiers
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Store):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # E.g. os.path -> 'os' is accessed
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        unused = {sym: line for sym, line in imported_symbols.items() if sym not in used_names}

        # Filter out unused import lines
        lines = source_code.splitlines()
        new_lines = []
        removed_count = 0

        for idx, line in enumerate(lines, start=1):
            # Check if this line is an import of an unused symbol
            is_unused_line = False
            for u_sym, u_line in unused.items():
                if idx == u_line:
                    # If line has single import: "import u_sym" or "from x import u_sym"
                    if re.match(rf'^\s*(import\s+{u_sym}|from\s+\S+\s+import\s+{u_sym})\s*$', line):
                        is_unused_line = True
                        removed_count += 1
                        break
            if not is_unused_line:
                new_lines.append(line)

        cleaned_code = "\n".join(new_lines) + "\n"
        valid, err = self.validate_code(cleaned_code)
        if not valid:
            return {"success": False, "error": f"Failed syntax check after stripping imports: {err}"}

        return {
            "success": True,
            "unused_detected": list(unused.keys()),
            "lines_removed": removed_count,
            "code": cleaned_code
        }
