"""
Capability 27: Visual Guidance Subsystem for J.A.R.V.I.S.
Generates HUD visual annotations, neon cyan bounding boxes, directional arrows,
numbered step badges, reticles, and composites step-by-step walkthrough guides.
"""
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont


class VisualGuidance:
    """Generates visual overlay annotations and HUD telemetry for user walkthroughs."""

    CYAN = (0, 229, 255)
    EMERALD = (16, 185, 129)
    AMBER = (245, 158, 11)
    ROSE = (244, 63, 94)

    def __init__(self):
        self._active_overlays: List[Dict[str, Any]] = []

    def create_bounding_box(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        color: str = "#00e5ff",
        glow: bool = True,
    ) -> Dict[str, Any]:
        """Creates a HUD bounding box metadata structure with header tab."""
        box = {
            "type": "bounding_box",
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
            "label": str(label).upper(),
            "color": color,
            "glow": glow,
            "center": (int(x + width / 2), int(y + height / 2)),
        }
        self._active_overlays.append(box)
        return box

    def create_arrow(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        label: Optional[str] = None,
        color: str = "#00e5ff",
    ) -> Dict[str, Any]:
        """Creates a directional arrow vector pointing to a control."""
        arrow = {
            "type": "arrow",
            "start": (int(start_x), int(start_y)),
            "end": (int(end_x), int(end_y)),
            "label": label,
            "color": color,
        }
        self._active_overlays.append(arrow)
        return arrow

    def create_step_badge(
        self,
        step_number: int,
        x: int,
        y: int,
        caption: str,
        color: str = "#00e5ff",
    ) -> Dict[str, Any]:
        """Creates a numbered step badge indicator."""
        badge = {
            "type": "step_badge",
            "step": step_number,
            "x": int(x),
            "y": int(y),
            "caption": caption,
            "color": color,
        }
        self._active_overlays.append(badge)
        return badge

    def clear_overlays(self):
        """Clears all active HUD guidance elements."""
        count = len(self._active_overlays)
        self._active_overlays.clear()
        return {"status": "success", "cleared_count": count}

    def get_active_overlays(self) -> List[Dict[str, Any]]:
        return list(self._active_overlays)

    def draw_overlays_on_image(self, base_image: Image.Image) -> Image.Image:
        """Draws all active bounding boxes, badges, and arrows onto a PIL Image."""
        img = base_image.copy().convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for item in self._active_overlays:
            itype = item.get("type")
            if itype == "bounding_box":
                x, y, w, h = item["x"], item["y"], item["width"], item["height"]
                # Box border
                draw.rectangle([x, y, x + w, y + h], outline=(*self.CYAN, 230), width=2)
                # Header tab
                draw.rectangle([x, max(0, y - 20), x + len(item["label"]) * 8 + 12, y], fill=(*self.CYAN, 240))
                draw.text((x + 4, max(0, y - 18)), item["label"], fill=(3, 7, 18, 255))

            elif itype == "step_badge":
                bx, by = item["x"], item["y"]
                r = 14
                draw.ellipse([bx - r, by - r, bx + r, by + r], fill=(*self.CYAN, 240), outline=(255, 255, 255, 255), width=2)
                draw.text((bx - 4, by - 7), str(item["step"]), fill=(3, 7, 18, 255))
                if item.get("caption"):
                    draw.rectangle([bx + r + 4, by - 10, bx + r + len(item["caption"]) * 7 + 10, by + 10], fill=(10, 16, 26, 200))
                    draw.text((bx + r + 8, by - 7), item["caption"], fill=(255, 255, 255, 255))

            elif itype == "arrow":
                sx, sy = item["start"]
                ex, ey = item["end"]
                draw.line([sx, sy, ex, ey], fill=(*self.CYAN, 230), width=3)
                # Arrow circle target
                draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(*self.CYAN, 255))

        return Image.alpha_composite(img, overlay).convert("RGB")


visual_guidance = VisualGuidance()
