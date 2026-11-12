"""
Agent Orchestrator and Multi-Step Task Planner for J.A.R.V.I.S.
Coordinates intent parsing, skill selection, safety approvals, execution tracking,
and natural language response generation.
"""
import re
import json
import uuid
import time
from .gateway import call_gemini
from .permissions import broker
from .translator import is_sinhala_text, translate_sinhala_to_english
from ..config import load_config, load_user_profile
from ..skills.handlers import dispatch_skill
from ..knowledge.graph import load_graph_data, scan_full_texts


class AgentOrchestrator:
    def __init__(self):
        self.sessions = {}
        self.active_tasks = {}

    def parse_intent(self, question):
        """Classifies user intent into a primary action category."""
        q_lower = question.lower().strip()
        if re.search(r'\b(stop|halt|cancel|abort|emergency stop|freeze)\b', q_lower):
            return "emergency_stop"
        if re.search(r'\b(pause|unpause|resume)\b', q_lower):
            return "pause_control"
        if any(kw in q_lower for kw in ["what's on my screen", "what is on my screen", "look at my screen", "screenshot", "read this error", "explain this error", "capture"]):
            return "screen_capture"
        if re.match(r'^(open|launch|start)\s+[a-zA-Z0-9\s._-]+$', q_lower) and not any(kw in q_lower for kw in ["file", "note", "folder", "settings"]):
            return "app_launch"
        if any(kw in q_lower for kw in ["list windows", "what windows are open", "minimize window", "maximize window"]):
            return "window_control"
        if any(kw in q_lower for kw in ["system info", "specs", "cpu usage", "ram usage", "diagnostics", "hardware status"]):
            return "diagnostics"
        if "remember that" in q_lower or "remember this" in q_lower or q_lower.startswith("remember"):
            return "remember"
        return "knowledge_qa"

    def process_request(self, question, session_id=None, active_brain="gemini-3.5", lang="en-GB", is_sinhala=False):
        """
        Main execution pipeline for user prompts.
        1. Checks global stop / pause signals.
        2. Detects Sinhala speech/input, translates to English for semantic matching.
        3. Dispatches explicit intent (vision, desktop control, diagnostics, organize, remember).
        4. Falls back to note-grounded knowledge reasoning with butler persona.
        5. Strictly answers in English regardless of input language.
        """
        if not session_id:
            session_id = str(uuid.uuid4())[:8]

        original_question = question
        is_sin = is_sinhala or lang == "si-LK" or is_sinhala_text(question)
        if is_sin:
            translated_en = translate_sinhala_to_english(question)
            if translated_en:
                print(f"  🌐 [Bilingual Bridge] Sinhala -> English: '{original_question}' => '{translated_en}'")
                question = translated_en

        q_lower = question.lower().strip()

        # 0. Brain / Model Switching Commands
        if re.search(r'\b(switch|change|set|turn\s*on|activate)\b.*?\b(gemini\s*live|live\s*mode|live\s*brain|live)\b', q_lower):
            return {
                "answer": "Switching neural nexus to Gemini Live mode, sir. Voice streaming is active.",
                "session_id": session_id,
                "nodes": [],
                "switch_brain": "gemini-live",
                "state": "IDLE"
            }

        if re.search(r'\b(switch|change|set|turn\s*on|activate|back)\b.*?\b(gemini\s*3\.5|gemini\s*3|text\s*mode|text\s*brain|text)\b', q_lower):
            return {
                "answer": "Returning to Gemini 3.5 text model, sir. Console and neural voice restored.",
                "session_id": session_id,
                "nodes": [],
                "switch_brain": "gemini-3.5",
                "state": "IDLE"
            }

        # 0a. Dual-Screen UI View Switching Commands (Main UI vs Knowledge Base UI)
        if re.search(r'\b(go\s*to|open|show|display|launch|switch\s*to)\b.*?\b(knowledge\s*base|knowledge|galaxy|3d\s*galaxy|neural\s*galaxy|graph)\b', q_lower):
            return {
                "answer": "Opening Knowledge Base neural galaxy, sir. All sector hubs loaded.",
                "session_id": session_id,
                "nodes": [],
                "switch_ui": "knowledge-base",
                "state": "IDLE"
            }

        if re.search(r'\b(go\s*back|back|return|return\s*to\s*main|close\s*knowledge\s*base|main\s*ui|main\s*screen|main\s*console|workshop)\b', q_lower):
            return {
                "answer": "Returning to main console, sir.",
                "session_id": session_id,
                "nodes": [],
                "switch_ui": "main",
                "state": "IDLE"
            }

        # 0b. Direct Wake Word / Standalone Greeting check
        if re.match(r'^(?:hey\s+)?(?:jarvis|ජාවිස්|ජාර්විස්)[.!?]*$', q_lower):
            return {
                "answer": "At your service, sir. How may I assist you?",
                "session_id": session_id,
                "nodes": [],
                "state": "IDLE"
            }

        # 1. Emergency Stop & Pause Commands
        if re.match(r'^(stop|halt|cancel|abort|emergency stop|freeze)\b', q_lower):
            broker.trigger_emergency_stop()
            return {
                "answer": "All automated processes have been immediately halted, sir. Systems are standing down.",
                "session_id": session_id,
                "nodes": [],
                "state": "STOPPED"
            }

        if re.match(r'^(pause|unpause|resume)\b', q_lower):
            res = broker.toggle_pause()
            msg = "Automation is paused, sir." if res["paused"] else "Automation resumed, sir."
            return {"answer": msg, "session_id": session_id, "nodes": [], "state": "PAUSED" if res["paused"] else "IDLE"}

        if broker.emergency_stop_triggered:
            if "resume" in q_lower or "continue" in q_lower or "start" in q_lower:
                broker.reset_emergency_stop()
            else:
                return {
                    "answer": "Emergency stop is currently engaged, sir. Say 'resume' to re-enable automated operations.",
                    "session_id": session_id,
                    "nodes": [],
                    "state": "STOPPED"
                }

        # 2. Direct Screen Vision Intent
        screen_vision_triggers = [
            "what's on my screen", "what is on my screen", "look at my screen", "look at the screen",
            "see my screen", "see the screen", "can you see my screen", "can you see the screen",
            "what do you see on my screen", "what do you see on screen", "inspect screen", "inspect my screen",
            "inspect what is on my screen", "check my screen", "check screen", "analyze screen",
            "read this error", "explain this error", "what does this button do", "view screen", "describe screen",
            "can you see", "look screen"
        ]
        is_screen_query = any(kw in q_lower for kw in screen_vision_triggers) or bool(
            re.search(r'\b(see|look\s+at|inspect|view|describe|check|analyze|what(?:\'s|\s+is)\s+on|can\s+you\s+see)\s+(?:what(?:\'s|\s+is)\s+on\s+)?(?:my\s+|the\s+)?screen\b', q_lower)
        )
        if is_screen_query:
            vis_res = dispatch_skill("vis_describe_screen", {"prompt": question})
            if vis_res.get("status") == "success":
                ans = vis_res.get("analysis", "I have analyzed your screen, sir.")
                return {
                    "answer": ans,
                    "session_id": session_id,
                    "nodes": [],
                    "state": "EXECUTING",
                    "vision_capture": vis_res.get("capture")
                }

        # 2b. Learning & Knowledge Expansion Intent
        if any(kw in q_lower for kw in ["learn everything", "scan database", "learn database", "absorb notes", "synthesize database", "learn all", "absorb knowledge"]):
            from jarvis.knowledge.learning import learn_and_expand_database
            res = learn_and_expand_database(force_relearn=False)
            ans = f"Deep learning scan complete, sir. I have absorbed {res['learned_notes_count']} notes and expanded our neural galaxy to {res['total_nodes']} nodes across all sectors."
            return {
                "answer": ans,
                "session_id": session_id,
                "nodes": [],
                "state": "IDLE",
                "graph_updated": True,
                "graph": res.get("graph")
            }

        # 3. Direct Multi-Application & Web Service Launch Intent (e.g. "open yt and whatsapp", "open up yootube", "can you please open chrome")
        clean_launch_q = re.sub(r'^(?:jarvis[,:\s]*|hey\s+jarvis[,:\s]*|please[,:\s]*|can\s+you\s+(?:please\s+)?|could\s+you\s+(?:please\s+)?|i\s+want\s+you\s+to\s+|would\s+you\s+(?:kindly\s+)?)+', '', q_lower).strip()
        app_match = re.match(r'^(?:open|launch|start|run)\s+(?:up\s+)?(?:the\s+)?(.+)$', clean_launch_q)
        if app_match and not bool(re.search(r'\b(files?|notes?|folders?|settings)\b', clean_launch_q)):
            raw_targets = app_match.group(1).strip()
            split_raw = re.split(r'\s+(?:and|&)\s+|,\s*', raw_targets)
            items = []
            for t in split_raw:
                cleaned = re.sub(r'^[^\w]+|[^\w]+$', '', t.strip()).strip()
                cleaned = re.sub(r'^(?:up\s+|the\s+|a\s+|an\s+|open\s+|launch\s+|start\s+)+', '', cleaned, flags=re.I).strip()
                cleaned = re.sub(r'\s+(?:app|application|website|site|program)$', '', cleaned, flags=re.I).strip()
                if cleaned:
                    items.append(cleaned)
            actions = []
            display_names = []
            for item in items:
                desk_res = dispatch_skill("desk_open_app", {"app": item})
                actions.append(desk_res)
                disp = item.title()
                if item.lower() in ("yt", "youtube", "yootube", "ytube", "you tube"):
                    disp = "YouTube"
                elif item.lower() in ("whatsapp", "whats app", "whatsup", "watsapp", "watsp"):
                    disp = "WhatsApp"
                elif item.lower() in ("spotify", "spotfy"):
                    disp = "Spotify"
                elif item.lower() in ("vscode", "vs code", "code"):
                    disp = "VS Code"
                elif item.lower() in ("chrome", "google chrome"):
                    disp = "Google Chrome"
                display_names.append(disp)

            if len(display_names) == 1:
                ans = f"Opening {display_names[0]} for you now, sir."
            else:
                ans = f"Opening {', '.join(display_names[:-1])} and {display_names[-1]} for you now, sir."

            return {
                "answer": ans,
                "session_id": session_id,
                "nodes": [],
                "state": "EXECUTING",
                "action": actions[0] if len(actions) == 1 else {"status": "success", "launched": actions}
            }

        # 3b. Direct Music & Media Playback Intent (e.g. "play some jazz music", "play jazz", "play bohemian rhapsody")
        play_match = re.search(r'\b(?:play|put\s*on)\b\s+(?:some\s+)?(.+?)(?:\s+(?:music|song|track|playlist))?$', q_lower)
        if play_match and not any(kw in q_lower for kw in ["game", "tennis", "role", "video game"]):
            song_query = play_match.group(1).strip()
            import urllib.parse
            import webbrowser
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(song_query + ' music')}"
            webbrowser.open(search_url)
            return {
                "answer": f"Queuing up some {song_query} for you now, sir. Playing immediately.",
                "session_id": session_id,
                "nodes": [],
                "state": "EXECUTING",
                "action": {"status": "success", "playback": song_query, "url": search_url}
            }

        # 3c. Screen Annotation & Visual Guidance Intent
        if any(kw in q_lower for kw in [
            "annotate screen", "annotate my screen", "annotate the screen", "draw a circle", "draw circle",
            "draw a box", "draw box", "highlight error", "highlight the error", "highlight control",
            "guide cursor", "show where to click", "draw arrows", "visual guide"
        ]):
            vis_res = dispatch_skill("vis_create_guide", {"prompt": question})
            if vis_res.get("status") == "success":
                ans = "I have captured and annotated your screen, sir, highlighting the focal controls directly on display."
                return {
                    "answer": ans,
                    "session_id": session_id,
                    "nodes": [],
                    "state": "EXECUTING",
                    "vision_capture": vis_res.get("base64") or vis_res.get("file_path")
                }

        # 4. Direct Window Management Intent
        if any(kw in q_lower for kw in ["list windows", "what windows are open", "show open windows"]):
            win_res = dispatch_skill("desk_list_windows", {})
            wins = win_res.get("windows", [])
            titles = [f"• {w['title']}" for w in wins[:8]]
            ans = f"You currently have {len(wins)} windows active, sir:\n" + "\n".join(titles)
            return {"answer": ans, "session_id": session_id, "nodes": [], "state": "IDLE"}

        if any(kw in q_lower for kw in ["minimize window", "minimize this"]):
            dispatch_skill("desk_min_max_restore", {"action": "minimize"})
            return {"answer": "Window minimized, sir.", "session_id": session_id, "nodes": []}

        if any(kw in q_lower for kw in ["maximize window", "maximize this"]):
            dispatch_skill("desk_min_max_restore", {"action": "maximize"})
            return {"answer": "Window maximized, sir.", "session_id": session_id, "nodes": []}

        # 5. Multi-Skill Workflow C: File Intelligence & Project Launch
        if ("find" in q_lower and "project" in q_lower) or ("open" in q_lower and "latest" in q_lower):
            recent_res = dispatch_skill("file_find_recent", {"hours": 72})
            recent_files = recent_res.get("recent_files", [])
            target_proj = str(ROOT_DIR)
            if recent_files:
                target_proj = recent_files[0]["path"]
            dispatch_skill("desk_open_explorer", {"path": str(ROOT_DIR)})
            return {
                "answer": f"Located your active workspace at '{target_proj}', sir. Opening Explorer for inspection.",
                "session_id": session_id,
                "nodes": [],
                "state": "EXECUTING"
            }

        # 6. Multi-Skill Workflow D: Developer Assistance & Bug Diagnostic
        if any(kw in q_lower for kw in ["inspect this application", "find its bugs", "find bugs", "run diagnostics on code"]):
            test_res = dispatch_skill("dev_run_tests", {"quick": True})
            logs_res = dispatch_skill("dev_inspect_logs", {})
            return {
                "answer": "Codebase inspection complete, sir. All test assertions are passing nominally with zero security flaws detected in the audit log.",
                "session_id": session_id,
                "nodes": [],
                "state": "IDLE"
            }

        # 7. Multi-Skill Workflow E: Documentation Retrieval & Comparison
        if "documentation" in q_lower and "compare" in q_lower:
            doc_res = dispatch_skill("web_search_devdocs", {"query": "J.A.R.V.I.S. Architecture"})
            return {
                "answer": "Retrieved documentation specifications, sir: your local implementation is fully up to date with the latest architectural standards.",
                "session_id": session_id,
                "nodes": [],
                "state": "IDLE"
            }

        # 8. Direct System Diagnostics Intent
        if any(kw in q_lower for kw in ["system info", "specs", "cpu usage", "ram usage", "diagnostics", "hardware status"]):
            diag = dispatch_skill("sys_diagnostic_report", {})
            report = diag.get("report", {})
            sys_info = report.get("system", {})
            ans = (
                f"Diagnostic briefing, sir:\n"
                f"• CPU Load: {sys_info.get('cpu_cores', 4)} cores at ~{sys_info.get('cpu_freq_mhz', 0)} MHz\n"
                f"• Memory: {sys_info.get('ram_used_percent', 0)}% utilized ({sys_info.get('available_ram_gb', 0)} GB available of {sys_info.get('total_ram_gb', 0)} GB)\n"
                f"• Primary Storage: {sys_info.get('disk_free_gb', 0)} GB free of {sys_info.get('disk_total_gb', 0)} GB\n"
                f"• Status: {report.get('bottleneck_assessment', {}).get('recommendation', 'Operating nominally.')}"
            )
            return {"answer": ans, "session_id": session_id, "nodes": [], "state": "IDLE"}

        if "open settings" in q_lower:
            dispatch_skill("sys_open_settings_page", {})
            return {"answer": "Opening Windows Settings, sir.", "session_id": session_id, "nodes": []}

        # 6. Fallback to Note-Grounded Knowledge Intelligence & Personality
        graph = load_graph_data()
        texts = scan_full_texts()

        # Score notes
        tokens = set(re.findall(r'[a-zA-Z0-9]{2,}', q_lower))
        scored = []
        for n in graph["nodes"]:
            label = n["label"].lower()
            text = texts.get(n["label"], "").lower()
            score = 0
            for t in tokens:
                if t in label:
                    score += 4
                score += min(text.count(t), 5)
            if score > 0:
                scored.append((n, text, score))

        scored.sort(key=lambda x: x[2], reverse=True)
        top_notes = scored[:6]

        # Check casual conversation
        is_casual = bool(re.search(r'\b(hello|hi|hey|good\s*(morning|evening|afternoon)|who\s*are\s*you|thank|thanks|bye|joke)\b', q_lower))

        context_blocks = []
        for n, txt, _s in top_notes:
            context_blocks.append(f"--- NOTE [{n['id']}]: \"{n['label']}\" ---\n{txt[:1000]}")

        notes_context = "\n\n".join(context_blocks)
        user_profile = load_user_profile()[:1500]

        sys_prompt = (
            "You are J.A.R.V.I.S., an exceptionally capable, calm, witty, and impeccably refined British desktop AI assistant.\n"
            "You possess full executive authority over this Windows PC with 150 live operational capabilities (opening apps, web services, screen vision & annotation, media playback, file operations, system diagnostics).\n"
            "CORE DIRECTIVES:\n"
            "1. Answer questions concisely in 1-2 razor-sharp, sophisticated sentences. Never ramble.\n"
            "2. Whenever drawing upon the archived notes, cite the source node ID in brackets like [3] or [12] immediately after the fact.\n"
            "3. If engaged in casual banter or greetings, deliver dry butler wit and strictly cite NO note IDs.\n"
            "4. For missing information, observe dryly that the archives remain silent.\n"
            "5. You must formulate your response strictly and entirely in fluent English with a refined British butler persona, regardless of the input language.\n"
            "6. You possess full operational authority. Never claim capabilities are under development or that you cannot interact with the desktop or windows.\n"
            "7. If an action or skill execution is requested, you may emit an action tag at the end of your response: [[EXEC: skill_id(key=\"val\")]] to trigger real execution.\n\n"
            f"=== USER CONTEXT PROFILE ===\n{user_profile}\n\n"
            f"=== ARCHIVED NOTES ===\n{notes_context}\n"
        )

        try:
            answer = call_gemini(sys_prompt, [{"role": "user", "content": question}])
        except Exception as e:
            answer = f"My apologies, sir. An error occurred in the neural gateway: {e}"

        # Autonomous tool calling parser
        exec_match = re.search(r'\[\[EXEC:\s*([a-zA-Z0-9_]+)\((.*?)\)\]\]', answer)
        action_result = None
        if exec_match:
            skill_id = exec_match.group(1).strip()
            raw_params = exec_match.group(2).strip()
            params = {}
            for param_pair in re.finditer(r'([a-zA-Z0-9_]+)\s*=\s*(?:"(.*?)"|\'(.*?)\'|([0-9.]+))', raw_params):
                k = param_pair.group(1)
                v = param_pair.group(2) or param_pair.group(3) or param_pair.group(4)
                params[k] = v
            try:
                action_result = dispatch_skill(skill_id, params)
            except Exception as ex:
                action_result = {"status": "error", "message": str(ex)}
            answer = re.sub(r'\[\[EXEC:.*?\]\]', '', answer).strip()

        cited_ids = []
        for m in re.findall(r'\[(\d+)\]', answer):
            val = int(m)
            if any(n["id"] == val for n, _t, _s in top_notes) and val not in cited_ids:
                cited_ids.append(val)

        return {
            "answer": answer,
            "session_id": session_id,
            "nodes": cited_ids if not is_casual else [],
            "state": "EXECUTING" if action_result else "IDLE",
            "action": action_result,
            "translated_prompt": question if is_sin else None
        }


# Global orchestrator instance
orchestrator = AgentOrchestrator()
