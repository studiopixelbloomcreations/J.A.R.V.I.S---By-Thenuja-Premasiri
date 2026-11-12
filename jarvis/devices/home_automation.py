"""
Capability 121: Home Automation
Unified Home Assistant REST API client, embedded MQTT pub/sub broker adapter
with wildcard matching (+ and #), and event-driven automation rule engine.
"""

import json
import re
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable, Pattern


@dataclass
class MQTTMessage:
    topic: str
    payload: Any
    timestamp: float = field(default_factory=time.time)
    qos: int = 0
    retain: bool = False


class MQTTClientAdapter:
    """
    Embedded pub/sub message broker and client adapter.
    Implements MQTT topic hierarchy and wildcard routing:
    - '+' matches a single path level (e.g. 'home/+/temperature')
    - '#' matches multi-level tail (e.g. 'jarvis/devices/#')
    """

    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self._subscribers: List[Tuple[str, Pattern, Callable[[str, Any], None]]] = []
        self._retained_messages: Dict[str, MQTTMessage] = {}
        self._message_log: List[MQTTMessage] = []
        self._is_connected: bool = True

    @staticmethod
    def _topic_pattern_to_regex(pattern: str) -> Pattern:
        """Translates MQTT wildcard topic syntax into regular expression."""
        escaped = re.escape(pattern)
        # Replace escaped wildcards
        escaped = escaped.replace(r"\+", r"[^/]+")
        escaped = escaped.replace(r"\#", r".*")
        return re.compile(f"^{escaped}$")

    def subscribe(self, topic: str, callback: Callable[[str, Any], None]) -> bool:
        """Subscribes callback to an MQTT topic pattern."""
        regex = self._topic_pattern_to_regex(topic)
        self._subscribers.append((topic, regex, callback))

        # Deliver matching retained messages if any
        for r_topic, msg in self._retained_messages.items():
            if regex.match(r_topic):
                try:
                    callback(r_topic, msg.payload)
                except Exception:
                    pass
        return True

    def unsubscribe(self, topic: str) -> int:
        """Removes subscribers for the given topic pattern."""
        initial_count = len(self._subscribers)
        self._subscribers = [s for s in self._subscribers if s[0] != topic]
        return initial_count - len(self._subscribers)

    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> MQTTMessage:
        """Publishes an MQTT message to all matching subscribers."""
        msg = MQTTMessage(topic=topic, payload=payload, qos=qos, retain=retain)
        self._message_log.append(msg)

        if retain:
            self._retained_messages[topic] = msg

        # Route to subscribers
        for _, regex, cb in list(self._subscribers):
            if regex.match(topic):
                try:
                    cb(topic, payload)
                except Exception:
                    pass

        return msg

    def get_message_history(self, topic_filter: Optional[str] = None) -> List[MQTTMessage]:
        """Returns message history, optionally filtered by topic prefix."""
        if not topic_filter:
            return list(self._message_log)
        return [m for m in self._message_log if m.topic.startswith(topic_filter)]


