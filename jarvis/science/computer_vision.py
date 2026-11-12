"""
Computer Vision Engine (Capability 72)
Provides Harris Corner Detection with Non-Maximum Suppression,
Connected Component Blob extraction, and geometric contour feature metrics
(area, perimeter, centroid, aspect ratio, circularity).
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from jarvis.science.image_processing import ImageProcessingEngine


class HarrisCornerDetector:
    """Harris Corner Detection with spatial gradients and Non-Maximum Suppression."""

    @staticmethod
    def detect_corners(
        image: np.ndarray,
        k: float = 0.04,
        threshold_ratio: float = 0.01,
        nms_window: int = 5,
    ) -> List[Dict[str, Union[int, float]]]:
        """
        Detects interest points/corners using Harris Corner response:
        R = det(M) - k * trace(M)^2
        Returns list of corner coordinates {"x": col, "y": row, "response": val}.
        """
        img = np.asarray(image, dtype=float)
        # Compute spatial derivatives
        sobel_res = ImageProcessingEngine.sobel_edge_detection(img)
        ix = sobel_res["gx"]
        iy = sobel_res["gy"]

        # Products of derivatives
        ix2 = ix * ix
        iy2 = iy * iy
        ixiy = ix * iy

        # Gaussian window weighting
        g_ix2 = ImageProcessingEngine.gaussian_blur(ix2, size=5, sigma=1.0)
        g_iy2 = ImageProcessingEngine.gaussian_blur(iy2, size=5, sigma=1.0)
        g_ixiy = ImageProcessingEngine.gaussian_blur(ixiy, size=5, sigma=1.0)

        # Harris response R = det(M) - k * trace(M)^2
        det_m = (g_ix2 * g_iy2) - (g_ixiy ** 2)
        trace_m = g_ix2 + g_iy2
        response = det_m - k * (trace_m ** 2)

        # Absolute threshold
        max_resp = np.max(response)
        if max_resp <= 0:
            return []
        abs_thresh = threshold_ratio * max_resp

        # Non-maximum suppression (NMS)
        h, w = response.shape
        rad = nms_window // 2
        corners = []

        for r in range(rad, h - rad):
            for c in range(rad, w - rad):
                val = response[r, c]
                if val > abs_thresh:
                    local_window = response[r - rad: r + rad + 1, c - rad: c + rad + 1]
                    if val == np.max(local_window):
                        corners.append({
                            "x": int(c),
                            "y": int(r),
                            "response": float(val),
                        })

        corners.sort(key=lambda item: item["response"], reverse=True)
        return corners


class ContourAnalyzer:
    """Connected component analysis and geometric feature extraction from binary masks."""

    @staticmethod
    def extract_blobs(binary_image: np.ndarray, min_area: int = 4) -> List[Dict[str, Any]]:
        """
        Extracts 8-connected foreground blobs from a binary mask (pixels > 0).
        Calculates area, perimeter, bounding box, centroid, circularity, and aspect ratio.
        """
        mask = (np.asarray(binary_image) > 0).astype(int)
        h, w = mask.shape
        visited = np.zeros((h, w), dtype=bool)
        blobs = []

        # 8-connected neighbors
        neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for r in range(h):
            for c in range(w):
                if mask[r, c] and not visited[r, c]:
                    # Breadth-first search flood fill
                    queue = [(r, c)]
                    visited[r, c] = True
                    pixels = []

                    while queue:
                        curr_r, curr_c = queue.pop(0)
                        pixels.append((curr_r, curr_c))

                        for dr, dc in neighbors:
                            nr, nc = curr_r + dr, curr_c + dc
                            if 0 <= nr < h and 0 <= nc < w:
                                if mask[nr, nc] and not visited[nr, nc]:
                                    visited[nr, nc] = True
                                    queue.append((nr, nc))

                    area = len(pixels)
                    if area < min_area:
                        continue

                    # Bounding box
                    rows = [p[0] for p in pixels]
                    cols = [p[1] for p in pixels]
                    min_r, max_r = min(rows), max(rows)
                    min_c, max_c = min(cols), max(cols)
                    box_w = max_c - min_c + 1
                    box_h = max_r - min_r + 1

                    # Centroid (center of mass)
                    centroid_x = float(np.mean(cols))
                    centroid_y = float(np.mean(rows))

                    # Perimeter: count border pixels that have at least one 4-neighbor outside
                    perimeter = 0
                    cardinal = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    pixel_set = set(pixels)
                    for pr, pc in pixels:
                        is_border = False
                        for cdr, cdc in cardinal:
                            if (pr + cdr, pc + cdc) not in pixel_set:
                                is_border = True
                                break
                        if is_border:
                            perimeter += 1
                    perimeter = max(1, perimeter)

                    # Compactness / Circularity (4 * pi * Area / Perimeter^2)
                    circularity = (4.0 * math.pi * area) / (perimeter ** 2)
                    circularity = min(1.0, circularity)

                    # Aspect ratio
                    aspect_ratio = float(box_w) / float(box_h) if box_h > 0 else 1.0

                    blobs.append({
                        "area": area,
                        "perimeter": perimeter,
                        "centroid": (round(centroid_x, 2), round(centroid_y, 2)),
                        "bbox": {
                            "x": min_c,
                            "y": min_r,
                            "width": box_w,
                            "height": box_h,
                        },
                        "aspect_ratio": round(aspect_ratio, 3),
                        "circularity": round(circularity, 3),
                    })

        blobs.sort(key=lambda b: b["area"], reverse=True)
        return blobs
