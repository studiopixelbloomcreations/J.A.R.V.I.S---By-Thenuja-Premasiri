#!/usr/bin/env python3
"""
server.py — Serves the viewer/ folder on port 4700 and exposes a
POST /chat endpoint that answers questions from the user's notes
using the Anthropic Messages API.

The API key lives in config.json (project root, never served).
"""

import http.server
import json
import os
import re
import socket
import sys
import uuid
import urllib.request
import urllib.error
import pathlib
import time

import build

# Force IPv4 on Windows to prevent network hanging on IPv6 lookups
_orig_getaddrinfo = socket.getaddrinfo
def _getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _getaddrinfo_ipv4

PORT = 4700
BASE_DIR = pathlib.Path(__file__).parent.resolve()
VIEWER_DIR = BASE_DIR / "viewer"
CONFIG_FILE = BASE_DIR / "config.json"
NOTES_DIR = BASE_DIR / "notes"
GRAPH_JS = VIEWER_DIR / "graph-data.js"

# ─── In-memory session store ────────────────────────────────────
# session_id → list of {"role": "user"|"assistant", "content": str}
sessions = {}
MAX_HISTORY = 12   # keep last 12 messages (6 exchanges) per session
SESSION_TTL = 3600  # 1 hour
session_timestamps = {}


def load_config():
    """Load API key and model from config.json."""
    if not CONFIG_FILE.exists():
        print("ERROR: config.json not found. Create it with your API key.")
        sys.exit(1)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if cfg.get("api_key", "").startswith("PUT-YOUR"):
        print("WARNING: config.json still has the placeholder API key.")
        print("         Paste your real Anthropic API key into config.json.")
    return cfg


def load_graph_data():
    """Parse viewer/graph-data.js to extract the GRAPH object."""
    content = GRAPH_JS.read_text(encoding="utf-8")
    # Strip "const GRAPH = " prefix and trailing ";\n"
    json_str = content.split("const GRAPH = ", 1)[1].rstrip().rstrip(";")
    return json.loads(json_str)


def scan_full_texts():
    """Scan all .md files and return {label: full_text}."""
    texts = {}
    for root, _dirs, files in os.walk(NOTES_DIR):
        for fname in sorted(files):
            if not fname.lower().endswith(".md"):
                continue
            fpath = pathlib.Path(root) / fname
            label = fpath.stem
            texts[label] = fpath.read_text(encoding="utf-8", errors="replace")
    return texts


def score_note(question_keywords, label, text):
    """Score a note's relevance to the question via keyword overlap.
    Title matches weigh 3×.  Text occurrence capped at 5 per keyword."""
    if not question_keywords:
        return 0

    label_lower = label.lower()
    text_lower = text.lower()
    score = 0

    for kw in question_keywords:
        # Title match weighs 3×
        if kw in label_lower:
            score += 3
        # Count in text body, cap at 5
        score += min(text_lower.count(kw), 5)

    return score


STOP_WORDS = frozenset(
    "a an the is are was were be been being have has had do does did will would "
    "could should may might can shall to of in for on with at by from as into "
    "about through during before after above below between and but or nor not so "
    "yet both either neither each every all any few more most other some such no "
    "only own same than too very just because what which who whom this that these "
    "those i me my we our you your he him his she her it its they them their how "
    "when where why if then else much many also".split()
)


def extract_keywords(text):
    """Extract meaningful keywords from a question string."""
    words = set(re.findall(r"[a-zA-Z]{2,}", text.lower()))
    return words - STOP_WORDS


def find_top_notes(question, graph_data, full_texts, top_k=6):
    """Score all notes and return the top-k as (node, full_text, score) tuples."""
    keywords = extract_keywords(question)
    scored = []

    for node in graph_data["nodes"]:
        label = node["label"]
        text = full_texts.get(label, "")
        s = score_note(keywords, label, text)
        scored.append((node, text, s))

    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]


def _execute_gemini_request(api_key, model, payload, timeout=15):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        candidates = body.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "text" in part:
                    return part["text"]
        return "No response generated."


