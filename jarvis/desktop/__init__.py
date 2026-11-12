"""
J.A.R.V.I.S. Desktop & OS Automation Subsystem (Capabilities 16-30).
Provides native and virtual desktop control, mouse/cursor dynamics, keyboard synthesis,
window orchestration, emergency stop fail-safes, and comprehensive OS intelligence.
"""

from .emergency import (
    emergency,
    EmergencyController,
    EmergencyStopError,
)

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

from .keyboard import (
    press_key,
    press_hotkey,
    type_text,
)

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
    launch_application,
    list_running_processes,
    get_screen_geometry,
    get_system_diagnostics,
    is_window_hung,
    send_whatsapp_message,
    control_volume,
    control_media,
    lock_workstation,
    show_desktop,
    get_battery_status,
    get_weather_telemetry,
)

from .interaction_engine import (
    DesktopInteractionEngine,
    interaction_engine,
)

# Capabilities 16-30
from .desktop_vision import desktop_vision, DesktopVision
from .ui_element import ui_recognizer, UIElementRecognizer, UIElement
from .app_intelligence import app_intelligence, ApplicationIntelligence
from .orchestration import window_orchestrator, WindowOrchestrator
from .file_intelligence import file_intelligence, FileIntelligence
from .troubleshooting import troubleshooter, AutomatedTroubleshooter
from .hardware import hardware_monitor, HardwareMonitor
from .diagnostics import app_diagnostics, ApplicationDiagnostics
from .environment import env_config, EnvironmentConfiguration
from .workflow import workflow_engine, WorkflowEngine
from .state_memory import desktop_state_memory, DesktopStateMemory
from .visual_guidance import visual_guidance, VisualGuidance
from .app_learning import app_learning, ApplicationLearningEngine
from .backup import backup_intelligence, LocalBackupIntelligence
from .health import system_health_reporter, SystemHealthReporter

__all__ = [
    # Subsystems
    "emergency",
    "EmergencyController",
    "EmergencyStopError",
    "interaction_engine",
    "DesktopInteractionEngine",
    # Mouse
    "get_cursor_position",
    "move_cursor",
    "move_relative",
    "move_bezier",
    "click",
    "right_click",
    "double_click",
    "triple_click",
    "middle_click",
    "mouse_down",
    "mouse_up",
    "scroll",
    "scroll_horizontal",
    "drag_to",
    "drag_and_drop",
    "set_virtual_mode",
    "is_virtual_mode",
    # Keyboard
    "press_key",
    "press_hotkey",
    "type_text",
    # Windows
    "list_windows",
    "get_active_window",
    "find_window",
    "focus_window",
    "minimize_window",
    "maximize_window",
    "restore_window",
    "close_window",
    "move_resize_window",
    "snap_window",
    "tile_windows",
    "cascade_windows",
    "launch_application",
    "list_running_processes",
    "get_screen_geometry",
    "get_system_diagnostics",
    "is_window_hung",
    "send_whatsapp_message",
    "control_volume",
    "control_media",
    "lock_workstation",
    "show_desktop",
    "get_battery_status",
    "get_weather_telemetry",
    # Capabilities 16-30
    "desktop_vision",
    "DesktopVision",
    "ui_recognizer",
    "UIElementRecognizer",
    "UIElement",
    "app_intelligence",
    "ApplicationIntelligence",
    "window_orchestrator",
    "WindowOrchestrator",
    "file_intelligence",
    "FileIntelligence",
    "troubleshooter",
    "AutomatedTroubleshooter",
    "hardware_monitor",
    "HardwareMonitor",
    "app_diagnostics",
    "ApplicationDiagnostics",
    "env_config",
    "EnvironmentConfiguration",
    "workflow_engine",
    "WorkflowEngine",
    "desktop_state_memory",
    "DesktopStateMemory",
    "visual_guidance",
    "VisualGuidance",
    "app_learning",
    "ApplicationLearningEngine",
    "backup_intelligence",
    "LocalBackupIntelligence",
    "system_health_reporter",
    "SystemHealthReporter",
]
