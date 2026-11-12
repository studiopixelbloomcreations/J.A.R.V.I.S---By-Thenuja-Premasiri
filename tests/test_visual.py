"""
J.A.R.V.I.S. Visual Intelligence Comprehensive Unit Test Suite
Validates Capabilities 126 through 135:
126. Interactive Research Boxes (Structured findings payload generator)
127. Dynamic Knowledge Graph Visualization Data Adapter
128. Holographic-Style Data Panels
129. Timeline Visualization
130. Statistical Dashboards
131. Live Task Visualization
132. Screen Annotation (Draw overlays, arrows, labels on captures)
133. Visual Comparison (Pixel & structural image diffs)
134. 3D Data Visualization
135. Contextual Visual Overlays

CRITICAL CHECK: Verifies that viewer/index.html is protected and unmodified.
"""

import os
import sys
import json
import time
import math
import unittest
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from jarvis.visual import (
    ResearchBoxPayloadGenerator,
    ResearchFinding,
    ResearchCitation,
    ResearchMetric,
    KnowledgeGraphAdapter,
    GraphNode,
    GraphLink,
    HolographicPanelGenerator,
    TimelineVisualizer,
    TimelineEvent,
    TimelineMilestone,
    StatisticalDashboardGenerator,
    LiveTaskVisualizer,
    TaskNode,
    ScreenAnnotationEngine,
    VisualComparisonEngine,
    ComparisonResult,
    DiffRegion,
    ThreeDDataVisualizer,
    Point3D,
    Vector3D,
    ContextualOverlayEngine,
    HUDPill,
    FloatingTooltip,
    visual_intelligence,
    CAPABILITY_METADATA,
)


