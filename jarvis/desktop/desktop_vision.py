"""
Capability 16: Full Desktop Vision Subsystem for J.A.R.V.I.S.
Provides multi-display geometry mapping, high-DPI scaling factor detection,
pixel color sampling, fullscreen/window/region capture, and visual change detection.
"""
import io
import time
import ctypes
from ctypes import wintypes
from PIL import Image, ImageGrab, ImageChops, ImageStat
from ..vision.capture import capture_screen
from .windows import get_screen_geometry, get_active_window

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
shcore = getattr(ctypes.windll, "shcore", None)


class DesktopVision:
    """Provides advanced desktop vision analysis and screen capture capabilities."""

    def __init__(self):
        self._last_capture = None
        self._last_capture_time = 0

    def get_dpi_scaling(self):
        """Returns monitor DPI scaling percentage (e.g. 100, 125, 150)."""
        try:
            hdc = user32.GetDC(0)
            LOGPIXELSX = 88
            dpi_x = gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            user32.ReleaseDC(0, hdc)
            scale = int((dpi_x / 96.0) * 100)
            return {"dpi": dpi_x, "scale_percent": scale}
        except Exception:
            return {"dpi": 96, "scale_percent": 100}

    def get_multi_monitor_layout(self):
        """Enumerates connected monitors with coordinates and bounding boxes."""
        monitors = []

        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HMONITOR,
            wintypes.HDC,
            ctypes.POINTER(wintypes.RECT),
            wintypes.LPARAM,
        )

        def enum_cb(hmonitor, hdc, lprect, lparam):
            r = lprect.contents
            monitors.append({
                "index": len(monitors) + 1,
                "x": r.left,
                "y": r.top,
                "width": r.right - r.left,
                "height": r.bottom - r.top,
                "is_primary": (r.left == 0 and r.top == 0),
            })
            return True

        cb = MONITORENUMPROC(enum_cb)
        user32.EnumDisplayMonitors(0, 0, cb, 0)
        if not monitors:
            geo = get_screen_geometry()
            monitors.append({
                "index": 1,
                "x": 0,
                "y": 0,
                "width": geo["primary"]["width"],
                "height": geo["primary"]["height"],
                "is_primary": True
            })
        return monitors

    def capture_fullscreen(self, save_path=None):
        """Captures full virtual desktop screen."""
        res = capture_screen(mode="fullscreen")
        self._last_capture_time = time.time()
        return {
            "status": "success",
            "width": res.get("width"),
            "height": res.get("height"),
            "file_path": res.get("file_path"),
            "base64": res.get("base64"),
            "timestamp": self._last_capture_time,
        }

    def capture_window(self, identifier=None, save_path=None):
        """Captures active or identified window."""
        res = capture_screen(mode="active_window")
        return {
            "status": "success",
            "width": res.get("width"),
            "height": res.get("height"),
            "file_path": res.get("file_path"),
            "base64": res.get("base64"),
            "window_title": res.get("window_title"),
        }

    def capture_screen_region(self, x, y, width, height, save_path=None):
        """Captures arbitrary bounding box on desktop."""
        res = capture_screen(mode="region", region=[int(x), int(y), int(width), int(height)])
        return {
            "status": "success",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "file_path": res.get("file_path"),
            "base64": res.get("base64"),
        }

    def sample_pixel_color(self, x, y):
        """Returns RGB hex and tuple of pixel color at coordinate (x, y)."""
        hdc = user32.GetDC(0)
        try:
            color_ref = gdi32.GetPixel(hdc, int(x), int(y))
            # COLORREF is 0x00BBGGRR
            r = color_ref & 0xFF
            g = (color_ref >> 8) & 0xFF
            b = (color_ref >> 16) & 0xFF
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            return {"status": "success", "x": x, "y": y, "rgb": (r, g, b), "hex": hex_code}
        finally:
            user32.ReleaseDC(0, hdc)

    def detect_visual_difference(self, img1, img2, tolerance=10):
        """
        Calculates percentage of changed pixels between two screenshots.
        Returns diff metrics and change percentage.
        """
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)
        diff = ImageChops.difference(img1.convert("RGB"), img2.convert("RGB"))
        stat = ImageStat.Stat(diff)
        rms = sum(stat.rms) / len(stat.rms)
        changed_percent = round(min(100.0, (rms / 255.0) * 100), 2)
        has_changed = changed_percent > tolerance
        return {
            "status": "success",
            "changed_percent": changed_percent,
            "has_changed": has_changed,
            "rms": round(rms, 2),
        }


desktop_vision = DesktopVision()
