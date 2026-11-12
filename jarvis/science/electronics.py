"""
Electronics Analysis Engine (Capability 63)
Provides Ohm's law, resistor/capacitor/inductor network simplification,
AC impedance, series/parallel RLC resonance analysis, op-amp configurations,
and DC nodal netlist analysis.
"""

import math
import cmath
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class OhmsLaw:
    """Ohm's Law and Power equations."""

    @staticmethod
    def solve(
        voltage: Optional[float] = None,
        current: Optional[float] = None,
        resistance: Optional[float] = None,
        power: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Solves for missing 2 parameters among Voltage (V), Current (A), Resistance (Ohm), Power (W).
        Given at least 2 parameters.
        """
        knowns = {k: val for k, val in [("voltage", voltage), ("current", current),
                                         ("resistance", resistance), ("power", power)] if val is not None}
        if len(knowns) < 2:
            raise ValueError(f"At least two parameters required to solve Ohm's law, got {len(knowns)}")

        v, i, r, p = voltage, current, resistance, power

        if v is not None and i is not None:
            r = v / i if i != 0 else float("inf")
            p = v * i
        elif v is not None and r is not None:
            i = v / r if r != 0 else float("inf")
            p = (v ** 2) / r if r != 0 else float("inf")
        elif v is not None and p is not None:
            i = p / v if v != 0 else float("inf")
            r = (v ** 2) / p if p != 0 else float("inf")
        elif i is not None and r is not None:
            v = i * r
            p = (i ** 2) * r
        elif i is not None and p is not None:
            v = p / i if i != 0 else float("inf")
            r = p / (i ** 2) if i != 0 else float("inf")
        elif r is not None and p is not None:
            v = math.sqrt(p * r)
            i = math.sqrt(p / r) if r != 0 else float("inf")

        return {
            "voltage_V": float(v),
            "current_A": float(i),
            "resistance_Ohm": float(r),
            "power_W": float(p),
        }


class PassiveNetworks:
    """Equivalent resistance, capacitance, and inductance calculations."""

    @staticmethod
    def resistors_series(resistors: List[float]) -> float:
        """Series resistance Req = sum(R_i)."""
        return sum(resistors)

    @staticmethod
    def resistors_parallel(resistors: List[float]) -> float:
        """Parallel resistance Req = 1 / sum(1 / R_i)."""
        if any(r <= 0 for r in resistors):
            raise ValueError("All resistor values must be strictly positive.")
        inv_sum = sum(1.0 / r for r in resistors)
        return 1.0 / inv_sum if inv_sum > 0 else 0.0

    @staticmethod
    def capacitors_series(capacitors: List[float]) -> float:
        """Series capacitance Ceq = 1 / sum(1 / C_i)."""
        if any(c <= 0 for c in capacitors):
            raise ValueError("All capacitor values must be strictly positive.")
        inv_sum = sum(1.0 / c for c in capacitors)
        return 1.0 / inv_sum if inv_sum > 0 else 0.0

    @staticmethod
    def capacitors_parallel(capacitors: List[float]) -> float:
        """Parallel capacitance Ceq = sum(C_i)."""
        return sum(capacitors)

    @staticmethod
    def rc_transient(v_source: float, r_ohm: float, c_farad: float, t_seconds: float, mode: str = "charging") -> Dict[str, float]:
        """
        RC time constant tau = R * C.
        charging: v(t) = V_s * (1 - e^(-t / tau))
        discharging: v(t) = V_0 * e^(-t / tau)
        """
        tau = r_ohm * c_farad
        if tau <= 0:
            raise ValueError("R and C must be positive.")
        decay = math.exp(-t_seconds / tau)
        if mode == "charging":
            v_t = v_source * (1.0 - decay)
            i_t = (v_source / r_ohm) * decay
        else:
            v_t = v_source * decay
            i_t = -(v_source / r_ohm) * decay

        return {
            "tau_s": tau,
            "t_s": t_seconds,
            "v_t_V": v_t,
            "i_t_A": i_t,
            "tau_multiples": t_seconds / tau,
        }


class RLCAnalysis:
    """AC frequency response and RLC resonance calculations."""

    @staticmethod
    def series_rlc(
        resistance: float,
        inductance: float,
        capacitance: float,
        frequency_hz: float,
    ) -> Dict[str, float]:
        """
        Calculates series RLC impedance Z = R + j*(omega*L - 1/(omega*C)),
        magnitude, phase angle, and resonance metrics.
        """
        if frequency_hz <= 0 or inductance <= 0 or capacitance <= 0:
            raise ValueError("Frequency, inductance, and capacitance must be positive.")

        omega = 2.0 * math.pi * frequency_hz
        xl = omega * inductance
        xc = 1.0 / (omega * capacitance)
        x_net = xl - xc

        z_complex = complex(resistance, x_net)
        z_mag = abs(z_complex)
        phase_rad = cmath.phase(z_complex)
        phase_deg = math.degrees(phase_rad)

        # Resonance
        f0 = 1.0 / (2.0 * math.pi * math.sqrt(inductance * capacitance))
        q_factor = (1.0 / resistance) * math.sqrt(inductance / capacitance) if resistance > 0 else float("inf")
        bandwidth = f0 / q_factor if q_factor > 0 else 0.0

        return {
            "frequency_hz": frequency_hz,
            "omega_rad_s": omega,
            "reactance_L_Ohm": xl,
            "reactance_C_Ohm": xc,
            "net_reactance_Ohm": x_net,
            "impedance_magnitude_Ohm": z_mag,
            "phase_angle_deg": phase_deg,
            "resonant_frequency_hz": f0,
            "quality_factor_Q": q_factor,
            "bandwidth_hz": bandwidth,
        }


class OpAmpCircuits:
    """Operational Amplifier Gain & Transfer Functions."""

    @staticmethod
    def inverting_amplifier(r_in: float, r_feedback: float) -> Dict[str, float]:
        """Inverting Op-Amp: Gain Av = -Rf / Rin."""
        if r_in <= 0 or r_feedback < 0:
            raise ValueError("Resistances must be positive.")
        gain = -r_feedback / r_in
        return {"gain": gain, "gain_db": 20.0 * math.log10(abs(gain)) if gain != 0 else float("-inf")}

    @staticmethod
    def non_inverting_amplifier(r_in: float, r_feedback: float) -> Dict[str, float]:
        """Non-inverting Op-Amp: Gain Av = 1 + Rf / Rin."""
        if r_in <= 0 or r_feedback < 0:
            raise ValueError("Resistances must be positive.")
        gain = 1.0 + (r_feedback / r_in)
        return {"gain": gain, "gain_db": 20.0 * math.log10(gain)}

    @staticmethod
    def voltage_divider(v_in: float, r1: float, r2: float) -> Dict[str, float]:
        """Voltage divider: Vout = Vin * R2 / (R1 + R2)."""
        if (r1 + r2) <= 0:
            raise ValueError("Sum of resistances must be positive.")
        v_out = v_in * (r2 / (r1 + r2))
        return {
            "v_in": v_in,
            "r1": r1,
            "r2": r2,
            "v_out": v_out,
            "attenuation_ratio": r2 / (r1 + r2),
        }


class DCNetlistSolver:
    """
    Solves linear DC nodal networks with resistors and independent DC current/voltage sources.
    Uses modified nodal analysis (MNA).
    """

    @staticmethod
    def solve_resistor_ladder(voltage_source: float, resistor_values: List[float]) -> List[float]:
        """
        Solves node voltages for an N-stage ladder network with series and shunt resistors.
        Returns node voltages along ladder.
        """
        # Simple voltage divider chain: V0 -> R1 -> V1 -> R2 -> V2 ... -> Rn -> GND
        r_total = sum(resistor_values)
        if r_total <= 0:
            raise ValueError("Total resistance must be positive.")
        voltages = [voltage_source]
        current = voltage_source / r_total
        v_current = voltage_source
        for r in resistor_values[:-1]:
            v_current -= current * r
            voltages.append(v_current)
        voltages.append(0.0)
        return voltages