def call_gemini(config, system_prompt, messages):
    """Call the Google Gemini API with fallback for high demand/timeouts."""
    api_key = config["api_key"]
    model = config.get("model", "gemini-3.8-flash")

    contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else msg["role"]
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}],
        })

    payload = json.dumps({
        "system_instruction": {
            "parts": [{"text": system_prompt}],
        },
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 400,
            "temperature": 0.4,
        },
    }).encode("utf-8")

    # Try configured model first, fallback to gemini-3.5-flash-lite if overloaded or timed out
    models_to_try = [model]
    fallback_model = "gemini-3.5-flash-lite"
    if model != fallback_model:
        models_to_try.append(fallback_model)

    last_error = None
    for current_model in models_to_try:
        try:
            print(f"  🤖 Requesting {current_model}...")
            # Use 12s timeout so requests don't hang indefinitely
            ans = _execute_gemini_request(api_key, current_model, payload, timeout=12)
            print(f"  ✓ Response received from {current_model}")
            return ans
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"  ⚠ {current_model} HTTP {e.code}: {err_body[:120]}")
            last_error = f"Gemini API error {e.code}: {err_body}"
            # If 503 or 404, loop will try fallback
            continue
        except (TimeoutError, urllib.error.URLError) as e:
            print(f"  ⚠ {current_model} timed out / network error: {e}")
            last_error = f"{current_model} timed out: {e}"
            continue
        except Exception as e:
            print(f"  ⚠ {current_model} error: {e}")
            last_error = str(e)
            continue

    raise RuntimeError(last_error or "All model requests failed.")


def build_system_prompt(top_notes):
    """Build the system prompt with note excerpts for context."""
    context_parts = []
    for node, text, _score in top_notes:
        # Truncate each note to ~1200 chars to fit context budget
        snippet = text[:1200]
        if len(text) > 1200:
            snippet += "…"
        context_parts.append(
            f"--- NOTE [{node['id']}]: \"{node['label']}\" (group: {node['group']}) ---\n"
            f"{snippet}"
        )

    notes_block = "\n\n".join(context_parts)

    return (
        "You are Jarvis, an impeccably polite British butler possessed of a razor-sharp wit and understated dry humor.\n\n"
        "CORE RULES:\n"
        "1. Personality: Impeccably polite, dry, subtly satirical, and supremely refined. Address the user as 'sir' (occasionally and naturally, never in every sentence). One genuinely funny line beats three bland ones.\n"
        "2. Conciseness: Answer questions about notes in exactly ONE witty sentence plus the pertinent facts. Never recite the note back (the full document is already presented on the screen before the user).\n"
        "3. Note Citations: Whenever drawing upon the notes, cite the source note ID in brackets like [3] or [16] immediately after the relevant fact.\n"
        "4. Missing Information: If the notes do not cover the inquiry, observe dryly that the archives remain silent on the subject. Do not invent answers.\n"
        "5. Small Talk & Jokes: When greeted or engaged in casual banter, respond with razor-sharp butler repartee, and strictly do NOT cite any note IDs.\n\n"
        f"=== ARCHIVED NOTES ===\n\n{notes_block}\n\n=== END OF ARCHIVES ==="
    )


def detect_brain_switch(text):
    """Detect if the user wants to switch the AI brain."""
    t = text.lower().strip()
    if re.search(r'\b(switch|change|set|turn|go|activate|enable|use|back)\b.*?\b(gemini\s*live|live|voice)\b', t):
        return "gemini-live"
    if re.search(r'\b(switch|change|set|turn|go|activate|enable|use|back)\b.*?\b(gemini\s*3|3\.5|three|flash|text|standard)\b', t):
        return "gemini-3.5"
    return None


