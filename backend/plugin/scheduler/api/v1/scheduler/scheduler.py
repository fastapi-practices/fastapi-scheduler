from typing import Annotated

from fastapi import APIRouter, Body, Path, Query

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession
from backend.plugin.scheduler.schema.scheduler import (
    CreateSchedulerJobParam,
    DeleteSchedulerJobParam,
    DeleteSchedulerRunParam,
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


@router.post('/jobs', summary='创建调度任务', dependencies=[DependsJwtAuth])
async def create_scheduler_job(obj: CreateSchedulerJobParam) -> ResponseSchemaModel[GetSchedulerJobDetail]:
    data = await scheduler_service.create(obj=obj)
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


@router.delete('/jobs', summary='批量删除调度任务', dependencies=[DependsJwtAuth])
async def delete_scheduler_jobs(
    obj: Annotated[DeleteSchedulerJobParam, Body(description='批量删除调度任务参数')],
) -> ResponseModel:
    count = await scheduler_service.delete_jobs(schedule_ids=obj.ids)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete('/jobs/{schedule_id}', summary='删除调度任务', dependencies=[DependsJwtAuth])
async def delete_scheduler_job(
    schedule_id: Annotated[str, Path(description='任务 ID')],
) -> ResponseModel:
    await scheduler_service.delete(schedule_id=schedule_id)
    return response_base.success()


@router.get(
    '/runs',
    summary='分页获取所有调度运行记录',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_scheduler_runs_paginated(
    db: CurrentSession,
    schedule_id: Annotated[str | None, Query(description='任务 ID')] = None,
) -> ResponseSchemaModel[PageData[GetSchedulerRunDetail]]:
    page_data = await scheduler_service.get_list(db=db, schedule_id=schedule_id)
    return response_base.success(data=page_data)


@router.delete('/runs', summary='批量删除调度运行记录', dependencies=[DependsJwtAuth])
async def delete_scheduler_runs(
    obj: Annotated[DeleteSchedulerRunParam, Body(description='批量删除调度运行记录参数')],
) -> ResponseModel:
    count = scheduler_service.delete_runs(job_ids=obj.job_ids)
    if count > 0:
        return response_base.success()
    return response_base.fail()
