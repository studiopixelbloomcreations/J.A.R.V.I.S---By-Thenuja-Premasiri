"""
Mathematical Reasoning Engine (Capability 61)
Provides symbolic-like parsing, safe AST evaluation, numerical differentiation,
numerical integration, root-finding algorithms, polynomial analysis, and linear system solvers.
"""

import ast
import math
import operator
from typing import Callable, Dict, List, Optional, Tuple, Union
import numpy as np

# Safe binary and unary operators mapping
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "sqrt": math.sqrt,
    "abs": abs,
    "ceil": math.ceil,
    "floor": math.floor,
    "radians": math.radians,
    "degrees": math.degrees,
}

SAFE_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": float("inf"),
}


class ExpressionEvaluator:
    """Safe mathematical expression evaluator using Python AST parsing."""

    def __init__(self, variables: Optional[Dict[str, float]] = None):
        self.variables = dict(variables or {})

    def set_variable(self, name: str, value: float) -> None:
        self.variables[name] = float(value)

    def evaluate(self, expr_str: str, local_vars: Optional[Dict[str, float]] = None) -> float:
        context = dict(self.variables)
        if local_vars:
            context.update(local_vars)
        # normalize common caret ^ to **
        normalized = expr_str.replace("^", "**")
        node = ast.parse(normalized, mode="eval")
        return self._eval_node(node.body, context)

    def _eval_node(self, node: ast.AST, context: Dict[str, float]) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        if isinstance(node, ast.Name):
            if node.id in context:
                return float(context[node.id])
            if node.id in SAFE_CONSTANTS:
                return SAFE_CONSTANTS[node.id]
            raise ValueError(f"Unknown identifier: {node.id}")

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in SAFE_OPERATORS:
                operand = self._eval_node(node.operand, context)
                return SAFE_OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type}")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in SAFE_OPERATORS:
                left = self._eval_node(node.left, context)
                right = self._eval_node(node.right, context)
                return SAFE_OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type}")

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCTIONS:
                func = SAFE_FUNCTIONS[node.func.id]
                args = [self._eval_node(arg, context) for arg in node.args]
                return float(func(*args))
            raise ValueError(f"Function call not permitted: {getattr(node.func, 'id', 'anonymous')}")

        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def safe_eval_math(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    """Convenience helper to safely evaluate mathematical expressions."""
    evaluator = ExpressionEvaluator(variables)
    return evaluator.evaluate(expr)


# --- Numerical Calculus ---

def numerical_derivative(
    func: Callable[[float], float],
    x: float,
    h: float = 1e-5,
    method: str = "central",
) -> float:
    """
    Computes numerical derivative f'(x).
    Methods: 'central' (O(h^2)), 'forward' (O(h)), 'backward' (O(h)).
    """
    if method == "central":
        return (func(x + h) - func(x - h)) / (2.0 * h)
    elif method == "forward":
        return (func(x + h) - func(x)) / h
    elif method == "backward":
        return (func(x) - func(x - h)) / h
    else:
        raise ValueError(f"Unknown differentiation method: {method}")


def second_derivative(func: Callable[[float], float], x: float, h: float = 1e-4) -> float:
    """Computes second numerical derivative f''(x) using central difference."""
    return (func(x + h) - 2.0 * func(x) + func(x - h)) / (h * h)


def gradient(
    func: Callable[[List[float]], float],
    point: List[float],
    h: float = 1e-5,
) -> List[float]:
    """Computes gradient vector of a scalar function f(x1, x2, ...)."""
    grad = []
    p = list(point)
    for i in range(len(p)):
        old_val = p[i]
        p[i] = old_val + h
        f_plus = func(p)
        p[i] = old_val - h
        f_minus = func(p)
        p[i] = old_val
        grad.append((f_plus - f_minus) / (2.0 * h))
    return grad


def integrate_trapezoidal(
    func: Callable[[float], float],
    a: float,
    b: float,
    n: int = 1000,
) -> float:
    """Numerical integration via composite Trapezoidal rule."""
    if n <= 0:
        raise ValueError("n must be positive integer")
    h = (b - a) / float(n)
    total = 0.5 * (func(a) + func(b))
    for i in range(1, n):
        total += func(a + i * h)
    return total * h


def integrate_simpson(
    func: Callable[[float], float],
    a: float,
    b: float,
    n: int = 1000,
) -> float:
    """Numerical integration via composite Simpson's 1/3 rule (n must be even)."""
    if n % 2 != 0:
        n += 1
    h = (b - a) / float(n)
    total = func(a) + func(b)
    for i in range(1, n, 2):
        total += 4.0 * func(a + i * h)
    for i in range(2, n, 2):
        total += 2.0 * func(a + i * h)
    return (h / 3.0) * total


# --- Root Finding & Polynomials ---

def root_bisection(
    func: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-7,
    max_iter: int = 100,
) -> Dict[str, Union[float, int, bool]]:
    """Finds root in bracket [a, b] using bisection method."""
    fa = func(a)
    fb = func(b)
    if fa * fb > 0:
        raise ValueError("Function values at interval endpoints must have opposite signs.")

    mid = a
    for it in range(1, max_iter + 1):
        mid = (a + b) / 2.0
        fmid = func(mid)
        if abs(fmid) < tol or (b - a) / 2.0 < tol:
            return {"root": mid, "iterations": it, "converged": True, "f_val": fmid}
        if fa * fmid < 0:
            b = mid
            fb = fmid
        else:
            a = mid
            fa = fmid

    return {"root": mid, "iterations": max_iter, "converged": False, "f_val": func(mid)}


def root_newton_raphson(
    func: Callable[[float], float],
    x0: float,
    fprime: Optional[Callable[[float], float]] = None,
    tol: float = 1e-7,
    max_iter: int = 100,
) -> Dict[str, Union[float, int, bool]]:
    """Finds root starting from x0 using Newton-Raphson iteration."""
    x = x0
    for it in range(1, max_iter + 1):
        fx = func(x)
        if abs(fx) < tol:
            return {"root": x, "iterations": it, "converged": True, "f_val": fx}
        dfx = fprime(x) if fprime else numerical_derivative(func, x)
        if abs(dfx) < 1e-12:
            return {"root": x, "iterations": it, "converged": False, "f_val": fx, "error": "Zero derivative encountered"}
        x_next = x - fx / dfx
        if abs(x_next - x) < tol:
            return {"root": x_next, "iterations": it, "converged": True, "f_val": func(x_next)}
        x = x_next

    return {"root": x, "iterations": max_iter, "converged": False, "f_val": func(x)}


def polynomial_roots(coeffs: List[float]) -> List[complex]:
    """
    Computes all roots of polynomial P(x) = c_n x^n + ... + c_1 x + c_0.
    Input coeffs are ordered from highest degree to lowest degree [c_n, ..., c_0].
    Uses companion matrix eigenvalue approach via numpy.
    """
    # Strip leading zeros
    while coeffs and abs(coeffs[0]) < 1e-12:
        coeffs = coeffs[1:]
    if len(coeffs) <= 1:
        return []
    if len(coeffs) == 2:
        # c1 * x + c0 = 0 -> x = -c0 / c1
        return [complex(-coeffs[1] / coeffs[0], 0.0)]
    if len(coeffs) == 3:
        # Quadratic formula: ax^2 + bx + c = 0
        a, b, c = coeffs[0], coeffs[1], coeffs[2]
        disc = b * b - 4 * a * c
        if disc >= 0:
            sq = math.sqrt(disc)
            return [complex((-b + sq) / (2 * a), 0.0), complex((-b - sq) / (2 * a), 0.0)]
        else:
            sq = math.sqrt(-disc)
            return [complex(-b / (2 * a), sq / (2 * a)), complex(-b / (2 * a), -sq / (2 * a))]

    # General companion matrix
    poly_norm = np.array(coeffs, dtype=float) / coeffs[0]
    roots = np.roots(poly_norm)
    return [complex(r) for r in roots]


# --- Linear Algebra Solvers ---

def solve_linear_system(A: List[List[float]], b: List[float]) -> List[float]:
    """
    Solves A * x = b using Gaussian elimination with partial pivoting.
    """
    n = len(A)
    if any(len(row) != n for row in A) or len(b) != n:
        raise ValueError("Matrix A must be square and dimension must match vector b.")

    # Augmented matrix
    M = [list(A[i]) + [float(b[i])] for i in range(n)]

    for i in range(n):
        # Pivot search
        max_row = i
        max_val = abs(M[i][i])
        for r in range(i + 1, n):
            if abs(M[r][i]) > max_val:
                max_val = abs(M[r][i])
                max_row = r
        if max_val < 1e-12:
            raise ValueError("Singular or near-singular matrix cannot be solved uniquely.")

        if max_row != i:
            M[i], M[max_row] = M[max_row], M[i]

        pivot = M[i][i]
        for c in range(i, n + 1):
            M[i][c] /= pivot

        for r in range(n):
            if r != i:
                factor = M[r][i]
                for c in range(i, n + 1):
                    M[r][c] -= factor * M[i][c]

    return [M[i][n] for i in range(n)]


def matrix_determinant(A: List[List[float]]) -> float:
    """Computes determinant of square matrix A."""
    arr = np.array(A, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("Matrix must be 2D square array.")
    return float(np.linalg.det(arr))


def matrix_inverse(A: List[List[float]]) -> List[List[float]]:
    """Computes inverse of square matrix A."""
    det = matrix_determinant(A)
    if abs(det) < 1e-12:
        raise ValueError("Matrix is singular and non-invertible.")
    arr = np.array(A, dtype=float)
    inv = np.linalg.inv(arr)
    return inv.tolist()
