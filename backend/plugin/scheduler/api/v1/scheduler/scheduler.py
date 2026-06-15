from typing import Annotated

from fastapi import APIRouter, Path, Query

from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.plugin.scheduler.schema.scheduler import (
    GetSchedulerJobDetail,
    GetSchedulerRunDetail,
    GetSchedulerStatusDetail,
    RunSchedulerJobDetail,
)
from backend.plugin.scheduler.service.scheduler_service import scheduler_service

router = APIRouter()


@router.get('/status', summary='获取调度器状态', dependencies=[DependsJwtAuth])
async def get_scheduler_status() -> ResponseSchemaModel[GetSchedulerStatusDetail]:
    data = await scheduler_service.get_status()
    return response_base.success(data=data)


@router.get('/jobs', summary='获取所有调度任务', dependencies=[DependsJwtAuth])
async def get_all_scheduler_jobs() -> ResponseSchemaModel[list[GetSchedulerJobDetail]]:
    data = await scheduler_service.get_all()
    return response_base.success(data=data)


@router.get('/jobs/{schedule_id}', summary='获取调度任务详情', dependencies=[DependsJwtAuth])
async def get_scheduler_job(
    schedule_id: Annotated[str, Path(description='任务 ID')],
) -> ResponseSchemaModel[GetSchedulerJobDetail]:
    data = await scheduler_service.get(schedule_id=schedule_id)
    return response_base.success(data=data)


@router.put('/jobs/{schedule_id}/pause', summary='暂停调度任务', dependencies=[DependsJwtAuth])
async def pause_scheduler_job(
    schedule_id: Annotated[str, Path(description='任务 ID')],
) -> ResponseSchemaModel[GetSchedulerJobDetail]:
    data = await scheduler_service.pause(schedule_id=schedule_id)
    return response_base.success(data=data)


@router.put('/jobs/{schedule_id}/resume', summary='恢复调度任务', dependencies=[DependsJwtAuth])
async def resume_scheduler_job(
    schedule_id: Annotated[str, Path(description='任务 ID')],
) -> ResponseSchemaModel[GetSchedulerJobDetail]:
    data = await scheduler_service.resume(schedule_id=schedule_id)
    return response_base.success(data=data)


@router.post('/jobs/{schedule_id}/run', summary='立即运行调度任务', dependencies=[DependsJwtAuth])
async def run_scheduler_job(
    schedule_id: Annotated[str, Path(description='任务 ID')],
) -> ResponseSchemaModel[RunSchedulerJobDetail]:
    data = await scheduler_service.run(schedule_id=schedule_id)
    return response_base.success(data=data)


@router.delete('/jobs/{schedule_id}', summary='删除调度任务', dependencies=[DependsJwtAuth])
async def delete_scheduler_job(
    schedule_id: Annotated[str, Path(description='任务 ID')],
) -> ResponseModel:
    await scheduler_service.delete(schedule_id=schedule_id)
    return response_base.success()


@router.get('/runs', summary='获取调度运行记录', dependencies=[DependsJwtAuth])
async def get_all_scheduler_runs(
    schedule_id: Annotated[str | None, Query(description='任务 ID')] = None,
    limit: Annotated[int, Query(ge=1, le=200, description='返回数量')] = 100,
) -> ResponseSchemaModel[list[GetSchedulerRunDetail]]:
    data = scheduler_service.get_runs(schedule_id=schedule_id, limit=limit)
    return response_base.success(data=data)
