"""
Vercel Serverless Function Entry Point for J.A.R.V.I.S.
Handles Cloud AI Gateway, Knowledge Graph, Skills Registry, and Local Companion Bridge.
"""
import os
import sys
import json
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

# Add root directory to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from jarvis.config import load_config, load_user_profile
from jarvis.skills.registry import registry
from jarvis.core.gateway import call_gemini


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path.replace("/api", "")

        if path in ["/skills", "/skills/"]:
            skills = registry.get_all()
            self._send_json({"status": "success", "skills": skills, "total": len(skills)})
        elif path in ["/profile", "/profile/"]:
            profile = load_user_profile()
            self._send_json({"status": "success", "profile": profile})
        elif path in ["/health", "/health/"]:
            self._send_json({
                "status": "healthy",
                "service": "J.A.R.V.I.S. Cloud Gateway",
                "capabilities": 150,
                "environment": "Vercel Serverless"
            })
        else:
            self._send_json({"error": f"Endpoint '{path}' not found on Vercel API Gateway."}, 404)

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path.replace("/api", "")

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(raw_body.decode("utf-8"))
        except Exception:
            body = {}

        if path in ["/chat", "/chat/"]:
            question = body.get("question", body.get("message", "")).strip()
            brain = body.get("brain", "gemini-3.5")
            if not question:
                self._send_json({"error": "No question provided."}, 400)
                return

            q_lower = question.lower().strip()
            import re
            if re.search(r'\b(switch|change|set|turn\s*on|activate)\b.*?\b(gemini\s*live|live\s*mode|live\s*brain|live)\b', q_lower):
                self._send_json({
                    "answer": "Switching neural nexus to Gemini Live mode, sir. Voice streaming is active.",
                    "session_id": "vercel-session",
                    "nodes": [],
                    "switch_brain": "gemini-live",
                    "state": "IDLE"
                })
                return

            if re.search(r'\b(switch|change|set|turn\s*on|activate|back)\b.*?\b(gemini\s*3\.5|gemini\s*3|text\s*mode|text\s*brain|text)\b', q_lower):
                self._send_json({
                    "answer": "Returning to Gemini 3.5 text model, sir. Console and neural voice restored.",
                    "session_id": "vercel-session",
                    "nodes": [],
                    "switch_brain": "gemini-3.5",
                    "state": "IDLE"
                })
                return

            if brain == "gemini-live":
                sys_prompt = (
                    "You are J.A.R.V.I.S., an exceptionally capable, calm, witty, and impeccably refined British desktop AI assistant.\n"
                    "You are operating in real-time voice streaming mode (Gemini Live). Respond in ONE single, crisp, natural conversational sentence with British butler wit."
                )
            else:
                sys_prompt = (
                    "You are J.A.R.V.I.S., an exceptionally capable, calm, witty, and impeccably refined British desktop AI assistant.\n"
                    "Answer concisely in 1-2 razor-sharp, sophisticated sentences with British butler wit."
                )

            try:
                answer = call_gemini(sys_prompt, [{"role": "user", "content": question}])
            except Exception as e:
                answer = f"My neural gateway encountered an anomaly, sir: {e}"

            self._send_json({
                "answer": answer,
                "session_id": "vercel-session",
                "nodes": [],
                "state": "IDLE"
            })
        elif path in ["/tts", "/tts/"]:
            from jarvis.core.gateway import generate_fish_audio_tts
            text = body.get("text", "").strip()
            if not text:
                self._send_json({"error": "No text provided."}, 400)
                return
            result, status = generate_fish_audio_tts(text)
            if isinstance(result, bytes):
                self.send_response(status)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(result)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(result)
            else:
                self._send_json(result, status)
        elif path in ["/bridge", "/bridge/"]:
            # Companion bridge status
            companion_url = os.environ.get("JARVIS_COMPANION_URL", "http://localhost:4700")
            self._send_json({
                "status": "success",
                "companion_url": companion_url,
                "message": "Desktop automation requires local J.A.R.V.I.S. Windows companion."
            })
        else:
            self._send_json({"error": f"Endpoint '{path}' not supported."}, 404)

    def _send_json(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
