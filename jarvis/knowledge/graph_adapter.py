"""
Knowledge Graph Data Adapter for J.A.R.V.I.S.
Provides clean data interfaces and payloads for downstream visualizers and UI consumers
WITHOUT modifying or tampering with viewer/ files or the protected 3D visualization.
"""

import re
import json
from typing import Dict, List, Any, Optional
from ..config import ROOT_DIR, NOTES_DIR, VIEWER_DIR
from .graph import load_graph_data, scan_full_texts


class KnowledgeGraphAdapter:
    """
    Read-only data adapter and provider for graph topologies, subgraphs,
    cluster filtering, and entity node telemetry.
    """

    def __init__(self):
        pass

    def get_full_graph_payload(self) -> Dict[str, Any]:
        """
        Retrieves the complete graph data payload containing nodes, links, and group metadata.
        """
        graph = load_graph_data()
        nodes = graph.get("nodes", [])
        links = graph.get("links", [])

        # Calculate node degrees
        degrees: Dict[int, int] = {i: 0 for i in range(len(nodes))}
        for link in links:
            s, t = link.get("source"), link.get("target")
            if s in degrees:
                degrees[s] += 1
            if t in degrees:
                degrees[t] += 1

        enriched_nodes = []
        for i, node in enumerate(nodes):
            n_copy = dict(node)
            n_copy["degree"] = degrees.get(i, 0)
            enriched_nodes.append(n_copy)

        groups = sorted(list(set(n.get("group", "general") for n in nodes)))

        return {
            "status": "success",
            "node_count": len(enriched_nodes),
            "link_count": len(links),
            "groups": groups,
            "nodes": enriched_nodes,
            "links": links
        }

    def get_subgraph(self, center_id: int, depth: int = 1) -> Dict[str, Any]:
        """
        Extracts a localized ego-subgraph centered around a specific node ID.
        """
        graph = load_graph_data()
        nodes = graph.get("nodes", [])
        links = graph.get("links", [])

        if center_id < 0 or center_id >= len(nodes):
            return {"status": "error", "message": f"Node ID {center_id} out of bounds."}

        # Breadth-first search for connected node IDs
        visited_ids = {center_id}
        current_layer = {center_id}

        for _ in range(depth):
            next_layer = set()
            for link in links:
                s, t = link.get("source"), link.get("target")
                if s in current_layer and t not in visited_ids:
                    visited_ids.add(t)
                    next_layer.add(t)
                elif t in current_layer and s not in visited_ids:
                    visited_ids.add(s)
                    next_layer.add(s)
            current_layer = next_layer

        subgraph_nodes = [nodes[i] for i in visited_ids if i < len(nodes)]
        subgraph_links = [l for l in links if l.get("source") in visited_ids and l.get("target") in visited_ids]

        return {
            "status": "success",
            "center_node": nodes[center_id],
            "depth": depth,
            "subgraph_nodes": subgraph_nodes,
            "subgraph_links": subgraph_links,
            "node_count": len(subgraph_nodes),
            "link_count": len(subgraph_links)
        }

    def get_cluster_by_group(self, group_name: str) -> Dict[str, Any]:
        """
        Retrieves all nodes and internal links belonging to a designated sector group.
        """
        graph = load_graph_data()
        nodes = graph.get("nodes", [])
        links = graph.get("links", [])

        group_nodes = [n for n in nodes if n.get("group", "").lower() == group_name.lower()]
        group_node_ids = {n["id"] for n in group_nodes if "id" in n}

        cluster_links = [l for l in links if l.get("source") in group_node_ids and l.get("target") in group_node_ids]

        return {
            "status": "success",
            "group": group_name,
            "nodes": group_nodes,
            "links": cluster_links,
            "count": len(group_nodes)
        }

    def get_graph_analytics(self) -> Dict[str, Any]:
        """
        Calculates topological telemetry: density, degree distribution, and sector clustering.
        """
        graph = load_graph_data()
        nodes = graph.get("nodes", [])
        links = graph.get("links", [])
        n_count = len(nodes)
        l_count = len(links)

        max_possible_links = (n_count * (n_count - 1)) / 2 if n_count > 1 else 1
        density = round(l_count / max_possible_links, 4) if max_possible_links > 0 else 0

        sector_counts: Dict[str, int] = {}
        for n in nodes:
            g = n.get("group", "general")
            sector_counts[g] = sector_counts.get(g, 0) + 1

        return {
            "node_count": n_count,
            "link_count": l_count,
            "density": density,
            "sector_distribution": sector_counts
        }


# Module singleton
graph_adapter = KnowledgeGraphAdapter()
