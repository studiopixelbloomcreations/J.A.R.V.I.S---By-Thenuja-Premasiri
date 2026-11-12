"""
J.A.R.V.I.S. Cross-Agent End-to-End (E2E) Integration Test Suite
Validates complex multi-agent collaborative workflows across all capability subsystems:
1. Research + Knowledge Storage + Visual Presentation
2. Desktop Vision + UI Recognition + Annotation
3. Goal Decomposition + Multi-Agent Orchestration
4. Network Inventory + Security Posture Audit
"""

import os
import sys
import tempfile
import pathlib
import unittest
from typing import Dict, Any

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from PIL import Image

# 1. Research + Knowledge + Visual
from jarvis.intelligence.research import DeepResearchEngine
from jarvis.intelligence.analytics import KnowledgeSynthesizer
from jarvis.knowledge.document_understanding import DocumentUnderstandingEngine
from jarvis.knowledge.relationship_discovery import RelationshipDiscoveryEngine
from jarvis.visual.research_box import ResearchBoxPayloadGenerator, ResearchFinding, ResearchCitation, ResearchMetric
from jarvis.visual.graph_adapter import KnowledgeGraphAdapter, GraphNode, GraphLink

# 2. Desktop Vision + UI Recognition + Annotation
from jarvis.desktop.windows import list_windows
from jarvis.desktop.mouse import set_virtual_mode, move_cursor, get_cursor_position, is_virtual_mode
from jarvis.desktop.emergency import emergency
from jarvis.vision.capture import create_diagnostic_desktop_canvas, get_active_window_info
from jarvis.vision.annotator import annotate_screenshot

# 3. Goal Decomposition + Multi-Agent Orchestration
from jarvis.autonomy.goal_decomposer import GoalDecomposer, DecomposedGoal, SubGoal
from jarvis.autonomy.multi_agent import MultiAgentOrchestrator, AgentWorker, AgentRole, AgentState, AgentMessage

# 4. Network Inventory + Security Posture Audit
from jarvis.cybersecurity.network import NetworkInventoryScanner
from jarvis.cybersecurity.posture import SecurityPostureAnalyzer, PostureReport


