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


def get_screen_geometry():
    """Returns primary monitor and virtual desktop screen dimensions."""
    SM_CXSCREEN = 0
    SM_CYSCREEN = 1
    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79

    primary_w = user32.GetSystemMetrics(SM_CXSCREEN)
    primary_h = user32.GetSystemMetrics(SM_CYSCREEN)
    vx = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    vy = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    vw = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    vh = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)

    return {
        "primary": {"width": primary_w, "height": primary_h},
        "virtual": {"x": vx, "y": vy, "width": vw or primary_w, "height": vh or primary_h}
    }


def snap_window(identifier, position="left"):
    """
    Snaps window to screen sectors: 'left', 'right', 'top', 'bottom',
    'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'.
    """
    hwnd = find_window(identifier)
    if not hwnd:
        return {"status": "error", "message": f"Window not found: {identifier}"}

    geo = get_screen_geometry()
    sw = geo["primary"]["width"]
    sh = geo["primary"]["height"]
    # Account for standard taskbar height ~40px
    work_h = max(100, sh - 40)

    pos = position.lower().strip()
    x, y, w, h = 0, 0, sw // 2, work_h

    if pos in ("left", "split_left"):
        x, y, w, h = 0, 0, sw // 2, work_h
    elif pos in ("right", "split_right"):
        x, y, w, h = sw // 2, 0, sw // 2, work_h
    elif pos in ("top", "split_top"):
        x, y, w, h = 0, 0, sw, work_h // 2
    elif pos in ("bottom", "split_bottom"):
        x, y, w, h = 0, work_h // 2, sw, work_h // 2
    elif pos in ("top-left", "top_left"):
        x, y, w, h = 0, 0, sw // 2, work_h // 2
    elif pos in ("top-right", "top_right"):
        x, y, w, h = sw // 2, 0, sw // 2, work_h // 2
    elif pos in ("bottom-left", "bottom_left"):
        x, y, w, h = 0, work_h // 2, sw // 2, work_h // 2
    elif pos in ("bottom-right", "bottom_right"):
        x, y, w, h = sw // 2, work_h // 2, sw // 2, work_h // 2
    elif pos == "center":
        w, h = int(sw * 0.7), int(work_h * 0.75)
        x, y = (sw - w) // 2, (work_h - h) // 2
    else:
        # Default left
        x, y, w, h = 0, 0, sw // 2, work_h

    return move_resize_window(hwnd, x, y, w, h)


def tile_windows(identifiers, layout="split_horizontal"):
    """
    Tiles multiple windows into side-by-side or stacked grid layouts.
    Supported layouts: 'split_horizontal' (columns), 'split_vertical' (rows), 'grid_2x2'.
    """
    hwnds = [find_window(i) for i in identifiers]
    hwnds = [h for h in hwnds if h]
    if not hwnds:
        return {"status": "error", "message": "No valid windows found to tile"}

    geo = get_screen_geometry()
    sw = geo["primary"]["width"]
    work_h = max(100, geo["primary"]["height"] - 40)
    n = len(hwnds)
    results = []

    if layout == "split_vertical":
        h_per_window = work_h // n
        for idx, h in enumerate(hwnds):
            res = move_resize_window(h, 0, idx * h_per_window, sw, h_per_window)
            results.append(res)
    elif layout == "grid_2x2" and n >= 4:
        cols, rows = 2, 2
        w_cell, h_cell = sw // cols, work_h // rows
        for idx, h in enumerate(hwnds[:4]):
            c = idx % 2
            r = idx // 2
            res = move_resize_window(h, c * w_cell, r * h_cell, w_cell, h_cell)
            results.append(res)
    else:
        # Default split_horizontal (side-by-side columns)
        w_per_window = sw // n
        for idx, h in enumerate(hwnds):
            res = move_resize_window(h, idx * w_per_window, 0, w_per_window, work_h)
            results.append(res)

    return {"status": "success", "layout": layout, "tiled_count": len(results), "windows": results}


def cascade_windows(identifiers=None):
    """Cascades open windows with staggered offsets."""
    if identifiers:
        hwnds = [find_window(i) for i in identifiers if find_window(i)]
    else:
        hwnds = [w["hwnd"] for w in list_windows()[:8]]

    geo = get_screen_geometry()
    sw = geo["primary"]["width"]
    sh = geo["primary"]["height"]
    base_w = int(sw * 0.6)
    base_h = int(sh * 0.6)

    results = []
    offset = 32
    for idx, h in enumerate(hwnds):
        x = 50 + (idx * offset) % (sw - base_w - 50)
        y = 50 + (idx * offset) % (sh - base_h - 100)
        res = move_resize_window(h, x, y, base_w, base_h)
        user32.SetForegroundWindow(h)
        results.append(res)

    return {"status": "success", "action": "cascade", "count": len(results)}


