from fastapi import APIRouter

from backend.plugin.scheduler.api.v1.scheduler.scheduler import router as scheduler_router

router = APIRouter(prefix='/scheduler')

router.include_router(scheduler_router, tags=['调度器'])
