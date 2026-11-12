"""
Unified Creative Intelligence Manager for J.A.R.V.I.S.
Provides unified dispatching and orchestration across Capabilities 76-90.
"""

from typing import Dict, List, Any, Optional

from .film_production import FilmProductionAssistant, ShotPlanner, ProductionDocumentation
from .story_development import StoryDeveloper, StoryboardGenerator
from .video_audio import VideoEditingAssistant, AudioAnalyzer, MusicProductionAssistant
from .visual_arts import GraphicDesignAssistant, ImageAnalyzer
from .animation_vfx import AnimationPlanner, VFXPlanner
from .marketing_assets import BrandIntelligence, SocialMediaManager, CreativeAssetManager


CAPABILITIES = {
    76: {"id": "film_production", "name": "Film Production Assistant", "class": FilmProductionAssistant},
    77: {"id": "story_development", "name": "Story Development", "class": StoryDeveloper},
    78: {"id": "storyboard_gen", "name": "Storyboard Generation", "class": StoryboardGenerator},
    79: {"id": "shot_planning", "name": "Shot Planning", "class": ShotPlanner},
    80: {"id": "video_editing", "name": "Video Editing Assistance", "class": VideoEditingAssistant},
    81: {"id": "audio_analysis", "name": "Audio Analysis", "class": AudioAnalyzer},
    82: {"id": "music_production", "name": "Music Production Assistance", "class": MusicProductionAssistant},
    83: {"id": "graphic_design", "name": "Graphic Design Assistance", "class": GraphicDesignAssistant},
    84: {"id": "image_analysis", "name": "Image Analysis", "class": ImageAnalyzer},
    85: {"id": "animation_planning", "name": "Animation Planning", "class": AnimationPlanner},
    86: {"id": "vfx_planning", "name": "VFX Planning", "class": VFXPlanner},
    87: {"id": "brand_intelligence", "name": "Brand Intelligence", "class": BrandIntelligence},
    88: {"id": "social_media", "name": "Social Media Management", "class": SocialMediaManager},
    89: {"id": "creative_assets", "name": "Creative Asset Management", "class": CreativeAssetManager},
    90: {"id": "production_docs", "name": "Production Documentation", "class": ProductionDocumentation}
}


class CreativeIntelligenceManager:
    """Unified Orchestrator for all Creative Intelligence Capabilities (76-90)."""

    def __init__(self):
        self.film_assistant = FilmProductionAssistant()
        self.story_developer = StoryDeveloper()
        self.storyboard_gen = StoryboardGenerator()
        self.shot_planner = ShotPlanner()
        self.video_editor = VideoEditingAssistant()
        self.audio_analyzer = AudioAnalyzer()
        self.music_assistant = MusicProductionAssistant()
        self.graphic_designer = GraphicDesignAssistant()
        self.image_analyzer = ImageAnalyzer()
        self.animation_planner = AnimationPlanner()
        self.vfx_planner = VFXPlanner()
        self.brand_intel = BrandIntelligence()
        self.social_manager = SocialMediaManager()
        self.asset_manager = CreativeAssetManager()
        self.prod_docs = ProductionDocumentation()

    def get_capabilities(self) -> Dict[int, Dict[str, str]]:
        """Returns catalog of supported capabilities 76-90."""
        return {num: {"id": meta["id"], "name": meta["name"]} for num, meta in CAPABILITIES.items()}

    def execute_capability(self, capability: int, action: str, **kwargs) -> Any:
        """
        Dispatches dynamic calls to specific capability handlers.
        """
        target_cap = CAPABILITIES.get(capability)
        if not target_cap:
            raise ValueError(f"Capability {capability} not found in Creative Intelligence domain (76-90).")

        # Route by capability number
        if capability == 76:
            handler = getattr(self.film_assistant, action)
        elif capability == 77:
            handler = getattr(self.story_developer, action)
        elif capability == 78:
            handler = getattr(self.storyboard_gen, action)
        elif capability == 79:
            handler = getattr(self.shot_planner, action)
        elif capability == 80:
            handler = getattr(self.video_editor, action)
        elif capability == 81:
            handler = getattr(self.audio_analyzer, action)
        elif capability == 82:
            handler = getattr(self.music_assistant, action)
        elif capability == 83:
            handler = getattr(self.graphic_designer, action)
        elif capability == 84:
            handler = getattr(self.image_analyzer, action)
        elif capability == 85:
            handler = getattr(self.animation_planner, action)
        elif capability == 86:
            handler = getattr(self.vfx_planner, action)
        elif capability == 87:
            handler = getattr(self.brand_intel, action)
        elif capability == 88:
            handler = getattr(self.social_manager, action)
        elif capability == 89:
            handler = getattr(self.asset_manager, action)
        elif capability == 90:
            handler = getattr(self.prod_docs, action)
        else:
            raise ValueError(f"Unsupported capability: {capability}")

        return handler(**kwargs)


# Global singleton instance
creative_manager = CreativeIntelligenceManager()
