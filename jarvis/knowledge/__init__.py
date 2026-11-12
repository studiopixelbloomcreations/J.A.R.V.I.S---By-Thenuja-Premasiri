"""
J.A.R.V.I.S. Knowledge Subsystem
Capabilities 94, 95, 98, 99 & Knowledge Graph Data Adapter
"""

from .graph import load_graph_data, scan_full_texts, search_notes_fast
from .learning import synthesize_note_understanding, learn_and_expand_database
from .document_understanding import DocumentUnderstandingEngine, document_understanding
from .relationship_discovery import RelationshipDiscoveryEngine, relationship_discovery
from .deduplication import KnowledgeDeduplicator, knowledge_deduplicator
from .provenance import SourceProvenanceTracker, source_provenance
from .graph_adapter import KnowledgeGraphAdapter, graph_adapter

__all__ = [
    "load_graph_data",
    "scan_full_texts",
    "search_notes_fast",
    "synthesize_note_understanding",
    "learn_and_expand_database",
    "DocumentUnderstandingEngine",
    "document_understanding",
    "RelationshipDiscoveryEngine",
    "relationship_discovery",
    "KnowledgeDeduplicator",
    "knowledge_deduplicator",
    "SourceProvenanceTracker",
    "source_provenance",
    "KnowledgeGraphAdapter",
    "graph_adapter",
]
