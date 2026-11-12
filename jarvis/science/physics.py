"""
Physics Analysis Engine (Capability 62)
Provides classical mechanics, kinematics, dynamics, gravitation, circular motion,
work-energy-momentum collisions, and thermodynamics calculations.
"""

import math
from typing import Dict, List, Optional, Tuple, Union

# Fundamental Physical Constants
G_CONSTANT = 6.67430e-11        # m^3 / (kg * s^2)
STANDARD_GRAVITY = 9.80665      # m / s^2
IDEAL_GAS_CONSTANT_R = 8.314462618 # J / (mol * K)
STEFAN_BOLTZMANN = 5.670374419e-8 # W / (m^2 * K^4)


class KinematicsSolver:
    """1D and 2D Kinematics calculations."""

    @staticmethod
    def solve_1d(
        u: Optional[float] = None,
        v: Optional[float] = None,
        a: Optional[float] = None,
        t: Optional[float] = None,
        s: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Solves 1D constant acceleration kinematic equations:
        v = u + a*t
        s = u*t + 0.5*a*t^2
        v^2 = u^2 + 2*a*s
        s = 0.5 * (u + v) * t
        Given any 3 parameters, calculates the missing 2.
        """
        # Count knowns
        knowns = {k: val for k, val in [("u", u), ("v", v), ("a", a), ("t", t), ("s", s)] if val is not None}
        if len(knowns) < 3:
            raise ValueError(f"Need at least 3 known kinematic parameters, got {len(knowns)}: {list(knowns.keys())}")

        # Iterate until all 5 solved
        res = dict(knowns)
        for _ in range(5):
            # If u, a, t known
            if "u" in res and "a" in res and "t" in res:
                if "v" not in res:
                    res["v"] = res["u"] + res["a"] * res["t"]
                if "s" not in res:
                    res["s"] = res["u"] * res["t"] + 0.5 * res["a"] * (res["t"] ** 2)

            # If u, v, t known
            if "u" in res and "v" in res and "t" in res:
                if res["t"] != 0:
                    if "a" not in res:
                        res["a"] = (res["v"] - res["u"]) / res["t"]
                    if "s" not in res:
                        res["s"] = 0.5 * (res["u"] + res["v"]) * res["t"]

            # If u, v, a known
            if "u" in res and "v" in res and "a" in res:
                if res["a"] != 0:
                    if "t" not in res:
                        res["t"] = (res["v"] - res["u"]) / res["a"]
                    if "s" not in res:
                        res["s"] = (res["v"] ** 2 - res["u"] ** 2) / (2.0 * res["a"])

            # If v, a, t known
            if "v" in res and "a" in res and "t" in res:
                if "u" not in res:
                    res["u"] = res["v"] - res["a"] * res["t"]
                if "s" not in res and "u" in res:
                    res["s"] = res["u"] * res["t"] + 0.5 * res["a"] * (res["t"] ** 2)

            # If u, a, s known
            if "u" in res and "a" in res and "s" in res and "v" not in res:
                v_sq = res["u"] ** 2 + 2.0 * res["a"] * res["s"]
                if v_sq >= 0:
                    res["v"] = math.sqrt(v_sq)

            # If s, v, a known
            if "s" in res and "v" in res and "a" in res and "u" not in res:
                u_sq = res["v"] ** 2 - 2.0 * res["a"] * res["s"]
                if u_sq >= 0:
                    res["u"] = math.sqrt(u_sq)

        return res

    @staticmethod
    def projectile_motion(
        v0: float,
        angle_deg: float,
        y0: float = 0.0,
        g: float = STANDARD_GRAVITY,
        num_trajectory_points: int = 50,
    ) -> Dict[str, Union[float, List[Dict[str, float]]]]:
        """
        Calculates 2D projectile trajectory in vacuum under uniform gravity g.
        Returns time of flight, maximum height, horizontal range, and trajectory coordinates.
        """
        if v0 < 0:
            raise ValueError("Initial velocity v0 must be non-negative.")
        if g <= 0:
            raise ValueError("Gravity g must be positive.")

        theta = math.radians(angle_deg)
        vx = v0 * math.cos(theta)
        vy0 = v0 * math.sin(theta)

        # Time to apex
        t_apex = max(0.0, vy0 / g)
        h_max = y0 + (vy0 ** 2) / (2.0 * g)

        # Total time of flight (when y(t) = 0): y0 + vy0*t - 0.5*g*t^2 = 0
        # -0.5*g*t^2 + vy0*t + y0 = 0 -> 0.5*g*t^2 - vy0*t - y0 = 0
        discriminant = vy0 ** 2 + 2.0 * g * y0
        if discriminant < 0:
            t_flight = 0.0
        else:
            t_flight = (vy0 + math.sqrt(discriminant)) / g

        total_range = vx * t_flight

        # Impact velocities
        vy_impact = vy0 - g * t_flight
        v_impact = math.sqrt(vx ** 2 + vy_impact ** 2)
        impact_angle_deg = math.degrees(math.atan2(vy_impact, vx))

        # Sample trajectory
        trajectory = []
        n_pts = max(2, num_trajectory_points)
        for i in range(n_pts):
            t = (t_flight * i) / (n_pts - 1) if t_flight > 0 else 0.0
            x_pos = vx * t
            y_pos = max(0.0, y0 + vy0 * t - 0.5 * g * (t ** 2))
            cur_vy = vy0 - g * t
            trajectory.append({
                "t": round(t, 4),
                "x": round(x_pos, 4),
                "y": round(y_pos, 4),
                "vx": round(vx, 4),
                "vy": round(cur_vy, 4),
            })

        return {
            "v0": v0,
            "angle_deg": angle_deg,
            "y0": y0,
            "t_flight": t_flight,
            "t_apex": t_apex,
            "max_height": h_max,
            "range": total_range,
            "impact_speed": v_impact,
            "impact_angle_deg": impact_angle_deg,
            "trajectory": trajectory,
        }


class DynamicsSolver:
    """Classical Dynamics, Newton's Laws, Momentum, Collisions, and Work-Energy."""

    @staticmethod
    def inclined_plane(
        mass_kg: float,
        angle_deg: float,
        mu_k: float = 0.0,
        mu_s: float = 0.0,
        g: float = STANDARD_GRAVITY,
    ) -> Dict[str, float]:
        """
        Calculates forces on an object on an inclined plane.
        Checks if static friction holds, or calculates acceleration.
        """
        theta = math.radians(angle_deg)
        mg = mass_kg * g
        normal_force = mg * math.cos(theta)
        parallel_force = mg * math.sin(theta)
        max_static_friction = mu_s * normal_force

        if parallel_force <= max_static_friction:
            # Body remains static
            friction_force = parallel_force
            accel = 0.0
            status = "static"
        else:
            friction_force = mu_k * normal_force
            net_force = parallel_force - friction_force
            accel = net_force / mass_kg
            status = "sliding"

        return {
            "mass_kg": mass_kg,
            "angle_deg": angle_deg,
            "normal_force_N": normal_force,
            "parallel_force_N": parallel_force,
            "friction_force_N": friction_force,
            "net_force_N": mass_kg * accel,
            "acceleration_m_s2": accel,
            "status": status,
        }

    @staticmethod
    def work_energy(
        mass_kg: float,
        velocity: float,
        height: float = 0.0,
        spring_k: float = 0.0,
        spring_x: float = 0.0,
        g: float = STANDARD_GRAVITY,
    ) -> Dict[str, float]:
        """Calculates kinetic, gravitational potential, spring elastic, and total mechanical energy."""
        ke = 0.5 * mass_kg * (velocity ** 2)
        pe_grav = mass_kg * g * height
        pe_spring = 0.5 * spring_k * (spring_x ** 2)
        total = ke + pe_grav + pe_spring
        return {
            "kinetic_energy_J": ke,
            "gravitational_pe_J": pe_grav,
            "spring_pe_J": pe_spring,
            "total_mechanical_energy_J": total,
        }

    @staticmethod
    def collision_1d(
        m1: float,
        u1: float,
        m2: float,
        u2: float,
        elastic: bool = True,
    ) -> Dict[str, float]:
        """
        Simulates 1D collision between two bodies.
        If elastic=True, conserves kinetic energy and momentum.
        If elastic=False, completely inelastic collision (masses coalesce).
        """
        if m1 <= 0 or m2 <= 0:
            raise ValueError("Masses must be strictly positive.")

        p_initial = m1 * u1 + m2 * u2
        ke_initial = 0.5 * m1 * (u1 ** 2) + 0.5 * m2 * (u2 ** 2)

        if elastic:
            v1 = ((m1 - m2) * u1 + 2.0 * m2 * u2) / (m1 + m2)
            v2 = (2.0 * m1 * u1 + (m2 - m1) * u2) / (m1 + m2)
        else:
            v1 = (m1 * u1 + m2 * u2) / (m1 + m2)
            v2 = v1

        p_final = m1 * v1 + m2 * v2
        ke_final = 0.5 * m1 * (v1 ** 2) + 0.5 * m2 * (v2 ** 2)
        ke_loss = ke_initial - ke_final

        return {
            "v1": v1,
            "v2": v2,
            "p_initial": p_initial,
            "p_final": p_final,
            "ke_initial": ke_initial,
            "ke_final": ke_final,
            "ke_loss_J": ke_loss,
            "elastic": elastic,
        }


class GravitationAndOrbit:
    """Gravitation, circular motion, and Keplerian orbital mechanics."""

    @staticmethod
    def gravitational_force(m1: float, m2: float, r: float) -> float:
        """Newton's Law of Gravitation: F = G * m1 * m2 / r^2."""
        if r <= 0:
            raise ValueError("Distance r must be positive.")
        return G_CONSTANT * m1 * m2 / (r ** 2)

    @staticmethod
    def orbital_mechanics(central_mass_kg: float, orbital_radius_m: float) -> Dict[str, float]:
        """Calculates orbital speed, period, and escape velocity at radius r."""
        if central_mass_kg <= 0 or orbital_radius_m <= 0:
            raise ValueError("Mass and radius must be positive.")

        gm = G_CONSTANT * central_mass_kg
        v_orb = math.sqrt(gm / orbital_radius_m)
        v_esc = math.sqrt(2.0 * gm / orbital_radius_m)
        period = 2.0 * math.pi * math.sqrt((orbital_radius_m ** 3) / gm)

        return {
            "orbital_velocity_m_s": v_orb,
            "escape_velocity_m_s": v_esc,
            "orbital_period_s": period,
            "orbital_period_hours": period / 3600.0,
            "orbital_radius_m": orbital_radius_m,
        }


class ThermodynamicsEngine:
    """Thermodynamics, Ideal Gas, Heat Transfer, and Carnot Cycles."""

    @staticmethod
    def ideal_gas_law(
        P: Optional[float] = None,
        V: Optional[float] = None,
        n: Optional[float] = None,
        T: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Ideal gas law P * V = n * R * T.
        Solves for the one missing variable among (P in Pa, V in m^3, n in mol, T in Kelvin).
        """
        knowns = {k: val for k, val in [("P", P), ("V", V), ("n", n), ("T", T)] if val is not None}
        if len(knowns) != 3:
            raise ValueError(f"Exactly 3 parameters must be provided, got {len(knowns)}")

        R = IDEAL_GAS_CONSTANT_R
        res = dict(knowns)

        if "P" not in res:
            res["P"] = (res["n"] * R * res["T"]) / res["V"]
        elif "V" not in res:
            res["V"] = (res["n"] * R * res["T"]) / res["P"]
        elif "n" not in res:
            res["n"] = (res["P"] * res["V"]) / (R * res["T"])
        elif "T" not in res:
            res["T"] = (res["P"] * res["V"]) / (res["n"] * R)

        return res

    @staticmethod
    def heat_transfer_conduction(
        thermal_conductivity_k: float,
        area_m2: float,
        temp_hot_k: float,
        temp_cold_k: float,
        thickness_m: float,
    ) -> float:
        """Fourier's law of 1D thermal conduction: Q_dot = k * A * (T_hot - T_cold) / d (in Watts)."""
        if thickness_m <= 0:
            raise ValueError("Thickness must be positive.")
        return thermal_conductivity_k * area_m2 * (temp_hot_k - temp_cold_k) / thickness_m

    @staticmethod
    def carnot_efficiency(temp_cold_k: float, temp_hot_k: float) -> Dict[str, float]:
        """Calculates maximum theoretical thermal efficiency of a Carnot heat engine."""
        if temp_hot_k <= 0 or temp_cold_k <= 0:
            raise ValueError("Temperatures must be positive absolute Kelvin.")
        if temp_cold_k >= temp_hot_k:
            raise ValueError("Hot reservoir temperature must exceed cold reservoir temperature.")

        eta = 1.0 - (temp_cold_k / temp_hot_k)
        return {
            "efficiency": eta,
            "efficiency_percent": eta * 100.0,
            "temp_cold_k": temp_cold_k,
            "temp_hot_k": temp_hot_k,
        }
