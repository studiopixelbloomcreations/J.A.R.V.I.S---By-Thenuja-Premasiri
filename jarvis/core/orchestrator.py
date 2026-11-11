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

    def process_request(self, question, session_id=None, active_brain="gemini-3.5"):
        """
        Main execution pipeline for user prompts.
        1. Checks global stop / pause signals.
        2. Dispatches explicit intent (vision, desktop control, diagnostics, organize, remember).
        3. Falls back to note-grounded knowledge reasoning with butler persona.
        """
        if not session_id:
            session_id = str(uuid.uuid4())[:8]

        q_lower = question.lower().strip()

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
        if any(kw in q_lower for kw in ["what's on my screen", "what is on my screen", "look at my screen", "read this error", "explain this error", "what does this button do"]):
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

        # 3. Direct Application Launch Intent
        app_match = re.match(r'^(open|launch|start)\s+([a-zA-Z0-9\s._-]+)$', q_lower)
        if app_match and not any(kw in q_lower for kw in ["file", "note", "folder", "settings"]):
            target_app = app_match.group(2).strip()
            # Normalize common apps
            app_map = {
                "chrome": "chrome",
                "notepad": "notepad",
                "calculator": "calc",
                "calc": "calc",
                "explorer": "explorer",
                "cmd": "cmd",
                "powershell": "powershell",
                "task manager": "taskmgr",
                "vs code": "code",
                "vscode": "code"
            }
            exec_target = app_map.get(target_app.lower(), target_app)
            desk_res = dispatch_skill("desk_open_app", {"app": exec_target})
            if desk_res.get("status") == "success":
                return {
                    "answer": f"Launching {target_app.title()} for you now, sir.",
                    "session_id": session_id,
                    "nodes": [],
                    "state": "EXECUTING",
                    "action": desk_res
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

        # 5. Direct System Diagnostics Intent
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
            "CORE DIRECTIVES:\n"
            "1. Answer questions concisely in 1-2 razor-sharp, sophisticated sentences. Never ramble.\n"
            "2. Whenever drawing upon the archived notes, cite the source node ID in brackets like [3] or [12] immediately after the fact.\n"
            "3. If engaged in casual banter or greetings, deliver dry butler wit and strictly cite NO note IDs.\n"
            "4. For missing information, observe dryly that the archives remain silent.\n\n"
            f"=== USER CONTEXT PROFILE ===\n{user_profile}\n\n"
            f"=== ARCHIVED NOTES ===\n{notes_context}\n"
        )

        try:
            answer = call_gemini(sys_prompt, [{"role": "user", "content": question}])
        except Exception as e:
            answer = f"My apologies, sir. An error occurred in the neural gateway: {e}"

        cited_ids = []
        for m in re.findall(r'\[(\d+)\]', answer):
            val = int(m)
            if any(n["id"] == val for n, _t, _s in top_notes) and val not in cited_ids:
                cited_ids.append(val)

        return {
            "answer": answer,
            "session_id": session_id,
            "nodes": cited_ids if not is_casual else [],
            "state": "IDLE"
        }


# Global orchestrator instance
orchestrator = AgentOrchestrator()
