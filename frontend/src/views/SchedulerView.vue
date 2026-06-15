<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { message, Tag, TypographyText } from 'antdv-next'
import {
  DeleteOutlined,
  FullscreenOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  SearchOutlined,
} from '@antdv-next/icons'

import { schedulerApi, type SchedulerJob, type SchedulerRun, type SchedulerStatus } from '../api/scheduler'
import { AdminDataTable, AdminSearchForm, type AdminSearchField } from '../components/admin-kit'
import { formatDateTime, getErrorMessage } from '../utils/format'

const status = ref<SchedulerStatus | null>(null)
const jobs = ref<SchedulerJob[]>([])
const recentRuns = ref<SchedulerRun[]>([])
const selectedJob = ref<SchedulerJob | null>(null)
const loading = ref(false)
const detailLoading = ref(false)
const recentRunsLoading = ref(false)
const detailOpen = ref(false)
const searchVisible = ref(true)
const pageMaximized = ref(false)
const actionLoading = ref<Record<string, boolean>>({})
const filters = ref<Record<string, any>>({
  schedule_id: '',
  task_id: '',
  status: undefined,
  trigger_type: undefined,
  next_fire_range: [],
})
const appliedFilters = ref<Record<string, any>>({ ...filters.value })
type TableRecord = Record<string, any>
const detailDrawerSize = 736

const jobColumns = [
  { title: '任务 ID', dataIndex: 'id', key: 'id', width: 220 },
  { title: '任务函数', dataIndex: 'task_id', key: 'task_id', width: 280 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 130 },
  { title: '触发器', dataIndex: 'trigger', key: 'trigger', minWidth: 260, ellipsis: true },
  { title: '下次运行', dataIndex: 'next_fire_time', key: 'next_fire_time', width: 190 },
  { title: '最近运行', dataIndex: 'last_fire_time', key: 'last_fire_time', width: 190 },
  { title: '操作', key: 'actions', width: 230, fixed: 'right' as const },
]

