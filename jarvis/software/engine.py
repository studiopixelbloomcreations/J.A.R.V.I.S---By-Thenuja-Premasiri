"""
Unified Software Engineering Nexus for J.A.R.V.I.S.
Coordinating Capabilities 31-45:
31. Autonomous Coding Agent
32. Repository Understanding
33. Automated Debugging
34. Test Generation
35. Test Execution
36. Code Review
37. Architecture Analysis
38. Dependency Analysis
39. Documentation Generation
40. Git Intelligence
41. Deployment Assistant
42. Build Diagnostics
43. Database Intelligence
44. API Testing
45. Refactoring Agent
"""

import pathlib
from typing import Dict, Any, Optional, Union

from .coding_agent import AutonomousCodingAgent
from .repo_analyzer import RepoAnalyzer
from .debugger import AutomatedDebugger
from .test_gen import TestGenerator
from .test_runner import TestRunner
from .code_reviewer import CodeReviewer
from .architecture import ArchitectureAnalyzer
from .dependencies import DependencyAnalyzer
from .doc_gen import DocumentationGenerator
from .git_intelligence import GitIntelligence
from .deployment import DeploymentAssistant
from .build_diagnostics import BuildDiagnostics
from .db_intelligence import DatabaseIntelligence
from .api_tester import APITester
from .refactoring import RefactoringAgent


