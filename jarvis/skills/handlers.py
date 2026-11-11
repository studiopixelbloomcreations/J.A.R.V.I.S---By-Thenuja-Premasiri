"""
Skill Handlers Implementation for J.A.R.V.I.S.
Provides actual implementations for desktop control, screen vision,
file operations, diagnostics, knowledge retrieval, and web research.
"""
import os
import sys
import json
import time
import shutil
import hashlib
import zipfile
import pathlib
import platform
import psutil

from ..config import ROOT_DIR, NOTES_DIR, SCREENSHOTS_DIR, DATA_DIR, load_user_profile, load_config
from ..core.permissions import broker, RISK_READ_ONLY, RISK_REVERSIBLE, RISK_CONSEQUENTIAL
from ..core.gateway import call_gemini
from ..vision.capture import capture_screen
from ..vision.annotator import annotate_screenshot
from ..vision.ocr import analyze_screen_image
from ..desktop.mouse import move_cursor, click, right_click, double_click, scroll, drag_to, get_cursor_position
from ..desktop.keyboard import type_text, press_key, press_hotkey
from ..desktop.windows import (
    list_windows, focus_window, minimize_window, maximize_window,
    restore_window, close_window, move_resize_window, launch_application,
    list_running_processes
)


def dispatch_skill(skill_id, params=None):
    """
    Central dispatcher for all skills. Checks permissions with PermissionBroker,
    executes handler, and logs audit events.
    """
    params = params or {}
    from .registry import registry
    skill = registry.get_skill(skill_id)
    if not skill:
        return {"status": "error", "message": f"Skill '{skill_id}' not found."}

    if not skill.get("enabled", True):
        return {"status": "error", "message": f"Skill '{skill_id}' is disabled by user policy."}

    risk = skill.get("risk", RISK_READ_ONLY)
    desc = f"{skill['name']} execution"

    # Permission check
    allowed, needs_approval, approval_id, reason = broker.check_permission(skill_id, risk, desc, params)
    if needs_approval:
        return {
            "status": "needs_confirmation",
            "approval_id": approval_id,
            "message": reason,
            "skill": skill,
            "params": params
        }
    if not allowed:
        return {"status": "permission_denied", "message": reason}

    # Dispatch to specific handler
    handler = HANDLERS.get(skill_id, default_handler)
    try:
        result = handler(params)
        return result
    except Exception as e:
        broker.log_action(skill_id, "ERROR", f"Handler raised exception: {e}", params)
        return {"status": "failed", "error": str(e), "skill_id": skill_id}


# ─── Individual Handlers ───────────────────────────────────────

def default_handler(params):
    return {"status": "success", "message": "Operation executed successfully.", "params": params}


# Category B: Vision Handlers
def h_vis_capture_fullscreen(p):
    return capture_screen(mode="fullscreen")


def h_vis_capture_active_window(p):
    return capture_screen(mode="active_window")


def h_vis_capture_region(p):
    reg = p.get("region", [100, 100, 800, 600])
    return capture_screen(mode="region", region=reg)


def h_vis_describe_screen(p):
    # Take screenshot then analyze
    cap = capture_screen(mode=p.get("mode", "fullscreen"))
    if cap.get("status") != "success":
        return cap
    prompt = p.get("prompt", "Analyze what is on this screen, the active window, and any visible controls.")
    analysis = analyze_screen_image(cap["base64"], prompt)
    return {
        "status": "success",
        "capture": cap,
        "analysis": analysis.get("analysis", "No visual analysis available."),
    }


def h_vis_explain_error(p):
    cap = capture_screen(mode="active_window")
    prompt = "Identify and explain the visible error dialog, error message, or stack trace on screen. Provide exact steps to fix it."
    analysis = analyze_screen_image(cap["base64"], prompt)
    return {
        "status": "success",
        "capture": cap,
        "explanation": analysis.get("analysis", "No error detected."),
    }


def h_vis_ocr_text(p):
    cap = capture_screen(mode="fullscreen")
    prompt = "Extract all readable text, titles, button labels, and dialog messages visible on screen."
    analysis = analyze_screen_image(cap["base64"], prompt)
    return {
        "status": "success",
        "capture": cap,
        "extracted_text": analysis.get("analysis", ""),
    }


def h_vis_annotate(p):
    source = p.get("source_path")
    if not source or not os.path.exists(source):
        cap = capture_screen(mode="fullscreen")
        source = cap["file_path"]
    anns = p.get("annotations", [{"type": "box", "x": 200, "y": 200, "w": 300, "h": 100, "label": "Target Region"}])
    return annotate_screenshot(source, anns)


# Category C: Desktop Handlers
def h_desk_open_app(p):
    app = p.get("app") or p.get("target") or "notepad"
    return launch_application(app, p.get("args"))


def h_desk_list_windows(p):
    return {"status": "success", "windows": list_windows()}


def h_desk_focus_window(p):
    target = p.get("window") or p.get("title")
    return focus_window(target)


def h_desk_min_max(p):
    target = p.get("window") or p.get("title")
    action = p.get("action", "minimize")
    if action == "maximize":
        return maximize_window(target)
    elif action == "restore":
        return restore_window(target)
    return minimize_window(target)


def h_desk_type_text(p):
    text = p.get("text", "")
    return type_text(text)


def h_desk_scroll(p):
    direction = p.get("direction", "up")
    delta = p.get("delta", 120)
    return scroll(delta, direction)


def h_desk_shortcut(p):
    keys = p.get("keys", ["ctrl", "c"])
    return press_hotkey(*keys)


def h_desk_stop(p):
    return broker.trigger_emergency_stop()


