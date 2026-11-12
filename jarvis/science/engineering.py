"""
Engineering Calculations Engine (Capability 74)
Provides high-precision dimensional unit conversions, mechanics of materials
(axial stress/strain, torsional shear, factor of safety, thermal expansion),
area moments of inertia for standard cross-sections, and beam deflection/bending stress calculations.
"""

import math
from typing import Dict, List, Optional, Tuple, Union


class UnitConverter:
    """High-precision conversion across physical engineering dimensions."""

    # Base SI conversions
    _LENGTH_TO_M = {
        "m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001, "um": 1e-6, "nm": 1e-9,
        "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344, "nmi": 1852.0,
    }

    _MASS_TO_KG = {
        "kg": 1.0, "g": 0.001, "mg": 1e-6, "lb": 0.45359237, "oz": 0.028349523125,
        "ton_metric": 1000.0, "ton_us": 907.18474,
    }

    _FORCE_TO_N = {
        "n": 1.0, "kn": 1000.0, "mn": 1e6, "lbf": 4.4482216152605, "dyn": 1e-5,
    }

    _PRESSURE_TO_PA = {
        "pa": 1.0, "kpa": 1000.0, "mpa": 1e6, "gpa": 1e9, "bar": 1e5,
        "psi": 6894.757293168, "ksi": 6894757.293168, "atm": 101325.0, "torr": 133.3223684,
    }

    _ENERGY_TO_J = {
        "j": 1.0, "kj": 1000.0, "mj": 1e6, "cal": 4.184, "kcal": 4184.0,
        "btu": 1055.05585, "kwh": 3.6e6, "ft_lbf": 1.3558179483314, "ev": 1.602176634e-19,
    }

    _POWER_TO_W = {
        "w": 1.0, "kw": 1000.0, "mw": 1e6, "hp": 745.69987158227022, "ft_lbf_s": 1.3558179483314,
    }

    @staticmethod
    def convert_length(value: float, from_unit: str, to_unit: str) -> float:
        f = from_unit.lower()
        t = to_unit.lower()
        if f not in UnitConverter._LENGTH_TO_M or t not in UnitConverter._LENGTH_TO_M:
            raise ValueError(f"Unknown length unit: {from_unit} or {to_unit}")
        meters = value * UnitConverter._LENGTH_TO_M[f]
        return meters / UnitConverter._LENGTH_TO_M[t]

    @staticmethod
    def convert_mass(value: float, from_unit: str, to_unit: str) -> float:
        f = from_unit.lower()
        t = to_unit.lower()
        if f not in UnitConverter._MASS_TO_KG or t not in UnitConverter._MASS_TO_KG:
            raise ValueError(f"Unknown mass unit: {from_unit} or {to_unit}")
        kg = value * UnitConverter._MASS_TO_KG[f]
        return kg / UnitConverter._MASS_TO_KG[t]

    @staticmethod
    def convert_force(value: float, from_unit: str, to_unit: str) -> float:
        f = from_unit.lower()
        t = to_unit.lower()
        if f not in UnitConverter._FORCE_TO_N or t not in UnitConverter._FORCE_TO_N:
            raise ValueError(f"Unknown force unit: {from_unit} or {to_unit}")
        n = value * UnitConverter._FORCE_TO_N[f]
        return n / UnitConverter._FORCE_TO_N[t]

    @staticmethod
    def convert_pressure(value: float, from_unit: str, to_unit: str) -> float:
        f = from_unit.lower()
        t = to_unit.lower()
        if f not in UnitConverter._PRESSURE_TO_PA or t not in UnitConverter._PRESSURE_TO_PA:
            raise ValueError(f"Unknown pressure unit: {from_unit} or {to_unit}")
        pa = value * UnitConverter._PRESSURE_TO_PA[f]
        return pa / UnitConverter._PRESSURE_TO_PA[t]

    @staticmethod
    def convert_power(value: float, from_unit: str, to_unit: str) -> float:
        f = from_unit.lower()
        t = to_unit.lower()
        if f not in UnitConverter._POWER_TO_W or t not in UnitConverter._POWER_TO_W:
            raise ValueError(f"Unknown power unit: {from_unit} or {to_unit}")
        w = value * UnitConverter._POWER_TO_W[f]
        return w / UnitConverter._POWER_TO_W[t]

    @staticmethod
    def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
        f = from_unit.upper()
        t = to_unit.upper()
        # To Kelvin
        if f == "K":
            k = value
        elif f == "C":
            k = value + 273.15
        elif f == "F":
            k = (value - 32.0) * (5.0 / 9.0) + 273.15
        elif f == "R":
            k = value * (5.0 / 9.0)
        else:
            raise ValueError(f"Unknown temperature unit: {from_unit}")

        # From Kelvin
        if t == "K":
            return k
        elif t == "C":
            return k - 273.15
        elif t == "F":
            return (k - 273.15) * (9.0 / 5.0) + 32.0
        elif t == "R":
            return k * (9.0 / 5.0)
        else:
            raise ValueError(f"Unknown temperature unit: {to_unit}")


