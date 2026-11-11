"""
Win32 Native Keyboard Engine for J.A.R.V.I.S.
Handles typing, individual key presses, and modifier hotkeys.
"""
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

VK_MAP = {
    "enter": 0x0D, "return": 0x0D,
    "esc": 0x1B, "escape": 0x1B,
    "tab": 0x09,
    "space": 0x20,
    "backspace": 0x08,
    "delete": 0x2E, "del": 0x2E,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "pageup": 0x21, "pagedown": 0x22, "home": 0x24, "end": 0x23,
    "ctrl": 0x11, "control": 0x11,
    "alt": 0x12,
    "shift": 0x10,
    "win": 0x5B, "windows": 0x5B,
    "capslock": 0x14,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75,
    "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
}


def press_key(key_name):
    """Presses and releases a single key."""
    key_lower = key_name.lower().strip()
    vk = VK_MAP.get(key_lower)
    if vk is None and len(key_lower) == 1:
        # Single alphanumeric character
        vk = ord(key_lower.upper())

    if vk:
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        return {"status": "success", "key": key_name}
    return {"status": "error", "message": f"Unknown key: {key_name}"}


def press_hotkey(*keys):
    """Presses a combination of keys simultaneously, e.g. ('ctrl', 'c') or ('alt', 'tab')."""
    vks = []
    for k in keys:
        kl = k.lower().strip()
        vk = VK_MAP.get(kl)
        if vk is None and len(kl) == 1:
            vk = ord(kl.upper())
        if vk:
            vks.append(vk)

    # Press down in order
    for vk in vks:
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.015)

    time.sleep(0.04)

    # Release in reverse order
    for vk in reversed(vks):
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.015)

    return {"status": "success", "hotkey": "+".join(keys)}


def type_text(text, delay=0.015):
    """Types unicode text accurately using KEYEVENTF_UNICODE."""
    for char in text:
        code = ord(char)
        # Windows SendInput or keybd_event unicode key
        user32.keybd_event(0, code, KEYEVENTF_UNICODE, 0)
        user32.keybd_event(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0)
        if delay > 0:
            time.sleep(delay)

    return {"status": "success", "typed_length": len(text)}
