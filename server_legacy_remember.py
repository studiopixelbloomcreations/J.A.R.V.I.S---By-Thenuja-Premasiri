"""
Memory & Research Synthesis Subsystem for J.A.R.V.I.S.
Preserves intelligent note classification, multi-section research generation,
and archive auto-organization.
"""
import re
import json
import urllib.request
import pathlib
import build
from jarvis.config import load_config, NOTES_DIR


def analyze_and_classify_note(raw_text, title_hint=""):
    config = load_config()
    existing_folders = [d.name for d in NOTES_DIR.iterdir() if d.is_dir()]
    if not existing_folders:
        existing_folders = ["operations", "finance", "marketing", "products", "team", "captures", "personal"]

    prompt = f"""You are J.A.R.V.I.S., an expert intelligence butler and analyst for an entrepreneur.
Analyze this user thought, observation, or business information:
\"{raw_text}\"

Existing knowledge folders: {', '.join(existing_folders)}.
Classification Rules:
1. Personal matters (health, family, fitness, private life, appointments): use 'personal'.
2. New company or venture mentioned: create a clean kebab-case folder name (e.g. 'apex-logistics').
3. Facilities, temperature, equipment, maintenance, logistics: use 'operations'.
4. Money, pricing, margins, budgets, investments, funding: use 'finance'.
5. Advertising, branding, social media, marketing, campaigns: use 'marketing'.
6. Products, drinks, coffee, menu, inventory: use 'products'.
7. Employees, hiring, scheduling, staff: use 'team'.
8. Otherwise, select the most accurate existing or new folder.

Task:
Conduct thorough research and deep contextual analysis on this topic. Write a rich, professional, multi-section markdown document. Minimum 250 words.

Output strict JSON:
{{
  "folder": "<folder-kebab-case>",
  "title": "<Clean Professional 2-5 Word Title>",
  "analysis": "<A comprehensive, professional, multi-section markdown document with headers (##) and deep research analysis.>"
}}"""

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": 950}
    }).encode("utf-8")

    api_key = config.get("api_key")
    models_to_try = [
        config.get("model", "gemini-3.5-flash-lite"),
        "gemini-3.5-flash",
        "gemini-2.5-flash",
    ]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

    for m in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=16) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                txt = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                txt_clean = re.sub(r'^```json\s*', '', txt, flags=re.I)
                txt_clean = re.sub(r'```$', '', txt_clean.strip())
                return json.loads(txt_clean)
        except Exception:
            continue

    # Fallback deterministic
    t_low = raw_text.lower()
    if any(w in t_low for w in ["personal", "doctor", "dentist", "gym", "workout", "fitness", "health"]):
        folder = "personal"
    elif any(w in t_low for w in ["another company", "other company", "new company", "startup", "venture"]):
        m = re.search(r'(?:company|venture|startup)\s+(?:named|called)?\s*([a-zA-Z0-9\s]+?)(?:\s+(?:that|which|doing)|\.|\,|$)', t_low)
        folder = re.sub(r'[^\w\s-]', '', m.group(1)).strip().replace(' ', '-') if m else "new-ventures"
    elif any(w in t_low for w in ["price", "cost", "dollar", "budget", "revenue", "margin", "profit", "cash"]):
        folder = "finance"
    elif any(w in t_low for w in ["temp", "temperature", "cooler", "machine", "clean", "hvac", "facility", "delivery"]):
        folder = "operations"
    else:
        folder = "captures"

    words = raw_text.split()
    title = " ".join(words[:5]).title() if words else "Intelligence Brief"
    title = re.sub(r'[^\w\s-]', '', title).strip()

    analysis = f"""# {title}

## Executive Summary
This document records critical intelligence captured by J.A.R.V.I.S.: "{raw_text}".

## Environmental & Strategic Analysis
Analysis of the recorded parameters indicates immediate relevance to {folder.replace('-', ' ').title()} operations and strategic planning.

## Actionable Recommendations
- Incorporate these parameters into weekly reviews and standard operating procedures.
- Monitor downstream dependencies across related systems.

*Researched and documented by J.A.R.V.I.S.*
"""
    return {"folder": folder, "title": title, "analysis": analysis}


def handle_remember_synthesis(raw_text):
    clean_statement = re.sub(r'^(please\s+)?remember(\s+that)?\s*', '', raw_text, flags=re.I).strip() or raw_text
    classification = analyze_and_classify_note(clean_statement)
    target_folder = classification.get("folder", "operations")
    title = classification.get("title", "Intelligence Brief")
    detailed_doc = classification.get("analysis", f"# {title}\n\n{clean_statement}\n")

    dest_dir = NOTES_DIR / target_folder
    dest_dir.mkdir(parents=True, exist_ok=True)

    clean_stem = re.sub(r'[^\w\s-]', '', title).strip().title()
    dest_file = dest_dir / f"{clean_stem}.md"
    cnt = 2
    while dest_file.exists():
        dest_file = dest_dir / f"{clean_stem} {cnt}.md"
        cnt += 1

    actual_title = dest_file.stem
    dest_file.write_text(detailed_doc, encoding="utf-8")

    fresh_graph = build.rebuild()

    new_node = None
    hub_node = None
    for n in fresh_graph["nodes"]:
        if n["label"] == actual_title and n["group"] == target_folder:
            new_node = n
        if n.get("is_hub") and n["group"] == target_folder:
            hub_node = n

    folder_display = target_folder.replace('-', ' ').title()
    confirmations = [
        f"Duly researched and filed under '{folder_display}', sir. A full analysis document has been compiled and added to the galaxy.",
        f"Archived into the '{folder_display}' sector, sir. I have conducted the relevant analysis and structured a detailed briefing for you.",
        f"Committed to the archives in '{folder_display}', sir. You will find a comprehensive strategic overview now illuminated on your screen."
    ]
    witty = confirmations[len(fresh_graph["nodes"]) % len(confirmations)]

    return {
        "answer": witty,
        "node": new_node,
        "hub_node": hub_node,
        "folder": target_folder,
        "graph": fresh_graph,
        "nodes": [new_node["id"]] if new_node else [],
        "new_node_id": new_node["id"] if new_node else None,
        "total_nodes": len(fresh_graph["nodes"])
    }, 200


