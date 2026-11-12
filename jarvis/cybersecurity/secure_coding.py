"""
Capability 57: Secure Coding Analysis (Regex & AST Security Flaw Detection)
Static Application Security Testing (SAST) scanner for Python source code using Abstract Syntax Trees (AST)
and regex rules. Detects SQL injection, command injection, hardcoded credentials, insecure deserialization,
weak cryptography, insecure temp files, and disabled SSL verification.
"""

import ast
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class CodeFlawFinding:
    rule_id: str
    cwe_id: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    line_number: int
    code_snippet: str
    description: str
    remediation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "cwe_id": self.cwe_id,
            "title": self.title,
            "severity": self.severity,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "description": self.description,
            "remediation": self.remediation,
        }


class ASTSecurityVisitor(ast.NodeVisitor):
    """AST visitor traversing Python code to flag dangerous AST nodes."""

    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.findings: List[CodeFlawFinding] = []

    def get_line_snippet(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.source_lines):
            return self.source_lines[lineno - 1].strip()
        return ""

    def visit_Call(self, node: ast.Call):
        # 1. Command Injection: subprocess with shell=True
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        if func_name in ["call", "check_call", "check_output", "Popen", "run"]:
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append(
                        CodeFlawFinding(
                            rule_id="SEC-CODE-CMD-INJ",
                            cwe_id="CWE-78",
                            title="Command Injection via Subprocess with shell=True",
                            severity="CRITICAL",
                            line_number=node.lineno,
                            code_snippet=self.get_line_snippet(node.lineno),
                            description="Executing commands with shell=True invites arbitrary command injection if input is untrusted.",
                            remediation="Pass command arguments as a list and remove shell=True: subprocess.run(['cmd', arg]).",
                        )
                    )

        # 2. Command Injection: os.system or os.popen
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "os" and node.func.attr in ["system", "popen"]:
                self.findings.append(
                    CodeFlawFinding(
                        rule_id="SEC-CODE-OS-SYSTEM",
                        cwe_id="CWE-78",
                        title=f"Unsafe Process Execution via os.{node.func.attr}",
                        severity="HIGH",
                        line_number=node.lineno,
                        code_snippet=self.get_line_snippet(node.lineno),
                        description=f"os.{node.func.attr} executes commands in a shell and is vulnerable to injection.",
                        remediation="Use subprocess.run([...], shell=False) with parameterized arguments.",
                    )
                )

        # 3. Insecure Deserialization: pickle.loads / pickle.load
        if func_name in ["loads", "load"]:
            is_pickle = False
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id in ["pickle", "_pickle", "cPickle"]:
                    is_pickle = True
            if is_pickle:
                self.findings.append(
                    CodeFlawFinding(
                        rule_id="SEC-CODE-PICKLE",
                        cwe_id="CWE-502",
                        title="Insecure Deserialization via Python pickle",
                        severity="CRITICAL",
                        line_number=node.lineno,
                        code_snippet=self.get_line_snippet(node.lineno),
                        description="Unpickling untrusted data allows arbitrary remote code execution via __reduce__.",
                        remediation="Use secure serialization formats like JSON, Protocol Buffers, or safe YAML loaders.",
                    )
                )

        # 4. Weak Cryptography: hashlib.md5 or hashlib.sha1
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "hashlib" and node.func.attr in ["md5", "sha1"]:
                # Check if used_for_security=False is set
                is_explicitly_safe = any(
                    kw.arg == "used_for_security" and isinstance(kw.value, ast.Constant) and kw.value.value is False
                    for kw in node.keywords
                )
                if not is_explicitly_safe:
                    self.findings.append(
                        CodeFlawFinding(
                            rule_id="SEC-CODE-WEAK-HASH",
                            cwe_id="CWE-327",
                            title=f"Use of Cryptographically Broken Hash Algorithm ({node.func.attr.upper()})",
                            severity="MEDIUM",
                            line_number=node.lineno,
                            code_snippet=self.get_line_snippet(node.lineno),
                            description=f"{node.func.attr.upper()} is collision-vulnerable and must not be used for security-critical contexts.",
                            remediation="Upgrade to SHA-256, SHA-3, or BLAKE2: hashlib.sha256().",
                        )
                    )

        # 5. Insecure Temp Files: tempfile.mktemp
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "tempfile" and node.func.attr == "mktemp":
                self.findings.append(
                    CodeFlawFinding(
                        rule_id="SEC-CODE-MKTEMP",
                        cwe_id="CWE-377",
                        title="Insecure Temporary File Creation via tempfile.mktemp",
                        severity="HIGH",
                        line_number=node.lineno,
                        code_snippet=self.get_line_snippet(node.lineno),
                        description="mktemp creates a race condition vulnerability (TOCTOU).",
                        remediation="Use tempfile.NamedTemporaryFile() or tempfile.mkstemp().",
                    )
                )

        # 6. Disabled SSL Verification: requests.get(..., verify=False)
        for kw in node.keywords:
            if kw.arg == "verify" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                self.findings.append(
                    CodeFlawFinding(
                        rule_id="SEC-CODE-SSL-VERIFY",
                        cwe_id="CWE-295",
                        title="Disabled TLS Certificate Verification (verify=False)",
                        severity="HIGH",
                        line_number=node.lineno,
                        code_snippet=self.get_line_snippet(node.lineno),
                        description="Disabling TLS verification exposes HTTP communications to Man-in-the-Middle (MitM) attacks.",
                        remediation="Enable certificate verification by setting verify=True or passing a valid CA bundle path.",
                    )
                )

        # 7. SQL Injection via execute with formatted query
        if func_name == "execute" and node.args:
            first_arg = node.args[0]
            # Checks for % or .format() or f-string
            is_interpolated = False
            if isinstance(first_arg, ast.JoinedStr):  # f-string
                is_interpolated = True
            elif isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, (ast.Mod, ast.Add)):  # % or +
                is_interpolated = True
            elif isinstance(first_arg, ast.Call) and isinstance(first_arg.func, ast.Attribute) and first_arg.func.attr == "format":
                is_interpolated = True

            if is_interpolated:
                self.findings.append(
                    CodeFlawFinding(
                        rule_id="SEC-CODE-SQLI",
                        cwe_id="CWE-89",
                        title="Potential SQL Injection via Dynamic Query String Formatting",
                        severity="CRITICAL",
                        line_number=node.lineno,
                        code_snippet=self.get_line_snippet(node.lineno),
                        description="Constructing SQL queries using string formatting or concatenation exposes database to SQL injection.",
                        remediation="Use parameterized queries with placeholder markers: cursor.execute('SELECT * FROM users WHERE id = %s', (uid,)).",
                    )
                )

        self.generic_visit(node)


