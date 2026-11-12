"""
Sensor Integration Engine (Capability 73)
Provides NMEA 0183 GPS sentence parsing ($GPRMC, $GPGGA) with XOR checksum verification,
IMU 6-DOF telemetry processing, complementary sensor fusion, 1D Kalman filtering,
and telemetry anomaly monitoring.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class NMEAParser:
    """NMEA 0183 GPS Sentence Parser ($GPRMC, $GPGGA)."""

    @staticmethod
    def verify_checksum(sentence: str) -> bool:
        """Verifies NMEA XOR checksum between '$' and '*'."""
        sentence = sentence.strip()
        if not sentence.startswith("$") or "*" not in sentence:
            return False
        content, cksum_str = sentence[1:].split("*", 1)
        calculated = 0
        for char in content:
            calculated ^= ord(char)
        try:
            expected = int(cksum_str[:2], 16)
            return calculated == expected
        except ValueError:
            return False

    @staticmethod
    def _convert_deg_min(coord_str: str, direction: str) -> float:
        """Converts DDMM.MMMM format to decimal degrees."""
        if not coord_str or not direction:
            return 0.0
        val = float(coord_str)
        deg = int(val / 100)
        minutes = val - (deg * 100)
        decimal = deg + (minutes / 60.0)
        if direction.upper() in ["S", "W"]:
            decimal = -decimal
        return decimal

    @staticmethod
    def parse_sentence(sentence: str) -> Dict[str, Any]:
        """Parses $GPRMC or $GPGGA NMEA sentence into structured data."""
        if not NMEAParser.verify_checksum(sentence):
            raise ValueError(f"Invalid NMEA sentence checksum: {sentence}")

        body = sentence.strip()[1:].split("*")[0]
        fields = body.split(",")
        talker_type = fields[0]

        if talker_type.endswith("RMC"):
            # Format: $GPRMC,utc,status,lat,NS,lon,EW,speed_knots,track,date,...
            status = fields[2]
            valid = (status == "A")
            lat = NMEAParser._convert_deg_min(fields[3], fields[4]) if valid else 0.0
            lon = NMEAParser._convert_deg_min(fields[5], fields[6]) if valid else 0.0
            speed_knots = float(fields[7]) if fields[7] and valid else 0.0
            track_deg = float(fields[8]) if fields[8] and valid else 0.0

            return {
                "type": "RMC",
                "valid": valid,
                "utc_time": fields[1],
                "latitude_deg": round(lat, 6),
                "longitude_deg": round(lon, 6),
                "speed_knots": speed_knots,
                "speed_kmh": round(speed_knots * 1.852, 2),
                "heading_deg": track_deg,
                "date": fields[9] if len(fields) > 9 else "",
            }

        elif talker_type.endswith("GGA"):
            # Format: $GPGGA,utc,lat,NS,lon,EW,quality,num_sats,hdop,alt,M,...
            quality = int(fields[6]) if fields[6] else 0
            valid = (quality > 0)
            lat = NMEAParser._convert_deg_min(fields[2], fields[3]) if valid else 0.0
            lon = NMEAParser._convert_deg_min(fields[4], fields[5]) if valid else 0.0
            sats = int(fields[7]) if fields[7] else 0
            hdop = float(fields[8]) if fields[8] else 99.0
            alt = float(fields[9]) if fields[9] else 0.0

            return {
                "type": "GGA",
                "valid": valid,
                "utc_time": fields[1],
                "fix_quality": quality,
                "latitude_deg": round(lat, 6),
                "longitude_deg": round(lon, 6),
                "satellites": sats,
                "hdop": hdop,
                "altitude_m": alt,
            }

        return {"type": talker_type, "raw_fields": fields}


class IMUSensorFusion:
    """IMU 6-DOF / 9-DOF telemetry and Complementary attitude filter."""

    def __init__(self, alpha: float = 0.98):
        self.alpha = alpha
        self.pitch_deg = 0.0
        self.roll_deg = 0.0

    def update_attitude(
        self,
        ax: float,
        ay: float,
        az: float,
        gx_deg_s: float,
        gy_deg_s: float,
        dt_s: float,
    ) -> Dict[str, float]:
        """
        Fuses 3-axis accelerometer and gyro rates to compute attitude (pitch, roll).
        Complementary filter: angle = alpha * (angle + gyro * dt) + (1 - alpha) * accel_angle
        """
        if dt_s <= 0:
            raise ValueError("dt_s must be positive.")

        # Accel tilt angles
        accel_roll_rad = math.atan2(ay, az)
        accel_pitch_rad = math.atan2(-ax, math.sqrt(ay ** 2 + az ** 2))

        accel_roll = math.degrees(accel_roll_rad)
        accel_pitch = math.degrees(accel_pitch_rad)

        # Complementary filter fusion
        self.roll_deg = self.alpha * (self.roll_deg + gx_deg_s * dt_s) + (1.0 - self.alpha) * accel_roll
        self.pitch_deg = self.alpha * (self.pitch_deg + gy_deg_s * dt_s) + (1.0 - self.alpha) * accel_pitch

        return {
            "roll_deg": round(self.roll_deg, 3),
            "pitch_deg": round(self.pitch_deg, 3),
            "accel_roll_deg": round(accel_roll, 3),
            "accel_pitch_deg": round(accel_pitch, 3),
        }


class KalmanFilter1D:
    """1D Linear Kalman Filter for scalar sensor state tracking (e.g. altitude, temperature)."""

    def __init__(self, process_noise_q: float = 1e-4, measurement_noise_r: float = 1e-2, initial_state: float = 0.0, initial_variance_p: float = 1.0):
        self.q = process_noise_q
        self.r = measurement_noise_r
        self.x = initial_state
        self.p = initial_variance_p

    def update(self, measurement: float) -> Tuple[float, float]:
        """
        Performs predict and update step with incoming scalar measurement.
        Returns (estimated_state, updated_covariance).
        """
        # Predict step
        p_pred = self.p + self.q

        # Update step
        k_gain = p_pred / (p_pred + self.r)
        self.x = self.x + k_gain * (measurement - self.x)
        self.p = (1.0 - k_gain) * p_pred

        return (self.x, self.p)


class TelemetryMonitor:
    """Monitors telemetry stream against configurable threshold limits."""

    def __init__(self):
        self.thresholds: Dict[str, Tuple[float, float]] = {}  # channel -> (min, max)
        self.alerts: List[Dict[str, Any]] = []

    def set_channel_limits(self, channel: str, min_val: float, max_val: float) -> None:
        self.thresholds[channel] = (min_val, max_val)

    def check_telemetry(self, timestamp: float, readings: Dict[str, float]) -> List[Dict[str, Any]]:
        """Checks incoming readings against defined safe envelope."""
        new_alerts = []
        for ch, val in readings.items():
            if ch in self.thresholds:
                min_v, max_v = self.thresholds[ch]
                if val < min_v:
                    alert = {"timestamp": timestamp, "channel": ch, "value": val, "limit": min_v, "condition": "UNDERFLOW"}
                    self.alerts.append(alert)
                    new_alerts.append(alert)
                elif val > max_v:
                    alert = {"timestamp": timestamp, "channel": ch, "value": val, "limit": max_v, "condition": "OVERFLOW"}
                    self.alerts.append(alert)
                    new_alerts.append(alert)
        return new_alerts
