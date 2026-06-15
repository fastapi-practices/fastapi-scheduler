from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.scheduler.api.v1.scheduler import router as scheduler_router

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

v1.include_router(scheduler_router)