class SecureCodingAnalyzer:
    """Performs Static Application Security Testing (SAST) on source files."""

    REGEX_SECRETS = [
        (r"(?i)(AKIA[0-9A-Z]{16})", "AWS Access Key ID", "CRITICAL", "CWE-798"),
        (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "Hardcoded Private Key", "CRITICAL", "CWE-798"),
        (r"(?i)(api[_-]?key|secret[_-]?token|auth[_-]?token)\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]", "Hardcoded API Key/Token", "HIGH", "CWE-798"),
        (r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{4,}['\"]", "Hardcoded Plaintext Password", "HIGH", "CWE-259"),
    ]

    def analyze_source_code(self, source_code: str, filename: Optional[str] = None) -> List[CodeFlawFinding]:
        """Runs AST and regex-based SAST on Python code string."""
        findings: List[CodeFlawFinding] = []
        lines = source_code.splitlines()

        # 1. Regex scanning for hardcoded secrets
        for idx, line in enumerate(lines, start=1):
            for pat, title, sev, cwe in self.REGEX_SECRETS:
                if re.search(pat, line):
                    findings.append(
                        CodeFlawFinding(
                            rule_id=f"SEC-CODE-SECRET-{cwe}",
                            cwe_id=cwe,
                            title=f"Hardcoded Credential Detected ({title})",
                            severity=sev,
                            line_number=idx,
                            code_snippet=line.strip()[:80],
                            description=f"Identified credential pattern ({title}) committed in source code.",
                            remediation="Store secrets in environment variables or a dedicated secrets manager.",
                        )
                    )
                    break

        # 2. AST parsing for structural security flaws
        try:
            tree = ast.parse(source_code)
            visitor = ASTSecurityVisitor(lines)
            visitor.visit(tree)
            findings.extend(visitor.findings)
        except SyntaxError:
            pass

        return findings

    def analyze_file(self, file_path: str) -> List[CodeFlawFinding]:
        """Analyzes a source file from disk."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return self.analyze_source_code(content, filename=file_path)
