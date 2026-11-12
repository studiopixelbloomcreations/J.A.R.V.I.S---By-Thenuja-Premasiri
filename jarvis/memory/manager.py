"""
Unified Knowledge & Memory Manager for J.A.R.V.I.S.
Integrates Capabilities 91-100:
91. Personal Knowledge Graph
92. Project Memory
93. Semantic Search
94. Document Understanding
95. Relationship Discovery
96. Research Memory
97. Timeline Memory
98. Knowledge Deduplication
99. Source Provenance
100. Memory Quality Assessment
"""

import re
import pathlib
from typing import Dict, List, Any, Optional

from ..config import NOTES_DIR, DATA_DIR, load_user_profile
from ..knowledge.document_understanding import document_understanding
from ..knowledge.relationship_discovery import relationship_discovery
from ..knowledge.deduplication import knowledge_deduplicator
from ..knowledge.provenance import source_provenance
from ..knowledge.graph_adapter import graph_adapter
from ..knowledge.graph import scan_full_texts

from .personal_graph import personal_graph
from .project_memory import project_memory
from .semantic_search import semantic_search
from .research_memory import research_memory
from .timeline_memory import timeline_memory
from .quality_assessment import memory_quality_assessor


class UnifiedMemoryManager:
    """
    Central orchestrator and facade for all 10 knowledge and memory capabilities.
    """

    def __init__(self):
        self.personal_graph = personal_graph
        self.project_memory = project_memory
        self.semantic_search = semantic_search
        self.doc_engine = document_understanding
        self.relationship_engine = relationship_discovery
        self.research_store = research_memory
        self.timeline = timeline_memory
        self.deduplicator = knowledge_deduplicator
        self.provenance = source_provenance
        self.quality = memory_quality_assessor
        self.graph_adapter = graph_adapter

    def remember(
        self,
        title: str,
        content: str,
        category: str = "personal",
        origin_type: str = "user_explicit",
        author: str = "Thenuja Premasiri",
        tags: Optional[List[str]] = None,
        save_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Captures a fact, note, or observation, automatically attaching provenance,
        indexing it in semantic search, and logging it to the timeline.
        """
        clean_title = re.sub(r'[^a-zA-Z0-9_\-\s]', '', title).strip().title() or "Untitled Observation"
        tags = tags or [category]

        file_path = ""
        if save_to_disk:
            captures_dir = NOTES_DIR / "captures"
            captures_dir.mkdir(parents=True, exist_ok=True)
            fname = f"{clean_title.replace(' ', '_')}.md"
            target_file = captures_dir / fname
            doc_body = f"# {clean_title}\n\n**Category:** {category} | **Author:** {author}\n\n{content}\n"
            target_file.write_text(doc_body, encoding="utf-8")
            file_path = str(target_file)

        # 1. Attach Provenance
        prov_record = self.provenance.register_provenance(
            target_id=clean_title,
            origin_type=origin_type,
            origin_uri=file_path or f"memory://{category}/{clean_title}",
            author=author,
            confidence=1.0 if origin_type == "user_explicit" else 0.85,
            notes=f"Recorded into {category} sector"
        )

        # 2. Record in Timeline
        event_record = self.timeline.record_event(
            title=f"Memory Ingested: {clean_title}",
            description=content[:200] + ("…" if len(content) > 200 else ""),
            category=category,
            importance=3,
            tags=tags
        )

        # 3. Add to Semantic Search Index
        self.semantic_search.add_custom_document(
            doc_id=clean_title,
            title=clean_title,
            content=content,
            group=category
        )

        return {
            "status": "success",
            "title": clean_title,
            "category": category,
            "file_path": file_path,
            "provenance_id": prov_record["record_id"],
            "event_id": event_record["id"],
            "citation": self.provenance.format_citation(clean_title, style="inline")
        }

    def grounded_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Executes semantic search and enriches results with structural parsing and citations.
        """
        search_res = self.semantic_search.search(query, top_k=top_k)
        enriched_results = []

        for hit in search_res.get("results", []):
            prov = self.provenance.get_provenance(hit["id"])
            citation = self.provenance.format_citation(hit["id"], style="inline")
            enriched_results.append({
                **hit,
                "citation": citation,
                "confidence": prov.get("confidence_score", 0.9) if prov else 0.85,
                "verified": prov.get("verification_status") == "verified" if prov else False
            })

        return {
            "status": "success",
            "query": query,
            "results_count": len(enriched_results),
            "results": enriched_results
        }

    def run_full_knowledge_audit(self) -> Dict[str, Any]:
        """
        Runs comprehensive analysis across the entire knowledge base:
        quality scores, duplicate detection, unlinked relationships, and lineage stats.
        """
        texts = scan_full_texts()
        quality_report = self.quality.assess_knowledge_base(texts)
        dupe_report = self.deduplicator.find_duplicates(texts)
        rel_report = self.relationship_engine.discover_relationships(texts)
        prov_stats = self.provenance.get_summary_stats()

        return {
            "status": "success",
            "total_notes": len(texts),
            "quality": quality_report,
            "deduplication": dupe_report,
            "relationships": rel_report,
            "provenance_telemetry": prov_stats
        }

    def get_personal_context_summary(self) -> Dict[str, Any]:
        """
        Synthesizes active personal context: entities, active projects, recent events.
        """
        profile_text = load_user_profile()
        entities = self.personal_graph.query_entities()
        active_projects = self.project_memory.list_projects(status="active")
        recent_events = self.timeline.get_recent(limit=5)
        blockers = self.project_memory.get_all_active_blockers()

        return {
            "profile_preview": profile_text[:300] + "…",
            "entity_count": len(entities),
            "active_projects": [p["name"] for p in active_projects],
            "unresolved_blockers": blockers,
            "recent_events": recent_events
        }


# Module singleton
memory_manager = UnifiedMemoryManager()
