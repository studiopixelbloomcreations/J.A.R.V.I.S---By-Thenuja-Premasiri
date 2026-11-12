"""
J.A.R.V.I.S. Visual Intelligence System (Capabilities 126 - 135)
Provides modular visual data payload generators, pure SVG chart and diagram renderers,
holographic HUD widgets, screen annotation, 3D geometric projections, and image comparison.

CRITICAL DIRECTIVE: Protected 3D galaxy visualization in viewer/index.html is NOT modified.
All visual components serve as modular data payloads, SVG/Canvas generators, or overlay layers.
"""

from .research_box import (
    ResearchBoxPayloadGenerator,
    ResearchFinding,
    ResearchCitation,
    ResearchMetric,
)
from .graph_adapter import (
    KnowledgeGraphAdapter,
    GraphNode,
    GraphLink,
)
from .holographic import (
    HolographicPanelGenerator,
)
from .timeline import (
    TimelineVisualizer,
    TimelineEvent,
    TimelineMilestone,
)
from .dashboards import (
    StatisticalDashboardGenerator,
)
from .task_visualizer import (
    LiveTaskVisualizer,
    TaskNode,
)
from .screen_annotation import (
    ScreenAnnotationEngine,
)
from .comparison import (
    VisualComparisonEngine,
    ComparisonResult,
    DiffRegion,
)
from .three_d import (
    ThreeDDataVisualizer,
    Point3D,
    Vector3D,
)
from .overlays import (
    ContextualOverlayEngine,
    HUDPill,
    FloatingTooltip,
)

# Capability mapping
CAPABILITY_METADATA = {
    126: {"name": "Interactive Research Boxes", "module": "research_box", "class": "ResearchBoxPayloadGenerator"},
    127: {"name": "Dynamic Knowledge Graph Data Adapter", "module": "graph_adapter", "class": "KnowledgeGraphAdapter"},
    128: {"name": "Holographic-Style Data Panels", "module": "holographic", "class": "HolographicPanelGenerator"},
    129: {"name": "Timeline Visualization", "module": "timeline", "class": "TimelineVisualizer"},
    130: {"name": "Statistical Dashboards", "module": "dashboards", "class": "StatisticalDashboardGenerator"},
    131: {"name": "Live Task Visualization", "module": "task_visualizer", "class": "LiveTaskVisualizer"},
    132: {"name": "Screen Annotation", "module": "screen_annotation", "class": "ScreenAnnotationEngine"},
    133: {"name": "Visual Comparison", "module": "comparison", "class": "VisualComparisonEngine"},
    134: {"name": "3D Data Visualization", "module": "three_d", "class": "ThreeDDataVisualizer"},
    135: {"name": "Contextual Visual Overlays", "module": "overlays", "class": "ContextualOverlayEngine"},
}


class VisualIntelligence:
    """
    Unified entry point for J.A.R.V.I.S. Visual Intelligence subsystems.
    """

    def __init__(self):
        self.research = ResearchBoxPayloadGenerator()
        self.graph = KnowledgeGraphAdapter()
        self.holo = HolographicPanelGenerator()
        self.timeline = TimelineVisualizer()
        self.dashboards = StatisticalDashboardGenerator()
        self.tasks = LiveTaskVisualizer()
        self.comparison = VisualComparisonEngine()
        self.three_d = ThreeDDataVisualizer()
        self.overlays = ContextualOverlayEngine()

    def create_screen_annotator(self, base_image=None, width=1920, height=1080):
        return ScreenAnnotationEngine(base_image=base_image, width=width, height=height)


# Global singleton instance
visual_intelligence = VisualIntelligence()

__all__ = [
    "ResearchBoxPayloadGenerator",
    "ResearchFinding",
    "ResearchCitation",
    "ResearchMetric",
    "KnowledgeGraphAdapter",
    "GraphNode",
    "GraphLink",
    "HolographicPanelGenerator",
    "TimelineVisualizer",
    "TimelineEvent",
    "TimelineMilestone",
    "StatisticalDashboardGenerator",
    "LiveTaskVisualizer",
    "TaskNode",
    "ScreenAnnotationEngine",
    "VisualComparisonEngine",
    "ComparisonResult",
    "DiffRegion",
    "ThreeDDataVisualizer",
    "Point3D",
    "Vector3D",
    "ContextualOverlayEngine",
    "HUDPill",
    "FloatingTooltip",
    "CAPABILITY_METADATA",
    "VisualIntelligence",
    "visual_intelligence",
]
