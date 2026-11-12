"""
J.A.R.V.I.S. Automated Comprehensive Intelligence & Reasoning Test Suite
Validates Capabilities 1-15:
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
Also verifies Skill Registry, Dispatcher, and Agent Orchestrator integration.
"""
import os
import sys
import unittest
import tempfile
import shutil

# Add workspace root to sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from jarvis.intelligence.research import (
    DeepResearchEngine,
    RecursiveResearchPlanner,
    LongTermResearchTracker,
    LiteratureAnalyzer
)
from jarvis.intelligence.reasoning import (
    HypothesisGenerator,
    EvidenceVerifier,
    ContradictionDetector,
    ContextualReasoner,
    UncertaintyEstimator
)
from jarvis.intelligence.analytics import (
    PredictiveAnalyzer,
    PatternRecognizer,
    DecisionSupportSystem,
    KnowledgeSynthesizer
)
from jarvis.intelligence.collaboration import MultiAgentCollaborator
from jarvis.intelligence.reporting import AutonomousReportGenerator
from jarvis.intelligence.engine import IntelligenceEngine, intelligence_engine
from jarvis.skills.registry import registry
from jarvis.skills.handlers import dispatch_skill
from jarvis.core.orchestrator import orchestrator


class TestCapabilities1And2Research(unittest.TestCase):
    def setUp(self):
        self.mock_corpus = {
            "VR Market Overview": "Steam Hardware Survey reveals Meta Quest 2 holds 33.5% share while Quest 3 holds 17.2%. Total Quest family commands 63.77% across PC VR ecosystems. N=12000 respondents in 2024.",
            "Display Hardware Specs": "Holographic micro-OLED panels achieve 90Hz refresh rate with 15ms motion-to-photon latency. Resolution stands at 4K per eye.",
            "Neural Engine Telemetry": "J.A.R.V.I.S. reasoning pipeline utilizes dual-tier neural nexus with local fallback. Operating frequency is 3.8 GHz with 16GB RAM."
        }
        self.deep_engine = DeepResearchEngine()
        self.recursive_planner = RecursiveResearchPlanner(self.deep_engine)

    def test_01_deep_research_engine(self):
        res = self.deep_engine.conduct_research("Meta Quest VR share", depth=2, breadth=3, corpus=self.mock_corpus)
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["sources_analyzed"], 1)
        self.assertIn("key_findings", res)
        self.assertGreater(len(res["key_entities"]), 0)
        self.assertGreaterEqual(res["confidence_score"], 0.2)
        self.assertIn("63.77%", str(res["statistics_extracted"]))

    def test_02_recursive_research(self):
        res = self.recursive_planner.plan_and_execute(
            "Quest VR ecosystem", max_depth=2, max_branches=2, corpus=self.mock_corpus
        )
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["total_nodes_explored"], 1)
        self.assertIn("exploration_tree", res)
        self.assertIn("total_unique_concepts", res)
        self.assertTrue(len(res["exploration_tree"]) > 0)


class TestCapabilities3To5Reasoning(unittest.TestCase):
    def setUp(self):
        self.hyp_gen = HypothesisGenerator()
        self.verifier = EvidenceVerifier()
        self.detector = ContradictionDetector()

    def test_03_hypothesis_generation(self):
        res = self.hyp_gen.generate_hypotheses("Latency spikes to 240ms during OCR capture")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["hypotheses_count"], 4)
        hyp_ids = [h["id"] for h in res["hypotheses"]]
        self.assertIn("H0_NULL", hyp_ids)
        self.assertIn("H1_PRIMARY", hyp_ids)
        self.assertIn("H2_ALTERNATIVE", hyp_ids)
        self.assertIn("H3_EDGE", hyp_ids)
        priors_sum = sum(h["prior"] for h in res["hypotheses"])
        self.assertAlmostEqual(priors_sum, 1.0, places=2)

    def test_04_evidence_verification(self):
        sources = [
            {"text": "Official telemetry confirms Meta Quest commands 63.77% market share.", "source": "Steam Survey", "source_type": "official_documentation"}
        ]
        res_support = self.verifier.verify_claim("Meta Quest commands 63.77% market share", sources)
        self.assertEqual(res_support["status"], "success")
        self.assertEqual(res_support["verdict"], "SUPPORTED")
        self.assertGreaterEqual(res_support["confidence_score"], 0.70)

        res_refute = self.verifier.verify_claim("Meta Quest has 0% market share and is unsupported", sources)
        self.assertIn(res_refute["verdict"], ["REFUTED", "INSUFFICIENT_EVIDENCE"])

    def test_05_contradiction_detection(self):
        # Polarity inversion test
        sa = "The background audio listening service is active and enabled."
        sb = "The background audio listening service is inactive and disabled."
        res = self.detector.compare_statements(sa, sb)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_contradiction"])
        self.assertEqual(res["severity"], "FATAL")

        # Consistent statements test
        sc = "The system runs on Windows 11."
        sd = "The OS environment is Windows 11 64-bit."
        res_ok = self.detector.compare_statements(sc, sd)
        self.assertFalse(res_ok["is_contradiction"])


