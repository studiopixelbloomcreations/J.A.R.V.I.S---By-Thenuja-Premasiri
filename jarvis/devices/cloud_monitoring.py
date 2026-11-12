"""
Capability 123: Cloud Resource Monitoring
Monitors external cloud services and LLM API endpoints (Gemini, OpenAI, GitHub, Cloudflare),
tracks latency, validates rate limit / quota headers, and enforces circuit breakers.
"""

import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class APIHealthProbe:
    endpoint_name: str
    url: str
    status_code: Optional[int] = None
    is_healthy: bool = False
    latency_ms: Optional[float] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_limit: Optional[int] = None
    quota_used_pct: Optional[float] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class CircuitBreaker:
    """Implements Circuit Breaker pattern to protect against failing remote APIs."""

    def __init__(self, failure_threshold: int = 3, recovery_time_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time_seconds
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0.0

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if (time.time() - self.last_failure_time) >= self.recovery_time:
                self.state = "HALF_OPEN"
                return True
            return False
        # HALF_OPEN allows single test call
        return True


class CloudResourceMonitor:
    """Monitors cloud providers, LLM API gateways, rate limits, and service SLAs."""

    DEFAULT_ENDPOINTS = {
        "Gemini API": "https://generativelanguage.googleapis.com",
        "OpenAI API": "https://api.openai.com/v1/models",
        "GitHub API": "https://api.github.com",
        "Cloudflare Edge": "https://1.1.1.1",
        "AWS Status": "https://status.aws.amazon.com",
    }

    def __init__(self):
        self._endpoints: Dict[str, str] = dict(self.DEFAULT_ENDPOINTS)
        self._history: Dict[str, List[APIHealthProbe]] = {}
        self._breakers: Dict[str, CircuitBreaker] = {}
        for name in self._endpoints:
            self._history[name] = []
            self._breakers[name] = CircuitBreaker()

    def register_endpoint(self, name: str, url: str):
        """Adds a custom cloud endpoint or webhook to monitor."""
        self._endpoints[name] = url
        if name not in self._history:
            self._history[name] = []
            self._breakers[name] = CircuitBreaker()

    def probe_endpoint(self, name: str, timeout: float = 2.0) -> APIHealthProbe:
        """Executes synthetic HTTP probe, measuring latency and parsing rate limit headers."""
        url = self._endpoints.get(name)
        if not url:
            return APIHealthProbe(endpoint_name=name, url="", error=f"Endpoint {name} not found")

        breaker = self._breakers[name]
        if not breaker.can_execute():
            probe = APIHealthProbe(
                endpoint_name=name,
                url=url,
                is_healthy=False,
                error=f"Circuit Breaker is OPEN ({breaker.state})",
            )
            self._history[name].append(probe)
            return probe

        start = time.perf_counter()
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "JARVIS-HealthMonitor/2.0"},
            method="GET"
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                status_code = response.getcode()
                headers = response.headers

                # Parse rate limit headers
                rem = headers.get("x-ratelimit-remaining")
                lim = headers.get("x-ratelimit-limit")
                remaining = int(rem) if rem and rem.isdigit() else None
                limit = int(lim) if lim and lim.isdigit() else None
                quota_pct = None
                if remaining is not None and limit is not None and limit > 0:
                    quota_pct = round(((limit - remaining) / limit) * 100.0, 1)

                probe = APIHealthProbe(
                    endpoint_name=name,
                    url=url,
                    status_code=status_code,
                    is_healthy=(200 <= status_code < 400),
                    latency_ms=round(elapsed_ms, 2),
                    rate_limit_remaining=remaining,
                    rate_limit_limit=limit,
                    quota_used_pct=quota_pct
                )
                breaker.record_success()

        except urllib.error.HTTPError as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            # 401 or 403 means reachable endpoint, but unauthenticated, still an alive server
            is_alive = e.code in (401, 403, 404)
            probe = APIHealthProbe(
                endpoint_name=name,
                url=url,
                status_code=e.code,
                is_healthy=is_alive,
                latency_ms=round(elapsed_ms, 2),
                error=f"HTTP {e.code}: {e.reason}"
            )
            if is_alive:
                breaker.record_success()
            else:
                breaker.record_failure()

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            probe = APIHealthProbe(
                endpoint_name=name,
                url=url,
                is_healthy=False,
                latency_ms=round(elapsed_ms, 2),
                error=str(e)
            )
            breaker.record_failure()

        self._history[name].append(probe)
        return probe

    def probe_all(self, timeout: float = 1.5) -> List[APIHealthProbe]:
        """Runs health checks across all registered cloud endpoints."""
        results = []
        for name in list(self._endpoints.keys()):
            results.append(self.probe_endpoint(name, timeout=timeout))
        return results

    def get_sla_metrics(self, endpoint_name: str) -> Dict[str, Any]:
        """Calculates rolling uptime SLA percentage and average latency."""
        history = self._history.get(endpoint_name, [])
        if not history:
            return {"uptime_pct": 100.0, "avg_latency_ms": None, "samples": 0}

        successful = [p for p in history if p.is_healthy]
        uptime_pct = (len(successful) / len(history)) * 100.0

        latencies = [p.latency_ms for p in successful if p.latency_ms is not None]
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

        return {
            "uptime_pct": round(uptime_pct, 2),
            "avg_latency_ms": avg_latency,
            "samples": len(history),
            "circuit_state": self._breakers[endpoint_name].state
        }

    def get_cloud_dashboard(self) -> Dict[str, Any]:
        """Compiles cloud API availability and quota telemetry snapshot."""
        endpoints_data = {}
        all_healthy = True

        for name in self._endpoints:
            history = self._history.get(name, [])
            latest = history[-1] if history else None
            sla = self.get_sla_metrics(name)

            if latest and not latest.is_healthy:
                all_healthy = False

            endpoints_data[name] = {
                "url": self._endpoints[name],
                "latest_status": asdict(latest) if latest else None,
                "sla": sla
            }

        return {
            "status": "nominal" if all_healthy else "degraded",
            "endpoint_count": len(self._endpoints),
            "endpoints": endpoints_data
        }