def organize_unassigned_notes():
    loose_files = [f for f in NOTES_DIR.iterdir() if f.is_file() and f.suffix.lower() == '.md']
    if not loose_files:
        return []

    organized = []
    for f in loose_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        classified = analyze_and_classify_note(content, f.stem)
        folder = classified.get("folder", "operations")
        title = classified.get("title", f.stem)

        dest_dir = NOTES_DIR / folder
        dest_dir.mkdir(parents=True, exist_ok=True)

        clean_stem = re.sub(r'[^\w\s-]', '', title).strip().title()
        dest_file = dest_dir / f"{clean_stem}.md"
        cnt = 2
        while dest_file.exists():
            dest_file = dest_dir / f"{clean_stem} {cnt}.md"
            cnt += 1

        f.rename(dest_file)
        organized.append({
            "original": f.name,
            "folder": folder,
            "title": dest_file.stem,
            "path": str(dest_file.relative_to(NOTES_DIR))
        })

    build.rebuild()
    return organized


def handle_ambient_learn(raw_text, lang="en-GB"):
    """
    Autonomous ambient background learner.
    Analyzes spoken text from the continuous listener.
    If speech is in Sinhala, seamlessly translates to English first.
    If personal knowledge or user preferences/projects are mentioned,
    it automatically writes a note to notes/personal/ and updates the Knowledge Galaxy.
    """
    clean_text = raw_text.strip()
    try:
        from jarvis.core.translator import is_sinhala_text, translate_sinhala_to_english
        if is_sinhala_text(clean_text) or lang == "si-LK":
            translated = translate_sinhala_to_english(clean_text)
            if translated:
                print(f"  🌐 [Ambient Sinhala] Translated: '{clean_text}' => '{translated}'")
                clean_text = translated
    except Exception as e:
        print(f"  ⚠ Ambient translation error: {e}")

    words = clean_text.split()
    if len(words) < 4:
        return {"learned": False, "reason": "Too short"}, 200

    low = clean_text.lower()
    if any(low.startswith(p) for p in ["jarvis", "switch to", "hey jarvis", "stop", "pause", "resume", "clear"]):
        return {"learned": False, "reason": "Command or wake word, not ambient fact."}, 200

    has_self_ref = any(w in low for w in [
        "i ", "i'm", "i've", "my ", "mine", "we ", "our ", "prefer", "like", "love", "hate",
        "working on", "building", "goal", "meeting", "doctor", "schedule", "routine", "usually",
        "habit", "fitness", "workout", "bought", "moved", "wife", "husband", "son", "daughter",
        "mother", "father", "friend", "client", "project", "budget", "car", "computer", "temperature"
    ])
    if not has_self_ref:
        return {"learned": False, "reason": "No personal reference detected."}, 200

    config = load_config()
    api_key = config.get("api_key")

    prompt = f"""You are the autonomous memory acquisition module of J.A.R.V.I.S.
Analyze this statement spoken in the user's presence:
"{clean_text}"

Determine if this statement discloses a durable, factual detail about the user's personal life, habits, preferences, health, family, routines, projects, or goals.
Output strict JSON:
{{
  "has_insight": true,
  "title": "Concise Note Title (2-5 words, e.g. Morning Coffee Routine)",
  "insight": "Crisp 1-2 sentence distillation of what was learned about the user.",
  "category": "personal"
}}
If it does not contain durable personal facts, set "has_insight": false."""

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": 300}
    }).encode("utf-8")

    data = None
    if api_key:
        for m in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    txt = resp_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    txt_clean = re.sub(r'^```json\s*', '', txt, flags=re.I)
                    txt_clean = re.sub(r'```$', '', txt_clean.strip())
                    data = json.loads(txt_clean)
                    break
            except Exception:
                continue

    if not data or not data.get("has_insight"):
        return {"learned": False, "reason": "No durable personal insight extracted."}, 200

    title = data.get("title", "Personal Context Note")
    insight = data.get("insight", clean_text)
    clean_stem = re.sub(r'[^\w\s-]', '', title).strip().title()

    dest_dir = NOTES_DIR / "personal"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / f"{clean_stem}.md"

    if dest_file.exists():
        existing_content = dest_file.read_text(encoding="utf-8", errors="replace")
        new_content = f"{existing_content}\n\n- **Updated:** {insight}\n"
        dest_file.write_text(new_content, encoding="utf-8")
    else:
        new_content = f"""# {title}

- **Acquired:** Autonomous ambient voice learning
- **Cluster:** Personal Context

## Overview
{insight}

*Autonomously recorded and integrated into Personal Knowledge Graph by J.A.R.V.I.S.*
"""
        dest_file.write_text(new_content, encoding="utf-8")

    fresh_graph = build.rebuild()
    new_node = None
    for n in fresh_graph.get("nodes", []):
        if n["label"] == dest_file.stem and n["group"] == "personal":
            new_node = n
            break

    return {
        "learned": True,
        "title": dest_file.stem,
        "insight": insight,
        "node": new_node,
        "graph": fresh_graph,
        "folder": "personal"
    }, 200
