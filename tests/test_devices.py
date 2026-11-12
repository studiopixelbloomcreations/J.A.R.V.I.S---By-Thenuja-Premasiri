"""
Unit and Integration Test Suite for J.A.R.V.I.S. External Environment
and Connected Devices (Capabilities 116-125).

Tests:
116. Local Network Dashboard
117. Smart Device Integration
118. Sensor Dashboard
119. Camera Integration (OpenCV / web camera capture & RTSP stream adapter)
120. Environmental Monitoring
121. Home Automation (MQTT / Home Assistant / REST IoT adapters)
122. Local Server Management (Service status, port health, restart triggers)
123. Cloud Resource Monitoring (API health, latency, quotas)
124. Database Monitoring (SQLite / PostgreSQL connection checks, query stats)
125. Device Health Monitoring (Battery, connectivity, temperature)
"""

import os
import shutil
import sqlite3
import tempfile
import time
import unittest

from jarvis.devices import (
    ConnectedDevicesOrchestrator,
    LocalNetworkDashboard,
    NetworkInterface,
    NetworkHost,
    SmartDeviceManager,
    SmartBulb,
    SmartPlug,
    Thermostat,
    BusyBarMatrix,
    SensorDashboard,
    SensorChannel,
    SensorReading,
    SensorThresholds,
    CameraManager,
    CameraFrame,
    EnvironmentalMonitor,
    EnvironmentalSnapshot,
    HomeAssistantClient,
    MQTTClientAdapter,
    AutomationRuleEngine,
    LocalServerManager,
    PortHealth,
    ServiceStatus,
    CloudResourceMonitor,
    CircuitBreaker,
    DatabaseMonitor,
    SQLiteHealthReport,
    DeviceHealthMonitor,
    BatteryStatus,
    ThermalStatus,
    ConnectivityStatus,
)


class TestCapability116LocalNetworkDashboard(unittest.TestCase):
    """Capability 116: Local Network Dashboard tests."""

    def setUp(self):
        self.dashboard = LocalNetworkDashboard()

    def test_get_interfaces(self):
        interfaces = self.dashboard.get_interfaces()
        self.assertIsInstance(interfaces, list)
        self.assertGreater(len(interfaces), 0)
        first = interfaces[0]
        self.assertIsInstance(first, NetworkInterface)
        self.assertTrue(hasattr(first, "name"))
        self.assertTrue(hasattr(first, "is_up"))
        self.assertTrue(hasattr(first, "ip_addresses"))

    def test_get_gateway_and_dns(self):
        gw = self.dashboard.get_gateway_and_dns()
        self.assertIn("hostname", gw)
        self.assertIn("local_ip", gw)
        self.assertIn("gateway", gw)
        self.assertIn("dns_servers", gw)
        self.assertIsInstance(gw["dns_servers"], list)

    def test_scan_arp_cache(self):
        hosts = self.dashboard.scan_arp_cache()
        self.assertIsInstance(hosts, list)
        # Should at least find local host
        self.assertGreater(len(hosts), 0)
        self.assertIsInstance(hosts[0], NetworkHost)
        self.assertTrue(hasattr(hosts[0], "ip"))
        self.assertTrue(hasattr(hosts[0], "mac"))

    def test_ping_host_loopback(self):
        # Ping loopback address
        res = self.dashboard.ping_host("127.0.0.1", port=80, timeout=0.1)
        self.assertIn("host", res)
        self.assertIn("reachable", res)
        self.assertIn("status", res)

    def test_throughput_metrics(self):
        metrics = self.dashboard.get_throughput_metrics()
        self.assertGreaterEqual(metrics.bytes_sent, 0)
        self.assertGreaterEqual(metrics.bytes_recv, 0)
        self.assertGreaterEqual(metrics.upload_kbps, 0.0)
        self.assertGreaterEqual(metrics.download_kbps, 0.0)

    def test_dashboard_summary(self):
        summary = self.dashboard.get_dashboard_summary()
        self.assertIn("status", summary)
        self.assertIn("host_summary", summary)
        self.assertIn("interface_count", summary)
        self.assertIn("discovered_hosts_count", summary)
        self.assertIn("throughput", summary)
        self.assertIn("health", summary)