class TestSwarmCrossAgentE2E(unittest.TestCase):
    """Integration and cross-agent regression test suite."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = pathlib.Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    # ── Workflow 1: Research + Knowledge Storage + Visual Presentation ─
    def test_workflow_research_knowledge_visual(self):
        """
        Tests multi-agent workflow:
        1. DeepResearchEngine extracts facts, entities, and stats from corpus.
        2. DocumentUnderstandingEngine & RelationshipDiscoveryEngine parse knowledge notes.
        3. ResearchBoxPayloadGenerator and DynamicGraphAdapter generate structured visual cards.
        """
        # Step 1: Research gathering
        research_engine = DeepResearchEngine()
        sample_corpus = {
            "Quantum_Compute_2026": (
                "Quantum computing architectures in 2026 reached 1,121 qubits. "
                "Coherence time improved by 45.2% using surface-17 codes. "
                "IBM, Rigetti, and Google deployed fault-tolerant logical qubits with error rates p < 0.001."
            ),
            "Cryogenic_Control": (
                "Dilution refrigerators maintain 15 mK temperatures. "
                "CMOS cryogenic controllers operate at 4.2 K, reducing wiring overhead by 80%."
            )
        }
        findings = research_engine.conduct_research(
            query="quantum computing logical qubits coherence time",
            depth=2,
            breadth=3,
            corpus=sample_corpus
        )
        self.assertIn("key_findings", findings)
        self.assertIn("key_entities", findings)
        self.assertIn("statistics_extracted", findings)
        self.assertGreaterEqual(len(findings["sources"]), 1)

        # Step 2: Knowledge parsing and relationship discovery
        doc_engine = DocumentUnderstandingEngine()
        parsed_doc = doc_engine.parse_document(
            text=sample_corpus["Quantum_Compute_2026"],
            title="Quantum_Compute_2026"
        )
        self.assertIn("word_count", parsed_doc)
        self.assertGreaterEqual(parsed_doc["word_count"], 10)

        rel_engine = RelationshipDiscoveryEngine()
        discovered_relations = rel_engine.discover_relationships(sample_corpus)
        self.assertIn("thematic_connections", discovered_relations)

        # Step 3: Visual presentation layer
        box_gen = ResearchBoxPayloadGenerator(theme="cyan_holo")
        finding_item = ResearchFinding(
            id="f-quantum-01",
            title="Fault-Tolerant Qubits Verification",
            summary=findings["key_findings"][0]["finding"] if findings["key_findings"] else "Coherence time improved by 45.2%.",
            category="Hardware",
            confidence=findings.get("confidence_score", 0.95),
            evidence=findings["statistics_extracted"]
        )
        payload = box_gen.create_payload(
            topic="Quantum Computing Verification",
            query="quantum computing logical qubits coherence time",
            summary="Quantum systems achieve fault-tolerant error rates below 0.001.",
            findings=[finding_item.summary],
            citations=[{"id": "c-01", "title": "Quantum Roadmap 2026", "url": "https://jarvis.internal/quantum"}]
        )
        self.assertEqual(payload["topic"], "Quantum Computing Verification")
        self.assertEqual(len(payload["findings"]), 1)
        self.assertIn("#00e5ff", box_gen.CYAN_ACCENT)

        # Knowledge graph visual adapter
        graph_adapter = KnowledgeGraphAdapter()
        graph_adapter.load_from_dict({
            "nodes": [
                {"id": "quantum", "label": "Quantum Computing", "group": "tech"},
                {"id": "cryo", "label": "Cryogenic Control", "group": "hardware"}
            ],
            "links": [
                {"source": "quantum", "target": "cryo", "relation": "requires"}
            ]
        })
        graph_payload = graph_adapter.to_3d_force_graph_payload()
        self.assertEqual(len(graph_payload["nodes"]), 2)
        self.assertEqual(len(graph_payload["links"]), 1)

    # ── Workflow 2: Desktop Vision + UI Recognition + Annotation ───────
    def test_workflow_desktop_vision_ui_annotation(self):
        """
        Tests multi-agent workflow:
        1. Capture diagnostic or desktop canvas with active window info.
        2. Manipulate virtual cursor with safety invariants.
        3. Render non-destructive annotations (bounding boxes, steps, arrows).
        """
        # Step 1: Capture diagnostic surface
        canvas = create_diagnostic_desktop_canvas(w=1280, h=720, window_title="Visual Inspector")
        self.assertIsInstance(canvas, Image.Image)
        self.assertEqual(canvas.size, (1280, 720))

        test_img_path = self.temp_path / "desktop_capture.png"
        canvas.save(str(test_img_path))
        self.assertTrue(test_img_path.exists())

        # Step 2: Virtual cursor and emergency invariant
        set_virtual_mode(True)
        self.assertTrue(is_virtual_mode())
        move_cursor(450, 320, smooth=False)
        pos = get_cursor_position()
        self.assertEqual(pos, (450, 320))

        # Check emergency safety interface
        self.assertFalse(emergency.is_stopped)

        # Step 3: Screen annotation engine
        annotations = [
            {"type": "box", "x": 100, "y": 80, "w": 250, "h": 60, "color": "#00e5ff", "label": "Search Capsule"},
            {"type": "step", "x": 100, "y": 160, "step_num": 1, "text": "Execute Diagnostics"},
            {"type": "arrow", "from_x": 225, "from_y": 140, "to_x": 225, "to_y": 200, "color": "#00e5ff"}
        ]
        result = annotate_screenshot(str(test_img_path), annotations)
        self.assertIn("file_path", result)
        self.assertIn("base64", result)
        self.assertTrue(pathlib.Path(result["file_path"]).exists())

    # ── Workflow 3: Goal Decomposition + Multi-Agent Orchestration ────
    def test_workflow_goal_decomposition_multi_agent(self):
        """
        Tests multi-agent workflow:
        1. GoalDecomposer analyzes high-level goal and generates phased sub-goals.
        2. MultiAgentOrchestrator enrolls specialized agents, delegates tasks, and routes messages.
        """
        decomposer = GoalDecomposer()
        goal_text = "Perform end-to-end security audit and deploy hardened production build"
        decomposed = decomposer.decompose(goal_text)

        self.assertIsInstance(decomposed, DecomposedGoal)
        self.assertGreaterEqual(len(decomposed.sub_goals), 2)
        markdown_plan = decomposed.to_markdown_plan()
        self.assertIn("Execution Plan", markdown_plan)

        # Multi-Agent Swarm Orchestration
        orchestrator = MultiAgentOrchestrator()

        agent_sec = AgentWorker(
            agent_id="sec-01",
            name="security-auditor",
            role=AgentRole.SECURITY,
            capabilities=["security_audit", "vulnerability_scan"]
        )
        agent_coder = AgentWorker(
            agent_id="code-01",
            name="software-engineer",
            role=AgentRole.CODER,
            capabilities=["code_hardening", "deployment"]
        )

        orchestrator.register_agent(agent_sec)
        orchestrator.register_agent(agent_coder)
        self.assertEqual(len(orchestrator.get_roster()), 2)

        # Delegate sub-goals via messaging
        first_subgoal = decomposed.sub_goals[0]
        msg = orchestrator.post_message(
            sender="coordinator",
            recipient="security-auditor",
            content=f"Execute Phase {first_subgoal.phase}: {first_subgoal.title}",
            msg_type="TASK_ASSIGN",
            payload={"subgoal_id": first_subgoal.id, "risk": first_subgoal.risk_level}
        )
        self.assertEqual(len(agent_sec.inbox), 1)
        self.assertEqual(agent_sec.inbox[0].msg_type, "TASK_ASSIGN")

        # Security auditor handoff to software engineer
        handoff_msg = orchestrator.post_message(
            sender="security-auditor",
            recipient="software-engineer",
            content="Audit complete. Vulnerability report attached. Ready for hardening patch.",
            msg_type="HANDOFF",
            payload={"findings_count": 0, "status": "VERIFIED"}
        )
        self.assertEqual(len(agent_coder.inbox), 1)
        self.assertEqual(agent_coder.inbox[0].sender, "security-auditor")
        self.assertEqual(len(orchestrator.message_board), 2)

    # ── Workflow 4: Network Inventory + Security Posture Audit ────────
    def test_workflow_network_inventory_security_posture(self):
        """
        Tests multi-agent workflow:
        1. NetworkInventoryScanner queries local network interfaces and checks host reachability.
        2. SecurityPostureAnalyzer evaluates host configuration, privileges, and posture grade.
        """
        # Step 1: Network Inventory
        scanner = NetworkInventoryScanner()
        interfaces = scanner.get_local_interfaces()
        self.assertIsInstance(interfaces, list)
        self.assertGreaterEqual(len(interfaces), 1)

        # Step 2: Security Posture Assessment
        analyzer = SecurityPostureAnalyzer()
        report = analyzer.assess_posture()

        self.assertIsInstance(report, PostureReport)
        self.assertGreaterEqual(report.score, 0)
        self.assertLessEqual(report.score, 100)
        self.assertIn(report.grade, ["A", "B", "C", "D", "F"])
        self.assertIn("score", report.to_dict())
        self.assertIsInstance(report.findings, list)


if __name__ == "__main__":
    unittest.main()
