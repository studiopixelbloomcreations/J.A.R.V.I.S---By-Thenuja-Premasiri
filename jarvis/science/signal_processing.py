"""
Signal Processing Engine (Capability 70)
Provides Fast Fourier Transform (FFT), spectral density analysis, peak harmonic detection,
Hamming-windowed sinc FIR filter design (Low-pass, High-pass, Band-pass),
and synthetic signal generation with AWGN noise.
"""

import math
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class SignalProcessingEngine:
    """Spectral analysis and digital filtering."""

    @staticmethod
    def compute_fft(
        signal: Union[List[float], np.ndarray],
        sample_rate_hz: float,
    ) -> Dict[str, Union[List[float], float]]:
        """
        Computes 1D Fast Fourier Transform, frequency bins, magnitude spectrum,
        phase spectrum, and power spectral density (PSD).
        """
        x = np.asarray(signal, dtype=float)
        n = len(x)
        if n < 4 or sample_rate_hz <= 0:
            raise ValueError("Signal length must be >= 4 and sample_rate_hz > 0.")

        # Compute FFT via numpy.fft
        fft_vals = np.fft.rfft(x)
        freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate_hz)

        # Magnitude (scaled for one-sided spectrum)
        magnitude = np.abs(fft_vals) * (2.0 / n)
        magnitude[0] /= 2.0  # DC component
        if n % 2 == 0 and len(magnitude) > 1:
            magnitude[-1] /= 2.0  # Nyquist component

        # Phase in degrees
        phase = np.angle(fft_vals, deg=True)

        # Power Spectral Density (PSD)
        psd = (np.abs(fft_vals) ** 2) / (sample_rate_hz * n)

        return {
            "num_samples": n,
            "sample_rate_hz": sample_rate_hz,
            "frequencies_hz": freqs.tolist(),
            "magnitude": magnitude.tolist(),
            "phase_deg": phase.tolist(),
            "psd": psd.tolist(),
        }

    @staticmethod
    def detect_peak_frequencies(
        frequencies: List[float],
        magnitudes: List[float],
        top_k: int = 5,
        min_magnitude: float = 0.05,
    ) -> List[Dict[str, float]]:
        """Identifies top-k dominant harmonic peaks from magnitude spectrum."""
        freqs = np.asarray(frequencies)
        mags = np.asarray(magnitudes)

        peaks = []
        for i in range(1, len(mags) - 1):
            if mags[i] > mags[i - 1] and mags[i] > mags[i + 1] and mags[i] >= min_magnitude:
                peaks.append((float(freqs[i]), float(mags[i])))

        # Sort descending by magnitude
        peaks.sort(key=lambda item: item[1], reverse=True)
        return [{"frequency_hz": round(p[0], 2), "magnitude": round(p[1], 4)} for p in peaks[:top_k]]

    @staticmethod
    def design_fir_lowpass(
        cutoff_hz: float,
        sample_rate_hz: float,
        num_taps: int = 65,
    ) -> np.ndarray:
        """
        Designs low-pass FIR filter using windowed sinc and Hamming window.
        num_taps must be odd.
        """
        if num_taps % 2 == 0:
            num_taps += 1
        fc = cutoff_hz / sample_rate_hz
        if fc >= 0.5:
            raise ValueError("Cutoff frequency must be below Nyquist rate (sample_rate / 2).")

        m = num_taps - 1
        half_m = m // 2
        h = np.zeros(num_taps)

        for i in range(num_taps):
            n = i - half_m
            if n == 0:
                h[i] = 2.0 * math.pi * fc
            else:
                h[i] = math.sin(2.0 * math.pi * fc * n) / n
            # Hamming window: 0.54 - 0.46 * cos(2*pi*i / m)
            w = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / m)
            h[i] *= w

        # Normalize filter gain to 1 at DC
        h /= np.sum(h)
        return h

    @staticmethod
    def design_fir_highpass(
        cutoff_hz: float,
        sample_rate_hz: float,
        num_taps: int = 65,
    ) -> np.ndarray:
        """Designs high-pass FIR filter via spectral inversion of low-pass filter."""
        lp = SignalProcessingEngine.design_fir_lowpass(cutoff_hz, sample_rate_hz, num_taps)
        hp = -lp
        half_m = (len(lp) - 1) // 2
        hp[half_m] += 1.0
        return hp

    @staticmethod
    def apply_fir_filter(signal: Union[List[float], np.ndarray], filter_taps: np.ndarray) -> List[float]:
        """Applies FIR filter via 1D linear convolution (same length as input)."""
        x = np.asarray(signal, dtype=float)
        filtered = np.convolve(x, filter_taps, mode="same")
        return filtered.tolist()

    @staticmethod
    def moving_average(signal: Union[List[float], np.ndarray], window_size: int = 5) -> List[float]:
        """Applies uniform moving average smoothing filter."""
        x = np.asarray(signal, dtype=float)
        if window_size <= 1:
            return x.tolist()
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(x, kernel, mode="same")
        return smoothed.tolist()

    @staticmethod
    def generate_synthetic_signal(
        duration_s: float,
        sample_rate_hz: float,
        frequencies: List[float],
        amplitudes: List[float],
        noise_std: float = 0.0,
    ) -> Dict[str, Union[List[float], float]]:
        """Generates synthetic multi-harmonic time series signal with optional Gaussian noise."""
        num_samples = int(duration_s * sample_rate_hz)
        t = np.linspace(0.0, duration_s, num_samples, endpoint=False)
        sig = np.zeros(num_samples)

        for f, a in zip(frequencies, amplitudes):
            sig += a * np.sin(2.0 * math.pi * f * t)

        if noise_std > 0.0:
            sig += np.random.normal(0.0, noise_std, num_samples)

        return {
            "time_s": t.tolist(),
            "signal": sig.tolist(),
            "sample_rate_hz": sample_rate_hz,
            "duration_s": duration_s,
        }
