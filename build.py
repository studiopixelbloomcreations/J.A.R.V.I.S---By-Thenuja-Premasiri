#!/usr/bin/env python3
"""
build.py — Scans every .md file in the notes/ folder and writes viewer/graph-data.js
containing const GRAPH = {nodes: [...], links: [...]}.

Architecture:
- Every folder in notes/ has a dedicated Main Hub Orb (e.g. "✦ Finance", "✦ Operations").
- All notes inside a folder are linked to their folder's Main Hub Orb (Spokes).
- All Main Hub Orbs are interconnected to each other (Galactic Backbone).
- Notes are also cross-linked when one mentions another's title or [[wikilinks]] (References).
- Every node has a numeric id strictly equal to its position in the nodes array.
"""

import os
import re
import json
import pathlib

NOTES_DIR = pathlib.Path(__file__).parent / "notes"
OUTPUT_FILE = pathlib.Path(__file__).parent / "viewer" / "graph-data.js"

WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')


def scan_notes(notes_dir):
    """Scan all .md files and return a list of note dicts."""
    notes = []
    for root, _dirs, files in os.walk(notes_dir):
        for fname in sorted(files):
            if not fname.lower().endswith('.md'):
                continue
            fpath = pathlib.Path(root) / fname
            rel = fpath.relative_to(notes_dir)
            parts = rel.parts
            # Group is top-level subfolder, or "general" if in root of notes
            group = parts[0] if len(parts) > 1 else "general"
            label = fpath.stem
            text = fpath.read_text(encoding='utf-8', errors='replace')
            excerpt = _make_excerpt(text, 700)
            wikilinks = set(WIKILINK_RE.findall(text))
            notes.append({
                'label': label,
                'group': group,
                'excerpt': excerpt,
                'text': text,
                'wikilinks': wikilinks,
            })
    return notes


def _make_excerpt(text, length=700):
    """Create a clean excerpt from markdown text."""
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            cleaned.append('')
            continue
        line = re.sub(r'^#{1,6}\s+', '', line)
        if re.match(r'^[\|\-\s:]+$', line):
            continue
        line = re.sub(r'\[\[([^\]]+)\]\]', r'\1', line)
        line = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', line)
        line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        line = re.sub(r'^-\s*\[[ x]\]\s*', '• ', line)
        line = re.sub(r'^[-*]\s+', '• ', line)
        line = re.sub(r'^\d+\.\s+', '', line)
        cleaned.append(line)
    result = ' '.join(l for l in cleaned if l).strip()
    if len(result) > length:
        result = result[:length]
        last_space = result.rfind(' ')
        if last_space > length * 0.7:
            result = result[:last_space]
        result += '…'
    return result


def build_links(notes, label_to_idx):
    """Determine reference links between notes based on wikilinks and title mentions."""
    links = set()
    for note in notes:
        my_id = label_to_idx.get(note['label'])
        if my_id is None:
            continue

        for wl in note['wikilinks']:
            if wl in label_to_idx:
                target_id = label_to_idx[wl]
                if my_id != target_id:
                    links.add((min(my_id, target_id), max(my_id, target_id)))

        text_lower = note['text'].lower()
        for other_label, target_id in label_to_idx.items():
            if my_id == target_id:
                continue
            if len(other_label) >= 4 and other_label.lower() in text_lower:
                links.add((min(my_id, target_id), max(my_id, target_id)))

    return [{'source': s, 'target': t, 'type': 'reference'} for s, t in sorted(links)]


FOLDER_CENTROIDS = {
    "personal":        (-850,  450, -750),  # Top-left rear sector
    "finance":         ( 850, -350,  750),  # Bottom-right front sector (Far from personal!)
    "operations":      (-750, -500,  650),  # Bottom-left front sector
    "marketing":       ( 750,  600, -550),  # Top-right rear sector
    "products":        ( 800, -500, -650),  # Bottom-right rear sector
    "team":            (-800,  300,  800),  # Top-left front sector
    "captures":        (   0, -900, -450),  # Far bottom sector
    "apex-logistics":  (   0,  900,  550),  # Far top sector
}


