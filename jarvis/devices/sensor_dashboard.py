"""
Capability 118: Sensor Dashboard
Aggregates telemetry from temperature, humidity, atmospheric pressure,
air quality (CO2, PM2.5, VOC), ambient light, sound, and motion sensors.
Calculates real-time statistics, trends, and threshold alerts.
"""

import math
import statistics
import time
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class SensorReading:
    sensor_id: str
    channel: str
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class SensorThresholds:
    warning_low: Optional[float] = None
    warning_high: Optional[float] = None
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None


class SensorChannel:
    """Maintains time-series data, statistical aggregates, and alert states for a single sensor channel."""

    def __init__(
        self,
        name: str,
        unit: str,
        max_history: int = 500,
        thresholds: Optional[SensorThresholds] = None
    ):
        self.name = name
        self.unit = unit
        self.max_history = max_history
        self.thresholds = thresholds or SensorThresholds()
        self._history: deque = deque(maxlen=max_history)

    def add_reading(self, value: float, timestamp: Optional[float] = None) -> SensorReading:
        reading = SensorReading(
            sensor_id=f"sensor-{self.name}",
            channel=self.name,
            value=float(value),
            unit=self.unit,
            timestamp=timestamp if timestamp is not None else time.time()
        )
        self._history.append(reading)
        return reading

    def get_latest(self) -> Optional[SensorReading]:
        return self._history[-1] if self._history else None

    def get_values(self) -> List[float]:
        return [r.value for r in self._history]

    def get_statistics(self) -> Dict[str, Any]:
        """Calculates min, max, average, standard deviation, and trend slope."""
        vals = self.get_values()
        if not vals:
            return {
                "count": 0,
                "latest": None,
                "min": None,
                "max": None,
                "mean": None,
                "std_dev": None,
                "median": None,
                "trend": "no_data"
            }

        mean_val = statistics.mean(vals)
        std_val = statistics.stdev(vals) if len(vals) > 1 else 0.0
        median_val = statistics.median(vals)

        # Trend estimation using first half vs second half difference
        trend = "stable"
        if len(vals) >= 4:
            half = len(vals) // 2
            first_avg = statistics.mean(vals[:half])
            second_avg = statistics.mean(vals[half:])
            diff = second_avg - first_avg
            # Use 1% of mean as threshold
            threshold = abs(mean_val) * 0.01 if mean_val != 0 else 0.1
            if diff > threshold:
                trend = "rising"
            elif diff < -threshold:
                trend = "falling"

        return {
            "count": len(vals),
            "latest": round(vals[-1], 2),
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
            "mean": round(mean_val, 2),
            "std_dev": round(std_val, 3),
            "median": round(median_val, 2),
            "trend": trend
        }

    def check_alert(self) -> Tuple[str, Optional[str]]:
        """Evaluates current reading against configured low/high threshold bounds."""
        latest = self.get_latest()
        if not latest:
            return ("NORMAL", None)

        val = latest.value
        t = self.thresholds

        if t.critical_high is not None and val >= t.critical_high:
            return ("CRITICAL_HIGH", f"{self.name} {val}{self.unit} exceeded critical high {t.critical_high}{self.unit}")
        if t.critical_low is not None and val <= t.critical_low:
            return ("CRITICAL_LOW", f"{self.name} {val}{self.unit} dropped below critical low {t.critical_low}{self.unit}")
        if t.warning_high is not None and val >= t.warning_high:
            return ("WARNING_HIGH", f"{self.name} {val}{self.unit} exceeded warning high {t.warning_high}{self.unit}")
        if t.warning_low is not None and val <= t.warning_low:
            return ("WARNING_LOW", f"{self.name} {val}{self.unit} dropped below warning low {t.warning_low}{self.unit}")

        return ("NORMAL", None)

    def detect_anomalies(self, z_thresh: float = 3.0) -> List[SensorReading]:
        """Identifies statistical outlier readings exceeding z_thresh standard deviations."""
        vals = self.get_values()
        if len(vals) < 5:
            return []
        mean_val = statistics.mean(vals)
        std_val = statistics.stdev(vals)
        if std_val == 0.0:
            return []

        anomalies = []
        for r in self._history:
            z = abs(r.value - mean_val) / std_val
            if z > z_thresh:
                anomalies.append(r)
        return anomalies


