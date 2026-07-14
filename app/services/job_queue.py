from __future__ import annotations

import json
import os
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from queue import PriorityQueue, Empty
from threading import Lock, Event
from typing import Any, Callable
from uuid import uuid4

from app.services.runtime_paths import get_job_dir


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RECOVERY_REQUIRED = "recovery_required"
    DEAD_LETTER = "dead_letter"


class JobPriority(int, Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Job:
    job_id: str
    kind: str
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str = ""
    finished_at: str = ""
    owner_pid: int = field(default_factory=os.getpid)
    worker_pid: int | None = None
    worker_thread_id: int | None = None
    events: list[dict] = field(default_factory=list)
    result: Any = None
    error: str = ""
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: float = 300.0
    cancelled: bool = False
    execution_token: str = field(default_factory=lambda: uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "kind": self.kind,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "owner_pid": self.owner_pid,
            "worker_pid": self.worker_pid,
            "worker_thread_id": self.worker_thread_id,
            "events": list(self.events),
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "cancelled": self.cancelled,
            "execution_token": self.execution_token,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Job:
        return cls(
            job_id=data["job_id"],
            kind=data["kind"],
            status=JobStatus(data.get("status", "pending")),
            priority=JobPriority(data.get("priority", 3)),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            started_at=data.get("started_at", ""),
            finished_at=data.get("finished_at", ""),
            owner_pid=data.get("owner_pid", os.getpid()),
            worker_pid=data.get("worker_pid"),
            worker_thread_id=data.get("worker_thread_id"),
            events=list(data.get("events", [])),
            result=data.get("result"),
            error=data.get("error", ""),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            timeout_seconds=data.get("timeout_seconds", 300.0),
            cancelled=data.get("cancelled", False),
            execution_token=data.get("execution_token", uuid4().hex),
        )


JobCallable = Callable[[Callable[[str, str, str], None]], dict[str, Any]]


class JobQueue:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._jobs: dict[str, Job] = {}
        self._queue = PriorityQueue()
        self._lock = Lock()
        self._store_dir = get_job_dir()
        self._store_dir.mkdir(parents=True, exist_ok=True)

        # Runner 注册表（内存中，无法持久化）
        self._runners: dict[str, JobCallable] = {}
        self._runners_lock = Lock()

        # 配置
        self._max_workers = int(os.environ.get("JOB_MAX_WORKERS", "3"))
        self._default_timeout = float(os.environ.get("JOB_DEFAULT_TIMEOUT", "300"))
        self._max_retries = int(os.environ.get("JOB_MAX_RETRIES", "3"))
        self._retry_delay_base = float(os.environ.get("JOB_RETRY_DELAY_BASE", "2.0"))
        self._retry_delay_max = float(os.environ.get("JOB_RETRY_DELAY_MAX", "60.0"))
        self._dead_letter_enabled = os.environ.get("JOB_DEAD_LETTER_ENABLED", "false").lower() == "true"
        self._heartbeat_interval = float(os.environ.get("JOB_HEARTBEAT_INTERVAL", "10"))
        self._max_events = int(os.environ.get("JOB_MAX_EVENTS", "200"))
        self._stale_timeout_seconds = float(os.environ.get("JOB_STALE_TIMEOUT", "600"))

        # 执行器
        self._executor = ThreadPoolExecutor(
            max_workers=self._max_workers,
            thread_name_prefix="job_worker_"
        )
        self._running_futures: dict[str, Any] = {}
        self._shutdown_event = Event()

        # 统计
        self._stats = {
            "total_created": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_cancelled": 0,
            "total_retried": 0,
            "total_dead_letter": 0,
            "total_timeout": 0,
        }
        self._stats_lock = Lock()

        # 恢复之前的任务
        self._recover_jobs()

        # 启动监控线程
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True, name="job_monitor")
        self._monitor_thread.start()

        # 启动调度线程
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True, name="job_scheduler")
        self._scheduler_thread.start()

    def create_job(
        self,
        kind: str,
        runner: JobCallable,
        priority: JobPriority = JobPriority.NORMAL,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> dict[str, Any]:
        job_id = uuid4().hex[:12]
        job = Job(
            job_id=job_id,
            kind=kind,
            status=JobStatus.QUEUED,
            priority=priority,
            max_retries=max_retries if max_retries is not None else self._max_retries,
            timeout_seconds=timeout if timeout is not None else self._default_timeout,
        )
        job.events.append({
            "time": _now(),
            "level": "info",
            "agent": "job-queue",
            "message": f"任务已创建，优先级：{priority.name}，超时：{job.timeout_seconds}秒，最大重试：{job.max_retries}次。",
        })

        with self._lock:
            self._jobs[job_id] = job
            self._persist_job(job)

        # 注册 runner
        with self._runners_lock:
            self._runners[job_id] = runner

        # 放入优先级队列 (priority_value, timestamp, job_id)
        # 数字越小优先级越高，所以用 priority.value 直接入队
        self._queue.put((priority.value, time.time(), job_id))

        with self._stats_lock:
            self._stats["total_created"] += 1

        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                job = self._load_job(job_id)
                if job:
                    self._jobs[job_id] = job
            return self._clone_job(job) if job else None

    def cancel_job(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                job = self._load_job(job_id)
                if job:
                    self._jobs[job_id] = job

            if not job:
                return None

            if job.status in (
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
                JobStatus.RECOVERY_REQUIRED,
                JobStatus.DEAD_LETTER,
            ):
                return self._clone_job(job)

            job.cancelled = True
            job.execution_token = uuid4().hex

            if job.status == JobStatus.RUNNING:
                job.events.append({
                    "time": _now(),
                    "level": "warning",
                    "agent": "job-queue",
                    "message": "任务取消信号已发送，等待当前执行停止。",
                })
            else:
                job.status = JobStatus.CANCELLED
                job.finished_at = _now()
                job.events.append({
                    "time": _now(),
                    "level": "info",
                    "agent": "job-queue",
                    "message": "任务已在队列中取消，不会执行。",
                })
                with self._stats_lock:
                    self._stats["total_cancelled"] += 1

            job.updated_at = _now()
            self._persist_job(job)

            # 从 runner 注册表移除
            with self._runners_lock:
                self._runners.pop(job_id, None)

            return self._clone_job(job)

    def list_jobs(self, status: JobStatus | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            jobs = list(self._jobs.values())

        # 也加载磁盘上的任务
        for f in self._store_dir.glob("*.json"):
            job_id = f.stem
            if job_id not in self._jobs:
                job = self._load_job(job_id)
                if job:
                    with self._lock:
                        self._jobs[job_id] = job
                    jobs.append(job)

        if status:
            jobs = [j for j in jobs if j.status == status]

        # 按更新时间倒序
        jobs.sort(key=lambda j: j.updated_at, reverse=True)
        return [self._clone_job(j) for j in jobs[:limit]]

    def get_stats(self) -> dict[str, Any]:
        with self._stats_lock:
            stats = dict(self._stats)

        with self._lock:
            running = sum(1 for j in self._jobs.values() if j.status == JobStatus.RUNNING)
            queued = sum(1 for j in self._jobs.values() if j.status == JobStatus.QUEUED)
            pending = sum(1 for j in self._jobs.values() if j.status == JobStatus.PENDING)

        return {
            **stats,
            "currently_running": running,
            "currently_queued": queued,
            "currently_pending": pending,
            "max_workers": self._max_workers,
            "queue_size": self._queue.qsize(),
        }

    def append_event(self, job_id: str, message: str, *, agent: str = "system", level: str = "info") -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.events.append({
                "time": _now(),
                "level": level,
                "agent": agent,
                "message": message,
            })
            # 限制事件数量
            if len(job.events) > self._max_events:
                job.events = job.events[-self._max_events:]
            job.updated_at = _now()
            self._persist_job(job)

    def shutdown(self, wait: bool = True, timeout: float = 30.0) -> None:
        self._shutdown_event.set()

        # 取消所有运行中的任务
        with self._lock:
            for job in self._jobs.values():
                if job.status == JobStatus.RUNNING:
                    job.cancelled = True

        self._executor.shutdown(wait=wait)

    def _scheduler_loop(self) -> None:
        while not self._shutdown_event.is_set():
            try:
                # 等待有任务，超时检查shutdown
                priority, timestamp, job_id = self._queue.get(timeout=1.0)
            except Empty:
                continue
            except Exception:
                continue

            with self._lock:
                job = self._jobs.get(job_id)
                if not job or job.cancelled or job.status not in (JobStatus.QUEUED, JobStatus.PENDING):
                    continue
                job.cancelled = False
                job.execution_token = uuid4().hex
                job.status = JobStatus.RUNNING
                job.started_at = _now()
                job.updated_at = _now()
                self._persist_job(job)

            # 提交到线程池执行
            future = self._executor.submit(self._execute_job_wrapper, job_id)
            with self._lock:
                self._running_futures[job_id] = future

    def _execute_job_wrapper(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.worker_pid = os.getpid()
            job.worker_thread_id = threading.current_thread().ident
            job.updated_at = _now()
            self._persist_job(job)

        # 获取 runner
        with self._runners_lock:
            runner = self._runners.get(job_id)

        if not runner:
            # 如果是恢复的任务，可能没有 runner
            with self._lock:
                job.status = JobStatus.FAILED
                job.finished_at = _now()
                job.error = "无法恢复任务执行器，请重新提交任务。"
                job.events.append({
                    "time": _now(),
                    "level": "error",
                    "agent": "job-queue",
                    "message": job.error,
                })
                job.updated_at = _now()
                self._persist_job(job)
            with self._stats_lock:
                self._stats["total_failed"] += 1
            with self._lock:
                self._running_futures.pop(job_id, None)
            return

        # 执行实际任务（带超时）
        self._run_job_with_timeout(job_id, runner)

    def _run_job_with_timeout(self, job_id: str, runner: JobCallable) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            execution_token = job.execution_token

        timeout = job.timeout_seconds
        result_container = [None]
        exception_container = [None]
        done_event = threading.Event()
        terminal_statuses = {
            JobStatus.TIMEOUT,
            JobStatus.CANCELLED,
            JobStatus.FAILED,
            JobStatus.RECOVERY_REQUIRED,
            JobStatus.DEAD_LETTER,
        }

        def target():
            try:
                def emit(message: str, agent: str = "system", level: str = "info") -> None:
                    with self._lock:
                        j = self._jobs.get(job_id)
                        if not j:
                            raise JobCancelledError("任务已不存在")
                        if j.execution_token != execution_token:
                            raise JobCancelledError("任务执行代次已失效")
                        if j.cancelled or j.status in terminal_statuses:
                            raise JobCancelledError("任务已被取消")
                    self.append_event(job_id, message, agent=agent, level=level)

                emit("后台执行已开始。", agent="execution-orchestrator")
                result_container[0] = runner(emit)
            except JobCancelledError:
                exception_container[0] = JobCancelledError("任务在执行中被取消")
            except Exception as exc:
                exception_container[0] = exc
            finally:
                done_event.set()

        # 启动工作线程
        worker_thread = threading.Thread(target=target, daemon=True, name=f"job_worker_inner_{job_id}")
        worker_thread.start()

        # 等待完成或超时
        completed = done_event.wait(timeout=timeout)

        if not completed:
            # 超时处理
            with self._lock:
                latest_job = self._jobs.get(job_id)
                if not latest_job or latest_job.execution_token != execution_token:
                    self._running_futures.pop(job_id, None)
                    return
                latest_job.status = JobStatus.TIMEOUT
                latest_job.finished_at = _now()
                latest_job.error = f"任务执行超过 {timeout} 秒超时。"
                latest_job.cancelled = True
                latest_job.execution_token = uuid4().hex
                latest_job.events.append({
                    "time": _now(),
                    "level": "error",
                    "agent": "job-queue",
                    "message": latest_job.error,
                })
                latest_job.updated_at = _now()
                self._persist_job(latest_job)

            with self._stats_lock:
                self._stats["total_timeout"] += 1

            self.append_event(job_id, f"任务超时（{timeout}秒）。", agent="job-queue", level="error")

            with self._lock:
                self._running_futures.pop(job_id, None)

            partial_result = result_container[0]
            if isinstance(partial_result, dict) and partial_result.get("page_url") and partial_result.get("file_path"):
                with self._lock:
                    latest_job = self._jobs.get(job_id)
                    if latest_job:
                        latest_job.status = JobStatus.COMPLETED
                        latest_job.result = partial_result
                        latest_job.error = ""
                        latest_job.updated_at = _now()
                        latest_job.events.append({
                            "time": _now(),
                            "level": "warning",
                            "agent": "job-queue",
                            "message": "后台收尾超时，但首版页面已经生成，先按可交付结果返回。",
                        })
                        self._persist_job(latest_job)
                with self._stats_lock:
                    self._stats["total_completed"] += 1
                with self._runners_lock:
                    self._runners.pop(job_id, None)
                return

            # 尝试重试
            will_retry = self._maybe_retry(job_id, runner, f"任务执行超过 {timeout} 秒超时。")
            if not will_retry:
                with self._runners_lock:
                    self._runners.pop(job_id, None)
            return

        with self._lock:
            latest_job = self._jobs.get(job_id)
            if (
                not latest_job
                or latest_job.execution_token != execution_token
                or latest_job.status in terminal_statuses
            ):
                self._running_futures.pop(job_id, None)
                return

        # 检查是否有异常
        if exception_container[0] is not None:
            exc = exception_container[0]

            if isinstance(exc, JobCancelledError):
                with self._lock:
                    latest_job = self._jobs.get(job_id)
                    if latest_job and latest_job.execution_token == execution_token:
                        latest_job.status = JobStatus.CANCELLED
                        latest_job.finished_at = _now()
                        latest_job.error = "任务已被取消。"
                        latest_job.events.append({
                            "time": _now(),
                            "level": "info",
                            "agent": "job-queue",
                            "message": "任务在执行过程中被取消。",
                        })
                        latest_job.updated_at = _now()
                        self._persist_job(latest_job)
                with self._stats_lock:
                    self._stats["total_cancelled"] += 1
                with self._lock:
                    self._running_futures.pop(job_id, None)
                with self._runners_lock:
                    self._runners.pop(job_id, None)
                return

            # 普通异常
            error_msg = "".join(traceback.format_exception_only(type(exc), exc)).strip()

            with self._lock:
                latest_job = self._jobs.get(job_id)
                if (
                    not latest_job
                    or latest_job.execution_token != execution_token
                    or latest_job.status in terminal_statuses
                ):
                    self._running_futures.pop(job_id, None)
                    with self._runners_lock:
                        self._runners.pop(job_id, None)
                    return
                latest_job.status = JobStatus.FAILED
                latest_job.finished_at = _now()
                latest_job.error = error_msg
                latest_job.updated_at = _now()
                self._persist_job(latest_job)

            self.append_event(job_id, f"任务失败：{exc}", agent="job-queue", level="error")

            with self._stats_lock:
                self._stats["total_failed"] += 1

            # 尝试重试
            will_retry = self._maybe_retry(job_id, runner, error_msg)

            with self._lock:
                self._running_futures.pop(job_id, None)

            if not will_retry:
                with self._runners_lock:
                    self._runners.pop(job_id, None)
            return

        # 成功完成
        with self._lock:
            latest_job = self._jobs.get(job_id)
            if (
                not latest_job
                or latest_job.execution_token != execution_token
                or latest_job.status in terminal_statuses
            ):
                self._running_futures.pop(job_id, None)
                with self._runners_lock:
                    self._runners.pop(job_id, None)
                return
            latest_job.status = JobStatus.COMPLETED
            latest_job.finished_at = _now()
            latest_job.result = result_container[0]
            latest_job.error = ""
            latest_job.updated_at = _now()
            self._persist_job(latest_job)

        self.append_event(job_id, "任务已完成，结果可以打开。", agent="job-queue")

        with self._stats_lock:
            self._stats["total_completed"] += 1

        with self._lock:
            self._running_futures.pop(job_id, None)
        with self._runners_lock:
            self._runners.pop(job_id, None)

    def _maybe_retry(self, job_id: str, runner: JobCallable, error_msg: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            if job.status == JobStatus.CANCELLED:
                return False

            if job.retry_count >= job.max_retries:
                job.status = JobStatus.FAILED
                job.finished_at = _now()
                job.error = error_msg[:1000]
                final_message = (
                    f"任务已用尽 {job.max_retries} 次重试，停止自动重试。"
                    f" 最后错误：{error_msg[:200]}"
                )
                job.events.append({
                    "time": _now(),
                    "level": "error",
                    "agent": "job-queue",
                    "message": final_message,
                })
                job.updated_at = _now()
                self._persist_job(job)

                if self._dead_letter_enabled:
                    with self._stats_lock:
                        self._stats["total_dead_letter"] += 1
                return False

            job.retry_count += 1
            job.status = JobStatus.QUEUED
            job.cancelled = False
            job.execution_token = uuid4().hex
            job.error = f"[第 {job.retry_count} 次重试] {error_msg[:200]}"
            job.started_at = ""
            job.worker_pid = None
            job.worker_thread_id = None
            job.events.append({
                "time": _now(),
                "level": "warning",
                "agent": "job-queue",
                "message": f"第 {job.retry_count}/{job.max_retries} 次重试，将在延迟后重新排队。",
            })
            job.updated_at = _now()
            self._persist_job(job)

        # 重新注册 runner（用于重试）
        with self._runners_lock:
            self._runners[job_id] = runner

        # 指数退避延迟
        delay = min(
            self._retry_delay_base * (2 ** (job.retry_count - 1)),
            self._retry_delay_max
        )

        def delayed_requeue():
            time.sleep(delay)
            with self._lock:
                latest_job = self._jobs.get(job_id)
                if (
                    latest_job
                    and not latest_job.cancelled
                    and latest_job.status == JobStatus.QUEUED
                ):
                    self._queue.put((latest_job.priority.value, time.time(), job_id))

        threading.Thread(target=delayed_requeue, daemon=True).start()

        with self._stats_lock:
            self._stats["total_retried"] += 1

        return True

    def _monitor_loop(self) -> None:
        while not self._shutdown_event.is_set():
            time.sleep(self._heartbeat_interval)
            try:
                self._cleanup_stale_jobs()
                self._persist_stats()
            except Exception:
                pass

    def _cleanup_stale_jobs(self) -> None:
        now = time.time()
        with self._lock:
            for job in list(self._jobs.values()):
                if job.status == JobStatus.RUNNING:
                    # 检查 worker 进程是否还活着
                    if job.worker_pid and not _process_exists(job.worker_pid):
                        job.status = JobStatus.FAILED
                        job.finished_at = _now()
                        job.error = "工作进程异常退出，任务中断。"
                        job.events.append({
                            "time": _now(),
                            "level": "error",
                            "agent": "job-queue",
                            "message": job.error,
                        })
                        job.updated_at = _now()
                        self._persist_job(job)
                        with self._stats_lock:
                            self._stats["total_failed"] += 1
                    else:
                        # 检查是否超过 stale 超时（运行中但很久没更新）
                        try:
                            last_update = datetime.fromisoformat(job.updated_at.replace("Z", "+00:00"))
                            elapsed = now - last_update.timestamp()
                            if elapsed > self._stale_timeout_seconds:
                                job.status = JobStatus.TIMEOUT
                                job.finished_at = _now()
                                job.error = f"任务运行超过 {self._stale_timeout_seconds} 秒无响应，判定为僵死。"
                                job.events.append({
                                    "time": _now(),
                                    "level": "error",
                                    "agent": "job-queue",
                                    "message": job.error,
                                })
                                job.updated_at = _now()
                                self._persist_job(job)
                                with self._stats_lock:
                                    self._stats["total_timeout"] += 1
                        except Exception:
                            pass

    def _recover_jobs(self) -> None:
        recovered_queued = 0
        recovered_failed = 0
        for f in self._store_dir.glob("*.json"):
            if f.name.endswith("_stats.json"):
                continue
            job_id = f.stem
            job = self._load_job(job_id)
            if not job:
                continue

            # 恢复之前未完成的任务到队列
            if job.status in (JobStatus.QUEUED, JobStatus.PENDING):
                job.status = JobStatus.RECOVERY_REQUIRED
                job.cancelled = True
                job.execution_token = uuid4().hex
                job.events.append({
                    "time": _now(),
                    "level": "warning",
                    "agent": "job-queue",
                    "message": "服务重启，任务缺少可恢复的执行器；请重新提交任务。",
                })
                job.updated_at = _now()
                job.worker_pid = None
                job.worker_thread_id = None
                self._jobs[job_id] = job
                self._persist_job(job)
                # 注意：恢复的任务没有 runner，需要调用方重新提交
                recovered_queued += 1
            elif job.status == JobStatus.RUNNING:
                # 检查进程是否还在
                if not _process_exists(job.worker_pid):
                    job.status = JobStatus.FAILED
                    job.finished_at = _now()
                    job.error = "服务重启后，原执行进程已不存在。"
                    job.events.append({
                        "time": _now(),
                        "level": "error",
                        "agent": "job-queue",
                        "message": job.error,
                    })
                    job.updated_at = _now()
                    self._jobs[job_id] = job
                    self._persist_job(job)
                    recovered_failed += 1
                else:
                    # 进程还在，标记为可疑但保留状态
                    job.events.append({
                        "time": _now(),
                        "level": "warning",
                        "agent": "job-queue",
                        "message": "服务重启，但原执行进程似乎仍在运行。任务状态保留。",
                    })
                    job.updated_at = _now()
                    self._jobs[job_id] = job
                    self._persist_job(job)
            else:
                self._jobs[job_id] = job

        if recovered_queued > 0 or recovered_failed > 0:
            print(f"[JobQueue] 已加载 {recovered_queued} 个待执行任务、{recovered_failed} 个失败任务（重启恢复）")

        # 恢复统计
        stats_path = self._store_dir / "_stats.json"
        if stats_path.exists():
            try:
                data = json.loads(stats_path.read_text(encoding="utf-8"))
                with self._stats_lock:
                    for key in self._stats:
                        if key in data:
                            self._stats[key] = data[key]
            except Exception:
                pass

    def _persist_job(self, job: Job) -> None:
        path = self._store_dir / f"{job.job_id}.json"
        temp_path = path.with_suffix(".tmp")
        try:
            temp_path.write_text(json.dumps(job.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
            temp_path.replace(path)
        except Exception:
            pass

    def _persist_stats(self) -> None:
        path = self._store_dir / "_stats.json"
        temp_path = path.with_suffix(".tmp")
        try:
            with self._stats_lock:
                data = dict(self._stats)
            temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            temp_path.replace(path)
        except Exception:
            pass

    def _load_job(self, job_id: str) -> Job | None:
        path = self._store_dir / f"{job_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return Job.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _clone_job(self, job: Job) -> dict[str, Any]:
        return job.to_dict()


class JobCancelledError(Exception):
    pass


class JobTimeoutError(Exception):
    pass


def _process_exists(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError, TypeError):
        return False


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# 全局单例
_queue = JobQueue()


def create_job(
    kind: str,
    runner: JobCallable,
    priority: JobPriority = JobPriority.NORMAL,
    timeout: float | None = None,
    max_retries: int | None = None,
) -> dict[str, Any]:
    return _queue.create_job(kind, runner, priority=priority, timeout=timeout, max_retries=max_retries)


def get_job(job_id: str) -> dict[str, Any] | None:
    return _queue.get_job(job_id)


def cancel_job(job_id: str) -> dict[str, Any] | None:
    return _queue.cancel_job(job_id)


def list_jobs(status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    s = JobStatus(status) if status else None
    return _queue.list_jobs(status=s, limit=limit)


def get_stats() -> dict[str, Any]:
    return _queue.get_stats()


def append_event(job_id: str, message: str, *, agent: str = "system", level: str = "info") -> None:
    _queue.append_event(job_id, message, agent=agent, level=level)


def shutdown_queue(wait: bool = True, timeout: float = 30.0) -> None:
    _queue.shutdown(wait=wait, timeout=timeout)
