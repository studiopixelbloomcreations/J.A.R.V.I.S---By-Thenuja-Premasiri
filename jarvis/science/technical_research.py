"""
Technical Research Engine (Capability 75)
Provides standard engineering materials database, ISO Metric & ANSI Unified fastener thread tables,
American Wire Gauge (AWG) specifications, and automated wire sizing calculators.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

MATERIALS_DATABASE: Dict[str, Dict[str, Any]] = {
    "astm_a36_steel": {
        "name": "ASTM A36 Structural Carbon Steel",
        "category": "Metal / Ferrous",
        "density_kg_m3": 7850.0,
        "elastic_modulus_gpa": 200.0,
        "shear_modulus_gpa": 79.3,
        "yield_strength_mpa": 250.0,
        "ultimate_tensile_strength_mpa": 400.0,
        "elongation_pct": 20.0,
        "poisson_ratio": 0.26,
        "thermal_conductivity_w_m_k": 51.9,
        "cte_ppm_k": 12.0,
    },
    "aisi_304_stainless": {
        "name": "AISI 304 Austenitic Stainless Steel",
        "category": "Metal / Ferrous",
        "density_kg_m3": 8000.0,
        "elastic_modulus_gpa": 193.0,
        "shear_modulus_gpa": 77.0,
        "yield_strength_mpa": 215.0,
        "ultimate_tensile_strength_mpa": 505.0,
        "elongation_pct": 70.0,
        "poisson_ratio": 0.29,
        "thermal_conductivity_w_m_k": 16.2,
        "cte_ppm_k": 17.3,
    },
    "al_6061_t6": {
        "name": "Aluminum 6061-T6 Alloy",
        "category": "Metal / Non-Ferrous",
        "density_kg_m3": 2700.0,
        "elastic_modulus_gpa": 68.9,
        "shear_modulus_gpa": 26.0,
        "yield_strength_mpa": 276.0,
        "ultimate_tensile_strength_mpa": 310.0,
        "elongation_pct": 12.0,
        "poisson_ratio": 0.33,
        "thermal_conductivity_w_m_k": 167.0,
        "cte_ppm_k": 23.6,
    },
    "ti_6al_4v_grade5": {
        "name": "Titanium Ti-6Al-4V (Grade 5)",
        "category": "Metal / Non-Ferrous",
        "density_kg_m3": 4430.0,
        "elastic_modulus_gpa": 113.8,
        "shear_modulus_gpa": 44.0,
        "yield_strength_mpa": 880.0,
        "ultimate_tensile_strength_mpa": 950.0,
        "elongation_pct": 14.0,
        "poisson_ratio": 0.342,
        "thermal_conductivity_w_m_k": 6.7,
        "cte_ppm_k": 8.6,
    },
    "copper_c11000": {
        "name": "Copper C11000 (Electrolytic Tough Pitch)",
        "category": "Metal / Non-Ferrous",
        "density_kg_m3": 8940.0,
        "elastic_modulus_gpa": 117.0,
        "shear_modulus_gpa": 44.0,
        "yield_strength_mpa": 69.0,
        "ultimate_tensile_strength_mpa": 220.0,
        "elongation_pct": 45.0,
        "poisson_ratio": 0.34,
        "thermal_conductivity_w_m_k": 390.0,
        "cte_ppm_k": 16.5,
    },
    "abs_plastic": {
        "name": "Acrylonitrile Butadiene Styrene (ABS)",
        "category": "Polymer / Thermoplastic",
        "density_kg_m3": 1050.0,
        "elastic_modulus_gpa": 2.3,
        "shear_modulus_gpa": 0.8,
        "yield_strength_mpa": 40.0,
        "ultimate_tensile_strength_mpa": 45.0,
        "elongation_pct": 30.0,
        "poisson_ratio": 0.35,
        "thermal_conductivity_w_m_k": 0.17,
        "cte_ppm_k": 90.0,
    },
}

ISO_METRIC_THREADS: Dict[str, Dict[str, float]] = {
    "M2": {"pitch_mm": 0.40, "tap_drill_mm": 1.60, "clearance_normal_mm": 2.40},
    "M2.5": {"pitch_mm": 0.45, "tap_drill_mm": 2.05, "clearance_normal_mm": 2.90},
    "M3": {"pitch_mm": 0.50, "tap_drill_mm": 2.50, "clearance_normal_mm": 3.40},
    "M4": {"pitch_mm": 0.70, "tap_drill_mm": 3.30, "clearance_normal_mm": 4.50},
    "M5": {"pitch_mm": 0.80, "tap_drill_mm": 4.20, "clearance_normal_mm": 5.50},
    "M6": {"pitch_mm": 1.00, "tap_drill_mm": 5.00, "clearance_normal_mm": 6.60},
    "M8": {"pitch_mm": 1.25, "tap_drill_mm": 6.80, "clearance_normal_mm": 9.00},
    "M10": {"pitch_mm": 1.50, "tap_drill_mm": 8.50, "clearance_normal_mm": 11.00},
    "M12": {"pitch_mm": 1.75, "tap_drill_mm": 10.20, "clearance_normal_mm": 13.50},
    "M16": {"pitch_mm": 2.00, "tap_drill_mm": 14.00, "clearance_normal_mm": 17.50},
    "M20": {"pitch_mm": 2.50, "tap_drill_mm": 17.50, "clearance_normal_mm": 22.00},
}

AWG_TABLE: Dict[int, Dict[str, float]] = {
    10: {"diameter_mm": 2.588, "area_mm2": 5.26, "resistance_ohm_km": 3.28, "ampacity_75c": 35.0},
    12: {"diameter_mm": 2.053, "area_mm2": 3.31, "resistance_ohm_km": 5.21, "ampacity_75c": 25.0},
    14: {"diameter_mm": 1.628, "area_mm2": 2.08, "resistance_ohm_km": 8.29, "ampacity_75c": 20.0},
    16: {"diameter_mm": 1.291, "area_mm2": 1.31, "resistance_ohm_km": 13.17, "ampacity_75c": 13.0},
    18: {"diameter_mm": 1.024, "area_mm2": 0.823, "resistance_ohm_km": 20.95, "ampacity_75c": 10.0},
    20: {"diameter_mm": 0.812, "area_mm2": 0.518, "resistance_ohm_km": 33.31, "ampacity_75c": 5.0},
    22: {"diameter_mm": 0.644, "area_mm2": 0.326, "resistance_ohm_km": 52.96, "ampacity_75c": 3.0},
    24: {"diameter_mm": 0.511, "area_mm2": 0.205, "resistance_ohm_km": 84.22, "ampacity_75c": 2.1},
    26: {"diameter_mm": 0.405, "area_mm2": 0.129, "resistance_ohm_km": 133.9, "ampacity_75c": 1.3},
    28: {"diameter_mm": 0.321, "area_mm2": 0.081, "resistance_ohm_km": 212.9, "ampacity_75c": 0.8},
}


class TechnicalResearchEngine:
    """Queryable engineering specification database."""

    @staticmethod
    def get_material(key_or_name: str) -> Optional[Dict[str, Any]]:
        """Finds material by key or substring match."""
        q = key_or_name.lower().replace(" ", "_").replace("-", "_")
        if q in MATERIALS_DATABASE:
            return MATERIALS_DATABASE[q]
        for key, mat in MATERIALS_DATABASE.items():
            if q in key or q in mat["name"].lower():
                return mat
        return None

    @staticmethod
    def list_materials() -> List[Dict[str, Any]]:
        """Returns list of all available materials in database."""
        return [{"key": k, **v} for k, v in MATERIALS_DATABASE.items()]

    @staticmethod
    def filter_materials(
        min_yield_mpa: Optional[float] = None,
        max_density_kg_m3: Optional[float] = None,
        min_modulus_gpa: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Filters materials matching engineering design criteria."""
        results = []
        for key, mat in MATERIALS_DATABASE.items():
            if min_yield_mpa is not None and mat["yield_strength_mpa"] < min_yield_mpa:
                continue
            if max_density_kg_m3 is not None and mat["density_kg_m3"] > max_density_kg_m3:
                continue
            if min_modulus_gpa is not None and mat["elastic_modulus_gpa"] < min_modulus_gpa:
                continue
            results.append({"key": key, **mat})
        return results

    @staticmethod
    def get_iso_metric_thread(designation: str) -> Optional[Dict[str, Any]]:
        """Returns pitch, tap drill, and clearance hole sizes for ISO metric thread (e.g. 'M3', 'M6')."""
        des = designation.upper()
        if des in ISO_METRIC_THREADS:
            return {"thread": des, **ISO_METRIC_THREADS[des]}
        return None

    @staticmethod
    def get_awg_wire(awg: int) -> Optional[Dict[str, Any]]:
        """Returns wire gauge specifications for given AWG number."""
        if awg in AWG_TABLE:
            return {"awg": awg, **AWG_TABLE[awg]}
        return None

    @staticmethod
    def recommend_awg_wire(
        current_amps: float,
        circuit_voltage_v: float,
        one_way_length_m: float,
        max_voltage_drop_pct: float = 3.0,
    ) -> Dict[str, Any]:
        """
        Recommends minimum AWG gauge considering ampacity and round-trip voltage drop limits.
        """
        max_v_drop = circuit_voltage_v * (max_voltage_drop_pct / 100.0)
        round_trip_m = 2.0 * one_way_length_m
        round_trip_km = round_trip_m / 1000.0

        candidates = []
        # Sort by gauge size ascending (largest wire first)
        for awg in sorted(AWG_TABLE.keys()):
            spec = AWG_TABLE[awg]
            # Ampacity check
            if spec["ampacity_75c"] < current_amps:
                continue
            # Voltage drop check: V_drop = I * R = I * (R_per_km * km)
            wire_res = spec["resistance_ohm_km"] * round_trip_km
            v_drop = current_amps * wire_res
            drop_pct = (v_drop / circuit_voltage_v) * 100.0
            if v_drop <= max_v_drop:
                candidates.append({
                    "recommended_awg": awg,
                    "ampacity_rating_a": spec["ampacity_75c"],
                    "actual_voltage_drop_v": round(v_drop, 3),
                    "voltage_drop_percent": round(drop_pct, 2),
                    "wire_resistance_ohm": round(wire_res, 4),
                })

        if candidates:
            # Pick the lightest/highest AWG number that passes
            return candidates[-1]

        return {"error": f"No standard AWG in database satisfies {current_amps}A load within {max_voltage_drop_pct}% drop."}
