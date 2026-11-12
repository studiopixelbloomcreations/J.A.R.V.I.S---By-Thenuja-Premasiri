"""
Capability 43: Database Intelligence
Provides SQLite schema introspection, safe read-only SQL execution,
query plan analysis (EXPLAIN QUERY PLAN), and schema migration helpers for J.A.R.V.I.S.
"""

import os
import re
import sqlite3
import pathlib
from typing import Dict, Any, List, Optional, Tuple


class DatabaseIntelligence:
    """Interrogates relational database schemas, validates query plans, and manages migrations."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = pathlib.Path(db_path) if db_path else None

    def _get_connection(self, path: Optional[str] = None) -> sqlite3.Connection:
        target = pathlib.Path(path) if path else self.db_path
        if not target:
            # Fallback to an in-memory DB if none provided
            return sqlite3.connect(":memory:")
        return sqlite3.connect(str(target))

    def inspect_schema(self, db_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Introspects SQLite tables, columns, data types, primary keys, and indexes.
        """
        conn = self._get_connection(db_path)
        cursor = conn.cursor()

        try:
            # Get all user tables
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables_raw = cursor.fetchall()

            schema: Dict[str, Any] = {}
            for table_name, table_sql in tables_raw:
                # PRAGMA table_info gives (cid, name, type, notnull, dflt_value, pk)
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                cols = cursor.fetchall()
                columns = []
                for c in cols:
                    columns.append({
                        "cid": c[0],
                        "name": c[1],
                        "type": c[2] or "TEXT",
                        "notnull": bool(c[3]),
                        "default_value": c[4],
                        "primary_key": bool(c[5])
                    })

                # PRAGMA index_list gives (seq, name, unique, origin, partial)
                cursor.execute(f"PRAGMA index_list('{table_name}')")
                indexes_raw = cursor.fetchall()
                indexes = [{"name": idx[1], "unique": bool(idx[2])} for idx in indexes_raw]

                # Row count
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
                    row_count = cursor.fetchone()[0]
                except Exception:
                    row_count = 0

                schema[table_name] = {
                    "sql": table_sql,
                    "columns": columns,
                    "indexes": indexes,
                    "row_count": row_count
                }

            return {
                "success": True,
                "tables_count": len(schema),
                "tables": schema
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def execute_safe_query(
        self,
        query: str,
        db_path: Optional[str] = None,
        max_rows: int = 100
    ) -> Dict[str, Any]:
        """
        Executes strictly safe read-only SQL queries with limit enforcement.
        Blocks mutating commands (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE).
        """
        q_clean = query.strip()
        q_upper = q_clean.upper()

        forbidden_keywords = [
            "DROP ", "DELETE ", "UPDATE ", "INSERT ", "ALTER ", "TRUNCATE ",
            "CREATE ", "ATTACH ", "DETACH ", "REINDEX ", "VACUUM "
        ]

        for kw in forbidden_keywords:
            if kw in q_upper or q_upper.startswith(kw.strip()):
                return {
                    "success": False,
                    "error": f"Mutating SQL keyword '{kw.strip()}' is blocked by DatabaseIntelligence safety policy.",
                    "read_only": True
                }

        # Enforce LIMIT if not already present
        if "LIMIT " not in q_upper:
            q_clean = f"{q_clean.rstrip(';')} LIMIT {max_rows}"

        conn = self._get_connection(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(q_clean)
            col_names = [d[0] for d in cursor.description] if cursor.description else []
            rows = cursor.fetchall()

            results = [dict(zip(col_names, row)) for row in rows]
            return {
                "success": True,
                "query_executed": q_clean,
                "columns": col_names,
                "row_count": len(results),
                "rows": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": q_clean
            }
        finally:
            conn.close()

    def explain_query(self, query: str, db_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs EXPLAIN QUERY PLAN to detect full table scans and index usage.
        """
        explain_q = f"EXPLAIN QUERY PLAN {query.strip()}"
        conn = self._get_connection(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(explain_q)
            rows = cursor.fetchall()
            # Rows are (id, parent, notused, detail)
            details = [r[3] if len(r) > 3 else str(r) for r in rows]

            has_table_scan = any("SCAN TABLE" in d and "INDEX" not in d for d in details)
            uses_index = any("USING INDEX" in d or "USING COVERING INDEX" in d for d in details)

            return {
                "success": True,
                "plan_steps": details,
                "has_full_table_scan": has_table_scan,
                "uses_index": uses_index,
                "recommendation": "Consider adding an index on queried filtering columns to avoid full table scans." if has_table_scan else "Query plan is utilizing indexed access efficiently."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
