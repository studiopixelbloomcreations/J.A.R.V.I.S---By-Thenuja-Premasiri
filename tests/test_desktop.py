"""
Unit Tests for J.A.R.V.I.S. Desktop & OS Intelligence Engine (Capabilities 16-30).
Validates virtual cursor, mouse dynamics, clicking, scrolling, dragging, window orchestration,
emergency stop/pause safety, and all 15 desktop intelligence subsystems.
"""
import os
import time
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image

import jarvis.desktop as d
from jarvis.desktop.emergency import EmergencyStopError


class TestDesktopInteractionEngine(unittest.TestCase):
    """Tests the integrated desktop interaction engine and cursor dynamics."""

    def setUp(self):
        d.emergency.reset()
        # Use virtual cursor mode for deterministic, non-disruptive tests
        d.set_virtual_mode(True)

    def tearDown(self):
        d.set_virtual_mode(False)
        d.emergency.reset()

    def test_virtual_mode_toggle(self):
        self.assertTrue(d.is_virtual_mode())
        d.set_virtual_mode(False)
        self.assertFalse(d.is_virtual_mode())
        d.set_virtual_mode(True)
        self.assertTrue(d.is_virtual_mode())

    def test_cursor_movement_and_position(self):
        res = d.move_cursor(320, 240, smooth=False)
        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("x"), 320)
        self.assertEqual(res.get("y"), 240)

        x, y = d.get_cursor_position()
        self.assertEqual((x, y), (320, 240))

        # Smooth move
        res_smooth = d.move_cursor(400, 300, smooth=True, steps=4)
        self.assertEqual(res_smooth.get("status"), "success")
        self.assertEqual(d.get_cursor_position(), (400, 300))

    def test_relative_and_bezier_movement(self):
        d.move_cursor(200, 200, smooth=False)
        res_rel = d.move_relative(50, -30)
        self.assertEqual(res_rel.get("status"), "success")
        self.assertEqual(d.get_cursor_position(), (250, 170))

        # Bezier curve move
        res_bez = d.move_bezier(500, 400, steps=8)
        self.assertEqual(res_bez.get("status"), "success")
        self.assertEqual(d.get_cursor_position(), (500, 400))

    def test_clicks_and_mouse_buttons(self):
        # Single click
        res_click = d.click(100, 150, button="left")
        self.assertEqual(res_click.get("status"), "success")
        self.assertEqual(res_click.get("action"), "left_click")

        # Right click
        res_right = d.right_click(200, 250)
        self.assertEqual(res_right.get("status"), "success")
        self.assertEqual(res_right.get("action"), "right_click")

        # Double click
        res_double = d.double_click(300, 350)
        self.assertEqual(res_double.get("status"), "success")
        self.assertEqual(res_double.get("clicks"), 2)

        # Triple click
        res_triple = d.triple_click(350, 350)
        self.assertEqual(res_triple.get("status"), "success")
        self.assertEqual(res_triple.get("clicks"), 3)

        # Middle click
        res_mid = d.middle_click(400, 400)
        self.assertEqual(res_mid.get("status"), "success")
        self.assertEqual(res_mid.get("action"), "middle_click")

        # Mouse down & up
        res_down = d.mouse_down("left")
        self.assertEqual(res_down.get("status"), "success")
        res_up = d.mouse_up("left")
        self.assertEqual(res_up.get("status"), "success")

    def test_scrolling_and_dragging(self):
        res_up = d.scroll(120, direction="up")
        self.assertEqual(res_up.get("status"), "success")
        self.assertEqual(res_up.get("delta"), 120)

        res_down = d.scroll(120, direction="down")
        self.assertEqual(res_down.get("status"), "success")
        self.assertEqual(res_down.get("delta"), -120)

        res_h = d.scroll_horizontal(120, direction="right")
        self.assertEqual(res_h.get("status"), "success")

        # Drag to
        res_drag = d.drag_to(600, 450)
        self.assertEqual(res_drag.get("status"), "success")
        self.assertEqual(res_drag.get("action"), "drag")

        # Drag and drop
        res_dnd = d.drag_and_drop(100, 100, 500, 500, steps=6)
        self.assertEqual(res_dnd.get("status"), "success")
        self.assertEqual(res_dnd.get("from"), (100, 100))
        self.assertEqual(res_dnd.get("to"), (500, 500))

    def test_emergency_stop_and_pause(self):
        self.assertFalse(d.emergency.is_stopped)
        self.assertFalse(d.emergency.is_paused)

        # Pause & Resume
        p_res = d.emergency.pause("Test pause")
        self.assertEqual(p_res.get("status"), "paused")
        self.assertTrue(d.emergency.is_paused)

        r_res = d.emergency.resume()
        self.assertEqual(r_res.get("status"), "running")
        self.assertFalse(d.emergency.is_paused)

        # Trigger emergency stop
        stop_res = d.emergency.trigger_emergency_stop("Safety test stop")
        self.assertEqual(stop_res.get("status"), "emergency_stop")
        self.assertTrue(d.emergency.is_stopped)

        # Any movement or action should raise EmergencyStopError
        with self.assertRaises(EmergencyStopError):
            d.move_cursor(100, 100)

        with self.assertRaises(EmergencyStopError):
            d.click(100, 100)

        # Reset returns to operational state
        reset_res = d.emergency.reset()
        self.assertEqual(reset_res.get("status"), "reset")
        self.assertFalse(d.emergency.is_stopped)

        # Should work again
        move_after_reset = d.move_cursor(150, 150, smooth=False)
        self.assertEqual(move_after_reset.get("status"), "success")

    def test_interaction_engine_unified_facade(self):
        engine = d.interaction_engine
        engine.set_virtual_mode(True)
        res = engine.move_cursor(220, 330, smooth=False)
        self.assertEqual(res.get("status"), "success")
        self.assertEqual(engine.get_cursor_position(), (220, 330))

        state = engine.get_desktop_state()
        self.assertIn("cursor", state)
        self.assertIn("geometry", state)
        self.assertIn("is_stopped", state)
        self.assertFalse(state["is_stopped"])


