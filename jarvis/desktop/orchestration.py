"""
Capability 19: Window Orchestration Subsystem for J.A.R.V.I.S.
Provides advanced multi-window layouts, quadrant snapping, grid tiling,
and presentation/workspace arrangement orchestrations.
"""
from typing import List, Dict, Any, Optional
from .windows import (
    list_windows,
    find_window,
    move_resize_window,
    get_screen_geometry,
    focus_window,
    minimize_window,
    maximize_window,
    restore_window,
)


class WindowOrchestrator:
    """Orchestrates complex multi-window desktop layouts and arrangements."""

    def __init__(self):
        self._saved_layouts: Dict[str, List[Dict[str, Any]]] = {}

    def apply_layout_preset(self, preset: str, window_identifiers: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Applies a predefined multi-window arrangement:
        'split_columns', 'split_rows', 'grid_2x2', 'coding_workspace', 'reading_workspace'.
        """
        hwnds = []
        if window_identifiers:
            for ident in window_identifiers:
                h = find_window(ident)
                if h:
                    hwnds.append(h)
        else:
            wins = list_windows()
            hwnds = [w["hwnd"] for w in wins[:4]]

        if not hwnds:
            return {"status": "error", "message": "No windows available to arrange"}

        geo = get_screen_geometry()
        sw = geo["primary"]["width"]
        sh = max(100, geo["primary"]["height"] - 40)

        results = []

        if preset == "split_columns":
            w_col = sw // len(hwnds)
            for idx, h in enumerate(hwnds):
                res = move_resize_window(h, idx * w_col, 0, w_col, sh)
                results.append(res)

        elif preset == "split_rows":
            h_row = sh // len(hwnds)
            for idx, h in enumerate(hwnds):
                res = move_resize_window(h, 0, idx * h_row, sw, h_row)
                results.append(res)

        elif preset == "grid_2x2":
            w_cell = sw // 2
            h_cell = sh // 2
            positions = [
                (0, 0),
                (w_cell, 0),
                (0, h_cell),
                (w_cell, h_cell),
            ]
            for idx, h in enumerate(hwnds[:4]):
                gx, gy = positions[idx]
                res = move_resize_window(h, gx, gy, w_cell, h_cell)
                results.append(res)

        elif preset == "coding_workspace":
            # Primary editor takes 68% left, secondary takes 32% right
            if len(hwnds) >= 1:
                w_main = int(sw * 0.68)
                results.append(move_resize_window(hwnds[0], 0, 0, w_main, sh))
            if len(hwnds) >= 2:
                w_side = sw - int(sw * 0.68)
                results.append(move_resize_window(hwnds[1], int(sw * 0.68), 0, w_side, sh))

        elif preset == "reading_workspace":
            # 50/50 split centered
            w_half = sw // 2
            if len(hwnds) >= 1:
                results.append(move_resize_window(hwnds[0], 0, 0, w_half, sh))
            if len(hwnds) >= 2:
                results.append(move_resize_window(hwnds[1], w_half, 0, w_half, sh))

        else:
            return {"status": "error", "message": f"Unknown preset: {preset}"}

        return {
            "status": "success",
            "preset": preset,
            "arranged_count": len(results),
            "windows": results
        }

    def snap_to_quadrant(self, window_identifier: Any, quadrant: str) -> Dict[str, Any]:
        """
        Snaps window to specified screen quadrant:
        'top_left', 'top_right', 'bottom_left', 'bottom_right'.
        """
        hwnd = find_window(window_identifier)
        if not hwnd:
            return {"status": "error", "message": f"Window not found: {window_identifier}"}

        geo = get_screen_geometry()
        sw = geo["primary"]["width"]
        sh = max(100, geo["primary"]["height"] - 40)
        qw, qh = sw // 2, sh // 2

        mapping = {
            "top_left": (0, 0),
            "top_right": (qw, 0),
            "bottom_left": (0, qh),
            "bottom_right": (qw, qh),
        }
        coords = mapping.get(quadrant.lower().replace("-", "_"))
        if not coords:
            return {"status": "error", "message": f"Invalid quadrant: {quadrant}"}

        qx, qy = coords
        return move_resize_window(hwnd, qx, qy, qw, qh)

    def save_layout(self, layout_name: str) -> Dict[str, Any]:
        """Saves current geometry of all visible windows under a named preset."""
        wins = list_windows()
        layout_data = []
        for w in wins:
            layout_data.append({
                "hwnd": w["hwnd"],
                "title": w["title"],
                "x": w["x"],
                "y": w["y"],
                "width": w["width"],
                "height": w["height"],
            })
        self._saved_layouts[layout_name] = layout_data
        return {"status": "success", "layout_name": layout_name, "window_count": len(layout_data)}

    def restore_layout(self, layout_name: str) -> Dict[str, Any]:
        """Restores window geometries from a previously saved layout."""
        if layout_name not in self._saved_layouts:
            return {"status": "error", "message": f"Saved layout '{layout_name}' not found"}

        restored = []
        for item in self._saved_layouts[layout_name]:
            res = move_resize_window(item["hwnd"], item["x"], item["y"], item["width"], item["height"])
            if res.get("status") == "success":
                restored.append(item["title"])

        return {"status": "success", "layout_name": layout_name, "restored_windows": restored}


window_orchestrator = WindowOrchestrator()
