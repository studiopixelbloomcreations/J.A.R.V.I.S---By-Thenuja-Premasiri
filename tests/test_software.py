"""
J.A.R.V.I.S. Software Engineering Capabilities Comprehensive Test Suite
Validates Capabilities 31 through 45:
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
And Unified SoftwareEngineeringNexus Dispatcher.
"""

import os
import sys
import tempfile
import pathlib
import sqlite3
import unittest

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from jarvis.software import (
    AutonomousCodingAgent,
    RepoAnalyzer,
    AutomatedDebugger,
    TestGenerator,
    TestRunner,
    CodeReviewer,
    ArchitectureAnalyzer,
    DependencyAnalyzer,
    DocumentationGenerator,
    GitIntelligence,
    DeploymentAssistant,
    BuildDiagnostics,
    DatabaseIntelligence,
    APITester,
    RefactoringAgent,
    SoftwareEngineeringNexus,
    nexus
)


class TestSoftwareCapabilities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = pathlib.Path(WORKSPACE_ROOT)

    # ── Capability 31: Autonomous Coding Agent ────────────────────────
    def test_cap_31_autonomous_coding(self):
        agent = AutonomousCodingAgent(str(self.root_dir))
        
        # 1. Syntax Validation
        valid, err = agent.validate_syntax("def add(a, b):\n    return a + b\n")
        self.assertTrue(valid)
        self.assertIsNone(err)

        invalid, err = agent.validate_syntax("def broken(\n")
        self.assertFalse(invalid)
        self.assertIsNotNone(err)

        # 2. Function Generation
        func_res = agent.create_function(
            "calculate_tax",
            ["amount: float", "rate: float = 0.05"],
            "return amount * rate",
            docstring="Calculates standard tax.",
            return_type="float"
        )
        self.assertTrue(func_res["valid"])
        self.assertIn("def calculate_tax", func_res["code"])

        # 3. Class Generation
        cls_res = agent.create_class(
            "AccountManager",
            [
                {"name": "__init__", "args": ["self", "balance: float = 0.0"], "body": "self.balance = balance"},
                {"name": "get_balance", "args": ["self"], "body": "return self.balance"}
            ],
            docstring="Manages ledger accounts."
        )
        self.assertTrue(cls_res["valid"])
        self.assertIn("class AccountManager", cls_res["code"])

        # 4. Patch Generation
        orig = "def foo():\n    return 1\n"
        mod = "def foo():\n    return 2\n"
        patch = agent.generate_patch(orig, mod, filename="test.py")
        self.assertIn("-    return 1", patch)
        self.assertIn("+    return 2", patch)

        # 5. Patch Application
        ok, res_code, p_err = agent.apply_patch(orig, patch)
        self.assertTrue(ok)
        self.assertEqual(res_code.strip(), mod.strip())

    # ── Capability 32: Repository Understanding ───────────────────────
    def test_cap_32_repo_understanding(self):
        analyzer = RepoAnalyzer(str(self.root_dir))
        
        # 1. Repository Scanning
        scan_res = analyzer.scan_repository()
        self.assertGreater(scan_res["total_files"], 0)
        self.assertGreater(scan_res["total_lines"], 0)
        self.assertIn(".py", scan_res["extension_distribution"])

        # 2. Symbol Indexing
        symbols = analyzer.index_symbols(str(self.root_dir / "jarvis" / "software"))
        self.assertGreater(symbols["modules_indexed"], 0)
        self.assertGreater(symbols["total_classes"], 0)
        
        # 3. Symbol Search
        found = analyzer.find_symbol("AutonomousCodingAgent", str(self.root_dir / "jarvis" / "software"))
        self.assertGreater(len(found), 0)

    # ── Capability 33: Automated Debugging ────────────────────────────
    def test_cap_33_automated_debugging(self):
        debugger = AutomatedDebugger(str(self.root_dir))
        
        sample_traceback = """Traceback (most recent call last):
  File "C:\\test\\app.py", line 42, in process_user
    name = user.get_full_name()
AttributeError: 'NoneType' object has no attribute 'get_full_name'"""

        analysis = debugger.analyze_traceback(sample_traceback)
        self.assertEqual(analysis["parsed_traceback"]["exception_type"], "AttributeError")
        self.assertEqual(analysis["parsed_traceback"]["culprit_frame"]["line"], 42)
        self.assertIn("Null or Missing Attribute", analysis["diagnosis"]["error_category"])
        self.assertTrue(analysis["can_auto_fix"])
        self.assertIn("is not None", analysis["safe_snippet"])

    # ── Capability 34: Test Generation ────────────────────────────────
    def test_cap_34_test_generation(self):
        generator = TestGenerator(str(self.root_dir))
        code_sample = """
def compute_discount(price: float, percentage: float) -> float:
    \"\"\"Computes discounted price.\"\"\"
    return price * (1.0 - percentage)
"""
        res = generator.generate_tests_for_code(code_sample, module_name="billing")
        self.assertTrue(res["success"])
        self.assertGreaterEqual(res["functions_found"], 1)
        self.assertIn("class TestBilling(unittest.TestCase):", res["test_code"])
        self.assertIn("def test_compute_discount_standard_execution", res["test_code"])

    # ── Capability 35: Test Execution ─────────────────────────────────
    def test_cap_35_test_execution(self):
        runner = TestRunner(str(self.root_dir))
        
        # Run a standalone passing test string
        test_code = """
import unittest

class SimplePassTest(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(2 + 2, 4)

if __name__ == '__main__':
    unittest.main()
"""
        res = runner.run_test_string(test_code, timeout=10)
        self.assertTrue(res["success"])
        self.assertEqual(res["tests_run"], 1)
        self.assertEqual(res["passed"], 1)
        self.assertEqual(res["failed"], 0)

    # ── Capability 36: Code Review ────────────────────────────────────
    def test_cap_36_code_review(self):
        reviewer = CodeReviewer()
        
        code_with_issues = """
def bad_function(items=[]):  # mutable default arg
    try:
        x = 10 / 2
    except:  # bare except
        pass
    api_key = "AIzaSySecretToken1234567890"  # hardcoded secret
"""
        report = reviewer.review_code(code_with_issues, filename="bad_sample.py")
        self.assertFalse(report["passed"])
        self.assertLess(report["score"], 80)
        
        rules = [issue["rule"] for issue in report["issues"]]
        self.assertIn("MUTABLE_DEFAULT_ARG", rules)
        self.assertIn("BARE_EXCEPT", rules)
        self.assertIn("HARDCODED_SECRET", rules)

    # ── Capability 37: Architecture Analysis ──────────────────────────
    def test_cap_37_architecture_analysis(self):
        arch = ArchitectureAnalyzer(str(self.root_dir))
        
        # Check dependency analysis on jarvis/software
        deps = arch.analyze_dependencies(str(self.root_dir / "jarvis" / "software"))
        self.assertGreater(deps["total_modules"], 0)
        
        # Check circular dependency detection
        cycles = arch.detect_circular_imports(str(self.root_dir / "jarvis" / "software"))
        self.assertIsInstance(cycles, list)

        # Check metrics
        metrics = arch.calculate_metrics(str(self.root_dir / "jarvis" / "software"))
        self.assertIn("coupling_metrics", metrics)

    # ── Capability 38: Dependency Analysis ────────────────────────────
    def test_cap_38_dependency_analysis(self):
        deps_analyzer = DependencyAnalyzer(str(self.root_dir))
        audit = deps_analyzer.audit_dependencies()
        
        self.assertIsInstance(audit["declared_requirements"], list)
        self.assertGreater(audit["installed_count"], 0)

    # ── Capability 39: Documentation Generation ───────────────────────
    def test_cap_39_doc_generation(self):
        doc_gen = DocumentationGenerator(str(self.root_dir))
        sample_path = str(self.root_dir / "jarvis" / "software" / "coding_agent.py")
        
        doc_res = doc_gen.generate_module_docs(sample_path)
        self.assertTrue(doc_res["success"])
        self.assertIn("# Module `coding_agent`", doc_res["markdown"])
        self.assertIn("AutonomousCodingAgent", doc_res["markdown"])
        self.assertGreater(doc_res["docstring_coverage_pct"], 50.0)

    # ── Capability 40: Git Intelligence ───────────────────────────────
    def test_cap_40_git_intelligence(self):
        git = GitIntelligence(str(self.root_dir))
        status = git.get_status()
        self.assertTrue(status.get("is_repo"))
        self.assertIn("branch", status)

        history = git.get_history(limit=3)
        self.assertIsInstance(history, list)

    # ── Capability 41: Deployment Assistant ───────────────────────────
    def test_cap_41_deployment_assistant(self):
        dep = DeploymentAssistant(str(self.root_dir))
        # Run preflight without triggering full re-test loop to keep test fast
        preflight = dep.run_preflight(target_port=4700, run_full_tests=False)
        self.assertIn("verdict", preflight)
        self.assertIn(preflight["verdict"], ["READY", "WARNING", "BLOCKED"])
        self.assertGreater(preflight["total_checks"], 0)

    # ── Capability 42: Build Diagnostics ──────────────────────────────
    def test_cap_42_build_diagnostics(self):
        build = BuildDiagnostics(str(self.root_dir))
        report = build.generate_build_report()
        self.assertTrue(report["compilation"]["success"])
        self.assertGreater(report["compilation"]["total_compiled"], 0)

    # ── Capability 43: Database Intelligence ──────────────────────────
    def test_cap_43_database_intelligence(self):
        # Create a temporary SQLite database for testing
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name

        try:
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE);")
            conn.execute("INSERT INTO users (name, email) VALUES ('Tony Stark', 'tony@stark.com');")
            conn.execute("INSERT INTO users (name, email) VALUES ('Bruce Banner', 'bruce@avengers.org');")
            conn.commit()
            conn.close()

            db_intel = DatabaseIntelligence(db_path)
            
            # 1. Schema Inspection
            schema = db_intel.inspect_schema()
            self.assertTrue(schema["success"])
            self.assertIn("users", schema["tables"])
            self.assertEqual(schema["tables"]["users"]["row_count"], 2)

            # 2. Safe Query
            q_res = db_intel.execute_safe_query("SELECT id, name FROM users ORDER BY id ASC")
            self.assertTrue(q_res["success"])
            self.assertEqual(len(q_res["rows"]), 2)
            self.assertEqual(q_res["rows"][0]["name"], "Tony Stark")

            # 3. Block Mutating Queries
            blocked = db_intel.execute_safe_query("DROP TABLE users")
            self.assertFalse(blocked["success"])
            self.assertIn("blocked", blocked["error"].lower())

            # 4. Explain Plan
            plan = db_intel.explain_query("SELECT * FROM users WHERE email = 'tony@stark.com'")
            self.assertTrue(plan["success"])
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    # ── Capability 44: API Testing ────────────────────────────────────
    def test_cap_44_api_testing(self):
        tester = APITester()
        
        # Test schema validation
        sample_json = {"status": "success", "count": 42, "items": ["a", "b"]}
        val_res = tester.validate_schema(sample_json, {"status": str, "count": int, "items": list})
        self.assertTrue(val_res["valid"])

        val_invalid = tester.validate_schema(sample_json, {"status": int})
        self.assertFalse(val_invalid["valid"])

    # ── Capability 45: Refactoring Agent ──────────────────────────────
    def test_cap_45_refactoring_agent(self):
        refactor = RefactoringAgent()
        
        # 1. Identifier Renaming
        orig_code = "def calculate(val):\n    return val * 2\n"
        res = refactor.rename_symbol(orig_code, "calculate", "compute_double")
        self.assertTrue(res["success"])
        self.assertIn("def compute_double(val):", res["code"])
        self.assertEqual(res["replacements"], 1)

        # 2. Extract Constant
        code_with_literal = 'def greet():\n    return "Welcome to Jarvis"\n'
        c_res = refactor.extract_constant(code_with_literal, "Welcome to Jarvis", "GREETING_MSG")
        self.assertTrue(c_res["success"])
        self.assertIn('GREETING_MSG = "Welcome to Jarvis"', c_res["code"])
        self.assertIn("return GREETING_MSG", c_res["code"])

        # 3. Remove Unused Imports
        code_unused = "import math\nimport os\n\ndef run():\n    return os.getcwd()\n"
        u_res = refactor.remove_unused_imports(code_unused)
        self.assertTrue(u_res["success"])
        self.assertIn("math", u_res["unused_detected"])
        self.assertNotIn("import math", u_res["code"])
        self.assertIn("import os", u_res["code"])

    # ── Unified SoftwareEngineeringNexus Dispatcher ───────────────────
    def test_nexus_dispatcher(self):
        # Test dispatcher across capability numbers 31 to 45
        target_sw = str(self.root_dir / "jarvis" / "software")
        for cap_num in range(31, 46):
            res = nexus.execute_capability(cap_num, target_dir=target_sw)
            self.assertIsInstance(res, dict)
            self.assertEqual(res.get("capability_number"), cap_num)
            self.assertIn("capability_name", res)


if __name__ == "__main__":
    unittest.main()
