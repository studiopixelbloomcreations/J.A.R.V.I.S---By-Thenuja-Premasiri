"""
Dynamic Knowledge Graph Visualization Data Adapter (Capability 127)
Adapts markdown notes, entity memories, and relationship maps into 2D/3D force graph payloads
compatible with ThreeJS, ForceGraph, D3, and Cytoscape.
CRITICAL: DOES NOT MODIFY viewer/index.html. Provides pure modular adapters and diff engines.
"""

import os
import re
import math
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class GraphNode:
    id: Any
    label: str
    folder_name: str = "general"
    group: str = "default"
    is_hub: bool = False
    val: float = 4.5
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    excerpt: str = ""
    color: str = "#00e5ff"
    icon: str = "📄"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphLink:
    source: Any
    target: Any
    value: float = 1.0
    label: str = ""
    link_type: str = "related"  # hub_spoke, wikilink, semantic, dependency
    curvature: float = 0.0
    color: str = "rgba(0, 229, 255, 0.4)"


class KnowledgeGraphAdapter:
    """
    Transforms unstructured notes and structured databases into graph visualizations.
    Supports 3D Galaxy, Fibonacci Sphere, and 2D D3 layouts, incremental diffs, and SVG rendering.
    """

    GROUP_COLORS = {
        "apex-logistics": "#38bdf8",
        "captures": "#fbbf24",
        "finance": "#34d399",
        "marketing": "#f472b6",
        "operations": "#a78bfa",
        "personal": "#60a5fa",
        "products": "#f87171",
        "team": "#fb923c",
        "default": "#00e5ff",
    }

    def __init__(self):
        self.nodes: Dict[Any, GraphNode] = {}
        self.links: List[GraphLink] = []

    def clear(self):
        self.nodes.clear()
        self.links.clear()

    def add_node(self, node: GraphNode) -> None:
        if not node.color or node.color == "#00e5ff":
            node.color = self.GROUP_COLORS.get(node.group.lower(), "#00e5ff")
        self.nodes[node.id] = node

    def add_link(self, link: GraphLink) -> None:
        self.links.append(link)

    def load_from_dict(self, graph_dict: Dict[str, Any]) -> None:
        """
        Loads graph data from a standard {nodes: [...], links: [...]} dictionary.
        """
        self.clear()
        for nd in graph_dict.get("nodes", []):
            node = GraphNode(
                id=nd.get("id"),
                label=nd.get("label", str(nd.get("id"))),
                folder_name=nd.get("folder_name", "general"),
                group=nd.get("group", "default"),
                is_hub=bool(nd.get("is_hub", False)),
                val=float(nd.get("val", 4.5)),
                x=float(nd.get("x", 0.0)),
                y=float(nd.get("y", 0.0)),
                z=float(nd.get("z", 0.0)),
                excerpt=nd.get("excerpt", ""),
                color=nd.get("color", ""),
                metadata=nd.get("metadata", {}),
            )
            self.add_node(node)

        for lk in graph_dict.get("links", []):
            src = lk.get("source")
            tgt = lk.get("target")
            link = GraphLink(
                source=src,
                target=tgt,
                value=float(lk.get("value", 1.0)),
                label=lk.get("label", ""),
                link_type=lk.get("link_type", "related"),
                curvature=float(lk.get("curvature", 0.0)),
                color=lk.get("color", "rgba(0, 229, 255, 0.4)"),
            )
            self.add_link(link)

    def load_from_notes_directory(self, notes_dir: str) -> None:
        """
        Parses notes directory recursively:
        - Extracts hub folders
        - Reads markdown files, extracts titles, tags, and wikilinks [[Target]]
        - Links notes to hubs and to cross-referenced targets
        """
        self.clear()
        if not os.path.exists(notes_dir):
            return

        title_to_id: Dict[str, int] = {}
        curr_id = 0

        # Pass 1: Discover Hubs (Subdirectories)
        subdirs = [d for d in os.listdir(notes_dir) if os.path.isdir(os.path.join(notes_dir, d))]
        hub_ids: Dict[str, int] = {}

        for folder in subdirs:
            group_key = folder.lower().replace(" ", "-")
            hub_node = GraphNode(
                id=curr_id,
                label=f"📁 {folder}",
                folder_name=folder,
                group=group_key,
                is_hub=True,
                val=14.0,
                excerpt=f"Main Hub for {folder}",
            )
            self.add_node(hub_node)
            hub_ids[folder] = curr_id
            title_to_id[folder] = curr_id
            curr_id += 1

        # Pass 2: Ingest Notes
        for root, _, files in os.walk(notes_dir):
            for file in files:
                if not file.endswith(".md"):
                    continue
                file_path = os.path.join(root, file)
                rel_dir = os.path.relpath(root, notes_dir)
                folder_name = rel_dir if rel_dir != "." else "General"
                group_key = folder_name.lower().replace(" ", "-")

                note_title = os.path.splitext(file)[0]

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception:
                    content = ""

                # Extract excerpt
                excerpt_lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")]
                excerpt = excerpt_lines[0] if excerpt_lines else note_title

                note_node = GraphNode(
                    id=curr_id,
                    label=note_title,
                    folder_name=folder_name,
                    group=group_key,
                    is_hub=False,
                    val=4.5,
                    excerpt=excerpt[:300],
                    metadata={"file_path": file_path},
                )
                self.add_node(note_node)
                title_to_id[note_title] = curr_id

                # Link to hub if present
                if folder_name in hub_ids:
                    self.add_link(
                        GraphLink(
                            source=hub_ids[folder_name],
                            target=curr_id,
                            value=2.0,
                            link_type="hub_spoke",
                        )
                    )

                # Find wikilinks: [[Target Note]]
                wikilinks = re.findall(r"\[\[(.*?)\]\]", content)
                for w in wikilinks:
                    target_name = w.split("|")[0].strip()
                    # Will resolve links in Pass 3
                    note_node.metadata.setdefault("wikilinks", []).append(target_name)

                curr_id += 1

        # Pass 3: Resolve wikilinks
        for node_id, node in self.nodes.items():
            if node.is_hub:
                continue
            for target_title in node.metadata.get("wikilinks", []):
                # Try exact or case-insensitive match
                target_id = title_to_id.get(target_title)
                if target_id is None:
                    for t_name, t_id in title_to_id.items():
                        if t_name.lower() == target_title.lower():
                            target_id = t_id
                            break

                if target_id is not None and target_id != node_id:
                    self.add_link(
                        GraphLink(
                            source=node_id,
                            target=target_id,
                            value=1.5,
                            link_type="wikilink",
                            curvature=0.2,
                        )
                    )

        # Apply default layout
        self.apply_layout("galaxy")

    def apply_layout(self, layout_type: str = "galaxy", spread: float = 180.0) -> None:
        """
        Computes 3D coordinates (x, y, z) for all nodes based on algorithmic layout.
        Supported: 'galaxy', 'sphere', 'hierarchical'.
        """
        node_list = list(self.nodes.values())
        total = len(node_list)
        if total == 0:
            return

        if layout_type == "galaxy":
            # Group nodes by group/hub. Place hubs in an outer ring, spoke nodes orbiting their hub.
            hubs = [n for n in node_list if n.is_hub]
            hub_count = max(1, len(hubs))

            hub_positions: Dict[str, Tuple[float, float, float]] = {}
            for i, hub in enumerate(hubs):
                angle = (2 * math.pi * i) / hub_count
                hx = math.cos(angle) * spread * 0.85
                hz = math.sin(angle) * spread * 0.85
                hy = math.sin(angle * 2) * (spread * 0.3)
                hub.x = round(hx, 1)
                hub.y = round(hy, 1)
                hub.z = round(hz, 1)
                hub_positions[hub.group] = (hx, hy, hz)

            # Position spoke nodes in orbital shells around their group hub
            group_spokes: Dict[str, List[GraphNode]] = {}
            for n in node_list:
                if not n.is_hub:
                    group_spokes.setdefault(n.group, []).append(n)

            for group, spokes in group_spokes.items():
                center = hub_positions.get(group, (0.0, 0.0, 0.0))
                spoke_count = max(1, len(spokes))
                for j, snode in enumerate(spokes):
                    phi = (2 * math.pi * j) / spoke_count
                    r = (spread * 0.25) + ((j % 3) * (spread * 0.12))
                    sx = center[0] + math.cos(phi) * r
                    sz = center[2] + math.sin(phi) * r
                    sy = center[1] + ((j % 5) - 2) * 15.0
                    snode.x = round(sx, 1)
                    snode.y = round(sy, 1)
                    snode.z = round(sz, 1)

        elif layout_type == "sphere":
            # Fibonacci sphere distribution
            golden_ratio = (1 + math.sqrt(5)) / 2
            for i, node in enumerate(node_list):
                theta = 2 * math.pi * i / golden_ratio
                phi = math.acos(1 - 2 * (i + 0.5) / total)
                r = spread * (1.3 if not node.is_hub else 0.8)
                node.x = round(r * math.sin(phi) * math.cos(theta), 1)
                node.y = round(r * math.cos(phi), 1)
                node.z = round(r * math.sin(phi) * math.sin(theta), 1)

        elif layout_type == "hierarchical":
            # Multi-level hierarchical tree
            hubs = [n for n in node_list if n.is_hub]
            spokes = [n for n in node_list if not n.is_hub]
            # Level 0: Hubs at y = +100
            for i, hub in enumerate(hubs):
                hub.x = round((i - len(hubs) / 2) * 60, 1)
                hub.y = 100.0
                hub.z = 0.0
            # Level 1: Spokes below
            for j, spoke in enumerate(spokes):
                row = j // 8
                col = j % 8
                spoke.x = round((col - 4) * 45.0, 1)
                spoke.y = round(-40.0 - row * 50.0, 1)
                spoke.z = round(((j % 3) - 1) * 30.0, 1)

    def to_3d_force_graph_payload(self) -> Dict[str, Any]:
        """
        Outputs schema compatible with 3D force graph libraries.
        """
        nodes_out = []
        for n in self.nodes.values():
            nodes_out.append({
                "id": n.id,
                "label": n.label,
                "folder_name": n.folder_name,
                "group": n.group,
                "is_hub": n.is_hub,
                "val": n.val,
                "x": n.x,
                "y": n.y,
                "z": n.z,
                "excerpt": n.excerpt,
                "color": n.color,
            })

        links_out = []
        for l in self.links:
            links_out.append({
                "source": l.source,
                "target": l.target,
                "value": l.value,
                "link_type": l.link_type,
                "curvature": l.curvature,
                "color": l.color,
            })

        return {"nodes": nodes_out, "links": links_out}

    def to_d3_2d_payload(self) -> Dict[str, Any]:
        """
        Outputs 2D projected graph payload for D3.js simulations.
        """
        payload = self.to_3d_force_graph_payload()
        for n in payload["nodes"]:
            # Project x, z to 2D x, y
            n["r"] = n["val"] * 2.5
        return payload

    def to_cytoscape_payload(self) -> Dict[str, Any]:
        """
        Outputs Cytoscape.js elements format: {elements: {nodes: [...], edges: [...]}}.
        """
        cy_nodes = []
        for n in self.nodes.values():
            cy_nodes.append({
                "data": {
                    "id": str(n.id),
                    "label": n.label,
                    "group": n.group,
                    "is_hub": n.is_hub,
                },
                "position": {"x": n.x * 2, "y": n.y * 2},
            })

        cy_edges = []
        for idx, l in enumerate(self.links):
            cy_edges.append({
                "data": {
                    "id": f"e{idx}",
                    "source": str(l.source),
                    "target": str(l.target),
                    "type": l.link_type,
                }
            })
        return {"elements": {"nodes": cy_nodes, "edges": cy_edges}}

    def filter_subgraph(
        self,
        query: Optional[str] = None,
        groups: Optional[List[str]] = None,
        hub_only: bool = False,
        focus_node_id: Optional[Any] = None,
        max_hops: int = 1,
    ) -> "KnowledgeGraphAdapter":
        """
        Returns a new filtered KnowledgeGraphAdapter containing only matching nodes and connecting links.
        """
        sub = KnowledgeGraphAdapter()
        matched_ids: Set[Any] = set()

        if focus_node_id is not None and focus_node_id in self.nodes:
            matched_ids.add(focus_node_id)
            current_fringe = {focus_node_id}
            for _ in range(max_hops):
                next_fringe = set()
                for link in self.links:
                    if link.source in current_fringe:
                        matched_ids.add(link.target)
                        next_fringe.add(link.target)
                    elif link.target in current_fringe:
                        matched_ids.add(link.source)
                        next_fringe.add(link.source)
                current_fringe = next_fringe

        else:
            q_lower = query.lower().strip() if query else None
            g_set = set(g.lower() for g in groups) if groups else None

            for nid, node in self.nodes.items():
                if hub_only and not node.is_hub:
                    continue
                if g_set and node.group.lower() not in g_set:
                    continue
                if q_lower:
                    if (q_lower not in node.label.lower() and
                            q_lower not in node.excerpt.lower() and
                            q_lower not in node.folder_name.lower()):
                        continue
                matched_ids.add(nid)

        # Populate subgraph
        for nid in matched_ids:
            if nid in self.nodes:
                sub.add_node(self.nodes[nid])

        for lk in self.links:
            if lk.source in matched_ids and lk.target in matched_ids:
                sub.add_link(lk)

        return sub

    @staticmethod
    def compute_graph_diff(
        old_payload: Dict[str, Any], new_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates incremental differences between two graph states.
        Enables seamless live visual updates without reloading the 3D scene.
        """
        old_nodes = {n["id"]: n for n in old_payload.get("nodes", [])}
        new_nodes = {n["id"]: n for n in new_payload.get("nodes", [])}

        old_links = {(l["source"], l["target"]): l for l in old_payload.get("links", [])}
        new_links = {(l["source"], l["target"]): l for l in new_payload.get("links", [])}

        added_node_ids = set(new_nodes.keys()) - set(old_nodes.keys())
        removed_node_ids = set(old_nodes.keys()) - set(new_nodes.keys())
        common_node_ids = set(new_nodes.keys()) & set(old_nodes.keys())

        modified_nodes = []
        for nid in common_node_ids:
            o_n = old_nodes[nid]
            n_n = new_nodes[nid]
            if (o_n.get("label") != n_n.get("label") or
                    o_n.get("val") != n_n.get("val") or
                    o_n.get("group") != n_n.get("group")):
                modified_nodes.append(n_n)

        added_link_keys = set(new_links.keys()) - set(old_links.keys())
        removed_link_keys = set(old_links.keys()) - set(new_links.keys())

        return {
            "added_nodes": [new_nodes[nid] for nid in added_node_ids],
            "removed_nodes": [old_nodes[nid] for nid in removed_node_ids],
            "modified_nodes": modified_nodes,
            "added_links": [new_links[k] for k in added_link_keys],
            "removed_links": [old_links[k] for k in removed_link_keys],
            "total_nodes": len(new_nodes),
            "total_links": len(new_links),
        }

    def render_svg_preview(self, width: int = 700, height: int = 450) -> str:
        """
        Generates a 2D projected SVG preview diagram of the graph with glowing hubs and cyan links.
        """
        cx = width / 2
        cy = height / 2

        # Find min/max bounds for scaling
        all_nodes = list(self.nodes.values())
        if not all_nodes:
            return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><text x="20" y="30" fill="#fff">Empty Graph</text></svg>'

        max_coord = max(max(abs(n.x), abs(n.y), 1.0) for n in all_nodes)
        scale = (min(width, height) * 0.4) / max_coord

        # Render links
        links_svg = ""
        for l in self.links:
            s_node = self.nodes.get(l.source)
            t_node = self.nodes.get(l.target)
            if s_node and t_node:
                x1 = cx + s_node.x * scale
                y1 = cy + s_node.y * scale
                x2 = cx + t_node.x * scale
                y2 = cy + t_node.y * scale
                stroke_color = "#00e5ff" if l.link_type == "hub_spoke" else "rgba(56, 189, 248, 0.35)"
                width_px = 1.5 if l.link_type == "hub_spoke" else 0.8
                links_svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke_color}" stroke-width="{width_px}"/>\n'

        # Render nodes
        nodes_svg = ""
        for n in all_nodes:
            nx = cx + n.x * scale
            ny = cy + n.y * scale
            r = 7.0 if n.is_hub else 3.5
            color = n.color or "#00e5ff"

            if n.is_hub:
                # Outer glow ring
                nodes_svg += f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{r + 4}" fill="none" stroke="{color}" stroke-width="1" stroke-opacity="0.4"/>\n'
                nodes_svg += f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{r}" fill="{color}" />\n'
                label_clean = n.label[:18]
                nodes_svg += f'<text x="{nx + r + 4:.1f}" y="{ny + 3:.1f}" fill="#ffffff" font-family="monospace" font-size="9" font-weight="bold">{label_clean}</text>\n'
            else:
                nodes_svg += f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{r}" fill="{color}" fill-opacity="0.85"/>\n'

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <rect width="{width}" height="{height}" fill="#040d1a" rx="6" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.4"/>
    <text x="20" y="28" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" letter-spacing="1.5">// KNOWLEDGE GRAPH ADAPTER PREVIEW: {len(self.nodes)} NODES | {len(self.links)} LINKS</text>
    <g class="graph-viewport">
        {links_svg}
        {nodes_svg}
    </g>
</svg>"""
        return svg
