from datetime import datetime
from typing import TYPE_CHECKING, Any

from apscheduler import AsyncScheduler, Event, JobAcquired, JobAdded, JobReleased

from backend.core.conf import settings
from backend.plugin.scheduler.schema.scheduler import GetSchedulerRunDetail

if TYPE_CHECKING:
    from apscheduler.abc import Subscription


class SchedulerManager:
    """APScheduler 调度器管理器"""

    def __init__(self) -> None:
        self._scheduler: AsyncScheduler | None = None
        self._started = False
        self._subscription: Subscription | None = None
        self._running_jobs: dict[str, dict[str, Any]] = {}
        self._run_records: list[GetSchedulerRunDetail] = []

    @property
    def scheduler(self) -> AsyncScheduler:
        """获取调度器实例"""
        if self._scheduler is None:
            self._scheduler = AsyncScheduler(identity=settings.SCHEDULER_IDENTITY)
        return self._scheduler

    @property
    def started(self) -> bool:
        """获取调度器启动状态"""
        return self._started

    def mark_started(self) -> None:
        """标记调度器已启动"""
        self._started = True

    def mark_stopped(self) -> None:
        """标记调度器已停止"""
        self._started = False
        self._running_jobs.clear()

    def register_event_listener(self) -> None:
        """注册调度事件监听"""
        if self._subscription is not None:
            return
        self._subscription = self.scheduler.subscribe(
            self.record_event,
            (JobAdded, JobAcquired, JobReleased),
            is_async=False,
        )

    def unregister_event_listener(self) -> None:
        """注销调度事件监听"""
        if self._subscription is None:
            return
        self._subscription.unsubscribe()
        self._subscription = None

    def record_event(self, event: Event) -> None:
        """记录调度运行事件"""
        if isinstance(event, JobAdded):
            self._running_jobs[str(event.job_id)] = {
                'job_id': str(event.job_id),
                'task_id': event.task_id,
                'schedule_id': event.schedule_id,
            }
        elif isinstance(event, JobAcquired):
            job_id = str(event.job_id)
            self._running_jobs.setdefault(job_id, {'job_id': job_id})
            self._running_jobs[job_id].update({
                'scheduler_id': event.scheduler_id,
                'task_id': event.task_id,
                'schedule_id': event.schedule_id,
                'scheduled_start': event.scheduled_start,
                'started_at': event.timestamp,
            })
        elif isinstance(event, JobReleased):
            self._append_run_record(event)

    def get_run_records(self, *, schedule_id: str | None = None) -> list[GetSchedulerRunDetail]:
        """获取内存运行记录"""
        records = self._run_records
        if schedule_id:
            records = [record for record in records if record.schedule_id == schedule_id]
        return records

    def delete_run_records(self, *, job_ids: list[str]) -> int:
        """
        批量删除内存运行记录

        :param job_ids: 运行任务 ID 列表
        :return:
        """
        job_id_set = set(job_ids)
        before_count = len(self._run_records)
        self._run_records = [record for record in self._run_records if record.job_id not in job_id_set]
        return before_count - len(self._run_records)

    def bind_manual_run(self, *, job_id: str, schedule_id: str) -> None:
        """绑定手动运行记录与调度任务"""
        self._running_jobs.setdefault(job_id, {'job_id': job_id})
        self._running_jobs[job_id]['schedule_id'] = schedule_id
        for record in self._run_records:
            if record.job_id == job_id and record.schedule_id is None:
                record.schedule_id = schedule_id

    def _append_run_record(self, event: JobReleased) -> None:
        job_id = str(event.job_id)
        running = self._running_jobs.pop(job_id, {})
        started_at = event.started_at or running.get('started_at')
        finished_at = event.timestamp
        duration_seconds = _get_duration_seconds(started_at, finished_at)
        self._run_records.insert(
            0,
            GetSchedulerRunDetail(
                job_id=job_id,
                schedule_id=event.schedule_id or running.get('schedule_id'),
                task_id=event.task_id or running.get('task_id', ''),
                scheduler_id=event.scheduler_id or running.get('scheduler_id'),
                scheduled_start=event.scheduled_start or running.get('scheduled_start'),
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration_seconds,
                outcome=event.outcome.name,
                exception_type=event.exception_type,
                exception_message=event.exception_message,
                exception_traceback=event.exception_traceback,
            ),
        )
        del self._run_records[200:]


scheduler_manager = SchedulerManager()


def get_scheduler() -> AsyncScheduler:
    """获取 APScheduler 调度器实例"""
    return scheduler_manager.scheduler


def _get_duration_seconds(started_at: datetime | None, finished_at: datetime | None) -> float | None:
    if not started_at or not finished_at:
        return None
    return round((finished_at - started_at).total_seconds(), 3)
