"""
Personal Knowledge Graph Engine for J.A.R.V.I.S.
Capability 91: Personal Knowledge Graph

Represents and queries the user's personal knowledge network:
entities (people, organizations, projects, skills, tools, locations, concepts)
and typed directed relationships with semantic attributes and graph algorithms.
"""

import json
import pathlib
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from collections import deque
from ..config import DATA_DIR, PROFILE_FILE

PERSONAL_GRAPH_FILE = DATA_DIR / "personal_knowledge_graph.json"


class PersonalKnowledgeGraph:
    """
    In-memory and persisted directed knowledge graph of personal entities,
    biographical context, professional associations, and conceptual nodes.
    """

    def __init__(self, storage_path: Optional[pathlib.Path] = None):
        self.storage_path = storage_path or PERSONAL_GRAPH_FILE
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Dict[str, Any]] = []
        self.load()
        if not self.entities:
            self._seed_default_profile()

    def add_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
        attributes: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Adds or updates a personal entity in the graph."""
        e_id = entity_id.lower().strip().replace(" ", "_")
        entity = {
            "id": e_id,
            "name": name,
            "entity_type": entity_type,
            "attributes": attributes or {},
            "tags": tags or [],
            "created_at": self.entities.get(e_id, {}).get("created_at", datetime.now().isoformat()),
            "last_updated": datetime.now().isoformat()
        }
        self.entities[e_id] = entity
        self.save()
        return entity

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an entity by its identifier."""
        e_id = entity_id.lower().strip().replace(" ", "_")
        return self.entities.get(e_id)

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Adds a directed relationship between two entities."""
        s = source_id.lower().strip().replace(" ", "_")
        t = target_id.lower().strip().replace(" ", "_")

        # Check if already exists to update
        for rel in self.relationships:
            if rel["source"] == s and rel["target"] == t and rel["relation"] == relation_type:
                rel["weight"] = weight
                rel["attributes"] = attributes or rel.get("attributes", {})
                rel["last_updated"] = datetime.now().isoformat()
                self.save()
                return rel

        rel_record = {
            "source": s,
            "target": t,
            "relation": relation_type,
            "weight": weight,
            "attributes": attributes or {},
            "created_at": datetime.now().isoformat()
        }
        self.relationships.append(rel_record)
        self.save()
        return rel_record

    def get_neighbors(
        self,
        entity_id: str,
        direction: str = "both",
        relation_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns connected entities and their connecting relationships.
        direction: 'both', 'outgoing', or 'incoming'
        """
        e_id = entity_id.lower().strip().replace(" ", "_")
        neighbors = []

        for rel in self.relationships:
            if relation_filter and rel["relation"] != relation_filter:
                continue

            if direction in ("outgoing", "both") and rel["source"] == e_id:
                target = self.entities.get(rel["target"])
                if target:
                    neighbors.append({
                        "entity": target,
                        "relation": rel["relation"],
                        "direction": "outgoing",
                        "weight": rel["weight"]
                    })

            if direction in ("incoming", "both") and rel["target"] == e_id:
                source = self.entities.get(rel["source"])
                if source:
                    neighbors.append({
                        "entity": source,
                        "relation": rel["relation"],
                        "direction": "incoming",
                        "weight": rel["weight"]
                    })

        return neighbors

    def find_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """
        Breadth-first search shortest path between two entities.
        Returns list of entity IDs in order, or None if no path exists.
        """
        start = start_id.lower().strip().replace(" ", "_")
        end = end_id.lower().strip().replace(" ", "_")

        if start not in self.entities or end not in self.entities:
            return None
        if start == end:
            return [start]

        queue = deque([[start]])
        visited = {start}

        adj: Dict[str, Set[str]] = {k: set() for k in self.entities}
        for rel in self.relationships:
            adj[rel["source"]].add(rel["target"])
            adj[rel["target"]].add(rel["source"])  # Undirected traversal for connectivity

        while queue:
            path = queue.popleft()
            node = path[-1]

            for neighbor in adj.get(node, []):
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return None

    def query_entities(
        self,
        entity_type: Optional[str] = None,
        tag: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries entities matching optional filters."""
        results = []
        q = search_query.lower() if search_query else None

        for e in self.entities.values():
            if entity_type and e["entity_type"].lower() != entity_type.lower():
                continue
            if tag and tag.lower() not in [t.lower() for t in e.get("tags", [])]:
                continue
            if q and (q not in e["name"].lower() and q not in e["id"]):
                continue
            results.append(e)

        return results

    def compute_degree_centrality(self) -> Dict[str, int]:
        """Calculates degree centrality for each node."""
        degrees: Dict[str, int] = {k: 0 for k in self.entities}
        for rel in self.relationships:
            if rel["source"] in degrees:
                degrees[rel["source"]] += 1
            if rel["target"] in degrees:
                degrees[rel["target"]] += 1
        return degrees

    def to_viewer_payload(self) -> Dict[str, Any]:
        """
        Exports personal knowledge graph into node/link format compatible with graph visualizations.
        """
        nodes = []
        id_to_idx = {}
        for idx, (e_id, entity) in enumerate(self.entities.items()):
            id_to_idx[e_id] = idx
            nodes.append({
                "id": idx,
                "label": entity["name"],
                "group": entity["entity_type"],
                "tags": entity.get("tags", []),
                "key": e_id
            })

        links = []
        for rel in self.relationships:
            s_idx = id_to_idx.get(rel["source"])
            t_idx = id_to_idx.get(rel["target"])
            if s_idx is not None and t_idx is not None:
                links.append({
                    "source": s_idx,
                    "target": t_idx,
                    "relation": rel["relation"],
                    "value": rel.get("weight", 1.0)
                })

        return {"nodes": nodes, "links": links}

    def _seed_default_profile(self):
        """Seeds personal knowledge graph from Thenuja's profile context."""
        # Core Person
        self.add_entity("thenuja", "Thenuja Premasiri", "Person", {"role": "Creator & Student", "status": "Active"}, ["user", "founder"])

        # Organizations
        self.add_entity("pixel_bloom", "Pixel Bloom Studios", "Organization", {"industry": "VFX & Creative Studio"}, ["business", "creative"])
        self.add_entity("st_annes_college", "St. Anne's College", "Organization", {"city": "Kurunegala", "type": "School"}, ["education", "school"])

        # Projects
        self.add_entity("jarvis", "Project J.A.R.V.I.S.", "Project", {"focus": "Autonomous Desktop Assistant", "version": "2.0"}, ["tech", "ai", "core"])
        self.add_entity("aevra", "Project Aevra", "Project", {"focus": "Autonomous Agent Ecosystem"}, ["tech", "ai"])
        self.add_entity("stem_mind", "STEM-Mind", "Project", {"focus": "Grade 10 STEM Learning & Revision"}, ["education", "stem"])
        self.add_entity("apex_logistics", "Apex Logistics", "Project", {"focus": "Operational Logistics Workflow"}, ["operations"])

        # Tools & Skills
        self.add_entity("vfx_short_films", "AI VFX & Short Films", "Skill", {"mastery": "Practitioner"}, ["creative", "film"])
        self.add_entity("english_debating", "English Debating Circle", "Skill", {"circle": "St. Anne's Debating"}, ["communication", "school"])
        self.add_entity("davinci_resolve", "DaVinci Resolve", "Tool", {"category": "Color Grading & Editing"}, ["creative", "tool"])
        self.add_entity("blender", "Blender 3D", "Tool", {"category": "3D VFX & Modeling"}, ["creative", "tool"])
        self.add_entity("python", "Python 3", "Tool", {"category": "Engineering"}, ["code", "tech"])
        self.add_entity("gemini_api", "Google Gemini API", "Tool", {"category": "Multimodal AI"}, ["ai", "tech"])

        # Relationships
        self.add_relationship("thenuja", "pixel_bloom", "founded", 1.0)
        self.add_relationship("thenuja", "st_annes_college", "studies_at", 1.0)
        self.add_relationship("thenuja", "jarvis", "leads", 1.0)
        self.add_relationship("thenuja", "vfx_short_films", "practices", 1.0)
        self.add_relationship("thenuja", "english_debating", "leads", 1.0)

        self.add_relationship("pixel_bloom", "vfx_short_films", "specializes_in", 0.9)
        self.add_relationship("pixel_bloom", "davinci_resolve", "uses_tool", 0.85)
        self.add_relationship("pixel_bloom", "blender", "uses_tool", 0.85)

        self.add_relationship("jarvis", "python", "built_with", 1.0)
        self.add_relationship("jarvis", "gemini_api", "powered_by", 1.0)
        self.add_relationship("jarvis", "thenuja", "assists", 1.0)

        self.add_relationship("stem_mind", "st_annes_college", "aligned_with", 0.8)
        self.add_relationship("stem_mind", "thenuja", "created_by", 1.0)

        self.save()

    def load(self):
        """Loads personal graph from storage."""
        if self.storage_path and self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self.entities = data.get("entities", {})
                self.relationships = data.get("relationships", [])
            except Exception:
                self.entities = {}
                self.relationships = []

    def save(self):
        """Saves personal graph to storage."""
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "entity_count": len(self.entities),
                "relationship_count": len(self.relationships),
                "entities": self.entities,
                "relationships": self.relationships
            }
            self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# Module singleton
personal_graph = PersonalKnowledgeGraph()
