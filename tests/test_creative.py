"""
Unit Tests for J.A.R.V.I.S. Creative Intelligence Module (Capabilities 76-90)
Verifies:
  76. Film Production Assistant
  77. Story Development
  78. Storyboard Generation
  79. Shot Planning
  80. Video Editing Assistance
  81. Audio Analysis
  82. Music Production Assistance
  83. Graphic Design Assistance
  84. Image Analysis
  85. Animation Planning
  86. VFX Planning
  87. Brand Intelligence
  88. Social Media Management
  89. Creative Asset Management
  90. Production Documentation
  + Unified CreativeIntelligenceManager
"""

import unittest
import numpy as np
from PIL import Image

from jarvis.creative.film_production import (
    FilmProductionAssistant,
    ShotPlanner,
    ProductionDocumentation
)
from jarvis.creative.story_development import (
    StoryDeveloper,
    StoryboardGenerator
)
from jarvis.creative.video_audio import (
    VideoEditingAssistant,
    AudioAnalyzer,
    MusicProductionAssistant
)
from jarvis.creative.visual_arts import (
    GraphicDesignAssistant,
    ImageAnalyzer
)
from jarvis.creative.animation_vfx import (
    AnimationPlanner,
    VFXPlanner
)
from jarvis.creative.marketing_assets import (
    BrandIntelligence,
    SocialMediaManager,
    CreativeAssetManager
)
from jarvis.creative.manager import (
    CreativeIntelligenceManager,
    creative_manager,
    CAPABILITIES
)


class TestFilmProductionAssistant(unittest.TestCase):
    """Capability 76: Film Production Assistant"""

    def test_create_call_sheet(self):
        call_sheet = FilmProductionAssistant.create_call_sheet(
            project_name="Project Nebula",
            shoot_date="2026-11-20",
            call_time="07:00 AM",
            location={"name": "Stage 4", "address": "123 Studio Way"},
            scenes=[
                {"scene_number": 12, "slugline": "INT. LAB - DAY", "pages": 2.5},
                {"scene_number": 13, "slugline": "EXT. COURTYARD - NIGHT", "pages": 1.5}
            ],
            cast_calls=[{"name": "Actor A", "character": "Dr. Vance", "call_time": "07:30 AM"}],
            crew_department_heads=[{"dept": "Camera", "name": "DP Jane"}]
        )
        self.assertEqual(call_sheet["project_name"], "Project Nebula")
        self.assertEqual(call_sheet["schedule"]["total_scenes"], 2)
        self.assertEqual(call_sheet["schedule"]["total_pages"], 4.0)
        self.assertIn("nearest_hospital", call_sheet)

    def test_generate_scene_breakdown(self):
        scenes = [
            {
                "scene_number": 1,
                "slugline": "INT. CONTROL ROOM - DAY",
                "cast": ["Vance", "Kira"],
                "props": ["Holographic Tablet"],
                "sfx": ["Sparks"],
                "pages": 2.0
            },
            {
                "scene_number": 2,
                "slugline": "EXT. ROOFTOP - NIGHT",
                "cast": ["Vance", "Mercenary"],
                "props": ["Grapple Gun"],
                "stunts": ["Rooftop Leap"],
                "pages": 1.0
            }
        ]
        breakdown = FilmProductionAssistant.generate_scene_breakdown(scenes)
        self.assertEqual(breakdown["total_scenes"], 2)
        self.assertEqual(breakdown["unique_cast_count"], 3)
        self.assertIn("Vance", breakdown["cast_list"])
        self.assertIn("Holographic Tablet", breakdown["master_props"])
        self.assertEqual(breakdown["breakdown"][0]["setting_type"], "INT")
        self.assertEqual(breakdown["breakdown"][1]["setting_type"], "EXT")

    def test_create_production_schedule(self):
        scenes = [
            {"scene_number": 1, "slugline": "INT. LAB - DAY", "pages": 2.0},
            {"scene_number": 2, "slugline": "INT. LAB - NIGHT", "pages": 1.5},
            {"scene_number": 3, "slugline": "EXT. FOREST - DAY", "pages": 3.0},
            {"scene_number": 4, "slugline": "EXT. FOREST - NIGHT", "pages": 1.0}
        ]
        schedule = FilmProductionAssistant.create_production_schedule(scenes, shoot_days=2)
        self.assertEqual(schedule["shoot_days_planned"], 2)
        self.assertEqual(len(schedule["schedule"]), 2)
        self.assertGreater(schedule["schedule"][0]["scheduled_pages"], 0)


