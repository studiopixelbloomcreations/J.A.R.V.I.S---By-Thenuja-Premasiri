"""
J.A.R.V.I.S. Native Windows Desktop Shell
Wraps the J.A.R.V.I.S. HUD into a transparent, always-on-top, draggable desktop overlay.
"""
import sys
import time
import threading
import webview
from jarvis.config import load_config


class DesktopApi:
    def __init__(self, window):
        self._window = window
        self.is_compact = False

    def toggle_compact_mode(self):
        """Switches between floating compact Orb and expanded command deck."""
        self.is_compact = not self.is_compact
        if self.is_compact:
            self._window.resize(360, 360)
        else:
            self._window.resize(1140, 780)
        return {"status": "success", "is_compact": self.is_compact}

    def minimize(self):
        self._window.minimize()

    def hide(self):
        self._window.hide()

    def show(self):
        self._window.show()

    def close(self):
        self._window.destroy()

    def set_always_on_top(self, on_top):
        self._window.on_top = bool(on_top)
        return {"status": "success", "on_top": self._window.on_top}


def launch_desktop_app(port=4700):
    """Initializes and runs the native Windows desktop overlay window."""
    url = f"http://localhost:{port}"

    window = webview.create_window(
        title="J.A.R.V.I.S. Desktop System",
        url=url,
        width=1140,
        height=780,
        resizable=True,
        frameless=True,
        easy_drag=True,
        on_top=True,
        background_color="#000000",
        transparent=True,
    )
    api = DesktopApi(window)
    window.expose(api.toggle_compact_mode, api.minimize, api.hide, api.show, api.close, api.set_always_on_top)

    print("✦ J.A.R.V.I.S. Desktop Overlay launching via WebView2...")
    webview.start(debug=False)


if __name__ == "__main__":
    cfg = load_config()
    launch_desktop_app(cfg.get("port", 4700))
