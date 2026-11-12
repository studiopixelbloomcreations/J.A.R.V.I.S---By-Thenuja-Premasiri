"""
Capability 107: Failure Recovery
Resilience framework providing error classification, exponential backoff with jitter,
circuit breakers, automatic fallback plans, and self-healing routines.
"""
from __future__ import annotations

import enum
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable


class ErrorCategory(str, enum.Enum):
    TRANSIENT = "TRANSIENT"      # Rate limits, network blips, lock timeouts (safe to retry)
    PERMANENT = "PERMANENT"      # Syntax errors, invalid schema, authorization failures
    RESOURCE = "RESOURCE"        # Disk full, missing directory, memory pressure
    UNKNOWN = "UNKNOWN"


def classify_error(exc: Exception) -> ErrorCategory:
    """Classifies an exception into transient, permanent, or resource categories."""
    msg = str(exc).lower()
    exc_type = type(exc).__name__.lower()

    if any(k in msg or k in exc_type for k in ["timeout", "timed out", "connection", "rate limit", "busy", "retry", "503", "429"]):
        return ErrorCategory.TRANSIENT
    if any(k in msg or k in exc_type for k in ["filenotfound", "not found", "nosuchfile", "directory", "disk full", "space"]):
        return ErrorCategory.RESOURCE
    if any(k in msg or k in exc_type for k in ["syntaxerror", "typeerror", "valueerror", "unauthorized", "permissionerror", "keyerror"]):
        return ErrorCategory.PERMANENT
    return ErrorCategory.UNKNOWN


@dataclass
class RetryPolicy:
    """Configurable backoff retry configuration."""
    max_retries: int = 3
    base_delay_seconds: float = 0.2
    max_delay_seconds: float = 5.0
    exponential_factor: float = 2.0
    jitter: bool = True

    def get_delay(self, attempt: int) -> float:
        """Calculates backoff delay with optional random jitter."""
        delay = self.base_delay_seconds * (self.exponential_factor ** attempt)
        delay = min(delay, self.max_delay_seconds)
        if self.jitter:
            delay += random.uniform(0, 0.1 * delay)
        return round(delay, 3)


class CircuitState(str, enum.Enum):
    CLOSED = "CLOSED"          # Normal operation, passes requests
    OPEN = "OPEN"              # Tripped, immediately fails fast
    HALF_OPEN = "HALF_OPEN"    # Probing recovery with limited canary requests


class CircuitBreaker:
    """Circuit breaker pattern to protect fragile downstream subsystems."""

    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: float = 15.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()

    def allow_request(self) -> bool:
        """Determines if a request should be allowed through."""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout elapsed
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = time.time()
                return True
            return False
        if self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self) -> None:
        """Registers a successful operation, resetting failure counters."""
        self.consecutive_failures = 0
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()

    def record_failure(self) -> None:
        """Registers an operational failure, tripping circuit if threshold reached."""
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "consecutive_failures": self.consecutive_failures,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time
        }


class FailureRecoveryManager:
    """
    Capability 107: Autonomous Failure Recovery Manager.
    Coordinates resilient execution, circuit breakers, fallbacks, and recovery diagnostics.
    """

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.recovery_log: List[Dict[str, Any]] = []

    def get_circuit_breaker(self, name: str, threshold: int = 3, timeout: float = 15.0) -> CircuitBreaker:
        """Retrieves or creates a named circuit breaker."""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name=name, failure_threshold=threshold, recovery_timeout=timeout)
        return self.circuit_breakers[name]

    def execute_with_resilience(self, action_name: str, fn: Callable, *args,
                                retry_policy: Optional[RetryPolicy] = None,
                                fallback_fn: Optional[Callable] = None,
                                cb_name: Optional[str] = None,
                                **kwargs) -> Any:
        """
        Executes a callable enveloped with circuit breaking, error classification,
        exponential backoff retries, and fallback handling.
        """
        policy = retry_policy or RetryPolicy()
        cb = self.get_circuit_breaker(cb_name) if cb_name else None

        if cb and not cb.allow_request():
            self._log_event(action_name, "CIRCUIT_BLOCKED", f"Circuit {cb.name} is OPEN.")
            if fallback_fn:
                self._log_event(action_name, "FALLBACK_TRIGGERED", "Invoking fallback due to tripped circuit.")
                return fallback_fn(*args, **kwargs)
            raise RuntimeError(f"Circuit breaker '{cb.name}' is OPEN. Request rejected.")

        last_exc = None
        for attempt in range(policy.max_retries + 1):
            try:
                result = fn(*args, **kwargs)
                if cb:
                    cb.record_success()
                self._log_event(action_name, "SUCCESS", f"Succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exc = e
                category = classify_error(e)
                if cb:
                    cb.record_failure()

                self._log_event(
                    action_name,
                    "FAILURE",
                    f"Attempt {attempt + 1} failed: [{category.value}] {str(e)}"
                )

                # If permanent error or out of retries, do not retry
                if category == ErrorCategory.PERMANENT or attempt == policy.max_retries:
                    break

                delay = policy.get_delay(attempt)
                time.sleep(delay)

        # Retries exhausted or permanent failure
        if fallback_fn:
            self._log_event(action_name, "FALLBACK_TRIGGERED", f"Falling back after {type(last_exc).__name__}")
            return fallback_fn(*args, **kwargs)

        raise last_exc

    def self_heal_path(self, path_str: str) -> bool:
        """Autonomous self-healing action: recreates missing directories safely."""
        import pathlib
        try:
            p = pathlib.Path(path_str)
            p.mkdir(parents=True, exist_ok=True)
            self._log_event("SELF_HEAL", "DIRECTORY_RECREATED", f"Recreated missing path {path_str}")
            return True
        except Exception as e:
            self._log_event("SELF_HEAL", "ERROR", f"Failed to self-heal path {path_str}: {str(e)}")
            return False

    def _log_event(self, action: str, outcome: str, detail: str) -> None:
        self.recovery_log.append({
            "timestamp": time.time(),
            "action": action,
            "outcome": outcome,
            "detail": detail
        })

    def get_summary(self) -> Dict[str, Any]:
        """Provides report of recovery actions and circuit breaker states."""
        return {
            "total_recovery_events": len(self.recovery_log),
            "recent_events": self.recovery_log[-10:],
            "circuit_breakers": {name: cb.to_dict() for name, cb in self.circuit_breakers.items()}
        }