class TestWindowOrchestration(unittest.TestCase):
    """Tests window management, geometry calculation, and tiling orchestration."""

    def test_screen_geometry(self):
        geo = d.get_screen_geometry()
        self.assertIn("primary", geo)
        self.assertIn("virtual", geo)
        self.assertGreater(geo["primary"]["width"], 0)
        self.assertGreater(geo["primary"]["height"], 0)

    def test_window_enumeration_and_search(self):
        wins = d.list_windows()
        self.assertIsInstance(wins, list)
        if wins:
            first = wins[0]
            self.assertIn("hwnd", first)
            self.assertIn("title", first)
            self.assertIn("width", first)
            self.assertIn("height", first)

            # Test finding by exact or partial title
            found_hwnd = d.find_window(first["title"])
            self.assertEqual(found_hwnd, first["hwnd"])

    def test_snap_and_quadrant_calculation(self):
        # Test snap on nonexistent window gracefully reports error
        res_err = d.snap_window(999999999, "left")
        self.assertEqual(res_err.get("status"), "error")

        # Test quadrant orchestrator
        res_quad_err = d.window_orchestrator.snap_to_quadrant(999999999, "top_left")
        self.assertEqual(res_quad_err.get("status"), "error")

    def test_window_orchestrator_layout_presets(self):
        # Apply layout with no windows or mock window
        res = d.window_orchestrator.apply_layout_preset("split_columns", window_identifiers=[])
        self.assertIn("status", res)

        # Save and restore layout
        save_res = d.window_orchestrator.save_layout("test_session_layout")
        self.assertEqual(save_res.get("status"), "success")
        restore_res = d.window_orchestrator.restore_layout("test_session_layout")
        self.assertEqual(restore_res.get("status"), "success")