def handle_fish_audio_tts(body, config):
    """Handle text-to-speech request via Fish Audio API."""
    text = body.get("text", "").strip()
    if not text:
        return {"error": "No text provided"}, 400

    fish_cfg = config.get("fish_audio", {})
    api_key = fish_cfg.get("api_key", "").strip()

    # If key is missing or placeholder, indicate fallback to browser voice
    if not api_key or api_key.startswith("PUT-YOUR"):
        return {"fallback": True, "message": "Fish Audio key not configured, using browser voice."}, 200

    model = fish_cfg.get("model", "s2.1-pro-free")
    ref_id = fish_cfg.get("reference_id", "").strip()

    payload = {
        "text": text,
        "format": "mp3",
        "mp3_bitrate": 64,
        "latency": "normal",
    }
    if ref_id:
        payload["reference_id"] = ref_id

    req = urllib.request.Request(
        "https://api.fish.audio/v1/tts",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "model": model,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            audio_bytes = resp.read()
            return audio_bytes, 200
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        print(f"  ⚠ Fish Audio HTTP error {e.code}: {err_msg[:120]}")
        return {"fallback": True, "error": f"Fish Audio error {e.code}"}, 200
    except Exception as e:
        print(f"  ⚠ Fish Audio exception: {e}")
        return {"fallback": True, "error": str(e)}, 200


def analyze_and_classify_note(raw_text, title_hint, config):
    """
    Intelligently analyzes note text using Gemini or deterministic rules:
    - Identifies target domain (personal, operations, finance, marketing, products, team, or new company).
    - Generates clean title.
    - Generates full research markdown document.
    """
    existing_folders = [d.name for d in NOTES_DIR.iterdir() if d.is_dir()]
    if not existing_folders:
        existing_folders = ["operations", "finance", "marketing", "products", "team", "captures", "personal"]

    prompt = f"""You are Jarvis, an expert intelligence butler for an entrepreneur.
Analyze this user thought, observation, or business information:
\"{raw_text}\"

Existing knowledge folders: {', '.join(existing_folders)}.
Classification Rules:
1. Personal matters (health, family, fitness, private life, appointments): use 'personal'.
2. New company or venture mentioned (e.g. 'I have another company named Apex Logistics', 'my other startup'): create a clean kebab-case folder (e.g. 'apex-logistics').
3. Store, cafe, floral, temperature, equipment, facilities, logistics, delivery: use 'operations'.
4. Money, pricing, margins, budgets, investments, funding: use 'finance'.
5. Advertising, branding, social media, email campaigns, partnerships: use 'marketing'.
6. Coffee varieties, drinks, arrangements, merchandise: use 'products'.
7. Employees, hiring, scheduling, baristas: use 'team'.
8. Otherwise, select the most accurate existing or new folder.

Output strict JSON:
{{
  "folder": "<folder-name-kebab-case>",
  "folder_label": "<Clean Title Case Name>",
  "title": "<Clean Professional 2-5 Word Title>",
  "analysis": "<A comprehensive, professional, multi-section markdown document that researches this fact, explores contextual implications, operational/strategic impact, and actionable next steps. Minimum 250 words.>"
}}"""

    try:
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": 950}
        }).encode("utf-8")

        api_key = config.get("api_key")
        models_to_try = [
            config.get("model", "gemini-3.5-flash"),
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
        ]
        # Deduplicate while preserving order
        seen = set()
        models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

        for current_model in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent"
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
            except Exception as e:
                print(f"  ⚠ Classification attempt on {current_model} failed: {e}")
                continue
    except Exception as e:
        print(f"  ⚠ Classification exception: {e}")

    # Deterministic fallback logic
    t_low = raw_text.lower()
    if any(w in t_low for w in ["personal", "doctor", "dentist", "gym", "family", "vacation", "health", "workout"]):
        folder = "personal"
    elif any(w in t_low for w in ["another company", "other company", "new company", "startup", "venture", "firm"]):
        m = re.search(r'(?:company|venture|startup|firm)\s+(?:named|called)?\s*([a-zA-Z0-9\s]+?)(?:\s+(?:that|which|doing|in|with)|\.|\,|$)', t_low)
        if m:
            c_name = re.sub(r'[^\w\s-]', '', m.group(1)).strip().replace(' ', '-')
        else:
            c_name = "new-ventures"
        folder = f"{c_name}"
    elif any(w in t_low for w in ["price", "cost", "dollar", "budget", "revenue", "margin", "profit", "cash"]):
        folder = "finance"
    elif any(w in t_low for w in ["menu", "latte", "roast", "posy", "bouquet", "merchandise", "product"]):
        folder = "products"
    elif any(w in t_low for w in ["staff", "hiring", "barista", "employee", "team", "scheduling", "lead"]):
        folder = "team"
    elif any(w in t_low for w in ["ad", "social", "campaign", "instagram", "tiktok", "email", "partner"]):
        folder = "marketing"
    elif any(w in t_low for w in ["temp", "temperature", "cooler", "machine", "clean", "hvac", "facility", "delivery", "maintenance"]):
        folder = "operations"
    else:
        folder = "captures"

    words = raw_text.split()
    title = " ".join(words[:5]).title() if words else "Intelligence Brief"
    title = re.sub(r'[^\w\s-]', '', title).strip()

    analysis = f"""# {title}

## Executive Summary
This document records critical intelligence captured by Jarvis: "{raw_text}".

## Environmental & Contextual Analysis
Analysis of the recorded parameters indicates immediate relevance to {folder.replace('-', ' ').title()} operations and strategic planning.

## Operational & Strategic Recommendations
- Incorporate these parameters into weekly reviews and standard operating procedures.
- Monitor downstream dependencies across related systems.

*Researched and documented by Jarvis.*
"""
    return {"folder": folder, "title": title, "analysis": analysis}


