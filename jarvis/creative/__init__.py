"""
Creative Intelligence Package for J.A.R.V.I.S. (Capabilities 76-90)
"""

from .film_production import (
    FilmProductionAssistant,
    ShotPlanner,
    ProductionDocumentation
)
from .story_development import (
    StoryDeveloper,
    StoryboardGenerator
)
from .video_audio import (
    VideoEditingAssistant,
    AudioAnalyzer,
    MusicProductionAssistant
)
from .visual_arts import (
    GraphicDesignAssistant,
    ImageAnalyzer
)
from .animation_vfx import (
    AnimationPlanner,
    VFXPlanner
)
from .marketing_assets import (
    BrandIntelligence,
    SocialMediaManager,
    CreativeAssetManager
)
from .manager import (
    CreativeIntelligenceManager,
    creative_manager,
    CAPABILITIES
)

__all__ = [
    "FilmProductionAssistant",
    "ShotPlanner",
    "ProductionDocumentation",
    "StoryDeveloper",
    "StoryboardGenerator",
    "VideoEditingAssistant",
    "AudioAnalyzer",
    "MusicProductionAssistant",
    "GraphicDesignAssistant",
    "ImageAnalyzer",
    "AnimationPlanner",
    "VFXPlanner",
    "BrandIntelligence",
    "SocialMediaManager",
    "CreativeAssetManager",
    "CreativeIntelligenceManager",
    "creative_manager",
    "CAPABILITIES"
]
