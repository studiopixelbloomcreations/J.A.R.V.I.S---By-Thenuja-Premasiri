"""
Unified Intelligence Engine for J.A.R.V.I.S.
Integrates all 15 Reasoning & Intelligence Capabilities into a cohesive system.
"""
from typing import Dict, List, Any, Optional

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


class IntelligenceEngine:
    """
    Unified Coordinator for Capabilities 1-15:
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
    def __init__(self):
        # Instantiate all 15 capability modules
        self.deep_research = DeepResearchEngine()
        self.recursive_research = RecursiveResearchPlanner(self.deep_research)
        self.hypothesis_generator = HypothesisGenerator()
        self.evidence_verifier = EvidenceVerifier()
        self.contradiction_detector = ContradictionDetector()
        self.predictive_analyzer = PredictiveAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.decision_support = DecisionSupportSystem()
        self.knowledge_synthesizer = KnowledgeSynthesizer()
        self.contextual_reasoner = ContextualReasoner()
        self.multi_agent_collab = MultiAgentCollaborator()
        self.long_term_research = LongTermResearchTracker()
        self.uncertainty_estimator = UncertaintyEstimator()
        self.literature_analyzer = LiteratureAnalyzer()
        self.report_generator = AutonomousReportGenerator()

    def execute_capability(self, capability_key: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dispatches execution to the corresponding intelligence capability handler."""
        p = params or {}
        key = str(capability_key).lower().strip()

        # Capability 1: Deep Research Engine
        if key in ("1", "deep_research", "deep_research_engine", "intel_deep_research"):
            query = p.get("query", "J.A.R.V.I.S. Architecture")
            depth = int(p.get("depth", 2))
            breadth = int(p.get("breadth", 3))
            return self.deep_research.conduct_research(query, depth=depth, breadth=breadth)

        # Capability 2: Recursive Research
        if key in ("2", "recursive_research", "intel_recursive_research"):
            query = p.get("query", "Neural Interface Architecture")
            max_depth = int(p.get("max_depth", 3))
            max_branches = int(p.get("max_branches", 2))
            return self.recursive_research.plan_and_execute(query, max_depth=max_depth, max_branches=max_branches)

        # Capability 3: Hypothesis Generation
        if key in ("3", "hypothesis_generation", "hypotheses", "intel_hypothesis_generation"):
            observation = p.get("observation", "System latency spikes during screen OCR")
            domain = p.get("domain", "system_diagnostics")
            return self.hypothesis_generator.generate_hypotheses(observation, domain=domain)

        # Capability 4: Evidence Verification
        if key in ("4", "evidence_verification", "verify_claim", "intel_evidence_verification"):
            claim = p.get("claim", "Quest 2 represents 63.77% market share.")
            sources = p.get("sources", [{"text": "Steam VR survey shows Quest family at 63.77% share.", "source": "Steam Survey"}])
            return self.evidence_verifier.verify_claim(claim, sources)

        # Capability 5: Contradiction Detection
        if key in ("5", "contradiction_detection", "compare_statements", "intel_contradiction_detection"):
            sa = p.get("statement_a", "All systems are operational and active.")
            sb = p.get("statement_b", "Primary services are inactive and offline.")
            return self.contradiction_detector.compare_statements(sa, sb)

        # Capability 6: Predictive Analysis
        if key in ("6", "predictive_analysis", "scenarios", "intel_predictive_analysis"):
            if "historical_values" in p:
                return self.predictive_analyzer.forecast_series(p["historical_values"], int(p.get("steps", 3)))
            topic = p.get("topic", "VR Headset Adoption")
            current = float(p.get("current_metric", 100.0))
            return self.predictive_analyzer.generate_scenarios(topic, current)

        # Capability 7: Pattern Recognition
        if key in ("7", "pattern_recognition", "intel_pattern_recognition"):
            if "series" in p:
                return self.pattern_recognizer.detect_numerical_anomalies(p["series"])
            entries = p.get("logs", ["Error 404 in worker", "Error 404 in worker", "Warning timeout"])
            return self.pattern_recognizer.detect_text_patterns(entries)

        # Capability 8: Decision Support
        if key in ("8", "decision_support", "intel_decision_support"):
            problem = p.get("problem", "Select optimal TTS engine")
            options = p.get("options", [
                {"name": "Fish Audio", "scores": {"latency": 9, "fidelity": 9, "local_cost": 8}},
                {"name": "Browser SpeechSynthesis", "scores": {"latency": 10, "fidelity": 6, "local_cost": 10}}
            ])
            weights = p.get("weights", {"latency": 0.4, "fidelity": 0.4, "local_cost": 0.2})
            return self.decision_support.evaluate_options(problem, options, weights)

        # Capability 9: Knowledge Synthesis
        if key in ("9", "knowledge_synthesis", "intel_knowledge_synthesis"):
            topic = p.get("topic", "Edge vs Cloud AI Execution")
            perspectives = p.get("perspectives", [
                {"perspective_name": "Edge AI", "claim": "Low latency and high privacy on device.", "evidence": "Direct inference."},
                {"perspective_name": "Cloud AI", "claim": "Massive parameter scale and reasoning power.", "evidence": "Cluster compute."}
            ])
            return self.knowledge_synthesizer.synthesize_knowledge(topic, perspectives)

        # Capability 10: Contextual Reasoning
        if key in ("10", "contextual_reasoning", "intel_contextual_reasoning"):
            directive = p.get("directive", "Optimize memory and speed up responses")
            constraints = p.get("constraints", {})
            return self.contextual_reasoner.contextualize_directive(directive, constraints)

        # Capability 11: Multi-Agent Collaboration
        if key in ("11", "multi_agent_collab", "multi_agent_collaboration", "intel_multi_agent_collab"):
            task = p.get("task", "Architect resilient 24/7 background audio monitor")
            rounds = int(p.get("rounds", 2))
            return self.multi_agent_collab.conduct_deliberation(task, rounds=rounds)

        # Capability 12: Long-Term Research
        if key in ("12", "long_term_research", "intel_long_term_research"):
            action = p.get("action", "create")
            if action == "create":
                title = p.get("title", "Neural Holographic Interface Evolution")
                obj = p.get("objective", "Develop persistent 3D spatial assistance.")
                agenda = self.long_term_research.create_agenda(title, obj, p.get("milestones"))
                return {"status": "success", "agenda": agenda, "agenda_id": agenda["agenda_id"]}
            if action == "log_evidence":
                entry = self.long_term_research.log_evidence(
                    p["agenda_id"], p["claim"], p.get("source", "Telemetry"), float(p.get("confidence", 0.85))
                )
                return {"status": "success", "entry": entry}
            if action == "summary":
                summary = self.long_term_research.get_summary(p["agenda_id"])
                return {"status": "success", "summary": summary}
            return {"status": "error", "message": f"Unknown long_term_research action: '{action}'."}

        # Capability 13: Uncertainty Estimation
        if key in ("13", "uncertainty_estimation", "intel_uncertainty_estimation"):
            probs = p.get("probabilities", [0.70, 0.20, 0.10])
            sample_count = int(p.get("sample_count", 10))
            source_count = int(p.get("source_count", 3))
            return self.uncertainty_estimator.estimate_uncertainty(probs, sample_count, source_count)

        # Capability 14: Scientific Literature Analysis
        if key in ("14", "literature_analysis", "scientific_literature_analysis", "intel_literature_analysis"):
            text = p.get("text", "A randomized controlled trial (N=1,200) showed significant improvements (p=0.002, 95% CI [0.12, 0.45]).")
            title = p.get("title", "Clinical Study")
            return self.literature_analyzer.analyze_paper(text, title=title)

        # Capability 15: Autonomous Report Generation
        if key in ("15", "autonomous_report", "report_generation", "intel_autonomous_report"):
            topic = p.get("topic", "J.A.R.V.I.S. Autonomous Reasoning Benchmark")
            return self.report_generator.generate_report(topic, research_data=p.get("research_data"))

        return {
            "status": "error",
            "message": f"Unknown intelligence capability '{capability_key}'. Valid: 1-15."
        }

    def run_full_pipeline(self, topic: str) -> Dict[str, Any]:
        """Runs an end-to-end multi-stage autonomous research and synthesis workflow."""
        # Step 1: Deep Research
        res = self.deep_research.conduct_research(topic, depth=2, breadth=3)
        # Step 2: Formulate Hypotheses
        hyp = self.hypothesis_generator.generate_hypotheses(topic)
        # Step 3: Predictive Scenarios
        pred = self.predictive_analyzer.generate_scenarios(topic, 100.0)
        # Step 4: Decision Analysis
        dec = self.decision_support.evaluate_options(
            f"Deployment Strategy for {topic}",
            [
                {"name": "Autonomous Phased Rollout", "scores": {"speed": 8, "safety": 9, "cost": 7}},
                {"name": "Immediate Full Cutover", "scores": {"speed": 10, "safety": 4, "cost": 9}}
            ],
            {"speed": 0.4, "safety": 0.4, "cost": 0.2}
        )
        # Step 5: Multi-Agent Consensus
        collab = self.multi_agent_collab.conduct_deliberation(f"Synthesize {topic}", rounds=2)
        # Step 6: Generate Executive Report
        report = self.report_generator.generate_report(topic, research_data=res, analytics_data=pred)

        return {
            "status": "success",
            "topic": topic,
            "research": res,
            "hypotheses": hyp,
            "scenarios": pred,
            "decision": dec,
            "collaboration": collab,
            "report": report
        }


# Global Intelligence Engine instance
intelligence_engine = IntelligenceEngine()
