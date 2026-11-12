"""
J.A.R.V.I.S. Automated Comprehensive Test Suite
Validates Configuration, Permissions, Vision, Desktop Automation,
150-Skill Registry & Dispatcher, Orchestrator, and REST API Endpoints.
"""

import unittest
import json
import os
import sys
import urllib.request
import urllib.parse
from PIL import Image

# Add workspace root to sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from jarvis.config import load_config, load_user_profile, SCREENSHOTS_DIR, NOTES_DIR, DATA_DIR
from jarvis.core.permissions import (
    broker,
    RISK_READ_ONLY,
    RISK_REVERSIBLE,
    RISK_CONSEQUENTIAL,
    RISK_RESTRICTED,
)
from jarvis.vision.capture import capture_screen, create_diagnostic_desktop_canvas
from jarvis.vision.annotator import annotate_screenshot
from jarvis.desktop.mouse import get_cursor_position, move_cursor
from jarvis.desktop.keyboard import type_text, press_key, press_hotkey
from jarvis.desktop.windows import list_windows, get_active_window, get_system_diagnostics
from jarvis.skills.registry import registry, CATEGORIES, SKILL_DEFINITIONS
from jarvis.skills.handlers import dispatch_skill
from jarvis.core.orchestrator import orchestrator


class TestConfigAndPaths(unittest.TestCase):
    def test_config_loading(self):
        config = load_config()
        self.assertIsInstance(config, dict)
        self.assertIn("model", config)
        self.assertIn("fallback_models", config)
        self.assertIn("fish_audio", config)

    def test_user_profile_loading(self):
        profile = load_user_profile()
        self.assertIsInstance(profile, str)
        self.assertIn("Thenuja", profile)

    def test_storage_directories_exist(self):
        self.assertTrue(os.path.exists(SCREENSHOTS_DIR))
        self.assertTrue(os.path.exists(NOTES_DIR))
        self.assertTrue(os.path.exists(DATA_DIR))


class TestPermissionBroker(unittest.TestCase):
    def setUp(self):
        broker.reset_emergency_stop()
        broker.toggle_pause(False)

    def tearDown(self):
        broker.reset_emergency_stop()
        broker.toggle_pause(False)

    def test_risk_evaluation(self):
        # Read-only operation is allowed immediately
        allowed, needs_approval, app_id, msg = broker.check_permission(
            "test_ro", RISK_READ_ONLY, "Read operation"
        )
        self.assertTrue(allowed)
        self.assertFalse(needs_approval)
        self.assertIsNone(app_id)

        # Consequential operation creates a pending confirmation request
        allowed, needs_approval, app_id, msg = broker.check_permission(
            "test_cq", RISK_CONSEQUENTIAL, "Consequential operation"
        )
        self.assertFalse(allowed)
        self.assertTrue(needs_approval)
        self.assertIsNotNone(app_id)

        # Restricted operation is strictly blocked
        allowed, needs_approval, app_id, msg = broker.check_permission(
            "test_rst", RISK_RESTRICTED, "Restricted operation"
        )
        self.assertFalse(allowed)
        self.assertFalse(needs_approval)

    def test_approval_resolution(self):
        allowed, needs_approval, app_id, msg = broker.check_permission(
            "test_approval", RISK_CONSEQUENTIAL, "Test approval flow"
        )
        self.assertTrue(needs_approval)

        pending = broker.get_pending_approvals()
        self.assertTrue(any(r["id"] == app_id for r in pending))

        # Approve
        res = broker.resolve_approval(app_id, approved=True)
        self.assertEqual(res.get("status"), "success")
        self.assertTrue(res.get("approved"))

        # Verify no longer in pending list
        pending_after = broker.get_pending_approvals()
        self.assertFalse(any(r["id"] == app_id for r in pending_after))

    def test_emergency_stop_and_resume(self):
        broker.trigger_emergency_stop()
        self.assertTrue(broker.emergency_stop_triggered)

        # Permission checks must fail during emergency stop
        allowed, needs_approval, _, msg = broker.check_permission(
            "test_blocked", RISK_READ_ONLY, "Attempted read"
        )
        self.assertFalse(allowed)

        # Clear stop
        broker.reset_emergency_stop()
        self.assertFalse(broker.emergency_stop_triggered)

        allowed_after, _, _, _ = broker.check_permission(
            "test_allowed", RISK_READ_ONLY, "Allowed read"
        )
        self.assertTrue(allowed_after)

    def test_audit_logging(self):
        broker.log_action("test_audit", "TEST_STATUS", "Audited operation", {"param": 42})
        logs = broker.get_audit_log(limit=5)
        self.assertTrue(len(logs) > 0)
        self.assertEqual(logs[0]["skill_id"], "test_audit")
        self.assertEqual(logs[0]["status"], "TEST_STATUS")