class HomeAssistantClient:
    """
    REST API client adapter for Home Assistant with embedded mock fallback
    for reliable testing and offline operation.
    """

    def __init__(self, base_url: str = "http://localhost:8123", access_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token or "mock_jarvis_token"
        self._mock_states: Dict[str, Dict[str, Any]] = {}
        self._service_call_log: List[Dict[str, Any]] = []
        self._seed_mock_entities()

    def _seed_mock_entities(self):
        """Populates baseline Home Assistant entities."""
        self._mock_states = {
            "light.studio_desk": {
                "entity_id": "light.studio_desk",
                "state": "on",
                "attributes": {"brightness": 200, "rgb_color": [0, 240, 255], "friendly_name": "Studio Desk Light"},
                "last_updated": time.time()
            },
            "switch.fan": {
                "entity_id": "switch.fan",
                "state": "off",
                "attributes": {"friendly_name": "Air Circulation Fan"},
                "last_updated": time.time()
            },
            "climate.studio": {
                "entity_id": "climate.studio",
                "state": "cool",
                "attributes": {"current_temperature": 23.0, "temperature": 21.5, "friendly_name": "Studio HVAC"},
                "last_updated": time.time()
            },
            "sensor.indoor_co2": {
                "entity_id": "sensor.indoor_co2",
                "state": "540",
                "attributes": {"unit_of_measurement": "ppm", "friendly_name": "Desk CO2 Sensor"},
                "last_updated": time.time()
            }
        }

    def _send_request(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Sends HTTP request to Home Assistant REST API; returns None on connection error."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    def check_api(self) -> Dict[str, Any]:
        """Checks API health; falls back to mock status if remote is unavailable."""
        res = self._send_request("/api/")
        if res:
            return {"status": "connected", "remote": True, "message": res.get("message", "API running.")}
        return {"status": "connected_mock", "remote": False, "message": "Jarvis local mock engine active."}

    def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Fetches entity state."""
        res = self._send_request(f"/api/states/{entity_id}")
        if res:
            return res
        return self._mock_states.get(entity_id)

    def set_state(self, entity_id: str, state: str, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Updates entity state."""
        payload = {"state": state, "attributes": attributes or {}}
        res = self._send_request(f"/api/states/{entity_id}", method="POST", data=payload)
        if res:
            return res

        # Mock fallback update
        existing = self._mock_states.get(entity_id, {"entity_id": entity_id, "attributes": {}})
        existing["state"] = state
        existing["attributes"].update(attributes or {})
        existing["last_updated"] = time.time()
        self._mock_states[entity_id] = existing
        return existing

    def call_service(self, domain: str, service: str, service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invokes a Home Assistant domain service (e.g. light/turn_on, switch/toggle)."""
        call_record = {
            "domain": domain,
            "service": service,
            "data": service_data or {},
            "timestamp": time.time()
        }
        self._service_call_log.append(call_record)

        res = self._send_request(f"/api/services/{domain}/{service}", method="POST", data=service_data or {})
        if res:
            return {"success": True, "remote": True, "result": res}

        # Apply state changes to mock store
        entity_id = (service_data or {}).get("entity_id")
        if entity_id and entity_id in self._mock_states:
            if service == "turn_on":
                self._mock_states[entity_id]["state"] = "on"
            elif service == "turn_off":
                self._mock_states[entity_id]["state"] = "off"
            elif service == "toggle":
                cur = self._mock_states[entity_id]["state"]
                self._mock_states[entity_id]["state"] = "off" if cur == "on" else "on"

        return {"success": True, "remote": False, "call": call_record}


class AutomationRuleEngine:
    """Event-condition-action automation processor for smart environment rules and scenes."""

    def __init__(self, ha_client: HomeAssistantClient, mqtt_client: MQTTClientAdapter):
        self.ha = ha_client
        self.mqtt = mqtt_client
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._scenes: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_scenes()

    def _initialize_default_scenes(self):
        self._scenes = {
            "Focus Mode": {
                "light.studio_desk": {"state": "on", "attributes": {"brightness": 255, "rgb_color": [0, 240, 255]}},
                "switch.fan": {"state": "on"},
                "climate.studio": {"state": "cool", "attributes": {"temperature": 21.0}},
            },
            "Cinema Mode": {
                "light.studio_desk": {"state": "on", "attributes": {"brightness": 30, "rgb_color": [40, 0, 100]}},
                "switch.fan": {"state": "off"},
            },
            "Night Off": {
                "light.studio_desk": {"state": "off"},
                "switch.fan": {"state": "off"},
            }
        }

    def register_rule(
        self,
        rule_id: str,
        trigger_channel: str,
        condition: Callable[[float], bool],
        action: Callable[[], None],
        description: str = ""
    ):
        """Registers a reactive trigger rule."""
        self._rules[rule_id] = {
            "channel": trigger_channel,
            "condition": condition,
            "action": action,
            "description": description,
            "last_triggered": 0.0
        }

    def evaluate(self, channel: str, value: float) -> int:
        """Evaluates rules bound to the updated telemetry channel."""
        triggered = 0
        now = time.time()
        for rule_id, rule in self._rules.items():
            if rule["channel"] == channel:
                # 5 second debounce between rule firings
                if (now - rule["last_triggered"]) >= 5.0:
                    if rule["condition"](value):
                        rule["last_triggered"] = now
                        try:
                            rule["action"]()
                            triggered += 1
                        except Exception:
                            pass
        return triggered

    def activate_scene(self, scene_name: str) -> Dict[str, Any]:
        """Activates a multi-device lighting and environmental preset."""
        scene = self._scenes.get(scene_name)
        if not scene:
            return {"success": False, "error": f"Scene '{scene_name}' not defined"}

        applied = []
        for entity_id, target in scene.items():
            state = target.get("state", "on")
            attrs = target.get("attributes", {})
            self.ha.set_state(entity_id, state=state, attributes=attrs)
            applied.append({"entity_id": entity_id, "state": state})

        # Publish scene event via MQTT
        self.mqtt.publish(f"jarvis/scene/{scene_name.lower().replace(' ', '_')}", {"status": "activated"})

        return {"success": True, "scene": scene_name, "applied_entities": applied}
