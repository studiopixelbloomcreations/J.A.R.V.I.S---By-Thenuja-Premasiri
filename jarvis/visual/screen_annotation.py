"""
Screen Annotation Engine (Capability 132)
Non-destructive visual overlays on screen captures and diagrams:
Bounding boxes, numbered step markers, directional arrows, spotlight masks,
redaction/blur zones, reticle crosshairs, and SVG overlay layers.
"""

import io
import time
import math
import base64
from typing import List, Dict, Any, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFilter, ImageFont


class ScreenAnnotationEngine:
    """
    Renders rich non-destructive annotations onto images and generates standalone SVG overlay layers.
    """

    CYAN_ACCENT = "#00e5ff"
    DARK_BADGE = (15, 23, 42, 230)

    def __init__(self, base_image: Optional[Union[str, Image.Image]] = None, width: int = 1920, height: int = 1080):
        if isinstance(base_image, str):
            self.image = Image.open(base_image).convert("RGBA")
            self.width, self.height = self.image.size
        elif isinstance(base_image, Image.Image):
            self.image = base_image.convert("RGBA")
            self.width, self.height = self.image.size
        else:
            self.width = width
            self.height = height
            self.image = Image.new("RGBA", (width, height), (6, 19, 37, 255))

        self.elements: List[Dict[str, Any]] = []

    def add_box(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str = "",
        color_hex: str = "#00e5ff",
        stroke_width: int = 3,
        fill_alpha: int = 40,
    ) -> "ScreenAnnotationEngine":
        self.elements.append({
            "type": "box",
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "label": label,
            "color": color_hex,
            "stroke_width": stroke_width,
            "fill_alpha": fill_alpha,
        })
        return self

    def add_arrow(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        color_hex: str = "#00e5ff",
        width: int = 4,
        curved: bool = False,
    ) -> "ScreenAnnotationEngine":
        self.elements.append({
            "type": "arrow",
            "from_x": from_x,
            "from_y": from_y,
            "to_x": to_x,
            "to_y": to_y,
            "color": color_hex,
            "width": width,
            "curved": curved,
        })
        return self

    def add_step_marker(
        self,
        x: int,
        y: int,
        step_num: int = 1,
        text: str = "",
        color_hex: str = "#00e5ff",
        radius: int = 16,
    ) -> "ScreenAnnotationEngine":
        self.elements.append({
            "type": "step",
            "x": x,
            "y": y,
            "step_num": step_num,
            "text": text,
            "color": color_hex,
            "radius": radius,
        })
        return self

    def add_spotlight(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        dim_alpha: int = 160,
    ) -> "ScreenAnnotationEngine":
        """
        Dims the entire screen except for the illuminated focus box.
        """
        self.elements.append({
            "type": "spotlight",
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "dim_alpha": dim_alpha,
        })
        return self

    def add_redaction(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        style: str = "blur",  # 'blur' or 'blackout'
        blur_radius: int = 12,
    ) -> "ScreenAnnotationEngine":
        self.elements.append({
            "type": "redaction",
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "style": style,
            "blur_radius": blur_radius,
        })
        return self

    def add_crosshair(
        self,
        x: int,
        y: int,
        radius: int = 28,
        label: str = "",
        color_hex: str = "#00e5ff",
    ) -> "ScreenAnnotationEngine":
        self.elements.append({
            "type": "crosshair",
            "x": x,
            "y": y,
            "radius": radius,
            "label": label,
            "color": color_hex,
        })
        return self

    def render_pil(self) -> Image.Image:
        """
        Renders all annotation elements onto a composite copy of the base image.
        """
        canvas = self.image.copy()

        # Step 1: Apply Redactions directly onto canvas
        for el in self.elements:
            if el["type"] == "redaction":
                rx, ry, rw, rh = el["x"], el["y"], el["w"], el["h"]
                rx = max(0, min(self.width, rx))
                ry = max(0, min(self.height, ry))
                rw = max(1, min(self.width - rx, rw))
                rh = max(1, min(self.height - ry, rh))
                crop_box = (rx, ry, rx + rw, ry + rh)

                if el["style"] == "blackout":
                    draw_c = ImageDraw.Draw(canvas)
                    draw_c.rectangle(crop_box, fill=(0, 0, 0, 255))
                else:  # blur
                    region = canvas.crop(crop_box)
                    blurred = region.filter(ImageFilter.GaussianBlur(radius=el.get("blur_radius", 12)))
                    canvas.paste(blurred, crop_box)

        # Step 2: Overlay layer for transparent strokes, spotlights, and badges
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Handle spotlight dimming first
        for el in self.elements:
            if el["type"] == "spotlight":
                dim_alpha = el.get("dim_alpha", 160)
                dim_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, dim_alpha))
                # Clear spotlight area
                dim_draw = ImageDraw.Draw(dim_layer)
                sx, sy, sw, sh = el["x"], el["y"], el["w"], el["h"]
                dim_draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(0, 0, 0, 0))
                overlay = Image.alpha_composite(overlay, dim_layer)
                draw = ImageDraw.Draw(overlay)

        # Handle geometry elements
        for el in self.elements:
            el_type = el["type"]
            hex_color = el.get("color", self.CYAN_ACCENT)

            # Hex to RGB
            if hex_color.startswith("#") and len(hex_color) == 7:
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
            else:
                r, g, b = 0, 229, 255

            if el_type == "box":
                bx, by, bw, bh = el["x"], el["y"], el["w"], el["h"]
                sw = el.get("stroke_width", 3)
                fa = el.get("fill_alpha", 40)
                draw.rectangle([bx, by, bx + bw, by + bh], fill=(r, g, b, fa), outline=(r, g, b, 230), width=sw)
                label = el.get("label", "")
                if label:
                    badge_w = len(label) * 8 + 14
                    draw.rectangle([bx, by - 22, bx + badge_w, by], fill=self.DARK_BADGE, outline=(r, g, b, 200))
                    draw.text((bx + 6, by - 18), label, fill=(255, 255, 255, 255))

            elif el_type == "arrow":
                fx, fy = el["from_x"], el["from_y"]
                tx, ty = el["to_x"], el["to_y"]
                w_px = el.get("width", 4)
                draw.line([fx, fy, tx, ty], fill=(r, g, b, 240), width=w_px)

                # Draw arrowhead
                ang = math.atan2(ty - fy, tx - fx)
                head_len = 14
                arrow_p1 = (tx - head_len * math.cos(ang - math.pi / 6), ty - head_len * math.sin(ang - math.pi / 6))
                arrow_p2 = (tx - head_len * math.cos(ang + math.pi / 6), ty - head_len * math.sin(ang + math.pi / 6))
                draw.polygon([(tx, ty), arrow_p1, arrow_p2], fill=(r, g, b, 255))

            elif el_type == "step":
                sx, sy = el["x"], el["y"]
                snum = str(el.get("step_num", 1))
                stext = el.get("text", "")
                rad = el.get("radius", 16)

                draw.ellipse([sx - rad, sy - rad, sx + rad, sy + rad], fill=(r, g, b, 240), outline=(255, 255, 255, 255), width=2)
                draw.text((sx - 5, sy - 8), snum, fill=(10, 15, 30, 255))
                if stext:
                    t_width = len(stext) * 8 + 16
                    draw.rectangle([sx + rad + 6, sy - 12, sx + rad + 6 + t_width, sy + 14], fill=self.DARK_BADGE, outline=(r, g, b, 200))
                    draw.text((sx + rad + 12, sy - 8), stext, fill=(255, 255, 255, 255))

            elif el_type == "crosshair":
                cx, cy = el["x"], el["y"]
                crad = el.get("radius", 28)
                clabel = el.get("label", f"{cx},{cy}")
                draw.ellipse([cx - crad, cy - crad, cx + crad, cy + crad], outline=(r, g, b, 200), width=1)
                draw.line([cx - crad - 6, cy, cx + crad + 6, cy], fill=(r, g, b, 230), width=1)
                draw.line([cx, cy - crad - 6, cx, cy + crad + 6], fill=(r, g, b, 230), width=1)
                if clabel:
                    draw.text((cx + crad + 4, cy - 8), clabel, fill=(r, g, b, 255))

        # Alpha composite
        final_img = Image.alpha_composite(canvas, overlay).convert("RGB")
        return final_img

    def render_to_base64(self, quality: int = 90) -> str:
        """
        Renders image to base64 JPEG data URI.
        """
        pil_img = self.render_pil()
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=quality)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"

    def render_svg_overlay(self) -> str:
        """
        Generates a standalone transparent SVG overlay layer for web embedding.
        """
        items_svg = ""
        for el in self.elements:
            etype = el["type"]
            color = el.get("color", self.CYAN_ACCENT)

            if etype == "box":
                items_svg += f"""
                <rect x="{el['x']}" y="{el['y']}" width="{el['w']}" height="{el['h']}" fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-width="{el.get('stroke_width', 2)}"/>
                <text x="{el['x'] + 6}" y="{el['y'] - 6}" fill="{color}" font-family="monospace" font-size="11" font-weight="bold">{el.get('label', '')}</text>
                """
            elif etype == "arrow":
                items_svg += f"""
                <line x1="{el['from_x']}" y1="{el['from_y']}" x2="{el['to_x']}" y2="{el['to_y']}" stroke="{color}" stroke-width="{el.get('width', 3)}" marker-end="url(#svgArrow)"/>
                """
            elif etype == "step":
                items_svg += f"""
                <circle cx="{el['x']}" cy="{el['y']}" r="{el.get('radius', 16)}" fill="{color}" stroke="#ffffff" stroke-width="2"/>
                <text x="{el['x']}" y="{el['y'] + 4}" fill="#040d1a" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">{el.get('step_num', 1)}</text>
                <text x="{el['x'] + 24}" y="{el['y'] + 4}" fill="#ffffff" font-family="sans-serif" font-size="11">{el.get('text', '')}</text>
                """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">
    <defs>
        <marker id="svgArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 8 5 L 0 9 z" fill="{self.CYAN_ACCENT}"/>
        </marker>
    </defs>
    {items_svg}
</svg>"""
        return svg
