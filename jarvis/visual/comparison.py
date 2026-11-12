"""
Visual Comparison Engine (Capability 133)
Computes pixel-by-pixel differences, structural similarity scores,
bounding boxes of changed regions, diff masks, and side-by-side comparison payloads.
"""

import io
import math
import base64
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import numpy as np


@dataclass
class DiffRegion:
    x: int
    y: int
    w: int
    h: int
    area: int
    change_intensity: float = 1.0


@dataclass
class ComparisonResult:
    similarity_score: float  # 0.0 to 1.0 (1.0 = identical)
    diff_percentage: float  # 0.0% to 100.0%
    total_diff_pixels: int
    changed_regions: List[DiffRegion] = field(default_factory=list)
    diff_image_base64: str = ""
    side_by_side_base64: str = ""
    summary: str = ""


class VisualComparisonEngine:
    """
    Robust image diffing and structural visual comparison engine.
    """

    def __init__(self, threshold: int = 25):
        self.threshold = threshold

    def _ensure_image(self, img_input: Union[str, Image.Image]) -> Image.Image:
        if isinstance(img_input, str):
            return Image.open(img_input).convert("RGB")
        return img_input.convert("RGB")

    def compute_dhash(self, img_input: Union[str, Image.Image], hash_size: int = 8) -> str:
        """
        Computes difference hash (dHash) for fast perceptual duplicate matching.
        """
        img = self._ensure_image(img_input).convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(img, dtype=np.int32)
        diff = arr[:, 1:] > arr[:, :-1]
        bits = "".join(["1" if b else "0" for b in diff.flatten()])
        hex_hash = f"{int(bits, 2):0{hash_size * hash_size // 4}x}"
        return hex_hash

    def compare_images(
        self,
        img_a_input: Union[str, Image.Image],
        img_b_input: Union[str, Image.Image],
        generate_visuals: bool = True,
    ) -> ComparisonResult:
        """
        Compares two images and returns a detailed ComparisonResult.
        """
        img_a = self._ensure_image(img_a_input)
        img_b = self._ensure_image(img_b_input)

        # Match dimensions if they differ
        target_w = max(img_a.width, img_b.width)
        target_h = max(img_a.height, img_b.height)

        if img_a.size != (target_w, target_h):
            canvas_a = Image.new("RGB", (target_w, target_h), (0, 0, 0))
            canvas_a.paste(img_a, (0, 0))
            img_a = canvas_a

        if img_b.size != (target_w, target_h):
            canvas_b = Image.new("RGB", (target_w, target_h), (0, 0, 0))
            canvas_b.paste(img_b, (0, 0))
            img_b = canvas_b

        arr_a = np.array(img_a, dtype=np.float32)
        arr_b = np.array(img_b, dtype=np.float32)

        # Pixel difference
        diff_arr = np.abs(arr_a - arr_b)
        max_channel_diff = np.max(diff_arr, axis=2)
        diff_mask = max_channel_diff > self.threshold

        total_pixels = target_w * target_h
        diff_pixel_count = int(np.sum(diff_mask))
        diff_pct = (diff_pixel_count / max(1, total_pixels)) * 100.0

        # Mean Absolute Error and perceptual similarity
        mae = float(np.mean(diff_arr))
        # Similarity score: 1.0 when identical, scales down with MAE
        sim_score = max(0.0, min(1.0, 1.0 - (mae / 255.0)))

        # Find clustered bounding boxes of changed regions
        changed_regions = self._find_changed_regions(diff_mask, target_w, target_h)

        diff_b64 = ""
        side_by_side_b64 = ""

        if generate_visuals:
            # Generate Diff Highlight Image (semi-transparent red overlay on img_b)
            diff_vis = img_b.copy().convert("RGBA")
            overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Highlight changed pixels in hot red/magenta
            red_pixels = np.zeros((target_h, target_w, 4), dtype=np.uint8)
            red_pixels[diff_mask] = [255, 0, 85, 170]
            mask_img = Image.fromarray(red_pixels, mode="RGBA")
            overlay = Image.alpha_composite(overlay, mask_img)

            # Draw bounding boxes around clusters
            draw_boxes = ImageDraw.Draw(overlay)
            for reg in changed_regions:
                draw_boxes.rectangle(
                    [reg.x, reg.y, reg.x + reg.w, reg.y + reg.h],
                    outline=(0, 229, 255, 230),
                    width=2,
                )

            diff_composite = Image.alpha_composite(diff_vis, overlay).convert("RGB")
            buf_diff = io.BytesIO()
            diff_composite.save(buf_diff, format="JPEG", quality=85)
            diff_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf_diff.getvalue()).decode('utf-8')}"

            # Side-by-side composite image
            side_img = Image.new("RGB", (target_w * 2 + 10, target_h), (6, 19, 37))
            side_img.paste(img_a, (0, 0))
            side_img.paste(img_b, (target_w + 10, 0))
            buf_side = io.BytesIO()
            side_img.save(buf_side, format="JPEG", quality=85)
            side_by_side_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf_side.getvalue()).decode('utf-8')}"

        summary = f"Visual match {sim_score*100:.1f}%. Changed pixels: {diff_pixel_count} ({diff_pct:.2f}%). Detected {len(changed_regions)} change clusters."

        return ComparisonResult(
            similarity_score=round(sim_score, 4),
            diff_percentage=round(diff_pct, 2),
            total_diff_pixels=diff_pixel_count,
            changed_regions=changed_regions,
            diff_image_base64=diff_b64,
            side_by_side_base64=side_by_side_b64,
            summary=summary,
        )

    def _find_changed_regions(
        self,
        diff_mask: np.ndarray,
        width: int,
        height: int,
        grid_size: int = 32,
    ) -> List[DiffRegion]:
        """
        Segments diff mask into coarse grid cells and merges adjacent active cells into bounding boxes.
        """
        cols = (width + grid_size - 1) // grid_size
        rows = (height + grid_size - 1) // grid_size

        active_cells = []
        for r in range(rows):
            for c in range(cols):
                y0 = r * grid_size
                y1 = min(height, (r + 1) * grid_size)
                x0 = c * grid_size
                x1 = min(width, (c + 1) * grid_size)

                cell_mask = diff_mask[y0:y1, x0:x1]
                if np.sum(cell_mask) > (grid_size * grid_size * 0.05):
                    active_cells.append((c, r))

        if not active_cells:
            return []

        # Connected component clustering on the grid
        visited = set()
        regions = []

        for cell in active_cells:
            if cell in visited:
                continue
            cluster = []
            queue = [cell]
            visited.add(cell)

            while queue:
                curr = queue.pop(0)
                cluster.append(curr)
                cx, cy = curr
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    neighbor = (cx + dx, cy + dy)
                    if neighbor in active_cells and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            # Compute bounding box for cluster
            min_c = min(c for c, r in cluster)
            max_c = max(c for c, r in cluster)
            min_r = min(r for c, r in cluster)
            max_r = max(r for c, r in cluster)

            rx = min_c * grid_size
            ry = min_r * grid_size
            rw = min(width - rx, (max_c - min_c + 1) * grid_size)
            rh = min(height - ry, (max_r - min_r + 1) * grid_size)

            regions.append(DiffRegion(x=rx, y=ry, w=rw, h=rh, area=rw * rh))

        return regions
