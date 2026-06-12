from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from apscheduler import AsyncScheduler
from fastapi import FastAPI

from backend.common.lifespan import lifespan_manager
from backend.common.log import log
from backend.core.conf import settings


class SchedulerManager:
    """APScheduler 调度器管理器"""

    def __init__(self) -> None:
        self._scheduler: AsyncScheduler | None = None

    @property
    def scheduler(self) -> AsyncScheduler:
        """获取调度器实例"""
        if self._scheduler is None:
            self._scheduler = AsyncScheduler(identity=settings.SCHEDULER_IDENTITY)
        return self._scheduler


scheduler_manager = SchedulerManager()
_scheduler_lifespan_registered = False


def get_scheduler() -> AsyncScheduler:
    """获取 APScheduler 调度器实例"""
    return scheduler_manager.scheduler


@asynccontextmanager
async def scheduler_lifespan(app: FastAPI) -> AsyncGenerator[dict[str, AsyncScheduler] | None, None]:
    """
    注册 APScheduler 生命周期

    :param app: FastAPI 应用实例
    :return:
    """
    if not settings.SCHEDULER_ENABLED:
        log.info('APScheduler 已禁用')
        yield None
        return

    scheduler = scheduler_manager.scheduler
    async with scheduler:
        await scheduler.start_in_background()
        log.info('APScheduler 已启动')
        try:
            yield {'scheduler': scheduler}
        finally:
            await scheduler.stop()
    log.info('APScheduler 已停止')


def register_scheduler_lifespan() -> None:
    """注册 APScheduler 生命周期钩子"""
    global _scheduler_lifespan_registered
    if _scheduler_lifespan_registered:
        return
    lifespan_manager.register(scheduler_lifespan)
    _scheduler_lifespan_registered = True
