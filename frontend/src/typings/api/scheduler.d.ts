declare namespace Api {
  /**
   * namespace Scheduler
   *
   * backend api module: "scheduler"
   */
  namespace Scheduler {
    type JobStatus = 'scheduled' | 'running' | 'paused' | 'completed' | (string & {});

    type RunOutcome = 'success' | 'error' | 'missed_start_deadline' | 'cancelled' | (string & {});

    /** scheduler status */
    interface Status {
      enabled: boolean;
      started: boolean;
      identity: string;
      timezone: string;
      schedule_count: number;
      running_job_count: number;
    }

    /** scheduler job */
    interface Job {
      id: string;
      task_id: string;
      trigger: string;
      trigger_type: string;
      trigger_config: Record<string, any>;
      args: any[];
      kwargs: Record<string, any>;
      paused: boolean;
      status: JobStatus;
      coalesce: string;
      misfire_grace_time?: number | null;
      max_jitter?: number | null;
      job_executor: string;
      job_result_expiration_time: number;
      metadata: Record<string, any>;
      next_fire_time?: string | null;
      last_fire_time?: string | null;
      acquired_by?: string | null;
      acquired_until?: string | null;
      running_job_count: number;
    }

    /** scheduler job list */
    type JobList = Job[];

    /** run scheduler job result */
    interface RunJobResult {
      schedule_id: string;
      job_id: string;
    }

    /** scheduler run record */
    interface RunRecord {
      job_id: string;
      schedule_id?: string | null;
      task_id: string;
      scheduler_id?: string | null;
      scheduled_start?: string | null;
      started_at?: string | null;
      finished_at?: string | null;
      duration_seconds?: number | null;
      outcome: RunOutcome;
      exception_type?: string | null;
      exception_message?: string | null;
      exception_traceback?: string[] | null;
    }

    /** scheduler run record list */
    interface RunRecordPage {
      items: RunRecord[];
      total: number;
      page: number;
      size: number;
      total_pages: number;
      links: {
        first: string;
        last: string;
        self: string;
        next?: string | null;
        prev?: string | null;
      };
    }

    /** scheduler run record search params */
    type RunSearchParams = CommonType.RecordNullable<Pick<RunRecord, 'schedule_id'> & { page: number; size: number }>;

    /** scheduler run record search model */
    type RunSearchModel = Pick<Common.PaginatingCommonParams, 'current' | 'size'> &
      CommonType.RecordNullable<Pick<RunRecord, 'schedule_id'>>;
  }
}