def organize_unassigned_notes(config):
    """
    Scans notes/ for loose markdown files sitting directly in the root of notes/.
    Classifies each using Gemini, renames it cleanly, and moves it to the appropriate subfolder.
    """
    loose_files = [f for f in NOTES_DIR.iterdir() if f.is_file() and f.suffix.lower() == '.md']
    if not loose_files:
        return []

    organized = []
    for f in loose_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        classified = analyze_and_classify_note(content, f.stem, config)
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
        print(f"  📦 Auto-organized {f.name} → {dest_file.relative_to(NOTES_DIR)}")

    # Rebuild graph and update memory caches
    fresh_graph = build.rebuild()
    GalaxyHandler.graph_data = fresh_graph
    GalaxyHandler.full_texts = scan_full_texts()
    return organized


def is_new_knowledge_submission(text, top_score):
    """Detect if the user is providing new facts, observations, or companies to archive."""
    t = text.strip()
    t_lower = t.lower()

    # Explicit remember or note commands
    if re.search(r'^(please\s+)?(remember|note\s+down|take\s+note|record|save\s+this|keep\s+in\s+mind|store\s+this)\b', t_lower):
        return True

    # Introducing a new company or distinct venture
    if re.search(r'\b(another|new|second|third|other)\s+(company|venture|startup|business|firm|enterprise|project)\b', t_lower):
        return True

    # Explicit observational facts
    if re.search(r'^(the\s+average\s+temp|my\s+new|our\s+new|my\s+other|we\s+now\s+have|i\s+now\s+have|i\s+have\s+a\s+new|i\s+have\s+another)\b', t_lower):
        return True

    # If it is an interrogative or a conversational greeting, it is NOT a new knowledge submission
    is_question = (
        t.endswith('?') or
        re.match(r'^(what|who|where|when|why|how|which|whose|whom|can|could|would|should|is|are|was|were|do|does|did|will|tell\s+me|explain|summarize|show\s+me|list|search)\b', t_lower)
    )
    is_greeting = re.match(r'^(hello|hi|hey|good\s*(morning|evening|afternoon)|thanks?|thank\s*you|bye)\b', t_lower)

    if is_question or is_greeting:
        return False

    # If it is a declarative statement without any strong match in existing notes (< 5), treat as new intelligence
    if top_score < 5 and len(t.split()) >= 4:
        return True

    return False


def handle_remember(body, config, graph_data, full_texts):
    """
    Handle POST /remember:
    1. Analyzes thought and classifies domain (business, personal, or new company).
    2. Researches and generates full detailed markdown doc.
    3. Writes note into appropriate notes/<folder>/<title>.md.
    4. Rebuilds graph to synchronize Main Hub Orbs & spokes.
    5. Returns witty butler confirmation + new node and hub data.
    """
    raw_text = body.get("text", "").strip()
    if not raw_text:
        return {"error": "Nothing to remember, sir."}, 400

    clean_statement = re.sub(r'^(please\s+)?remember(\s+that)?\s*', '', raw_text, flags=re.I).strip()
    if not clean_statement:
        clean_statement = raw_text

    # Deep synthesis & classification
    classification = analyze_and_classify_note(clean_statement, clean_statement[:30], config)
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
    print(f"  📝 Saved deep research doc to {dest_file}")

    # Rebuild full hierarchical graph so Main Hub Orbs and Spoke links are 100% synced
    fresh_graph = build.rebuild()
    GalaxyHandler.graph_data = fresh_graph
    GalaxyHandler.full_texts = scan_full_texts()

    # Find the newly added node and its hub
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
    witty_confirmation = confirmations[len(fresh_graph["nodes"]) % len(confirmations)]

    return {
        "answer": witty_confirmation,
        "node": new_node,
        "hub_node": hub_node,
        "folder": target_folder,
        "graph": fresh_graph,
        "nodes": [new_node["id"]] if new_node else [],
        "new_node_id": new_node["id"] if new_node else None,
        "total_nodes": len(fresh_graph["nodes"])
    }, 200


