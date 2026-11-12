"""
Film Production and Documentation Module for J.A.R.V.I.S.
Covers Capabilities:
  - 76. Film Production Assistant (Call sheets, scene breakdowns, schedules)
  - 79. Shot Planning (Shot lists, lens focal lengths, camera angles)
  - 90. Production Documentation (Budget sheets, release forms, treatment summaries)
"""

import math
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta


class FilmProductionAssistant:
    """Capability 76: Film Production Assistant"""

    @staticmethod
    def create_call_sheet(
        project_name: str,
        shoot_date: str,
        call_time: str,
        location: Dict[str, str],
        scenes: List[Dict[str, Any]],
        cast_calls: List[Dict[str, Any]],
        crew_department_heads: List[Dict[str, str]],
        hospital_info: Optional[Dict[str, str]] = None,
        weather_forecast: Optional[str] = "Clear, 21C / 70F, Sunset 19:42",
        parking_notes: Optional[str] = "Crew parking in East Lot behind Stage 3."
    ) -> Dict[str, Any]:
        """
        Generates an industry-standard call sheet payload.
        """
        hospital = hospital_info or {
            "name": "General Emergency Hospital",
            "address": "100 Medical Center Blvd",
            "phone": "555-0199"
        }

        total_pages = sum(float(s.get("pages", 1.0)) for s in scenes)

        return {
            "project_name": project_name,
            "shoot_date": shoot_date,
            "general_call": call_time,
            "weather": weather_forecast,
            "location": location,
            "parking_notes": parking_notes,
            "nearest_hospital": hospital,
            "schedule": {
                "total_scenes": len(scenes),
                "total_pages": round(total_pages, 2),
                "scenes": scenes
            },
            "cast": cast_calls,
            "crew": crew_department_heads,
            "vip_safety_notice": "Safety briefing starts 15 mins prior to camera roll."
        }

    @staticmethod
    def generate_scene_breakdown(script_text_or_scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes scenes and extracts required departments:
        cast, extras, props, wardrobe, vehicles, special effects (SFX), stunts.
        """
        breakdown_items = []
        all_cast = set()
        all_props = set()
        all_locations = set()

        for idx, scene in enumerate(script_text_or_scenes, start=1):
            slugline = scene.get("slugline", f"SCENE {idx} - INT. LOCATION - DAY")
            setting_type = "INT" if "INT." in slugline.upper() else ("EXT" if "EXT." in slugline.upper() else "INT/EXT")
            time_of_day = "NIGHT" if "NIGHT" in slugline.upper() else "DAY"
            cast = scene.get("cast", [])
            props = scene.get("props", [])
            wardrobe = scene.get("wardrobe", [])
            sfx = scene.get("sfx", [])
            stunts = scene.get("stunts", [])
            notes = scene.get("notes", "")

            for c in cast:
                all_cast.add(c)
            for p in props:
                all_props.add(p)
            all_locations.add(slugline)

            breakdown_items.append({
                "scene_number": scene.get("scene_number", idx),
                "slugline": slugline,
                "setting_type": setting_type,
                "time_of_day": time_of_day,
                "pages": float(scene.get("pages", 1.0)),
                "cast": cast,
                "extras": scene.get("extras", 0),
                "props": props,
                "wardrobe": wardrobe,
                "sfx": sfx,
                "stunts": stunts,
                "notes": notes
            })

        return {
            "total_scenes": len(breakdown_items),
            "unique_cast_count": len(all_cast),
            "cast_list": sorted(list(all_cast)),
            "unique_locations": sorted(list(all_locations)),
            "master_props": sorted(list(all_props)),
            "breakdown": breakdown_items
        }

    @staticmethod
    def create_production_schedule(
        scenes: List[Dict[str, Any]],
        shoot_days: int = 3,
        day_hours: float = 10.0
    ) -> Dict[str, Any]:
        """
        Groups and distributes scenes across production shoot days,
        optimizing for location grouping to minimize setup moves.
        """
        # Group by location / setting
        location_groups: Dict[str, List[Dict[str, Any]]] = {}
        for sc in scenes:
            loc = sc.get("slugline", "DEFAULT_LOCATION").split("-")[0].strip()
            location_groups.setdefault(loc, []).append(sc)

        flattened_optimized_scenes = []
        for loc, sc_list in location_groups.items():
            flattened_optimized_scenes.extend(sc_list)

        # Distribute into shoot days
        days_schedule = []
        scenes_per_day = math.ceil(len(flattened_optimized_scenes) / max(1, shoot_days))
        for d in range(shoot_days):
            day_slice = flattened_optimized_scenes[d * scenes_per_day : (d + 1) * scenes_per_day]
            day_pages = sum(float(s.get("pages", 1.0)) for s in day_slice)
            days_schedule.append({
                "day_number": d + 1,
                "scenes": [s.get("scene_number", i + 1) for i, s in enumerate(day_slice)],
                "scene_count": len(day_slice),
                "scheduled_pages": round(day_pages, 2),
                "est_hours": min(day_hours, round(day_pages * 2.2 + len(day_slice) * 0.75, 1))
            })

        return {
            "shoot_days_planned": shoot_days,
            "total_scenes": len(scenes),
            "schedule": days_schedule
        }


class ShotPlanner:
    """Capability 79: Shot Planning"""

    # Lens categories for 35mm full-frame sensor (36mm x 24mm)
    LENS_DATABASE = {
        "ultra_wide": {"focal_length": 18, "angle_of_view_deg": 100.0, "use": "Expansive environments, tight spaces, deep perspective"},
        "wide": {"focal_length": 24, "angle_of_view_deg": 84.0, "use": "Establishing shots, dynamic movement, environmental context"},
        "standard_wide": {"focal_length": 35, "angle_of_view_deg": 63.4, "use": "Natural perspective, documentary, walking dialogue"},
        "normal": {"focal_length": 50, "angle_of_view_deg": 46.8, "use": "Human eye equivalence, medium coverage, portraits"},
        "portrait": {"focal_length": 85, "angle_of_view_deg": 28.6, "use": "Flattering close-ups, shallow depth-of-field, cinematic compression"},
        "telephoto": {"focal_length": 135, "angle_of_view_deg": 18.2, "use": "Intimate close-ups, distant tracking, background separation"}
    }

    @staticmethod
    def calculate_field_of_view(sensor_width_mm: float, focal_length_mm: float) -> Dict[str, float]:
        """
        Calculates horizontal Field of View (FOV) in degrees given sensor width and focal length.
        FOV = 2 * arctan(sensor_width / (2 * focal_length))
        """
        if focal_length_mm <= 0:
            raise ValueError("Focal length must be strictly positive.")
        fov_rad = 2.0 * math.atan(sensor_width_mm / (2.0 * focal_length_mm))
        fov_deg = math.degrees(fov_rad)
        return {
            "sensor_width_mm": sensor_width_mm,
            "focal_length_mm": focal_length_mm,
            "horizontal_fov_degrees": round(fov_deg, 2)
        }

    @classmethod
    def generate_shot_list(
        cls,
        scene_info: Dict[str, Any],
        coverage_style: str = "cinematic_master_coverage"
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive shot list including shot type, focal length,
        camera angle, camera movement, and framing description.
        """
        scene_num = scene_info.get("scene_number", 1)
        action_desc = scene_info.get("action", "Characters interact in the room.")
        characters = scene_info.get("characters", ["Character A", "Character B"])

        shots = [
            {
                "shot_id": f"{scene_num}A",
                "type": "Wide Establishing / Master Shot",
                "focal_length_mm": 24,
                "angle": "Eye-level",
                "movement": "Slow push-in / Dolly",
                "framing": "Full room showing spatial geography and character placement",
                "audio_notes": "Room ambiance, primary dialogue capture",
                "purpose": "Anchor the geography and rhythm of the scene"
            },
            {
                "shot_id": f"{scene_num}B",
                "type": "Medium Two-Shot",
                "focal_length_mm": 35,
                "angle": "Slight low-angle",
                "movement": "Static on sticks",
                "framing": "Waist-up framing of both interacting subjects",
                "audio_notes": "Boom mic focused on interaction axis",
                "purpose": "Establish conversational tension"
            }
        ]

        # Add coverage for individual characters
        for idx, char in enumerate(characters):
            shot_letter = chr(ord('C') + idx)
            shots.append({
                "shot_id": f"{scene_num}{shot_letter}",
                "type": f"Over-the-Shoulder (OTS) / Medium Close-Up",
                "subject": char,
                "focal_length_mm": 50,
                "angle": "Eye-level",
                "movement": "Handheld micro-jitters for emotional urgency",
                "framing": f"Chest up on {char} with slight foreground shoulder",
                "audio_notes": "Lavalier and primary directional boom",
                "purpose": f"Intimate emotional engagement with {char}"
            })

        # Add insert / detail cutaway
        detail_letter = chr(ord('C') + len(characters))
        shots.append({
            "shot_id": f"{scene_num}{detail_letter}",
            "type": "Macro Insert / Extreme Close-Up",
            "focal_length_mm": 85,
            "angle": "High-angle top down",
            "movement": "Static",
            "framing": "Key prop / tactile object hands interact with",
            "audio_notes": "Foley emphasis, sharp tactile sound",
            "purpose": "Narrative visual punctuation"
        })

        return {
            "scene_number": scene_num,
            "coverage_style": coverage_style,
            "action_summary": action_desc,
            "total_shots": len(shots),
            "shot_list": shots
        }


class ProductionDocumentation:
    """Capability 90: Production Documentation"""

    @staticmethod
    def generate_budget_sheet(
        line_items: List[Dict[str, Any]],
        contingency_pct: float = 10.0
    ) -> Dict[str, Any]:
        """
        Compiles an industry-standard film/media production budget
        categorized into Above-The-Line (ATL), Below-The-Line (BTL),
        Post-Production, and Contingency.
        """
        atl_total = 0.0
        btl_total = 0.0
        post_total = 0.0
        other_total = 0.0

        categorized = {"ATL": [], "BTL": [], "POST": [], "OTHER": []}

        for item in line_items:
            cat = str(item.get("category", "BTL")).upper()
            cost = float(item.get("rate", 0.0)) * float(item.get("quantity", 1.0))
            record = {
                "description": item.get("description", "Unnamed line item"),
                "category": cat,
                "unit": item.get("unit", "day"),
                "rate": item.get("rate", 0.0),
                "quantity": item.get("quantity", 1.0),
                "total_cost": round(cost, 2)
            }
            if cat in categorized:
                categorized[cat].append(record)
            else:
                categorized["OTHER"].append(record)

            if cat == "ATL":
                atl_total += cost
            elif cat == "BTL":
                btl_total += cost
            elif cat == "POST":
                post_total += cost
            else:
                other_total += cost

        subtotal = atl_total + btl_total + post_total + other_total
        contingency_amount = subtotal * (contingency_pct / 100.0)
        grand_total = subtotal + contingency_amount

        return {
            "summary": {
                "above_the_line_total": round(atl_total, 2),
                "below_the_line_total": round(btl_total, 2),
                "post_production_total": round(post_total, 2),
                "subtotal": round(subtotal, 2),
                "contingency_percent": contingency_pct,
                "contingency_amount": round(contingency_amount, 2),
                "grand_total": round(grand_total, 2)
            },
            "line_items_by_department": categorized
        }

    @staticmethod
    def generate_release_form(
        talent_name: str,
        project_name: str,
        producer_name: str,
        rights_type: str = "all_media_perpetuity_worldwide",
        compensation: str = "Screen credit and copy of completed project"
    ) -> Dict[str, Any]:
        """
        Generates a legally structured Talent / Location Release Agreement.
        """
        agreement_text = (
            f"TALENT AND APPEARANCE RELEASE AGREEMENT\n\n"
            f"For valuable consideration, receipt of which is hereby acknowledged, I, {talent_name}, "
            f"grant to {producer_name} ('Producer') and its successors, licensees, and assigns, "
            f"the perpetual, irrevocable right and license to photograph, record, and reproduce my image, "
            f"likeness, voice, and performance in connection with the production entitled '{project_name}'.\n\n"
            f"1. RIGHTS GRANTED: {rights_type.replace('_', ' ').title()}.\n"
            f"2. COMPENSATION: {compensation}.\n"
            f"3. NO INJUNCTIVE RELIEF: In no event shall Talent have the right to enjoin or restrain the development, "
            f"production, advertising, or exploitation of the project."
        )

        return {
            "contract_type": "Talent Release Form",
            "talent_name": talent_name,
            "project_name": project_name,
            "producer_name": producer_name,
            "effective_date": date.today().isoformat(),
            "rights_scope": rights_type,
            "compensation_terms": compensation,
            "legal_text": agreement_text
        }

    @staticmethod
    def generate_treatment_summary(
        title: str,
        logline: str,
        synopsis: str,
        tone_and_style: str,
        target_audience: str,
        visual_references: List[str]
    ) -> Dict[str, Any]:
        """
        Creates a structured pitch treatment summary for executive review.
        """
        return {
            "project_title": title,
            "logline": logline,
            "synopsis": synopsis,
            "creative_vision": {
                "tone_and_style": tone_and_style,
                "visual_references": visual_references
            },
            "market_positioning": {
                "target_demographic": target_audience,
                "comparable_titles": visual_references[:3]
            },
            "timestamp": datetime.now().isoformat()
        }
