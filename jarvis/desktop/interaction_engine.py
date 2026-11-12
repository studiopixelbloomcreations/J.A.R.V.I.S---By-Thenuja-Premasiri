"""
Integrated Local Desktop Interaction Engine for J.A.R.V.I.S.
Provides unified control over virtual cursor, mouse dynamics, scrolling, dragging,
keyboard synthesis, window orchestration, and emergency stop/pause safety mechanisms.
"""
import logging
from .emergency import emergency, EmergencyStopError
from .mouse import (
    get_cursor_position,
    move_cursor,
    move_relative,
    move_bezier,
    click,
    right_click,
    double_click,
    triple_click,
    middle_click,
    mouse_down,
    mouse_up,
    scroll,
    scroll_horizontal,
    drag_to,
    drag_and_drop,
    set_virtual_mode,
    is_virtual_mode,
)
from .keyboard import press_key, press_hotkey, type_text
from .windows import (
    list_windows,
    get_active_window,
    find_window,
    focus_window,
    minimize_window,
    maximize_window,
    restore_window,
    close_window,
    move_resize_window,
    snap_window,
    tile_windows,
    cascade_windows,
    get_screen_geometry,
    launch_application,
    is_window_hung,
)

logger = logging.getLogger("jarvis.desktop.interaction_engine")


class DesktopInteractionEngine:
    """
    Unified local desktop interaction engine combining mouse, keyboard,
    window geometry orchestration, and emergency safety control.
    """

    def __init__(self, virtual_mode=False):
        self._emergency = emergency
        if virtual_mode:
            set_virtual_mode(True)

    # ------------------ Emergency & Safety ------------------
    def emergency_stop(self, reason="Manual emergency stop"):
        """Immediately halts all cursor actions, releases buttons, and flags emergency stop."""
        return self._emergency.trigger_emergency_stop(reason)

    def pause(self, reason="User paused"):
        """Pauses in-flight desktop automation."""
        return self._emergency.pause(reason)

    def resume(self):
        """Resumes paused desktop automation."""
        return self._emergency.resume()

    def reset_emergency(self):
        """Resets emergency stop and pause states back to operational."""
        return self._emergency.reset()

    def is_stopped(self):
        return self._emergency.is_stopped

    def is_paused(self):
        return self._emergency.is_paused

    def check_safety(self, current_pos=None):
        return self._emergency.check_safety(current_pos)

    # ------------------ Virtual Mode ------------------
    def set_virtual_mode(self, enabled: bool):
        return set_virtual_mode(enabled)

    def is_virtual_mode(self):
        return is_virtual_mode()

    # ------------------ Cursor & Mouse Movement ------------------
    def get_cursor_position(self):
        return get_cursor_position()

    def move_cursor(self, x, y, smooth=True, steps=12):
        return move_cursor(x, y, smooth=smooth, steps=steps)

    def move_relative(self, dx, dy, smooth=False, steps=6):
        return move_relative(dx, dy, smooth=smooth, steps=steps)

    def move_bezier(self, target_x, target_y, steps=20, deviation=0.15):
        return move_bezier(target_x, target_y, steps=steps, deviation=deviation)

    # ------------------ Mouse Clicks ------------------
    def click(self, x=None, y=None, button="left", clicks=1):
        return click(x=x, y=y, button=button, clicks=clicks)

    def right_click(self, x=None, y=None):
        return right_click(x=x, y=y)

    def double_click(self, x=None, y=None):
        return double_click(x=x, y=y)

    def triple_click(self, x=None, y=None):
        return triple_click(x=x, y=y)

    def middle_click(self, x=None, y=None):
        return middle_click(x=x, y=y)

    def mouse_down(self, button="left"):
        return mouse_down(button)

    def mouse_up(self, button="left"):
        return mouse_up(button)

    # ------------------ Scrolling & Dragging ------------------
    def scroll(self, delta=120, direction="up"):
        return scroll(delta=delta, direction=direction)

    def scroll_horizontal(self, delta=120, direction="right"):
        return scroll_horizontal(delta=delta, direction=direction)

    def drag_to(self, target_x, target_y):
        return drag_to(target_x, target_y)

    def drag_and_drop(self, start_x, start_y, end_x, end_y, steps=20):
        return drag_and_drop(start_x, start_y, end_x, end_y, steps=steps)

    # ------------------ Keyboard Synthesizer ------------------
    def type_text(self, text, delay=0.015):
        self._emergency.check_safety()
        return type_text(text, delay=delay)

    def press_key(self, key_name):
        self._emergency.check_safety()
        return press_key(key_name)

    def press_hotkey(self, *keys):
        self._emergency.check_safety()
        return press_hotkey(*keys)

    # ------------------ Window Orchestration ------------------
    def list_windows(self):
        return list_windows()

    def get_active_window(self):
        return get_active_window()

    def find_window(self, identifier):
        return find_window(identifier)

    def focus_window(self, identifier):
        return focus_window(identifier)

    def minimize_window(self, identifier):
        return minimize_window(identifier)

    def maximize_window(self, identifier):
        return maximize_window(identifier)

    def restore_window(self, identifier):
        return restore_window(identifier)

    def close_window(self, identifier):
        return close_window(identifier)

    def move_resize_window(self, identifier, x, y, width, height):
        return move_resize_window(identifier, x, y, width, height)

    def snap_window(self, identifier, position="left"):
        return snap_window(identifier, position=position)

    def tile_windows(self, identifiers, layout="split_horizontal"):
        return tile_windows(identifiers, layout=layout)

    def cascade_windows(self, identifiers=None):
        return cascade_windows(identifiers=identifiers)

    def launch_application(self, target, args=None):
        return launch_application(target, args=args)

    def is_window_hung(self, identifier):
        return is_window_hung(identifier)

    def get_screen_geometry(self):
        return get_screen_geometry()

    # ------------------ State Telemetry ------------------
    def get_desktop_state(self):
        """Returns consolidated desktop status telemetry."""
        cur_x, cur_y = get_cursor_position()
        return {
            "cursor": {"x": cur_x, "y": cur_y},
            "active_window": get_active_window(),
            "is_stopped": self.is_stopped(),
            "is_paused": self.is_paused(),
            "virtual_mode": is_virtual_mode(),
            "geometry": get_screen_geometry(),
        }


# Singleton engine instance
interaction_engine = DesktopInteractionEngine()
