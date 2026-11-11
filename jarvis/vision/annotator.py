"""
Non-Destructive Screen Annotation Engine for J.A.R.V.I.S.
Renders highlights, pointers, arrows, and step markers on screenshots.
"""
import io
import time
import base64
from PIL import Image, ImageDraw, ImageFont
from ..config import SCREENSHOTS_DIR


def annotate_screenshot(source_path, annotations):
    """
    Renders non-destructive annotations onto a copy of the source screenshot.
    annotations is a list of dicts:
    - {'type': 'box', 'x': int, 'y': int, 'w': int, 'h': int, 'color': '#06b6d4', 'label': 'Click here'}
    - {'type': 'step', 'x': int, 'y': int, 'step_num': 1, 'text': 'Open Settings'}
    - {'type': 'arrow', 'from_x': int, 'from_y': int, 'to_x': int, 'to_y': int, 'color': '#38bdf8'}

    Returns dict with annotated image path and base64.
    """
    try:
        orig = Image.open(source_path).convert("RGBA")
        overlay = Image.new("RGBA", orig.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        for ann in annotations:
            ann_type = ann.get("type", "box")
            color_hex = ann.get("color", "#06b6d4")

            # Convert hex to RGBA
            if color_hex.startswith("#") and len(color_hex) == 7:
                r = int(color_hex[1:3], 16)
                g = int(color_hex[3:5], 16)
                b = int(color_hex[5:7], 16)
                stroke_color = (r, g, b, 230)
                fill_color = (r, g, b, 45)
            else:
                stroke_color = (6, 182, 212, 230)
                fill_color = (6, 182, 212, 45)

            if ann_type == "box":
                x = ann.get("x", 0)
                y = ann.get("y", 0)
                w = ann.get("w", 100)
                h = ann.get("h", 40)
                # Outer glow effect & main box
                draw.rectangle([x - 2, y - 2, x + w + 2, y + h + 2], outline=stroke_color, width=3)
                draw.rectangle([x, y, x + w, y + h], fill=fill_color)

                label = ann.get("label", "")
                if label:
                    # Draw label badge above box
                    draw.rectangle([x, y - 24, x + len(label) * 8 + 12, y - 2], fill=(15, 23, 42, 220), outline=stroke_color)
                    draw.text((x + 6, y - 20), label, fill=(255, 255, 255, 255))

            elif ann_type == "step":
                x = ann.get("x", 0)
                y = ann.get("y", 0)
                step_num = str(ann.get("step_num", 1))
                text = ann.get("text", "")
                radius = 16

                # Outer glowing circle
                draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(14, 165, 233, 240), outline=(255, 255, 255, 255), width=2)
                draw.text((x - 4, y - 7), step_num, fill=(255, 255, 255, 255))
                if text:
                    draw.rectangle([x + radius + 4, y - 12, x + radius + len(text) * 8 + 16, y + 14], fill=(15, 23, 42, 220), outline=stroke_color)
                    draw.text((x + radius + 10, y - 8), text, fill=(255, 255, 255, 255))

            elif ann_type == "arrow":
                fx = ann.get("from_x", 0)
                fy = ann.get("from_y", 0)
                tx = ann.get("to_x", 0)
                ty = ann.get("to_y", 0)
                draw.line([fx, fy, tx, ty], fill=stroke_color, width=4)
                # Arrowhead circle
                draw.ellipse([tx - 6, ty - 6, tx + 6, ty + 6], fill=stroke_color)

        combined = Image.alpha_composite(orig, overlay).convert("RGB")
        ts = int(time.time() * 1000)
        ann_filename = f"annotated_{ts}.jpg"
        ann_path = SCREENSHOTS_DIR / ann_filename
        combined.save(ann_path, format="JPEG", quality=90)

        buffer = io.BytesIO()
        combined.save(buffer, format="JPEG", quality=85)
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "status": "success",
            "file_path": str(ann_path),
            "filename": ann_filename,
            "base64": f"data:image/jpeg;base64,{b64}",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