class MechanicsOfMaterials:
    """Stress, strain, safety factors, and cross-section properties."""

    @staticmethod
    def axial_stress_strain(
        force_n: float,
        area_m2: float,
        original_length_m: float,
        youngs_modulus_pa: float,
        yield_strength_pa: Optional[float] = None,
    ) -> Dict[str, float]:
        """Calculates normal stress, axial strain, total elongation, and Factor of Safety."""
        if area_m2 <= 0 or original_length_m <= 0 or youngs_modulus_pa <= 0:
            raise ValueError("Area, length, and Young's modulus must be positive.")

        stress_pa = force_n / area_m2
        strain = stress_pa / youngs_modulus_pa
        elongation_m = strain * original_length_m

        res = {
            "stress_pa": stress_pa,
            "stress_mpa": stress_pa / 1e6,
            "strain": strain,
            "elongation_m": elongation_m,
            "elongation_mm": elongation_m * 1000.0,
        }

        if yield_strength_pa and yield_strength_pa > 0:
            fos = yield_strength_pa / abs(stress_pa) if stress_pa != 0 else float("inf")
            res["factor_of_safety"] = fos
            res["yield_exceeded"] = abs(stress_pa) > yield_strength_pa

        return res

    @staticmethod
    def rectangular_cross_section(width_m: float, height_m: float) -> Dict[str, float]:
        """Calculates area, centroid, and area moments of inertia (Ix, Iy) for solid rectangle."""
        area = width_m * height_m
        ix = (width_m * (height_m ** 3)) / 12.0
        iy = (height_m * (width_m ** 3)) / 12.0
        return {"area_m2": area, "ix_m4": ix, "iy_m4": iy, "c_neutral_axis_m": height_m / 2.0}

    @staticmethod
    def circular_cross_section(diameter_m: float) -> Dict[str, float]:
        """Calculates area and area moment of inertia for solid circle."""
        r = diameter_m / 2.0
        area = math.pi * (r ** 2)
        ix = (math.pi * (diameter_m ** 4)) / 64.0
        polar_j = (math.pi * (diameter_m ** 4)) / 32.0
        return {"area_m2": area, "ix_m4": ix, "iy_m4": ix, "polar_j_m4": polar_j, "c_neutral_axis_m": r}


class BeamDeflectionSolver:
    """Calculates maximum deflection and bending stress for classic beam cases."""

    @staticmethod
    def cantilever_point_load(
        load_n: float,
        length_m: float,
        youngs_modulus_pa: float,
        inertia_m4: float,
        c_extreme_fiber_m: float,
    ) -> Dict[str, float]:
        """
        Cantilever beam with point load P at free end:
        delta_max = P * L^3 / (3 * E * I)
        M_max = P * L
        sigma_max = M_max * c / I
        """
        ei = youngs_modulus_pa * inertia_m4
        if ei <= 0:
            raise ValueError("E and I must be positive.")

        delta_max = (load_n * (length_m ** 3)) / (3.0 * ei)
        m_max = load_n * length_m
        bending_stress = (m_max * c_extreme_fiber_m) / inertia_m4

        return {
            "load_n": load_n,
            "length_m": length_m,
            "max_deflection_m": delta_max,
            "max_deflection_mm": delta_max * 1000.0,
            "max_bending_moment_nm": m_max,
            "max_bending_stress_pa": bending_stress,
            "max_bending_stress_mpa": bending_stress / 1e6,
        }

    @staticmethod
    def simply_supported_center_load(
        load_n: float,
        length_m: float,
        youngs_modulus_pa: float,
        inertia_m4: float,
        c_extreme_fiber_m: float,
    ) -> Dict[str, float]:
        """
        Simply supported beam with point load P at center:
        delta_max = P * L^3 / (48 * E * I)
        M_max = P * L / 4
        sigma_max = M_max * c / I
        """
        ei = youngs_modulus_pa * inertia_m4
        if ei <= 0:
            raise ValueError("E and I must be positive.")

        delta_max = (load_n * (length_m ** 3)) / (48.0 * ei)
        m_max = (load_n * length_m) / 4.0
        bending_stress = (m_max * c_extreme_fiber_m) / inertia_m4

        return {
            "load_n": load_n,
            "length_m": length_m,
            "max_deflection_m": delta_max,
            "max_deflection_mm": delta_max * 1000.0,
            "max_bending_moment_nm": m_max,
            "max_bending_stress_pa": bending_stress,
            "max_bending_stress_mpa": bending_stress / 1e6,
        }