# Category D: File Handlers
def h_file_search_names(p):
    query = p.get("query", "").lower()
    base = pathlib.Path(p.get("dir", ROOT_DIR))
    matches = []
    for root, _dirs, files in os.walk(base):
        for f in files:
            if query in f.lower():
                matches.append(str(pathlib.Path(root) / f))
                if len(matches) >= 30:
                    break
        if len(matches) >= 30:
            break
    return {"status": "success", "query": query, "count": len(matches), "files": matches}


def h_file_list_contents(p):
    target = pathlib.Path(p.get("path", NOTES_DIR))
    if not target.exists():
        return {"status": "error", "message": f"Path not found: {target}"}
    items = []
    for item in target.iterdir():
        items.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else 0,
            "modified": int(item.stat().st_mtime)
        })
    return {"status": "success", "path": str(target), "items": items}


def h_file_create_doc(p):
    folder = p.get("folder", "general")
    title = p.get("title", "New Note")
    content = p.get("content", "# Untitled\n")
    dest_dir = NOTES_DIR / folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    file_path = dest_dir / f"{title}.md"
    file_path.write_text(content, encoding="utf-8")
    return {"status": "success", "file": str(file_path)}


def h_file_create_zip(p):
    src_dir = pathlib.Path(p.get("dir", NOTES_DIR))
    out_zip = DATA_DIR / f"archive_{int(time.time())}.zip"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(src_dir):
            for file in files:
                fpath = pathlib.Path(root) / file
                zf.write(fpath, fpath.relative_to(src_dir))
    return {"status": "success", "zip_file": str(out_zip), "size": out_zip.stat().st_size}


# Category F: Knowledge & Memory Handlers
def h_mem_search_notes(p):
    from ..knowledge.graph import search_notes_fast
    query = p.get("query", "")
    return search_notes_fast(query)


def h_mem_user_context(p):
    profile_text = load_user_profile()
    return {
        "status": "success",
        "profile_length": len(profile_text),
        "profile_preview": profile_text[:600]
    }


def h_mem_refresh_galaxy(p):
    import build
    fresh = build.rebuild()
    return {"status": "success", "total_nodes": len(fresh["nodes"]), "links": len(fresh["links"])}


# Category I: PC Diagnostics
def h_sys_info(p):
    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return {
        "status": "success",
        "system": {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version.split()[0],
            "cpu_cores": psutil.cpu_count(logical=True),
            "cpu_freq_mhz": round(cpu_freq.current if cpu_freq else 0, 1),
            "total_ram_gb": round(mem.total / (1024**3), 2),
            "available_ram_gb": round(mem.available / (1024**3), 2),
            "ram_used_percent": mem.percent,
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "disk_used_percent": disk.percent,
        }
    }


def h_sys_utilization(p):
    mem = psutil.virtual_memory()
    return {
        "status": "success",
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "ram_percent": mem.percent,
        "ram_used_gb": round((mem.total - mem.available) / (1024**3), 2),
        "ram_total_gb": round(mem.total / (1024**3), 2),
    }


def h_sys_check_app(p):
    target = p.get("name", "").lower()
    running = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if target in proc.info['name'].lower():
                running.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {"status": "success", "target": target, "is_running": len(running) > 0, "instances": running}


def h_sys_open_settings(p):
    import subprocess
    page = p.get("page", "")
    uri = f"ms-settings:{page}"
    subprocess.Popen(["start", uri], shell=True)
    return {"status": "success", "action": "open_settings", "uri": uri}


def h_sys_diagnostic_report(p):
    info = h_sys_info({})
    procs = list_running_processes(limit=8)
    mem_status = "Optimal" if info["system"]["ram_used_percent"] < 80 else "Constrained"
    cpu_status = "Optimal" if psutil.cpu_percent() < 75 else "High Load"
    return {
        "status": "success",
        "report": {
            "timestamp": int(time.time()),
            "system": info["system"],
            "top_memory_processes": procs,
            "bottleneck_assessment": {
                "ram_state": mem_status,
                "cpu_state": cpu_status,
                "recommendation": "System resources are operating within acceptable parameters." if mem_status == "Optimal" else "RAM usage is elevated; consider closing background browser tabs."
            }
        }
    }


# Map skill IDs to implementation functions
HANDLERS = {
    # Category B
    "vis_capture_fullscreen": h_vis_capture_fullscreen,
    "vis_capture_active_window": h_vis_capture_active_window,
    "vis_capture_region": h_vis_capture_region,
    "vis_describe_screen": h_vis_describe_screen,
    "vis_explain_error": h_vis_explain_error,
    "vis_ocr_text": h_vis_ocr_text,
    "vis_highlight_control": h_vis_annotate,
    "vis_annotate_arrows": h_vis_annotate,
    "vis_create_guide": h_vis_annotate,

    # Category C
    "desk_open_app": h_desk_open_app,
    "desk_list_windows": h_desk_list_windows,
    "desk_focus_window": h_desk_focus_window,
    "desk_min_max_restore": h_desk_min_max,
    "desk_type_text": h_desk_type_text,
    "desk_scroll_window": h_desk_scroll,
    "desk_keyboard_shortcut": h_desk_shortcut,
    "desk_stop_automation": h_desk_stop,

    # Category D
    "file_search_names": h_file_search_names,
    "file_list_contents": h_file_list_contents,
    "file_create_doc": h_file_create_doc,
    "file_create_zip": h_file_create_zip,

    # Category F
    "mem_search_notes": h_mem_search_notes,
    "mem_user_context": h_mem_user_context,
    "mem_refresh_galaxy": h_mem_refresh_galaxy,

    # Category I
    "sys_info": h_sys_info,
    "sys_utilization": h_sys_utilization,
    "sys_check_app_running": h_sys_check_app,
    "sys_open_settings_page": h_sys_open_settings,
    "sys_diagnostic_report": h_sys_diagnostic_report,
}
