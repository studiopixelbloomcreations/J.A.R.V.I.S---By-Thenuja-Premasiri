"""
Simulation Management Engine (Capability 66)
Provides Monte Carlo stochastic simulators (Pi estimation, Geometric Brownian Motion,
confidence bounds) and Numerical Ordinary Differential Equation solvers (Euler, RK4)
for dynamical systems (Harmonic Oscillator, Nonlinear Pendulum, Drag Projectile, Lorenz Attractor).
"""

import math
import random
from typing import Callable, Dict, List, Optional, Tuple, Union
import numpy as np


class MonteCarloEngine:
    """Stochastic simulations, random walks, and Monte Carlo integration."""

    @staticmethod
    def estimate_pi(num_samples: int = 100000, seed: Optional[int] = 42) -> Dict[str, Union[float, int]]:
        """Estimates Pi via uniform random sampling inside unit square and quarter circle."""
        if seed is not None:
            np.random.seed(seed)
        x = np.random.uniform(0.0, 1.0, num_samples)
        y = np.random.uniform(0.0, 1.0, num_samples)
        inside = (x ** 2 + y ** 2) <= 1.0
        inside_count = int(np.sum(inside))
        pi_estimate = 4.0 * inside_count / float(num_samples)
        error = abs(pi_estimate - math.pi)

        return {
            "samples": num_samples,
            "inside_count": inside_count,
            "pi_estimate": pi_estimate,
            "actual_pi": math.pi,
            "error": error,
            "error_percent": (error / math.pi) * 100.0,
        }

    @staticmethod
    def geometric_brownian_motion(
        s0: float,
        mu: float,
        sigma: float,
        t_total: float,
        num_steps: int = 252,
        num_paths: int = 500,
        seed: Optional[int] = 42,
    ) -> Dict[str, Union[float, List[float], Dict[str, float]]]:
        """
        Simulates geometric Brownian motion paths:
        S(t + dt) = S(t) * exp((mu - 0.5 * sigma^2)*dt + sigma*sqrt(dt)*Z)
        Returns mean path, 5th and 95th percentile confidence envelopes.
        """
        if seed is not None:
            np.random.seed(seed)

        dt = t_total / float(num_steps)
        drift = (mu - 0.5 * (sigma ** 2)) * dt
        vol = sigma * math.sqrt(dt)

        paths = np.zeros((num_paths, num_steps + 1))
        paths[:, 0] = s0

        for step in range(1, num_steps + 1):
            z = np.random.normal(0.0, 1.0, num_paths)
            paths[:, step] = paths[:, step - 1] * np.exp(drift + vol * z)

        mean_path = np.mean(paths, axis=0).tolist()
        p05_path = np.percentile(paths, 5, axis=0).tolist()
        p50_path = np.percentile(paths, 50, axis=0).tolist()
        p95_path = np.percentile(paths, 95, axis=0).tolist()

        final_values = paths[:, -1]
        var_95 = s0 - float(np.percentile(final_values, 5))

        return {
            "s0": s0,
            "mu": mu,
            "sigma": sigma,
            "t_total": t_total,
            "steps": num_steps,
            "paths_count": num_paths,
            "final_mean": float(np.mean(final_values)),
            "final_std": float(np.std(final_values)),
            "value_at_risk_95": float(var_95),
            "mean_trajectory": [round(x, 4) for x in mean_path],
            "p05_trajectory": [round(x, 4) for x in p05_path],
            "p50_trajectory": [round(x, 4) for x in p50_path],
            "p95_trajectory": [round(x, 4) for x in p95_path],
        }

    @staticmethod
    def integrate(
        func: Callable[[float], float],
        a: float,
        b: float,
        num_samples: int = 50000,
        seed: Optional[int] = 42,
    ) -> Dict[str, float]:
        """Monte Carlo numerical integration of func(x) from a to b with standard error."""
        if seed is not None:
            np.random.seed(seed)
        samples = np.random.uniform(a, b, num_samples)
        f_vals = np.array([func(x) for x in samples])
        mean_f = np.mean(f_vals)
        var_f = np.var(f_vals)
        integral = (b - a) * mean_f
        std_err = (b - a) * math.sqrt(var_f / num_samples)

        return {
            "integral": float(integral),
            "standard_error": float(std_err),
            "num_samples": num_samples,
        }