class TestCapabilities6To9Analytics(unittest.TestCase):
    def setUp(self):
        self.pred_analyzer = PredictiveAnalyzer()
        self.pattern_rec = PatternRecognizer()
        self.decision_sys = DecisionSupportSystem()
        self.synthesizer = KnowledgeSynthesizer()

    def test_06_predictive_analysis(self):
        # Forecast series
        hist = [10.0, 12.0, 14.5, 17.0, 20.2]
        fc = self.pred_analyzer.forecast_series(hist, forecast_steps=3)
        self.assertEqual(fc["status"], "success")
        self.assertEqual(fc["trend_direction"], "ACCELERATING_UPWARD")
        self.assertEqual(len(fc["projections"]), 3)
        self.assertGreater(fc["projections"][-1]["projected_value"], hist[-1])

        # Scenario generation
        sc = self.pred_analyzer.generate_scenarios("VR Headset Adoption", 63.77)
        self.assertEqual(sc["status"], "success")
        self.assertEqual(len(sc["scenarios"]), 4)
        prob_sum = sum(s["probability"] for s in sc["scenarios"])
        self.assertAlmostEqual(prob_sum, 1.0, places=2)

    def test_07_pattern_recognition(self):
        # Numerical anomalies (outlier detection)
        vals = [10.0, 10.2, 9.8, 10.1, 10.0, 9.9, 85.0]  # 85 is outlier
        anom = self.pattern_rec.detect_numerical_anomalies(vals, z_threshold=2.0)
        self.assertEqual(anom["status"], "success")
        self.assertTrue(anom["has_critical_anomaly"])
        self.assertGreaterEqual(anom["z_anomalies_count"], 1)

        # Text motif recognition
        logs = [
            "ConnectionTimeout: host unreachable at 10.0.0.1",
            "ConnectionTimeout: host unreachable at 10.0.0.2",
            "Service restarted successfully",
            "ConnectionTimeout: host unreachable at 10.0.0.3"
        ]
        motifs = self.pattern_rec.detect_text_patterns(logs)
        self.assertEqual(motifs["status"], "success")
        self.assertTrue(motifs["repetition_detected"])
        self.assertIn("ConnectionTimeout", motifs["detected_error_motifs"])

    def test_08_decision_support(self):
        options = [
            {"name": "Option Alpha", "scores": {"speed": 9, "accuracy": 8, "cost": 6}},
            {"name": "Option Beta", "scores": {"speed": 6, "accuracy": 9, "cost": 9}}
        ]
        weights = {"speed": 0.5, "accuracy": 0.3, "cost": 0.2}
        dec = self.decision_sys.evaluate_options("Engine Selection", options, weights)
        self.assertEqual(dec["status"], "success")
        self.assertEqual(dec["recommended_choice"], "Option Alpha")
        self.assertIn("Option Alpha", dec["tradeoff_summary"])

    def test_09_knowledge_synthesis(self):
        perspectives = [
            {"perspective_name": "Edge Execution", "claim": "Ultra low latency without network hops.", "evidence": "5ms on-device inference"},
            {"perspective_name": "Cloud Compute", "claim": "Unlimited parameter capacity and cluster scaling.", "evidence": "Gemini 3.5 reasoning"}
        ]
        syn = self.synthesizer.synthesize_knowledge("Inference Architecture", perspectives)
        self.assertEqual(syn["status"], "success")
        self.assertIn("thesis", syn["dialectic_triad"])
        self.assertIn("antithesis", syn["dialectic_triad"])
        self.assertIn("synthesis", syn["dialectic_triad"])


