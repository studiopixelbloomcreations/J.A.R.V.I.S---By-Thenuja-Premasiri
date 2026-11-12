"""
Capability 113: Task Continuity (Checkpoint & State Resumption)
Provides atomic persistence of DAG states, completed task node outputs, and context snapshots,
enabling zero-loss recovery and task resumption after crashes or interruptions.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Any, Optional, Tuple

from ..config import DATA_DIR
from .task_planner import TaskDAG, TaskNode, TaskStatus

CHECKPOINT_DIR = pathlib.Path(DATA_DIR) / "autonomy" / "checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class CheckpointRecord:
    """Serialized snapshot of an in-flight workflow."""
    checkpoint_id: str
    workflow_id: str
    timestamp: float
    dag_state: Dict[str, Any]
    completed_task_ids: List[str]
    intermediate_outputs: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CheckpointRecord:
        return cls(**data)


class CheckpointManager:
    """
    Capability 113: Autonomous Checkpoint & Continuity Manager.
    Manages snapshot creation, file system integrity, and seamless resumption of task DAGs.
    """

    def __init__(self, storage_dir: Optional[pathlib.Path] = None):
        self.storage_dir = storage_dir or CHECKPOINT_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _compute_checksum(self, payload: Dict[str, Any]) -> str:
        """Calculates deterministic SHA-256 hash of payload."""
        s = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def save_checkpoint(self, workflow_id: str, dag: TaskDAG,
                        completed_ids: Set[str],
                        intermediate_outputs: Optional[Dict[str, Any]] = None,
                        context: Optional[Dict[str, Any]] = None) -> str:
        """
        Atomically writes a state checkpoint to disk.
        """
        checkpoint_id = f"chk_{workflow_id}_{uuid.uuid4().hex[:8]}"
        payload = {
            "checkpoint_id": checkpoint_id,
            "workflow_id": workflow_id,
            "timestamp": time.time(),
            "dag_state": dag.to_dict(),
            "completed_task_ids": sorted(list(completed_ids)),
            "intermediate_outputs": intermediate_outputs or {},
            "context": context or {}
        }
        checksum = self._compute_checksum(payload)
        payload["checksum"] = checksum

        record = CheckpointRecord.from_dict(payload)
        file_path = self.storage_dir / f"{checkpoint_id}.json"
        tmp_path = self.storage_dir / f"{checkpoint_id}.tmp"

        # Atomic write
        tmp_path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
        tmp_path.replace(file_path)

        return checkpoint_id

    def load_checkpoint(self, checkpoint_id: str) -> CheckpointRecord:
        """Loads and verifies a checkpoint file."""
        file_path = self.storage_dir / f"{checkpoint_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found at {file_path}")

        data = json.loads(file_path.read_text(encoding="utf-8"))
        stored_checksum = data.get("checksum", "")

        # Verify integrity
        verify_data = dict(data)
        verify_data.pop("checksum", None)
        calc_checksum = self._compute_checksum(verify_data)
        if stored_checksum and stored_checksum != calc_checksum:
            raise ValueError(f"Checkpoint integrity violation for {checkpoint_id}: checksum mismatch.")

        return CheckpointRecord.from_dict(data)

    def get_latest_checkpoint(self, workflow_id: str) -> Optional[CheckpointRecord]:
        """Finds the most recent checkpoint for a given workflow."""
        candidates = []
        for p in self.storage_dir.glob(f"chk_{workflow_id}_*.json"):
            try:
                rec = self.load_checkpoint(p.stem)
                candidates.append(rec)
            except Exception:
                pass

        if not candidates:
            return None
        candidates.sort(key=lambda x: x.timestamp, reverse=True)
        return candidates[0]

    def restore_execution(self, checkpoint_id: str) -> Tuple[TaskDAG, Set[str], Dict[str, Any]]:
        """
        Restores a TaskDAG to its exact execution state from checkpoint.
        Marks completed nodes, sets intermediate outputs, and identifies remaining tasks.
        """
        record = self.load_checkpoint(checkpoint_id)
        dag = TaskDAG.from_dict(record.dag_state)
        completed_ids = set(record.completed_task_ids)

        for tid in completed_ids:
            if tid in dag.tasks:
                dag.tasks[tid].status = TaskStatus.COMPLETED
                if tid in record.intermediate_outputs:
                    dag.tasks[tid].result = record.intermediate_outputs[tid]

        return dag, completed_ids, record.intermediate_outputs

    def prune_old_checkpoints(self, workflow_id: str, keep_latest: int = 3) -> int:
        """Removes older checkpoints for a workflow, preserving the most recent N."""
        files = list(self.storage_dir.glob(f"chk_{workflow_id}_*.json"))
        if len(files) <= keep_latest:
            return 0

        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        to_remove = files[keep_latest:]
        for p in to_remove:
            try:
                p.unlink()
            except Exception:
                pass
        return len(to_remove)
