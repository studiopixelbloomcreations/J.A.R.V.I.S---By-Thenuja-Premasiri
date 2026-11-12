"""
Capability 124: Database Monitoring
Performs SQLite integrity checks, page and WAL statistics, table inventories,
query latency benchmarks, and PostgreSQL connection health probes.
"""

import os
import sqlite3
import socket
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class SQLiteHealthReport:
    db_path: str
    file_size_bytes: int = 0
    is_healthy: bool = False
    integrity_result: str = "unknown"
    quick_check_result: str = "unknown"
    page_count: int = 0
    page_size: int = 4096
    freelist_count: int = 0
    fragmentation_pct: float = 0.0
    journal_mode: str = "delete"
    tables: Dict[str, int] = field(default_factory=dict)
    index_count: int = 0
    benchmark_read_ms: float = 0.0
    benchmark_write_ms: float = 0.0


@dataclass
class SlowQueryRecord:
    query: str
    duration_ms: float
    timestamp: float = field(default_factory=time.time)
    database: str = "sqlite"


class DatabaseMonitor:
    """Monitors local SQLite repositories and external PostgreSQL database instances."""

    def __init__(self, default_db_path: Optional[str] = None, slow_query_threshold_ms: float = 50.0):
        self.default_db_path = default_db_path
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self._slow_queries: List[SlowQueryRecord] = []

    def inspect_sqlite(self, db_path: Optional[str] = None) -> SQLiteHealthReport:
        """
        Executes full SQLite PRAGMA integrity inspection, page analysis,
        and table inventory.
        """
        target_path = db_path or self.default_db_path or ":memory:"
        is_memory = (target_path == ":memory:")

        file_size = 0
        if not is_memory and os.path.exists(target_path):
            file_size = os.path.getsize(target_path)

        report = SQLiteHealthReport(db_path=target_path, file_size_bytes=file_size)

        try:
            conn = sqlite3.connect(target_path)
            cursor = conn.cursor()

            # Integrity check
            cursor.execute("PRAGMA integrity_check;")
            integrity_row = cursor.fetchone()
            report.integrity_result = integrity_row[0] if integrity_row else "error"
            report.is_healthy = (report.integrity_result.lower() == "ok")

            # Quick check
            cursor.execute("PRAGMA quick_check;")
            quick_row = cursor.fetchone()
            report.quick_check_result = quick_row[0] if quick_row else "error"

            # Page and WAL stats
            cursor.execute("PRAGMA page_count;")
            report.page_count = cursor.fetchone()[0]

            cursor.execute("PRAGMA page_size;")
            report.page_size = cursor.fetchone()[0]

            cursor.execute("PRAGMA freelist_count;")
            report.freelist_count = cursor.fetchone()[0]

            if report.page_count > 0:
                report.fragmentation_pct = round((report.freelist_count / report.page_count) * 100.0, 2)

            cursor.execute("PRAGMA journal_mode;")
            report.journal_mode = cursor.fetchone()[0].lower()

            # Table inventory & row counts
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]

            for t in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM `{t}`;")
                    report.tables[t] = cursor.fetchone()[0]
                except Exception:
                    report.tables[t] = 0

            # Indices count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index';")
            report.index_count = cursor.fetchone()[0]

            # Benchmark read latency
            t0 = time.perf_counter()
            cursor.execute("SELECT 1;")
            cursor.fetchone()
            report.benchmark_read_ms = round((time.perf_counter() - t0) * 1000.0, 3)

            # Benchmark write latency in transaction
            t1 = time.perf_counter()
            cursor.execute("CREATE TABLE IF NOT EXISTS _jarvis_bench (id INTEGER PRIMARY KEY, ts REAL);")
            cursor.execute("INSERT INTO _jarvis_bench (ts) VALUES (?);", (time.time(),))
            conn.commit()
            cursor.execute("DROP TABLE IF EXISTS _jarvis_bench;")
            conn.commit()
            report.benchmark_write_ms = round((time.perf_counter() - t1) * 1000.0, 3)

            conn.close()

        except Exception as e:
            report.is_healthy = False
            report.integrity_result = f"Exception: {str(e)}"

        return report

    def record_query_execution(self, query: str, duration_ms: float, database: str = "sqlite"):
        """Logs queries that surpass the slow query threshold."""
        if duration_ms >= self.slow_query_threshold_ms:
            self._slow_queries.append(SlowQueryRecord(
                query=query.strip(),
                duration_ms=round(duration_ms, 2),
                database=database
            ))

    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Returns captured slow queries."""
        return [asdict(q) for q in self._slow_queries]

    def check_postgres_health(
        self,
        host: str = "localhost",
        port: int = 5432,
        dbname: str = "postgres",
        timeout: float = 1.0
    ) -> Dict[str, Any]:
        """
        Probes PostgreSQL connectivity via socket handshake and measures latency.
        """
        start = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        is_connected = False
        err = None
        try:
            res = sock.connect_ex((host, port))
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            if res == 0:
                is_connected = True
            else:
                err = f"Connection error {res}"
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            err = str(e)
        finally:
            try:
                sock.close()
            except Exception:
                pass

        return {
            "database_type": "PostgreSQL",
            "host": host,
            "port": port,
            "dbname": dbname,
            "reachable": is_connected,
            "latency_ms": round(elapsed_ms, 2) if is_connected else None,
            "error": err
        }

    def get_database_dashboard(self, sqlite_path: Optional[str] = None) -> Dict[str, Any]:
        """Compiles unified database telemetry dashboard."""
        sqlite_report = self.inspect_sqlite(sqlite_path)
        pg_check = self.check_postgres_health()

        return {
            "status": "nominal" if sqlite_report.is_healthy else "degraded",
            "sqlite": asdict(sqlite_report),
            "postgresql": pg_check,
            "slow_query_count": len(self._slow_queries),
            "slow_queries": self.get_slow_queries()[:10]
        }
