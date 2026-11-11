#!/usr/bin/env python3
"""
J.A.R.V.I.S. Core Intelligence Server
Serves the holographic desktop HUD, provides perception and vision endpoints,
orchestrates multi-step automation, manages the 150-skill registry, and enforces safety permissions.
"""
import sys
import os
import json
import socket
import threading
import urllib.parse
import http.server
import pathlib

# Monkeypatch socket.getaddrinfo on Windows to prevent IPv6 DNS lookup hangs
_orig_getaddrinfo = socket.getaddrinfo


def _ipv4_first_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    try:
        res = _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        if res:
            return res
    except Exception:
        pass
    return _orig_getaddrinfo(host, port, family, type, proto, flags)


socket.getaddrinfo = _ipv4_first_getaddrinfo

# Ensure jarvis package is on sys.path
ROOT_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

import build
from jarvis.config import load_config, load_user_profile, VIEWER_DIR, SCREENSHOTS_DIR
from jarvis.core.permissions import broker
from jarvis.core.gateway import generate_fish_audio_tts, generate_gemini_live_audio
from jarvis.core.orchestrator import orchestrator
from jarvis.skills.registry import registry
from jarvis.skills.handlers import dispatch_skill
from jarvis.knowledge.graph import load_graph_data, scan_full_texts
from jarvis.vision.capture import capture_screen
from jarvis.vision.ocr import analyze_screen_image
from jarvis.vision.annotator import annotate_screenshot
from jarvis.desktop.windows import list_windows

PORT = 4700


class JarvisHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(VIEWER_DIR), **kwargs)

    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path

        if path == "/skills":
            self._send_json({"status": "success", "skills": registry.get_all(), "total": len(registry.get_all())})
        elif path == "/approvals":
            self._send_json({"status": "success", "approvals": broker.get_pending_approvals()})
        elif path == "/audit":
            self._send_json({"status": "success", "audit": broker.get_audit_log(60)})
        elif path == "/diagnostics":
            res = dispatch_skill("sys_diagnostic_report", {})
            self._send_json(res)
        elif path == "/windows":
            res = dispatch_skill("desk_list_windows", {})
            self._send_json(res)
        elif path == "/profile":
            self._send_json({"status": "success", "profile": load_user_profile()})
        elif path == "/vision/capture":
            res = capture_screen(mode="fullscreen")
            self._send_json({"status": "success", "capture": res})
        elif path.startswith("/screenshots/"):
            # Serve captured screenshots
            fname = path.replace("/screenshots/", "")
            fpath = SCREENSHOTS_DIR / fname
            if fpath.exists():
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg" if fname.endswith(".jpg") else "image/png")
                self.send_header("Content-Length", str(fpath.stat().st_size))
                self.end_headers()
                self.wfile.write(fpath.read_bytes())
            else:
                self.send_error(404, "Screenshot not found")
        else:
            # Serve static files from viewer/
            super().do_GET()

    def do_POST(self):
        path = self.path

        if path == "/chat":
            self._handle_chat()
        elif path == "/tts":
            self._handle_tts()
        elif path == "/remember":
            self._handle_remember()
        elif path == "/ambient_learn":
            self._handle_ambient_learn()
        elif path == "/organize":
            self._handle_organize()
        elif path == "/stop":
            body = self._read_json()
            if body.get("action") == "resume" or body.get("resume"):
                res = broker.reset_emergency_stop()
            else:
                res = broker.trigger_emergency_stop()
            self._send_json(res)
        elif path == "/resume":
            res = broker.reset_emergency_stop()
            self._send_json(res)
        elif path == "/pause":
            body = self._read_json()
            paused = body.get("paused")
            res = broker.toggle_pause(paused)
            if not res.get("paused"):
                broker.reset_emergency_stop()
            self._send_json(res)
        elif path == "/approvals/resolve":
            body = self._read_json()
            res = broker.resolve_approval(body.get("approval_id"), body.get("approved", True))
            self._send_json(res)
        elif path == "/skills/toggle":
            body = self._read_json()
            ok = registry.set_enabled(body.get("skill_id"), body.get("enabled", True))
            self._send_json({"status": "success" if ok else "error", "skill_id": body.get("skill_id")})
        elif path == "/skills/execute":
            body = self._read_json()
            res = dispatch_skill(body.get("skill_id"), body.get("params", {}))
            self._send_json(res)
        elif path == "/vision/capture":
            body = self._read_json()
            res = capture_screen(mode=body.get("mode", "fullscreen"), region=body.get("region"))
            self._send_json(res)
        elif path == "/vision/analyze":
            body = self._read_json()
            res = analyze_screen_image(body.get("image", ""), body.get("prompt", "Analyze this screen."))
            self._send_json(res)
        elif path == "/vision/annotate":
            body = self._read_json()
            res = annotate_screenshot(body.get("source_path"), body.get("annotations", []))
            self._send_json(res)
        else:
            self.send_error(404, "Endpoint Not Found")

    def _read_json(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(content_length)
            return json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            return {}

    def _handle_chat(self):
        body = self._read_json()
        question = body.get("question", body.get("message", "")).strip()
        session_id = body.get("session_id", "")
        active_brain = body.get("brain", body.get("model", "gemini-3.5"))

        if not question:
            self._send_json({"error": "No question provided."}, 400)
            return

        result = orchestrator.process_request(question, session_id, active_brain)
        self._send_json(result)

    def _handle_remember(self):
        body = self._read_json()
        raw_text = body.get("text", "").strip()
        if not raw_text:
            self._send_json({"error": "Nothing to remember, sir."}, 400)
            return

        from server_legacy_remember import handle_remember_synthesis
        res, status = handle_remember_synthesis(raw_text)
        self._send_json(res, status)

    def _handle_ambient_learn(self):
        body = self._read_json()
        raw_text = body.get("text", "").strip()
        if not raw_text or len(raw_text.split()) < 3:
            self._send_json({"learned": False, "reason": "Insufficient speech."}, 200)
            return

        from server_legacy_remember import handle_ambient_learn
        res, status = handle_ambient_learn(raw_text)
        self._send_json(res, status)

    def _handle_organize(self):
        from server_legacy_remember import organize_unassigned_notes
        organized = organize_unassigned_notes()
        fresh = load_graph_data()
        self._send_json({"status": "ok", "organized": organized, "graph": fresh})

    def _handle_tts(self):
        body = self._read_json()
        text = body.get("text", "").strip()
        brain = body.get("brain", "gemini-3.5")
        if not text:
            self._send_json({"error": "No text provided"}, 400)
            return

        if brain == "gemini-live":
            # Gemini Live uses Google's Charon voice
            result, status = generate_gemini_live_audio(text)
            content_type = "audio/wav"
        else:
            # Gemini 3.5 uses Fish Audio British butler voice
            result, status = generate_fish_audio_tts(text)
            content_type = "audio/mpeg"

        if isinstance(result, bytes):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(result)))
            self.end_headers()
            self.wfile.write(result)
        else:
            self._send_json(result, status)

    def _send_json(self, data, status=200):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        # Cleaner log output
        msg = fmt % args
        if any(p in msg for p in ["POST /chat", "POST /vision", "POST /skills"]):
            print(f"  ⚡ {msg}")
        elif "404" in msg or "500" in msg:
            print(f"  ⚠  {msg}")


def run_http_server(port):
    try:
        with http.server.HTTPServer(("", port), JarvisHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"Port {port} server stopped: {e}")


def main():
    cfg = load_config()
    print(f"\n=======================================================")
    print(f"✦ J.A.R.V.I.S. INTELLIGENCE SYSTEM — ONLINE")
    print(f"  Model: {cfg.get('model')} | Primary Port: {PORT}")
    print(f"  Skills: {len(registry.get_all())} registered")
    print(f"  Dual Localhost URLs: http://localhost:{PORT} and http://localhost:4719")
    print(f"=======================================================\n")

    # Start mirror listener on 4719 so whichever port user has open in browser responds
    if PORT != 4719:
        t = threading.Thread(target=run_http_server, args=(4719,), daemon=True)
        t.start()

    run_http_server(PORT)


if __name__ == "__main__":
    main()
