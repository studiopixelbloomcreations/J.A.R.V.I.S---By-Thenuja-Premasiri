"""
Image Processing Engine (Capability 69)
Provides 2D spatial convolution kernels, Gaussian/box blurs, Laplacian sharpening,
Sobel/Prewitt/Laplacian edge detectors, histogram equalization, gamma correction,
and Otsu automated thresholding.
"""

import math
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class ImageProcessingEngine:
    """Core 2D convolution and digital image processing filters."""

    @staticmethod
    def convolve2d(image: np.ndarray, kernel: np.ndarray, mode: str = "reflect") -> np.ndarray:
        """
        Performs 2D spatial convolution of a 2D grayscale image with a 2D kernel.
        """
        img = np.asarray(image, dtype=float)
        kern = np.asarray(kernel, dtype=float)
        if img.ndim != 2 or kern.ndim != 2:
            raise ValueError("Image and kernel must be 2D arrays.")

        kh, kw = kern.shape
        pad_h = kh // 2
        pad_w = kw // 2

        # Pad image
        if mode == "reflect":
            padded = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode="reflect")
        elif mode == "constant":
            padded = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant", constant_values=0)
        else:
            padded = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode="edge")

        # Flip kernel for true mathematical convolution
        k_flipped = np.flip(np.flip(kern, 0), 1)

        out_h, out_w = img.shape
        output = np.zeros((out_h, out_w), dtype=float)

        for r in range(out_h):
            for c in range(out_w):
                region = padded[r: r + kh, c: c + kw]
                output[r, c] = np.sum(region * k_flipped)

        return output

    @staticmethod
    def gaussian_kernel(size: int = 5, sigma: float = 1.0) -> np.ndarray:
        """Generates normalized 2D Gaussian blur kernel."""
        if size % 2 == 0:
            size += 1
        ax = np.linspace(-(size // 2), size // 2, size)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
        return kernel / np.sum(kernel)

    @staticmethod
    def gaussian_blur(image: np.ndarray, size: int = 5, sigma: float = 1.0) -> np.ndarray:
        """Applies Gaussian smoothing to 2D image."""
        kernel = ImageProcessingEngine.gaussian_kernel(size, sigma)
        return ImageProcessingEngine.convolve2d(image, kernel)

    @staticmethod
    def box_blur(image: np.ndarray, size: int = 3) -> np.ndarray:
        """Applies uniform box blur filter."""
        kernel = np.ones((size, size), dtype=float) / (size * size)
        return ImageProcessingEngine.convolve2d(image, kernel)

    @staticmethod
    def sharpen(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """Applies Laplacian sharpening kernel."""
        kernel = np.array([
            [0.0, -1.0 * strength, 0.0],
            [-1.0 * strength, 1.0 + 4.0 * strength, -1.0 * strength],
            [0.0, -1.0 * strength, 0.0]
        ], dtype=float)
        return np.clip(ImageProcessingEngine.convolve2d(image, kernel), 0, 255)

    @staticmethod
    def sobel_edge_detection(image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Computes Sobel gradient in X and Y directions, overall gradient magnitude and phase angles.
        """
        kx = np.array([
            [-1.0, 0.0, 1.0],
            [-2.0, 0.0, 2.0],
            [-1.0, 0.0, 1.0]
        ], dtype=float)

        ky = np.array([
            [-1.0, -2.0, -1.0],
            [ 0.0,  0.0,  0.0],
            [ 1.0,  2.0,  1.0]
        ], dtype=float)

        gx = ImageProcessingEngine.convolve2d(image, kx)
        gy = ImageProcessingEngine.convolve2d(image, ky)

        magnitude = np.sqrt(gx ** 2 + gy ** 2)
        direction = np.arctan2(gy, gx)

        return {
            "gx": gx,
            "gy": gy,
            "magnitude": magnitude,
            "direction": direction,
        }

    @staticmethod
    def laplacian_edge_detection(image: np.ndarray) -> np.ndarray:
        """Applies isotropic 3x3 Laplacian edge detection operator."""
        kernel = np.array([
            [0.0,  1.0, 0.0],
            [1.0, -4.0, 1.0],
            [0.0,  1.0, 0.0]
        ], dtype=float)
        return np.abs(ImageProcessingEngine.convolve2d(image, kernel))

    @staticmethod
    def gamma_correction(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        """Applies nonlinear gamma adjustment: I_out = 255 * (I / 255)^gamma."""
        if gamma <= 0:
            raise ValueError("Gamma must be strictly positive.")
        norm = np.clip(image, 0.0, 255.0) / 255.0
        corrected = np.power(norm, gamma) * 255.0
        return np.clip(corrected, 0.0, 255.0)

    @staticmethod
    def histogram_equalization(image: np.ndarray) -> np.ndarray:
        """Enhances contrast of grayscale image via cumulative distribution histogram equalization."""
        img_int = np.clip(image, 0, 255).astype(np.uint8)
        hist, _ = np.histogram(img_int.flatten(), bins=256, range=[0, 256])

        # Cumulative distribution function (CDF)
        cdf = hist.cumsum()
        cdf_masked = np.ma.masked_equal(cdf, 0)
        # Normalize CDF
        cdf_masked = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
        cdf_final = np.ma.filled(cdf_masked, 0).astype(np.uint8)

        equalized = cdf_final[img_int]
        return equalized.astype(float)

    @staticmethod
    def otsu_threshold(image: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Computes optimal global binarization threshold using Otsu's method
        (maximizes inter-class between background and foreground variance).
        Returns (threshold_value, binary_image).
        """
        img_int = np.clip(image, 0, 255).astype(np.uint8)
        hist, _ = np.histogram(img_int.flatten(), bins=256, range=[0, 256])
        total_pixels = img_int.size

        current_max = 0.0
        best_threshold = 0

        weight_bg = 0
        sum_bg = 0
        total_sum = np.dot(np.arange(256), hist)

        for t in range(256):
            weight_bg += hist[t]
            if weight_bg == 0:
                continue
            weight_fg = total_pixels - weight_bg
            if weight_fg == 0:
                break

            sum_bg += t * hist[t]
            mean_bg = sum_bg / weight_bg
            mean_fg = (total_sum - sum_bg) / weight_fg

            # Between-class variance
            between_var = weight_bg * weight_fg * ((mean_bg - mean_fg) ** 2)

            if between_var > current_max:
                current_max = between_var
                best_threshold = t

        binary = (img_int >= best_threshold).astype(float) * 255.0
        return float(best_threshold), binary
