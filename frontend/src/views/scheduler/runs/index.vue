<script setup lang="tsx">
import { computed, ref, shallowRef } from 'vue';
import { useRoute } from 'vue-router';
import { Button, Tag } from 'antdv-next';
import { useBoolean } from '@sa/hooks';
import { useElementSize } from '@vueuse/core';
import { fetchDeleteSchedulerRunRecords, fetchGetSchedulerRunRecordList } from '@/service/api';
import { useAntdvPaginatedTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import RunDetailDrawer from './modules/run-detail-drawer.vue';
import RunSearch from './modules/run-search.vue';
import {
  formatDateTime,
  formatDuration,
  getRunOutcomeTagColor,
  translateRunOutcome
} from '../jobs/modules/shared';

defineOptions({
  name: 'SchedulerRuns'
});

const route = useRoute();

const searchParams = ref<Api.Scheduler.RunSearchModel>({
  current: 1,
  size: 10,
  schedule_id: typeof route.query.schedule_id === 'string' ? route.query.schedule_id : null
});

const detail = shallowRef<Api.Scheduler.RunRecord | null>(null);
const { bool: detailVisible, setTrue: openDetailDrawer } = useBoolean();

const tableScrollX = 1714;
const tableBodyReservedHeight = 120;
const tableWrapperRef = ref<HTMLElement>();
const { height: tableWrapperHeight } = useElementSize(tableWrapperRef);
const tableScrollY = computed(() => Math.max(120, Math.floor(tableWrapperHeight.value - tableBodyReservedHeight)));

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useAntdvPaginatedTable({
  api: () => fetchGetSchedulerRunRecordList(getSearchParams()),
  transform: response => {
    const pageData = !response.error ? response.data : null;

    return {
      data: pageData?.items || [],
      pageNum: pageData?.page || 1,
      pageSize: pageData?.size || 10,
      total: pageData?.total || 0
    };
  },
  onPaginationParamsChange: params => {
    searchParams.value.current = params.current || 1;
    searchParams.value.size = params.pageSize || 10;
  },
  immediate: false,
  columns: () => [
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      fixed: 'start',
      render: (_value: unknown, _record: Api.Scheduler.RunRecord, index: number) => index + 1
    },
    {
      key: 'job_id',
      dataIndex: 'job_id',
      title: $t('page.scheduler.runs.columns.jobId'),
      align: 'center',
      width: 240,
      fixed: 'start'
    },
    {
      key: 'schedule_id',
      dataIndex: 'schedule_id',
      title: $t('page.scheduler.runs.columns.scheduleId'),
      align: 'center',
      width: 220
    },
    {
      key: 'task_id',
      dataIndex: 'task_id',
      title: $t('page.scheduler.runs.columns.taskId'),
      align: 'center',
      width: 240
    },
    {
      key: 'outcome',
      dataIndex: 'outcome',
      title: $t('page.scheduler.runs.columns.outcome'),
      align: 'center',
      width: 120,
      render: (_value: unknown, record: Api.Scheduler.RunRecord) => (
        <Tag color={getRunOutcomeTagColor(record.outcome)}>{translateRunOutcome(record.outcome)}</Tag>
      )
    },
    {
      key: 'started_at',
      dataIndex: 'started_at',
      title: $t('page.scheduler.runs.columns.startedAt'),
      align: 'center',
      width: 180,
      render: (_value: unknown, record: Api.Scheduler.RunRecord) => formatDateTime(record.started_at)
    },
    {
      key: 'finished_at',
      dataIndex: 'finished_at',
      title: $t('page.scheduler.runs.columns.finishedAt'),
      align: 'center',
      width: 180,
      render: (_value: unknown, record: Api.Scheduler.RunRecord) => formatDateTime(record.finished_at)
    },
    {
      key: 'duration_seconds',
      dataIndex: 'duration_seconds',
      title: $t('page.scheduler.runs.columns.durationSeconds'),
      align: 'center',
      width: 130,
      render: (_value: unknown, record: Api.Scheduler.RunRecord) => formatDuration(record.duration_seconds)
    },
    {
      key: 'exception_message',
      dataIndex: 'exception_message',
      title: $t('page.scheduler.runs.columns.exceptionMessage'),
      align: 'center',
      width: 240,
      render: (_value: unknown, record: Api.Scheduler.RunRecord) => (
        <span class={record.exception_message ? 'text-error' : ''}>{record.exception_message || '-'}</span>
      )
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 100,
      fixed: 'end',
      render: (_value: unknown, record: Api.Scheduler.RunRecord) => (
        <Button type="primary" ghost size="small" onClick={() => openDetail(record)}>
          {$t('page.scheduler.runs.detail')}
        </Button>
      )
    }
  ]
});

const { checkedRowKeys, onBatchDeleted } = useTableOperate(data, 'job_id', getData);

const { bool: batchDeleting, setBool: setBatchDeleting } = useBoolean();

const rowSelection = computed(() => ({
  fixed: true,
  selectedRowKeys: checkedRowKeys.value,
  onChange: (keys: (string | number)[]) => {
    checkedRowKeys.value = keys as string[];
  }
}));

function getSearchParams(): Api.Scheduler.RunSearchParams {
  return {
    schedule_id: searchParams.value.schedule_id || undefined,
    page: searchParams.value.current,
    size: searchParams.value.size
  };
}

async function handleBatchDelete() {
  setBatchDeleting(true);

  const { error } = await fetchDeleteSchedulerRunRecords([...checkedRowKeys.value]);

  if (!error) {
    await onBatchDeleted();
  } else {
    checkedRowKeys.value = [];
    await getData();
  }

  setBatchDeleting(false);
}

function openDetail(record: Api.Scheduler.RunRecord) {
  detail.value = record;
  openDetailDrawer();
}

getData();
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <RunSearch v-model:model="searchParams" @search="getDataByPage" />

    <ACard
      :title="$t('page.scheduler.runs.title')"
      variant="borderless"
      :body-style="{ display: 'flex', minHeight: 0, flex: 1, flexDirection: 'column', overflow: 'hidden' }"
      class="flex-col-stretch sm:flex-1-hidden card-wrapper"
    >
      <template #extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          @refresh="getData"
        >
          <template #default>
            <APopconfirm :title="$t('common.confirmDelete')" @confirm="handleBatchDelete">
              <AButton size="small" ghost danger :disabled="checkedRowKeys.length === 0" :loading="batchDeleting">
                <template #icon>
                  <icon-ic-round-delete class="text-icon" />
                </template>
                {{ $t('common.batchDelete') }}
              </AButton>
            </APopconfirm>
          </template>
        </TableHeaderOperation>
      </template>

      <div ref="tableWrapperRef" class="min-h-0 flex-1 overflow-hidden">
        <ATable
          row-key="job_id"
          :row-selection="rowSelection"
          :columns="columns"
          :data-source="data"
          :loading="loading"
          :scroll="{ x: tableScrollX, y: tableScrollY }"
          :pagination="mobilePagination"
          size="small"
        />
      </div>

      <RunDetailDrawer v-model:visible="detailVisible" :row-data="detail" />
    </ACard>
  </div>
</template>
