"""
Knowledge Graph & Markdown Retrieval Engine for J.A.R.V.I.S.
"""
import re
import json
import pathlib
from ..config import ROOT_DIR, NOTES_DIR, VIEWER_DIR

GRAPH_DATA_FILE = VIEWER_DIR / "graph-data.js"


def load_graph_data():
    """Loads graph nodes and links from graph-data.js."""
    if not GRAPH_DATA_FILE.exists():
        import build
        return build.rebuild()
    try:
        content = GRAPH_DATA_FILE.read_text(encoding="utf-8")
        json_str = re.sub(r'^[^{]*', '', content).rstrip(';\n ')
        return json.loads(json_str)
    except Exception as e:
        import build
        return build.rebuild()


def scan_full_texts():
    """Scans all markdown notes and maps note stem -> full text."""
    texts = {}
    for p in NOTES_DIR.rglob("*.md"):
        try:
            texts[p.stem] = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
    return texts


def search_notes_fast(query, top_k=6):
    """Searches notes by matching query tokens against titles and text."""
    graph = load_graph_data()
    texts = scan_full_texts()
    tokens = set(re.findall(r'[a-zA-Z0-9]{2,}', query.lower()))

    scored = []
    for node in graph["nodes"]:
        label = node["label"].lower()
        full_text = texts.get(node["label"], "").lower()
        score = 0
        for tok in tokens:
            if tok in label:
                score += 5
            score += min(full_text.count(tok), 6)

        if score > 0:
            scored.append({
                "node": node,
                "score": score,
                "text_snippet": full_text[:400] + ("…" if len(full_text) > 400 else "")
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"status": "success", "results": scored[:top_k], "total_matches": len(scored)}
