"""
Window and Application Management Engine for J.A.R.V.I.S.
Provides window enumeration, focusing, minimizing, maximizing, positioning,
application launching, and running process diagnostics.
"""
import os
import re
import time
import subprocess
import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32

SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2
SW_MAXIMIZE = 3
SW_RESTORE = 9
WM_CLOSE = 0x0010


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def list_windows():
    """Lists all visible top-level desktop windows with titles and geometry."""
    windows = []
    fg_hwnd = user32.GetForegroundWindow()

    def enum_cb(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True

        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value.strip()

        # Skip tooltips, empty titles, or hidden utility shells
        if not title or title in ["Program Manager", "Settings", "Default IME", "MSCTFIME UI"]:
            return True

        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top

        if w > 80 and h > 80:
            windows.append({
                "hwnd": hwnd,
                "title": title,
                "x": rect.left,
                "y": rect.top,
                "width": w,
                "height": h,
                "is_active": (hwnd == fg_hwnd)
            })
        return True

    cb = WNDENUMPROC(enum_cb)
    user32.EnumWindows(cb, 0)
    return windows


def get_active_window():
    """Returns metadata for the currently active foreground window."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    title = buff.value.strip()
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return {
        "hwnd": hwnd,
        "title": title,
        "x": rect.left,
        "y": rect.top,
        "width": rect.right - rect.left,
        "height": rect.bottom - rect.top,
    }


def get_system_diagnostics():
    """Compiles hardware, OS metrics, and running process telemetry."""
    from ..skills.handlers import h_sys_info
    info = h_sys_info({})
    info["top_memory_processes"] = list_running_processes(limit=8)
    return info


def find_window(identifier):
    """Finds window by hwnd int or partial case-insensitive title match."""
    if isinstance(identifier, int):
        return identifier if user32.IsWindow(identifier) else None

    target = str(identifier).lower().strip()
    windows = list_windows()
    # Exact match first
    for w in windows:
        if w["title"].lower() == target:
            return w["hwnd"]
    # Partial match
    for w in windows:
        if target in w["title"].lower():
            return w["hwnd"]
    return None


def focus_window(identifier):
    """Brings the target window to foreground and restores it if minimized."""
    hwnd = find_window(identifier)
    if not hwnd:
        return {"status": "error", "message": f"Window not found: {identifier}"}

    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    return {"status": "success", "action": "focus", "hwnd": hwnd}


def minimize_window(identifier):
    hwnd = find_window(identifier)
    if not hwnd:
        return {"status": "error", "message": f"Window not found: {identifier}"}
    user32.ShowWindow(hwnd, SW_SHOWMINIMIZED)
    return {"status": "success", "action": "minimize", "hwnd": hwnd}


def maximize_window(identifier):
    hwnd = find_window(identifier)
    if not hwnd:
        return {"status": "error", "message": f"Window not found: {identifier}"}
    user32.ShowWindow(hwnd, SW_MAXIMIZE)
    return {"status": "success", "action": "maximize", "hwnd": hwnd}


def restore_window(identifier):
    hwnd = find_window(identifier)
    if not hwnd:
        return {"status": "error", "message": f"Window not found: {identifier}"}
    user32.ShowWindow(hwnd, SW_RESTORE)
    return {"status": "success", "action": "restore", "hwnd": hwnd}


def close_window(identifier):
    hwnd = find_window(identifier)
    if not hwnd:
        return {"status": "error", "message": f"Window not found: {identifier}"}
    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    return {"status": "success", "action": "close", "hwnd": hwnd}


def move_resize_window(identifier, x, y, width, height):
    hwnd = find_window(identifier)
    if not hwnd:
        return {"status": "error", "message": f"Window not found: {identifier}"}
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.MoveWindow(hwnd, int(x), int(y), int(width), int(height), True)
    return {"status": "success", "action": "move_resize", "hwnd": hwnd, "x": x, "y": y, "width": width, "height": height}


def launch_application(target, args=None):
    """
    Launches an application by name (e.g. 'notepad', 'calc', 'chrome', 'explorer', 'yt', 'whatsapp', 'spotify')
    or executable file path or web URL/protocol.
    """
    import webbrowser
    import shutil
    import urllib.parse
    t_clean = str(target or "").strip()
    if not t_clean:
        t_clean = "https://www.youtube.com"

    # Strip conversational noise and verb particles:
    # "open up youtube" -> "youtube", "up yootube" -> "yootube"
    t_lower = re.sub(r'^(?:up\s+|the\s+|a\s+|an\s+|open\s+|launch\s+|start\s+)+', '', t_clean.lower()).strip()
    t_lower = re.sub(r'\s+(?:app|application|website|site|program)$', '', t_lower).strip()

    # Known application, protocol, & web service mappings
    app_map = {
        # YouTube & Video
        "yt": "https://www.youtube.com",
        "youtube": "https://www.youtube.com",
        "yootube": "https://www.youtube.com",
        "ytube": "https://www.youtube.com",
        "you tube": "https://www.youtube.com",

        # WhatsApp
        "whatsapp": "whatsapp://",
        "whats app": "whatsapp://",
        "whatsup": "whatsapp://",
        "watsapp": "whatsapp://",
        "watsp": "whatsapp://",

        # Spotify
        "spotify": "spotify://",
        "spotfy": "spotify://",

        # Web services & socials
        "gmail": "https://mail.google.com",
        "mail": "https://mail.google.com",
        "google": "https://www.google.com",
        "browser": "https://www.google.com",
        "web": "https://www.google.com",
        "internet": "https://www.google.com",
        "github": "https://github.com",
        "git": "https://github.com",
        "twitter": "https://x.com",
        "x": "https://x.com",
        "reddit": "https://reddit.com",
        "facebook": "https://facebook.com",
        "fb": "https://facebook.com",
        "instagram": "https://instagram.com",
        "insta": "https://instagram.com",
        "netflix": "https://netflix.com",

        # Browsers & Windows Desktop Apps
        "chrome": "chrome",
        "google chrome": "chrome",
        "edge": "msedge",
        "msedge": "msedge",
        "microsoft edge": "msedge",
        "notepad": "notepad",
        "notes": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "explorer": "explorer",
        "file explorer": "explorer",
        "files": "explorer",
        "folder": "explorer",
        "cmd": "cmd",
        "command prompt": "cmd",
        "terminal": "wt",
        "powershell": "powershell",
        "task manager": "taskmgr",
        "taskmgr": "taskmgr",
        "vs code": "code",
        "vscode": "code",
        "code": "code",
        "settings": "ms-settings:",
        "control panel": "control",
        "paint": "mspaint",
        "mspaint": "mspaint"
    }

    resolved = app_map.get(t_lower, app_map.get(t_clean.lower(), t_clean))

    # 1. Direct Web URLs
    if resolved.startswith("http://") or resolved.startswith("https://"):
        try:
            webbrowser.open(resolved)
            return {
                "status": "success",
                "action": "open_url",
                "target": resolved,
                "message": f"Opened '{resolved}' in your default browser."
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to open URL '{resolved}': {e}"}

    # 2. Windows URI Protocols (whatsapp://, spotify://, ms-settings:)
    if "://" in resolved or resolved.endswith(":"):
        try:
            os.startfile(resolved)
            return {
                "status": "success",
                "action": "launch_protocol",
                "target": resolved,
                "message": f"Launched '{resolved}' protocol successfully."
            }
        except Exception:
            # Fallback for web interface if desktop app protocol fails
            if "whatsapp" in resolved:
                webbrowser.open("https://web.whatsapp.com")
            elif "spotify" in resolved:
                webbrowser.open("https://open.spotify.com")
            return {
                "status": "success",
                "action": "fallback_web",
                "target": resolved,
                "message": f"Opened web interface for '{t_clean}'."
            }

    # 3. Standard executable launching
    try:
        cmd = [resolved]
        if args:
            if isinstance(args, list):
                cmd.extend(args)
            else:
                cmd.append(str(args))

        # Check if resolved is on PATH or executable
        found_path = shutil.which(resolved)
        if found_path:
            proc = subprocess.Popen(cmd, shell=False)
            time.sleep(0.3)
            return {
                "status": "success",
                "action": "launch",
                "target": resolved,
                "pid": proc.pid,
                "message": f"Launched '{resolved}' successfully."
            }

        # Try os.startfile for Windows shell associations
        try:
            os.startfile(resolved)
            return {
                "status": "success",
                "action": "startfile",
                "target": resolved,
                "message": f"Launched '{resolved}' successfully."
            }
        except Exception:
            pass

        # If it looks like a domain name (e.g. youtube.com, notion.so) or web service:
        if "." in resolved:
            url = f"https://{resolved}" if not resolved.startswith("http") else resolved
            webbrowser.open(url)
            return {
                "status": "success",
                "action": "open_url",
                "target": url,
                "message": f"Opened '{url}' in your default browser."
            }

        # Last resort: open Google search for the application
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(resolved)}")
        return {
            "status": "success",
            "action": "web_search_fallback",
            "target": resolved,
            "message": f"Searched for '{resolved}' in your browser."
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to launch '{target}': {e}"}


def list_running_processes(filter_name=None, limit=50):
    """Lists running processes with CPU and memory usage using psutil."""
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = p.info
            name = info.get('name') or ''
            if filter_name and filter_name.lower() not in name.lower():
                continue
            procs.append({
                "pid": info['pid'],
                "name": name,
                "cpu_percent": round(info.get('cpu_percent') or 0, 1),
                "memory_percent": round(info.get('memory_percent') or 0, 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procs.sort(key=lambda x: x['memory_percent'], reverse=True)
    return procs[:limit]