class SoftwareEngineeringNexus:
    """Master orchestrator for all 15 software engineering capabilities."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = pathlib.Path(root_dir) if root_dir else pathlib.Path.cwd()
        
        # Capability Engines
        self.coding = AutonomousCodingAgent(str(self.root_dir))
        self.repo = RepoAnalyzer(str(self.root_dir))
        self.debugger = AutomatedDebugger(str(self.root_dir))
        self.test_gen = TestGenerator(str(self.root_dir))
        self.test_runner = TestRunner(str(self.root_dir))
        self.reviewer = CodeReviewer()
        self.architecture = ArchitectureAnalyzer(str(self.root_dir))
        self.deps = DependencyAnalyzer(str(self.root_dir))
        self.docs = DocumentationGenerator(str(self.root_dir))
        self.git = GitIntelligence(str(self.root_dir))
        self.deployment = DeploymentAssistant(str(self.root_dir))
        self.build = BuildDiagnostics(str(self.root_dir))
        self.database = DatabaseIntelligence()
        self.api = APITester()
        self.refactoring = RefactoringAgent()

        self.capability_map = {
            31: ("Autonomous Coding Agent", self._cap_31),
            32: ("Repository Understanding", self._cap_32),
            33: ("Automated Debugging", self._cap_33),
            34: ("Test Generation", self._cap_34),
            35: ("Test Execution", self._cap_35),
            36: ("Code Review", self._cap_36),
            37: ("Architecture Analysis", self._cap_37),
            38: ("Dependency Analysis", self._cap_38),
            39: ("Documentation Generation", self._cap_39),
            40: ("Git Intelligence", self._cap_40),
            41: ("Deployment Assistant", self._cap_41),
            42: ("Build Diagnostics", self._cap_42),
            43: ("Database Intelligence", self._cap_43),
            44: ("API Testing", self._cap_44),
            45: ("Refactoring Agent", self._cap_45),
        }

    def execute_capability(self, cap_id: Union[int, str], **kwargs) -> Dict[str, Any]:
        """
        Dispatches request to the appropriate software engineering capability (31-45).
        """
        if isinstance(cap_id, str):
            try:
                cap_num = int(cap_id)
            except ValueError:
                # Name matching
                cap_num = self._lookup_by_name(cap_id)
        else:
            cap_num = cap_id

        if cap_num not in self.capability_map:
            return {
                "success": False,
                "error": f"Capability {cap_id} is not handled by SoftwareEngineeringNexus (owns 31-45)."
            }

        name, handler = self.capability_map[cap_num]
        res = handler(**kwargs)
        res["capability_number"] = cap_num
        res["capability_name"] = name
        return res

    def _lookup_by_name(self, name_query: str) -> int:
        q = name_query.lower().strip()
        for num, (name, _) in self.capability_map.items():
            if q in name.lower():
                return num
        return -1

    # ── Handlers for Capabilities 31-45 ────────────────────────────────

    def _cap_31(self, **kw):
        """31: Autonomous Coding Agent"""
        action = kw.get("action", "validate_syntax")
        code = kw.get("code", "")
        if action == "validate_syntax":
            valid, err = self.coding.validate_syntax(code)
            return {"valid": valid, "error": err}
        elif action == "generate_patch":
            patch = self.coding.generate_patch(kw.get("original", ""), kw.get("modified", ""), kw.get("filename", "file.py"))
            return {"patch": patch}
        elif action == "create_function":
            return self.coding.create_function(kw.get("name", "func"), kw.get("args", []), kw.get("body", "pass"), kw.get("docstring"))
        elif action == "create_class":
            return self.coding.create_class(kw.get("name", "Cls"), kw.get("methods", []), kw.get("bases"), kw.get("docstring"))
        elif action == "write_code":
            return self.coding.safe_write_code(kw.get("path", ""), kw.get("content", ""))
        return {"error": f"Unknown action: {action}"}

    def _cap_32(self, **kw):
        """32: Repository Understanding"""
        action = kw.get("action", "scan")
        target_dir = kw.get("target_dir")
        if action == "scan":
            return self.repo.scan_repository(target_dir)
        elif action == "symbols":
            return self.repo.index_symbols(target_dir)
        elif action == "find_symbol":
            return {"results": self.repo.find_symbol(kw.get("symbol", ""), target_dir)}
        return {"error": f"Unknown action: {action}"}

    def _cap_33(self, **kw):
        """33: Automated Debugging"""
        tb = kw.get("traceback", "")
        return self.debugger.analyze_traceback(tb)

    def _cap_34(self, **kw):
        """34: Test Generation"""
        if "code" in kw:
            return self.test_gen.generate_tests_for_code(kw["code"], kw.get("module_name", "sample_module"))
        elif "file" in kw:
            return self.test_gen.generate_tests_for_file(kw["file"])
        return {"error": "Provide 'code' or 'file' for test generation"}

    def _cap_35(self, **kw):
        """35: Test Execution"""
        if "code" in kw:
            return self.test_runner.run_test_string(kw["code"])
        if kw.get("quick") or not kw.get("path"):
            return {"status": "ready", "test_runner": "unittest", "root_dir": str(self.root_dir)}
        return self.test_runner.run_tests(kw.get("path"), timeout=kw.get("timeout", 60))

    def _cap_36(self, **kw):
        """36: Code Review"""
        if "code" in kw:
            return self.reviewer.review_code(kw["code"], kw.get("filename", "snippet.py"))
        elif "file" in kw:
            return self.reviewer.review_file(kw["file"])
        return {"error": "Provide 'code' or 'file' for review"}

    def _cap_37(self, **kw):
        """37: Architecture Analysis"""
        action = kw.get("action", "analyze")
        target_dir = kw.get("target_dir")
        if action == "analyze":
            return self.architecture.analyze_dependencies(target_dir)
        elif action == "circular":
            cycles = self.architecture.detect_circular_imports(target_dir)
            return {"circular_cycles": cycles, "count": len(cycles)}
        elif action == "metrics":
            return self.architecture.calculate_metrics(target_dir)
        elif action == "violations":
            return {"violations": self.architecture.check_layer_violations(kw.get("rules"), target_dir)}
        return {"error": f"Unknown action: {action}"}

    def _cap_38(self, **kw):
        """38: Dependency Analysis"""
        req_path = kw.get("req_path")
        return self.deps.audit_dependencies(req_path)

    def _cap_39(self, **kw):
        """39: Documentation Generation"""
        if "file" in kw:
            return self.docs.generate_module_docs(kw["file"])
        elif kw.get("action") == "audit":
            return self.docs.audit_coverage(kw.get("target_dir"))
        return {"error": "Provide 'file' or action='audit'"}

    def _cap_40(self, **kw):
        """40: Git Intelligence"""
        action = kw.get("action", "status")
        if action == "status":
            return self.git.get_status()
        elif action == "diff":
            return self.git.get_diff(cached=kw.get("cached", False), file_path=kw.get("file"))
        elif action == "history":
            return {"history": self.git.get_history(limit=kw.get("limit", 10))}
        elif action == "checkpoint":
            return self.git.create_checkpoint(kw.get("message", "automated-checkpoint"))
        return {"error": f"Unknown action: {action}"}

    def _cap_41(self, **kw):
        """41: Deployment Assistant"""
        return self.deployment.run_preflight(
            target_port=kw.get("port", 4700),
            run_full_tests=kw.get("run_tests", False)
        )

    def _cap_42(self, **kw):
        """42: Build Diagnostics"""
        action = kw.get("action", "report")
        if action == "compile":
            return self.build.compile_all(kw.get("target_dir"))
        elif action == "structure":
            return self.build.verify_project_structure()
        return self.build.generate_build_report()

    def _cap_43(self, **kw):
        """43: Database Intelligence"""
        action = kw.get("action", "schema")
        db_path = kw.get("db_path")
        if action == "schema":
            return self.database.inspect_schema(db_path)
        elif action == "query":
            return self.database.execute_safe_query(kw.get("query", ""), db_path, kw.get("max_rows", 100))
        elif action == "explain":
            return self.database.explain_query(kw.get("query", ""), db_path)
        return {"error": f"Unknown action: {action}"}

    def _cap_44(self, **kw):
        """44: API Testing"""
        action = kw.get("action", "test")
        endpoint = kw.get("endpoint", "")
        if not endpoint and action == "test":
            return {"status": "ready", "message": "API tester ready", "base_url": self.api.base_url}
        if action == "test":
            return self.api.test_endpoint(
                endpoint,
                method=kw.get("method", "GET"),
                payload=kw.get("payload"),
                headers=kw.get("headers"),
                timeout=kw.get("timeout", 5.0)
            )
        elif action == "benchmark":
            return self.api.benchmark_endpoint(endpoint, iterations=kw.get("iterations", 5))
        return {"error": f"Unknown action: {action}"}

    def _cap_45(self, **kw):
        """45: Refactoring Agent"""
        action = kw.get("action", "rename")
        code = kw.get("code", "")
        if action == "rename":
            return self.refactoring.rename_symbol(code, kw.get("old_name", ""), kw.get("new_name", ""))
        elif action == "extract_constant":
            return self.refactoring.extract_constant(code, kw.get("literal", ""), kw.get("constant_name", "CONST_VAL"))
        elif action == "remove_unused_imports":
            return self.refactoring.remove_unused_imports(code)
        return {"error": f"Unknown action: {action}"}


# Global nexus instance
nexus = SoftwareEngineeringNexus()
