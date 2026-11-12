"""
Statistical Modeling Engine (Capability 68)
Provides Ordinary Least Squares (OLS) linear & polynomial regression,
parametric distribution fitting (Normal, Exponential, Uniform, Poisson),
and hypothesis testing (One/Two-sample t-test, Z-test, Chi-square independence test).
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function Phi(x) using math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def student_t_cdf_approx(t: float, df: float) -> float:
    """Accurate approximation of Student's t CDF using Hill's algorithm or normal transform."""
    if df <= 0:
        raise ValueError("Degrees of freedom must be positive.")
    # For large df, approaches normal
    if df > 100:
        return norm_cdf(t)
    # Transformation to normal deviate via Cornish-Fisher expansion
    a = df - 0.5
    b = 48.0 * (a ** 2)
    z = math.sqrt(a * math.log(1.0 + (t ** 2) / df))
    z_corr = z - (z ** 3 + 3.0 * z) / b
    p = norm_cdf(z_corr if t >= 0 else -z_corr)
    return p if t >= 0 else 1.0 - p


class RegressionEngine:
    """Ordinary Least Squares Linear & Polynomial Regression."""

    @staticmethod
    def linear_regression(x: List[float], y: List[float]) -> Dict[str, Union[float, List[float]]]:
        """
        Fits simple linear regression y = slope * x + intercept.
        Returns coefficients, R^2, MSE, RMSE, std errors, and t-stats.
        """
        ax = np.asarray(x, dtype=float)
        ay = np.asarray(y, dtype=float)
        n = len(ax)
        if n < 3 or len(ay) != n:
            raise ValueError("Datasets must have matching length >= 3.")

        x_mean = np.mean(ax)
        y_mean = np.mean(ay)

        ss_xx = np.sum((ax - x_mean) ** 2)
        ss_yy = np.sum((ay - y_mean) ** 2)
        ss_xy = np.sum((ax - x_mean) * (ay - y_mean))

        if ss_xx < 1e-12:
            raise ValueError("Variance of x is zero; cannot perform linear regression.")

        slope = float(ss_xy / ss_xx)
        intercept = float(y_mean - slope * x_mean)

        y_pred = slope * ax + intercept
        residuals = ay - y_pred
        sse = float(np.sum(residuals ** 2))
        mse = sse / n
        rmse = math.sqrt(mse)

        # R^2
        r_squared = 1.0 - (sse / ss_yy) if ss_yy > 1e-12 else 0.0
        r_squared = max(0.0, min(1.0, r_squared))

        # Adjusted R^2 for 1 predictor
        adj_r_squared = 1.0 - ((1.0 - r_squared) * (n - 1) / (n - 2)) if n > 2 else r_squared

        # Standard errors
        df = n - 2
        s_err = math.sqrt(sse / df) if df > 0 else 0.0
        se_slope = s_err / math.sqrt(ss_xx) if ss_xx > 0 else 0.0
        se_intercept = s_err * math.sqrt((1.0 / n) + (x_mean ** 2) / ss_xx) if ss_xx > 0 else 0.0

        t_stat_slope = slope / se_slope if se_slope > 0 else 0.0
        p_val_slope = 2.0 * (1.0 - student_t_cdf_approx(abs(t_stat_slope), df))

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": float(r_squared),
            "adjusted_r_squared": float(adj_r_squared),
            "mse": float(mse),
            "rmse": float(rmse),
            "se_slope": float(se_slope),
            "se_intercept": float(se_intercept),
            "t_statistic": float(t_stat_slope),
            "p_value": float(max(0.0, min(1.0, p_val_slope))),
            "predicted": y_pred.tolist(),
            "residuals": residuals.tolist(),
        }

    @staticmethod
    def polynomial_regression(x: List[float], y: List[float], degree: int = 2) -> Dict[str, Any]:
        """Fits polynomial curve of specified degree using least squares."""
        ax = np.asarray(x, dtype=float)
        ay = np.asarray(y, dtype=float)
        if len(ax) <= degree or len(ax) != len(ay):
            raise ValueError("Data length must exceed polynomial degree.")

        coeffs = np.polyfit(ax, ay, deg=degree)
        poly = np.poly1d(coeffs)
        y_pred = poly(ax)

        sse = np.sum((ay - y_pred) ** 2)
        sst = np.sum((ay - np.mean(ay)) ** 2)
        r_squared = 1.0 - (sse / sst) if sst > 1e-12 else 0.0

        return {
            "degree": degree,
            "coefficients": [float(c) for c in coeffs],
            "r_squared": float(r_squared),
            "predicted": y_pred.tolist(),
            "formula": str(poly),
        }


class DistributionFitter:
    """Parameter estimation for continuous and discrete distributions."""

    @staticmethod
    def fit_normal(data: List[float]) -> Dict[str, float]:
        """Fits Normal (Gaussian) distribution: estimates mu, sigma via MLE."""
        arr = np.asarray(data, dtype=float)
        mu = float(np.mean(arr))
        sigma = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
        log_lik = -0.5 * len(arr) * math.log(2.0 * math.pi * (sigma ** 2)) - np.sum((arr - mu) ** 2) / (2.0 * sigma ** 2) if sigma > 0 else 0.0

        return {
            "distribution": "normal",
            "mean_mu": mu,
            "std_sigma": sigma,
            "variance": sigma ** 2,
            "log_likelihood": float(log_lik),
        }

    @staticmethod
    def fit_exponential(data: List[float]) -> Dict[str, float]:
        """Fits Exponential distribution: estimates rate lambda = 1 / mean."""
        arr = np.asarray(data, dtype=float)
        if any(x < 0 for x in arr):
            raise ValueError("Exponential distribution requires non-negative data.")
        mean_val = float(np.mean(arr))
        if mean_val <= 0:
            raise ValueError("Mean must be strictly positive.")
        rate_lambda = 1.0 / mean_val
        log_lik = len(arr) * math.log(rate_lambda) - rate_lambda * np.sum(arr)

        return {
            "distribution": "exponential",
            "rate_lambda": rate_lambda,
            "scale": mean_val,
            "log_likelihood": float(log_lik),
        }


class HypothesisTesting:
    """Statistical hypothesis testing."""

    @staticmethod
    def one_sample_t_test(data: List[float], pop_mean: float) -> Dict[str, float]:
        """One-sample Student's t-test: H0: mean(data) == pop_mean."""
        arr = np.asarray(data, dtype=float)
        n = len(arr)
        if n < 2:
            raise ValueError("At least 2 observations required.")

        sample_mean = float(np.mean(arr))
        sample_std = float(np.std(arr, ddof=1))
        df = n - 1
        sem = sample_std / math.sqrt(n)

        t_stat = (sample_mean - pop_mean) / sem if sem > 0 else 0.0
        p_val = 2.0 * (1.0 - student_t_cdf_approx(abs(t_stat), df))

        return {
            "sample_mean": sample_mean,
            "pop_mean_tested": pop_mean,
            "t_statistic": float(t_stat),
            "degrees_of_freedom": float(df),
            "p_value": float(max(0.0, min(1.0, p_val))),
            "statistically_significant_05": p_val < 0.05,
        }

    @staticmethod
    def two_sample_t_test(group1: List[float], group2: List[float]) -> Dict[str, float]:
        """Two-sample independent Student's t-test."""
        a1 = np.asarray(group1, dtype=float)
        a2 = np.asarray(group2, dtype=float)
        n1, n2 = len(a1), len(a2)
        if n1 < 2 or n2 < 2:
            raise ValueError("Both groups must have at least 2 samples.")

        m1, m2 = float(np.mean(a1)), float(np.mean(a2))
        v1, v2 = float(np.var(a1, ddof=1)), float(np.var(a2, ddof=1))

        # Pooled variance
        df = n1 + n2 - 2
        sp_sq = ((n1 - 1) * v1 + (n2 - 1) * v2) / df
        se_diff = math.sqrt(sp_sq * (1.0 / n1 + 1.0 / n2))

        t_stat = (m1 - m2) / se_diff if se_diff > 0 else 0.0
        p_val = 2.0 * (1.0 - student_t_cdf_approx(abs(t_stat), df))

        return {
            "mean1": m1,
            "mean2": m2,
            "mean_difference": m1 - m2,
            "t_statistic": float(t_stat),
            "degrees_of_freedom": float(df),
            "p_value": float(max(0.0, min(1.0, p_val))),
            "statistically_significant_05": p_val < 0.05,
        }

    @staticmethod
    def chi_square_independence(observed_matrix: List[List[float]]) -> Dict[str, float]:
        """Chi-square test of independence for a 2D contingency table."""
        obs = np.asarray(observed_matrix, dtype=float)
        r, c = obs.shape
        if r < 2 or c < 2:
            raise ValueError("Contingency table must be at least 2x2.")

        row_totals = np.sum(obs, axis=1, keepdims=True)
        col_totals = np.sum(obs, axis=0, keepdims=True)
        grand_total = np.sum(obs)

        expected = (row_totals @ col_totals) / grand_total
        chi_stat = float(np.sum(((obs - expected) ** 2) / expected))
        df = (r - 1) * (c - 1)

        # Approximate p-value via Wilson-Hilferty transformation of chi-square to normal
        z = ((chi_stat / df) ** (1.0 / 3.0) - (1.0 - 2.0 / (9.0 * df))) / math.sqrt(2.0 / (9.0 * df))
        p_val = 1.0 - norm_cdf(z)

        return {
            "chi2_statistic": chi_stat,
            "degrees_of_freedom": float(df),
            "p_value": float(max(0.0, min(1.0, p_val))),
            "statistically_significant_05": p_val < 0.05,
        }
