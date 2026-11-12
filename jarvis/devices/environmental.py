"""
Capability 120: Environmental Monitoring
Calculates thermodynamic indexes (Heat Index, Dew Point, Vapor Pressure Deficit),
Indoor Air Quality (IAQ) composite scoring, ASHRAE-55 thermal comfort,
and automated HVAC / ventilation recommendations.
"""

import math
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional


@dataclass
class EnvironmentalSnapshot:
    temperature_c: float
    humidity_pct: float
    pressure_hpa: float = 1013.25
    co2_ppm: float = 500.0
    pm25_ugm3: float = 8.0
    tvoc_ppb: float = 60.0
    heat_index_c: float = 22.0
    dew_point_c: float = 11.0
    vpd_kpa: float = 1.2
    iaq_score: int = 45
    iaq_grade: str = "EXCELLENT"
    comfort_status: str = "COMFORTABLE"
    recommendations: List[str] = None


class EnvironmentalMonitor:
    """Computes thermodynamic environmental comfort indices and health analytics."""

    def __init__(self):
        pass

    @staticmethod
    def calculate_dew_point(temperature_c: float, humidity_pct: float) -> float:
        """
        Calculates Dew Point in Celsius using the Magnus-Tetens approximation.
        Valid for range -45°C to 60°C and 1% to 100% RH.
        """
        rh = max(1.0, min(100.0, float(humidity_pct)))
        a = 17.27
        b = 237.7
        alpha = ((a * temperature_c) / (b + temperature_c)) + math.log(rh / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        return round(dew_point, 2)

    @staticmethod
    def calculate_heat_index(temperature_c: float, humidity_pct: float) -> float:
        """
        Calculates NOAA Heat Index in Celsius using the full Rothfusz regression equation.
        """
        # Convert to Fahrenheit for NOAA formula
        t_f = (temperature_c * 9.0 / 5.0) + 32.0
        rh = max(0.0, min(100.0, float(humidity_pct)))

        # Below 80°F, heat index is effectively equal to air temperature
        if t_f < 80.0:
            hi_f = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (rh * 0.094))
            return round((hi_f - 32.0) * 5.0 / 9.0, 2)

        # Full Rothfusz regression equation
        hi_f = (
            -42.379
            + 2.04901523 * t_f
            + 10.14333127 * rh
            - 0.22475541 * t_f * rh
            - 0.00683783 * (t_f ** 2)
            - 0.05481717 * (rh ** 2)
            + 0.00122874 * (t_f ** 2) * rh
            + 0.00085282 * t_f * (rh ** 2)
            - 0.00000199 * (t_f ** 2) * (rh ** 2)
        )

        # Adjustments for dry or humid air
        if rh < 13.0 and (80.0 <= t_f <= 112.0):
            adj = ((13.0 - rh) / 4.0) * math.sqrt((17.0 - abs(t_f - 95.0)) / 17.0)
            hi_f -= adj
        elif rh > 85.0 and (80.0 <= t_f <= 87.0):
            adj = ((rh - 85.0) / 10.0) * ((87.0 - t_f) / 5.0)
            hi_f += adj

        hi_c = (hi_f - 32.0) * 5.0 / 9.0
        return round(hi_c, 2)

    @staticmethod
    def calculate_vpd(temperature_c: float, humidity_pct: float) -> float:
        """
        Calculates Vapor Pressure Deficit (VPD) in kilopascals (kPa).
        Important metric for transpiration, room dryness, and respiratory comfort.
        """
        rh = max(0.0, min(100.0, float(humidity_pct)))
        # Saturation vapor pressure (Tetens formula)
        vp_sat = 0.61078 * math.exp((17.27 * temperature_c) / (temperature_c + 237.3))
        # Actual vapor pressure
        vp_act = vp_sat * (rh / 100.0)
        vpd = vp_sat - vp_act
        return round(max(0.0, vpd), 3)

    @staticmethod
    def calculate_iaq(co2_ppm: float, pm25_ugm3: float, tvoc_ppb: float) -> Tuple[int, str]:
        """
        Produces an Indoor Air Quality (IAQ) index (0 to 500) and grade
        based on EPA and WHO standards.
        """
        # CO2 sub-index (0 to 100 scale: 400ppm -> 0, 1500ppm -> 100)
        co2_score = max(0.0, (co2_ppm - 400.0) / 11.0)
        # PM2.5 sub-index (0 to 100 scale: 0 -> 0, 50 ug/m3 -> 100)
        pm_score = (pm25_ugm3 / 50.0) * 100.0
        # TVOC sub-index (0 to 100 scale: 0 -> 0, 300 ppb -> 100)
        voc_score = (tvoc_ppb / 300.0) * 100.0

        # Weighted composite score
        composite = int(0.40 * co2_score + 0.35 * pm_score + 0.25 * voc_score)
        composite = max(0, min(500, composite))

        if composite <= 50:
            grade = "EXCELLENT"
        elif composite <= 100:
            grade = "MODERATE"
        elif composite <= 150:
            grade = "POOR"
        elif composite <= 200:
            grade = "UNHEALTHY"
        elif composite <= 300:
            grade = "VERY_UNHEALTHY"
        else:
            grade = "HAZARDOUS"

        return composite, grade

    def evaluate_environment(
        self,
        temperature_c: float,
        humidity_pct: float,
        pressure_hpa: float = 1013.25,
        co2_ppm: float = 500.0,
        pm25_ugm3: float = 8.0,
        tvoc_ppb: float = 60.0
    ) -> EnvironmentalSnapshot:
        """
        Evaluates full thermal and air quality parameters against ASHRAE-55
        standards and generates concrete mitigation recommendations.
        """
        dew_point = self.calculate_dew_point(temperature_c, humidity_pct)
        heat_index = self.calculate_heat_index(temperature_c, humidity_pct)
        vpd = self.calculate_vpd(temperature_c, humidity_pct)
        iaq_score, iaq_grade = self.calculate_iaq(co2_ppm, pm25_ugm3, tvoc_ppb)

        # ASHRAE-55 Comfort evaluation
        comfort_status = "COMFORTABLE"
        recommendations: List[str] = []

        if temperature_c < 19.0:
            comfort_status = "TOO_COLD"
            recommendations.append(f"Room temperature is cool ({temperature_c}°C). Increase heating setpoint to 21°C.")
        elif temperature_c > 26.0:
            comfort_status = "TOO_WARM"
            recommendations.append(f"Room temperature is warm ({temperature_c}°C). Enable cooling or fan circulation.")

        if humidity_pct < 30.0:
            recommendations.append(f"Low relative humidity ({humidity_pct}%). Turn on humidifier to prevent vocal and airway strain.")
        elif humidity_pct > 65.0:
            recommendations.append(f"Elevated humidity ({humidity_pct}%). Turn on dehumidifier to suppress mold growth risk.")

        if co2_ppm >= 1000.0:
            recommendations.append(f"Elevated CO2 detected ({co2_ppm} ppm). Open a window or activate HVAC fresh air intake.")
        if pm25_ugm3 >= 25.0:
            recommendations.append(f"Particulate matter PM2.5 elevated ({pm25_ugm3} µg/m³). Turn on HEPA air purifier.")
        if tvoc_ppb >= 220.0:
            recommendations.append(f"Volatile organic compounds TVOC high ({tvoc_ppb} ppb). Increase ventilation.")

        if not recommendations:
            recommendations.append("All ambient thermodynamic and air quality parameters are optimal.")

        return EnvironmentalSnapshot(
            temperature_c=round(temperature_c, 2),
            humidity_pct=round(humidity_pct, 2),
            pressure_hpa=round(pressure_hpa, 2),
            co2_ppm=round(co2_ppm, 1),
            pm25_ugm3=round(pm25_ugm3, 1),
            tvoc_ppb=round(tvoc_ppb, 1),
            heat_index_c=heat_index,
            dew_point_c=dew_point,
            vpd_kpa=vpd,
            iaq_score=iaq_score,
            iaq_grade=iaq_grade,
            comfort_status=comfort_status,
            recommendations=recommendations
        )
