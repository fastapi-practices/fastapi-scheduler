from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from apscheduler import AsyncScheduler
from fastapi import FastAPI

from backend.common.log import log
from backend.core.conf import settings
from backend.plugin.scheduler.utils.scheduler import scheduler_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict[str, AsyncScheduler] | None, None]:
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
        scheduler_manager.register_event_listener()
        await scheduler.start_in_background()
        scheduler_manager.mark_started()
        log.info('APScheduler 已启动')
        try:
            yield {'scheduler': scheduler}
        finally:
            await scheduler.stop()
            scheduler_manager.unregister_event_listener()
            scheduler_manager.mark_stopped()
    log.info('APScheduler 已停止')
