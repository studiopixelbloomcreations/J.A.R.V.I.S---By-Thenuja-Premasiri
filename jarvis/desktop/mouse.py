"""
Win32 Native & Virtual Mouse Control Engine for J.A.R.V.I.S.
Provides smooth interpolation, Bezier curves, clicks, double-clicks, right-clicks,
middle clicks, drag and drop, vertical & horizontal scrolling, and safety emergency checks.
"""
import time
import math
import ctypes
from ctypes import wintypes
from .emergency import emergency, EmergencyStopError

user32 = ctypes.windll.user32

# Mouse event constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0009
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x01000
MOUSEEVENTF_ABSOLUTE = 0x8000

# Virtual cursor tracking
_virtual_mode = False
_virtual_cursor = [500, 500]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


def set_virtual_mode(enabled: bool):
    """Toggles virtual cursor mode (useful for testing, sandbox, or headless execution)."""
    global _virtual_mode
    _virtual_mode = bool(enabled)
    return {"status": "success", "virtual_mode": _virtual_mode}


def is_virtual_mode():
    """Returns True if virtual cursor mode is active."""
    return _virtual_mode


def get_cursor_position():
    """Returns current (x, y) coordinates of the mouse cursor."""
    if _virtual_mode:
        return _virtual_cursor[0], _virtual_cursor[1]
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def move_cursor(x, y, smooth=True, steps=12):
    """
    Moves mouse cursor to target coordinates, optionally with smooth interpolation.
    Checks emergency stop and corner fail-safe invariants.
    """
    emergency.check_safety()
    curr_x, curr_y = get_cursor_position()
    target_x, target_y = int(x), int(y)

    if _virtual_mode:
        if smooth and steps > 1:
            for i in range(1, steps + 1):
                emergency.check_safety()
                _virtual_cursor[0] = int(curr_x + (target_x - curr_x) * (i / steps))
                _virtual_cursor[1] = int(curr_y + (target_y - curr_y) * (i / steps))
                time.sleep(0.002)
        _virtual_cursor[0], _virtual_cursor[1] = target_x, target_y
        return {"status": "success", "x": target_x, "y": target_y, "virtual": True}

    if not smooth or steps <= 1:
        emergency.check_safety((target_x, target_y))
        user32.SetCursorPos(target_x, target_y)
        return {"status": "success", "x": target_x, "y": target_y}

    for i in range(1, steps + 1):
        inter_x = int(curr_x + (target_x - curr_x) * (i / steps))
        inter_y = int(curr_y + (target_y - curr_y) * (i / steps))
        emergency.check_safety((inter_x, inter_y))
        user32.SetCursorPos(inter_x, inter_y)
        time.sleep(0.006)

    user32.SetCursorPos(target_x, target_y)
    return {"status": "success", "x": target_x, "y": target_y}


def move_relative(dx, dy, smooth=False, steps=6):
    """Moves mouse cursor relative to current position."""
    curr_x, curr_y = get_cursor_position()
    return move_cursor(curr_x + dx, curr_y + dy, smooth=smooth, steps=steps)


def move_bezier(target_x, target_y, steps=20, deviation=0.15):
    """
    Moves mouse cursor along a smooth quadratic Bezier curve to mimic human hand motion.
    """
    emergency.check_safety()
    curr_x, curr_y = get_cursor_position()
    tx, ty = int(target_x), int(target_y)

    # Control point offset perpendicular to vector
    mid_x = (curr_x + tx) / 2.0
    mid_y = (curr_y + ty) / 2.0
    dx = tx - curr_x
    dy = ty - curr_y
    dist = math.hypot(dx, dy)

    ctrl_x = mid_x - dy * deviation
    ctrl_y = mid_y + dx * deviation

    for i in range(1, steps + 1):
        t = i / float(steps)
        # B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2
        bx = int((1 - t) ** 2 * curr_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * tx)
        by = int((1 - t) ** 2 * curr_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * ty)

        if _virtual_mode:
            emergency.check_safety()
            _virtual_cursor[0], _virtual_cursor[1] = bx, by
        else:
            emergency.check_safety((bx, by))
            user32.SetCursorPos(bx, by)
        time.sleep(0.005)

    return {"status": "success", "x": tx, "y": ty, "bezier": True}


def mouse_down(button="left"):
    """Depresses specified mouse button."""
    emergency.check_safety()
    btn = button.lower()
    if _virtual_mode:
        return {"status": "success", "action": "mouse_down", "button": btn}

    if btn == "right":
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    elif btn == "middle":
        user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
    else:
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    return {"status": "success", "action": "mouse_down", "button": btn}


def mouse_up(button="left"):
    """Releases specified mouse button."""
    btn = button.lower()
    if _virtual_mode:
        return {"status": "success", "action": "mouse_up", "button": btn}

    if btn == "right":
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    elif btn == "middle":
        user32.mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
    else:
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    return {"status": "success", "action": "mouse_up", "button": btn}


def click(x=None, y=None, button="left", clicks=1):
    """Executes single or multiple clicks at current or specified position."""
    emergency.check_safety()
    if x is not None and y is not None:
        move_cursor(x, y)

    time.sleep(0.01)
    for _ in range(clicks):
        emergency.check_safety()
        mouse_down(button)
        time.sleep(0.02)
        mouse_up(button)
        time.sleep(0.03)

    pos_x, pos_y = get_cursor_position()
    return {"status": "success", "action": f"{button}_click", "clicks": clicks, "x": pos_x, "y": pos_y}


def right_click(x=None, y=None):
    return click(x, y, button="right")


def double_click(x=None, y=None):
    return click(x, y, button="left", clicks=2)


def triple_click(x=None, y=None):
    return click(x, y, button="left", clicks=3)


def middle_click(x=None, y=None):
    return click(x, y, button="middle", clicks=1)


def scroll(delta=120, direction="up"):
    """Scrolls mouse wheel vertically. Delta is scroll amount (positive for up, negative for down)."""
    emergency.check_safety()
    val = abs(delta) if direction.lower() in ["up", "scrollup"] else -abs(delta)
    if not _virtual_mode:
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, val, 0)
    return {"status": "success", "action": "scroll", "direction": direction, "delta": val}


def scroll_horizontal(delta=120, direction="right"):
    """Scrolls mouse wheel horizontally (tilt wheel)."""
    emergency.check_safety()
    val = abs(delta) if direction.lower() in ["right", "scrollright"] else -abs(delta)
    if not _virtual_mode:
        user32.mouse_event(MOUSEEVENTF_HWHEEL, 0, 0, val, 0)
    return {"status": "success", "action": "scroll_horizontal", "direction": direction, "delta": val}


def drag_to(target_x, target_y):
    """Drags from current position to target coordinates."""
    emergency.check_safety()
    mouse_down("left")
    time.sleep(0.03)
    move_cursor(target_x, target_y, smooth=True, steps=18)
    time.sleep(0.03)
    mouse_up("left")
    return {"status": "success", "action": "drag", "to_x": target_x, "to_y": target_y}


def drag_and_drop(start_x, start_y, end_x, end_y, steps=20):
    """Moves to start position, clicks down, drags smoothly to end position, and releases."""
    emergency.check_safety()
    move_cursor(start_x, start_y, smooth=True, steps=steps // 2 or 6)
    time.sleep(0.04)
    mouse_down("left")
    time.sleep(0.04)
    move_cursor(end_x, end_y, smooth=True, steps=steps)
    time.sleep(0.04)
    mouse_up("left")
    return {
        "status": "success",
        "action": "drag_and_drop",
        "from": (start_x, start_y),
        "to": (end_x, end_y)
    }
