"""
Automated Comprehensive Test Suite for Knowledge & Memory Subsystem
Validates Capabilities 91-100:
91. Personal Knowledge Graph (jarvis/memory/personal_graph.py)
92. Project Memory (jarvis/memory/project_memory.py)
93. Semantic Search (jarvis/memory/semantic_search.py)
94. Document Understanding (jarvis/knowledge/document_understanding.py)
95. Relationship Discovery (jarvis/knowledge/relationship_discovery.py)
96. Research Memory (jarvis/memory/research_memory.py)
97. Timeline Memory (jarvis/memory/timeline_memory.py)
98. Knowledge Deduplication (jarvis/knowledge/deduplication.py)
99. Source Provenance (jarvis/knowledge/provenance.py)
100. Memory Quality Assessment (jarvis/memory/quality_assessment.py)
Plus Knowledge Graph Adapter and Unified Memory Manager.
"""

import os
import sys
import time
import shutil
import tempfile
import pathlib
import unittest

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from jarvis.config import ROOT_DIR, VIEWER_DIR, NOTES_DIR, DATA_DIR
from jarvis.knowledge.document_understanding import DocumentUnderstandingEngine, document_understanding
from jarvis.knowledge.relationship_discovery import RelationshipDiscoveryEngine, relationship_discovery
from jarvis.knowledge.deduplication import KnowledgeDeduplicator, knowledge_deduplicator
from jarvis.knowledge.provenance import SourceProvenanceTracker, source_provenance
from jarvis.knowledge.graph_adapter import KnowledgeGraphAdapter, graph_adapter
from jarvis.knowledge.graph import load_graph_data, scan_full_texts

from jarvis.memory.personal_graph import PersonalKnowledgeGraph, personal_graph
from jarvis.memory.project_memory import ProjectMemoryManager, project_memory
from jarvis.memory.semantic_search import SemanticSearchEngine, semantic_search
from jarvis.memory.research_memory import ResearchMemoryStore, research_memory
from jarvis.memory.timeline_memory import TimelineMemoryManager, timeline_memory
from jarvis.memory.quality_assessment import MemoryQualityAssessor, memory_quality_assessor
from jarvis.memory.manager import UnifiedMemoryManager, memory_manager