class TestCapabilities10To15Advanced(unittest.TestCase):
    def setUp(self):
        self.reasoner = ContextualReasoner(user_profile="User: Thenuja | OS: Windows 11 | Role: Architect")
        self.collab = MultiAgentCollaborator()
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = LongTermResearchTracker(storage_dir=self.temp_dir)
        self.uncertainty = UncertaintyEstimator()
        self.lit_analyzer = LiteratureAnalyzer()
        self.reporter = AutonomousReportGenerator(reports_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_10_contextual_reasoning(self):
        res = self.reasoner.contextualize_directive("speed up system response times")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["inferred_intent"], "PERFORMANCE_OPTIMIZATION")
        self.assertEqual(res["operating_context"]["os"], "Windows 11")
        self.assertGreaterEqual(len(res["grounded_execution_plan"]), 2)

    def test_11_multi_agent_collaboration(self):
        res = self.collab.conduct_deliberation("Design 24/7 Voice VAD monitor", rounds=2)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["rounds_conducted"], 2)
        self.assertGreaterEqual(res["consensus_score"], 0.75)
        self.assertEqual(res["consensus_verdict"], "APPROVED")
        roles = [turn["role"] for turn in res["debate_transcript"]]
        self.assertIn("Proposer", roles)
        self.assertIn("Critic", roles)
        self.assertIn("Fact-Checker", roles)
        self.assertIn("Synthesizer", roles)

    def test_12_long_term_research(self):
        agenda = self.tracker.create_agenda(
            "Spatial Holographic HUD",
            "Develop 3D orb and card projection",
            milestones=["Build Orb kinetics", "Implement 13-block deck", "Add Corner Docking"]
        )
        aid = agenda["agenda_id"]
        # Log evidence
        self.tracker.log_evidence(aid, "Orb kinetics stable at 60fps", "viewer/orb.js", 0.95)
        # Update milestone
        ms = self.tracker.update_milestone(aid, 1, "completed")
        self.assertEqual(ms["status"], "completed")
        # Hypothesis registration & Bayesian update
        hyp = self.tracker.register_hypothesis(aid, "GPU shaders reduce CPU overhead by 40%", 0.50)
        updated_hyp = self.tracker.update_hypothesis_bayes(aid, hyp["hyp_id"], 0.90, 0.20)
        self.assertGreater(updated_hyp["posterior"], 0.50)
        # Disk save & load
        save_path = self.tracker.save_to_disk(aid)
        self.assertTrue(os.path.exists(save_path))
        loaded = self.tracker.load_from_disk(save_path)
        self.assertEqual(loaded["agenda_id"], aid)

    def test_13_uncertainty_estimation(self):
        probs = [0.80, 0.15, 0.05]
        res = self.uncertainty.estimate_uncertainty(probs, sample_count=20, source_count=4)
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["shannon_entropy_bits"], 0.0)
        self.assertIn("epistemic_uncertainty", res)
        self.assertIn("aleatoric_uncertainty", res)
        self.assertIn("composite_uncertainty", res)
        self.assertIn(res["uncertainty_classification"], ["LOW_UNCERTAINTY_ROBUST", "MODERATE_UNCERTAINTY"])

    def test_14_scientific_literature_analysis(self):
        paper = (
            "A randomized controlled trial (N=1,500) evaluated spatial computing interfaces. "
            "Primary outcomes demonstrated significant cognitive speedup (p=0.001, 95% CI [0.22, 0.68], OR=2.4). "
            "Methodology employed double-blind protocol with low risk of bias."
        )
        res = self.lit_analyzer.analyze_paper(paper, title="Spatial Interfaces Trial")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["study_type"], "Randomized Controlled Trial")
        self.assertEqual(res["sample_size"], 1500)
        self.assertTrue(res["statistics"]["statistically_significant"])
        self.assertGreaterEqual(res["methodology_rigor_score"], 80.0)
        self.assertEqual(res["risk_of_bias"], "Low")

    def test_15_autonomous_report_generation(self):
        rep = self.reporter.generate_report(
            "VR Market Architecture",
            research_data={
                "key_findings": [{"source": "Steam Survey", "finding": "Quest family commands 63.77% market share."}],
                "key_entities": ["Quest 2", "Quest 3", "J.A.R.V.I.S."],
                "confidence_score": 0.95
            }
        )
        self.assertEqual(rep["status"], "success")
        self.assertTrue(os.path.exists(rep["report_file"]))
        self.assertIn("J.A.R.V.I.S. INTELLIGENCE BRIEFING", rep["full_markdown"])
        self.assertIn("hud_deck", rep)
        self.assertEqual(len(rep["hud_deck"]["blocks"]), 6)


