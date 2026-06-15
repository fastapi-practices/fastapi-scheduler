from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID

from apscheduler import AsyncScheduler, Job, Schedule, ScheduleLookupError
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from backend.common.exception import errors
from backend.core.conf import settings
from backend.plugin.scheduler.schema.scheduler import (
    GetSchedulerJobDetail,
    GetSchedulerRunDetail,
    GetSchedulerStatusDetail,
    RunSchedulerJobDetail,
)
from backend.plugin.scheduler.utils.scheduler import get_scheduler as _get_scheduler
from backend.plugin.scheduler.utils.scheduler import scheduler_manager
from backend.utils.timezone import timezone


def get_scheduler() -> AsyncScheduler:
    """获取 APScheduler 调度器实例"""
    return _get_scheduler()


class SchedulerService:
    """调度器服务类"""

    @staticmethod
    async def get_status() -> GetSchedulerStatusDetail:
        """获取调度器状态"""
        schedule_count = 0
        running_job_count = 0
        if settings.SCHEDULER_ENABLED and scheduler_manager.started:
            schedules = await scheduler_manager.scheduler.get_schedules()
            jobs = await scheduler_manager.scheduler.get_jobs()
            schedule_count = len(schedules)
            running_job_count = _count_running_jobs(jobs)
        return GetSchedulerStatusDetail(
            enabled=settings.SCHEDULER_ENABLED,
            started=scheduler_manager.started,
            identity=settings.SCHEDULER_IDENTITY,
            timezone=settings.DATETIME_TIMEZONE,
            schedule_count=schedule_count,
            running_job_count=running_job_count,
        )

    @staticmethod
    async def get_all() -> list[GetSchedulerJobDetail]:
        """获取所有调度任务"""
        if not settings.SCHEDULER_ENABLED or not scheduler_manager.started:
            return []
        schedules = await scheduler_manager.scheduler.get_schedules()
        jobs = await scheduler_manager.scheduler.get_jobs()
        running_counts = _get_running_job_counts(jobs)
        return [_to_job_detail(schedule, running_counts) for schedule in schedules]

    @staticmethod
    async def get(*, schedule_id: str) -> GetSchedulerJobDetail:
        """
        获取调度任务详情

        :param schedule_id: 任务 ID
        :return:
        """
        _ensure_scheduler_operable()
        schedule = await _get_schedule(schedule_id=schedule_id)
        jobs = await scheduler_manager.scheduler.get_jobs()
        running_counts = _get_running_job_counts(jobs)
        return _to_job_detail(schedule, running_counts)

    async def pause(self, *, schedule_id: str) -> GetSchedulerJobDetail:
        """
        暂停调度任务

        :param schedule_id: 任务 ID
        :return:
        """
        _ensure_scheduler_operable()
        await _get_schedule(schedule_id=schedule_id)
        await scheduler_manager.scheduler.pause_schedule(schedule_id)
        return await self.get(schedule_id=schedule_id)

    async def resume(self, *, schedule_id: str) -> GetSchedulerJobDetail:
        """
        恢复调度任务

        :param schedule_id: 任务 ID
        :return:
        """
        _ensure_scheduler_operable()
        await _get_schedule(schedule_id=schedule_id)
        await scheduler_manager.scheduler.unpause_schedule(schedule_id, resume_from='now')
        return await self.get(schedule_id=schedule_id)

    @staticmethod
    async def run(*, schedule_id: str) -> RunSchedulerJobDetail:
        """
        立即运行调度任务

        :param schedule_id: 任务 ID
        :return:
        """
        _ensure_scheduler_operable()
        schedule = await _get_schedule(schedule_id=schedule_id)
        job_id = await scheduler_manager.scheduler.add_job(
            schedule.task_id,
            args=schedule.args,
            kwargs=schedule.kwargs,
            result_expiration_time=3600,
        )
        scheduler_manager.bind_manual_run(job_id=str(job_id), schedule_id=schedule_id)
        return RunSchedulerJobDetail(schedule_id=schedule_id, job_id=str(job_id))

    @staticmethod
    async def delete(*, schedule_id: str) -> None:
        """
        删除调度任务

        :param schedule_id: 任务 ID
        :return:
        """
        _ensure_scheduler_operable()
        await _get_schedule(schedule_id=schedule_id)
        await scheduler_manager.scheduler.remove_schedule(schedule_id)

    @staticmethod
    def get_runs(*, schedule_id: str | None = None, limit: int = 100) -> list[GetSchedulerRunDetail]:
        """
        获取调度任务运行记录

        :param schedule_id: 任务 ID
        :param limit: 返回数量
        :return:
        """
        return scheduler_manager.get_run_records(schedule_id=schedule_id, limit=limit)