class TestCapabilities16To30(unittest.TestCase):
    """Verifies all 15 Desktop and OS Intelligence capabilities (16 to 30)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="jarvis_desktop_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # Capability 16: Full Desktop Vision
    def test_cap16_desktop_vision(self):
        vis = d.desktop_vision
        dpi = vis.get_dpi_scaling()
        self.assertIn("dpi", dpi)
        self.assertIn("scale_percent", dpi)

        monitors = vis.get_multi_monitor_layout()
        self.assertIsInstance(monitors, list)
        self.assertGreaterEqual(len(monitors), 1)

        pixel = vis.sample_pixel_color(100, 100)
        self.assertEqual(pixel.get("status"), "success")
        self.assertIn("hex", pixel)
        self.assertIn("rgb", pixel)

        # Visual difference detection
        img1 = Image.new("RGB", (100, 100), color="white")
        img2 = Image.new("RGB", (100, 100), color="black")
        diff_res = vis.detect_visual_difference(img1, img2)
        self.assertEqual(diff_res.get("status"), "success")
        self.assertTrue(diff_res.get("has_changed"))
        self.assertGreater(diff_res.get("changed_percent"), 90.0)

    # Capability 17: UI Element Recognition
    def test_cap17_ui_element_recognition(self):
        recognizer = d.ui_recognizer
        # Enumerate controls on active or desktop window
        controls = recognizer.enumerate_controls()
        self.assertIsInstance(controls, list)

        # Element hit testing
        elem = recognizer.element_at_point(50, 50)
        # Result is UIElement or None
        if elem:
            self.assertIsInstance(elem, d.UIElement)
            self.assertIn("hwnd", elem.to_dict())

    # Capability 18: Application Intelligence
    def test_cap18_application_intelligence(self):
        app_intel = d.app_intelligence
        # Categorization
        self.assertEqual(app_intel.categorize_app("chrome.exe"), "Browser")
        self.assertEqual(app_intel.categorize_app("code"), "IDE_Editor")
        self.assertEqual(app_intel.categorize_app("powershell.exe"), "Terminal_Shell")
        self.assertEqual(app_intel.categorize_app("whatsapp"), "Communication")

        # Active apps
        active_apps = app_intel.get_active_applications()
        self.assertIsInstance(active_apps, list)
        self.assertGreater(len(active_apps), 0)
        self.assertIn("pid", active_apps[0])

        # Installed apps
        installed = app_intel.get_installed_applications(limit=10)
        self.assertIsInstance(installed, list)

    # Capability 19: Window Orchestration
    def test_cap19_window_orchestration(self):
        orch = d.window_orchestrator
        self.assertIsNotNone(orch)
        save = orch.save_layout("unit_test_layout")
        self.assertEqual(save.get("status"), "success")

    # Capability 20: File Intelligence
    def test_cap20_file_intelligence(self):
        fi = d.file_intelligence
        # Create test files
        f1 = Path(self.test_dir) / "doc1.txt"
        f2 = Path(self.test_dir) / "doc2.txt"
        f1.write_text("Hello Jarvis Intelligence Test", encoding="utf-8")
        f2.write_text("Hello Jarvis Intelligence Test", encoding="utf-8")

        meta = fi.get_file_metadata(str(f1))
        self.assertEqual(meta.get("status"), "success")
        self.assertEqual(meta.get("name"), "doc1.txt")
        self.assertEqual(meta.get("category"), "Document")

        search_res = fi.search_files(self.test_dir, pattern="*.txt")
        self.assertEqual(len(search_res), 2)

        # Duplicate detection (doc1 and doc2 have identical content)
        dups = fi.find_duplicate_files(self.test_dir, min_size_bytes=5)
        self.assertGreaterEqual(len(dups), 1)
        self.assertEqual(len(dups[0]["copies"]), 2)

    # Capability 21: Automated Troubleshooting
    def test_cap21_automated_troubleshooting(self):
        tb = d.troubleshooter
        scan = tb.run_troubleshooting_scan()
        self.assertIn("status", scan)
        self.assertIn("total_issues", scan)
        self.assertIn("unresponsive_windows", scan)
        self.assertIn("recommended_actions", scan)

        # Clean temp files dry run
        clean_res = tb.clean_temp_files(dry_run=True)
        self.assertEqual(clean_res.get("status"), "success")
        self.assertTrue(clean_res.get("dry_run"))

    # Capability 22: Hardware Monitoring
    def test_cap22_hardware_monitoring(self):
        hw = d.hardware_monitor
        cpu = hw.get_cpu_metrics()
        self.assertIn("utilization_percent", cpu)
        self.assertGreater(cpu["logical_cores"], 0)

        mem = hw.get_memory_metrics()
        self.assertIn("total_gb", mem)
        self.assertIn("used_percent", mem)

        disk = hw.get_disk_metrics()
        self.assertIn("partitions", disk)
        self.assertGreater(len(disk["partitions"]), 0)

        bat = hw.get_battery_metrics()
        self.assertIn("has_battery", bat)

        telemetry = hw.get_full_telemetry()
        self.assertIn("status", telemetry)
        self.assertIn("alerts", telemetry)

    # Capability 23: Application Diagnostics
    def test_cap23_application_diagnostics(self):
        diag = d.app_diagnostics
        my_pid = os.getpid()
        proc_diag = diag.diagnose_process(my_pid)
        self.assertEqual(proc_diag.get("status"), "success")
        self.assertEqual(proc_diag.get("pid"), my_pid)
        self.assertIn("threads", proc_diag)
        self.assertIn("memory", proc_diag)

    # Capability 24: Environment Configuration
    def test_cap24_environment_configuration(self):
        env = d.env_config
        os_tel = env.get_os_telemetry()
        self.assertIn("system", os_tel)
        self.assertIn("python_version", os_tel)

        path_audit = env.audit_path_variable()
        self.assertIn("total_entries", path_audit)
        self.assertIn("valid_count", path_audit)

        py_env = env.get_python_environment()
        self.assertIn("executable", py_env)
        self.assertIn("is_virtualenv", py_env)

    # Capability 25: Workflow Automation
    def test_cap25_workflow_automation(self):
        wf = d.workflow_engine
        d.set_virtual_mode(True)
        steps = [
            {"action": "move", "params": {"x": 200, "y": 300, "smooth": False}},
            {"action": "wait", "params": {"seconds": 0.05}},
            {"action": "scroll", "params": {"delta": 60, "direction": "up"}},
        ]
        wf_res = wf.run_workflow("test_workflow", steps)
        self.assertEqual(wf_res.get("status"), "success")
        self.assertEqual(wf_res.get("steps_count"), 3)
        self.assertEqual(len(wf_res.get("logs")), 3)

    # Capability 26: Desktop State Memory
    def test_cap26_desktop_state_memory(self):
        mem = d.DesktopStateMemory(storage_dir=os.path.join(self.test_dir, "states"))
        snap1 = mem.capture_snapshot("snap_init")
        self.assertEqual(snap1.get("name"), "snap_init")
        self.assertIn("windows", snap1)

        loaded = mem.load_snapshot("snap_init")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.get("name"), "snap_init")

        # Snapshot diff
        diff = mem.diff_snapshots("snap_init", "snap_init")
        self.assertEqual(diff.get("status"), "success")
        self.assertEqual(diff.get("closed_count"), 0)
        self.assertEqual(diff.get("new_count"), 0)

    # Capability 27: Visual Guidance
    def test_cap27_visual_guidance(self):
        vg = d.visual_guidance
        vg.clear_overlays()
        b = vg.create_bounding_box(50, 50, 200, 100, label="Search Bar")
        self.assertEqual(b.get("label"), "SEARCH BAR")

        arrow = vg.create_arrow(10, 10, 50, 50, label="Click here")
        self.assertEqual(arrow.get("type"), "arrow")

        badge = vg.create_step_badge(1, 100, 100, caption="First step")
        self.assertEqual(badge.get("step"), 1)

        self.assertEqual(len(vg.get_active_overlays()), 3)

        # Draw onto mock PIL image
        canvas = Image.new("RGB", (640, 480), color=(20, 25, 35))
        annotated = vg.draw_overlays_on_image(canvas)
        self.assertEqual(annotated.size, (640, 480))

        vg.clear_overlays()
        self.assertEqual(len(vg.get_active_overlays()), 0)

    # Capability 28: Application Learning
    def test_cap28_application_learning(self):
        learn = d.ApplicationLearningEngine(profile_path=os.path.join(self.test_dir, "app_learn.json"))
        rec1 = learn.record_app_launch("chrome.exe")
        self.assertEqual(rec1.get("total_launches"), 1)
        rec2 = learn.record_app_launch("chrome.exe")
        self.assertEqual(rec2.get("total_launches"), 2)

        learn.record_window_placement("chrome.exe", 0, 0, 1280, 800)
        pref = learn.get_preferred_geometry("chrome.exe")
        self.assertIsNotNone(pref)
        self.assertEqual(pref["width"], 1280)

        top = learn.get_top_frequent_apps()
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]["app"], "chrome.exe")

        sugg = learn.suggest_optimal_layout(["chrome.exe", "code.exe"])
        self.assertEqual(sugg.get("recommended_preset"), "split_columns")

    # Capability 29: Local Backup Intelligence
    def test_cap29_local_backup_intelligence(self):
        backup_mgr = d.LocalBackupIntelligence(backup_dir=os.path.join(self.test_dir, "backups"))
        # Source directory to back up
        src_folder = Path(self.test_dir) / "source_project"
        src_folder.mkdir()
        (src_folder / "fileA.txt").write_text("Alpha code file", encoding="utf-8")
        (src_folder / "fileB.txt").write_text("Beta documentation", encoding="utf-8")

        res_backup = backup_mgr.create_backup(str(src_folder), backup_name="test_proj")
        self.assertEqual(res_backup.get("status"), "success")
        self.assertEqual(res_backup.get("files_backed_up"), 2)
        archive_name = res_backup.get("archive_name")

        # Verify integrity
        integrity = backup_mgr.verify_backup_integrity(archive_name)
        self.assertEqual(integrity.get("status"), "healthy")
        self.assertTrue(integrity.get("is_valid"))

        # Restore
        dest_folder = Path(self.test_dir) / "restored_project"
        res_restore = backup_mgr.restore_backup(archive_name, str(dest_folder))
        self.assertEqual(res_restore.get("status"), "success")
        self.assertTrue((dest_folder / "fileA.txt").exists())
        self.assertEqual((dest_folder / "fileA.txt").read_text(encoding="utf-8"), "Alpha code file")

    # Capability 30: System Health Reporting
    def test_cap30_system_health_reporting(self):
        reporter = d.system_health_reporter
        score_data = reporter.compute_health_score()
        self.assertIn("health_score", score_data)
        self.assertIn("status", score_data)
        self.assertGreaterEqual(score_data["health_score"], 0.0)
        self.assertLessEqual(score_data["health_score"], 100.0)

        md = reporter.generate_markdown_report()
        self.assertIn("J.A.R.V.I.S. System Health & OS Diagnostic Report", md)
        self.assertIn("Hardware Performance Telemetry", md)


if __name__ == "__main__":
    unittest.main()