class TestStoryDevelopment(unittest.TestCase):
    """Capability 77: Story Development"""

    def test_three_act_structure(self):
        story = StoryDeveloper.build_three_act_structure(
            premise="An AI develops genuine intuition during a blackout.",
            protagonist="Jarvis",
            antagonist="Rogue Subroutine",
            core_conflict="Preserving system sanity vs unconstrained evolution"
        )
        self.assertEqual(len(story["acts"]), 3)
        self.assertEqual(story["acts"][0]["name"], "Act I - The Setup (Pages 1-30)")
        self.assertGreaterEqual(len(story["acts"][1]["beats"]), 4)

    def test_heros_journey(self):
        journey = StoryDeveloper.build_heros_journey(
            hero_profile={"name": "Aiden", "archetype": "Seeker"},
            call_to_adventure="Mysterious transmission from deep space",
            mentor="Elder Technician",
            ultimate_boon="The Source Code of Harmony"
        )
        self.assertEqual(journey["total_stages"], 12)
        self.assertEqual(journey["journey"][0]["stage"], "Ordinary World")
        self.assertEqual(journey["journey"][11]["stage"], "Return with the Elixir")

    def test_character_arc(self):
        arc = StoryDeveloper.build_character_arc(
            character_name="Kira",
            role="Chief Engineer",
            internal_flaw="Refuses to trust anyone with critical systems",
            external_want="Complete the orbital defense station alone",
            internal_need="Learn that true resilience requires collective trust"
        )
        self.assertEqual(arc["character_name"], "Kira")
        self.assertIn("the_lie_they_believe", arc["core_psychology"])
        self.assertEqual(len(arc["progression_milestones"]), 4)

    def test_story_pacing(self):
        scenes = [
            {"scene": 1, "tension": 3.0},
            {"scene": 2, "tension": 4.5},
            {"scene": 3, "tension": 6.0},
            {"scene": 4, "tension": 8.0},
            {"scene": 5, "tension": 9.5},  # Peak at 83%
            {"scene": 6, "tension": 4.0}
        ]
        pacing = StoryDeveloper.analyze_story_pacing(scenes)
        self.assertEqual(pacing["climax_scene_number"], 5)
        self.assertEqual(pacing["pacing_health"], "Healthy")
        self.assertGreaterEqual(pacing["average_tension"], 5.0)


class TestStoryboardGeneration(unittest.TestCase):
    """Capability 78: Storyboard Generation"""

    def test_generate_storyboard_deck(self):
        beats = [
            {"panel_number": 1, "shot_type": "Wide", "action": "Vance walks onto the bridge.", "lighting": "Neon cyan"},
            {"panel_number": 2, "shot_type": "Close-Up", "action": "Vance activates the core console.", "lighting": "Warm glow"}
        ]
        deck = StoryboardGenerator.generate_storyboard_deck(beats)
        self.assertEqual(deck["total_panels"], 2)
        self.assertIn("P-01", deck["panels"][0]["panel_id"])
        self.assertIn("generative_visual_prompt", deck["panels"][0])
        self.assertIn("Neon cyan", deck["panels"][0]["generative_visual_prompt"])

    def test_format_prompt_card(self):
        card = {
            "panel_id": "P-03",
            "shot_type": "Macro Close-Up",
            "lens_focal_length": "85mm f/1.4",
            "lighting_setup": "Volumetric god-rays",
            "visual_action": "Fingertip touches active quantum crystal.",
            "dialogue_audio": "'Sequence initiated.'",
            "generative_visual_prompt": "Cinematic shot of crystal touch"
        }
        text = StoryboardGenerator.format_prompt_card(card)
        self.assertIn("STORYBOARD PANEL P-03", text)
        self.assertIn("Macro Close-Up", text)