class TestVisionSubsystem(unittest.TestCase):
    def test_diagnostic_canvas_generation(self):
        img = create_diagnostic_desktop_canvas()
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (1600, 900))

    def test_screen_capture(self):
        cap = capture_screen(mode="fullscreen")
        self.assertIsNotNone(cap)
        self.assertIn("file_path", cap)
        self.assertIn("timestamp", cap)
        self.assertTrue(os.path.exists(cap["file_path"]))

    def test_screenshot_annotation(self):
        base_path = os.path.join(SCREENSHOTS_DIR, "test_base.png")
        img = Image.new("RGB", (800, 600), color=(20, 20, 30))
        img.save(base_path)

        annotations = [
            {"type": "box", "x": 100, "y": 100, "w": 200, "h": 150, "label": "Target Region", "color": "#00e5ff"},
            {"type": "arrow", "from_x": 50, "from_y": 50, "to_x": 100, "to_y": 100, "color": "#ff3366"},
            {"type": "step", "x": 200, "y": 175, "step_num": 1, "text": "Step 1 Action", "color": "#00e5ff"}
        ]

        result = annotate_screenshot(base_path, annotations)
        self.assertEqual(result.get("status"), "success")
        self.assertTrue(os.path.exists(result["file_path"]))
        self.assertTrue(len(result.get("base64", "")) > 100)


class TestDesktopAutomation(unittest.TestCase):
    def test_mouse_position_and_movement(self):
        x, y = get_cursor_position()
        self.assertIsInstance(x, int)
        self.assertIsInstance(y, int)

        res = move_cursor(x, y, smooth=False)
        self.assertEqual(res.get("status"), "success")

    def test_window_enumeration(self):
        wins = list_windows()
        self.assertIsInstance(wins, list)

    def test_active_window(self):
        act = get_active_window()
        # Active window may be None in headless tests, or a dict
        if act:
            self.assertIn("hwnd", act)

    def test_system_diagnostics(self):
        diag = get_system_diagnostics()
        self.assertIn("system", diag)
        self.assertIn("cpu_cores", diag["system"])
        self.assertIn("ram_used_percent", diag["system"])
        self.assertIn("top_memory_processes", diag)


class TestSkillRegistryAndDispatcher(unittest.TestCase):
    def setUp(self):
        broker.reset_emergency_stop()
        broker.toggle_pause(False)

    def tearDown(self):
        broker.reset_emergency_stop()
        broker.toggle_pause(False)

    def test_150_skills_loaded(self):
        skills = registry.get_all()
        self.assertEqual(len(skills), 150, f"Expected exactly 150 skills, found {len(skills)}")

    def test_prd_category_distribution(self):
        self.assertEqual(len(CATEGORIES), 10)
        expected_distribution = {
            "A": 15,  # 1-15: Voice and Conversation
            "B": 15,  # 16-30: Screen Vision and Annotation
            "C": 20,  # 31-50: Desktop and Window Control
            "D": 20,  # 51-70: File and Folder Assistance
            "E": 15,  # 71-85: Web and Research
            "F": 15,  # 86-100: Knowledge, Memory, and Personal Context
            "G": 15,  # 101-115: Productivity and Planning
            "H": 15,  # 116-130: Coding and Developer Assistance
            "I": 15,  # 131-145: PC Diagnostics and Settings
            "J": 5,   # 146-150: Creative and Media Work
        }
        for cat, expected_count in expected_distribution.items():
            self.assertIn(cat, CATEGORIES)
            cat_skills = registry.get_by_category(cat)
            self.assertEqual(
                len(cat_skills),
                expected_count,
                f"Category {cat} ({CATEGORIES[cat]}) expected {expected_count} skills, got {len(cat_skills)}"
            )

    def test_skill_lookup(self):
        s1 = registry.get_skill("voice_ptt")
        self.assertIsNotNone(s1)
        self.assertEqual(s1["num"], 1)
        self.assertEqual(s1["risk"], RISK_READ_ONLY)

        s150 = registry.get_skill("cre_social_copy")
        self.assertIsNotNone(s150)
        self.assertEqual(s150["num"], 150)

    def test_skill_toggle(self):
        self.assertTrue(registry.get_skill("voice_ptt")["enabled"])
        registry.set_enabled("voice_ptt", False)
        self.assertFalse(registry.get_skill("voice_ptt")["enabled"])
        registry.set_enabled("voice_ptt", True)
        self.assertTrue(registry.get_skill("voice_ptt")["enabled"])

    def test_dispatch_read_only_skill(self):
        res = dispatch_skill("sys_info", {})
        self.assertEqual(res["status"], "success")
        self.assertIn("system", res)

    def test_dispatch_consequential_requires_confirmation(self):
        res = dispatch_skill("file_rename_preview", {"path": "test.txt"})
        self.assertEqual(res["status"], "needs_confirmation")
        self.assertIn("approval_id", res)


