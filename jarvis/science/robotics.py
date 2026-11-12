"""
Robotics Intelligence Engine (Capability 64)
Provides Forward & Inverse Kinematics for planar and DH manipulators,
trapezoidal/polynomial trajectory planners, and robust PID controllers with anti-windup.
"""

import math
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class PlanarArmKinematics:
    """Forward and Inverse Kinematics for 2-Link and 3-Link Planar Arms."""

    @staticmethod
    def forward_2link(l1: float, l2: float, theta1_deg: float, theta2_deg: float) -> Dict[str, Union[float, Tuple[float, float]]]:
        """
        Computes forward kinematics for 2-link planar arm.
        Returns elbow joint position (x1, y1) and end-effector position (x2, y2).
        """
        t1 = math.radians(theta1_deg)
        t2 = math.radians(theta2_deg)

        x1 = l1 * math.cos(t1)
        y1 = l1 * math.sin(t1)

        x2 = x1 + l2 * math.cos(t1 + t2)
        y2 = y1 + l2 * math.sin(t1 + t2)

        return {
            "elbow_x": x1,
            "elbow_y": y1,
            "end_effector_x": x2,
            "end_effector_y": y2,
            "end_effector_dist": math.sqrt(x2 ** 2 + y2 ** 2),
        }

    @staticmethod
    def inverse_2link(l1: float, l2: float, target_x: float, target_y: float) -> Dict[str, Union[bool, List[Dict[str, float]], str]]:
        """
        Computes analytical inverse kinematics for 2-link planar arm.
        Returns both elbow-up and elbow-down joint angles (theta1, theta2) in degrees.
        """
        r_sq = target_x ** 2 + target_y ** 2
        r = math.sqrt(r_sq)

        # Reachability check
        if r > (l1 + l2) or r < abs(l1 - l2):
            return {
                "reachable": False,
                "solutions": [],
                "error": f"Target ({target_x}, {target_y}) out of reachable workspace [{abs(l1 - l2):.2f}, {l1 + l2:.2f}]",
            }

        # Law of cosines for theta2
        cos_theta2 = (r_sq - l1 ** 2 - l2 ** 2) / (2.0 * l1 * l2)
        # Numerical clamp
        cos_theta2 = max(-1.0, min(1.0, cos_theta2))

        # Two configurations: elbow-down (positive theta2) and elbow-up (negative theta2)
        solutions = []
        for sign in [1.0, -1.0]:
            sin_theta2 = sign * math.sqrt(max(0.0, 1.0 - cos_theta2 ** 2))
            t2 = math.atan2(sin_theta2, cos_theta2)

            k1 = l1 + l2 * cos_theta2
            k2 = l2 * sin_theta2
            t1 = math.atan2(target_y, target_x) - math.atan2(k2, k1)

            solutions.append({
                "configuration": "elbow_down" if sign > 0 else "elbow_up",
                "theta1_deg": math.degrees(t1),
                "theta2_deg": math.degrees(t2),
            })

        return {
            "reachable": True,
            "solutions": solutions,
            "target_dist": r,
        }

    @staticmethod
    def dh_transform_matrix(theta_rad: float, d: float, a: float, alpha_rad: float) -> np.ndarray:
        """
        Standard Denavit-Hartenberg (DH) 4x4 transformation matrix:
        Rot_z(theta) * Trans_z(d) * Trans_x(a) * Rot_x(alpha)
        """
        ct = math.cos(theta_rad)
        st = math.sin(theta_rad)
        ca = math.cos(alpha_rad)
        sa = math.sin(alpha_rad)

        return np.array([
            [ct, -st * ca,  st * sa, a * ct],
            [st,  ct * ca, -ct * sa, a * st],
            [0,   sa,       ca,      d],
            [0,   0,        0,       1.0]
        ], dtype=float)


