"""
Jarvis Connected Devices & External Environment Subsystem (Capabilities 116-125).

Capabilities:
116. Local Network Dashboard (LocalNetworkDashboard)
117. Smart Device Integration (SmartDeviceManager, SmartBulb, SmartPlug, Thermostat, BusyBarMatrix)
118. Sensor Dashboard (SensorDashboard, SensorChannel, SensorReading)
119. Camera Integration (CameraManager, CameraFrame)
120. Environmental Monitoring (EnvironmentalMonitor, EnvironmentalSnapshot)
121. Home Automation (HomeAssistantClient, MQTTClientAdapter, AutomationRuleEngine)
122. Local Server Management (LocalServerManager, PortHealth, ServiceStatus)
123. Cloud Resource Monitoring (CloudResourceMonitor, APIHealthProbe, CircuitBreaker)
124. Database Monitoring (DatabaseMonitor, SQLiteHealthReport, SlowQueryRecord)
125. Device Health Monitoring (DeviceHealthMonitor, BatteryStatus, ThermalStatus, ConnectivityStatus)
"""

from typing import Dict, Any, Optional

from .network_dashboard import LocalNetworkDashboard, NetworkInterface, NetworkHost, NetworkThroughput
from .smart_devices import SmartDeviceManager, SmartDevice, SmartBulb, SmartPlug, Thermostat, BusyBarMatrix
from .sensor_dashboard import SensorDashboard, SensorChannel, SensorReading, SensorThresholds
from .camera_manager import CameraManager, CameraFrame
from .environmental import EnvironmentalMonitor, EnvironmentalSnapshot
from .home_automation import HomeAssistantClient, MQTTClientAdapter, AutomationRuleEngine, MQTTMessage
from .server_management import LocalServerManager, PortHealth, ServiceStatus
from .cloud_monitoring import CloudResourceMonitor, APIHealthProbe, CircuitBreaker
from .database_monitoring import DatabaseMonitor, SQLiteHealthReport, SlowQueryRecord
from .device_health import DeviceHealthMonitor, BatteryStatus, ThermalStatus, ConnectivityStatus


class ConnectedDevicesOrchestrator:
    """
    Unified Orchestrator for External Environment and Connected Devices.
    Coordinates all 10 device & infrastructure capabilities (116-125).
    """

    def __init__(self, db_path: Optional[str] = None):
        self.network = LocalNetworkDashboard()
        self.smart_devices = SmartDeviceManager()
        self.sensors = SensorDashboard()
        self.camera = CameraManager()
        self.environmental = EnvironmentalMonitor()
        self.mqtt = MQTTClientAdapter()
        self.ha = HomeAssistantClient()
        self.automation = AutomationRuleEngine(self.ha, self.mqtt)
        self.servers = LocalServerManager()
        self.cloud = CloudResourceMonitor()
        self.database = DatabaseMonitor(default_db_path=db_path)
        self.health = DeviceHealthMonitor()

    def get_full_environment_telemetry(self) -> Dict[str, Any]:
        """
        Gathers comprehensive telemetry across network, smart home, sensors,
        camera, environment, local servers, cloud, databases, and host vitality.
        """
        # Read latest sensor values for environmental computation
        temp_chan = self.sensors.get_channel("temperature")
        hum_chan = self.sensors.get_channel("humidity")
        co2_chan = self.sensors.get_channel("co2")
        pm_chan = self.sensors.get_channel("pm25")
        voc_chan = self.sensors.get_channel("tvoc")

        temp = temp_chan.get_latest().value if temp_chan and temp_chan.get_latest() else 22.5
        hum = hum_chan.get_latest().value if hum_chan and hum_chan.get_latest() else 48.0
        co2 = co2_chan.get_latest().value if co2_chan and co2_chan.get_latest() else 520.0
        pm = pm_chan.get_latest().value if pm_chan and pm_chan.get_latest() else 8.0
        voc = voc_chan.get_latest().value if voc_chan and voc_chan.get_latest() else 65.0

        env_snap = self.environmental.evaluate_environment(temp, hum, co2_ppm=co2, pm25_ugm3=pm, tvoc_ppb=voc)

        return {
            "status": "online",
            "capabilities_active": [116, 117, 118, 119, 120, 121, 122, 123, 124, 125],
            "network": self.network.get_dashboard_summary(),
            "smart_devices": {
                "devices": [d.to_dict() for d in self.smart_devices.list_devices()],
                "energy": self.smart_devices.get_energy_summary()
            },
            "sensors": self.sensors.get_dashboard_summary(),
            "camera": self.camera.get_status(),
            "environmental": {
                "temperature_c": env_snap.temperature_c,
                "humidity_pct": env_snap.humidity_pct,
                "heat_index_c": env_snap.heat_index_c,
                "dew_point_c": env_snap.dew_point_c,
                "vpd_kpa": env_snap.vpd_kpa,
                "iaq_score": env_snap.iaq_score,
                "iaq_grade": env_snap.iaq_grade,
                "comfort_status": env_snap.comfort_status,
                "recommendations": env_snap.recommendations,
            },
            "servers": self.servers.get_server_dashboard(),
            "cloud": self.cloud.get_cloud_dashboard(),
            "database": self.database.get_database_dashboard(),
            "host_health": self.health.get_health_dashboard()
        }


__all__ = [
    "ConnectedDevicesOrchestrator",
    "LocalNetworkDashboard",
    "NetworkInterface",
    "NetworkHost",
    "NetworkThroughput",
    "SmartDeviceManager",
    "SmartDevice",
    "SmartBulb",
    "SmartPlug",
    "Thermostat",
    "BusyBarMatrix",
    "SensorDashboard",
    "SensorChannel",
    "SensorReading",
    "SensorThresholds",
    "CameraManager",
    "CameraFrame",
    "EnvironmentalMonitor",
    "EnvironmentalSnapshot",
    "HomeAssistantClient",
    "MQTTClientAdapter",
    "AutomationRuleEngine",
    "MQTTMessage",
    "LocalServerManager",
    "PortHealth",
    "ServiceStatus",
    "CloudResourceMonitor",
    "APIHealthProbe",
    "CircuitBreaker",
    "DatabaseMonitor",
    "SQLiteHealthReport",
    "SlowQueryRecord",
    "DeviceHealthMonitor",
    "BatteryStatus",
    "ThermalStatus",
    "ConnectivityStatus",
]