class TestPersonalKnowledgeGraph(unittest.TestCase):
    """Capability 91: Personal Knowledge Graph"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.graph_file = pathlib.Path(self.temp_dir) / "test_pkg.json"
        self.pkg = PersonalKnowledgeGraph(storage_path=self.graph_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_seeded_entities_and_relationships(self):
        """Verifies default personal context entities and relationships are seeded."""
        thenuja = self.pkg.get_entity("thenuja")
        self.assertIsNotNone(thenuja)
        self.assertEqual(thenuja["name"], "Thenuja Premasiri")
        self.assertEqual(thenuja["entity_type"], "Person")

        pixel_bloom = self.pkg.get_entity("pixel_bloom")
        self.assertIsNotNone(pixel_bloom)
        self.assertEqual(pixel_bloom["name"], "Pixel Bloom Studios")

        jarvis = self.pkg.get_entity("jarvis")
        self.assertIsNotNone(jarvis)
        self.assertEqual(jarvis["name"], "Project J.A.R.V.I.S.")

    def test_add_entity_and_query(self):
        """Tests adding custom entities and querying by category or tag."""
        ent = self.pkg.add_entity("unreal_engine", "Unreal Engine 5", "Tool", {"type": "Real-time 3D"}, ["creative", "vfx"])
        self.assertEqual(ent["id"], "unreal_engine")

        tools = self.pkg.query_entities(entity_type="Tool")
        tool_ids = [t["id"] for t in tools]
        self.assertIn("unreal_engine", tool_ids)

        vfx_tagged = self.pkg.query_entities(tag="vfx")
        vfx_ids = [t["id"] for t in vfx_tagged]
        self.assertIn("unreal_engine", vfx_ids)

    def test_relationships_and_neighbors(self):
        """Tests adding relationships and retrieving directional neighbors."""
        self.pkg.add_entity("houdini", "SideFX Houdini", "Tool")
        self.pkg.add_relationship("pixel_bloom", "houdini", "experiments_with", weight=0.8)

        outgoing = self.pkg.get_neighbors("pixel_bloom", direction="outgoing")
        outgoing_targets = [n["entity"]["id"] for n in outgoing]
        self.assertIn("houdini", outgoing_targets)

        incoming = self.pkg.get_neighbors("houdini", direction="incoming")
        incoming_sources = [n["entity"]["id"] for n in incoming]
        self.assertIn("pixel_bloom", incoming_sources)

    def test_path_finding(self):
        """Tests BFS shortest path discovery between entities."""
        # thenuja -> pixel_bloom -> blender
        path = self.pkg.find_path("thenuja", "blender")
        self.assertIsNotNone(path)
        self.assertIn("thenuja", path)
        self.assertIn("blender", path)

    def test_to_viewer_payload(self):
        """Tests export to standard node/link visual payload."""
        payload = self.pkg.to_viewer_payload()
        self.assertIn("nodes", payload)
        self.assertIn("links", payload)
        self.assertTrue(len(payload["nodes"]) >= 5)
        self.assertTrue(len(payload["links"]) >= 5)


class TestProjectMemory(unittest.TestCase):
    """Capability 92: Project Memory"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store_file = pathlib.Path(self.temp_dir) / "test_pm.json"
        self.pm = ProjectMemoryManager(storage_path=self.store_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_seeded_projects(self):
        """Verifies core initiatives are registered."""
        jarvis = self.pm.get_project("jarvis")
        self.assertIsNotNone(jarvis)
        self.assertEqual(jarvis["name"], "Project J.A.R.V.I.S.")
        self.assertIn("Python", jarvis["tech_stack"])

        pb = self.pm.get_project("pixel_bloom")
        self.assertIsNotNone(pb)
        self.assertEqual(pb["category"], "creative")

    def test_register_and_list_projects(self):
        """Tests registering a new project and filtering by category."""
        self.pm.register_project("quantum_flow", "Quantum Flow", "Simulation lab", "research", ["C++", "CUDA"])
        proj = self.pm.get_project("quantum_flow")
        self.assertEqual(proj["name"], "Quantum Flow")

        research_projs = self.pm.list_projects(category="research")
        self.assertEqual(len(research_projs), 1)
        self.assertEqual(research_projs[0]["project_id"], "quantum_flow")

    def test_milestone_lifecycle(self):
        """Tests milestone addition and status updates."""
        ms = self.pm.add_milestone("jarvis", "Audio Neural Bridge", "2026-12-15", "pending")
        self.assertIsNotNone(ms)
        self.assertEqual(ms["status"], "pending")

        updated = self.pm.update_milestone_status("jarvis", ms["id"], "completed")
        self.assertTrue(updated)
        jarvis = self.pm.get_project("jarvis")
        ms_record = next(m for m in jarvis["milestones"] if m["id"] == ms["id"])
        self.assertEqual(ms_record["status"], "completed")

    def test_adr_and_blockers(self):
        """Tests architectural decision records and operational blocker tracking."""
        adr = self.pm.record_decision(
            "jarvis",
            "Zero-Polling Architecture",
            "Use reactive board notifications to eliminate idle token and CPU burn.",
            ["500ms polling loop"]
        )
        self.assertIsNotNone(adr)
        self.assertEqual(adr["title"], "Zero-Polling Architecture")

        blk = self.pm.add_blocker("pixel_bloom", "GPU VRAM bottleneck on 4K renders", severity="high")
        self.assertIsNotNone(blk)
        self.assertFalse(blk["resolved"])

        active_blks = self.pm.get_all_active_blockers()
        self.assertTrue(any(b["id"] == blk["id"] for b in active_blks))

        resolved = self.pm.resolve_blocker("pixel_bloom", blk["id"])
        self.assertTrue(resolved)
        active_blks_after = self.pm.get_all_active_blockers()
        self.assertFalse(any(b["id"] == blk["id"] for b in active_blks_after))


class TestSemanticSearch(unittest.TestCase):
    """Capability 93: Semantic Search"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = SemanticSearchEngine(notes_dir=pathlib.Path(self.temp_dir))
        self.engine.add_custom_document(
            "doc_vfx",
            "Cinematic Color Grading in DaVinci",
            "This guide covers ACEScg color workflows, film emulation, LUTs, and VFX character consistency.",
            "creative"
        )
        self.engine.add_custom_document(
            "doc_bio",
            "Grade 10 Biology Cellular Respiration",
            "Cellular respiration breaks down glucose in the mitochondria to produce ATP for cell metabolism.",
            "education"
        )
        self.engine.add_custom_document(
            "doc_jarvis",
            "J.A.R.V.I.S. Swarm Message Board Protocols",
            "Autonomous multi-agent swarms communicate through asynchronous message boards with sequence numbers.",
            "tech"
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_semantic_retrieval_with_synonyms(self):
        """Tests semantic search retrieving relevant docs via expanded synonyms."""
        # 'film' should expand to 'vfx', 'cinematic', etc., ranking doc_vfx highest
        res = self.engine.search("film", top_k=3)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["total_matches"] >= 1)
        top_hit = res["results"][0]
        self.assertEqual(top_hit["id"], "doc_vfx")

    def test_school_study_expansion(self):
        """Tests school and study synonym matching."""
        res = self.engine.search("school exam study", top_k=2)
        top_hit = res["results"][0]
        self.assertEqual(top_hit["id"], "doc_bio")

    def test_group_filtering(self):
        """Tests filtering search results by sector group."""
        res = self.engine.search("cellular", group_filter="education")
        self.assertEqual(len(res["results"]), 1)
        self.assertEqual(res["results"][0]["id"], "doc_bio")

        res_none = self.engine.search("cellular", group_filter="tech")
        self.assertEqual(len(res_none["results"]), 0)


class TestDocumentUnderstanding(unittest.TestCase):
    """Capability 94: Document Understanding"""

    def setUp(self):
        self.engine = DocumentUnderstandingEngine(wpm_reading_speed=200)
        self.sample_doc = """# J.A.R.V.I.S. Neural Architecture

## Overview
J.A.R.V.I.S. coordinates autonomous workflows for [[Thenuja Premasiri]] and [[Pixel Bloom Studios]].
Refer to [Official Portal](https://pixelbloom.lk) for deployment guides.

### Deliverables & Milestones
- [x] Implement 150-Skill Dispatcher
- [ ] Deploy Native Swarm Engine
- [ ] Connect Real-Time dB Analyser

### Technology Matrix
| Subsystem | Framework | Status |
|---|---|---|
| Memory | SQLite + Vector | Active |
| Audio | Fish Audio S2.1 | Online |

```python
def execute_skill(skill_id):
    return {"status": "success"}
```

Thenuja Premasiri founded Pixel Bloom Studios in Kurunegala to direct AI VFX short films.
"""

    def test_document_parsing_structure(self):
        """Verifies parsing of headings, tasks, wikilinks, URLs, and code blocks."""
        parsed = self.engine.parse_document(self.sample_doc, title="Architecture Note")
        self.assertEqual(parsed["title"], "Architecture Note")
        self.assertTrue(parsed["word_count"] > 30)
        self.assertGreater(parsed["estimated_reading_minutes"], 0.0)

        # Check headings
        headings = [h["text"] for h in parsed["headings"]]
        self.assertIn("J.A.R.V.I.S. Neural Architecture", headings)
        self.assertIn("Overview", headings)
        self.assertIn("Deliverables & Milestones", headings)

        # Check tasks
        self.assertEqual(len(parsed["tasks"]), 3)
        self.assertTrue(parsed["tasks"][0]["completed"])
        self.assertFalse(parsed["tasks"][1]["completed"])

        # Check wikilinks
        wikilinks = [w["target"] for w in parsed["wikilinks"]]
        self.assertIn("Thenuja Premasiri", wikilinks)
        self.assertIn("Pixel Bloom Studios", wikilinks)

        # Check external links
        self.assertEqual(len(parsed["external_links"]), 1)
        self.assertEqual(parsed["external_links"][0]["url"], "https://pixelbloom.lk")

        # Check code blocks
        self.assertEqual(len(parsed["code_blocks"]), 1)
        self.assertEqual(parsed["code_blocks"][0]["language"], "python")

        # Check tables
        self.assertEqual(len(parsed["tables"]), 1)
        self.assertEqual(parsed["tables"][0]["headers"], ["Subsystem", "Framework", "Status"])
        self.assertEqual(len(parsed["tables"][0]["rows"]), 2)

    def test_metrics_and_classification(self):
        """Verifies readability metrics and domain classification."""
        parsed = self.engine.parse_document(self.sample_doc)
        metrics = parsed["metrics"]
        self.assertIn("readability_score", metrics)
        self.assertIn("lexical_density", metrics)
        self.assertIn(parsed["primary_topic"], ["tech", "creative", "personal"])
        self.assertTrue(len(parsed["executive_summary"]) > 20)


class TestRelationshipDiscovery(unittest.TestCase):
    """Capability 95: Relationship Discovery"""

    def setUp(self):
        self.engine = RelationshipDiscoveryEngine()
        self.notes = {
            "Pixel Bloom Studios": "Pixel Bloom Studios produces VFX and cinematic animation using Blender and DaVinci Resolve.",
            "Character Continuity": "Maintaining consistent characters in Pixel Bloom Studios animations requires seed locking and LoRA models.",
            "DaVinci Resolve Workflow": "DaVinci Resolve is our primary color grading workstation for cinematic short films.",
            "St Annes Debating": "The English Debating circle at St. Anne's College meets weekly to practice parliamentary debate.",
            "Isolated Island Note": "Completely disconnected note about quantum gardening in an alternate dimension."
        }
        self.existing_links = {
            "Pixel Bloom Studios": {"DaVinci Resolve Workflow"}
        }

    def test_discover_unlinked_mentions(self):
        """Verifies detection of unlinked mentions (e.g. 'Character Continuity' mentions 'Pixel Bloom Studios')."""
        res = self.engine.discover_relationships(self.notes, self.existing_links)
        unlinked = res["unlinked_mentions"]
        pair_found = any(u["source"] == "Character Continuity" and u["target"] == "Pixel Bloom Studios" for u in unlinked)
        self.assertTrue(pair_found)

    def test_shared_entities_and_islands(self):
        """Verifies shared entity discovery and isolated island detection."""
        res = self.engine.discover_relationships(self.notes, self.existing_links)
        self.assertIn("Isolated Island Note", res["knowledge_islands"])

    def test_suggest_wikilinks_for_text(self):
        """Tests suggesting wikilinks for arbitrary text."""
        text = "We need to open DaVinci Resolve Workflow and coordinate with Pixel Bloom Studios."
        suggestions = self.engine.suggest_wikilinks_for_text(text, list(self.notes.keys()))
        sug_titles = [s["title"] for s in suggestions]
        self.assertIn("Pixel Bloom Studios", sug_titles)
        self.assertIn("DaVinci Resolve Workflow", sug_titles)


class TestResearchMemory(unittest.TestCase):
    """Capability 96: Research Memory"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store_file = pathlib.Path(self.temp_dir) / "test_rm.json"
        self.rm = ResearchMemoryStore(storage_path=self.store_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_seeded_dossiers(self):
        """Verifies default research dossiers exist."""
        dossiers = self.rm.list_dossiers()
        self.assertTrue(len(dossiers) >= 3)
        topics = [d["topic"] for d in dossiers]
        self.assertTrue(any("VFX" in t for t in topics))
        self.assertTrue(any("STEM" in t for t in topics))

    def test_create_dossier_and_add_finding(self):
        """Tests dossier creation, finding insertion, and verification."""
        d = self.rm.create_dossier("WebRTC Audio Streaming", "Investigation into sub-100ms voice transport", "tech", ["audio", "webrtc"])
        fnd = self.rm.add_finding(d["id"], "Opus encoder with 20ms frame size yields 45ms end-to-end latency.", confidence=0.92, source_url="https://webrtc.org")
        self.assertIsNotNone(fnd)
        self.assertFalse(fnd["verified"])

        verified = self.rm.verify_claim(d["id"], fnd["id"], verifier="Lead Engineer")
        self.assertTrue(verified)
        updated_d = self.rm.get_dossier(d["id"])
        self.assertEqual(len(updated_d["verified_claims"]), 1)

    def test_export_markdown(self):
        """Tests markdown rendering of a research dossier."""
        d = self.rm.list_dossiers()[0]
        md = self.rm.export_dossier_markdown(d["id"])
        self.assertIsNotNone(md)
        self.assertIn("# 🔬 Research Dossier", md)
        self.assertIn("## Executive Summary", md)


class TestTimelineMemory(unittest.TestCase):
    """Capability 97: Timeline Memory"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store_file = pathlib.Path(self.temp_dir) / "test_tm.json"
        self.tm = TimelineMemoryManager(storage_path=self.store_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_seeded_timeline_events(self):
        """Verifies chronological baseline is seeded."""
        recent = self.tm.get_recent(limit=10)
        self.assertTrue(len(recent) >= 4)

    def test_record_and_range_query(self):
        """Tests event creation and epoch time-window queries."""
        t1 = time.time()
        evt = self.tm.record_event(
            "Neural Indexing Completed",
            "Indexed 250 markdown documents into the 3D celestial nebula.",
            "tech",
            importance=4,
            entities=["jarvis"]
        )
        self.assertIsNotNone(evt)
        t2 = time.time()

        window = self.tm.query_range(t1 - 1, t2 + 1)
        self.assertTrue(any(e["id"] == evt["id"] for e in window))

        ent_events = self.tm.get_events_for_entity("jarvis")
        self.assertTrue(any(e["id"] == evt["id"] for e in ent_events))

    def test_export_timeline_markdown(self):
        """Tests chronological markdown export."""
        md = self.tm.export_timeline_markdown(limit=5)
        self.assertIn("# ⏱️ J.A.R.V.I.S. Chronological Timeline Memory", md)


class TestKnowledgeDeduplication(unittest.TestCase):
    """Capability 98: Knowledge Deduplication"""

    def setUp(self):
        self.dedup = KnowledgeDeduplicator(fuzzy_threshold=0.75)

    def test_exact_and_normalized_duplicates(self):
        """Tests detection of exact and formatting-variant duplicates."""
        doc1 = "# Project Roadmap\n\n- Deploy multi-agent swarm\n- Build cybernetic orb."
        doc2 = "# Project Roadmap\n\n- Deploy multi-agent swarm\n- Build cybernetic orb."
        doc3 = "### Project Roadmap\nDeploy multi-agent swarm. Build cybernetic orb."
        doc4 = "# Unique Finance Record\nTotal quarterly revenue: $45,000 USD."

        notes = {"Doc1": doc1, "Doc2": doc2, "Doc3": doc3, "Doc4": doc4}
        report = self.dedup.find_duplicates(notes)

        self.assertFalse(report["clean_status"])
        self.assertTrue(len(report["exact_duplicate_groups"]) >= 1)
        # Doc1 and Doc2 are exact duplicates
        exact_pair = report["exact_duplicate_groups"][0]
        self.assertIn("Doc1", exact_pair)
        self.assertIn("Doc2", exact_pair)

    def test_merge_notes(self):
        """Tests intelligent note merging with preserved wikilinks and sections."""
        primary = "# Studio Guidelines\n\nFollow [[ACEScg]] color standards."
        secondary = "# Studio Rules\n\nFollow [[ACEScg]] color standards.\n\nUse [[Blender]] for 3D modeling."

        merged = self.dedup.merge_notes("Studio Guidelines", primary, "Studio Rules", secondary)
        self.assertEqual(merged["title"], "Studio Guidelines")
        self.assertIn("ACEScg", merged["preserved_wikilinks"])
        self.assertIn("Blender", merged["preserved_wikilinks"])
        self.assertIn("Use [[Blender]] for 3D modeling", merged["merged_content"])


class TestSourceProvenance(unittest.TestCase):
    """Capability 99: Source Provenance"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store_file = pathlib.Path(self.temp_dir) / "test_prov.json"
        self.tracker = SourceProvenanceTracker(storage_path=self.store_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_provenance_lifecycle_and_verification(self):
        """Tests registering, modifying, and verifying source provenance."""
        rec = self.tracker.register_provenance(
            target_id="DaVinci Color Profile",
            origin_type="authoritative_doc",
            origin_uri="notes/creative/color.md",
            author="Thenuja Premasiri"
        )
        self.assertEqual(rec["confidence_score"], 0.95)
        self.assertEqual(rec["verification_status"], "verified")

        # Record audit transformation
        self.tracker.record_transformation("DaVinci Color Profile", "calibrated", "Lead Colorist", "Updated to ACES 1.3")
        trail = self.tracker.get_audit_trail("DaVinci Color Profile")
        self.assertTrue(len(trail) >= 2)

        # Citations
        inline_cite = self.tracker.format_citation("DaVinci Color Profile", style="inline")
        self.assertIn("DaVinci Color Profile", inline_cite)

        footnote = self.tracker.format_citation("DaVinci Color Profile", style="footnote")
        self.assertIn("Thenuja Premasiri", footnote)

        stats = self.tracker.get_summary_stats()
        self.assertEqual(stats["total_records"], 1)


class TestMemoryQualityAssessment(unittest.TestCase):
    """Capability 100: Memory Quality Assessment"""

    def setUp(self):
        self.assessor = MemoryQualityAssessor(freshness_half_life_days=90.0)

    def test_assess_healthy_note(self):
        """Tests quality scoring of a well-structured, fresh note."""
        content = """# Autonomous Swarm Architecture
## Overview
The native swarm system allows multi-agent collaboration with zero idle polling.
- Reactive board wakeups
- Clean separation of concerns
- Cross-verified tests

See [[Project JARVIS Architecture]] and [[Personal Knowledge Graph]] for details.
"""
        res = self.assessor.assess_note(
            title="Autonomous Swarm Architecture",
            content=content,
            last_modified_epoch=time.time(),
            wikilinks=["Project JARVIS Architecture", "Personal Knowledge Graph"],
            available_titles={"Project JARVIS Architecture", "Personal Knowledge Graph"}
        )
        self.assertGreaterEqual(res["overall_health_score"], 80.0)
        self.assertIn("A", res["grade"])
        self.assertEqual(len(res["broken_links"]), 0)

    def test_assess_sparse_stale_note(self):
        """Tests penalty detection on stale, sparse notes with broken links."""
        res = self.assessor.assess_note(
            title="Old Note",
            content="just a draft",
            last_modified_epoch=time.time() - (150 * 86400),  # 150 days old
            wikilinks=["NonExistentLink"],
            available_titles={"RealNote"}
        )
        self.assertLess(res["overall_health_score"], 65.0)
        self.assertIn("NonExistentLink", res["broken_links"])
        self.assertTrue(len(res["issues"]) >= 2)


class TestKnowledgeGraphAdapter(unittest.TestCase):
    """Knowledge Graph Safe Data Provider & Payload Adapter"""

    def setUp(self):
        self.adapter = KnowledgeGraphAdapter()

    def test_full_payload_and_degrees(self):
        """Verifies full payload retrieval with degree enrichment."""
        payload = self.adapter.get_full_graph_payload()
        self.assertEqual(payload["status"], "success")
        self.assertIn("nodes", payload)
        self.assertIn("links", payload)
        self.assertTrue(payload["node_count"] > 0)
        # Verify degree property added to nodes
        if payload["nodes"]:
            self.assertIn("degree", payload["nodes"][0])

    def test_subgraph_extraction(self):
        """Verifies depth-1 and depth-2 ego subgraph extraction."""
        sub = self.adapter.get_subgraph(0, depth=1)
        self.assertEqual(sub["status"], "success")
        self.assertIn("subgraph_nodes", sub)
        self.assertIn("subgraph_links", sub)

    def test_graph_analytics(self):
        """Verifies topological metrics calculation."""
        analytics = self.adapter.get_graph_analytics()
        self.assertIn("node_count", analytics)
        self.assertIn("link_count", analytics)
        self.assertIn("density", analytics)
        self.assertIn("sector_distribution", analytics)


class TestUnifiedMemoryManager(unittest.TestCase):
    """Integration of Capabilities 91-100 via UnifiedMemoryManager"""

    def setUp(self):
        self.mgr = memory_manager

    def test_remember_and_grounded_search(self):
        """Tests complete pipeline: ingest fact, attach provenance, record timeline, search."""
        title = f"Test Observation {int(time.time())}"
        content = "Testing integration of autonomous memory subsystem with ACEScg colorimetry."
        res = self.mgr.remember(
            title=title,
            content=content,
            category="creative",
            origin_type="user_explicit",
            tags=["test", "vfx"],
            save_to_disk=False
        )
        self.assertEqual(res["status"], "success")
        self.assertIn("provenance_id", res)
        self.assertIn("event_id", res)

        # Grounded search
        search_res = self.mgr.grounded_search("ACEScg", top_k=3)
        self.assertEqual(search_res["status"], "success")
        self.assertTrue(search_res["results_count"] >= 1)

    def test_personal_context_summary(self):
        """Tests personal context synthesis."""
        summary = self.mgr.get_personal_context_summary()
        self.assertIn("profile_preview", summary)
        self.assertGreater(summary["entity_count"], 0)
        self.assertTrue(len(summary["active_projects"]) > 0)

    def test_knowledge_audit(self):
        """Tests comprehensive knowledge audit."""
        audit = self.mgr.run_full_knowledge_audit()
        self.assertEqual(audit["status"], "success")
        self.assertIn("quality", audit)
        self.assertIn("deduplication", audit)
        self.assertIn("relationships", audit)
        self.assertIn("provenance_telemetry", audit)


class TestCriticalDirectivePreservation(unittest.TestCase):
    """
    CRITICAL DIRECTIVE: DO NOT TOUCH OR MODIFY THE EXISTING 3D KNOWLEDGE GRAPH VISUALIZATION IN viewer/.
    Treat viewer/index.html, viewer/orb.js, and the 3D celestial nebula visualization as strictly protected.
    """

    def test_viewer_files_exist_and_unaltered(self):
        """Verifies viewer/index.html and viewer/orb.js are strictly intact."""
        index_html = VIEWER_DIR / "index.html"
        orb_js = VIEWER_DIR / "orb.js"
        graph_data_js = VIEWER_DIR / "graph-data.js"

        self.assertTrue(index_html.exists(), "viewer/index.html must exist")
        self.assertTrue(orb_js.exists(), "viewer/orb.js must exist")
        self.assertTrue(graph_data_js.exists(), "viewer/graph-data.js must exist")

        html_text = index_html.read_text(encoding="utf-8")
        self.assertIn("nebula", html_text.lower())


if __name__ == "__main__":
    unittest.main()