class TestIntelligenceEngineFacade(unittest.TestCase):
    def test_all_15_capabilities_dispatch(self):
        engine = IntelligenceEngine()
        # Test capability dispatch for all 15 capabilities
        for cap_num in range(1, 16):
            res = engine.execute_capability(str(cap_num), {})
            self.assertEqual(
                res.get("status"), "success",
                f"Capability {cap_num} failed execution: {res}"
            )

    def test_full_pipeline_execution(self):
        engine = IntelligenceEngine()
        pipe_res = engine.run_full_pipeline("Holographic Neural Assistant")
        self.assertEqual(pipe_res["status"], "success")
        self.assertIn("research", pipe_res)
        self.assertIn("hypotheses", pipe_res)
        self.assertIn("scenarios", pipe_res)
        self.assertIn("decision", pipe_res)
        self.assertIn("collaboration", pipe_res)
        self.assertIn("report", pipe_res)


class TestRegistryAndOrchestratorIntegration(unittest.TestCase):
    def test_skill_registry_lookup_and_aliases(self):
        # 150 catalog skills remain untouched
        all_catalog = registry.get_all()
        self.assertEqual(len(all_catalog), 150)

        # Intelligence capabilities accessible via registry
        intel_skills = registry.get_intelligence_skills()
        self.assertEqual(len(intel_skills), 15)

        # Lookup by id and alias
        s1 = registry.get_skill("intel_deep_research")
        self.assertIsNotNone(s1)
        self.assertEqual(s1["num"], 1)

        s1_alias = registry.get_skill("deep_research")
        self.assertIsNotNone(s1_alias)
        self.assertEqual(s1_alias["name"], "Deep Research Engine")

        s15 = registry.get_skill("intel_autonomous_report")
        self.assertIsNotNone(s15)
        self.assertEqual(s15["num"], 15)

    def test_dispatch_skill_integration(self):
        res1 = dispatch_skill("intel_deep_research", {"query": "J.A.R.V.I.S."})
        self.assertEqual(res1["status"], "success")

        res3 = dispatch_skill("intel_hypothesis_generation", {"observation": "Memory saturation"})
        self.assertEqual(res3["status"], "success")

        res11 = dispatch_skill("intel_multi_agent_collab", {"task": "Audit audio telemetry"})
        self.assertEqual(res11["status"], "success")

    def test_orchestrator_intent_and_execution(self):
        intent = orchestrator.parse_intent("run deep research on quantum computing")
        self.assertEqual(intent, "intelligence_reasoning")

        resp_research = orchestrator.process_request("run deep research on neural networks")
        self.assertEqual(resp_research["state"], "EXECUTING")
        self.assertIn("Deep research completed", resp_research["answer"])

        resp_hyp = orchestrator.process_request("generate hypotheses for audio stuttering")
        self.assertEqual(resp_hyp["state"], "EXECUTING")
        self.assertIn("Formulated", resp_hyp["answer"])

        resp_collab = orchestrator.process_request("run agent debate on system architecture")
        self.assertEqual(resp_collab["state"], "EXECUTING")
        self.assertIn("Multi-agent deliberation completed", resp_collab["answer"])

        resp_rep = orchestrator.process_request("generate intelligence report on VR market analysis")
        self.assertEqual(resp_rep["state"], "EXECUTING")
        self.assertIn("Autonomous intelligence dossier compiled", resp_rep["answer"])


if __name__ == "__main__":
    unittest.main()
