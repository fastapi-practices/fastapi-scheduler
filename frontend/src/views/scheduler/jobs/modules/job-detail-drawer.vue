<script setup lang="ts">
import { formatBoolean, formatDateTime, formatJson, formatSeconds, getJobStatusTagColor, translateJobStatus } from './shared';

const visible = defineModel<boolean>('visible', { required: true });

defineProps<{
  loading: boolean;
  rowData: Api.Scheduler.Job | null;
}>();
</script>

<template>
  <ADrawer v-model:open="visible" :title="$t('page.scheduler.jobs.detailTitle')" width="640px">
    <ASpin :spinning="loading">
      <ADescriptions v-if="rowData" bordered size="small" :column="1">
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.id')">
          {{ rowData.id }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.taskId')">
          {{ rowData.task_id }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.status')">
          <ATag :color="getJobStatusTagColor(rowData.status)">
            {{ translateJobStatus(rowData.status) }}
          </ATag>
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.paused')">
          {{ formatBoolean(rowData.paused) }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.triggerType')">
          {{ rowData.trigger_type }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.trigger')">
          {{ rowData.trigger }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.nextFireTime')">
          {{ formatDateTime(rowData.next_fire_time) }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.lastFireTime')">
          {{ formatDateTime(rowData.last_fire_time) }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.acquiredBy')">
          {{ rowData.acquired_by || '-' }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.acquiredUntil')">
          {{ formatDateTime(rowData.acquired_until) }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.runningJobCount')">
          {{ rowData.running_job_count }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.coalesce')">
          {{ rowData.coalesce }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.misfireGraceTime')">
          {{ formatSeconds(rowData.misfire_grace_time) }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.maxJitter')">
          {{ formatSeconds(rowData.max_jitter) }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.jobExecutor')">
          {{ rowData.job_executor }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.jobResultExpirationTime')">
          {{ formatSeconds(rowData.job_result_expiration_time) }}
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.triggerConfig')">
          <pre class="m-0 whitespace-pre-wrap break-all text-12px">{{ formatJson(rowData.trigger_config) }}</pre>
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.args')">
          <pre class="m-0 whitespace-pre-wrap break-all text-12px">{{ formatJson(rowData.args) }}</pre>
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.kwargs')">
          <pre class="m-0 whitespace-pre-wrap break-all text-12px">{{ formatJson(rowData.kwargs) }}</pre>
        </ADescriptionsItem>
        <ADescriptionsItem :label="$t('page.scheduler.jobs.columns.metadata')">
          <pre class="m-0 whitespace-pre-wrap break-all text-12px">{{ formatJson(rowData.metadata) }}</pre>
        </ADescriptionsItem>
      </ADescriptions>
    </ASpin>
  </ADrawer>
</template>

<style scoped></style>
