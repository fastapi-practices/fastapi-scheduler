<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { message } from 'antdv-next'
import {
  BarChartOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FieldTimeOutlined,
  LineChartOutlined,
  PlayCircleOutlined,
  WarningOutlined,
} from '@antdv-next/icons'

import { schedulerApi, type SchedulerJob, type SchedulerRun, type SchedulerStatus } from '../api/scheduler'
import { formatDateTime, getErrorMessage } from '../utils/format'

const status = ref<SchedulerStatus | null>(null)
const jobs = ref<SchedulerJob[]>([])
const runs = ref<SchedulerRun[]>([])
const loading = ref(false)

const totalJobs = computed(() => jobs.value.length)
const totalRuns = computed(() => runs.value.length)
const successRuns = computed(() => runs.value.filter((run) => run.outcome === 'success').length)
const failedRuns = computed(() => runs.value.filter((run) => run.outcome !== 'success').length)
const successRate = computed(() => {
  if (!totalRuns.value) return 0
  return Number(((successRuns.value / totalRuns.value) * 100).toFixed(1))
})
const jobStatusItems = computed(() => {
  const counts = jobs.value.reduce<Record<string, number>>((data, job) => {
    data[job.status] = (data[job.status] || 0) + 1
    return data
  }, {})
  return ['scheduled', 'running', 'paused', 'completed'].map((key) => {
    const meta = getJobStatusMeta(key)
    const value = counts[key] || 0
    return {
      key,
      label: meta.text,
      value,
      color: meta.progressColor,
      tagColor: meta.tagColor,
      percent: getPercent(value, totalJobs.value),
    }
  })
})

const outcomeItems = computed(() => {
  const counts = runs.value.reduce<Record<string, number>>((data, run) => {
    data[run.outcome] = (data[run.outcome] || 0) + 1
    return data
  }, {})
  return Object.entries(counts).map(([key, value]) => {
    const meta = getOutcomeMeta(key)
    return {
      key,
      label: meta.text,
      value,
      color: meta.progressColor,
      tagColor: meta.tagColor,
      percent: getPercent(value, totalRuns.value),
    }
  })
})

const nextJobs = computed(() =>
  jobs.value
    .filter((job) => job.next_fire_time)
    .slice()
    .sort((left, right) => Date.parse(left.next_fire_time || '') - Date.parse(right.next_fire_time || ''))
    .slice(0, 5),
)

const recentRuns = computed(() => runs.value.slice(0, 8))
const recentFailures = computed(() => runs.value.filter((run) => run.outcome !== 'success').slice(0, 4))

const getPercent = (value: number, total: number) => {
  if (!total) return 0
  return Number(((value / total) * 100).toFixed(1))
}

const getJobStatusMeta = (value: string) => {
  const meta: Record<string, { tagColor: string; progressColor: string; text: string }> = {
    scheduled: { tagColor: 'processing', progressColor: '#1677ff', text: '等待中' },
    running: { tagColor: 'success', progressColor: '#52c41a', text: '运行中' },
    paused: { tagColor: 'warning', progressColor: '#faad14', text: '已暂停' },
    completed: { tagColor: 'default', progressColor: '#8c8c8c', text: '已完成' },
  }
  return meta[value] || { tagColor: 'default', progressColor: '#8c8c8c', text: value || '-' }
}

const getOutcomeMeta = (value: string) => {
  const meta: Record<string, { tagColor: string; progressColor: string; text: string }> = {
    success: { tagColor: 'success', progressColor: '#52c41a', text: '成功' },
    error: { tagColor: 'error', progressColor: '#ff4d4f', text: '失败' },
    missed_start_deadline: { tagColor: 'warning', progressColor: '#faad14', text: '错过窗口' },
    deserialization_failed: { tagColor: 'error', progressColor: '#ff4d4f', text: '反序列化失败' },
    cancelled: { tagColor: 'default', progressColor: '#8c8c8c', text: '已取消' },
    abandoned: { tagColor: 'error', progressColor: '#ff4d4f', text: '已丢弃' },
  }
  return meta[value] || { tagColor: 'default', progressColor: '#8c8c8c', text: value || '-' }
}

const formatDuration = (value?: number | null) => {
  if (value === null || value === undefined) return '-'
  return `${value.toFixed(3)}s`
}

