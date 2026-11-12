"""
J.A.R.V.I.S. Intelligence and Reasoning Subsystem
Owns Capabilities 1-15:
1. Deep Research Engine
2. Recursive Research
3. Hypothesis Generation
4. Evidence Verification
5. Contradiction Detection
6. Predictive Analysis
7. Pattern Recognition
8. Decision Support
9. Knowledge Synthesis
10. Contextual Reasoning
11. Multi-Agent Collaboration
12. Long-Term Research
13. Uncertainty Estimation
14. Scientific Literature Analysis
15. Autonomous Report Generation
"""
from .research import (
    DeepResearchEngine,
    RecursiveResearchPlanner,
    LongTermResearchTracker,
    LiteratureAnalyzer
)
from .reasoning import (
    HypothesisGenerator,
    EvidenceVerifier,
    ContradictionDetector,
    ContextualReasoner,
    UncertaintyEstimator
)
from .analytics import (
    PredictiveAnalyzer,
    PatternRecognizer,
    DecisionSupportSystem,
    KnowledgeSynthesizer
)
from .collaboration import MultiAgentCollaborator
from .reporting import AutonomousReportGenerator
from .engine import IntelligenceEngine, intelligence_engine

__all__ = [
    "DeepResearchEngine",
    "RecursiveResearchPlanner",
    "HypothesisGenerator",
    "EvidenceVerifier",
    "ContradictionDetector",
    "PredictiveAnalyzer",
    "PatternRecognizer",
    "DecisionSupportSystem",
    "KnowledgeSynthesizer",
    "ContextualReasoner",
    "MultiAgentCollaborator",
    "LongTermResearchTracker",
    "UncertaintyEstimator",
    "LiteratureAnalyzer",
    "AutonomousReportGenerator",
    "IntelligenceEngine",
    "intelligence_engine"
]