class TestCapability117SmartDeviceIntegration(unittest.TestCase):
    """Capability 117: Smart Device Integration tests."""

    def setUp(self):
        self.manager = SmartDeviceManager()

    def test_default_devices_populated(self):
        devices = self.manager.list_devices()
        self.assertGreaterEqual(len(devices), 4)
        types = {d.device_type for d in devices}
        self.assertIn("bulb", types)
        self.assertIn("plug", types)
        self.assertIn("thermostat", types)
        self.assertIn("busybar", types)

    def test_device_registration_and_lookup(self):
        custom_plug = SmartPlug(
            device_id="plug-lab-01",
            name="Lab 3D Printer Plug",
            room="Workshop",
            power=True,
            power_w=350.0
        )
        self.manager.register_device(custom_plug)
        retrieved = self.manager.get_device("plug-lab-01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Lab 3D Printer Plug")

        # Unregister
        self.assertTrue(self.manager.unregister_device("plug-lab-01"))
        self.assertIsNone(self.manager.get_device("plug-lab-01"))

    def test_list_filtering(self):
        studio_devices = self.manager.list_devices(room="Studio")
        self.assertGreater(len(studio_devices), 0)
        for d in studio_devices:
            self.assertEqual(d.room, "Studio")

        bulbs = self.manager.list_devices(device_type="bulb")
        self.assertEqual(len(bulbs), 1)
        self.assertEqual(bulbs[0].device_type, "bulb")

    def test_set_power_and_brightness(self):
        bulb_id = "bulb-desk-01"
        res_power = self.manager.set_power(bulb_id, False)
        self.assertTrue(res_power["success"])
        bulb = self.manager.get_device(bulb_id)
        self.assertFalse(bulb.properties["power"])

        res_bright = self.manager.set_brightness(bulb_id, 45)
        self.assertTrue(res_bright["success"])
        self.assertEqual(res_bright["brightness"], 45)

        # Clamping check
        res_clamp = self.manager.set_brightness(bulb_id, 150)
        self.assertEqual(res_clamp["brightness"], 100)

    def test_set_color_rgb(self):
        bulb_id = "bulb-desk-01"
        res = self.manager.set_color_rgb(bulb_id, 0, 240, 255)
        self.assertTrue(res["success"])
        self.assertEqual(res["rgb"], [0, 240, 255])

    def test_set_temperature_target(self):
        thermo_id = "thermo-studio-01"
        res = self.manager.set_temperature_target(thermo_id, 20.5)
        self.assertTrue(res["success"])
        self.assertEqual(res["target_temperature"], 20.5)

    def test_busybar_matrix_drawing(self):
        busybar_id = "busybar-desk-01"
        # Standard APP tier message
        res = self.manager.draw_busybar_text(busybar_id, "TEST RUNNING", priority=30)
        self.assertTrue(res["success"])
        self.assertEqual(res["status_code"], 200)
        self.assertEqual(res["rendered_text"], "TEST RUNNING")

        # Lower priority message should be rejected
        res_low = self.manager.draw_busybar_text(busybar_id, "TICKER", priority=5)
        self.assertFalse(res_low["success"])
        self.assertEqual(res_low["status_code"], 409)

        # High priority message should succeed
        res_hi = self.manager.draw_busybar_text(busybar_id, "CRITICAL ALERT", priority=85)
        self.assertTrue(res_hi["success"])
        self.assertEqual(res_hi["priority"], 85)

    def test_energy_summary(self):
        energy = self.manager.get_energy_summary()
        self.assertIn("monitored_plugs", energy)
        self.assertIn("total_power_w", energy)
        self.assertIn("total_energy_kwh", energy)
        self.assertIn("estimated_daily_kwh", energy)
        self.assertGreater(energy["total_power_w"], 0)


