<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { message, Tag, TypographyText } from 'antdv-next'
import {
  FullscreenOutlined,
  ReloadOutlined,
  SearchOutlined,
} from '@antdv-next/icons'

import { schedulerApi, type SchedulerJob, type SchedulerRun } from '../api/scheduler'
import { AdminDataTable, AdminSearchForm, type AdminSearchField } from '../components/admin-kit'
import { formatDateTime, getErrorMessage } from '../utils/format'

type TableRecord = Record<string, any>

const jobs = ref<SchedulerJob[]>([])
const runs = ref<SchedulerRun[]>([])
const selectedRun = ref<SchedulerRun | null>(null)
const loading = ref(false)
const detailOpen = ref(false)
const searchVisible = ref(true)
const pageMaximized = ref(false)
const filters = ref<Record<string, any>>({
  job_id: '',
  schedule_id: '',
  task_id: '',
  outcome: undefined,
  run_range: [],
})
const appliedFilters = ref<Record<string, any>>({ ...filters.value })
const detailDrawerSize = 720

const runColumns = [
  { title: '运行 ID', dataIndex: 'job_id', key: 'job_id', width: 250 },
  { title: '任务 ID', dataIndex: 'schedule_id', key: 'schedule_id', width: 180 },
  { title: '任务函数', dataIndex: 'task_id', key: 'task_id', width: 240 },
  { title: '结果', dataIndex: 'outcome', key: 'outcome', width: 110 },
  { title: '计划开始', dataIndex: 'scheduled_start', key: 'scheduled_start', width: 180 },
  { title: '实际开始', dataIndex: 'started_at', key: 'started_at', width: 180 },
  { title: '结束时间', dataIndex: 'finished_at', key: 'finished_at', width: 180 },
  { title: '耗时', dataIndex: 'duration_seconds', key: 'duration_seconds', width: 100 },
  { title: '操作', key: 'actions', width: 90, fixed: 'right' as const },
]

const scheduleOptions = computed(() => {
  const values = new Set<string>()
  jobs.value.forEach((job) => values.add(job.id))
  runs.value.forEach((run) => {
    if (run.schedule_id) values.add(run.schedule_id)
  })
  return Array.from(values).map((value) => ({ label: value, value }))
})

const outcomeOptions = computed(() =>
  Array.from(new Set(runs.value.map((run) => run.outcome)))
    .filter(Boolean)
    .map((value) => ({ label: getOutcomeMeta(value).text, value })),
)

const searchFields = computed<AdminSearchField[]>(() => [
  {
    key: 'job_id',
    label: '运行 ID',
    type: 'input',
    placeholder: '请输入',
  },
  {
    key: 'schedule_id',
    label: '任务 ID',
    type: 'select',
    placeholder: '请选择',
    options: scheduleOptions.value,
  },
  {
    key: 'task_id',
    label: '任务函数',
    type: 'input',
    placeholder: '请输入',
  },
  {
    key: 'outcome',
    label: '结果',
    type: 'select',
    placeholder: '请选择',
    options: outcomeOptions.value,
  },
  {
    key: 'run_range',
    label: '执行时间',
    type: 'dateRange',
    placeholder: ['开始日期', '结束日期'],
  },
])

const isDateInRange = (value?: string | null, range?: any[]) => {
  if (!range?.length || !value) return true
  const current = Date.parse(value)
  const start = range[0] ? Number(range[0].valueOf?.() ?? Date.parse(range[0])) : Number.NEGATIVE_INFINITY
  const end = range[1] ? Number(range[1].valueOf?.() ?? Date.parse(range[1])) : Number.POSITIVE_INFINITY
  return Number.isFinite(current) && current >= start && current <= end
}

