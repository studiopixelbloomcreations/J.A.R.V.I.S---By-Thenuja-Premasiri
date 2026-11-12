"""
Capability 117: Smart Device Integration
Controls, monitors, and provisions smart home devices (Bulbs, Plugs, Switches,
Thermostats, and BusyBar LED Matrix displays) across local network protocols.
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class SmartDevice:
    device_id: str
    name: str
    device_type: str = "generic"
    manufacturer: str = "Generic"
    model: str = "v1"
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    room: str = "Office"
    is_online: bool = True
    last_seen: float = field(default_factory=time.time)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class SmartBulb(SmartDevice):
    power: bool = False
    brightness: int = 100  # 0 to 100%
    color_temp: int = 4000  # 2000K to 6500K
    rgb: List[int] = field(default_factory=lambda: [0, 240, 255])  # Jarvis Cyan default

    def __post_init__(self):
        self.device_type = "bulb"
        self.properties.update({
            "power": self.power,
            "brightness": self.brightness,
            "color_temp": self.color_temp,
            "rgb": self.rgb,
        })


@dataclass
class SmartPlug(SmartDevice):
    power: bool = True
    voltage_v: float = 230.0
    current_a: float = 0.45
    power_w: float = 103.5
    energy_kwh: float = 14.8

    def __post_init__(self):
        self.device_type = "plug"
        self.properties.update({
            "power": self.power,
            "voltage_v": self.voltage_v,
            "current_a": self.current_a,
            "power_w": self.power_w,
            "energy_kwh": self.energy_kwh,
        })


@dataclass
class Thermostat(SmartDevice):
    current_temperature: float = 22.5
    target_temperature: float = 21.0
    hvac_mode: str = "cool"  # off, heat, cool, auto
    fan_mode: str = "auto"
    humidity: float = 52.0

    def __post_init__(self):
        self.device_type = "thermostat"
        self.properties.update({
            "current_temperature": self.current_temperature,
            "target_temperature": self.target_temperature,
            "hvac_mode": self.hvac_mode,
            "fan_mode": self.fan_mode,
            "humidity": self.humidity,
        })


@dataclass
class BusyBarMatrix(SmartDevice):
    matrix_width: int = 72
    matrix_height: int = 16
    current_text: str = "J.A.R.V.I.S. ONLINE"
    priority: int = 20  # default APP tier
    api_token: Optional[str] = None
    firmware_version: str = "27.15.0"
    drawing_mode: str = "72x16 DRAWING"

    def __post_init__(self):
        self.device_type = "busybar"
        self.manufacturer = "BusyBar Systems"
        self.properties.update({
            "matrix_size": f"{self.matrix_width}x{self.matrix_height}",
            "current_text": self.current_text,
            "priority": self.priority,
            "firmware": self.firmware_version,
            "drawing_mode": self.drawing_mode,
        })


class SmartDeviceManager:
    """Manages connected IoT smart devices, state synchronization, and automation triggers."""

    def __init__(self):
        self._devices: Dict[str, SmartDevice] = {}
        self._action_history: List[Dict[str, Any]] = []
        self._populate_default_mesh()

    def _populate_default_mesh(self):
        """Initializes default ambient devices for the Jarvis workstation environment."""
        bulb = SmartBulb(
            device_id="bulb-desk-01",
            name="Studio Desk Bias Light",
            device_type="bulb",
            manufacturer="Philips Hue",
            model="Play Lightbar",
            ip_address="192.168.1.140",
            room="Studio",
            power=True,
            brightness=80,
            rgb=[0, 240, 255]
        )
        plug = SmartPlug(
            device_id="plug-workstation-01",
            name="Workstation Master Plug",
            device_type="plug",
            manufacturer="TP-Link Kasa",
            model="KP115",
            ip_address="192.168.1.145",
            room="Studio",
            power=True,
            power_w=142.0,
            energy_kwh=38.6
        )
        thermo = Thermostat(
            device_id="thermo-studio-01",
            name="Studio Climate Control",
            device_type="thermostat",
            manufacturer="Ecobee",
            model="SmartThermostat Premium",
            ip_address="192.168.1.150",
            room="Studio",
            current_temperature=23.0,
            target_temperature=21.5,
            hvac_mode="cool"
        )
        busybar = BusyBarMatrix(
            device_id="busybar-desk-01",
            name="Front LED BusyBar Multi-Tool",
            device_type="busybar",
            ip_address="192.168.1.153",
            room="Desk",
            current_text="HELLO WORLD",
            priority=20
        )

        for dev in [bulb, plug, thermo, busybar]:
            self.register_device(dev)

    def register_device(self, device: SmartDevice) -> bool:
        """Registers a smart device into the active inventory."""
        self._devices[device.device_id] = device
        return True

    def unregister_device(self, device_id: str) -> bool:
        """Removes a smart device by identifier."""
        if device_id in self._devices:
            del self._devices[device_id]
            return True
        return False

    def get_device(self, device_id: str) -> Optional[SmartDevice]:
        """Retrieves a device by ID."""
        return self._devices.get(device_id)

    def list_devices(self, device_type: Optional[str] = None, room: Optional[str] = None) -> List[SmartDevice]:
        """Lists registered devices with optional type and room filtering."""
        results = list(self._devices.values())
        if device_type:
            results = [d for d in results if d.device_type.lower() == device_type.lower()]
        if room:
            results = [d for d in results if d.room.lower() == room.lower()]
        return results

    def set_power(self, device_id: str, power: bool) -> Dict[str, Any]:
        """Switches device power state."""
        dev = self.get_device(device_id)
        if not dev:
            return {"success": False, "error": f"Device {device_id} not found"}

        if hasattr(dev, "power"):
            dev.power = power
        dev.properties["power"] = power
        dev.last_seen = time.time()

        action = {
            "timestamp": time.time(),
            "device_id": device_id,
            "action": "set_power",
            "state": power,
        }
        self._action_history.append(action)
        return {"success": True, "device_id": device_id, "power": power}

    def set_brightness(self, device_id: str, brightness: int) -> Dict[str, Any]:
        """Sets smart bulb brightness (0 to 100)."""
        dev = self.get_device(device_id)
        if not dev:
            return {"success": False, "error": f"Device {device_id} not found"}

        clamped = max(0, min(100, int(brightness)))
        if hasattr(dev, "brightness"):
            dev.brightness = clamped
        dev.properties["brightness"] = clamped
        dev.last_seen = time.time()

        return {"success": True, "device_id": device_id, "brightness": clamped}

    def set_color_rgb(self, device_id: str, r: int, g: int, b: int) -> Dict[str, Any]:
        """Sets smart bulb RGB color vector."""
        dev = self.get_device(device_id)
        if not dev:
            return {"success": False, "error": f"Device {device_id} not found"}

        rgb = [max(0, min(255, int(v))) for v in [r, g, b]]
        if hasattr(dev, "rgb"):
            dev.rgb = rgb
        dev.properties["rgb"] = rgb
        dev.last_seen = time.time()

        return {"success": True, "device_id": device_id, "rgb": rgb}

    def set_temperature_target(self, device_id: str, target_temp: float) -> Dict[str, Any]:
        """Adjusts thermostat setpoint."""
        dev = self.get_device(device_id)
        if not dev:
            return {"success": False, "error": f"Device {device_id} not found"}

        clamped = max(15.0, min(32.0, float(target_temp)))
        if hasattr(dev, "target_temperature"):
            dev.target_temperature = clamped
        dev.properties["target_temperature"] = clamped
        dev.last_seen = time.time()

        return {"success": True, "device_id": device_id, "target_temperature": clamped}

    def draw_busybar_text(
        self,
        device_id: str,
        text: str,
        priority: int = 20,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Renders scrolling or static text payload to BusyBar 72x16 matrix display.
        Respects priority hierarchy: 0-10 SYS, 11-40 APP, 41-79 HI, 80-100 CRIT.
        """
        dev = self.get_device(device_id)
        if not dev:
            return {"success": False, "error": f"Device {device_id} not found"}

        if dev.device_type != "busybar":
            return {"success": False, "error": f"Device {device_id} is not a BusyBar display"}

        # Validate token if required
        busybar: BusyBarMatrix = dev  # type: ignore
        if busybar.api_token and busybar.api_token != token:
            return {"success": False, "status_code": 401, "error": "Invalid API Token"}

        # Check priority collision
        if priority < busybar.priority:
            return {
                "success": False,
                "status_code": 409,
                "error": f"Preempted by higher priority display task ({busybar.priority} > {priority})"
            }

        busybar.current_text = text
        busybar.priority = priority
        busybar.properties["current_text"] = text
        busybar.properties["priority"] = priority
        busybar.last_seen = time.time()

        return {
            "success": True,
            "status_code": 200,
            "device_id": device_id,
            "rendered_text": text,
            "priority": priority,
            "matrix_size": "72x16",
            "drawing_mode": busybar.drawing_mode
        }

    def discover_devices(self, scan_subnet: Optional[str] = None) -> List[Dict[str, Any]]:
        """Simulates automated discovery of smart devices on local subnet."""
        # Returns current active inventory plus discovery metadata
        return [
            {
                "device_id": d.device_id,
                "name": d.name,
                "type": d.device_type,
                "ip": d.ip_address,
                "online": d.is_online,
                "properties": d.properties
            }
            for d in self._devices.values()
        ]

    def get_energy_summary(self) -> Dict[str, Any]:
        """Aggregates energy consumption across connected smart plugs and appliances."""
        total_watts = 0.0
        total_kwh = 0.0
        plug_count = 0

        for dev in self._devices.values():
            if dev.device_type == "plug" and isinstance(dev, SmartPlug):
                if dev.power:
                    total_watts += dev.power_w
                total_kwh += dev.energy_kwh
                plug_count += 1

        return {
            "monitored_plugs": plug_count,
            "total_power_w": round(total_watts, 2),
            "total_energy_kwh": round(total_kwh, 2),
            "estimated_daily_kwh": round((total_watts * 24.0) / 1000.0, 2)
        }
