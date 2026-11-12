"""
J.A.R.V.I.S. Unified System Launcher
Starts background server, verifies telemetry, and opens default browser to the Neural Galaxy UI.
Can be invoked via 'start jarvis' or 'jarvis' from any terminal, or on Windows boot.
"""
import os
import sys
import time
import socket
import subprocess
import webbrowser
import urllib.request

WORKSPACE = r"C:\Users\thenu\my-jarvis V2"
SERVER_PY = os.path.join(WORKSPACE, "server.py")
VIEWER_URL = "http://localhost:4719/"
API_URL = "http://localhost:4700/skills"

BANNER = r"""
  ══════════════════════════════════════════════════════════════════
       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗    ██████╗ ███████╗
       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝   ██╔═══██╗██╔════╝
       ██║███████║██████╔╝██║   ██║██║███████╗   ██║   ██║███████╗
  ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║   ██║   ██║╚════██║
  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║██╗╚██████╔╝███████║
   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚══════╝
       J.A.R.V.I.S. — AUTONOMOUS PERSONAL INTELLIGENCE SYSTEM
  ══════════════════════════════════════════════════════════════════
"""

def is_port_open(host="127.0.0.1", port=4700, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def main():
    print(BANNER)
    print(" [✦] Initializing J.A.R.V.I.S. OS Core Engines...")

    # Check if already running
    if not is_port_open("127.0.0.1", 4700) or not is_port_open("127.0.0.1", 4719):
        print(" [✦] Launching dual-threaded server (API :4700 | Viewer :4719)...")
        # Launch detached background process
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

        subprocess.Popen(
            [sys.executable, SERVER_PY],
            cwd=WORKSPACE,
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True
        )

        # Wait for ports to bind
        retries = 15
        while retries > 0:
            time.sleep(0.5)
            if is_port_open("127.0.0.1", 4700) and is_port_open("127.0.0.1", 4719):
                break
            retries -= 1

    # Verify API response
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "JARVIS-Launcher"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                print(" [✓] API Intelligence Core: ONLINE")
    except Exception as e:
        print(f" [!] Notice: API warming up ({e})")

    if is_port_open("127.0.0.1", 4719):
        print(f" [✓] Neural Galaxy 3D Interface: ONLINE at {VIEWER_URL}")
        print(" [✦] Opening primary visual interface in default browser...")
        webbrowser.open(VIEWER_URL)
        print(" [✓] J.A.R.V.I.S. is fully operational, sir. Standing by for voice commands.\n")
    else:
        print(" [✗] Error: Viewer port :4719 did not bind in time.")

if __name__ == "__main__":
    main()
