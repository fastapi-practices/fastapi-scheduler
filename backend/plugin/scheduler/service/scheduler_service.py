from collections.abc import Sequence
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID

import sqlalchemy as sa

from apscheduler import (
    AsyncScheduler,
    CoalescePolicy,
    ConflictPolicy,
    ConflictingIdError,
    Job,
    Schedule,
    ScheduleLookupError,
    TaskLookupError,
)
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.core.conf import settings
from backend.plugin.scheduler.schema.scheduler import (
    CreateSchedulerJobParam,
    GetSchedulerJobDetail,
    GetSchedulerRunDetail,
    GetSchedulerStatusDetail,
    RunSchedulerJobDetail,
)
from backend.plugin.scheduler.utils.scheduler import get_scheduler as _get_scheduler
from backend.plugin.scheduler.utils.scheduler import scheduler_manager
from backend.utils.timezone import timezone

_RUN_RECORD_FIELDS = (
    'job_id',
    'schedule_id',
    'task_id',
    'scheduler_id',
    'scheduled_start',
    'started_at',
    'finished_at',
    'duration_seconds',
    'outcome',
    'exception_type',
    'exception_message',
    'exception_traceback',
)


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

    async def create(self, *, obj: CreateSchedulerJobParam) -> GetSchedulerJobDetail:
        """
        创建调度任务

        :param obj: 创建调度任务参数
        :return:
        """
        _ensure_scheduler_operable()
        trigger = _build_trigger(trigger_type=obj.trigger_type, trigger_config=obj.trigger_config)
        add_schedule_kwargs: dict[str, Any] = {
            'id': obj.id,
            'args': obj.args,
            'kwargs': obj.kwargs,
            'paused': obj.paused,
            'coalesce': CoalescePolicy[obj.coalesce],
            'max_jitter': obj.max_jitter,
            'job_result_expiration_time': obj.job_result_expiration_time,
            'conflict_policy': ConflictPolicy[obj.conflict_policy],
        }
        if obj.job_executor is not None:
            add_schedule_kwargs['job_executor'] = obj.job_executor
        if obj.misfire_grace_time is not None:
            add_schedule_kwargs['misfire_grace_time'] = obj.misfire_grace_time
        if obj.metadata:
            add_schedule_kwargs['metadata'] = obj.metadata
        try:
            schedule_id = await scheduler_manager.scheduler.add_schedule(obj.task_id, trigger, **add_schedule_kwargs)
        except ConflictingIdError as exc:
            raise errors.ConflictError(msg='调度任务已存在') from exc
        except TaskLookupError as exc:
            raise errors.NotFoundError(msg='APScheduler 任务不存在') from exc
        except (TypeError, ValueError) as exc:
            raise errors.RequestError(msg=f'调度任务参数错误: {exc}') from exc
        return await self.get(schedule_id=schedule_id)

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
    async def delete_jobs(*, schedule_ids: list[str]) -> int:
        """
        批量删除调度任务

        :param schedule_ids: 任务 ID 列表
        :return:
        """
        _ensure_scheduler_operable()
        schedule_ids = list(dict.fromkeys(schedule_ids))
        for schedule_id in schedule_ids:
            await _get_schedule(schedule_id=schedule_id)
        for schedule_id in schedule_ids:
            await scheduler_manager.scheduler.remove_schedule(schedule_id)
        return len(schedule_ids)

    @staticmethod
    async def get_list(*, db: AsyncSession, schedule_id: str | None = None) -> dict[str, Any]:
        """
        获取调度任务运行记录

        :param db: 数据库会话
        :param schedule_id: 任务 ID
        :return:
        """
        records = scheduler_manager.get_run_records(schedule_id=schedule_id)
        run_record_select = _get_run_records_select(records)
        return await paging_data(db, run_record_select, transformer=_serialize_run_record_rows)

    @staticmethod
    def delete_runs(*, job_ids: list[str]) -> int:
        """
        批量删除调度任务运行记录

        :param job_ids: 运行任务 ID 列表
        :return:
        """
        return scheduler_manager.delete_run_records(job_ids=job_ids)


scheduler_service: SchedulerService = SchedulerService()


def _build_trigger(*, trigger_type: str, trigger_config: dict[str, Any]) -> DateTrigger | IntervalTrigger | CronTrigger:
    """构建调度触发器"""
    try:
        if trigger_type == 'date':
            return DateTrigger(**trigger_config)
        if trigger_type == 'interval':
            return IntervalTrigger(**trigger_config)
        if trigger_type == 'cron':
            return CronTrigger(**trigger_config)
    except (TypeError, ValueError) as exc:
        raise errors.RequestError(msg=f'触发器参数错误: {exc}') from exc
    raise errors.RequestError(msg='触发器类型不支持')


def _get_run_records_select(records: list[GetSchedulerRunDetail]) -> sa.Select:
    """获取调度运行记录分页查询表达式"""
    if not records:
        columns = [sa.literal(None).label(field) for field in _RUN_RECORD_FIELDS]
        return sa.select(*columns).where(sa.false())
    selects = []
    for index, record in enumerate(records):
        record_data = record.model_dump(mode='json')
        columns = [sa.literal(index).label('_sort_order')]
        for field in _RUN_RECORD_FIELDS:
            value = record_data[field]
            if field == 'exception_traceback':
                column = sa.literal(value, type_=sa.JSON).label(field)
            else:
                column = sa.literal(value).label(field)
            columns.append(column)
        selects.append(sa.select(*columns))
    run_records = sa.union_all(*selects).subquery()
    columns = [getattr(run_records.c, field) for field in _RUN_RECORD_FIELDS]
    return sa.select(*columns).order_by(run_records.c._sort_order)


def _serialize_run_record_rows(items: Sequence[Any]) -> list[dict[str, Any]]:
    """序列化调度运行记录分页行"""
    return [dict(item._mapping) for item in items]


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
