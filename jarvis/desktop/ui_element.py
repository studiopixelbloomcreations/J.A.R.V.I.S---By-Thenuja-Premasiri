"""
Capability 17: UI Element Recognition Subsystem for J.A.R.V.I.S.
Discovers and recognizes native Win32 controls, child windows, buttons, input fields,
and coordinates for programmatic element interaction and visual hit-testing.
"""
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .windows import find_window, get_active_window

user32 = ctypes.windll.user32

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


@dataclass
class UIElement:
    hwnd: int
    parent_hwnd: int
    control_type: str
    text: str
    x: int
    y: int
    width: int
    height: int
    is_visible: bool
    is_enabled: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hwnd": self.hwnd,
            "parent_hwnd": self.parent_hwnd,
            "control_type": self.control_type,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "is_visible": self.is_visible,
            "is_enabled": self.is_enabled,
            "center": (self.x + self.width // 2, self.y + self.height // 2),
        }

    def contains_point(self, px: int, py: int) -> bool:
        return (self.x <= px <= self.x + self.width) and (self.y <= py <= self.y + self.height)


class UIElementRecognizer:
    """Discovers and interrogates Win32 UI controls inside windows."""

    def enumerate_controls(self, window_identifier=None) -> List[UIElement]:
        """Enumerates child controls within a window (or currently active window)."""
        if window_identifier is None:
            act = get_active_window()
            parent_hwnd = act["hwnd"] if act else user32.GetForegroundWindow()
        else:
            parent_hwnd = find_window(window_identifier)

        if not parent_hwnd:
            return []

        elements: List[UIElement] = []

        def enum_child_proc(hwnd, lparam):
            is_vis = bool(user32.IsWindowVisible(hwnd))
            is_en = bool(user32.IsWindowEnabled(hwnd))

            # Class name
            class_buff = ctypes.create_unicode_buffer(128)
            user32.GetClassNameW(hwnd, class_buff, 128)
            control_type = class_buff.value

            # Text
            text_len = user32.GetWindowTextLengthW(hwnd)
            text = ""
            if text_len > 0:
                text_buff = ctypes.create_unicode_buffer(text_len + 1)
                user32.GetWindowTextW(hwnd, text_buff, text_len + 1)
                text = text_buff.value.strip()

            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top

            if w > 0 and h > 0:
                elem = UIElement(
                    hwnd=hwnd,
                    parent_hwnd=parent_hwnd,
                    control_type=control_type,
                    text=text,
                    x=rect.left,
                    y=rect.top,
                    width=w,
                    height=h,
                    is_visible=is_vis,
                    is_enabled=is_en,
                )
                elements.append(elem)
            return True

        cb = WNDENUMPROC(enum_child_proc)
        user32.EnumChildWindows(parent_hwnd, cb, 0)
        return elements

    def find_element(self, query: str, window_identifier=None, match_case=False) -> Optional[UIElement]:
        """Finds a control by text, partial text, or class name."""
        controls = self.enumerate_controls(window_identifier)
        q = query if match_case else query.lower().strip()

        # Exact text match first
        for c in controls:
            ctext = c.text if match_case else c.text.lower()
            if ctext == q:
                return c

        # Partial text match
        for c in controls:
            ctext = c.text if match_case else c.text.lower()
            if q in ctext:
                return c

        # Class match
        for c in controls:
            c_type = c.control_type if match_case else c.control_type.lower()
            if q in c_type:
                return c

        return None

    def find_all_buttons(self, window_identifier=None) -> List[UIElement]:
        """Finds all visible buttons in the target window."""
        controls = self.enumerate_controls(window_identifier)
        return [c for c in controls if "button" in c.control_type.lower() and c.is_visible]

    def find_all_inputs(self, window_identifier=None) -> List[UIElement]:
        """Finds all text input / edit boxes in the target window."""
        controls = self.enumerate_controls(window_identifier)
        return [c for c in controls if "edit" in c.control_type.lower() and c.is_visible]

    def element_at_point(self, x: int, y: int, window_identifier=None) -> Optional[UIElement]:
        """Performs hit testing to find the smallest UIElement at coordinate (x, y)."""
        controls = self.enumerate_controls(window_identifier)
        matching = [c for c in controls if c.contains_point(x, y)]
        if not matching:
            return None
        # Sort by area ascending so we get the most specific child element
        matching.sort(key=lambda c: c.width * c.height)
        return matching[0]


ui_recognizer = UIElementRecognizer()
