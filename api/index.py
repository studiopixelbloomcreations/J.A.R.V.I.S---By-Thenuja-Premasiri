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
            if not question:
                self._send_json({"error": "No question provided."}, 400)
                return

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