const filteredRuns = computed(() => {
  const jobId = String(appliedFilters.value.job_id || '').trim().toLowerCase()
  const taskId = String(appliedFilters.value.task_id || '').trim().toLowerCase()
  return runs.value.filter((run) => {
    const matchedJob = !jobId || run.job_id.toLowerCase().includes(jobId)
    const matchedTask = !taskId || run.task_id.toLowerCase().includes(taskId)
    const matchedOutcome = !appliedFilters.value.outcome || run.outcome === appliedFilters.value.outcome
    const matchedSchedule = !appliedFilters.value.schedule_id || run.schedule_id === appliedFilters.value.schedule_id
    const matchedTime = isDateInRange(run.started_at || run.scheduled_start, appliedFilters.value.run_range)
    return matchedJob && matchedTask && matchedOutcome && matchedSchedule && matchedTime
  })
})

const tableScrollY = computed(() => (searchVisible.value ? 'calc(100vh - 420px)' : 'calc(100vh - 292px)'))

const selectedRunDescriptionItems = computed(() => {
  const run = selectedRun.value
  if (!run) return []
  const outcome = getOutcomeMeta(run.outcome)
  const codeText = (value?: string | null) => h(TypographyText, { code: true }, () => value || '-')

  return [
    { key: 'job_id', label: '运行 ID', content: codeText(run.job_id) },
    { key: 'schedule_id', label: '任务 ID', content: codeText(run.schedule_id) },
    { key: 'task_id', label: '任务函数', content: run.task_id || '-' },
    { key: 'scheduler_id', label: '调度器 ID', content: run.scheduler_id || '-' },
    { key: 'outcome', label: '结果', content: h(Tag, { color: outcome.color }, () => outcome.text) },
    { key: 'scheduled_start', label: '计划开始', content: formatDateTime(run.scheduled_start) },
    { key: 'started_at', label: '实际开始', content: formatDateTime(run.started_at) },
    { key: 'finished_at', label: '结束时间', content: formatDateTime(run.finished_at) },
    { key: 'duration_seconds', label: '耗时', content: formatDuration(run.duration_seconds) },
    { key: 'exception_type', label: '异常类型', content: run.exception_type || '-' },
    { key: 'exception_message', label: '异常信息', content: run.exception_message || '-' },
  ]
})

const tracebackText = computed(() => selectedRun.value?.exception_traceback?.join('\n') || '')

const getOutcomeMeta = (value: string) => {
  const meta: Record<string, { color: string; text: string }> = {
    success: { color: 'success', text: '成功' },
    error: { color: 'error', text: '失败' },
    missed_start_deadline: { color: 'warning', text: '错过窗口' },
    deserialization_failed: { color: 'error', text: '反序列化失败' },
    cancelled: { color: 'default', text: '已取消' },
    abandoned: { color: 'error', text: '已丢弃' },
  }
  return meta[value] || { color: 'default', text: value || '-' }
}

const formatDuration = (value?: number | null) => {
  if (value === null || value === undefined) return '-'
  return `${value.toFixed(3)}s`
}

const applyFilters = (value: Record<string, any>) => {
  appliedFilters.value = { ...value }
}

const toggleFullscreen = () => {
  pageMaximized.value = !pageMaximized.value
}

const toSchedulerRun = (record: SchedulerRun | TableRecord) => record as SchedulerRun

const openRunDetail = (record: SchedulerRun | TableRecord) => {
  selectedRun.value = toSchedulerRun(record)
  detailOpen.value = true
}