class TestCapability118SensorDashboard(unittest.TestCase):
    """Capability 118: Sensor Dashboard tests."""

    def setUp(self):
        self.dashboard = SensorDashboard()

    def test_default_channels(self):
        summary = self.dashboard.get_dashboard_summary()
        self.assertIn("channels", summary)
        channels = summary["channels"]
        self.assertIn("temperature", channels)
        self.assertIn("humidity", channels)
        self.assertIn("co2", channels)
        self.assertIn("pm25", channels)
        self.assertIn("tvoc", channels)
        self.assertIn("light_lux", channels)

    def test_channel_statistics(self):
        chan = self.dashboard.get_channel("temperature")
        self.assertIsNotNone(chan)
        stats = chan.get_statistics()
        self.assertGreater(stats["count"], 0)
        self.assertIsNotNone(stats["mean"])
        self.assertIsNotNone(stats["min"])
        self.assertIsNotNone(stats["max"])
        self.assertIn(stats["trend"], ["rising", "falling", "stable"])

    def test_threshold_alerts(self):
        chan = self.dashboard.get_channel("co2")
        # Normal reading
        chan.add_reading(600.0)
        sev, msg = chan.check_alert()
        self.assertEqual(sev, "NORMAL")

        # Warning reading (> 1000)
        chan.add_reading(1100.0)
        sev, msg = chan.check_alert()
        self.assertEqual(sev, "WARNING_HIGH")
        self.assertIsNotNone(msg)

        # Critical reading (> 1500)
        chan.add_reading(1650.0)
        sev, msg = chan.check_alert()
        self.assertEqual(sev, "CRITICAL_HIGH")

    def test_anomaly_detection(self):
        chan = SensorChannel("test_sound", "dB")
        # Add normal baseline
        for _ in range(20):
            chan.add_reading(45.0)
        # Add massive outlier
        chan.add_reading(140.0)
        anomalies = chan.detect_anomalies(z_thresh=2.5)
        self.assertGreaterEqual(len(anomalies), 1)
        self.assertEqual(anomalies[-1].value, 140.0)

    def test_ingest_reading(self):
        reading = self.dashboard.ingest_reading("radon", 1.8, "pCi/L")
        self.assertEqual(reading.channel, "radon")
        self.assertEqual(reading.value, 1.8)
        self.assertIsNotNone(self.dashboard.get_channel("radon"))


