"""
Story Development and Storyboard Generation Module for J.A.R.V.I.S.
Covers Capabilities:
  - 77. Story Development (Three-act structure, hero's journey, character arcs)
  - 78. Storyboard Generation (Scene description, camera setup, visual prompt cards)
"""

from typing import Dict, List, Any, Optional


class StoryDeveloper:
    """Capability 77: Story Development"""

    @staticmethod
    def build_three_act_structure(
        premise: str,
        protagonist: str,
        antagonist: str,
        core_conflict: str,
        stakes: str = "Survival and existential identity"
    ) -> Dict[str, Any]:
        """
        Constructs a complete Hollywood standard 3-Act / 8-Sequence narrative architecture.
        """
        act_1 = {
            "name": "Act I - The Setup (Pages 1-30)",
            "beats": [
                {"beat": "Status Quo / Hook", "description": f"Introduce {protagonist} in their normal world under pressure."},
                {"beat": "Inciting Incident", "description": f"An unexpected catalyst ruptures stability: {core_conflict}."},
                {"beat": "Call to Action / Reluctance", "description": f"{protagonist} attempts to resist entering the conflict."},
                {"beat": "Plot Point 1 (Break into Act II)", "description": f"Decisive choice locks {protagonist} on the path of no return against {antagonist}."}
            ]
        }

        act_2 = {
            "name": "Act II - Confrontation (Pages 31-90)",
            "beats": [
                {"beat": "Fun & Games / The Promise of the Premise", "description": f"{protagonist} navigates the new world, gaining allies and initial small victories."},
                {"beat": "Midpoint Shift", "description": f"Stakes elevate from proactive desire to urgent survival ({stakes}); false victory or defeat."},
                {"beat": "Antagonist Retaliation", "description": f"{antagonist} mounts a devastating counteroffensive, isolating the hero."},
                {"beat": "All Is Lost / Dark Night of the Soul", "description": f"Catastrophic failure; the mentor or plan is destroyed; protagonist faces inner despair."},
                {"beat": "Plot Point 2 (Break into Act III)", "description": f"A crucial epiphany reveals the only truth or vulnerability to confront {antagonist}."}
            ]
        }

        act_3 = {
            "name": "Act III - Resolution (Pages 91-110)",
            "beats": [
                {"beat": "The Final Battle / Climax", "description": f"Direct confrontation between {protagonist} and {antagonist} requiring moral sacrifice."},
                {"beat": "Resolution / The New Normal", "description": f"The dust settles; a transformed world and internalized maturity for {protagonist}."}
            ]
        }

        return {
            "premise": premise,
            "protagonist": protagonist,
            "antagonist": antagonist,
            "core_conflict": core_conflict,
            "stakes": stakes,
            "acts": [act_1, act_2, act_3]
        }

    @staticmethod
    def build_heros_journey(
        hero_profile: Dict[str, str],
        call_to_adventure: str,
        mentor: str,
        ultimate_boon: str
    ) -> Dict[str, Any]:
        """
        Generates Joseph Campbell / Christopher Vogler's 12-Stage Hero's Journey.
        """
        hero_name = hero_profile.get("name", "The Hero")

        stages = [
            {"step": 1, "stage": "Ordinary World", "desc": f"{hero_name} lives in an unfulfilling or constrained status quo."},
            {"step": 2, "stage": "Call to Adventure", "desc": call_to_adventure},
            {"step": 3, "stage": "Refusal of the Call", "desc": f"{hero_name} hesitates due to fear, obligation, or self-doubt."},
            {"step": 4, "stage": "Meeting the Mentor", "desc": f"{mentor} provides wisdom, a talisman, or training."},
            {"step": 5, "stage": "Crossing the First Threshold", "desc": f"{hero_name} commits irrevocably to the Special World."},
            {"step": 6, "stage": "Tests, Allies, and Enemies", "desc": "Navigating challenges and identifying loyal companions."},
            {"step": 7, "stage": "Approach to the Inmost Cave", "desc": "Preparations and strategy at the heart of darkness."},
            {"step": 8, "stage": "The Ordeal", "desc": "Direct brush with death, testing supreme resilience."},
            {"step": 9, "stage": "Reward (Seizing the Sword)", "desc": f"{hero_name} acquires {ultimate_boon}."},
            {"step": 10, "stage": "The Road Back", "desc": "The return journey fraught with pursuit or countdown urgency."},
            {"step": 11, "stage": "The Resurrection", "desc": "Final supreme test where the old self dies and the true hero emerges."},
            {"step": 12, "stage": "Return with the Elixir", "desc": f"Returning home bringing {ultimate_boon} to heal the community."}
        ]

        return {
            "hero": hero_name,
            "mentor": mentor,
            "total_stages": len(stages),
            "journey": stages
        }

    @staticmethod
    def build_character_arc(
        character_name: str,
        role: str,
        internal_flaw: str,
        external_want: str,
        internal_need: str,
        arc_type: str = "positive_change"
    ) -> Dict[str, Any]:
        """
        Creates an in-depth psychological character arc mapping internal need vs external want.
        """
        return {
            "character_name": character_name,
            "role": role,
            "arc_type": arc_type,
            "core_psychology": {
                "the_lie_they_believe": internal_flaw,
                "the_want_external_goal": external_want,
                "the_need_spiritual_truth": internal_need
            },
            "progression_milestones": [
                {"phase": "Act I - Entrenched in the Lie", "behavior": f"Relies on {internal_flaw} to cope with life."},
                {"phase": "Midpoint - The Glimpse of Truth", "behavior": f"Tastes success when acting on {internal_need}, but fear lingers."},
                {"phase": "Crisis - The Choice Point", "behavior": f"Forced to choose between {external_want} and {internal_need}."},
                {"phase": "Climax - Transformation", "behavior": f"Surrenders {external_want} to embrace {internal_need} and defeat the ultimate obstacle."}
            ]
        }

    @staticmethod
    def analyze_story_pacing(scenes_with_tension: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes narrative pacing curve across scenes based on tension levels (1-10).
        Identifies flat spots, sudden drops, and climax placement.
        """
        if not scenes_with_tension:
            return {"status": "empty", "recommendations": ["No scene data provided."]}

        tensions = [float(s.get("tension", 5.0)) for s in scenes_with_tension]
        avg_tension = sum(tensions) / len(tensions)
        max_tension = max(tensions)
        climax_index = tensions.index(max_tension)
        relative_climax_position = (climax_index + 1) / len(tensions)

        warnings = []
        # Check if climax happens too early (should usually be between 75% and 92% of the story)
        if relative_climax_position < 0.65:
            warnings.append(f"Climax occurs too early at scene {climax_index + 1} ({round(relative_climax_position * 100)}% through story). Recommend shifting peak tension to final act.")
        elif relative_climax_position > 0.98:
            warnings.append("Climax is at the very final moment with insufficient room for satisfying denouement.")

        # Check for consecutive flat spots
        flat_stretches = 0
        for i in range(1, len(tensions)):
            if abs(tensions[i] - tensions[i-1]) < 0.3 and tensions[i] < 4.0:
                flat_stretches += 1

        if flat_stretches >= 2:
            warnings.append("Detected multiple consecutive low-tension scenes; consider raising stakes or condensing exposition.")

        return {
            "total_scenes_evaluated": len(scenes_with_tension),
            "average_tension": round(avg_tension, 2),
            "peak_tension": max_tension,
            "climax_scene_number": climax_index + 1,
            "climax_relative_position_pct": round(relative_climax_position * 100, 1),
            "pacing_health": "Healthy" if not warnings else "Needs Adjustment",
            "critique": warnings if warnings else ["Tension curve follows a solid dramatic escalation."]
        }


class StoryboardGenerator:
    """Capability 78: Storyboard Generation"""

    @staticmethod
    def generate_storyboard_deck(
        scene_beats: List[Dict[str, Any]],
        visual_style: str = "35mm anamorphic cinematic film, moody atmospheric lighting"
    ) -> Dict[str, Any]:
        """
        Generates production storyboard prompt cards with technical camera setup,
        action notes, and generative AI prompt strings.
        """
        cards = []
        for idx, beat in enumerate(scene_beats, start=1):
            panel_num = beat.get("panel_number", idx)
            shot_type = beat.get("shot_type", "Medium Shot")
            action = beat.get("action", "Character moves into frame.")
            environment = beat.get("environment", "Modern industrial research lab")
            lighting = beat.get("lighting", "Cyan edge backlight with warm key")
            lens = beat.get("lens", "50mm prime, f/1.8 shallow depth of field")
            dialogue = beat.get("dialogue", "")

            # Formulate generative AI prompt
            ai_prompt = (
                f"{shot_type} of {action}. Setting: {environment}. "
                f"Lighting: {lighting}. Optics: Shot on {lens}. "
                f"Aesthetic: {visual_style}, hyper-realistic, 8k resolution, octane render, masterpiece."
            )

            cards.append({
                "panel_id": f"P-{panel_num:02d}",
                "shot_type": shot_type,
                "lens_focal_length": lens,
                "environment": environment,
                "lighting_setup": lighting,
                "visual_action": action,
                "dialogue_audio": dialogue,
                "generative_visual_prompt": ai_prompt
            })

        return {
            "style_theme": visual_style,
            "total_panels": len(cards),
            "panels": cards
        }

    @staticmethod
    def format_prompt_card(card_data: Dict[str, Any]) -> str:
        """
        Formats a storyboard card into a cleanly formatted production card text.
        """
        return (
            f"=== STORYBOARD PANEL {card_data.get('panel_id', '01')} ===\n"
            f"SHOT TYPE: {card_data.get('shot_type')}\n"
            f"LENS: {card_data.get('lens_focal_length')}\n"
            f"LIGHTING: {card_data.get('lighting_setup')}\n"
            f"ACTION: {card_data.get('visual_action')}\n"
            f"DIALOGUE: {card_data.get('dialogue_audio') or '[NO DIALOGUE]'}\n"
            f"AI PROMPT: {card_data.get('generative_visual_prompt')}\n"
            f"================================="
        )