scheduler_service: SchedulerService = SchedulerService()


async def _get_schedule(*, schedule_id: str) -> Schedule:
    try:
        return await scheduler_manager.scheduler.get_schedule(schedule_id)
    except ScheduleLookupError as exc:
        raise errors.NotFoundError(msg='调度任务不存在') from exc


def _ensure_scheduler_operable() -> None:
    if not settings.SCHEDULER_ENABLED:
        raise errors.RequestError(msg='调度器已禁用')
    if not scheduler_manager.started:
        raise errors.RequestError(msg='调度器尚未启动')


def _to_job_detail(schedule: Schedule, running_counts: dict[str, int]) -> GetSchedulerJobDetail:
    running_job_count = running_counts.get(schedule.id, 0)
    return GetSchedulerJobDetail(
        id=schedule.id,
        task_id=schedule.task_id,
        trigger=str(schedule.trigger),
        trigger_type=type(schedule.trigger).__name__,
        trigger_config=_get_trigger_config(schedule.trigger),
        args=_safe_value(list(schedule.args)),
        kwargs=_safe_value(schedule.kwargs),
        paused=schedule.paused,
        status=_get_schedule_status(schedule, running_job_count),
        coalesce=schedule.coalesce.name,
        misfire_grace_time=_get_seconds(schedule.misfire_grace_time),
        max_jitter=_get_seconds(schedule.max_jitter),
        job_executor=schedule.job_executor,
        job_result_expiration_time=_get_seconds(schedule.job_result_expiration_time) or 0,
        metadata=_safe_value(schedule.metadata),
        next_fire_time=schedule.next_fire_time,
        last_fire_time=schedule.last_fire_time,
        acquired_by=schedule.acquired_by,
        acquired_until=schedule.acquired_until,
        running_job_count=running_job_count,
    )


def _get_schedule_status(schedule: Schedule, running_job_count: int) -> str:
    if schedule.paused:
        return 'paused'
    if running_job_count > 0:
        return 'running'
    if schedule.next_fire_time is None:
        return 'completed'
    return 'scheduled'


def _get_running_job_counts(jobs: list[Job] | tuple[Job, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for job in jobs:
        if job.schedule_id and job.acquired_by:
            counts[job.schedule_id] = counts.get(job.schedule_id, 0) + 1
    return counts


def _count_running_jobs(jobs: list[Job] | tuple[Job, ...]) -> int:
    return sum(1 for job in jobs if job.acquired_by)


def _get_trigger_config(trigger: Any) -> dict[str, Any]:
    if isinstance(trigger, IntervalTrigger):
        return _safe_value({
            'weeks': trigger.weeks,
            'days': trigger.days,
            'hours': trigger.hours,
            'minutes': trigger.minutes,
            'seconds': trigger.seconds,
            'start_time': trigger.start_time,
            'end_time': trigger.end_time,
        })
    if isinstance(trigger, CronTrigger):
        return _safe_value({
            'year': trigger.year,
            'month': trigger.month,
            'day': trigger.day,
            'week': trigger.week,
            'day_of_week': trigger.day_of_week,
            'hour': trigger.hour,
            'minute': trigger.minute,
            'second': trigger.second,
            'start_time': trigger.start_time,
            'end_time': trigger.end_time,
            'timezone': trigger.timezone,
        })
    if isinstance(trigger, DateTrigger):
        return _safe_value({'run_time': trigger.run_time})
    return {'repr': str(trigger)}


def _get_seconds(value: timedelta | None) -> float | None:
    if value is None:
        return None
    return value.total_seconds()


def _safe_value(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, datetime):
        return timezone.to_str(timezone.from_datetime(value))
    if isinstance(value, timedelta):
        return value.total_seconds()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, dict):
        return {str(key): _safe_value(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [_safe_value(item) for item in value]
    return str(value)
