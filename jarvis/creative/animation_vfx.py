"""
Animation and VFX Planning Module for J.A.R.V.I.S.
Covers Capabilities:
  - 85. Animation Planning (Keyframing, timing sheets, 12 principles of animation)
  - 86. VFX Planning (Pass breakdowns, green-screen extraction guides, tracking)
"""

import math
from typing import Dict, List, Any, Optional, Tuple


class AnimationPlanner:
    """Capability 85: Animation Planning"""

    THE_12_PRINCIPLES = {
        "squash_and_stretch": "Gives the illusion of weight and volume to a character as it moves.",
        "anticipation": "Prepares the audience for a major action the character is about to perform.",
        "staging": "Directing the audience's attention to what is greatest importance in a scene.",
        "straight_ahead_and_pose_to_pose": "Choosing between spontaneous sequential flow or structured keyframe poses.",
        "follow_through_and_overlapping": "Parts of the body continue moving after the character stops; different parts move at different rates.",
        "slow_in_and_slow_out": "Softening the beginning and end of poses with easing curves.",
        "arcs": "Natural human and creature motions follow curved trajectory paths rather than straight lines.",
        "secondary_action": "Adding subordinate actions to enhance the main action without distracting from it.",
        "timing": "Number of frames between actions to communicate mass, momentum, and physical reality.",
        "exaggeration": "Pushing forms, poses, and expressions slightly beyond reality for dramatic punch.",
        "solid_drawing": "Understanding three-dimensional volume, anatomy, and balance in space.",
        "appeal": "Charisma and magnetic visual presence that draws the viewer's emotional connection."
    }

    @staticmethod
    def calculate_easing_curve(curve_name: str = "ease_in_out", steps: int = 24) -> List[Dict[str, float]]:
        """
        Calculates mathematical easing values (normalized 0.0 to 1.0) across frames.
        Supported curves: 'linear', 'ease_in', 'ease_out', 'ease_in_out', 'spring_anticipation'.
        """
        curve = curve_name.lower()
        points = []

        for i in range(steps):
            t = i / max(1, steps - 1)  # normalized time 0.0 -> 1.0

            if curve == "linear":
                val = t
            elif curve == "ease_in":
                val = t ** 3
            elif curve == "ease_out":
                val = 1.0 - ((1.0 - t) ** 3)
            elif curve == "ease_in_out":
                # Smoothstep cubic
                val = t * t * (3.0 - 2.0 * t)
            elif curve == "spring_anticipation":
                # Slight backward dip (-0.1) then smooth surge to 1.0
                val = -0.15 * math.sin(t * math.pi) if t < 0.25 else ((t - 0.25) / 0.75) ** 2
                val = min(1.0, max(-0.15, val))
            else:
                val = t

            points.append({
                "frame": i + 1,
                "normalized_time": round(t, 4),
                "eased_value": round(val, 4)
            })

        return points

    @classmethod
    def generate_timing_sheet(
        cls,
        action_beats: List[Dict[str, Any]],
        fps: int = 24
    ) -> Dict[str, Any]:
        """
        Generates traditional animation exposure sheet (X-Sheet) mapping frame numbers
        to Keyframes, Breakdowns, In-betweens, and phoneme lip-sync labels.
        """
        x_sheet = []
        frame_cursor = 1

        for beat in action_beats:
            duration_frames = int(beat.get("duration_frames", 12))
            action_desc = beat.get("action", "Character motion")
            lip_phoneme = beat.get("phoneme", "")

            # Frame 1 of beat: Keyframe
            x_sheet.append({
                "frame": frame_cursor,
                "type": "KEY",
                "drawing_label": f"K{frame_cursor}",
                "action": action_desc,
                "audio_phoneme": lip_phoneme,
                "camera_notes": beat.get("camera", "")
            })

            # Mid frame: Breakdown
            breakdown_frame = frame_cursor + (duration_frames // 2)
            for f in range(frame_cursor + 1, frame_cursor + duration_frames):
                if f == breakdown_frame and duration_frames > 4:
                    f_type = "BREAKDOWN"
                    label = f"B{f}"
                else:
                    f_type = "INBETWEEN"
                    label = f"IB{f}"

                x_sheet.append({
                    "frame": f,
                    "type": f_type,
                    "drawing_label": label,
                    "action": "",
                    "audio_phoneme": "",
                    "camera_notes": ""
                })

            frame_cursor += duration_frames

        return {
            "fps": fps,
            "total_frames": len(x_sheet),
            "total_seconds": round(len(x_sheet) / fps, 2),
            "x_sheet": x_sheet
        }

    @classmethod
    def audit_animation_shot(cls, action_summary: str, character_type: str = "organic_humanoid") -> Dict[str, Any]:
        """
        Audits a planned animation shot against the 12 Principles of Animation
        and provides specific artistic directives.
        """
        recommendations = [
            {"principle": "Squash & Stretch", "directive": "Maintain rigid volume during compression on landing or impact."},
            {"principle": "Anticipation", "directive": "Wind up opposite to target action vector for 4-6 frames before launch."},
            {"principle": "Arcs", "directive": "Route limb and head trajectories along gentle parabolas, never straight linear paths."},
            {"principle": "Slow In & Slow Out", "directive": "Cluster drawings tightly near contact points and apexes to produce natural weight."}
        ]

        if "creature" in character_type.lower() or "quadruped" in character_type.lower():
            recommendations.append({
                "principle": "Secondary Action",
                "directive": "Add tail wag, ear flop, and spine rippling offset by 2 frames after paw contact."
            })
        else:
            recommendations.append({
                "principle": "Follow Through & Overlapping",
                "directive": "Offset hair, cloth, and fingers by 3 frames behind torso deceleration."
            })

        return {
            "action_summary": action_summary,
            "character_type": character_type,
            "principles_checklist": recommendations
        }


class VFXPlanner:
    """Capability 86: VFX Planning"""

    @staticmethod
    def generate_pass_breakdown(shot_description: str, engine: str = "Unreal / ACEScg / Arnold") -> Dict[str, Any]:
        """
        Generates standard multi-pass CGI render and compositing breakdown.
        """
        passes = [
            {"name": "Beauty / Combined", "type": "RGBA", "purpose": "Reference comp verification"},
            {"name": "Diffuse Direct", "type": "RGB", "purpose": "Direct light bounce off surfaces without ambient influence"},
            {"name": "Diffuse Indirect", "type": "RGB", "purpose": "Global illumination and environmental color bleed"},
            {"name": "Specular Direct", "type": "RGB", "purpose": "Direct reflection of light sources"},
            {"name": "Specular Indirect", "type": "RGB", "purpose": "Environmental reflections and roughness gloss"},
            {"name": "Emission", "type": "RGB", "purpose": "Self-illuminating materials, neon lights, HUD displays"},
            {"name": "Transmission / Refraction", "type": "RGB", "purpose": "Glass, water, transparent optics"},
            {"name": "Ambient Occlusion (AO)", "type": "Grayscale", "purpose": "Contact shadows in crevices and corners"},
            {"name": "Shadow", "type": "Grayscale", "purpose": "Cast shadow density adjustment"},
            {"name": "Z-Depth", "type": "32-bit Float", "purpose": "Depth of field defocusing and atmospheric fog haze"},
            {"name": "Motion Vectors", "type": "2D Vector", "purpose": "Post-motion blur calculation in Nuke / After Effects"},
            {"name": "World Normals", "type": "XYZ Vector", "purpose": "Relighting, edge fresnel, and surface directional masking"},
            {"name": "Cryptomatte / Material IDs", "type": "Multi-channel EXR", "purpose": "Per-asset and per-material isolating mattes"}
        ]

        comp_recipe = [
            "1. Diffuse Total = Diffuse Direct + Diffuse Indirect",
            "2. Specular Total = Specular Direct + Specular Indirect",
            "3. Base Surface = (Diffuse Total * Diffuse Color) + Specular Total + Transmission + Emission",
            "4. Multiply Ambient Occlusion over shadows",
            "5. Apply Z-Depth post-lens defocus and atmosphere",
            "6. Apply Motion Vector blur"
        ]

        return {
            "shot_description": shot_description,
            "render_color_space": engine,
            "total_passes": len(passes),
            "passes": passes,
            "compositing_merge_recipe": comp_recipe
        }

    @staticmethod
    def green_screen_extraction_guide(
        lighting_notes: str = "Studio softbox setup",
        foreground_complexity: str = "Fine hair and translucent fabric"
    ) -> Dict[str, Any]:
        """
        Provides detailed green/blue screen chroma keying and extraction guidelines.
        """
        return {
            "backdrop_lighting": {
                "evenness_tolerance": "+/- 0.5 stops across entire background surface",
                "green_screen_exposure": "1 stop below key subject skin tone to prevent spill bounce",
                "subject_distance": "Minimum 2.5 to 3.0 meters from screen to eliminate green edge contamination"
            },
            "extraction_workflow": [
                {"step": "Garbage Matte", "action": "Roto out unwanted studio equipment, lights, and floor edges outside action area."},
                {"step": "Core Matte", "action": "Hard, 100% solid matte covering internal subject anatomy (no transparency)."},
                {"step": "Soft Edge Matte", "action": "Dedicated high-pass key targeting fine hair strands and translucent edges."},
                {"step": "Spill Suppression", "action": "Despill color matrix: Green = min(Green, (Red + Blue) / 2)."},
                {"step": "Light Wrap", "action": "Blend 2-4px blurred background luminance into foreground edges to integrate into destination plate."}
            ],
            "foreground_handling": {
                "complexity": foreground_complexity,
                "recommended_tool": "IBK Colour / IBK Gizmo in Nuke or Primatte Keyer"
            }
        }

    @staticmethod
    def plan_camera_tracking(
        scene_type: str = "Interior corridor with moving actors",
        motion_type: str = "Handheld moving push-in"
    ) -> Dict[str, Any]:
        """
        Generates 3D camera matchmoving and tracking guidelines.
        """
        return {
            "scene_environment": scene_type,
            "camera_motion": motion_type,
            "tracking_requirements": {
                "minimum_track_points": 85,
                "distribution": "30% foreground, 40% midground, 30% background for robust 3D depth parallax",
                "lens_calibration": "Shoot checkerboard / distortion grid before and after session",
                "target_reprojection_error": "< 0.75 pixels RMS error"
            },
            "survey_markers": "Affix high-contrast cross markers on stationary walls; ensure at least 8 markers visible at all times.",
            "rolling_shutter_compensation": "Enable sensor readout scanline correction if CMOS shutter > 15ms."
        }
