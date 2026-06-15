# Backend

FastAPI Scheduler 后端目录，基于 fba-slim，并通过 `backend/plugin/scheduler` 插件集成 APScheduler

## 启动

```bash
uv sync
uv run fba run 127.0.0.1 8000
```

## Docker

```bash
docker build -f Dockerfile -t fastapi_scheduler .
docker run -d -p 8000:8001 --name fastapi_scheduler fastapi_scheduler
```

APScheduler 会由 scheduler 插件随 FastAPI lifespan 自动启停，可通过 `SCHEDULER_ENABLED=false` 禁用