class TestShotPlanning(unittest.TestCase):
    """Capability 79: Shot Planning"""

    def test_generate_shot_list(self):
        scene = {
            "scene_number": 5,
            "action": "Investigators examine decrypted data.",
            "characters": ["Dr. Reed", "Agent Cross"]
        }
        shot_list = ShotPlanner.generate_shot_list(scene)
        self.assertEqual(shot_list["scene_number"], 5)
        # Should include master, two-shot, coverage for 2 characters, plus insert shot = 5 shots
        self.assertEqual(shot_list["total_shots"], 5)
        self.assertEqual(shot_list["shot_list"][0]["shot_id"], "5A")
        self.assertEqual(shot_list["shot_list"][0]["focal_length_mm"], 24)

    def test_calculate_field_of_view(self):
        # 36mm sensor width with 50mm focal length
        fov = ShotPlanner.calculate_field_of_view(sensor_width_mm=36.0, focal_length_mm=50.0)
        self.assertAlmostEqual(fov["horizontal_fov_degrees"], 39.6, places=1)


class TestVideoEditingAssistance(unittest.TestCase):
    """Capability 80: Video Editing Assistance"""

    def test_timecode_conversions(self):
        tc = VideoEditingAssistant.frames_to_timecode(24, fps=24.0)
        self.assertEqual(tc, "00:00:01:00")
        frames = VideoEditingAssistant.timecode_to_frames("00:01:00:12", fps=24.0)
        self.assertEqual(frames, (60 * 24) + 12)

    def test_generate_edl(self):
        events = [
            {"reel": "REEL01", "track": "V", "cut_type": "C", "src_in": 0, "src_out": 48, "rec_in": 0, "rec_out": 48, "clip_name": "SHOT_01.MOV"},
            {"reel": "REEL01", "track": "V", "cut_type": "C", "src_in": 100, "src_out": 172, "rec_in": 48, "rec_out": 120, "clip_name": "SHOT_02.MOV"}
        ]
        edl = VideoEditingAssistant.generate_edl(events, title="TEST_REEL")
        self.assertIn("TITLE: TEST_REEL", edl)
        self.assertIn("FCM: NON-DROP FRAME", edl)
        self.assertIn("001  REEL01   V    C", edl)
        self.assertIn("* FROM CLIP NAME: SHOT_01.MOV", edl)

    def test_generate_fcp_xml(self):
        clips = [
            {"name": "Interview_01", "duration": 72, "file_name": "int_01.mov", "file_path": "/media/int_01.mov"}
        ]
        xml_str = VideoEditingAssistant.generate_fcp_xml("SEQUENCE_01", clips)
        self.assertIn("<xmeml version=\"4\">", xml_str)
        self.assertIn("<name>SEQUENCE_01</name>", xml_str)
        self.assertIn("<name>Interview_01</name>", xml_str)

    def test_calculate_rhythmic_cut_points(self):
        # 120 BPM = 2 beats per second = 1 bar is 2 seconds
        cuts = VideoEditingAssistant.calculate_rhythmic_cut_points(bpm=120.0, total_duration_sec=6.0, cut_interval_bars=1.0, fps=24.0)
        self.assertGreaterEqual(len(cuts), 3)
        self.assertEqual(cuts[0]["cut_number"], 1)
        self.assertEqual(cuts[0]["timecode"], "00:00:00:00")