class SensorDashboard:
    """Unified telemetry hub managing environmental, optical, acoustic, and kinetic sensor channels."""

    def __init__(self):
        self._channels: Dict[str, SensorChannel] = {}
        self._initialize_default_channels()

    def _initialize_default_channels(self):
        channels_spec = [
            ("temperature", "°C", SensorThresholds(warning_low=18.0, warning_high=28.0, critical_low=14.0, critical_high=35.0)),
            ("humidity", "%", SensorThresholds(warning_low=30.0, warning_high=65.0, critical_low=20.0, critical_high=80.0)),
            ("pressure", "hPa", SensorThresholds(warning_low=980.0, warning_high=1030.0, critical_low=950.0, critical_high=1060.0)),
            ("co2", "ppm", SensorThresholds(warning_high=1000.0, critical_high=1500.0)),
            ("pm25", "µg/m³", SensorThresholds(warning_high=35.0, critical_high=75.0)),
            ("tvoc", "ppb", SensorThresholds(warning_high=220.0, critical_high=500.0)),
            ("light_lux", "lux", SensorThresholds(warning_low=100.0, warning_high=2500.0)),
            ("sound_db", "dB", SensorThresholds(warning_high=75.0, critical_high=85.0)),
            ("motion", "state", None),
        ]

        now = time.time()
        for name, unit, thresh in channels_spec:
            chan = SensorChannel(name=name, unit=unit, thresholds=thresh)
            self._channels[name] = chan

        # Seed realistic baseline readings
        self._seed_baseline(now)

    def _seed_baseline(self, now: float):
        seeds = {
            "temperature": [22.1, 22.2, 22.3, 22.4, 22.5],
            "humidity": [48.0, 48.5, 49.0, 49.2, 49.5],
            "pressure": [1013.2, 1013.1, 1013.0, 1012.8, 1012.9],
            "co2": [520, 525, 530, 528, 535],
            "pm25": [8.2, 8.5, 8.1, 8.4, 8.3],
            "tvoc": [65.0, 68.0, 66.0, 70.0, 69.0],
            "light_lux": [420.0, 425.0, 430.0, 435.0, 440.0],
            "sound_db": [42.5, 43.0, 41.8, 44.2, 43.1],
            "motion": [0.0, 0.0, 1.0, 1.0, 0.0],
        }
        for name, values in seeds.items():
            chan = self._channels.get(name)
            if chan:
                for i, v in enumerate(values):
                    chan.add_reading(v, timestamp=now - (5 - i) * 60)

    def ingest_reading(self, channel_name: str, value: float, unit: Optional[str] = None) -> SensorReading:
        """Ingests a telemetry reading for a designated channel, creating the channel if missing."""
        if channel_name not in self._channels:
            self._channels[channel_name] = SensorChannel(name=channel_name, unit=unit or "units")
        return self._channels[channel_name].add_reading(value)

    def get_channel(self, channel_name: str) -> Optional[SensorChannel]:
        return self._channels.get(channel_name)

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Collects all currently active warning and critical alerts across all sensors."""
        alerts = []
        for name, chan in self._channels.items():
            severity, message = chan.check_alert()
            if severity != "NORMAL":
                latest = chan.get_latest()
                alerts.append({
                    "channel": name,
                    "severity": severity,
                    "message": message,
                    "value": latest.value if latest else None,
                    "unit": chan.unit,
                    "timestamp": latest.timestamp if latest else time.time()
                })
        return alerts

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Builds complete aggregated sensor snapshot for telemetry widgets."""
        channels_data = {}
        for name, chan in self._channels.items():
            latest = chan.get_latest()
            severity, alert_msg = chan.check_alert()
            channels_data[name] = {
                "unit": chan.unit,
                "latest_value": latest.value if latest else None,
                "timestamp": latest.timestamp if latest else None,
                "statistics": chan.get_statistics(),
                "status": severity,
                "alert": alert_msg,
            }

        active_alerts = self.get_active_alerts()

        return {
            "status": "alert" if any(a["severity"].startswith("CRITICAL") for a in active_alerts) else ("warning" if active_alerts else "nominal"),
            "channel_count": len(self._channels),
            "channels": channels_data,
            "active_alerts_count": len(active_alerts),
            "active_alerts": active_alerts
        }