const loadAll = async () => {
  loading.value = true
  try {
    const [statusData, jobData, runData] = await Promise.all([
      schedulerApi.getStatus(),
      schedulerApi.getJobs(),
      schedulerApi.getRuns({ limit: 200 }),
    ])
    status.value = statusData
    jobs.value = jobData
    runs.value = runData
  } catch (error) {
    message.error(getErrorMessage(error, '分析数据加载失败'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadAll()
})
</script>

<template>
  <div class="analysis-page">
    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :md="12" :xl="6">
        <a-card class="analysis-stat" variant="borderless">
          <a-statistic title="调度计划" :value="status?.schedule_count ?? totalJobs">
            <template #prefix>
              <FieldTimeOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :md="12" :xl="6">
        <a-card class="analysis-stat" variant="borderless">
          <a-statistic title="运行中任务" :value="status?.running_job_count ?? 0">
            <template #prefix>
              <PlayCircleOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :md="12" :xl="6">
        <a-card class="analysis-stat" variant="borderless">
          <a-statistic title="成功率" :value="successRate" suffix="%">
            <template #prefix>
              <CheckCircleOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :md="12" :xl="6">
        <a-card class="analysis-stat" variant="borderless">
          <a-statistic title="异常执行" :value="failedRuns">
            <template #prefix>
              <WarningOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :xl="12">
        <a-card title="任务状态分布" class="analysis-card" :loading="loading">
          <div class="analysis-metric-list">
            <div v-for="item in jobStatusItems" :key="item.key" class="analysis-metric-row">
              <a-flex justify="space-between" align="center" gap="middle">
                <a-space>
                  <a-tag :color="item.tagColor">{{ item.label }}</a-tag>
                  <a-typography-text type="secondary">{{ item.value }} 个</a-typography-text>
                </a-space>
                <a-typography-text type="secondary">{{ item.percent }}%</a-typography-text>
              </a-flex>
              <a-progress :percent="item.percent" :show-info="false" :stroke-color="item.color" />
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :xs="24" :xl="12">
        <a-card title="执行结果分布" class="analysis-card" :loading="loading">
          <a-empty v-if="!outcomeItems.length" description="暂无运行记录" />
          <div v-else class="analysis-metric-list">
            <div v-for="item in outcomeItems" :key="item.key" class="analysis-metric-row">
              <a-flex justify="space-between" align="center" gap="middle">
                <a-space>
                  <a-tag :color="item.tagColor">{{ item.label }}</a-tag>
                  <a-typography-text type="secondary">{{ item.value }} 次</a-typography-text>
                </a-space>
                <a-typography-text type="secondary">{{ item.percent }}%</a-typography-text>
              </a-flex>
              <a-progress :percent="item.percent" :show-info="false" :stroke-color="item.color" />
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :xl="12">
        <a-card title="即将运行" class="analysis-card" :loading="loading">
          <template #extra>
            <ClockCircleOutlined />
          </template>
          <a-empty v-if="!nextJobs.length" description="暂无即将运行的任务" />
          <div v-else class="analysis-list">
            <div v-for="job in nextJobs" :key="job.id" class="analysis-list-item">
              <div class="analysis-list-main">
                <a-typography-text code>{{ job.id }}</a-typography-text>
                <a-typography-text class="analysis-list-sub">{{ job.task_id }}</a-typography-text>
              </div>
              <a-tag color="processing">{{ formatDateTime(job.next_fire_time) }}</a-tag>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :xs="24" :xl="12">
        <a-card title="异常摘要" class="analysis-card" :loading="loading">
          <template #extra>
            <BarChartOutlined />
          </template>
          <a-empty v-if="!recentFailures.length" description="暂无异常执行" />
          <div v-else class="analysis-list">
            <div v-for="run in recentFailures" :key="run.job_id" class="analysis-list-item analysis-list-item--danger">
              <div class="analysis-list-main">
                <a-typography-text code>{{ run.schedule_id || run.job_id }}</a-typography-text>
                <a-typography-text class="analysis-list-sub">
                  {{ run.exception_message || getOutcomeMeta(run.outcome).text }}
                </a-typography-text>
              </div>
              <a-tag :color="getOutcomeMeta(run.outcome).tagColor">
                {{ formatDateTime(run.finished_at) }}
              </a-tag>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-card title="最近执行脉冲" class="analysis-card" :loading="loading">
      <template #extra>
        <LineChartOutlined />
      </template>
      <a-empty v-if="!recentRuns.length" description="暂无运行记录" />
      <div v-else class="analysis-pulse-grid">
        <div v-for="run in recentRuns" :key="run.job_id" class="analysis-pulse-card">
          <a-flex justify="space-between" align="center" gap="small">
            <a-tag :color="getOutcomeMeta(run.outcome).tagColor">
              {{ getOutcomeMeta(run.outcome).text }}
            </a-tag>
            <a-typography-text type="secondary">{{ formatDuration(run.duration_seconds) }}</a-typography-text>
          </a-flex>
          <a-typography-text code class="analysis-pulse-id">{{ run.schedule_id || run.job_id }}</a-typography-text>
          <div class="analysis-pulse-time">{{ formatDateTime(run.finished_at) }}</div>
        </div>
      </div>
    </a-card>
  </div>
</template>

<style scoped>
.analysis-page {
  display: grid;
  gap: 16px;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow-x: hidden;
}

.analysis-stat,
.analysis-card {
  min-width: 0;
  background: var(--surface-1);
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

.analysis-metric-list,
.analysis-list {
  display: grid;
  gap: 12px;
}

.analysis-metric-row {
  min-width: 0;
}

.analysis-list-item {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  min-width: 0;
  padding: 12px;
  background: var(--surface-2);
  border: 1px solid var(--surface-border);
  border-radius: 10px;
}

.analysis-list-item--danger {
  border-color: rgba(255, 77, 79, 0.32);
}

.analysis-list-main {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.analysis-list-sub {
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.analysis-pulse-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.analysis-pulse-card {
  min-width: 0;
  padding: 12px;
  background: var(--surface-2);
  border: 1px solid var(--surface-border);
  border-radius: 10px;
}

.analysis-pulse-id {
  display: block;
  margin-top: 10px;
}

.analysis-pulse-time {
  margin-top: 6px;
  color: var(--text-secondary);
  font-size: 12px;
}

@media (max-width: 575px) {
  .analysis-list-item {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