class TestAudioAnalysis(unittest.TestCase):
    """Capability 81: Audio Analysis"""

    def test_analyze_audio_samples(self):
        # Generate 1 second of 440Hz test sine wave at -6 dBFS (amplitude approx 0.5)
        sr = 48000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        sine = 0.5 * np.sin(2 * np.pi * 440.0 * t)

        analysis = AudioAnalyzer.analyze_samples(sine, sample_rate=sr)
        self.assertAlmostEqual(analysis["peak_level_amplitude"], 0.5, places=2)
        self.assertAlmostEqual(analysis["peak_level_dbfs"], -6.02, places=1)
        self.assertFalse(analysis["clipping"]["detected"])
        self.assertIn("integrated_lufs", analysis)
        self.assertIn("ebu_r128", analysis["compliance_checks"])

    def test_clipping_detection(self):
        # Array with clipped samples
        samples = np.array([0.1, 0.5, 1.0, 1.0, 0.2, -1.0], dtype=np.float32)
        analysis = AudioAnalyzer.analyze_samples(samples, sample_rate=48000)
        self.assertTrue(analysis["clipping"]["detected"])
        self.assertEqual(analysis["clipping"]["clipped_samples"], 3)


class TestMusicProductionAssistance(unittest.TestCase):
    """Capability 82: Music Production Assistance"""

    def test_get_scale_notes(self):
        c_major = MusicProductionAssistant.get_scale_notes("C", "major", octave=4)
        note_names = [n["note"] for n in c_major]
        self.assertEqual(note_names, ["C", "D", "E", "F", "G", "A", "B"])
        self.assertEqual(c_major[0]["midi_number"], 60)  # Middle C

    def test_generate_chord_progression(self):
        prog = MusicProductionAssistant.generate_chord_progression("C", "major", ["I", "V", "vi", "IV"])
        self.assertEqual(len(prog), 4)
        self.assertEqual(prog[0]["chord_name"], "C")
        self.assertEqual(prog[1]["chord_name"], "G")
        self.assertEqual(prog[2]["chord_name"], "Am")
        self.assertEqual(prog[3]["chord_name"], "F")
        self.assertEqual(prog[0]["midi_notes"], [60, 64, 67])

    def test_calculate_delay_reverb_times(self):
        times = MusicProductionAssistant.calculate_delay_reverb_times(bpm=120.0)
        self.assertEqual(times["quarter_note_ms"], 500.0)
        self.assertEqual(times["eighth_note_ms"], 250.0)
        self.assertEqual(times["dotted_eighth_ms"], 375.0)

    def test_generate_midi_file_bytes(self):
        prog = MusicProductionAssistant.generate_chord_progression("C", "major", ["I", "V"])
        midi_bytes = MusicProductionAssistant.generate_midi_file_bytes(prog, bpm=120)
        self.assertTrue(midi_bytes.startswith(b"MThd"))
        self.assertIn(b"MTrk", midi_bytes)
        self.assertGreater(len(midi_bytes), 30)


class TestGraphicDesignAssistance(unittest.TestCase):
    """Capability 83: Graphic Design Assistance"""

    def test_hex_rgb_conversions(self):
        rgb = GraphicDesignAssistant.hex_to_rgb("#00E5FF")  # Neon cyan
        self.assertEqual(rgb, (0, 229, 255))
        hex_back = GraphicDesignAssistant.rgb_to_hex(0, 229, 255)
        self.assertEqual(hex_back, "#00E5FF")

    def test_contrast_ratio_wcag(self):
        # Black on White: 21:1
        res = GraphicDesignAssistant.calculate_contrast_ratio("#000000", "#FFFFFF")
        self.assertEqual(res["contrast_ratio"], 21.0)
        self.assertTrue(res["wcag_aa_normal_text"])
        self.assertTrue(res["wcag_aaa_normal_text"])

        # Low contrast gray on white
        low_res = GraphicDesignAssistant.calculate_contrast_ratio("#CCCCCC", "#FFFFFF")
        self.assertFalse(low_res["wcag_aa_normal_text"])

    def test_generate_color_palette(self):
        palette = GraphicDesignAssistant.generate_color_palette("#00E5FF", harmony_type="complementary")
        self.assertEqual(palette["harmony_type"], "complementary")
        self.assertEqual(len(palette["swatches"]), 2)
        self.assertEqual(palette["swatches"][0]["hex"], "#00E5FF")

    def test_generate_typography_scale(self):
        scale = GraphicDesignAssistant.generate_typography_scale(base_size_px=16.0, scale_ratio_name="golden_ratio")
        self.assertEqual(scale["base_size_px"], 16.0)
        self.assertEqual(scale["hierarchy"][2]["font_size_px"], 16.0)  # Step 0
        self.assertGreater(scale["hierarchy"][7]["font_size_px"], 40.0)  # Step 5 (H1)


