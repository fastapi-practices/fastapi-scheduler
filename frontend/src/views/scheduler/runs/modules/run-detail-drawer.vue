<script setup lang="ts">
import {
  formatDateTime,
  formatDuration,
  formatJson,
  getRunOutcomeTagColor,
  translateRunOutcome
} from '@/views/scheduler/jobs/modules/shared';

const visible = defineModel<boolean>('visible', { required: true });

defineProps<{
  rowData: Api.Scheduler.RunRecord | null;
}>();
</script>

<template>
  <ADrawer v-model:open="visible" :title="$t('page.scheduler.runs.detailTitle')" width="640px">
    <ADescriptions v-if="rowData" bordered size="small" :column="1">
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.jobId')">
        {{ rowData.job_id }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.scheduleId')">
        {{ rowData.schedule_id || '-' }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.taskId')">
        {{ rowData.task_id }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.schedulerId')">
        {{ rowData.scheduler_id || '-' }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.outcome')">
        <ATag :color="getRunOutcomeTagColor(rowData.outcome)">
          {{ translateRunOutcome(rowData.outcome) }}
        </ATag>
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.scheduledStart')">
        {{ formatDateTime(rowData.scheduled_start) }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.startedAt')">
        {{ formatDateTime(rowData.started_at) }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.finishedAt')">
        {{ formatDateTime(rowData.finished_at) }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.durationSeconds')">
        {{ formatDuration(rowData.duration_seconds) }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.exceptionType')">
        {{ rowData.exception_type || '-' }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.exceptionMessage')">
        {{ rowData.exception_message || '-' }}
      </ADescriptionsItem>
      <ADescriptionsItem :label="$t('page.scheduler.runs.columns.exceptionTraceback')">
        <pre class="m-0 whitespace-pre-wrap break-all text-12px">{{ formatJson(rowData.exception_traceback) }}</pre>
      </ADescriptionsItem>
    </ADescriptions>
  </ADrawer>
</template>

<style scoped></style>