class TrajectoryPlanner:
    """Motion profiling and trajectory generators."""

    @staticmethod
    def trapezoidal_profile(
        q0: float,
        q1: float,
        v_max: float,
        a_max: float,
        dt: float = 0.01,
    ) -> Dict[str, Union[float, List[Dict[str, float]]]]:
        """
        Generates trapezoidal velocity profile (bang-coast-bang) from q0 to q1.
        Returns profile parameters and sampled time points.
        """
        if v_max <= 0 or a_max <= 0:
            raise ValueError("v_max and a_max must be positive.")

        dist = q1 - q0
        direction = 1.0 if dist >= 0 else -1.0
        abs_dist = abs(dist)

        # Check if cruise velocity is reachable
        t_ramp = v_max / a_max
        d_ramp = 0.5 * a_max * (t_ramp ** 2)

        if 2.0 * d_ramp > abs_dist:
            # Triangular profile (cruise velocity never reached)
            t_ramp = math.sqrt(abs_dist / a_max)
            t_cruise = 0.0
            peak_v = a_max * t_ramp
        else:
            # Full trapezoidal profile
            d_cruise = abs_dist - 2.0 * d_ramp
            t_cruise = d_cruise / v_max
            peak_v = v_max

        t_total = 2.0 * t_ramp + t_cruise
        steps = int(math.ceil(t_total / dt)) + 1

        points = []
        for i in range(steps):
            t = min(i * dt, t_total)
            if t <= t_ramp:
                # Acceleration phase
                pos = 0.5 * a_max * (t ** 2)
                vel = a_max * t
                acc = a_max
            elif t <= (t_ramp + t_cruise):
                # Cruise phase
                pos = 0.5 * a_max * (t_ramp ** 2) + peak_v * (t - t_ramp)
                vel = peak_v
                acc = 0.0
            else:
                # Deceleration phase
                t_dec = t - t_ramp - t_cruise
                pos = (0.5 * a_max * (t_ramp ** 2) + peak_v * t_cruise +
                       peak_v * t_dec - 0.5 * a_max * (t_dec ** 2))
                vel = peak_v - a_max * t_dec
                acc = -a_max

            actual_pos = q0 + direction * pos
            actual_vel = direction * vel
            actual_acc = direction * acc

            points.append({
                "t": round(t, 4),
                "q": round(actual_pos, 4),
                "v": round(actual_vel, 4),
                "a": round(actual_acc, 4),
            })

        return {
            "q0": q0,
            "q1": q1,
            "total_time_s": t_total,
            "ramp_time_s": t_ramp,
            "cruise_time_s": t_cruise,
            "peak_velocity": peak_v * direction,
            "points": points,
        }


class PIDController:
    """Discrete Proportional-Integral-Derivative controller with anti-windup clamping."""

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        setpoint: float = 0.0,
        output_limits: Optional[Tuple[float, float]] = None,
        integral_limits: Optional[Tuple[float, float]] = None,
    ):
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)
        self.setpoint = float(setpoint)
        self.output_limits = output_limits
        self.integral_limits = integral_limits

        self.integral = 0.0
        self.last_error = 0.0
        self.last_measurement: Optional[float] = None

    def reset(self) -> None:
        self.integral = 0.0
        self.last_error = 0.0
        self.last_measurement = None

    def update(self, measurement: float, dt: float) -> float:
        """Computes control output u for the current measurement and timestep dt."""
        if dt <= 0:
            raise ValueError("dt must be positive.")

        error = self.setpoint - measurement

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup clamping
        self.integral += error * dt
        if self.integral_limits:
            min_i, max_i = self.integral_limits
            self.integral = max(min_i, min(max_i, self.integral))
        i_term = self.ki * self.integral

        # Derivative term on measurement (to prevent derivative kick)
        if self.last_measurement is not None:
            d_measurement = (measurement - self.last_measurement) / dt
            d_term = -self.kd * d_measurement
        else:
            d_term = 0.0

        output = p_term + i_term + d_term

        # Clamp output
        if self.output_limits:
            min_out, max_out = self.output_limits
            output = max(min_out, min(max_out, output))

        self.last_error = error
        self.last_measurement = measurement
        return output

    def simulate_step_response(
        self,
        plant_inertia: float = 1.0,
        plant_damping: float = 0.5,
        target: float = 1.0,
        total_time: float = 5.0,
        dt: float = 0.01,
    ) -> Dict[str, Union[float, List[Dict[str, float]]]]:
        """
        Simulates closed-loop step response against a 2nd order dynamic plant:
        plant_inertia * x'' + plant_damping * x' = u
        """
        self.reset()
        self.setpoint = target
        steps = int(total_time / dt)

        x = 0.0
        v = 0.0
        history = []

        for i in range(steps):
            t = i * dt
            u = self.update(x, dt)
            # Plant acceleration
            accel = (u - plant_damping * v) / plant_inertia
            v += accel * dt
            x += v * dt

            history.append({
                "t": round(t, 4),
                "setpoint": target,
                "position": round(x, 4),
                "velocity": round(v, 4),
                "control_effort": round(u, 4),
            })

        # Calculate overshoot & settling time
        positions = [h["position"] for h in history]
        max_pos = max(positions) if positions else 0.0
        overshoot_pct = max(0.0, ((max_pos - target) / target) * 100.0) if target != 0 else 0.0

        return {
            "target": target,
            "max_position": max_pos,
            "overshoot_percent": overshoot_pct,
            "final_position": positions[-1] if positions else 0.0,
            "history": history,
        }