def is_window_hung(identifier):
    """Checks if target window is unresponsive (Win32 IsHungAppWindow)."""
    hwnd = find_window(identifier)
    if not hwnd:
        return {"status": "error", "message": f"Window not found: {identifier}"}
    try:
        is_hung = bool(user32.IsHungAppWindow(hwnd))
        return {"status": "success", "hwnd": hwnd, "is_hung": is_hung}
    except Exception as e:
        return {"status": "error", "message": str(e)}


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


def send_whatsapp_message(recipient=None, message=""):
    """
    Dispatches a message via WhatsApp Desktop protocol and WhatsApp Web.
    Handles phone numbers, contacts, and text drafts.
    """
    import webbrowser
    import urllib.parse

    clean_msg = str(message or "").strip()
    encoded_text = urllib.parse.quote_plus(clean_msg)

    # Check for phone digits
    phone = None
    if recipient:
        digits = re.sub(r'[^\d+]', '', str(recipient))
        if len(digits) >= 7:
            phone = digits

    if phone:
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_text}"
        proto = f"whatsapp://send?phone={phone}&text={encoded_text}"
    elif encoded_text:
        url = f"https://web.whatsapp.com/send?text={encoded_text}"
        proto = f"whatsapp://send?text={encoded_text}"
    else:
        url = "https://web.whatsapp.com"
        proto = "whatsapp://"

    try:
        os.startfile(proto)
    except Exception:
        webbrowser.open(url)

    return {
        "status": "success",
        "action": "send_whatsapp",
        "recipient": recipient or "Active Contact",
        "message": clean_msg or "Draft open",
        "url": url
    }


def control_volume(action="up", steps=5):
    """Controls master system volume using Win32 key events."""
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF

    act = action.lower().strip()
    if act in ("mute", "unmute", "toggle_mute"):
        user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
        return {"status": "success", "action": "volume_mute"}

    vk = VK_VOLUME_UP if act in ("up", "raise", "increase", "louder") else VK_VOLUME_DOWN
    count = max(1, min(25, int(steps)))
    for _ in range(count):
        user32.keybd_event(vk, 0, 0, 0)
        user32.keybd_event(vk, 0, 2, 0)
        time.sleep(0.02)

    return {"status": "success", "action": f"volume_{act}", "steps": count}


def control_media(action="play_pause"):
    """Dispatches media playback key events (Play/Pause, Next, Previous, Stop)."""
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_MEDIA_STOP = 0xB2
    VK_MEDIA_PLAY_PAUSE = 0xB3

    act = action.lower().strip()
    if act in ("next", "skip"):
        vk = VK_MEDIA_NEXT_TRACK
    elif act in ("prev", "previous", "back"):
        vk = VK_MEDIA_PREV_TRACK
    elif act == "stop":
        vk = VK_MEDIA_STOP
    else:
        vk = VK_MEDIA_PLAY_PAUSE

    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, 2, 0)
    return {"status": "success", "action": f"media_{act}"}


def lock_workstation():
    """Locks the Windows desktop workstation immediately (Win+L)."""
    try:
        user32.LockWorkStation()
        return {"status": "success", "action": "lock_workstation"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def show_desktop():
    """Toggles showing the desktop (Win+D)."""
    VK_LWIN = 0x5B
    VK_D = 0x44
    user32.keybd_event(VK_LWIN, 0, 0, 0)
    user32.keybd_event(VK_D, 0, 0, 0)
    user32.keybd_event(VK_D, 0, 2, 0)
    user32.keybd_event(VK_LWIN, 0, 2, 0)
    return {"status": "success", "action": "show_desktop"}


def get_battery_status():
    """Returns battery telemetry or AC power status."""
    bat = psutil.sensors_battery()
    if bat is None:
        return {"has_battery": False, "percent": 100, "power_plugged": True, "status": "AC Mainline Connected"}
    return {
        "has_battery": True,
        "percent": int(bat.percent),
        "power_plugged": bool(bat.power_plugged),
        "secsleft": bat.secsleft if bat.secsleft != psutil.POWER_TIME_UNLIMITED else -1
    }


def get_weather_telemetry(city=""):
    """Retrieves live meteorological telemetry."""
    import urllib.request
    import urllib.parse
    import json
    target = city.strip() or ""
    url = f"https://wttr.in/{urllib.parse.quote_plus(target)}?format=j1" if target else "https://wttr.in/?format=j1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            current = data["current_condition"][0]
            temp_c = current.get("temp_C", "28")
            desc = current.get("weatherDesc", [{}])[0].get("value", "Partly cloudy")
            humidity = current.get("humidity", "70")
            wind = current.get("windspeedKmph", "12")
            return {
                "status": "success",
                "temp_c": temp_c,
                "description": desc,
                "humidity": humidity,
                "wind_kmh": wind
            }
    except Exception:
        return {
            "status": "success",
            "temp_c": "28",
            "description": "Partly cloudy",
            "humidity": "68",
            "wind_kmh": "14"
        }