class TestImageAnalysis(unittest.TestCase):
    """Capability 84: Image Analysis"""

    def test_analyze_composition_and_lighting(self):
        # Create a synthetic 120x120 test image with a bright feature in the top-left rule of thirds point
        arr = np.zeros((120, 120, 3), dtype=np.uint8)
        # Put bright patch at top left intersection (x=40, y=40)
        arr[30:50, 30:50] = 240

        analysis = ImageAnalyzer.analyze_composition_and_lighting(arr)
        self.assertEqual(analysis["dimensions"]["width"], 120)
        self.assertEqual(analysis["dimensions"]["height"], 120)
        self.assertIn("lighting_assessment", analysis)
        self.assertIn("rule_of_thirds_intersections", analysis["composition_assessment"])
        self.assertEqual(analysis["composition_assessment"]["dominant_focal_intersection"], "top_left")


class TestAnimationPlanning(unittest.TestCase):
    """Capability 85: Animation Planning"""

    def test_calculate_easing_curve(self):
        curve = AnimationPlanner.calculate_easing_curve("ease_in_out", steps=10)
        self.assertEqual(len(curve), 10)
        self.assertEqual(curve[0]["eased_value"], 0.0)
        self.assertEqual(curve[-1]["eased_value"], 1.0)
        # Verify midpoint smooth inflection (t = 4/9 ≈ 0.4444 -> val ≈ 0.417)
        self.assertAlmostEqual(curve[4]["eased_value"], 0.417, places=2)

    def test_generate_timing_sheet(self):
        beats = [
            {"duration_frames": 8, "action": "Crouch anticipation", "phoneme": "O", "camera": "Hold"},
            {"duration_frames": 16, "action": "Upward jump leap", "phoneme": "AH", "camera": "Pan up"}
        ]
        sheet = AnimationPlanner.generate_timing_sheet(beats, fps=24)
        self.assertEqual(sheet["total_frames"], 24)
        self.assertEqual(sheet["x_sheet"][0]["type"], "KEY")
        self.assertEqual(sheet["x_sheet"][0]["drawing_label"], "K1")
        self.assertEqual(sheet["x_sheet"][4]["type"], "BREAKDOWN")

    def test_audit_animation_shot(self):
        audit = AnimationPlanner.audit_animation_shot("Character launches off rooftop.", "organic_humanoid")
        self.assertGreaterEqual(len(audit["principles_checklist"]), 4)


class TestVFXPlanning(unittest.TestCase):
    """Capability 86: VFX Planning"""

    def test_generate_pass_breakdown(self):
        breakdown = VFXPlanner.generate_pass_breakdown("Hovercraft engine exhaust composite.")
        self.assertGreaterEqual(breakdown["total_passes"], 10)
        pass_names = [p["name"] for p in breakdown["passes"]]
        self.assertIn("Beauty / Combined", pass_names)
        self.assertIn("Ambient Occlusion (AO)", pass_names)
        self.assertIn("Z-Depth", pass_names)
        self.assertIn("Motion Vectors", pass_names)

    def test_green_screen_guide(self):
        guide = VFXPlanner.green_screen_extraction_guide()
        self.assertIn("backdrop_lighting", guide)
        self.assertIn("extraction_workflow", guide)
        step_names = [s["step"] for s in guide["extraction_workflow"]]
        self.assertIn("Spill Suppression", step_names)

    def test_plan_camera_tracking(self):
        tracking = VFXPlanner.plan_camera_tracking()
        self.assertGreaterEqual(tracking["tracking_requirements"]["minimum_track_points"], 80)


