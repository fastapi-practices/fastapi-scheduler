import { request } from '../request';

/** get scheduler status */
export function fetchGetSchedulerStatus() {
  return request<Api.Scheduler.Status>({ url: '/scheduler/status', method: 'get' });
}

/** get scheduler job list */
export function fetchGetSchedulerJobList() {
  return request<Api.Scheduler.JobList>({ url: '/scheduler/jobs', method: 'get' });
}

/** get scheduler job detail */
export function fetchGetSchedulerJob(schedule_id: string) {
  return request<Api.Scheduler.Job>({ url: `/scheduler/jobs/${schedule_id}`, method: 'get' });
}

/** create scheduler job */
export function fetchCreateSchedulerJob(data: Api.Scheduler.CreateJobParam) {
  return request<Api.Scheduler.Job>({
    url: '/scheduler/jobs',
    method: 'post',
    data
  });
}

/** pause scheduler job */
export function fetchPauseSchedulerJob(schedule_id: string) {
  return request<Api.Scheduler.Job>({
    url: `/scheduler/jobs/${schedule_id}/pause`,
    method: 'put'
  });
}

/** resume scheduler job */
export function fetchResumeSchedulerJob(schedule_id: string) {
  return request<Api.Scheduler.Job>({
    url: `/scheduler/jobs/${schedule_id}/resume`,
    method: 'put'
  });
}

/** run scheduler job immediately */
export function fetchRunSchedulerJob(schedule_id: string) {
  return request<Api.Scheduler.RunJobResult>({
    url: `/scheduler/jobs/${schedule_id}/run`,
    method: 'post'
  });
}

/** delete scheduler job */
export function fetchDeleteSchedulerJob(schedule_id: string) {
  return request<unknown>({
    url: `/scheduler/jobs/${schedule_id}`,
    method: 'delete'
  });
}

/** batch delete scheduler jobs */
export function fetchDeleteSchedulerJobs(ids: string[]) {
  return request<unknown>({
    url: '/scheduler/jobs',
    method: 'delete',
    data: { ids }
  });
}

/** get scheduler run record list */
export function fetchGetSchedulerRunRecordList(params?: Api.Scheduler.RunSearchParams) {
  return request<Api.Scheduler.RunRecordPage>({
    url: '/scheduler/runs',
    method: 'get',
    params
  });
}

/** batch delete scheduler run records */
export function fetchDeleteSchedulerRunRecords(job_ids: string[]) {
  return request<unknown>({
    url: '/scheduler/runs',
    method: 'delete',
    data: { job_ids }
  });
}