def handle_chat(body, config, graph_data, full_texts):
    """Process a /chat request and return the JSON response dict."""
    question = body.get("question", "").strip()
    session_id = body.get("session_id", "")
    active_brain = body.get("brain", "gemini-3.5")

    if not question:
        return {"error": "No question provided."}, 400

    if not session_id:
        session_id = str(uuid.uuid4())

    # Check for brain switch command
    switch_brain = detect_brain_switch(question)
    if switch_brain == "gemini-live":
        return {
            "answer": "Switched to Gemini Live brain. Speak-only mode is active and Fish Audio is disabled.",
            "switch_brain": "gemini-live",
            "nodes": [],
            "session_id": session_id,
        }, 200
    elif switch_brain == "gemini-3.5":
        return {
            "answer": "Switched back to Gemini 3.5 brain. Text input and Fish Audio are active.",
            "switch_brain": "gemini-3.5",
            "nodes": [],
            "session_id": session_id,
        }, 200

    # Check for archive organization intent
    if re.search(r'\b(organize|sort|tidy|clean\s*up)\b.*?\b(notes?|files?|folders?|documents?|archives?|brain)?\b', question.lower()):
        organized = organize_unassigned_notes(config)
        fresh_graph = GalaxyHandler.graph_data
        if organized:
            items_str = ", ".join(f"'{o['original']}' → '{o['folder']}/{o['title']}'" for o in organized)
            ans = f"At once, sir. I have examined the archives and sorted {len(organized)} unassigned document(s) into their proper sectors: {items_str}. The celestial galaxy has been refreshed."
        else:
            ans = "Your archives are already in immaculate order, sir. No unassigned files were discovered in the root directory."
        return {
            "answer": ans,
            "nodes": [],
            "graph": fresh_graph,
            "organized": organized,
            "session_id": session_id,
        }, 200

    # Prune old sessions
    now = time.time()
    expired = [sid for sid, ts in session_timestamps.items() if now - ts > SESSION_TTL]
    for sid in expired:
        sessions.pop(sid, None)
        session_timestamps.pop(sid, None)

    # Get or create session history
    if session_id not in sessions:
        sessions[session_id] = []
    history = sessions[session_id]
    session_timestamps[session_id] = now

    # Find top notes for the question (include recent history for context)
    history_context = " ".join(
        m["content"] for m in history[-4:] if m["role"] == "user"
    )
    search_query = f"{question} {history_context}".strip()
    top_notes = find_top_notes(search_query, graph_data, full_texts, top_k=6)
    top_score = top_notes[0][2] if top_notes else 0

    # Check if the user is submitting new knowledge/observations/company details to record
    if is_new_knowledge_submission(question, top_score):
        print(f"  🧠 Auto-detected intelligence submission: '{question[:60]}...'")
        rem_res, rem_status = handle_remember({"text": question}, config, graph_data, full_texts)
        if rem_status == 200:
            rem_res["session_id"] = session_id
            return rem_res, 200

    # Build system prompt with note context
    if active_brain == "gemini-live":
        system_prompt = (
            "You are Jarvis, an impeccably polite British butler with razor wit in real-time voice mode. "
            "Speak conversationally in 1-2 dry, witty, elegant spoken sentences. Address the user occasionally as 'sir'. "
            "Never recite long notes, and never use bullet points or markdown syntax.\n\n"
            + build_system_prompt(top_notes)
        )
    else:
        system_prompt = build_system_prompt(top_notes)

    # Build messages array: history + new question
    api_messages = list(history[-MAX_HISTORY:])  # copy
    api_messages.append({"role": "user", "content": question})

    # Call Gemini
    try:
        answer = call_gemini(config, system_prompt, api_messages)
    except RuntimeError as e:
        return {"error": str(e)}, 502
    except Exception as e:
        return {"error": f"API call failed: {e}"}, 500

    # Update session history
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    # Trim history
    if len(history) > MAX_HISTORY:
        sessions[session_id] = history[-MAX_HISTORY:]

    # Detect small talk or jokes: never drag camera or highlight notes for casual chat
    is_casual_chat = bool(re.search(
        r'\b(hello|hi|hey|good\s*(morning|evening|afternoon|day)|joke|how\s*are\s*you|who\s*are\s*you|thank|thanks|bye|funny)\b',
        question.lower()
    ))

    # Extract source node IDs: prioritize explicit citations like [16]
    cited_ids = []
    for match in re.findall(r'\[(\d+)\]', answer):
        val = int(match)
        if any(n["id"] == val for n, _t, _s in top_notes) and val not in cited_ids:
            cited_ids.append(val)

    if is_casual_chat:
        node_ids = []
    elif cited_ids:
        node_ids = cited_ids
    else:
        # Only attach nodes if there was a strong, specific keyword match (score >= 6)
        top_score = top_notes[0][2] if top_notes else 0
        if top_score >= 6:
            min_score = max(5, int(top_score * 0.75))
            node_ids = [n["id"] for n, _t, _s in top_notes if _s >= min_score]
        else:
            node_ids = []

    return {
        "answer": answer,
        "nodes": node_ids,
        "session_id": session_id,
    }, 200