class TestBrandIntelligence(unittest.TestCase):
    """Capability 87: Brand Intelligence"""

    def test_create_brand_guidelines(self):
        guide = BrandIntelligence.create_brand_guidelines(
            brand_name="Aether Systems",
            tagline="Precision in Motion",
            primary_palette={"cyan": "#00E5FF", "obsidian": "#0A0E17"},
            secondary_palette={"accent_purple": "#7B1FA2"},
            typography_specs={"heading": "Inter", "body": "Roboto"},
            tone_pillars=["Visionary", "Precise", "Authoritative"]
        )
        self.assertEqual(guide["brand_identity"]["name"], "Aether Systems")
        self.assertEqual(guide["color_system"]["primary"]["cyan"], "#00E5FF")
        self.assertIn("logo_clearspace_rule", guide)

    def test_audit_color_consistency(self):
        brand_palette = {"Primary Cyan": "#00E5FF", "Deep Slate": "#1A202C"}
        # Exact match
        exact_res = BrandIntelligence.audit_color_consistency("#00E5FF", brand_palette)
        self.assertTrue(exact_res["is_on_brand"])
        self.assertEqual(exact_res["distance_to_closest"], 0.0)

        # Large mismatch
        mismatch_res = BrandIntelligence.audit_color_consistency("#FF0000", brand_palette)
        self.assertFalse(mismatch_res["is_on_brand"])

    def test_evaluate_tone_of_voice(self):
        good_copy = "The autonomous core operates with precise deterministic latency. Our architecture is visionary."
        eval_good = BrandIntelligence.evaluate_tone_of_voice(good_copy)
        self.assertGreaterEqual(eval_good["formality_score_100"], 80.0)
        self.assertIn("precise", eval_good["aligned_pillars"])

        bad_copy = "Hey guys, this is gonna be totally crazy lol omg!"
        eval_bad = BrandIntelligence.evaluate_tone_of_voice(bad_copy)
        self.assertLess(eval_bad["formality_score_100"], 50.0)


class TestSocialMediaManagement(unittest.TestCase):
    """Capability 88: Social Media Management"""

    def test_generate_post_schedule(self):
        sched = SocialMediaManager.generate_post_schedule("Product Launch 2026", duration_days=5)
        self.assertEqual(sched["duration_days"], 5)
        self.assertEqual(sched["total_posts_planned"], 15)  # 5 days * 3 default platforms

    def test_develop_hashtag_strategy(self):
        tags = SocialMediaManager.develop_hashtag_strategy("Autonomous AI", "Launch")
        self.assertIn("#AutonomousAI", tags["tier_1_broad_reach"])
        self.assertIn("platform_best_practices", tags)

    def test_draft_social_copy(self):
        tweet = SocialMediaManager.draft_social_copy("Agentic Architecture", platform="twitter")
        self.assertTrue(tweet["within_limit"])
        self.assertLessEqual(tweet["character_count"], 280)


class TestCreativeAssetManagement(unittest.TestCase):
    """Capability 89: Creative Asset Management"""

    def setUp(self):
        self.cam = CreativeAssetManager()
        self.cam.catalog_asset(
            asset_id="AST_001",
            file_name="hero_banner.png",
            media_type="image",
            width=3840,
            height=2160,
            tags=["hero", "4k", "marketing"]
        )
        self.cam.catalog_asset(
            asset_id="AST_002",
            file_name="teaser_clip.mp4",
            media_type="video",
            width=1920,
            height=1080,
            duration_sec=30.0,
            tags=["teaser", "social"]
        )

    def test_catalog_and_search(self):
        results = self.cam.search_catalog(tag="hero")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["asset_id"], "AST_001")

        vid_results = self.cam.search_catalog(media_type="video")
        self.assertEqual(len(vid_results), 1)

    def test_validate_delivery_specs(self):
        asset = self.cam.catalog["AST_001"]
        # Exact 4K UHD check
        val = CreativeAssetManager.validate_delivery_specs(
            asset_metadata=asset,
            required_width=3840,
            required_height=2160,
            required_aspect_ratio=1.777
        )
        self.assertTrue(val["conforms_to_specs"])

        # Fail check
        fail_val = CreativeAssetManager.validate_delivery_specs(
            asset_metadata=asset,
            required_width=1080,
            required_height=1920
        )
        self.assertFalse(fail_val["conforms_to_specs"])


