# J.A.R.V.I.S. Performance & Hardware Awareness Report
**Project:** J.A.R.V.I.S. Autonomous Operating Intelligence  
**System Version:** 2.0.0  
**Date:** 2026-11-12  

---

## 1. Execution Speed Benchmarks

All capability engines have been engineered for high efficiency on standard Windows hardware without requiring high-end dedicated GPUs or heavy local LLM memory overheads.

| Subsystem Test Suite | Capabilities | Test Count | Suite Execution Time | Average Latency / Test |
| :--- | :---: | :---: | :---: | :---: |
| `tests/test_intelligence.py` | 1–15 | 20 | 0.635s | ~31.8 ms |
| `tests/test_desktop.py` | 16–30 | 26 | 26.591s* | ~1.02 s |
| `tests/test_software.py` | 31–45 | 16 | 0.812s | ~50.8 ms |
| `tests/test_cybersecurity.py` | 46–60 | 32 | 3.718s | ~116.2 ms |
| `tests/test_science.py` | 61–75 | 53 | 1.497s | ~28.2 ms |
| `tests/test_creative.py` | 76–90 | 45 | 0.044s | ~0.98 ms |
| `tests/test_memory.py` | 91–100 | 35 | 14.880s | ~425.1 ms |
| `tests/test_autonomy.py` | 101–115 | 33 | 13.780s | ~417.6 ms |
| `tests/test_devices.py` | 116–125 | 51 | 23.925s | ~469.1 ms |
| `tests/test_visual.py` | 126–135 | 40 | 0.160s | ~4.0 ms |
| `tests/test_swarm_e2e.py` | Cross-Domain | 4 | 0.005s | ~1.25 ms |
| `tests/test_jarvis.py` | Core Regression | 38 | 23.954s | ~630.3 ms |
| **Total Test Suite** | **All 135 + E2E** | **393** | **~109.9s** | **~279 ms** |

*\*Desktop test times include real mouse interpolation delays, window geometry verification, and hardware sampling cycles.*

---

## 2. Resource-Aware Scheduling & Throttling

Managed by `jarvis/autonomy/resource_guard.py`:
- **Real-Time Telemetry**: Continuously monitors host CPU utilization and physical RAM via `psutil`.
- **Dynamic Throttle Modes**:
  - `NORMAL` (CPU < 65%, RAM < 75%): Full concurrency, background tasks proceed unconstrained.
  - `MODERATE` (CPU 65–80%): Concurrency capped at 2 parallel workers; background indexing paced.
  - `AGGRESSIVE` (CPU 80–92%): Single-worker serialization; non-essential tasks delayed.
  - `PAUSED` (CPU > 92% or RAM > 90%): Suspends background research to ensure UI and OS responsiveness.
- **Lazy Loading**: Domain engines are imported and instantiated on-demand rather than consuming massive memory pools at initial launch.