def generate_graph(notes_dir):
    """Generate the full hierarchical galaxy structure with expanded spatial grouping."""
    import random
    import math

    # 1. Discover all folders in notes/
    folders = sorted([d.name for d in notes_dir.iterdir() if d.is_dir()])
    has_root_notes = any(f.is_file() and f.suffix.lower() == '.md' for f in notes_dir.iterdir())
    if has_root_notes and "general" not in folders:
        folders.append("general")
    if not folders:
        folders = ["general"]

    nodes = []
    links = []
    hub_map = {}
    hub_coords = {}

    # 2. Create Main Hub Orbs (one per folder) anchored in distinct, distant sectors
    for idx, f in enumerate(folders):
        hub_id = len(nodes)
        hub_map[f] = hub_id
        display_name = f.replace('-', ' ').title()

        if f in FOLDER_CENTROIDS:
            cx, cy, cz = FOLDER_CENTROIDS[f]
        else:
            # Golden spiral on sphere of radius 850 for any additional folders
            phi = math.acos(1 - 2 * (idx + 0.5) / max(len(folders), 1))
            theta = math.pi * (1 + 5**0.5) * idx
            cx = round(850 * math.sin(phi) * math.cos(theta), 1)
            cy = round(850 * math.sin(phi) * math.sin(theta), 1)
            cz = round(850 * math.cos(phi), 1)

        hub_coords[f] = (cx, cy, cz)

        nodes.append({
            'id': hub_id,
            'label': f"📁 {display_name}",
            'folder_name': display_name,
            'group': f,
            'is_hub': True,
            'val': 24,
            'x': cx,
            'y': cy,
            'z': cz,
            'fx': cx,
            'fy': cy,
            'fz': cz,
            'excerpt': f"Main Central Hub for all intelligence, notes, and operations in the '{display_name}' sector."
        })

    # 3. Interconnect all Main Hub Orbs (Galactic Backbone)
    hub_ids = list(hub_map.values())
    for i in range(len(hub_ids)):
        for j in range(i + 1, len(hub_ids)):
            links.append({
                'source': hub_ids[i],
                'target': hub_ids[j],
                'type': 'backbone'
            })

    # 4. Scan all markdown notes and place them in an orbital shell around their folder hub
    raw_notes = scan_notes(notes_dir)
    label_to_id = {}

    for note in raw_notes:
        note_id = len(nodes)
        label_to_id[note['label']] = note_id
        parent_group = note['group']
        cx, cy, cz = hub_coords.get(parent_group, (0, 0, 0))

        # Position note in an orbital cluster around its parent folder hub
        r_offset = random.uniform(60, 130)
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(-math.pi / 2, math.pi / 2)
        nx = cx + r_offset * math.cos(phi) * math.cos(theta)
        ny = cy + r_offset * math.sin(phi)
        nz = cz + r_offset * math.cos(phi) * math.sin(theta)

        nodes.append({
            'id': note_id,
            'label': note['label'],
            'group': parent_group,
            'is_hub': False,
            'val': 5,
            'x': round(nx, 1),
            'y': round(ny, 1),
            'z': round(nz, 1),
            'excerpt': note['text']
        })

        # Link to its folder's Main Hub Orb (Spoke)
        parent_hub = hub_map.get(parent_group)
        if parent_hub is not None:
            links.append({
                'source': note_id,
                'target': parent_hub,
                'type': 'spoke'
            })

    # 5. Cross-reference links
    ref_links = build_links(raw_notes, label_to_id)
    links.extend(ref_links)

    return {
        'nodes': nodes,
        'links': links,
        'groups': folders,
        'centroids': FOLDER_CENTROIDS
    }


def rebuild():
    """Rebuilds the graph from disk and writes viewer/graph-data.js."""
    graph = generate_graph(NOTES_DIR)
    os.makedirs(OUTPUT_FILE.parent, exist_ok=True)
    js_content = "const GRAPH = " + json.dumps(graph, indent=2) + ";\n"
    OUTPUT_FILE.write_text(js_content, encoding='utf-8')
    return graph


def main():
    print(f"Scanning notes in: {NOTES_DIR}")
    graph = rebuild()
    hubs_count = sum(1 for n in graph['nodes'] if n.get('is_hub'))
    notes_count = len(graph['nodes']) - hubs_count
    print(f"Generated {len(graph['nodes'])} total nodes ({hubs_count} Main Hub Orbs + {notes_count} Notes)")
    print(f"Generated {len(graph['links'])} links (Backbone + Spokes + References)")
    print(f"Groups: {', '.join(graph['groups'])}")

    os.makedirs(OUTPUT_FILE.parent, exist_ok=True)
    js_content = "const GRAPH = " + json.dumps(graph, indent=2) + ";\n"
    OUTPUT_FILE.write_text(js_content, encoding='utf-8')
    print(f"Wrote {OUTPUT_FILE} ({len(js_content)} bytes)")


if __name__ == '__main__':
    main()
