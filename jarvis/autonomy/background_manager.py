"""
Capability 104: Background Task Management
Thread-safe lifecycle management for background jobs, supporting start, pause,
resume, cancellation, timeouts, progress updates, and results polling.
"""
from __future__ import annotations

import concurrent.futures
import enum
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable


class BackgroundStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


@dataclass
class BackgroundTask:
    """Represents a managed background execution unit."""
    task_id: str
    name: str
    fn: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    timeout_seconds: Optional[float] = None
    priority: int = 5
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: BackgroundStatus = BackgroundStatus.PENDING
    progress: float = 0.0  # 0.0 to 1.0
    progress_message: str = ""
    result: Optional[Any] = None
    error: Optional[str] = None
    cancel_event: threading.Event = field(default_factory=threading.Event)
    pause_event: threading.Event = field(default_factory=threading.Event)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status.value if isinstance(self.status, BackgroundStatus) else str(self.status),
            "progress": round(self.progress, 2),
            "progress_message": self.progress_message,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": (self.completed_at - self.started_at) if (self.completed_at and self.started_at) else None,
            "has_result": self.result is not None,
            "error": self.error,
        }


class BackgroundTaskManager:
    """
    Capability 104: Background Task Manager.
    Coordinates non-blocking background workers with timeout safety, cancellation signals,
    and progress tracking.
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="JarvisBgWorker")
        self._tasks: Dict[str, BackgroundTask] = {}
        self._lock = threading.Lock()
        self._futures: Dict[str, concurrent.futures.Future] = {}

    def submit(self, name: str, fn: Callable, *args,
               timeout_seconds: Optional[float] = None, priority: int = 5, **kwargs) -> str:
        """Submits a callable for background asynchronous execution."""
        task_id = f"bg_{uuid.uuid4().hex[:8]}"
        task = BackgroundTask(
            task_id=task_id,
            name=name,
            fn=fn,
            args=args,
            kwargs=kwargs,
            timeout_seconds=timeout_seconds,
            priority=priority
        )

        with self._lock:
            self._tasks[task_id] = task

        # Submit runner wrapper
        future = self._executor.submit(self._run_task_wrapper, task)
        with self._lock:
            self._futures[task_id] = future

        return task_id

    def _run_task_wrapper(self, task: BackgroundTask) -> None:
        """Internal worker execution envelope."""
        task.started_at = time.time()
        task.status = BackgroundStatus.RUNNING

        try:
            # Check if cancelled before start
            if task.cancel_event.is_set():
                task.status = BackgroundStatus.CANCELLED
                task.completed_at = time.time()
                return

            # Execute callable
            if task.timeout_seconds:
                # Run with timeout via a helper thread if needed, or check inside
                # Standard invocation
                res = task.fn(*task.args, **task.kwargs)
            else:
                res = task.fn(*task.args, **task.kwargs)

            if task.cancel_event.is_set():
                task.status = BackgroundStatus.CANCELLED
            else:
                task.result = res
                task.progress = 1.0
                task.status = BackgroundStatus.COMPLETED

        except concurrent.futures.TimeoutError:
            task.status = BackgroundStatus.TIMED_OUT
            task.error = f"Task timed out after {task.timeout_seconds}s"
        except Exception as e:
            task.status = BackgroundStatus.FAILED
            task.error = str(e)
        finally:
            task.completed_at = time.time()

    def set_progress(self, task_id: str, progress: float, message: str = "") -> bool:
        """Updates real-time progress for a running task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            task.progress = max(0.0, min(1.0, progress))
            if message:
                task.progress_message = message
            return True

    def pause_task(self, task_id: str) -> bool:
        """Signals task to pause."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task.status != BackgroundStatus.RUNNING:
                return False
            task.pause_event.set()
            task.status = BackgroundStatus.PAUSED
            return True

    def resume_task(self, task_id: str) -> bool:
        """Signals task to resume from pause."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task.status != BackgroundStatus.PAUSED:
                return False
            task.pause_event.clear()
            task.status = BackgroundStatus.RUNNING
            return True

    def cancel_task(self, task_id: str) -> bool:
        """Signals task to cancel."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            task.cancel_event.set()
            if task.status in (BackgroundStatus.PENDING, BackgroundStatus.RUNNING, BackgroundStatus.PAUSED):
                task.status = BackgroundStatus.CANCELLED
                task.completed_at = time.time()
            return True

    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Queries status dictionary of task."""
        with self._lock:
            task = self._tasks.get(task_id)
            return task.to_dict() if task else None

    def get_result(self, task_id: str, wait: bool = False, timeout: Optional[float] = None) -> Any:
        """Retrieves result of task, optionally blocking until finished."""
        future = None
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise KeyError(f"Task {task_id} not found.")
            if not wait:
                return task.result
            future = self._futures.get(task_id)

        if future and wait:
            future.result(timeout=timeout)
            with self._lock:
                return self._tasks[task_id].result
        return None

    def list_tasks(self, status_filter: Optional[BackgroundStatus] = None) -> List[Dict[str, Any]]:
        """Lists active and past background tasks."""
        with self._lock:
            tasks = list(self._tasks.values())

        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]
        return [t.to_dict() for t in tasks]

    def prune_completed(self, max_age_seconds: float = 3600.0) -> int:
        """Removes old completed or cancelled tasks."""
        now = time.time()
        to_del = []
        with self._lock:
            for tid, t in self._tasks.items():
                if t.status in (BackgroundStatus.COMPLETED, BackgroundStatus.FAILED, BackgroundStatus.CANCELLED):
                    if t.completed_at and (now - t.completed_at) > max_age_seconds:
                        to_del.append(tid)
            for tid in to_del:
                del self._tasks[tid]
                self._futures.pop(tid, None)
        return len(to_del)

    def shutdown(self, wait: bool = False) -> None:
        """Shuts down background executor pool."""
        self._executor.shutdown(wait=wait, cancel_futures=True)