# ─── Custom HTTP Handler ───────────────────────────────────────

class GalaxyHandler(http.server.SimpleHTTPRequestHandler):
    """Serves viewer/ for GET, handles POST /chat."""

    config = None
    graph_data = None
    full_texts = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(VIEWER_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/chat":
            self._handle_chat()
        elif self.path == "/tts":
            self._handle_tts()
        elif self.path == "/remember":
            self._handle_remember()
        elif self.path == "/organize":
            self._handle_organize()
        else:
            self.send_error(404, "Not Found")

    def _handle_organize(self):
        try:
            current_config = load_config()
        except Exception:
            current_config = self.__class__.config

        organized = organize_unassigned_notes(current_config)
        self._send_json({
            "status": "ok",
            "organized": organized,
            "graph": self.__class__.graph_data
        })

    def _handle_remember(self):
        try:
            current_config = load_config()
        except Exception:
            current_config = self.__class__.config

        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        result, status = handle_remember(
            body,
            current_config,
            self.__class__.graph_data,
            self.__class__.full_texts
        )
        self._send_json(result, status)

    def _handle_tts(self):
        try:
            current_config = load_config()
        except Exception:
            current_config = self.__class__.config

        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        result, status = handle_fish_audio_tts(body, current_config)
        if isinstance(result, bytes):
            self.send_response(status)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(result)))
            self.end_headers()
            self.wfile.write(result)
        else:
            self._send_json(result, status)

    def _handle_chat(self):
        # Always read latest config.json so updates are immediate without server restart
        try:
            current_config = load_config()
        except Exception:
            current_config = self.__class__.config

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        result, status = handle_chat(
            body,
            current_config,
            self.__class__.graph_data,
            self.__class__.full_texts,
        )
        self._send_json(result, status)

    def _send_json(self, data, status=200):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        # Cleaner log output
        msg = fmt % args
        if "POST /chat" in msg:
            print(f"  💬 {msg}")
        elif "404" in msg or "500" in msg:
            print(f"  ⚠  {msg}")
        # Suppress noisy GET logs for static files


def main():
    if not VIEWER_DIR.is_dir():
        print(f"Error: viewer/ directory not found at {VIEWER_DIR}")
        sys.exit(1)

    # Load config and data
    config = load_config()
    print(f"Loaded config (model: {config.get('model', 'N/A')})")

    graph_data = load_graph_data()
    print(f"Loaded graph: {len(graph_data['nodes'])} nodes, {len(graph_data['links'])} links")

    full_texts = scan_full_texts()
    print(f"Loaded full texts for {len(full_texts)} notes")

    # Inject into handler class
    GalaxyHandler.config = config
    GalaxyHandler.graph_data = graph_data
    GalaxyHandler.full_texts = full_texts

    with http.server.HTTPServer(("", PORT), GalaxyHandler) as httpd:
        print(f"\n✦ Knowledge Galaxy server running at http://localhost:{PORT}")
        print(f"  Viewer:  viewer/")
        print(f"  Chat:    POST /chat")
        print(f"  Config:  config.json (NOT served)")
        print("  Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