class TestCapability119CameraIntegration(unittest.TestCase):
    """Capability 119: Camera Integration tests."""

    def setUp(self):
        self.cam = CameraManager(width=320, height=240, fps_target=15)

    def tearDown(self):
        self.cam.close_stream()

    def test_camera_status(self):
        status = self.cam.get_status()
        self.assertIn("source", status)
        self.assertIn("resolution", status)
        self.assertEqual(status["resolution"], "320x240")
        self.assertEqual(status["target_fps"], 15)

    def test_synthetic_frame_capture(self):
        frame = self.cam.capture_frame(simulate_motion=False)
        self.assertIsInstance(frame, CameraFrame)
        self.assertEqual(frame.width, 320)
        self.assertEqual(frame.height, 240)
        self.assertIsNotNone(frame.jpeg_bytes)
        self.assertIsNotNone(frame.base64_jpeg)
        self.assertGreater(len(frame.base64_jpeg), 100)

    def test_motion_detection_and_callback(self):
        motion_events = []
        self.cam.add_motion_callback(lambda f: motion_events.append(f))

        # First frame initializes baseline
        self.cam.capture_frame(simulate_motion=False)

        # Second frame introduces synthetic moving object
        frame_motion = self.cam.capture_frame(simulate_motion=True)
        self.assertIsInstance(frame_motion.motion_score, float)
        # If OpenCV is installed, motion detection should compute score
        if self.cam.get_status().get("opencv_available"):
            self.assertGreater(frame_motion.motion_score, 0.0)

    def test_save_snapshot(self):
        temp_dir = tempfile.mkdtemp()
        try:
            snapshot_path = os.path.join(temp_dir, "test_snapshot.jpg")
            ok = self.cam.save_snapshot(snapshot_path)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(snapshot_path))
            self.assertGreater(os.path.getsize(snapshot_path), 0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestCapability120EnvironmentalMonitoring(unittest.TestCase):
    """Capability 120: Environmental Monitoring tests."""

    def setUp(self):
        self.env = EnvironmentalMonitor()

    def test_dew_point_calculation(self):
        # 20°C at 50% relative humidity has dew point of ~9.3°C
        dp = self.env.calculate_dew_point(20.0, 50.0)
        self.assertAlmostEqual(dp, 9.3, delta=0.5)

    def test_heat_index_calculation(self):
        # Moderate temperature (<26.7°C / 80°F) matches dry temperature
        hi_mild = self.env.calculate_heat_index(22.0, 50.0)
        self.assertAlmostEqual(hi_mild, 22.0, delta=1.0)

        # Hot and humid conditions: 32°C at 80% RH produces significant heat index elevation
        hi_hot = self.env.calculate_heat_index(32.0, 80.0)
        self.assertGreater(hi_hot, 38.0)

    def test_vpd_calculation(self):
        # 25°C at 50% RH: VPsat ≈ 3.167 kPa, VPact ≈ 1.583 kPa -> VPD ≈ 1.58 kPa
        vpd = self.env.calculate_vpd(25.0, 50.0)
        self.assertAlmostEqual(vpd, 1.58, delta=0.1)

    def test_iaq_grading(self):
        score_clean, grade_clean = self.env.calculate_iaq(co2_ppm=420.0, pm25_ugm3=5.0, tvoc_ppb=30.0)
        self.assertEqual(grade_clean, "EXCELLENT")
        self.assertLessEqual(score_clean, 50)

        score_polluted, grade_polluted = self.env.calculate_iaq(co2_ppm=1600.0, pm25_ugm3=60.0, tvoc_ppb=350.0)
        self.assertIn(grade_polluted, ["POOR", "UNHEALTHY", "HAZARDOUS"])
        self.assertGreater(score_polluted, 100)

    def test_evaluate_environment(self):
        snapshot = self.env.evaluate_environment(
            temperature_c=22.5,
            humidity_pct=48.0,
            co2_ppm=520.0,
            pm25_ugm3=8.0,
            tvoc_ppb=65.0
        )
        self.assertIsInstance(snapshot, EnvironmentalSnapshot)
        self.assertEqual(snapshot.comfort_status, "COMFORTABLE")
        self.assertEqual(snapshot.iaq_grade, "EXCELLENT")
        self.assertIsInstance(snapshot.recommendations, list)
        self.assertGreater(len(snapshot.recommendations), 0)


class TestCapability121HomeAutomation(unittest.TestCase):
    """Capability 121: Home Automation tests."""

    def setUp(self):
        self.ha = HomeAssistantClient()
        self.mqtt = MQTTClientAdapter()
        self.engine = AutomationRuleEngine(self.ha, self.mqtt)

    def test_home_assistant_client(self):
        # Health check
        health = self.ha.check_api()
        self.assertIn("status", health)

        # State lookup
        state = self.ha.get_state("light.studio_desk")
        self.assertIsNotNone(state)
        self.assertEqual(state["state"], "on")

        # Set state
        updated = self.ha.set_state("light.studio_desk", "off", {"brightness": 0})
        self.assertEqual(updated["state"], "off")

        # Call service
        srv = self.ha.call_service("light", "turn_on", {"entity_id": "light.studio_desk"})
        self.assertTrue(srv["success"])

    def test_mqtt_wildcard_routing(self):
        received_single = []
        received_multi = []

        # Single level '+'
        self.mqtt.subscribe("jarvis/+/temperature", lambda t, p: received_single.append((t, p)))
        # Multi-level '#'
        self.mqtt.subscribe("jarvis/#", lambda t, p: received_multi.append((t, p)))

        # Publish matching both
        self.mqtt.publish("jarvis/studio/temperature", 22.4)
        self.assertEqual(len(received_single), 1)
        self.assertEqual(len(received_multi), 1)
        self.assertEqual(received_single[0][1], 22.4)

        # Publish nested path matching only '#'
        self.mqtt.publish("jarvis/studio/lights/desk/state", "ON")
        self.assertEqual(len(received_single), 1)
        self.assertEqual(len(received_multi), 2)

    def test_automation_rules_and_scenes(self):
        action_fired = []
        self.engine.register_rule(
            rule_id="rule_high_temp",
            trigger_channel="temperature",
            condition=lambda t: t >= 28.0,
            action=lambda: action_fired.append("cool_down_triggered"),
            description="Trigger cooling if temp exceeds 28°C"
        )

        # Sub-threshold
        fired_0 = self.engine.evaluate("temperature", 24.0)
        self.assertEqual(fired_0, 0)
        self.assertEqual(len(action_fired), 0)

        # Over-threshold
        fired_1 = self.engine.evaluate("temperature", 29.5)
        self.assertEqual(fired_1, 1)
        self.assertEqual(len(action_fired), 1)

        # Scene activation
        scene_res = self.engine.activate_scene("Focus Mode")
        self.assertTrue(scene_res["success"])
        self.assertEqual(scene_res["scene"], "Focus Mode")


class TestCapability122LocalServerManagement(unittest.TestCase):
    """Capability 122: Local Server Management tests."""

    def setUp(self):
        self.server_mgr = LocalServerManager()

    def test_check_port_health(self):
        # Probe non-listening local port (e.g. 59999)
        res = self.server_mgr.check_port_health(59999, host="127.0.0.1", timeout=0.1)
        self.assertIsInstance(res, PortHealth)
        self.assertEqual(res.port, 59999)
        self.assertFalse(res.is_open)

    def test_scan_common_ports(self):
        ports = self.server_mgr.scan_common_ports()
        self.assertIsInstance(ports, list)
        self.assertGreaterEqual(len(ports), 5)
        for p in ports:
            self.assertIsInstance(p, PortHealth)

    def test_inspect_current_process(self):
        current_pid = os.getpid()
        proc_status = self.server_mgr.inspect_process(current_pid)
        self.assertIsInstance(proc_status, ServiceStatus)
        self.assertTrue(proc_status.is_running)
        self.assertEqual(proc_status.pid, current_pid)
        self.assertGreater(proc_status.memory_rss_mb, 0.0)

    def test_trigger_restart_cooldown(self):
        # First trigger
        res1 = self.server_mgr.trigger_service_restart("test_daemon")
        self.assertTrue(res1["success"])

        # Second immediate trigger should be blocked by cooldown
        res2 = self.server_mgr.trigger_service_restart("test_daemon")
        self.assertFalse(res2["success"])
        self.assertIn("cooldown", res2["error"])

    def test_server_dashboard(self):
        dashboard = self.server_mgr.get_server_dashboard()
        self.assertIn("status", dashboard)
        self.assertIn("probed_ports_count", dashboard)
        self.assertIn("ports", dashboard)
        self.assertIn("jarvis_process", dashboard)


class TestCapability123CloudResourceMonitoring(unittest.TestCase):
    """Capability 123: Cloud Resource Monitoring tests."""

    def setUp(self):
        self.cloud_mgr = CloudResourceMonitor()

    def test_register_and_list_endpoints(self):
        self.cloud_mgr.register_endpoint("Custom Webhook", "https://httpbin.org/status/200")
        endpoints = self.cloud_mgr.get_cloud_dashboard()
        self.assertIn("Custom Webhook", endpoints["endpoints"])

    def test_circuit_breaker(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_time_seconds=0.05)
        self.assertEqual(cb.state, "CLOSED")
        self.assertTrue(cb.can_execute())

        cb.record_failure()
        self.assertEqual(cb.state, "CLOSED")

        cb.record_failure()
        self.assertEqual(cb.state, "OPEN")
        self.assertFalse(cb.can_execute())

        # Test recovery after timeout
        time.sleep(0.06)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, "HALF_OPEN")

        cb.record_success()
        self.assertEqual(cb.state, "CLOSED")

    def test_cloud_sla_metrics(self):
        # Synthetic SLA record
        self.cloud_mgr._history["Gemini API"] = []
        metrics = self.cloud_mgr.get_sla_metrics("Gemini API")
        self.assertEqual(metrics["uptime_pct"], 100.0)

    def test_cloud_dashboard(self):
        dash = self.cloud_mgr.get_cloud_dashboard()
        self.assertIn("status", dash)
        self.assertIn("endpoint_count", dash)
        self.assertIn("endpoints", dash)


