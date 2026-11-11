"""
Win32 Native Mouse Control Engine for J.A.R.V.I.S.
Provides smooth movement, clicks, double-clicks, right-clicks, drag, and scrolling.
"""
import time
import ctypes
from ctypes import wintypes

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
MOUSEEVENTF_ABSOLUTE = 0x8000


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


def get_cursor_position():
    """Returns current (x, y) coordinates of the mouse cursor."""
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def move_cursor(x, y, smooth=True, steps=12):
    """Moves mouse cursor to target coordinates, optionally with smooth interpolation."""
    curr_x, curr_y = get_cursor_position()
    if not smooth:
        user32.SetCursorPos(int(x), int(y))
        return {"status": "success", "x": x, "y": y}

    for i in range(1, steps + 1):
        inter_x = int(curr_x + (x - curr_x) * (i / steps))
        inter_y = int(curr_y + (y - curr_y) * (i / steps))
        user32.SetCursorPos(inter_x, inter_y)
        time.sleep(0.008)

    user32.SetCursorPos(int(x), int(y))
    return {"status": "success", "x": x, "y": y}


def click(x=None, y=None, button="left", clicks=1):
    """Executes single or multiple clicks at current or specified position."""
    if x is not None and y is not None:
        move_cursor(x, y)

    time.sleep(0.02)
    for _ in range(clicks):
        if button == "right":
            user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.02)
            user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        elif button == "middle":
            user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
            time.sleep(0.02)
            user32.mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
        else:
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.02)
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.05)

    pos_x, pos_y = get_cursor_position()
    return {"status": "success", "action": f"{button}_click", "clicks": clicks, "x": pos_x, "y": pos_y}


def right_click(x=None, y=None):
    return click(x, y, button="right")


def double_click(x=None, y=None):
    return click(x, y, button="left", clicks=2)


def scroll(delta=120, direction="up"):
    """Scrolls mouse wheel. Delta is scroll amount (positive for up, negative for down)."""
    val = delta if direction.lower() in ["up", "scrollup"] else -delta
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, val, 0)
    return {"status": "success", "action": "scroll", "direction": direction, "delta": val}


def drag_to(target_x, target_y):
    """Drags from current position to target coordinates."""
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    move_cursor(target_x, target_y, smooth=True, steps=18)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    return {"status": "success", "action": "drag", "to_x": target_x, "to_y": target_y}
