"""
Capability 44: API Testing
Performs automated REST endpoint validation, latency benchmarking,
and JSON response schema verification for J.A.R.V.I.S.
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional


class APITester:
    """Executes HTTP endpoint calls, parses responses, and validates schemas."""

    def __init__(self, base_url: str = "http://127.0.0.1:4700"):
        self.base_url = base_url.rstrip("/")

    def test_endpoint(
        self,
        endpoint_or_url: str,
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """
        Executes an HTTP request and measures status, latency, headers, and parsed body.
        """
        url = endpoint_or_url if endpoint_or_url.startswith("http") else f"{self.base_url}/{endpoint_or_url.lstrip('/')}"
        hdrs = headers or {}
        hdrs.setdefault("User-Agent", "JARVIS-APITester/2.0")

        data_bytes = None
        if payload is not None:
            data_bytes = json.dumps(payload).encode("utf-8")
            hdrs.setdefault("Content-Type", "application/json")

        req = urllib.request.Request(url, data=data_bytes, headers=hdrs, method=method.upper())
        start_time = time.time()

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                latency_ms = round((time.time() - start_time) * 1000, 2)
                status_code = resp.status
                body_bytes = resp.read()
                raw_text = body_bytes.decode("utf-8", errors="replace")
                
                json_data = None
                try:
                    json_data = json.loads(raw_text)
                except Exception:
                    pass

                return {
                    "success": 200 <= status_code < 300,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "url": url,
                    "method": method.upper(),
                    "json": json_data,
                    "text": raw_text[:500] if json_data is None else None,
                    "headers": dict(resp.headers)
                }

        except urllib.error.HTTPError as he:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            raw_text = he.read().decode("utf-8", errors="replace")
            json_data = None
            try:
                json_data = json.loads(raw_text)
            except Exception:
                pass

            return {
                "success": False,
                "status_code": he.code,
                "latency_ms": latency_ms,
                "url": url,
                "method": method.upper(),
                "error": str(he),
                "json": json_data,
                "text": raw_text[:500]
            }

        except Exception as e:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "status_code": 0,
                "latency_ms": latency_ms,
                "url": url,
                "method": method.upper(),
                "error": str(e)
            }

    def validate_schema(self, data: Dict[str, Any], schema_spec: Dict[str, type]) -> Dict[str, Any]:
        """
        Validates JSON dictionary against expected field types.
        Example: {"status": str, "count": int}
        """
        missing_fields = []
        type_mismatches = []

        for field, expected_type in schema_spec.items():
            if field not in data:
                missing_fields.append(field)
            elif not isinstance(data[field], expected_type):
                type_mismatches.append({
                    "field": field,
                    "expected": expected_type.__name__,
                    "actual": type(data[field]).__name__
                })

        valid = len(missing_fields) == 0 and len(type_mismatches) == 0
        return {
            "valid": valid,
            "missing_fields": missing_fields,
            "type_mismatches": type_mismatches
        }

    def benchmark_endpoint(
        self,
        endpoint_or_url: str,
        iterations: int = 5,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Runs repeated calls to measure latency statistics (min, max, average).
        """
        latencies: List[float] = []
        success_count = 0

        for _ in range(iterations):
            res = self.test_endpoint(endpoint_or_url, method=method)
            latencies.append(res["latency_ms"])
            if res["success"]:
                success_count += 1

        avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
        min_lat = min(latencies) if latencies else 0.0
        max_lat = max(latencies) if latencies else 0.0

        return {
            "endpoint": endpoint_or_url,
            "iterations": iterations,
            "successful_calls": success_count,
            "success_rate_pct": round((success_count / iterations) * 100, 1),
            "latency_ms": {
                "avg": avg_lat,
                "min": min_lat,
                "max": max_lat
            }
        }