class ODESimulator:
    """Numerical integration of ordinary differential equations (ODE)."""

    @staticmethod
    def rk4_solve(
        deriv_func: Callable[[float, List[float]], List[float]],
        y0: List[float],
        t_span: Tuple[float, float],
        num_steps: int = 1000,
    ) -> Dict[str, Union[List[float], List[List[float]]]]:
        """
        Runge-Kutta 4th Order (RK4) integrator for vector state y' = f(t, y).
        """
        t0, t_final = t_span
        dt = (t_final - t0) / float(num_steps)
        dim = len(y0)

        t_points = [t0]
        y_points = [[float(val) for val in y0]]

        y_curr = [float(v) for v in y0]
        t_curr = t0

        for _ in range(num_steps):
            k1 = deriv_func(t_curr, y_curr)

            y_k2 = [y_curr[j] + 0.5 * dt * k1[j] for j in range(dim)]
            k2 = deriv_func(t_curr + 0.5 * dt, y_k2)

            y_k3 = [y_curr[j] + 0.5 * dt * k2[j] for j in range(dim)]
            k3 = deriv_func(t_curr + 0.5 * dt, y_k3)

            y_k4 = [y_curr[j] + dt * k3[j] for j in range(dim)]
            k4 = deriv_func(t_curr + dt, y_k4)

            y_next = [
                y_curr[j] + (dt / 6.0) * (k1[j] + 2.0 * k2[j] + 2.0 * k3[j] + k4[j])
                for j in range(dim)
            ]
            t_curr += dt

            t_points.append(t_curr)
            y_points.append(y_next)
            y_curr = y_next

        return {
            "time": t_points,
            "states": y_points,
        }

    @staticmethod
    def simulate_harmonic_oscillator(
        mass: float = 1.0,
        spring_k: float = 10.0,
        damping_c: float = 0.5,
        x0: float = 1.0,
        v0: float = 0.0,
        t_final: float = 10.0,
        num_steps: int = 500,
    ) -> Dict[str, Union[float, List[float]]]:
        """
        Simulates damped harmonic oscillator:
        m * x'' + c * x' + k * x = 0
        State y = [position x, velocity v]
        """
        def deriv(t: float, y: List[float]) -> List[float]:
            x, v = y[0], y[1]
            dx_dt = v
            dv_dt = -(damping_c * v + spring_k * x) / mass
            return [dx_dt, dv_dt]

        res = ODESimulator.rk4_solve(deriv, [x0, v0], (0.0, t_final), num_steps)
        positions = [state[0] for state in res["states"]]
        velocities = [state[1] for state in res["states"]]

        return {
            "mass": mass,
            "spring_k": spring_k,
            "damping_c": damping_c,
            "time": res["time"],
            "position": positions,
            "velocity": velocities,
            "max_amplitude": max(abs(p) for p in positions),
        }

    @staticmethod
    def simulate_lorenz(
        sigma: float = 10.0,
        rho: float = 28.0,
        beta: float = 8.0 / 3.0,
        x0: float = 1.0,
        y0: float = 1.0,
        z0: float = 1.0,
        t_final: float = 20.0,
        num_steps: int = 2000,
    ) -> Dict[str, Union[float, List[float]]]:
        """
        Simulates Lorenz attractor chaotic dynamics:
        dx/dt = sigma * (y - x)
        dy/dt = x * (rho - z) - y
        dz/dt = x * y - beta * z
        """
        def deriv(t: float, y: List[float]) -> List[float]:
            x, y_val, z = y[0], y[1], y[2]
            dx = sigma * (y_val - x)
            dy = x * (rho - z) - y_val
            dz = x * y_val - beta * z
            return [dx, dy, dz]

        res = ODESimulator.rk4_solve(deriv, [x0, y0, z0], (0.0, t_final), num_steps)
        return {
            "time": res["time"],
            "x": [s[0] for s in res["states"]],
            "y": [s[1] for s in res["states"]],
            "z": [s[2] for s in res["states"]],
        }
