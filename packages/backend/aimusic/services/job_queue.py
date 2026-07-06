"""
Job Queue — async background task management.

Provides a thread-safe in-process job queue for long-running tasks
(rendering, exporting, AI generation). Uses Python threading for
Phase 7; Celery/RQ can replace this in production.

Job lifecycle:
  PENDING → RUNNING → COMPLETED | FAILED | CANCELLED
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """A background job with progress tracking."""
    id: str
    job_type: str                   # "render" | "export" | "ai_generate" | "seed"
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0           # 0.0 – 1.0
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status.value,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }


class JobQueue:
    """
    Thread-safe in-process job queue.

    Create a queue, submit jobs, poll for results.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._semaphore = threading.Semaphore(max_workers)

    # ── Public API ────────────────────────────────────────────────────────────

    def submit(
        self,
        job_type: str,
        fn: Callable[["Job"], Any],
        metadata: Optional[dict] = None,
    ) -> Job:
        """
        Submit a function to run in a background thread.

        The function receives the Job instance and should update
        `job.progress` (0.0–1.0) as it works. Return value is stored
        as `job.result`.

        Args:
            job_type: Label (e.g. "render", "export").
            fn: Callable that accepts a Job instance.
            metadata: Optional data attached to the job.

        Returns:
            Job instance (status: PENDING).
        """
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, job_type=job_type, metadata=metadata or {})

        with self._lock:
            self._jobs[job_id] = job

        thread = threading.Thread(
            target=self._run,
            args=(job, fn),
            daemon=True,
            name=f"sonmancer-job-{job_id[:8]}",
        )
        thread.start()
        logger.info(f"Job submitted: {job_id} ({job_type})")
        return job

    def get(self, job_id: str) -> Optional[Job]:
        """Return job by ID, or None if not found."""
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(
        self,
        job_type: Optional[str] = None,
        status: Optional[JobStatus] = None,
        limit: int = 50,
    ) -> list[Job]:
        """Return recent jobs, optionally filtered."""
        with self._lock:
            jobs = list(self._jobs.values())

        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]
        if status:
            jobs = [j for j in jobs if j.status == status]

        # Sort by created_at descending
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return jobs[:limit]

    def cancel(self, job_id: str) -> bool:
        """
        Request cancellation of a PENDING or RUNNING job.

        Note: cancellation is cooperative — the job function must
        check `job.status == CANCELLED` and exit early.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                return False
            job.status = JobStatus.CANCELLED
            return True

    def clear_completed(self, older_than_seconds: int = 3600) -> int:
        """Remove completed/failed jobs older than N seconds. Returns count removed."""
        cutoff = datetime.utcnow().timestamp() - older_than_seconds
        to_remove: list[str] = []

        with self._lock:
            for job_id, job in self._jobs.items():
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                    try:
                        ts = datetime.fromisoformat(
                            job.completed_at or job.created_at
                        ).timestamp()
                        if ts < cutoff:
                            to_remove.append(job_id)
                    except (ValueError, TypeError):
                        pass

            for job_id in to_remove:
                del self._jobs[job_id]

        if to_remove:
            logger.info(f"Cleared {len(to_remove)} completed job(s)")
        return len(to_remove)

    @property
    def stats(self) -> dict:
        """Return queue statistics."""
        with self._lock:
            jobs = list(self._jobs.values())
        counts = {s.value: 0 for s in JobStatus}
        for job in jobs:
            counts[job.status.value] += 1
        return {"total": len(jobs), **counts}

    # ── Private ────────────────────────────────────────────────────────────────

    def _run(self, job: Job, fn: Callable) -> None:
        """Execute a job in the current thread (called from daemon thread)."""
        self._semaphore.acquire()
        try:
            if job.status == JobStatus.CANCELLED:
                return

            with self._lock:
                job.status = JobStatus.RUNNING
                job.started_at = datetime.utcnow().isoformat()

            logger.info(f"Job started: {job.id} ({job.job_type})")
            result = fn(job)

            with self._lock:
                if job.status != JobStatus.CANCELLED:
                    job.status = JobStatus.COMPLETED
                    job.progress = 1.0
                    job.result = result
                    job.completed_at = datetime.utcnow().isoformat()
                    logger.info(f"Job completed: {job.id}")

        except Exception as exc:
            with self._lock:
                job.status = JobStatus.FAILED
                job.error = str(exc)
                job.completed_at = datetime.utcnow().isoformat()
            logger.error(f"Job failed: {job.id} — {exc}")
        finally:
            self._semaphore.release()


# ── Singleton ─────────────────────────────────────────────────────────────────

_queue: Optional[JobQueue] = None


def get_job_queue() -> JobQueue:
    """Return the global job queue singleton."""
    global _queue
    if _queue is None:
        _queue = JobQueue(max_workers=4)
    return _queue