class TestCapability124DatabaseMonitoring(unittest.TestCase):
    """Capability 124: Database Monitoring tests."""

    def setUp(self):
        self.db_mgr = DatabaseMonitor()
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_jarvis.db")

        # Create sample SQLite database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE telemetry (id INTEGER PRIMARY KEY, metric TEXT, val REAL);")
        cur.execute("INSERT INTO telemetry (metric, val) VALUES ('temp', 22.4), ('hum', 48.2);")
        conn.commit()
        conn.close()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_inspect_sqlite(self):
        report = self.db_mgr.inspect_sqlite(self.db_path)
        self.assertIsInstance(report, SQLiteHealthReport)
        self.assertTrue(report.is_healthy)
        self.assertEqual(report.integrity_result.lower(), "ok")
        self.assertGreater(report.page_count, 0)
        self.assertIn("telemetry", report.tables)
        self.assertEqual(report.tables["telemetry"], 2)
        self.assertGreaterEqual(report.benchmark_read_ms, 0.0)

    def test_slow_query_recording(self):
        self.db_mgr.record_query_execution("SELECT * FROM large_log WHERE 1=1;", 120.5)
        slow = self.db_mgr.get_slow_queries()
        self.assertEqual(len(slow), 1)
        self.assertEqual(slow[0]["duration_ms"], 120.5)

    def test_check_postgres_health(self):
        res = self.db_mgr.check_postgres_health(host="127.0.0.1", port=5432, timeout=0.1)
        self.assertIn("database_type", res)
        self.assertIn("reachable", res)
        self.assertIn("port", res)

    def test_database_dashboard(self):
        dash = self.db_mgr.get_database_dashboard(self.db_path)
        self.assertIn("status", dash)
        self.assertIn("sqlite", dash)
        self.assertIn("postgresql", dash)


