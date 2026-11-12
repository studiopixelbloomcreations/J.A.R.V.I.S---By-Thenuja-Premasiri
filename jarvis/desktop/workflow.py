"""
Capability 25: Workflow Automation Subsystem for J.A.R.V.I.S.
Executes multi-step scripted desktop macros and sequences with step-by-step
telemetry, pause/resume coordination, and emergency stop abort protection.
"""
import time
import logging
from typing import List, Dict, Any, Optional
from .emergency import emergency, EmergencyStopError
from .mouse import (
    move_cursor,
    click,
    double_click,
    right_click,
    drag_and_drop,
    scroll,
)
from .keyboard import type_text, press_key, press_hotkey
from .windows import (
    find_window,
    focus_window,
    minimize_window,
    maximize_window,
    snap_window,
    launch_application,
)

logger = logging.getLogger("jarvis.desktop.workflow")


class WorkflowAction:
    def __init__(self, action_type: str, params: Dict[str, Any]):
        self.action_type = action_type
        self.params = params

    def to_dict(self):
        return {"action": self.action_type, "params": self.params}


class WorkflowEngine:
    """Compiles and executes automated desktop task workflows."""

    def __init__(self):
        self._emergency = emergency

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a single workflow step with safety checks."""
        self._emergency.check_safety()
        act = step.get("action", "").lower().strip()
        params = step.get("params", {})
        start_t = time.perf_counter()

        if act == "move":
            res = move_cursor(params.get("x", 0), params.get("y", 0), smooth=params.get("smooth", True))
        elif act == "click":
            res = click(params.get("x"), params.get("y"), button=params.get("button", "left"), clicks=params.get("clicks", 1))
        elif act == "double_click":
            res = double_click(params.get("x"), params.get("y"))
        elif act == "right_click":
            res = right_click(params.get("x"), params.get("y"))
        elif act == "drag":
            res = drag_and_drop(
                params.get("from_x", 0),
                params.get("from_y", 0),
                params.get("to_x", 100),
                params.get("to_y", 100),
            )
        elif act == "scroll":
            res = scroll(delta=params.get("delta", 120), direction=params.get("direction", "up"))
        elif act == "type":
            res = type_text(params.get("text", ""), delay=params.get("delay", 0.015))
        elif act == "hotkey":
            keys = params.get("keys", [])
            res = press_hotkey(*keys)
        elif act == "press_key":
            res = press_key(params.get("key", "enter"))
        elif act == "wait":
            sec = min(10.0, float(params.get("seconds", 0.5)))
            time.sleep(sec)
            res = {"status": "success", "waited": sec}
        elif act == "launch":
            res = launch_application(params.get("target", ""), args=params.get("args"))
        elif act == "focus":
            res = focus_window(params.get("target"))
        elif act == "snap":
            res = snap_window(params.get("target"), position=params.get("position", "left"))
        else:
            return {"status": "error", "message": f"Unsupported action: {act}"}

        elapsed = round((time.perf_counter() - start_t) * 1000, 2)
        return {"step": act, "duration_ms": elapsed, "result": res}

    def run_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes an ordered list of workflow steps sequentially.
        Stops immediately if emergency stop is triggered.
        """
        self._emergency.check_safety()
        logs = []
        overall_start = time.perf_counter()

        for idx, step in enumerate(steps):
            try:
                self._emergency.check_safety()
                step_result = self.execute_step(step)
                logs.append({"step_index": idx + 1, "step": step, "output": step_result})
            except EmergencyStopError as ese:
                logger.warning(f"Workflow '{workflow_name}' aborted at step {idx + 1}: {ese}")
                return {
                    "status": "aborted",
                    "reason": str(ese),
                    "completed_steps": idx,
                    "total_steps": len(steps),
                    "logs": logs,
                }
            except Exception as e:
                logger.error(f"Error in step {idx + 1}: {e}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "failed_step_index": idx + 1,
                    "completed_steps": idx,
                    "total_steps": len(steps),
                    "logs": logs,
                }

        total_elapsed = round(time.perf_counter() - overall_start, 3)
        return {
            "status": "success",
            "workflow_name": workflow_name,
            "steps_count": len(steps),
            "duration_seconds": total_elapsed,
            "logs": logs,
        }


workflow_engine = WorkflowEngine()
