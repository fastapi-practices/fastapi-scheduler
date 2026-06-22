from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from backend.common.schema import SchemaBase


class SchedulerStatusSchemaBase(SchemaBase):
    """调度器状态基础模型"""

    enabled: bool = Field(description='是否启用')
    started: bool = Field(description='是否已启动')
    identity: str = Field(description='调度器标识')
    timezone: str = Field(description='调度器时区')
    schedule_count: int = Field(description='调度计划数量')
    running_job_count: int = Field(description='运行中任务数量')


class GetSchedulerStatusDetail(SchedulerStatusSchemaBase):
    """调度器状态详情"""


class SchedulerJobSchemaBase(SchemaBase):
    """调度任务基础模型"""

    id: str = Field(description='任务 ID')
    task_id: str = Field(description='APScheduler 任务 ID', min_length=1)
    trigger: str = Field(description='触发器描述')
    trigger_type: str = Field(description='触发器类型')
    trigger_config: dict[str, Any] = Field(description='触发器配置')
    args: list[Any] = Field(description='位置参数')
    kwargs: dict[str, Any] = Field(description='关键字参数')
    paused: bool = Field(description='是否暂停')
    status: str = Field(description='任务状态')
    coalesce: str = Field(description='合并策略')
    misfire_grace_time: float | None = Field(None, description='错过触发宽限秒数')
    max_jitter: float | None = Field(None, description='最大随机抖动秒数')
    job_executor: str = Field(description='执行器')
    job_result_expiration_time: float = Field(description='任务结果保留秒数')
    metadata: dict[str, Any] = Field(description='元数据')
    next_fire_time: datetime | None = Field(None, description='下次运行时间')
    last_fire_time: datetime | None = Field(None, description='最近运行时间')
    acquired_by: str | None = Field(None, description='当前获取调度器')
    acquired_until: datetime | None = Field(None, description='获取锁截止时间')
    running_job_count: int = Field(description='运行中任务数量')


class GetSchedulerJobDetail(SchedulerJobSchemaBase):
    """调度任务详情"""


class CreateSchedulerJobParam(SchemaBase):
    """创建调度任务参数"""

    id: str | None = Field(None, description='任务 ID')
    task_id: str = Field(description='APScheduler 任务 ID', min_length=1)
    trigger_type: Literal['date', 'interval', 'cron'] = Field(description='触发器类型')
    trigger_config: dict[str, Any] = Field(description='触发器配置')
    args: list[Any] = Field(default_factory=list, description='位置参数')
    kwargs: dict[str, Any] = Field(default_factory=dict, description='关键字参数')
    paused: bool = Field(False, description='是否暂停')
    coalesce: Literal['earliest', 'latest', 'all'] = Field('latest', description='合并策略')
    job_executor: str | None = Field(None, description='执行器')
    misfire_grace_time: float | None = Field(None, description='错过触发宽限秒数')
    max_jitter: float | None = Field(None, description='最大随机抖动秒数')
    job_result_expiration_time: float = Field(0, ge=0, description='任务结果保留秒数')
    metadata: dict[str, Any] = Field(default_factory=dict, description='元数据')
    conflict_policy: Literal['replace', 'do_nothing', 'exception'] = Field('exception', description='任务冲突策略')


class DeleteSchedulerJobParam(SchemaBase):
    """批量删除调度任务参数"""

    ids: list[str] = Field(description='任务 ID 列表', min_length=1)


class RunSchedulerJobDetail(SchemaBase):
    """手动运行任务详情"""

    schedule_id: str = Field(description='任务 ID')
    job_id: str = Field(description='运行任务 ID')


class SchedulerRunSchemaBase(SchemaBase):
    """调度任务运行记录基础模型"""

    job_id: str = Field(description='运行任务 ID')
    schedule_id: str | None = Field(None, description='任务 ID')
    task_id: str = Field(description='APScheduler 任务 ID')
    scheduler_id: str | None = Field(None, description='执行调度器 ID')
    scheduled_start: datetime | None = Field(None, description='计划开始时间')
    started_at: datetime | None = Field(None, description='实际开始时间')
    finished_at: datetime | None = Field(None, description='结束时间')
    duration_seconds: float | None = Field(None, description='运行耗时秒数')
    outcome: str = Field(description='运行结果')
    exception_type: str | None = Field(None, description='异常类型')
    exception_message: str | None = Field(None, description='异常信息')
    exception_traceback: list[str] | None = Field(None, description='异常堆栈')


class GetSchedulerRunDetail(SchedulerRunSchemaBase):
    """调度任务运行记录"""


class DeleteSchedulerRunParam(SchemaBase):
    """批量删除调度任务运行记录参数"""

    job_ids: list[str] = Field(description='运行任务 ID 列表', min_length=1)