class TestOrchestrator(unittest.TestCase):
    def test_intent_parsing(self):
        self.assertEqual(orchestrator.parse_intent("What is in my finance notes?"), "knowledge_qa")
        self.assertEqual(orchestrator.parse_intent("Take a screenshot of the display"), "screen_capture")
        self.assertEqual(orchestrator.parse_intent("Remember that our budget is 50k"), "remember")
        self.assertEqual(orchestrator.parse_intent("Show system diagnostics"), "diagnostics")
        self.assertEqual(orchestrator.parse_intent("EMERGENCY STOP NOW"), "emergency_stop")

    def test_direct_wake_word_query(self):
        res1 = orchestrator.process_request("Jarvis")
        self.assertIn("At your service, sir", res1["answer"])
        res2 = orchestrator.process_request("Hey Jarvis")
        self.assertIn("At your service, sir", res2["answer"])
        res3 = orchestrator.process_request("ජාවිස්", is_sinhala=True)
        self.assertIn("At your service, sir", res3["answer"])

    def test_multi_app_launch_intent(self):
        res = orchestrator.process_request("open yt and whatsapp")
        self.assertIn("YouTube and WhatsApp", res["answer"])
        self.assertEqual(res["state"], "EXECUTING")

    def test_dual_screen_ui_switching(self):
        res_kb = orchestrator.process_request("go to knowledge base")
        self.assertEqual(res_kb.get("switch_ui"), "knowledge-base")
        self.assertIn("Knowledge Base", res_kb.get("answer", ""))

        res_main = orchestrator.process_request("go back to main console")
        self.assertEqual(res_main.get("switch_ui"), "main")
        self.assertIn("main console", res_main.get("answer", ""))


class TestRestAPI(unittest.TestCase):
    BASE_URL = "http://localhost:4700"

    def setUp(self):
        # Ensure server safety state is nominal before test
        self._post("/resume", {})

    def tearDown(self):
        # Reset server safety state after test
        self._post("/resume", {})

    def _get(self, path):
        req = urllib.request.Request(f"{self.BASE_URL}{path}")
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, path, payload):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.BASE_URL}{path}",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_diagnostics_endpoint(self):
        res = self._get("/diagnostics")
        self.assertEqual(res.get("status"), "success")
        self.assertIn("report", res)
        self.assertIn("system", res["report"])

    def test_windows_endpoint(self):
        res = self._get("/windows")
        self.assertEqual(res.get("status"), "success")
        self.assertIn("windows", res)

    def test_skills_endpoint(self):
        res = self._get("/skills")
        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("total"), 150)
        self.assertEqual(len(res.get("skills", [])), 150)

    def test_profile_endpoint(self):
        res = self._get("/profile")
        self.assertEqual(res.get("status"), "success")
        self.assertIn("Thenuja", res.get("profile", ""))

    def test_vision_capture_endpoint(self):
        res = self._get("/vision/capture")
        self.assertEqual(res.get("status"), "success")
        self.assertIn("capture", res)
        self.assertTrue(os.path.exists(res["capture"]["file_path"]))

    def test_stop_and_resume_endpoint(self):
        # Stop
        stop_res = self._post("/stop", {"reason": "API test stop"})
        self.assertEqual(stop_res.get("status"), "success")

        # Resume
        resume_res = self._post("/pause", {"paused": False})
        self.assertEqual(resume_res.get("status"), "success")
        self.assertFalse(resume_res.get("paused"))

    def test_chat_note_query_endpoint(self):
        res = self._post("/chat", {"question": "What is in my notes?", "brain": "gemini-3.5"})
        self.assertIn("answer", res)
        self.assertIn("session_id", res)

    def test_skills_execute_endpoint(self):
        res = self._post("/skills/execute", {"skill_id": "desk_open_app", "params": {"app": "up yootube"}})
        self.assertEqual(res.get("status"), "success")
        self.assertIn("youtube.com", res.get("target", ""))

    def test_launch_application_variants(self):
        from jarvis.desktop.windows import launch_application
        res_yt = launch_application("up yootube")
        self.assertEqual(res_yt["status"], "success")
        self.assertIn("youtube.com", res_yt["target"])

        res_wa = launch_application("open up whatsapp")
        self.assertEqual(res_wa["status"], "success")
        self.assertIn("whatsapp", res_wa["target"])


if __name__ == "__main__":
    unittest.main()
