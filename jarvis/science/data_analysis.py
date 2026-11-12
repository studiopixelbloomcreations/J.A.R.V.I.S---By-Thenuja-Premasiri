"""
Scientific Data Analysis Engine (Capability 67)
Provides comprehensive statistical summary metrics (mean, median, mode, variance,
skewness, kurtosis, percentiles, IQR), Pearson & Spearman correlations,
outlier detection (Z-score and Tukey IQR fences), and tabular dataset aggregation.
"""

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class ScientificDataAnalyzer:
    """Statistical metric calculation, correlation matrices, and outlier identification."""

    @staticmethod
    def descriptive_stats(data: Union[List[float], np.ndarray]) -> Dict[str, float]:
        """
        Computes full suite of descriptive statistical metrics on a 1D numerical series.
        """
        arr = np.asarray(data, dtype=float)
        arr = arr[~np.isnan(arr)]
        n = len(arr)
        if n == 0:
            raise ValueError("Data series is empty or contains only NaNs.")

        mean_val = float(np.mean(arr))
        median_val = float(np.median(arr))
        var_val = float(np.var(arr, ddof=1)) if n > 1 else 0.0
        std_val = float(np.std(arr, ddof=1)) if n > 1 else 0.0
        sem_val = std_val / math.sqrt(n) if n > 0 else 0.0

        min_val = float(np.min(arr))
        max_val = float(np.max(arr))
        range_val = max_val - min_val

        # Mode calculation
        counts = Counter(arr.tolist())
        mode_val = float(counts.most_common(1)[0][0])

        # Skewness & Kurtosis
        if n >= 3 and std_val > 1e-12:
            m3 = float(np.mean((arr - mean_val) ** 3))
            skew_val = m3 / (std_val ** 3)
        else:
            skew_val = 0.0

        if n >= 4 and std_val > 1e-12:
            m4 = float(np.mean((arr - mean_val) ** 4))
            kurtosis_val = (m4 / (std_val ** 4)) - 3.0  # Excess kurtosis
        else:
            kurtosis_val = 0.0

        # Percentiles & IQR
        p25 = float(np.percentile(arr, 25))
        p75 = float(np.percentile(arr, 75))
        iqr = p75 - p25

        return {
            "count": float(n),
            "mean": mean_val,
            "median": median_val,
            "mode": mode_val,
            "variance": var_val,
            "std_dev": std_val,
            "std_error": sem_val,
            "min": min_val,
            "max": max_val,
            "range": range_val,
            "skewness": skew_val,
            "kurtosis_excess": kurtosis_val,
            "p25": p25,
            "p75": p75,
            "iqr": iqr,
        }

    @staticmethod
    def pearson_correlation(x: Union[List[float], np.ndarray], y: Union[List[float], np.ndarray]) -> float:
        """Calculates Pearson linear correlation coefficient r between x and y."""
        ax = np.asarray(x, dtype=float)
        ay = np.asarray(y, dtype=float)
        if len(ax) != len(ay) or len(ax) < 2:
            raise ValueError("Vectors must have matching length >= 2.")

        corr_matrix = np.corrcoef(ax, ay)
        r = float(corr_matrix[0, 1])
        return 0.0 if np.isnan(r) else r

    @staticmethod
    def spearman_correlation(x: Union[List[float], np.ndarray], y: Union[List[float], np.ndarray]) -> float:
        """Calculates Spearman rank correlation coefficient between x and y."""
        ax = np.asarray(x, dtype=float)
        ay = np.asarray(y, dtype=float)
        if len(ax) != len(ay) or len(ax) < 2:
            raise ValueError("Vectors must have matching length >= 2.")

        def rank_array(a: np.ndarray) -> np.ndarray:
            order = a.argsort()
            ranks = order.argsort().astype(float)
            return ranks

        rx = rank_array(ax)
        ry = rank_array(ay)
        return ScientificDataAnalyzer.pearson_correlation(rx, ry)

    @staticmethod
    def detect_outliers_zscore(data: Union[List[float], np.ndarray], threshold: float = 3.0) -> Dict[str, Any]:
        """Detects outliers using standard Z-score method (|z| > threshold)."""
        arr = np.asarray(data, dtype=float)
        mean_val = np.mean(arr)
        std_val = np.std(arr, ddof=1)
        if std_val < 1e-12:
            return {"outlier_indices": [], "outlier_values": [], "z_scores": [0.0] * len(arr)}

        z_scores = ((arr - mean_val) / std_val).tolist()
        outliers = [(i, float(arr[i]), float(z_scores[i])) for i in range(len(arr)) if abs(z_scores[i]) > threshold]

        return {
            "outlier_indices": [item[0] for item in outliers],
            "outlier_values": [item[1] for item in outliers],
            "z_scores": z_scores,
            "threshold": threshold,
        }

    @staticmethod
    def detect_outliers_iqr(data: Union[List[float], np.ndarray], factor: float = 1.5) -> Dict[str, Any]:
        """Detects outliers using Tukey's fences (IQR method: [Q1 - k*IQR, Q3 + k*IQR])."""
        arr = np.asarray(data, dtype=float)
        q25 = np.percentile(arr, 25)
        q75 = np.percentile(arr, 75)
        iqr = q75 - q25
        lower_bound = q25 - factor * iqr
        upper_bound = q75 + factor * iqr

        outlier_indices = []
        outlier_values = []
        for i, val in enumerate(arr):
            if val < lower_bound or val > upper_bound:
                outlier_indices.append(i)
                outlier_values.append(float(val))

        return {
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "iqr": float(iqr),
            "outlier_indices": outlier_indices,
            "outlier_values": outlier_values,
        }

    @staticmethod
    def group_by_aggregate(
        records: List[Dict[str, Any]],
        group_col: str,
        val_col: str,
        agg_func: str = "mean",
    ) -> Dict[str, float]:
        """Groups tabular records by group_col and aggregates val_col using agg_func (sum, mean, min, max, count)."""
        groups: Dict[str, List[float]] = {}
        for row in records:
            key = str(row.get(group_col, "UNKNOWN"))
            val = float(row.get(val_col, 0.0))
            if key not in groups:
                groups[key] = []
            groups[key].append(val)

        results: Dict[str, float] = {}
        for key, values in groups.items():
            if agg_func == "sum":
                results[key] = float(np.sum(values))
            elif agg_func == "mean":
                results[key] = float(np.mean(values))
            elif agg_func == "min":
                results[key] = float(np.min(values))
            elif agg_func == "max":
                results[key] = float(np.max(values))
            elif agg_func == "count":
                results[key] = float(len(values))
            else:
                raise ValueError(f"Unknown aggregation function: {agg_func}")

        return results
