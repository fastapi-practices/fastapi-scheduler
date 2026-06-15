# FastAPI Scheduler Frontend

Vue 3 + TypeScript + Vite + Antdv Next 控制台前端

## 启动

```bash
pnpm install
pnpm dev
```

默认通过 Vite proxy 将 `/api` 转发到 `http://127.0.0.1:8000`，可在 `.env` 中覆盖：

```env
VITE_API_BASE=/api/v1
```

## 构建

```bash
pnpm build
```
