# Scheduler

基于 APScheduler 提供应用生命周期内的异步调度器运行时

## 插件类型

- 应用级插件

## 配置说明

插件目录下 `plugin.toml` 的 `[settings]` 中包含以下内容：

```toml
[settings]
SCHEDULER_ENABLED = true
SCHEDULER_IDENTITY = "fastapi-scheduler"
```

当前项目的 `backend/core/conf.py` 已包含以下字段：

```python
##################################################
# [ Plugin ] scheduler
##################################################
# 基础配置（in plugin.toml）
SCHEDULER_ENABLED: bool = True
SCHEDULER_IDENTITY: str = 'fastapi-scheduler'
```

## 使用方式

1. 在业务代码中获取插件提供的 APScheduler 调度器实例并注册任务
2. 新增调度任务时填写已注册任务 ID，或填写可导入函数引用，例如 `backend.plugin.scheduler.utils.tasks:scheduler_noop`

## 卸载说明

- 移除插件目录并清理相关调度器配置
- 移除调用调度器实例的业务代码

## 联系方式

- 作者：`fastapi-scheduler`
- 反馈方式：提交 Issue 或 PR
