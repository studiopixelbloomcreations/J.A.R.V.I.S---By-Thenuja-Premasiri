"""
Relationship Discovery Engine for J.A.R.V.I.S.
Capability 95: Relationship Discovery

Analyzes explicit and latent connections between knowledge notes, entities,
and projects. Mines unlinked mentions, shared entity co-occurrences,
thematic clusters, bridge nodes, and isolated knowledge islands.
"""

import re
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict


class RelationshipDiscoveryEngine:
    """
    Mines unlinked references, detects latent topological relationships,
    and identifies structural patterns across the knowledge network.
    """

    def __init__(self):
        pass

    def discover_relationships(
        self,
        notes_dict: Dict[str, str],
        existing_wikilinks: Optional[Dict[str, Set[str]]] = None
    ) -> Dict[str, Any]:
        """
        Discovers explicit and latent relationships across a collection of notes (name -> content).
        """
        existing = existing_wikilinks or {}
        titles = list(notes_dict.keys())
        title_set = set(titles)

        unlinked_mentions: List[Dict[str, Any]] = []
        shared_entities: List[Dict[str, Any]] = []
        thematic_connections: List[Dict[str, Any]] = []
        degree_map: Dict[str, int] = defaultdict(int)

        # Precompute words and extracted entities for each note
        note_features: Dict[str, Dict[str, Any]] = {}
        for title, content in notes_dict.items():
            lower = content.lower()
            tokens = set(re.findall(r'\b[a-zA-Z0-9_\'-]{4,}\b', lower))
            # Extract capitalized potential entities
            entities = set(re.findall(r'\b[A-Z][a-zA-Z0-9_\'-]+(?:\s+[A-Z][a-zA-Z0-9_\'-]+)*\b', content))
            note_features[title] = {
                "lower": lower,
                "tokens": tokens,
                "entities": entities
            }

        # 1. Unlinked mentions discovery
        for source_title, content in notes_dict.items():
            s_lower = note_features[source_title]["lower"]
            known_links = existing.get(source_title, set())

            for target_title in titles:
                if source_title == target_title:
                    continue
                if target_title in known_links:
                    degree_map[source_title] += 1
                    continue

                # Check if target title appears in source text (min length 4)
                if len(target_title) >= 4 and target_title.lower() in s_lower:
                    unlinked_mentions.append({
                        "source": source_title,
                        "target": target_title,
                        "relationship_type": "unlinked_mention",
                        "confidence": 0.85,
                        "suggestion": f"Add [[{target_title}]] to '{source_title}'"
                    })

        # 2. Shared entities and thematic co-occurrence
        for i in range(len(titles)):
            for j in range(i + 1, len(titles)):
                t1, t2 = titles[i], titles[j]
                f1, f2 = note_features[t1], note_features[t2]

                # Shared named entities
                common_entities = f1["entities"].intersection(f2["entities"])
                filtered_entities = [e for e in common_entities if len(e) > 3]
                if len(filtered_entities) >= 2:
                    confidence = min(0.95, round(0.5 + 0.1 * len(filtered_entities), 2))
                    shared_entities.append({
                        "node_a": t1,
                        "node_b": t2,
                        "shared_entities": sorted(filtered_entities),
                        "count": len(filtered_entities),
                        "relationship_type": "shared_entities",
                        "confidence": confidence
                    })

                # Thematic token overlap (Jaccard)
                union_tokens = f1["tokens"].union(f2["tokens"])
                if union_tokens:
                    jaccard = len(f1["tokens"].intersection(f2["tokens"])) / len(union_tokens)
                    if jaccard > 0.15:
                        thematic_connections.append({
                            "node_a": t1,
                            "node_b": t2,
                            "jaccard_similarity": round(jaccard, 3),
                            "relationship_type": "thematic_overlap",
                            "confidence": round(min(0.9, jaccard * 3), 2)
                        })

        # 3. Identify knowledge islands (isolated notes with 0 connections)
        all_linked_nodes = set()
        for s, targets in existing.items():
            if targets:
                all_linked_nodes.add(s)
                all_linked_nodes.update(targets)

        islands = [t for t in titles if t not in all_linked_nodes]

        return {
            "total_notes_analyzed": len(titles),
            "unlinked_mentions_count": len(unlinked_mentions),
            "unlinked_mentions": unlinked_mentions[:50],
            "shared_entities_count": len(shared_entities),
            "shared_entities": shared_entities[:50],
            "thematic_connections_count": len(thematic_connections),
            "thematic_connections": thematic_connections[:50],
            "knowledge_islands": islands,
            "island_count": len(islands)
        }

    def suggest_wikilinks_for_text(self, text: str, available_titles: List[str]) -> List[Dict[str, Any]]:
        """
        Suggests relevant wikilinks that could be inserted into arbitrary text or a new note.
        """
        suggestions = []
        lower_text = text.lower()
        for title in available_titles:
            if len(title) >= 3 and title.lower() in lower_text:
                # Check if already wikilinked
                pattern = rf'\[\[{re.escape(title)}(?:\|[^\]]+)?\]\]'
                if not re.search(pattern, text, re.IGNORECASE):
                    suggestions.append({
                        "title": title,
                        "replacement": f"[[{title}]]",
                        "confidence": 0.9
                    })
        return suggestions

    def build_adjacency_matrix(self, notes_dict: Dict[str, str], links: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Builds graph adjacency representation and calculates centrality/bridge candidates.
        """
        titles = sorted(list(notes_dict.keys()))
        adj: Dict[str, Set[str]] = {t: set() for t in titles}
        for u, v in links:
            if u in adj and v in adj:
                adj[u].add(v)
                adj[v].add(u)

        degrees = {t: len(adj[t]) for t in titles}
        sorted_by_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)

        return {
            "adjacency": {k: list(v) for k, v in adj.items()},
            "degrees": degrees,
            "top_hubs": sorted_by_degree[:10]
        }


# Module singleton
relationship_discovery = RelationshipDiscoveryEngine()