const searchFields = computed<AdminSearchField[]>(() => [
  {
    key: 'schedule_id',
    label: '任务 ID',
    type: 'input',
    placeholder: '请输入',
  },
  {
    key: 'task_id',
    label: '任务函数',
    type: 'input',
    placeholder: '请输入',
  },
  {
    key: 'status',
    label: '状态',
    type: 'select',
    placeholder: '请选择',
    options: [
      { label: '等待中', value: 'scheduled' },
      { label: '运行中', value: 'running' },
      { label: '已暂停', value: 'paused' },
      { label: '已完成', value: 'completed' },
    ],
  },
  {
    key: 'trigger_type',
    label: '触发器',
    type: 'select',
    placeholder: '请选择',
    options: Array.from(new Set(jobs.value.map((job) => job.trigger_type)))
      .filter(Boolean)
      .map((value) => ({ label: value, value })),
  },
  {
    key: 'next_fire_range',
    label: '下次运行',
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

const filteredJobs = computed(() => {
  const scheduleId = String(appliedFilters.value.schedule_id || '').trim().toLowerCase()
  const taskId = String(appliedFilters.value.task_id || '').trim().toLowerCase()
  return jobs.value.filter((job) => {
    const matchedSchedule = !scheduleId || job.id.toLowerCase().includes(scheduleId)
    const matchedTask = !taskId || job.task_id.toLowerCase().includes(taskId)
    const matchedStatus = !appliedFilters.value.status || job.status === appliedFilters.value.status
    const matchedTrigger = !appliedFilters.value.trigger_type || job.trigger_type === appliedFilters.value.trigger_type
    const matchedNextFire = isDateInRange(job.next_fire_time, appliedFilters.value.next_fire_range)
    return matchedSchedule && matchedTask && matchedStatus && matchedTrigger && matchedNextFire
  })
})

const tableScrollY = computed(() => (searchVisible.value ? 'calc(100vh - 420px)' : 'calc(100vh - 292px)'))

const selectedJobDescriptionItems = computed(() => {
  const job = selectedJob.value
  if (!job) return []
  const jobStatus = getJobStatusMeta(job.status)
  const codeText = (value?: string | null) => h(TypographyText, { code: true }, () => value || '-')

  return [
    { key: 'id', label: '任务 ID', content: codeText(job.id) },
    { key: 'task_id', label: '任务函数', content: job.task_id || '-' },
    {
      key: 'status',
      label: '状态',
      content: h(Tag, { color: jobStatus.color }, () => jobStatus.text),
    },
    { key: 'trigger', label: '触发器', content: job.trigger || '-' },
    { key: 'job_executor', label: '执行器', content: job.job_executor || '-' },
    { key: 'coalesce', label: '合并策略', content: job.coalesce || '-' },
    { key: 'misfire_grace_time', label: 'Misfire 宽限', content: formatSeconds(job.misfire_grace_time) },
    {
      key: 'job_result_expiration_time',
      label: '结果保留',
      content: formatSeconds(job.job_result_expiration_time),
    },
    { key: 'next_fire_time', label: '下次运行', content: formatDateTime(job.next_fire_time) },
    { key: 'last_fire_time', label: '最近运行', content: formatDateTime(job.last_fire_time) },
  ]
})

const selectedJobRecentRuns = computed(() => recentRuns.value.slice(0, 5))

const getJobStatusMeta = (value: string) => {
  const meta: Record<string, { color: string; text: string }> = {
    scheduled: { color: 'processing', text: '等待中' },
    running: { color: 'success', text: '运行中' },
    paused: { color: 'warning', text: '已暂停' },
    completed: { color: 'default', text: '已完成' },
  }
  return meta[value] || { color: 'default', text: value || '-' }
}

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

const formatSeconds = (value?: number | null) => {
  if (value === null || value === undefined) return '-'
  return `${value}s`
}

const stringifyJson = (value: unknown) => JSON.stringify(value ?? {}, null, 2)

const setActionLoading = (key: string, value: boolean) => {
  actionLoading.value = { ...actionLoading.value, [key]: value }
}

const applyFilters = (value: Record<string, any>) => {
  appliedFilters.value = { ...value }
}

const toggleFullscreen = () => {
  pageMaximized.value = !pageMaximized.value
}

const toSchedulerJob = (record: SchedulerJob | TableRecord) => record as SchedulerJob

const updateJob = (job: SchedulerJob) => {
  const index = jobs.value.findIndex((item) => item.id === job.id)
  if (index >= 0) {
    jobs.value.splice(index, 1, job)
  }
  if (selectedJob.value?.id === job.id) {
    selectedJob.value = job
  }
}

const loadRecentRuns = async (scheduleId: string) => {
  recentRunsLoading.value = true
  try {
    recentRuns.value = await schedulerApi.getRuns({ scheduleId, limit: 5 })
  } catch (error) {
    message.error(getErrorMessage(error, '最近运行记录加载失败'))
  } finally {
    recentRunsLoading.value = false
  }
}

const loadAll = async () => {
  loading.value = true
  try {
    const [statusData, jobData] = await Promise.all([schedulerApi.getStatus(), schedulerApi.getJobs()])
    status.value = statusData
    jobs.value = jobData
  } catch (error) {
    message.error(getErrorMessage(error, '调度器数据加载失败'))
  } finally {
    loading.value = false
  }
}

const refreshStatus = async () => {
  try {
    status.value = await schedulerApi.getStatus()
  } catch (error) {
    message.error(getErrorMessage(error, '调度器状态刷新失败'))
  }
}

const openJobDetail = async (record: SchedulerJob | TableRecord) => {
  const job = toSchedulerJob(record)
  selectedJob.value = job
  recentRuns.value = []
  detailOpen.value = true
  detailLoading.value = true
  recentRunsLoading.value = true
  try {
    const [jobDetail, runData] = await Promise.all([
      schedulerApi.getJob(job.id),
      schedulerApi.getRuns({ scheduleId: job.id, limit: 5 }),
    ])
    updateJob(jobDetail)
    recentRuns.value = runData
  } catch (error) {
    message.error(getErrorMessage(error, '任务详情加载失败'))
  } finally {
    detailLoading.value = false
    recentRunsLoading.value = false
  }
}

const handlePause = async (record: SchedulerJob | TableRecord) => {
  const job = toSchedulerJob(record)
  setActionLoading(job.id, true)
  try {
    updateJob(await schedulerApi.pauseJob(job.id))
    await refreshStatus()
    message.success('任务已暂停')
  } catch (error) {
    message.error(getErrorMessage(error, '暂停任务失败'))
  } finally {
    setActionLoading(job.id, false)
  }
}

const handleResume = async (record: SchedulerJob | TableRecord) => {
  const job = toSchedulerJob(record)
  setActionLoading(job.id, true)
  try {
    updateJob(await schedulerApi.resumeJob(job.id))
    await refreshStatus()
    message.success('任务已恢复')
  } catch (error) {
    message.error(getErrorMessage(error, '恢复任务失败'))
  } finally {
    setActionLoading(job.id, false)
  }
}

const handleRun = async (record: SchedulerJob | TableRecord) => {
  const job = toSchedulerJob(record)
  setActionLoading(job.id, true)
  try {
    const result = await schedulerApi.runJob(job.id)
    await refreshStatus()
    if (selectedJob.value?.id === job.id) {
      window.setTimeout(() => {
        void loadRecentRuns(job.id)
      }, 800)
    }
    message.success(`已加入执行队列：${result.job_id}`)
  } catch (error) {
    message.error(getErrorMessage(error, '立即运行失败'))
  } finally {
    setActionLoading(job.id, false)
  }
}

const handleDelete = async (record: SchedulerJob | TableRecord) => {
  const job = toSchedulerJob(record)
  setActionLoading(job.id, true)
  try {
    await schedulerApi.deleteJob(job.id)
    jobs.value = jobs.value.filter((item) => item.id !== job.id)
    if (selectedJob.value?.id === job.id) {
      selectedJob.value = null
      detailOpen.value = false
      recentRuns.value = []
    }
    await refreshStatus()
    message.success('任务已删除')
  } catch (error) {
    message.error(getErrorMessage(error, '删除任务失败'))
  } finally {
    setActionLoading(job.id, false)
  }
}

onMounted(() => {
  void loadAll()
})
</script>

<template>
  <div :class="['scheduler-page', { 'scheduler-page--maximized': pageMaximized }]">
    <a-alert
      v-if="status && (!status.enabled || !status.started)"
      type="warning"
      show-icon
      message="调度器当前不可操作"
      description="调度器未启用或尚未启动时，只能查看基础状态，任务操作会被后端拒绝。"
    />

    <AdminSearchForm
      v-if="searchVisible"
      v-model:model="filters"
      :fields="searchFields"
      :loading="loading"
      @search="applyFilters"
      @reset="applyFilters"
    />

    <AdminDataTable
      title="调度任务"
      row-key="id"
      :columns="jobColumns"
      :data-source="filteredJobs"
      :loading="loading"
      fill
      :scroll-x="1500"
      :scroll-y="tableScrollY"
      empty-text="暂无调度任务"
    >
      <template #toolbar>
        <a-button type="primary" :loading="loading" @click="loadAll">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新任务
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
        <template v-if="column.key === 'id'">
          <a-typography-text code>{{ record.id }}</a-typography-text>
        </template>
        <template v-else-if="column.key === 'task_id'">
          <a-typography-text class="scheduler-nowrap">{{ record.task_id }}</a-typography-text>
        </template>
        <template v-else-if="column.key === 'trigger'">
          <a-tooltip :title="record.trigger">
            <a-tag color="blue">{{ record.trigger_type }}</a-tag>
          </a-tooltip>
        </template>
        <template v-else-if="column.key === 'status'">
          <span
            :class="[
              'scheduler-status-pill',
              `scheduler-status-pill--${record.status}`,
              { 'scheduler-status-pill--on': record.status === 'scheduled' || record.status === 'running' },
            ]"
          >
            <span class="scheduler-status-pill__text">{{ getJobStatusMeta(record.status).text }}</span>
            <span class="scheduler-status-pill__knob" />
          </span>
        </template>
        <template v-else-if="column.key === 'next_fire_time'">
          {{ formatDateTime(record.next_fire_time) }}
        </template>
        <template v-else-if="column.key === 'last_fire_time'">
          {{ formatDateTime(record.last_fire_time) }}
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space size="small">
            <a-button type="link" size="small" @click="openJobDetail(record)">详情</a-button>
            <a-button
              type="link"
              size="small"
              :loading="actionLoading[record.id]"
              @click="handleRun(record)"
            >
              <template #icon>
                <PlayCircleOutlined />
              </template>
              运行
            </a-button>
            <a-button
              v-if="record.paused"
              type="link"
              size="small"
              :loading="actionLoading[record.id]"
              @click="handleResume(record)"
            >
              恢复
            </a-button>
            <a-button
              v-else
              type="link"
              size="small"
              :loading="actionLoading[record.id]"
              @click="handlePause(record)"
            >
              <template #icon>
                <PauseCircleOutlined />
              </template>
              暂停
            </a-button>
            <a-popconfirm
              title="确认删除这个调度任务？"
              ok-text="删除"
              cancel-text="取消"
              @confirm="handleDelete(record)"
            >
              <a-button type="link" size="small" danger :loading="actionLoading[record.id]">
                <template #icon>
                  <DeleteOutlined />
                </template>
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </AdminDataTable>

    <a-drawer
      v-model:open="detailOpen"
      :size="detailDrawerSize"
      :title="selectedJob ? `任务详情：${selectedJob.id}` : '任务详情'"
      root-class="scheduler-detail-drawer"
      destroy-on-hidden
    >
      <a-skeleton :loading="detailLoading" active>
        <template v-if="selectedJob">
          <a-space class="scheduler-drawer-actions" wrap>
            <a-button :loading="actionLoading[selectedJob.id]" @click="handleRun(selectedJob)">
              <template #icon>
                <PlayCircleOutlined />
              </template>
              立即运行
            </a-button>
            <a-button
              v-if="selectedJob.paused"
              :loading="actionLoading[selectedJob.id]"
              @click="handleResume(selectedJob)"
            >
              恢复任务
            </a-button>
            <a-button v-else :loading="actionLoading[selectedJob.id]" @click="handlePause(selectedJob)">
              暂停任务
            </a-button>
          </a-space>

          <a-descriptions bordered size="small" :column="1" :items="selectedJobDescriptionItems" />

          <a-divider title-placement="start">触发器配置</a-divider>
          <pre class="scheduler-json">{{ stringifyJson(selectedJob.trigger_config) }}</pre>

          <a-divider title-placement="start">运行参数</a-divider>
          <a-row :gutter="[12, 12]">
            <a-col :xs="24" :md="12">
              <pre class="scheduler-json">{{ stringifyJson(selectedJob.args) }}</pre>
            </a-col>
            <a-col :xs="24" :md="12">
              <pre class="scheduler-json">{{ stringifyJson(selectedJob.kwargs) }}</pre>
            </a-col>
          </a-row>

          <a-divider title-placement="start">最近 5 次运行</a-divider>
          <a-spin :spinning="recentRunsLoading">
            <a-empty v-if="!selectedJobRecentRuns.length" description="暂无运行记录" />
            <div v-else class="scheduler-run-list">
              <div v-for="run in selectedJobRecentRuns" :key="run.job_id" class="scheduler-run-card">
                <a-flex justify="space-between" gap="middle" wrap="wrap">
                  <div class="scheduler-run-main">
                    <a-typography-text code>{{ run.job_id }}</a-typography-text>
                    <div class="scheduler-run-time">
                      {{ formatDateTime(run.started_at) }} - {{ formatDateTime(run.finished_at) }}
                    </div>
                  </div>
                  <a-space wrap>
                    <a-tag :color="getOutcomeMeta(run.outcome).color">
                      {{ getOutcomeMeta(run.outcome).text }}
                    </a-tag>
                    <a-typography-text type="secondary">
                      {{ formatDuration(run.duration_seconds) }}
                    </a-typography-text>
                  </a-space>
                </a-flex>
                <a-typography-paragraph v-if="run.exception_message" class="scheduler-run-error">
                  {{ run.exception_message }}
                </a-typography-paragraph>
              </div>
            </div>
          </a-spin>
        </template>
      </a-skeleton>
    </a-drawer>
  </div>
</template>

<style scoped>
.scheduler-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  height: 100%;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}

.scheduler-page--maximized {
  position: fixed;
  inset: 108px 18px 16px 258px;
  z-index: 60;
  width: auto;
  height: auto;
  padding: 0;
  background: var(--page-bg);
}

:global(.admin-shell-root--collapsed) .scheduler-page--maximized {
  left: 82px;
}

@media (max-width: 1199px) {
  .scheduler-page--maximized {
    inset: 104px 12px 12px;
  }
}

.scheduler-nowrap {
  white-space: nowrap;
}

.scheduler-status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  min-width: 78px;
  height: 26px;
  padding: 0 10px 0 4px;
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  line-height: 1;
  background: #8c8c8c;
  border-radius: 999px;
}

