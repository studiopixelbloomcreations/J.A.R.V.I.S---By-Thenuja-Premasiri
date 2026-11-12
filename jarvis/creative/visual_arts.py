"""
Graphic Design Assistance and Image Analysis Module for J.A.R.V.I.S.
Covers Capabilities:
  - 83. Graphic Design Assistance (Color palettes, contrast ratio, typography scales)
  - 84. Image Analysis (Composition, rule-of-thirds, lighting assessment)
"""

import math
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
from PIL import Image


class GraphicDesignAssistant:
    """Capability 83: Graphic Design Assistance"""

    TYPOGRAPHY_RATIOS = {
        "minor_second": 1.067,
        "major_second": 1.125,
        "minor_third": 1.200,
        "major_third": 1.250,
        "perfect_fourth": 1.333,
        "augmented_fourth": 1.414,
        "perfect_fifth": 1.500,
        "golden_ratio": 1.618
    }

    @staticmethod
    def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
        """Converts HEX string (#RRGGBB or RRGGBB) to (R, G, B) tuple 0-255."""
        h = hex_code.strip().lstrip("#")
        if len(h) == 3:
            h = "".join([c * 2 for c in h])
        if len(h) != 6:
            raise ValueError(f"Invalid hex color code: '{hex_code}'")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """Converts (R, G, B) tuple to uppercase HEX string #RRGGBB."""
        return f"#{max(0, min(255, int(round(r)))):02X}{max(0, min(255, int(round(g)))):02X}{max(0, min(255, int(round(b)))):02X}"

    @classmethod
    def rgb_to_hsl(cls, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Converts RGB (0-255) to HSL (H: 0-360, S: 0-1, L: 0-1)."""
        r_f = r / 255.0
        g_f = g / 255.0
        b_f = b / 255.0

        c_max = max(r_f, g_f, b_f)
        c_min = min(r_f, g_f, b_f)
        delta = c_max - c_min

        l = (c_max + c_min) / 2.0

        if delta == 0:
            h = 0.0
            s = 0.0
        else:
            s = delta / (1.0 - abs(2.0 * l - 1.0))
            if c_max == r_f:
                h = ((g_f - b_f) / delta) % 6.0
            elif c_max == g_f:
                h = ((b_f - r_f) / delta) + 2.0
            else:
                h = ((r_f - g_f) / delta) + 4.0
            h *= 60.0

        return (round(h, 2), round(s, 4), round(l, 4))

    @classmethod
    def hsl_to_rgb(cls, h: float, s: float, l: float) -> Tuple[int, int, int]:
        """Converts HSL (H: 0-360, S: 0-1, L: 0-1) to RGB (0-255)."""
        c = (1.0 - abs(2.0 * l - 1.0)) * s
        x = c * (1.0 - abs(((h / 60.0) % 2.0) - 1.0))
        m = l - (c / 2.0)

        if 0 <= h < 60:
            r_p, g_p, b_p = c, x, 0
        elif 60 <= h < 120:
            r_p, g_p, b_p = x, c, 0
        elif 120 <= h < 180:
            r_p, g_p, b_p = 0, c, x
        elif 180 <= h < 240:
            r_p, g_p, b_p = 0, x, c
        elif 240 <= h < 300:
            r_p, g_p, b_p = x, 0, c
        else:
            r_p, g_p, b_p = c, 0, x

        return (
            int(round((r_p + m) * 255.0)),
            int(round((g_p + m) * 255.0)),
            int(round((b_p + m) * 255.0))
        )

    @classmethod
    def calculate_relative_luminance(cls, hex_color: str) -> float:
        """
        Computes WCAG 2.1 relative luminance for a color.
        L = 0.2126 * R + 0.7152 * G + 0.0722 * B
        """
        r, g, b = cls.hex_to_rgb(hex_color)
        channels = []
        for c in (r, g, b):
            val = c / 255.0
            if val <= 0.04045:
                channels.append(val / 12.92)
            else:
                channels.append(((val + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    @classmethod
    def calculate_contrast_ratio(cls, hex_foreground: str, hex_background: str) -> Dict[str, Any]:
        """
        Computes WCAG 2.1 contrast ratio and accessibility compliance status.
        Ratio = (L1 + 0.05) / (L2 + 0.05) where L1 is the lighter luminance.
        """
        l1 = cls.calculate_relative_luminance(hex_foreground)
        l2 = cls.calculate_relative_luminance(hex_background)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        ratio = (lighter + 0.05) / (darker + 0.05)
        ratio_rounded = round(ratio, 2)

        return {
            "foreground": hex_foreground.upper(),
            "background": hex_background.upper(),
            "contrast_ratio": ratio_rounded,
            "ratio_string": f"{ratio_rounded}:1",
            "wcag_aa_normal_text": ratio >= 4.5,
            "wcag_aa_large_text": ratio >= 3.0,
            "wcag_aaa_normal_text": ratio >= 7.0,
            "wcag_aaa_large_text": ratio >= 4.5,
            "is_accessible": ratio >= 4.5
        }

    @classmethod
    def generate_color_palette(
        cls,
        base_hex: str,
        harmony_type: str = "analogous"
    ) -> Dict[str, Any]:
        """
        Generates color harmony palettes:
        'complementary', 'analogous', 'triadic', 'tetradic', 'monochromatic', 'split_complementary'.
        """
        r, g, b = cls.hex_to_rgb(base_hex)
        h, s, l = cls.rgb_to_hsl(r, g, b)

        palette = [{"role": "Base", "hex": cls.rgb_to_hex(r, g, b), "h": h, "s": s, "l": l}]

        harmony = harmony_type.lower()
        if harmony == "complementary":
            comp_h = (h + 180.0) % 360.0
            cr, cg, cb = cls.hsl_to_rgb(comp_h, s, l)
            palette.append({"role": "Complementary", "hex": cls.rgb_to_hex(cr, cg, cb), "h": comp_h, "s": s, "l": l})

        elif harmony == "analogous":
            for offset, label in [(-30.0, "Analogous Left"), (30.0, "Analogous Right"), (60.0, "Accent")]:
                nh = (h + offset) % 360.0
                nr, ng, nb = cls.hsl_to_rgb(nh, s, l)
                palette.append({"role": label, "hex": cls.rgb_to_hex(nr, ng, nb), "h": round(nh, 1), "s": s, "l": l})

        elif harmony == "triadic":
            for offset, label in [(120.0, "Triad 1"), (240.0, "Triad 2")]:
                nh = (h + offset) % 360.0
                nr, ng, nb = cls.hsl_to_rgb(nh, s, l)
                palette.append({"role": label, "hex": cls.rgb_to_hex(nr, ng, nb), "h": round(nh, 1), "s": s, "l": l})

        elif harmony == "tetradic":
            for offset, label in [(60.0, "Secondary"), (180.0, "Complementary"), (240.0, "Accent")]:
                nh = (h + offset) % 360.0
                nr, ng, nb = cls.hsl_to_rgb(nh, s, l)
                palette.append({"role": label, "hex": cls.rgb_to_hex(nr, ng, nb), "h": round(nh, 1), "s": s, "l": l})

        elif harmony == "split_complementary":
            for offset, label in [(150.0, "Split Left"), (210.0, "Split Right")]:
                nh = (h + offset) % 360.0
                nr, ng, nb = cls.hsl_to_rgb(nh, s, l)
                palette.append({"role": label, "hex": cls.rgb_to_hex(nr, ng, nb), "h": round(nh, 1), "s": s, "l": l})

        elif harmony == "monochromatic":
            for l_adj, label in [(0.2, "Tint (Light)"), (-0.2, "Shade (Dark)"), (0.4, "Highlight"), (-0.35, "Deep Shade")]:
                nl = max(0.05, min(0.95, l + l_adj))
                nr, ng, nb = cls.hsl_to_rgb(h, s, nl)
                palette.append({"role": label, "hex": cls.rgb_to_hex(nr, ng, nb), "h": h, "s": s, "l": round(nl, 2)})

        return {
            "base_color": base_hex.upper(),
            "harmony_type": harmony,
            "swatches": palette
        }

    @classmethod
    def generate_typography_scale(
        cls,
        base_size_px: float = 16.0,
        scale_ratio_name: str = "perfect_fourth"
    ) -> Dict[str, Any]:
        """
        Generates modular typography scale from Step -2 to Step +6.
        """
        ratio = cls.TYPOGRAPHY_RATIOS.get(scale_ratio_name.lower(), 1.333)

        steps = [
            (-2, "Caption / Legal", 400, 1.3),
            (-1, "Small / Secondary", 400, 1.4),
            (0, "Body / Base Paragraph", 400, 1.5),
            (1, "Lead / Subheading", 500, 1.4),
            (2, "H4 Section Title", 600, 1.3),
            (3, "H3 Card Header", 600, 1.25),
            (4, "H2 Major Heading", 700, 1.2),
            (5, "H1 Main Title", 700, 1.15),
            (6, "Display / Hero Banner", 800, 1.1)
        ]

        scale = []
        for step, label, weight, line_h in steps:
            size_px = base_size_px * (ratio ** step)
            rem = size_px / base_size_px
            scale.append({
                "step": step,
                "label": label,
                "font_size_px": round(size_px, 1),
                "font_size_rem": round(rem, 3),
                "font_weight": weight,
                "line_height": line_h
            })

        return {
            "base_size_px": base_size_px,
            "scale_ratio_name": scale_ratio_name,
            "scale_ratio_value": ratio,
            "hierarchy": scale
        }


class ImageAnalyzer:
    """Capability 84: Image Analysis (Composition, Rule of Thirds, Lighting)"""

    @staticmethod
    def analyze_composition_and_lighting(
        image_or_path: Union[str, Image.Image, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Performs comprehensive visual analysis:
          - Rule of thirds grid division and focal distribution
          - Luminance histogram (shadows, midtones, highlights)
          - Average brightness & dynamic range
          - Exposure classification (Underexposed, Low-Key, Balanced, High-Key, Overexposed)
          - Left-right & Top-bottom visual balance
        """
        if isinstance(image_or_path, str):
            img = Image.open(image_or_path).convert("RGB")
        elif isinstance(image_or_path, Image.Image):
            img = image_or_path.convert("RGB")
        elif isinstance(image_or_path, np.ndarray):
            if image_or_path.dtype != np.uint8:
                image_or_path = (np.clip(image_or_path, 0.0, 1.0) * 255.0).astype(np.uint8)
            img = Image.fromarray(image_or_path).convert("RGB")
        else:
            raise TypeError("Unsupported image input type.")

        width, height = img.size
        arr = np.asarray(img, dtype=np.float32)

        # 1. Grayscale luminance array using ITU-R BT.601
        luminance = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        avg_brightness = float(np.mean(luminance))
        min_lum = float(np.min(luminance))
        max_lum = float(np.max(luminance))
        dynamic_range = max_lum - min_lum

        # 2. Histogram distribution
        shadows_count = int(np.sum(luminance < 64))
        midtones_count = int(np.sum((luminance >= 64) & (luminance < 192)))
        highlights_count = int(np.sum(luminance >= 192))
        total_pixels = width * height

        shadows_pct = (shadows_count / total_pixels) * 100.0
        midtones_pct = (midtones_count / total_pixels) * 100.0
        highlights_pct = (highlights_count / total_pixels) * 100.0

        # 3. Exposure Assessment
        if avg_brightness < 45.0 or shadows_pct > 70.0:
            exposure_class = "Underexposed / Deep Shadows"
        elif avg_brightness < 85.0:
            exposure_class = "Low-Key (Moody / Cinematic)"
        elif avg_brightness > 210.0 or highlights_pct > 65.0:
            exposure_class = "Overexposed / Blown Highlights"
        elif avg_brightness > 165.0:
            exposure_class = "High-Key (Bright / Airy)"
        else:
            exposure_class = "Balanced Normal Exposure"

        # 4. Rule-of-Thirds Grid Evaluation
        # Divide into 3 horizontal and 3 vertical slices
        h_third = height // 3
        w_third = width // 3

        # Compute simple gradient / edge energy map to detect where visual interest is concentrated
        dy = np.abs(luminance[1:, :] - luminance[:-1, :])
        dx = np.abs(luminance[:, 1:] - luminance[:, :-1])
        energy = np.zeros_like(luminance)
        energy[:-1, :] += dy
        energy[:, :-1] += dx

        # Check energy at the 4 power intersections (x: 1/3, 2/3; y: 1/3, 2/3)
        margin_h = max(2, h_third // 4)
        margin_w = max(2, w_third // 4)

        intersections = {
            "top_left": float(np.mean(energy[h_third - margin_h:h_third + margin_h, w_third - margin_w:w_third + margin_w])),
            "top_right": float(np.mean(energy[h_third - margin_h:h_third + margin_h, 2 * w_third - margin_w:2 * w_third + margin_w])),
            "bottom_left": float(np.mean(energy[2 * h_third - margin_h:2 * h_third + margin_h, w_third - margin_w:w_third + margin_w])),
            "bottom_right": float(np.mean(energy[2 * h_third - margin_h:2 * h_third + margin_h, 2 * w_third - margin_w:2 * w_third + margin_w]))
        }

        # Left vs Right visual balance
        left_energy = float(np.sum(energy[:, :width // 2]))
        right_energy = float(np.sum(energy[:, width // 2:]))
        total_e = left_energy + right_energy + 1e-9
        lr_balance = (left_energy - right_energy) / total_e  # -1 (all right) to +1 (all left)

        strongest_focal_point = max(intersections.items(), key=lambda x: x[1])[0]

        return {
            "dimensions": {"width": width, "height": height, "aspect_ratio": round(width / max(1, height), 2)},
            "lighting_assessment": {
                "average_brightness_255": round(avg_brightness, 1),
                "dynamic_range": round(dynamic_range, 1),
                "exposure_classification": exposure_class,
                "shadows_pct": round(shadows_pct, 1),
                "midtones_pct": round(midtones_pct, 1),
                "highlights_pct": round(highlights_pct, 1)
            },
            "composition_assessment": {
                "rule_of_thirds_intersections": {k: round(v, 2) for k, v in intersections.items()},
                "dominant_focal_intersection": strongest_focal_point,
                "horizontal_balance_bias": "Left-weighted" if lr_balance > 0.15 else ("Right-weighted" if lr_balance < -0.15 else "Balanced Center"),
                "balance_coefficient": round(lr_balance, 3)
            }
        }
