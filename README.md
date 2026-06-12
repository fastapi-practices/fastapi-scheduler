# FastAPI Scheduler

基于 fba-slim 的 FastAPI 任务调度服务，已集成 APScheduler `4.0.0a6`

## 特性

- FastAPI 后端基础架构
- APScheduler 随应用 lifespan 自动启停
- PostgreSQL / MySQL 与 Redis 支持
- uv 管理依赖
- 保留 fba CLI、插件、迁移、日志能力

## 快速开始

```bash
uv sync
cp backend/.env.example backend/.env
uv run fba init --auto
uv run fba run 127.0.0.1 8000
```

访问地址：

- Swagger：`http://127.0.0.1:8000/docs`
- API 前缀：`http://127.0.0.1:8000/api/v1`

## 关键配置

在 `backend/.env` 中配置数据库、Redis 和调度器：

```env
DATABASE_TYPE='postgresql'
DATABASE_HOST='127.0.0.1'
DATABASE_PORT=5432
DATABASE_USER='postgres'
DATABASE_PASSWORD='123456'
REDIS_HOST='127.0.0.1'
REDIS_PORT=6379
REDIS_PASSWORD=''
REDIS_DATABASE=0
SCHEDULER_ENABLED=true
SCHEDULER_IDENTITY='fastapi-scheduler'
TOKEN_SECRET_KEY='replace-with-your-secret'
```

## 调度器

调度器入口：`backend/common/scheduler.py`

```python
from apscheduler.triggers.interval import IntervalTrigger

from backend.common.scheduler import get_scheduler


async def demo_job() -> None:
    print('scheduler job executed')


async def register_jobs() -> None:
    scheduler = get_scheduler()
    await scheduler.add_schedule(demo_job, IntervalTrigger(seconds=30), id='demo_job')
```

当前默认使用内存调度器，不默认创建任务表，也不默认持久化任务

## 常用命令

```bash
uv run fba run 127.0.0.1 8000
uv run fba format
uv run fba alembic revision -m "message"
uv run fba alembic upgrade head
uv export --format requirements-txt --no-hashes -o requirements.txt
```

## Docker

```bash
docker build -f Dockerfile -t fastapi_scheduler .
docker compose up -d
```

## 许可证

MIT