.scheduler-status-pill--scheduled,
.scheduler-status-pill--running {
  background: #1677ff;
}

.scheduler-status-pill--on {
  flex-direction: row-reverse;
  padding: 0 4px 0 10px;
}

.scheduler-status-pill--paused {
  background: #faad14;
}

.scheduler-status-pill--completed {
  background: #8c8c8c;
}

.scheduler-status-pill__text {
  transform: translateY(-1px);
}

.scheduler-status-pill__knob {
  width: 20px;
  height: 20px;
  margin-right: 6px;
  background: #fff;
  border-radius: 50%;
}

.scheduler-status-pill--on .scheduler-status-pill__knob {
  margin-right: 0;
  margin-left: 6px;
}

.scheduler-drawer-actions {
  margin-bottom: 16px;
}

.scheduler-json {
  min-height: 72px;
  margin: 0;
  padding: 12px;
  color: var(--text-primary);
  background: var(--surface-2);
  border: 1px solid var(--surface-border);
  border-radius: 8px;
}

.scheduler-run-list {
  display: grid;
  gap: 10px;
}

.scheduler-run-card {
  min-width: 0;
  padding: 12px;
  background: var(--surface-2);
  border: 1px solid var(--surface-border);
  border-radius: 10px;
}

.scheduler-run-main {
  min-width: 0;
}

.scheduler-run-time {
  margin-top: 4px;
  color: var(--text-secondary);
  font-size: 12px;
}

.scheduler-run-error {
  margin: 8px 0 0 !important;
  color: #ff4d4f !important;
}

:global(.scheduler-detail-drawer .ant-drawer-content-wrapper) {
  max-width: calc(100vw - 24px);
}
</style>
