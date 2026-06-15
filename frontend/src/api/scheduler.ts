import { request } from './auth'

export interface SchedulerStatus {
  enabled: boolean
  started: boolean
  identity: string
  timezone: string
  schedule_count: number
  running_job_count: number
}

export interface SchedulerJob {
  id: string
  task_id: string
  trigger: string
  trigger_type: string
  trigger_config: Record<string, unknown>
  args: unknown[]
  kwargs: Record<string, unknown>
  paused: boolean
  status: 'scheduled' | 'running' | 'paused' | 'completed' | string
  coalesce: string
  misfire_grace_time?: number | null
  max_jitter?: number | null
  job_executor: string
  job_result_expiration_time: number
  metadata: Record<string, unknown>
  next_fire_time?: string | null
  last_fire_time?: string | null
  acquired_by?: string | null
  acquired_until?: string | null
  running_job_count: number
}

export interface SchedulerRun {
  job_id: string
  schedule_id?: string | null
  task_id: string
  scheduler_id?: string | null
  scheduled_start?: string | null
  started_at?: string | null
  finished_at?: string | null
  duration_seconds?: number | null
  outcome: string
  exception_type?: string | null
  exception_message?: string | null
  exception_traceback?: string[] | null
}

export interface RunSchedulerJobResult {
  schedule_id: string
  job_id: string
}

export const schedulerApi = {
  getStatus() {
    return request<SchedulerStatus>('/scheduler/status')
  },
  getJobs() {
    return request<SchedulerJob[]>('/scheduler/jobs')
  },
  getJob(scheduleId: string) {
    return request<SchedulerJob>(`/scheduler/jobs/${encodeURIComponent(scheduleId)}`)
  },
  pauseJob(scheduleId: string) {
    return request<SchedulerJob>(`/scheduler/jobs/${encodeURIComponent(scheduleId)}/pause`, {
      method: 'PUT',
    })
  },
  resumeJob(scheduleId: string) {
    return request<SchedulerJob>(`/scheduler/jobs/${encodeURIComponent(scheduleId)}/resume`, {
      method: 'PUT',
    })
  },
  runJob(scheduleId: string) {
    return request<RunSchedulerJobResult>(`/scheduler/jobs/${encodeURIComponent(scheduleId)}/run`, {
      method: 'POST',
    })
  },
  deleteJob(scheduleId: string) {
    return request<null>(`/scheduler/jobs/${encodeURIComponent(scheduleId)}`, {
      method: 'DELETE',
    })
  },
  getRuns(params: { scheduleId?: string; limit?: number } = {}) {
    const search = new URLSearchParams()
    if (params.scheduleId) search.set('schedule_id', params.scheduleId)
    if (params.limit) search.set('limit', String(params.limit))
    const query = search.toString()
    return request<SchedulerRun[]>(`/scheduler/runs${query ? `?${query}` : ''}`)
  },
}