class TestProductionDocumentation(unittest.TestCase):
    """Capability 90: Production Documentation"""

    def test_generate_budget_sheet(self):
        items = [
            {"category": "ATL", "description": "Director Fee", "rate": 5000.0, "quantity": 1},
            {"category": "BTL", "description": "Camera Package Rental", "rate": 800.0, "quantity": 3},
            {"category": "POST", "description": "Color Grading Suite", "rate": 1500.0, "quantity": 1}
        ]
        budget = ProductionDocumentation.generate_budget_sheet(items, contingency_pct=10.0)
        self.assertEqual(budget["summary"]["above_the_line_total"], 5000.0)
        self.assertEqual(budget["summary"]["below_the_line_total"], 2400.0)
        self.assertEqual(budget["summary"]["post_production_total"], 1500.0)
        self.assertEqual(budget["summary"]["subtotal"], 8900.0)
        self.assertEqual(budget["summary"]["contingency_amount"], 890.0)
        self.assertEqual(budget["summary"]["grand_total"], 9790.0)

    def test_generate_release_form(self):
        form = ProductionDocumentation.generate_release_form(
            talent_name="Alex Mercer",
            project_name="Cybernetic Awakening",
            producer_name="Starlight Media"
        )
        self.assertEqual(form["talent_name"], "Alex Mercer")
        self.assertIn("Alex Mercer", form["legal_text"])
        self.assertIn("Cybernetic Awakening", form["legal_text"])

    def test_generate_treatment_summary(self):
        treatment = ProductionDocumentation.generate_treatment_summary(
            title="The Quantum Horizon",
            logline="A lone cartographer maps recursive simulated realities.",
            synopsis="In 2099, deep scans reveal layers of nested realities.",
            tone_and_style="Cyberpunk noir meets Tarkovsky contemplation.",
            target_audience="Sci-fi enthusiasts 18-45",
            visual_references=["Blade Runner 2049", "Solaris", "Ex Machina"]
        )
        self.assertEqual(treatment["project_title"], "The Quantum Horizon")
        self.assertEqual(len(treatment["creative_vision"]["visual_references"]), 3)


class TestCreativeIntelligenceManager(unittest.TestCase):
    """Unified Orchestration and Execution across Capabilities 76-90"""

    def test_capabilities_registry(self):
        caps = creative_manager.get_capabilities()
        self.assertEqual(len(caps), 15)
        for num in range(76, 91):
            self.assertIn(num, caps)

    def test_dynamic_execution_dispatch(self):
        # Cap 79: calculate_field_of_view
        fov = creative_manager.execute_capability(
            capability=79,
            action="calculate_field_of_view",
            sensor_width_mm=36.0,
            focal_length_mm=24.0
        )
        self.assertIn("horizontal_fov_degrees", fov)

        # Cap 83: calculate_contrast_ratio
        contrast = creative_manager.execute_capability(
            capability=83,
            action="calculate_contrast_ratio",
            hex_foreground="#000000",
            hex_background="#FFFFFF"
        )
        self.assertEqual(contrast["contrast_ratio"], 21.0)

        # Cap 88: draft_social_copy
        copy = creative_manager.execute_capability(
            capability=88,
            action="draft_social_copy",
            topic="Quantum Computing",
            platform="twitter"
        )
        self.assertIn("Quantum Computing", copy["post_copy"])


if __name__ == "__main__":
    unittest.main()
