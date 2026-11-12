"""
Emergency Stop and Safety Subsystem for J.A.R.V.I.S. Desktop Engine.
Provides thread-safe emergency abort, pause/resume mechanisms, and fail-safe triggers.
"""
import time
import logging
import threading
import ctypes

logger = logging.getLogger("jarvis.desktop.emergency")

user32 = ctypes.windll.user32

MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTUP = 0x0009
MOUSEEVENTF_MIDDLEUP = 0x0040
KEYEVENTF_KEYUP = 0x0002

# Common modifiers to release on abort
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12  # Alt
VK_LWIN = 0x5B


class EmergencyStopError(Exception):
    """Raised when an operation is cancelled due to emergency stop."""
    pass


class EmergencyController:
    """Thread-safe controller managing desktop automation safety, pauses, and emergency stops."""

    def __init__(self, enable_corner_failsafe=False):
        self._lock = threading.RLock()
        self._is_stopped = False
        self._is_paused = False
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused initially
        self.enable_corner_failsafe = enable_corner_failsafe
        self.stop_reason = None
        self.last_stopped_at = None
        self.stop_history = []

    @property
    def is_stopped(self):
        with self._lock:
            return self._is_stopped

    @property
    def is_paused(self):
        with self._lock:
            return self._is_paused

    def trigger_emergency_stop(self, reason="Manual emergency stop"):
        """
        Immediately stops desktop automation, releases held mouse buttons and keys,
        and halts pending movements.
        """
        with self._lock:
            self._is_stopped = True
            self._is_paused = False
            self.stop_reason = str(reason)
            self.last_stopped_at = time.time()
            self._pause_event.set()  # Unblock any paused thread so it can abort

            # Safety release of Win32 hardware states
            try:
                user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                user32.mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
                user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
                user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
                user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
                user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
            except Exception as e:
                logger.warning(f"Failed to release hardware state during emergency stop: {e}")

            record = {
                "timestamp": self.last_stopped_at,
                "reason": self.stop_reason
            }
            self.stop_history.append(record)
            logger.warning(f"EMERGENCY STOP ACTIVATED: {reason}")
            return {"status": "emergency_stop", "reason": self.stop_reason, "timestamp": self.last_stopped_at}

    def pause(self, reason="User requested pause"):
        """Pauses active desktop operations without aborting."""
        with self._lock:
            if self._is_stopped:
                return {"status": "error", "message": "Cannot pause while in emergency stop"}
            self._is_paused = True
            self._pause_event.clear()
            logger.info(f"Desktop interaction PAUSED: {reason}")
            return {"status": "paused", "reason": reason}

    def resume(self):
        """Resumes paused operations."""
        with self._lock:
            if self._is_stopped:
                return {"status": "error", "message": "Cannot resume: emergency stop is active. Reset first."}
            self._is_paused = False
            self._pause_event.set()
            logger.info("Desktop interaction RESUMED")
            return {"status": "running"}

    def reset(self):
        """Resets the emergency stop and pause states back to normal operational state."""
        with self._lock:
            self._is_stopped = False
            self._is_paused = False
            self.stop_reason = None
            self._pause_event.set()
            logger.info("Desktop emergency controller RESET")
            return {"status": "reset", "is_stopped": False, "is_paused": False}

    def check_safety(self, current_pos=None):
        """
        Validates safety invariants. If stopped, raises EmergencyStopError.
        If paused, blocks until resumed or stopped.
        If corner fail-safe is enabled and cursor is at (0,0), triggers emergency stop.
        """
        # Corner fail-safe check
        if self.enable_corner_failsafe:
            if current_pos is not None:
                cx, cy = current_pos
                if cx <= 1 and cy <= 1:
                    self.trigger_emergency_stop("Fail-safe: Mouse slammed into upper-left corner (0,0)")
                    raise EmergencyStopError(self.stop_reason)

        if self.is_stopped:
            raise EmergencyStopError(self.stop_reason or "Emergency stop active")

        # Wait if paused
        if self.is_paused:
            self._pause_event.wait()
            if self.is_stopped:
                raise EmergencyStopError(self.stop_reason or "Emergency stop activated during pause")

        return True


# Global singleton instance
emergency = EmergencyController()