const loadAll = async () => {
  loading.value = true
  try {
    const [jobData, runData] = await Promise.all([
      schedulerApi.getJobs(),
      schedulerApi.getRuns({ limit: 200 }),
    ])
    jobs.value = jobData
    runs.value = runData
  } catch (error) {
    message.error(getErrorMessage(error, '运行记录加载失败'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadAll()
})
</script>

<template>
  <div :class="['runs-page', { 'runs-page--maximized': pageMaximized }]">
    <AdminSearchForm
      v-if="searchVisible"
      v-model:model="filters"
      :fields="searchFields"
      :loading="loading"
      @search="applyFilters"
      @reset="applyFilters"
    />

    <AdminDataTable
      title="运行记录"
      row-key="job_id"
      :columns="runColumns"
      :data-source="filteredRuns"
      :loading="loading"
      fill
      :scroll-x="1510"
      :scroll-y="tableScrollY"
      empty-text="暂无运行记录"
    >
      <template #toolbar>
        <a-button type="primary" :loading="loading" @click="loadAll">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新记录
        </a-button>
        <a-tooltip title="筛选">
          <a-button shape="circle" type="primary" @click="searchVisible = !searchVisible">
            <template #icon>
              <SearchOutlined />
            </template>
          </a-button>
        </a-tooltip>
        <a-tooltip title="刷新">
          <a-button shape="circle" :loading="loading" @click="loadAll">
            <template #icon>
              <ReloadOutlined />
            </template>
          </a-button>
        </a-tooltip>
        <a-tooltip :title="pageMaximized ? '退出全屏' : '全屏'">
          <a-button shape="circle" @click="toggleFullscreen">
            <template #icon>
              <FullscreenOutlined />
            </template>
          </a-button>
        </a-tooltip>
      </template>
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'job_id'">
          <a-typography-text code>{{ record.job_id }}</a-typography-text>
        </template>
        <template v-else-if="column.key === 'schedule_id'">
          <a-typography-text code>{{ record.schedule_id || '-' }}</a-typography-text>
        </template>
        <template v-else-if="column.key === 'task_id'">
          <a-typography-text class="runs-nowrap">{{ record.task_id }}</a-typography-text>
        </template>
        <template v-else-if="column.key === 'outcome'">
          <a-tag :color="getOutcomeMeta(record.outcome).color">
            {{ getOutcomeMeta(record.outcome).text }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'scheduled_start'">
          {{ formatDateTime(record.scheduled_start) }}
        </template>
        <template v-else-if="column.key === 'started_at'">
          {{ formatDateTime(record.started_at) }}
        </template>
        <template v-else-if="column.key === 'finished_at'">
          {{ formatDateTime(record.finished_at) }}
        </template>
        <template v-else-if="column.key === 'duration_seconds'">
          {{ formatDuration(record.duration_seconds) }}
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-button type="link" size="small" @click="openRunDetail(record)">详情</a-button>
        </template>
      </template>
    </AdminDataTable>

    <a-drawer
      v-model:open="detailOpen"
      :size="detailDrawerSize"
      :title="selectedRun ? `运行详情：${selectedRun.job_id}` : '运行详情'"
      root-class="runs-detail-drawer"
      destroy-on-hidden
    >
      <template v-if="selectedRun">
        <a-descriptions bordered size="small" :column="1" :items="selectedRunDescriptionItems" />
        <template v-if="tracebackText">
          <a-divider title-placement="start">异常堆栈</a-divider>
          <pre class="runs-json">{{ tracebackText }}</pre>
        </template>
      </template>
    </a-drawer>
  </div>
</template>

<style scoped>
.runs-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  height: 100%;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}

.runs-page--maximized {
  position: fixed;
  inset: 108px 18px 16px 258px;
  z-index: 60;
  width: auto;
  height: auto;
  padding: 0;
  background: var(--page-bg);
}

:global(.admin-shell-root--collapsed) .runs-page--maximized {
  left: 82px;
}

@media (max-width: 1199px) {
  .runs-page--maximized {
    inset: 104px 12px 12px;
  }
}

.runs-nowrap {
  white-space: nowrap;
}

.runs-json {
  min-height: 120px;
  margin: 0;
  padding: 12px;
  color: var(--text-primary);
  background: var(--surface-2);
  border: 1px solid var(--surface-border);
  border-radius: 8px;
}

:global(.runs-detail-drawer .ant-drawer-content-wrapper) {
  max-width: calc(100vw - 24px);
}
</style>