class TestCapability125DeviceHealthMonitoring(unittest.TestCase):
    """Capability 125: Device Health Monitoring tests."""

    def setUp(self):
        self.health_mgr = DeviceHealthMonitor()

    def test_get_battery_status(self):
        batt = self.health_mgr.get_battery_status()
        self.assertIsInstance(batt, BatteryStatus)
        self.assertGreaterEqual(batt.percent, 0.0)
        self.assertLessEqual(batt.percent, 100.0)
        self.assertIsInstance(batt.power_plugged, bool)

    def test_get_thermal_status(self):
        thermal = self.health_mgr.get_thermal_status()
        self.assertIsInstance(thermal, ThermalStatus)
        self.assertGreater(thermal.cpu_temp_c, 0.0)
        self.assertIsInstance(thermal.is_throttling, bool)

    def test_connectivity_check(self):
        conn = self.health_mgr.check_connectivity()
        self.assertIsInstance(conn, ConnectivityStatus)
        self.assertIsInstance(conn.is_connected, bool)

    def test_calculate_health_score(self):
        # Optimal parameters
        batt = BatteryStatus(has_battery=True, percent=95.0, power_plugged=True)
        therm = ThermalStatus(has_sensors=True, cpu_temp_c=45.0, is_throttling=False)
        conn = ConnectivityStatus(is_connected=True, gateway_reachable=True, dns_resolving=True)

        score_opt, rating_opt, alerts_opt = self.health_mgr.calculate_health_score(
            batt, therm, conn, cpu_load_pct=15.0, mem_used_pct=40.0
        )
        self.assertGreaterEqual(score_opt, 90)
        self.assertEqual(rating_opt, "EXCELLENT")
        self.assertEqual(len(alerts_opt), 0)

        # Stressed parameters (High CPU, high temp, low battery)
        batt_low = BatteryStatus(has_battery=True, percent=12.0, power_plugged=False)
        therm_hot = ThermalStatus(has_sensors=True, cpu_temp_c=88.0, is_throttling=True)
        score_bad, rating_bad, alerts_bad = self.health_mgr.calculate_health_score(
            batt_low, therm_hot, conn, cpu_load_pct=95.0, mem_used_pct=92.0
        )
        self.assertLess(score_bad, 60)
        self.assertGreaterEqual(len(alerts_bad), 3)

    def test_health_dashboard(self):
        dash = self.health_mgr.get_health_dashboard()
        self.assertIn("health_score", dash)
        self.assertIn("health_rating", dash)
        self.assertIn("vitals", dash)
        self.assertIn("battery", dash)
        self.assertIn("thermal", dash)
        self.assertIn("connectivity", dash)


class TestConnectedDevicesOrchestrator(unittest.TestCase):
    """End-to-end integration tests for ConnectedDevicesOrchestrator (Caps 116-125)."""

    def setUp(self):
        self.orch = ConnectedDevicesOrchestrator()

    def test_orchestrator_initialization(self):
        self.assertIsNotNone(self.orch.network)
        self.assertIsNotNone(self.orch.smart_devices)
        self.assertIsNotNone(self.orch.sensors)
        self.assertIsNotNone(self.orch.camera)
        self.assertIsNotNone(self.orch.environmental)
        self.assertIsNotNone(self.orch.mqtt)
        self.assertIsNotNone(self.orch.ha)
        self.assertIsNotNone(self.orch.automation)
        self.assertIsNotNone(self.orch.servers)
        self.assertIsNotNone(self.orch.cloud)
        self.assertIsNotNone(self.orch.database)
        self.assertIsNotNone(self.orch.health)

    def test_full_environment_telemetry(self):
        telemetry = self.orch.get_full_environment_telemetry()
        self.assertEqual(telemetry["status"], "online")
        self.assertEqual(telemetry["capabilities_active"], list(range(116, 126)))
        self.assertIn("network", telemetry)
        self.assertIn("smart_devices", telemetry)
        self.assertIn("sensors", telemetry)
        self.assertIn("camera", telemetry)
        self.assertIn("environmental", telemetry)
        self.assertIn("servers", telemetry)
        self.assertIn("cloud", telemetry)
        self.assertIn("database", telemetry)
        self.assertIn("host_health", telemetry)


if __name__ == "__main__":
    unittest.main()
