"""
Capability 105: Scheduled Research and Recurring Workflows
Manages interval and recurring jobs for scheduled literature sweeps,
continuous information gathering, and automated background routines.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable


@dataclass
class JobExecutionRecord:
    """Record of a single scheduled job execution."""
    timestamp: float
    duration_seconds: float
    success: bool
    output: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "duration_seconds": round(self.duration_seconds, 3),
            "success": self.success,
            "output": str(self.output)[:200] if self.output is not None else None,
            "error": self.error
        }


@dataclass
class ScheduledJob:
    """Definition of a scheduled recurring or interval job."""
    job_id: str
    name: str
    fn: Callable
    interval_seconds: float
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    next_run_at: float = field(default_factory=time.time)
    last_run_at: Optional[float] = None
    run_count: int = 0
    enabled: bool = True
    history: List[JobExecutionRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "name": self.name,
            "interval_seconds": self.interval_seconds,
            "next_run_at": self.next_run_at,
            "last_run_at": self.last_run_at,
            "run_count": self.run_count,
            "enabled": self.enabled,
            "recent_history": [h.to_dict() for h in self.history[-5:]],
            "metadata": self.metadata
        }


class AutonomousScheduler:
    """
    Capability 105: Autonomous Workflow & Research Scheduler.
    Executes recurring knowledge refreshes, research monitoring, and routine tasks.
    """

    def __init__(self):
        self.jobs: Dict[str, ScheduledJob] = {}

    def schedule_interval(self, name: str, interval_seconds: float, fn: Callable,
                          *args, initial_delay: float = 0.0, **kwargs) -> str:
        """Schedules a recurring function call every interval_seconds."""
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        next_run = time.time() + initial_delay
        job = ScheduledJob(
            job_id=job_id,
            name=name,
            fn=fn,
            interval_seconds=interval_seconds,
            args=args,
            kwargs=kwargs,
            next_run_at=next_run
        )
        self.jobs[job_id] = job
        return job_id

    def schedule_research(self, topic: str, interval_seconds: float = 3600.0,
                          research_handler: Optional[Callable] = None) -> str:
        """
        Schedules a recurring research sweep on a specific topic.
        """
        def default_sweep(query: str):
            return {
                "topic": query,
                "timestamp": time.time(),
                "status": "gathered_findings",
                "notes_scanned": 15,
                "synthesized_summary": f"Autonomous research update for '{query}'"
            }

        fn = research_handler or default_sweep
        job_id = self.schedule_interval(
            f"ResearchSweep_{topic}",
            interval_seconds,
            fn,
            topic
        )
        self.jobs[job_id].metadata["is_research"] = True
        self.jobs[job_id].metadata["topic"] = topic
        return job_id

    def tick(self, current_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Evaluates all registered jobs and executes any that are due.
        Returns a list of execution result dictionaries for completed runs.
        """
        now = current_time if current_time is not None else time.time()
        results: List[Dict[str, Any]] = []

        for job in list(self.jobs.values()):
            if not job.enabled:
                continue

            if now >= job.next_run_at:
                t0 = time.time()
                success = False
                output = None
                error = None

                try:
                    output = job.fn(*job.args, **job.kwargs)
                    success = True
                except Exception as e:
                    error = str(e)
                finally:
                    duration = time.time() - t0
                    rec = JobExecutionRecord(
                        timestamp=now,
                        duration_seconds=duration,
                        success=success,
                        output=output,
                        error=error
                    )
                    job.history.append(rec)
                    job.run_count += 1
                    job.last_run_at = now
                    job.next_run_at = now + job.interval_seconds

                    results.append({
                        "job_id": job.job_id,
                        "name": job.name,
                        "success": success,
                        "duration": round(duration, 3),
                        "output": output,
                        "error": error
                    })

        return results

    def cancel(self, job_id: str) -> bool:
        """Removes a scheduled job."""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False

    def enable(self, job_id: str) -> bool:
        """Enables a paused job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = True
            return True
        return False

    def disable(self, job_id: str) -> bool:
        """Disables a job without removing it."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = False
            return True
        return False

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves details of a specific job."""
        job = self.jobs.get(job_id)
        return job.to_dict() if job else None

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Lists all registered jobs."""
        return [j.to_dict() for j in self.jobs.values()]