class TestProtectedViewerIntegrity(unittest.TestCase):
    """
    CRITICAL DIRECTIVE VERIFICATION:
    Ensure viewer/index.html exists and is strictly intact.
    """

    def test_viewer_index_html_intact(self):
        viewer_path = os.path.join(PROJECT_ROOT, "viewer", "index.html")
        self.assertTrue(os.path.exists(viewer_path), "viewer/index.html must exist")
        with open(viewer_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("3D Knowledge Galaxy", content)
        self.assertIn("ForceGraph3D", content)
        self.assertGreater(len(content), 50000, "viewer/index.html should be the complete 3D viewer")


class TestCapability126ResearchBox(unittest.TestCase):
    """
    Capability 126: Interactive Research Boxes (Structured findings payload generator)
    """

    def setUp(self):
        self.gen = ResearchBoxPayloadGenerator()

    def test_payload_generation(self):
        payload = self.gen.create_payload(
            topic="Quantum Computing",
            query="Explain topological qubits and error rates",
            summary="Topological qubits utilize anyons to suppress local decoherence.",
            findings=[
                {"title": "Decoherence Immunity", "summary": "Braiding operations are fault tolerant.", "confidence": 0.98},
                {"title": "Majorana Bound States", "summary": "Zero-bias conductance peaks observed.", "confidence": 0.92},
            ],
            metrics=[
                {"label": "Coherence Time", "value": "120", "unit": "μs"},
                {"label": "Fidelity", "value": "99.8", "unit": "%"},
            ],
            tags=["quantum", "physics", "hardware"],
        )
        self.assertEqual(payload["type"], "interactive_research_box")
        self.assertEqual(payload["topic"], "Quantum Computing")
        self.assertEqual(len(payload["findings"]), 2)
        self.assertEqual(len(payload["metrics"]), 2)
        self.assertIn("quantum", payload["tags"])
        self.assertEqual(payload["status"], "COMPLETED")

    def test_svg_card_rendering(self):
        payload = self.gen.create_payload(
            topic="Autonomous Swarms",
            query="Optimal routing protocols",
            summary="Distributed consensus algorithms enable zero-latency peer handoffs.",
            metrics=[{"label": "Throughput", "value": "450", "unit": "msg/s"}],
            tags=["swarm", "multi-agent"],
        )
        svg = self.gen.render_svg_card(payload, width=600, height=340)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("Autonomous Swarms", svg)
        self.assertIn("#00e5ff", svg)
        self.assertIn("RESEARCH BOX", svg)
        self.assertTrue(svg.endswith("</svg>"))

    def test_html_card_rendering(self):
        payload = self.gen.create_payload(
            topic="Neural Architecture",
            query="Attention mechanisms",
            summary="Sparse attention reduces quadratic memory scaling to linear.",
        )
        html = self.gen.render_html_card(payload)
        self.assertIn("jarvis-holo-research-box", html)
        self.assertIn("Neural Architecture", html)
        self.assertIn("CONFIDENCE:", html)

    def test_13_block_report_deck(self):
        deck = self.gen.generate_13_block_report_deck(
            topic="VR Ecosystem 2026",
            overview_stat="100+",
            overview_label="TITLES GENERATING >$1M GROSS REVENUE",
            milestones=[{"q": "Q1", "text": "Hardware refresh"}],
            bar_chart_data=[{"label": "Quest 3", "value": 63.8}],
            spec_items=[{"name": "FOV", "val": "110 deg"}],
            sources=["UploadVR", "Meta Reality Labs"],
        )
        self.assertEqual(deck["type"], "13_block_report_deck")
        self.assertEqual(deck["blocks_count"], 13)
        self.assertEqual(len(deck["blocks"]), 13)
        block_types = [b["type"] for b in deck["blocks"]]
        self.assertIn("stat_highlight", block_types)
        self.assertIn("live_bar_chart", block_types)
        self.assertIn("docked_orb_telemetry", block_types)


class TestCapability127GraphAdapter(unittest.TestCase):
    """
    Capability 127: Dynamic Knowledge Graph Visualization Data Adapter
    """

    def setUp(self):
        self.adapter = KnowledgeGraphAdapter()

    def test_load_from_dict_and_payload_generation(self):
        data = {
            "nodes": [
                {"id": 1, "label": "Hub A", "group": "operations", "is_hub": True, "val": 14},
                {"id": 2, "label": "Node B", "group": "operations", "is_hub": False, "val": 4.5},
            ],
            "links": [
                {"source": 1, "target": 2, "value": 2.0, "link_type": "hub_spoke"}
            ],
        }
        self.adapter.load_from_dict(data)
        payload = self.adapter.to_3d_force_graph_payload()
        self.assertEqual(len(payload["nodes"]), 2)
        self.assertEqual(len(payload["links"]), 1)
        self.assertEqual(payload["nodes"][0]["label"], "Hub A")

    def test_layout_algorithms(self):
        # Add test nodes
        for i in range(12):
            self.adapter.add_node(GraphNode(
                id=i,
                label=f"Node {i}",
                group="finance" if i < 6 else "marketing",
                is_hub=(i % 6 == 0),
            ))

        # Galaxy layout
        self.adapter.apply_layout("galaxy", spread=150.0)
        hubs = [n for n in self.adapter.nodes.values() if n.is_hub]
        self.assertTrue(len(hubs) > 0)

        # Fibonacci sphere layout
        self.adapter.apply_layout("sphere", spread=100.0)
        for n in self.adapter.nodes.values():
            dist = math.sqrt(n.x**2 + n.y**2 + n.z**2)
            self.assertGreater(dist, 10.0)

        # Hierarchical layout
        self.adapter.apply_layout("hierarchical")
        for hub in hubs:
            self.assertEqual(hub.y, 100.0)

    def test_filter_subgraph(self):
        self.adapter.add_node(GraphNode(id="ops_hub", label="Operations Hub", group="operations", is_hub=True))
        self.adapter.add_node(GraphNode(id="fin_hub", label="Finance Hub", group="finance", is_hub=True))
        self.adapter.add_node(GraphNode(id="doc_1", label="Inventory Log", group="operations", is_hub=False))
        self.adapter.add_link(GraphLink(source="ops_hub", target="doc_1"))

        sub = self.adapter.filter_subgraph(groups=["operations"])
        self.assertEqual(len(sub.nodes), 2)
        self.assertIn("ops_hub", sub.nodes)
        self.assertIn("doc_1", sub.nodes)
        self.assertNotIn("fin_hub", sub.nodes)
        self.assertEqual(len(sub.links), 1)

    def test_graph_diff_computation(self):
        old_g = {
            "nodes": [{"id": 1, "label": "Node 1", "val": 4.5}],
            "links": [],
        }
        new_g = {
            "nodes": [
                {"id": 1, "label": "Node 1 Mod", "val": 5.0},
                {"id": 2, "label": "Node 2", "val": 4.5},
            ],
            "links": [{"source": 1, "target": 2}],
        }
        diff = KnowledgeGraphAdapter.compute_graph_diff(old_g, new_g)
        self.assertEqual(len(diff["added_nodes"]), 1)
        self.assertEqual(diff["added_nodes"][0]["id"], 2)
        self.assertEqual(len(diff["modified_nodes"]), 1)
        self.assertEqual(diff["modified_nodes"][0]["label"], "Node 1 Mod")
        self.assertEqual(len(diff["added_links"]), 1)

    def test_svg_preview_rendering(self):
        self.adapter.add_node(GraphNode(id=1, label="Alpha", x=0, y=0, z=0, is_hub=True))
        self.adapter.add_node(GraphNode(id=2, label="Beta", x=50, y=50, z=0, is_hub=False))
        self.adapter.add_link(GraphLink(source=1, target=2))
        svg = self.adapter.render_svg_preview(width=600, height=400)
        self.assertIn("<svg", svg)
        self.assertIn("KNOWLEDGE GRAPH ADAPTER PREVIEW", svg)
        self.assertIn("Alpha", svg)


class TestCapability128HolographicPanels(unittest.TestCase):
    """
    Capability 128: Holographic-Style Data Panels
    """

    def setUp(self):
        self.holo = HolographicPanelGenerator()

    def test_circular_gauge_svg(self):
        svg = self.holo.render_circular_gauge_svg(
            value=78.5, min_val=0, max_val=100, label="GPU LOAD", unit="%"
        )
        self.assertIn("<svg", svg)
        self.assertIn("78.5", svg)
        self.assertIn("GPU LOAD", svg)
        self.assertIn("#00e5ff", svg)

    def test_radar_reticle_svg(self):
        targets = [
            {"distance": 0.5, "angle": 45, "label": "RADAR_TGT_1"},
            {"distance": 0.8, "angle": 180, "label": "RADAR_TGT_2"},
        ]
        svg = self.holo.render_radar_reticle_svg(targets=targets, scan_angle_deg=90)
        self.assertIn("<svg", svg)
        self.assertIn("RADAR_TGT_1", svg)
        self.assertIn("RADAR // SCANNER", svg)

    def test_telemetry_bar_svg(self):
        metrics = [
            {"label": "MIC LVL", "value": "-46.5", "unit": "dB", "status": "OPTIMAL"},
            {"label": "LATENCY", "value": "12", "unit": "ms", "status": "OPTIMAL"},
        ]
        svg = self.holo.render_telemetry_bar_svg(metrics, width=400, height=60)
        self.assertIn("<svg", svg)
        self.assertIn("MIC LVL", svg)
        self.assertIn("-46.5", svg)

    def test_hud_card_html(self):
        card_html = self.holo.render_hud_card(
            title="TELEMETRY CORE", content_html="<p>Systems operational</p>"
        )
        self.assertIn("jarvis-hud-card", card_html)
        self.assertIn("TELEMETRY CORE", card_html)
        self.assertIn("hud-corner-tl", card_html)

    def test_terminal_panel_html(self):
        logs = ["Initializing subsystem...", "Connected to neural core.", "Ready."]
        term_html = self.holo.render_terminal_panel_html(logs)
        self.assertIn("jarvis-term-panel", term_html)
        self.assertIn("Initializing subsystem...", term_html)


class TestCapability129TimelineVisualization(unittest.TestCase):
    """
    Capability 129: Timeline Visualization
    """

    def setUp(self):
        self.tl = TimelineVisualizer(title="Sprint Milestones")
        self.tl.add_event(TimelineEvent(id="e1", title="Research Complete", timestamp=100.0, status="completed", category="research"))
        self.tl.add_event(TimelineEvent(id="e2", title="Visual Engine Build", timestamp=200.0, status="in_progress", category="dev"))
        self.tl.add_event(TimelineEvent(id="e3", title="System Verification", timestamp=300.0, status="pending", category="qa"))

    def test_timeline_payload(self):
        payload = self.tl.to_timeline_payload()
        self.assertEqual(payload["type"], "timeline_visualization")
        self.assertEqual(payload["events_count"], 3)
        self.assertEqual(payload["events"][0]["title"], "Research Complete")

    def test_horizontal_svg(self):
        svg = self.tl.render_horizontal_svg(width=800, height=260)
        self.assertIn("<svg", svg)
        self.assertIn("SPRINT MILESTONES", svg)
        self.assertIn("Research Complete", svg)

    def test_vertical_gantt_svg(self):
        svg = self.tl.render_vertical_gantt_svg(width=800, height=360)
        self.assertIn("<svg", svg)
        self.assertIn("GANTT EXECUTION SCHEDULE", svg)
        self.assertIn("Research Complete", svg)

    def test_interactive_html(self):
        html = self.tl.render_interactive_html()
        self.assertIn("jarvis-timeline-container", html)
        self.assertIn("Visual Engine Build", html)


class TestCapability130StatisticalDashboards(unittest.TestCase):
    """
    Capability 130: Statistical Dashboards
    """

    def setUp(self):
        self.dash = StatisticalDashboardGenerator(title="Operations Metrics")

    def test_sparkline_svg(self):
        vals = [10.0, 15.0, 12.0, 18.0, 24.0, 22.0, 30.0]
        svg = self.dash.render_sparkline_svg(vals, width=120, height=36)
        self.assertIn("<svg", svg)
        self.assertIn("<polyline", svg)

    def test_bar_chart_svg(self):
        data = [
            {"label": "Quest 2", "value": 35.0},
            {"label": "Quest 3", "value": 28.0},
            {"label": "Index", "value": 15.0},
        ]
        svg = self.dash.render_bar_chart_svg(data, width=450, height=250, title="Market Share")
        self.assertIn("<svg", svg)
        self.assertIn("Quest 2", svg)
        self.assertIn("CHART: MARKET SHARE", svg)

    def test_donut_chart_svg(self):
        data = [
            {"label": "Direct", "value": 45.0},
            {"label": "Organic", "value": 30.0},
            {"label": "Referral", "value": 25.0},
        ]
        svg = self.dash.render_donut_chart_svg(data, width=380, height=240, title="Channel Mix")
        self.assertIn("<svg", svg)
        self.assertIn("DONUT: CHANNEL MIX", svg)
        self.assertIn("Direct", svg)

    def test_bento_dashboard_html(self):
        cards = [
            {"type": "kpi", "title": "REVENUE", "value": "$124,500", "delta": "+14.2%", "trend": "up", "sparkline": [10, 20, 25, 40]},
            {"type": "chart_bar", "title": "WEEKLY TRAFFIC", "data": [{"label": "Mon", "value": 120}, {"label": "Tue", "value": 150}]},
        ]
        html = self.dash.render_bento_dashboard_html(cards)
        self.assertIn("jarvis-bento-dashboard", html)
        self.assertIn("REVENUE", html)
        self.assertIn("$124,500", html)


class TestCapability131LiveTaskVisualization(unittest.TestCase):
    """
    Capability 131: Live Task Visualization
    """

    def setUp(self):
        self.vis = LiveTaskVisualizer(workflow_name="Swarm Synthesis Pipeline")
        self.vis.add_task(TaskNode(task_id="t1", name="Query Intake", agent_name="intelligence", status="completed", progress=100.0))
        self.vis.add_task(TaskNode(task_id="t2", name="Code Extraction", agent_name="software", status="running", progress=65.0, dependencies=["t1"]))
        self.vis.add_task(TaskNode(task_id="t3", name="Visual Generation", agent_name="visual", status="running", progress=80.0, dependencies=["t1"]))
        self.vis.add_task(TaskNode(task_id="t4", name="Report Assembly", agent_name="coordinator", status="pending", progress=0.0, dependencies=["t2", "t3"]))

    def test_live_state_payload(self):
        payload = self.vis.to_live_state_payload()
        self.assertEqual(payload["type"], "live_task_state")
        self.assertEqual(payload["total_tasks"], 4)
        self.assertEqual(payload["completed_tasks"], 1)
        self.assertEqual(payload["running_tasks"], 2)
        self.assertGreater(payload["overall_progress_pct"], 50.0)

    def test_segmented_progress_bar_svg(self):
        # 20-block segmented bar
        svg = self.vis.render_segmented_progress_bar_svg(progress_pct=65.0, total_blocks=20, width=400, height=28)
        self.assertIn("<svg", svg)
        self.assertIn('stroke="#00e5ff"', svg)
        self.assertIn("segGlow", svg)

    def test_dag_svg(self):
        svg = self.vis.render_dag_svg(width=800, height=400)
        self.assertIn("<svg", svg)
        self.assertIn("SWARM SYNTHESIS PIPELINE", svg)
        self.assertIn("Query Intake", svg)
        self.assertIn("@visual", svg)

    def test_swarm_monitor_svg(self):
        agents = [
            {"name": "intelligence", "role": "Reasoning", "status": "completed"},
            {"name": "visual", "role": "Visual Intelligence", "status": "working"},
        ]
        svg = self.vis.render_swarm_monitor_svg(agents, width=700, height=300)
        self.assertIn("<svg", svg)
        self.assertIn("@INTELLIGENCE", svg)
        self.assertIn("@VISUAL", svg)


class TestCapability132ScreenAnnotation(unittest.TestCase):
    """
    Capability 132: Screen Annotation (Draw overlays, arrows, labels on captures)
    """

    def setUp(self):
        # Create small test background image
        self.base_img = Image.new("RGB", (640, 480), (10, 20, 35))
        self.engine = ScreenAnnotationEngine(base_image=self.base_img)

    def test_annotations_composite(self):
        self.engine.add_box(50, 50, 120, 60, label="Search Bar", color_hex="#00e5ff")
        self.engine.add_arrow(110, 140, 110, 115, color_hex="#00e5ff")
        self.engine.add_step_marker(50, 50, step_num=1, text="Click Here")
        self.engine.add_crosshair(320, 240, radius=25, label="Center Target")
        self.engine.add_spotlight(40, 40, 140, 80, dim_alpha=120)
        self.engine.add_redaction(400, 50, 100, 30, style="blur")

        pil_res = self.engine.render_pil()
        self.assertEqual(pil_res.size, (640, 480))
        self.assertEqual(pil_res.mode, "RGB")

        b64 = self.engine.render_to_base64()
        self.assertTrue(b64.startswith("data:image/jpeg;base64,"))

        svg_overlay = self.engine.render_svg_overlay()
        self.assertIn("<svg", svg_overlay)
        self.assertIn("Search Bar", svg_overlay)


class TestCapability133VisualComparison(unittest.TestCase):
    """
    Capability 133: Visual Comparison (Pixel & structural image diffs)
    """

    def setUp(self):
        self.comp = VisualComparisonEngine(threshold=25)

    def test_identical_images_comparison(self):
        img_a = Image.new("RGB", (200, 200), (40, 80, 120))
        img_b = Image.new("RGB", (200, 200), (40, 80, 120))

        res = self.comp.compare_images(img_a, img_b)
        self.assertEqual(res.similarity_score, 1.0)
        self.assertEqual(res.diff_percentage, 0.0)
        self.assertEqual(res.total_diff_pixels, 0)
        self.assertEqual(len(res.changed_regions), 0)

    def test_diff_detection_and_clusters(self):
        img_a = Image.new("RGB", (200, 200), (40, 80, 120))
        img_b = img_a.copy()
        # Introduce a bright 40x40 square in img_b
        for x in range(50, 90):
            for y in range(50, 90):
                img_b.putpixel((x, y), (255, 255, 255))

        res = self.comp.compare_images(img_a, img_b)
        self.assertLess(res.similarity_score, 1.0)
        self.assertGreater(res.diff_percentage, 0.0)
        self.assertGreater(res.total_diff_pixels, 0)
        self.assertGreater(len(res.changed_regions), 0)
        self.assertTrue(res.diff_image_base64.startswith("data:image/jpeg;base64,"))
        self.assertTrue(res.side_by_side_base64.startswith("data:image/jpeg;base64,"))

    def test_dhash(self):
        img = Image.new("RGB", (100, 100), (50, 100, 150))
        h = self.comp.compute_dhash(img)
        self.assertIsInstance(h, str)
        self.assertEqual(len(h), 16)


class TestCapability134ThreeDVisualization(unittest.TestCase):
    """
    Capability 134: 3D Data Visualization
    """

    def setUp(self):
        self.v3d = ThreeDDataVisualizer()

    def test_point_cloud_generation(self):
        sphere_pts = self.v3d.generate_point_cloud(count=150, shape="sphere", radius=100)
        self.assertEqual(len(sphere_pts), 150)
        galaxy_pts = self.v3d.generate_point_cloud(count=120, shape="galaxy_spiral", radius=100)
        self.assertEqual(len(galaxy_pts), 120)
        helix_pts = self.v3d.generate_point_cloud(count=80, shape="helix", radius=80)
        self.assertEqual(len(helix_pts), 80)
        torus_pts = self.v3d.generate_point_cloud(count=100, shape="torus", radius=90)
        self.assertEqual(len(torus_pts), 100)

    def test_vector_field(self):
        v_field = self.v3d.generate_vector_field(grid_dim=3, spacing=30.0, pattern="vortex")
        self.assertEqual(len(v_field), 27)  # 3x3x3
        self.assertIsInstance(v_field[0], Vector3D)

    def test_isometric_svg_projection(self):
        pts = [
            Point3D(x=-50, y=0, z=0),
            Point3D(x=50, y=0, z=0),
            Point3D(x=0, y=50, z=0),
        ]
        lines = [(0, 1), (1, 2), (2, 0)]
        svg = self.v3d.render_isometric_svg(pts, lines=lines, width=500, height=350, title="TRIANGLE")
        self.assertIn("<svg", svg)
        self.assertIn("3D SPATIAL PROJECTION", svg)
        self.assertIn("<line", svg)

    def test_exploded_orb_svg(self):
        svg = self.v3d.render_exploded_orb_svg(width=450, height=350, label="J.A.R.V.I.S.")
        self.assertIn("<svg", svg)
        self.assertIn("KINETIC ORB ARCHITECTURE", svg)
        self.assertIn("orbBloom", svg)
        self.assertIn("J.A.R.V.I.S.", svg)

    def test_threejs_buffer_geometry_json(self):
        pts = [Point3D(x=10, y=20, z=30, r=0.0, g=1.0, b=1.0)]
        geom_json_str = self.v3d.to_threejs_buffer_geometry_json(pts)
        parsed = json.loads(geom_json_str)
        self.assertEqual(parsed["metadata"]["type"], "BufferGeometry")
        pos = parsed["data"]["attributes"]["position"]["array"]
        self.assertEqual(pos, [10.0, 20.0, 30.0])


class TestCapability135ContextualVisualOverlays(unittest.TestCase):
    """
    Capability 135: Contextual Visual Overlays
    """

    def setUp(self):
        self.ov = ContextualOverlayEngine()
        self.ov.add_pill("HISTORY", active=False)
        self.ov.add_pill("REPORT: CARDS", active=True)
        self.ov.add_tooltip(
            target_x=450,
            target_y=300,
            title="Inspect Subsystem",
            description="CPU saturation at 82%",
            severity="warning",
            actions=["Throttle Background", "Dismiss"],
        )

    def test_hud_pills_svg(self):
        svg = self.ov.render_hud_pills_svg(width=600, height=40)
        self.assertIn("<svg", svg)
        self.assertIn("[REPORT: CARDS]", svg)
        self.assertIn("[HISTORY]", svg)

    def test_overlay_svg(self):
        svg = self.ov.render_overlay_svg(screen_width=1280, screen_height=720)
        self.assertIn("<svg", svg)
        self.assertIn("CONTEXTUAL OVERLAY ACTIVE", svg)
        self.assertIn("INSPECT SUBSYSTEM", svg)
        self.assertIn("CPU saturation at 82%", svg)

    def test_overlay_html(self):
        html = self.ov.render_overlay_html()
        self.assertIn("jarvis-contextual-overlay-layer", html)
        self.assertIn("[REPORT: CARDS]", html)
        self.assertIn("active", html)


class TestVisualIntelligenceFacade(unittest.TestCase):
    """
    Validates unified VisualIntelligence facade and metadata mapping.
    """

    def test_facade_and_capabilities(self):
        self.assertIsNotNone(visual_intelligence.research)
        self.assertIsNotNone(visual_intelligence.graph)
        self.assertIsNotNone(visual_intelligence.holo)
        self.assertIsNotNone(visual_intelligence.timeline)
        self.assertIsNotNone(visual_intelligence.dashboards)
        self.assertIsNotNone(visual_intelligence.tasks)
        self.assertIsNotNone(visual_intelligence.comparison)
        self.assertIsNotNone(visual_intelligence.three_d)
        self.assertIsNotNone(visual_intelligence.overlays)

        for cap_num in range(126, 136):
            self.assertIn(cap_num, CAPABILITY_METADATA)
            meta = CAPABILITY_METADATA[cap_num]
            self.assertIn("name", meta)
            self.assertIn("module", meta)


if __name__ == "__main__":
    unittest.main()
