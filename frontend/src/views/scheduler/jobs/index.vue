<script setup lang="tsx">
import { computed, reactive, shallowRef } from "vue";
import { useRouter } from "vue-router";
import { Button, Popconfirm, Tag } from "antdv-next";
import { useBoolean } from "@sa/hooks";
import {
  fetchCreateSchedulerJob,
  fetchDeleteSchedulerJob,
  fetchDeleteSchedulerJobs,
  fetchGetSchedulerJob,
  fetchGetSchedulerJobList,
  fetchPauseSchedulerJob,
  fetchResumeSchedulerJob,
  fetchRunSchedulerJob,
} from "@/service/api";
import { useAntdvPaginatedTable, useTableOperate } from "@/hooks/common/table";
import { $t } from "@/locales";
import JobDetailDrawer from "./modules/job-detail-drawer.vue";
import JobOperateDrawer from "./modules/job-operate-drawer.vue";
import {
  formatBoolean,
  formatDateTime,
  getJobStatusTagColor,
  translateJobStatus,
} from "./modules/shared";

defineOptions({
  name: "SchedulerJobs",
});

const router = useRouter();

const detail = shallowRef<Api.Scheduler.Job | null>(null);
const operationLoading = reactive<Record<string, boolean>>({});
const paginationParams = reactive({
  current: 1,
  size: 10,
});

const { bool: detailVisible, setTrue: openDetailDrawer } = useBoolean();
const { bool: detailLoading, setBool: setDetailLoading } = useBoolean();
const {
  bool: operateVisible,
  setTrue: openCreateDrawer,
  setFalse: closeCreateDrawer,
} = useBoolean();
const { bool: createLoading, setBool: setCreateLoading } = useBoolean();

const tableScrollX = 1790;

const { columns, columnChecks, data, getData, loading, mobilePagination } =
  useAntdvPaginatedTable({
    api: () => fetchGetSchedulerJobList(),
    transform: (response) => {
      const records = !response.error ? response.data : [];

      return {
        data: records,
        pageNum: paginationParams.current,
        pageSize: paginationParams.size,
        total: records.length,
      };
    },
    onPaginationParamsChange: (params) => {
      paginationParams.current = params.current || 1;
      paginationParams.size = params.pageSize || 10;
    },
    immediate: false,
    columns: () => [
      {
        key: "index",
        title: $t("common.index"),
        align: "center",
        width: 64,
        fixed: "start",
        render: (_value: unknown, _record: Api.Scheduler.Job, index: number) =>
          index + 1,
      },
      {
        key: "id",
        dataIndex: "id",
        title: $t("page.scheduler.jobs.columns.id"),
        align: "center",
        width: 220,
        fixed: "start",
      },
      {
        key: "task_id",
        dataIndex: "task_id",
        title: $t("page.scheduler.jobs.columns.taskId"),
        align: "center",
        width: 240,
      },
      {
        key: "status",
        dataIndex: "status",
        title: $t("page.scheduler.jobs.columns.status"),
        align: "center",
        width: 120,
        render: (_value: unknown, record: Api.Scheduler.Job) => (
          <Tag color={getJobStatusTagColor(record.status)}>
            {translateJobStatus(record.status)}
          </Tag>
        ),
      },
      {
        key: "paused",
        dataIndex: "paused",
        title: $t("page.scheduler.jobs.columns.paused"),
        align: "center",
        width: 100,
        render: (_value: unknown, record: Api.Scheduler.Job) => (
          <Tag color={record.paused ? "warning" : "success"}>
            {formatBoolean(record.paused)}
          </Tag>
        ),
      },
      {
        key: "trigger_type",
        dataIndex: "trigger_type",
        title: $t("page.scheduler.jobs.columns.triggerType"),
        align: "center",
        width: 140,
      },
      {
        key: "next_fire_time",
        dataIndex: "next_fire_time",
        title: $t("page.scheduler.jobs.columns.nextFireTime"),
        align: "center",
        width: 180,
        render: (_value: unknown, record: Api.Scheduler.Job) =>
          formatDateTime(record.next_fire_time),
      },
      {
        key: "last_fire_time",
        dataIndex: "last_fire_time",
        title: $t("page.scheduler.jobs.columns.lastFireTime"),
        align: "center",
        width: 180,
        render: (_value: unknown, record: Api.Scheduler.Job) =>
          formatDateTime(record.last_fire_time),
      },
      {
        key: "running_job_count",
        dataIndex: "running_job_count",
        title: $t("page.scheduler.jobs.columns.runningJobCount"),
        align: "center",
        width: 130,
      },
      {
        key: "operate",
        title: $t("common.operate"),
        align: "center",
        width: 360,
        fixed: "end",
        render: (_value: unknown, record: Api.Scheduler.Job) => (
          <div class="flex-center justify-end gap-6px">
            <Button
              type="primary"
              ghost
              size="small"
              onClick={() => openDetail(record.id)}
            >
              {$t("page.scheduler.jobs.detail")}
            </Button>
            <Popconfirm
              title={
                record.paused
                  ? $t("page.scheduler.jobs.confirmResume")
                  : $t("page.scheduler.jobs.confirmPause")
              }
              onConfirm={() => handleTogglePause(record)}
            >
              <Button
                size="small"
                loading={getOperationLoading(
                  record.paused ? "resume" : "pause",
                  record.id,
                )}
              >
                {record.paused
                  ? $t("page.scheduler.jobs.resume")
                  : $t("page.scheduler.jobs.pause")}
              </Button>
            </Popconfirm>
            <Popconfirm
              title={$t("page.scheduler.jobs.confirmRun")}
              onConfirm={() => handleRun(record)}
            >
              <Button
                size="small"
                loading={getOperationLoading("run", record.id)}
              >
                {$t("page.scheduler.jobs.run")}
              </Button>
            </Popconfirm>
            <Button size="small" onClick={() => openRuns(record)}>
              {$t("page.scheduler.jobs.runs")}
            </Button>
            <Popconfirm
              title={$t("common.confirmDelete")}
              onConfirm={() => handleDelete(record)}
            >
              <Button
                danger
                ghost
                size="small"
                loading={getOperationLoading("delete", record.id)}
              >
                {$t("common.delete")}
              </Button>
            </Popconfirm>
          </div>
        ),
      },
    ],
  });

function getOperationKey(action: string, schedule_id: string) {
  return `${action}:${schedule_id}`;
}

function setOperationLoading(
  action: string,
  schedule_id: string,
  value: boolean,
) {
  operationLoading[getOperationKey(action, schedule_id)] = value;
}

function getOperationLoading(action: string, schedule_id: string) {
  return Boolean(operationLoading[getOperationKey(action, schedule_id)]);
}

const { checkedRowKeys, onBatchDeleted } = useTableOperate(data, "id", getData);

const { bool: batchDeleting, setBool: setBatchDeleting } = useBoolean();

const rowSelection = computed(() => ({
  fixed: true,
  selectedRowKeys: checkedRowKeys.value,
  onChange: (keys: (string | number)[]) => {
    checkedRowKeys.value = keys as string[];
  },
}));

async function handleBatchDelete() {
  setBatchDeleting(true);

  const { error } = await fetchDeleteSchedulerJobs([...checkedRowKeys.value]);

  if (!error) {
    await onBatchDeleted();
  } else {
    checkedRowKeys.value = [];
    await getData();
  }

  setBatchDeleting(false);
}

async function handleCreateJob(payload: Api.Scheduler.CreateJobParam) {
  setCreateLoading(true);

  const { error } = await fetchCreateSchedulerJob(payload);

  if (!error) {
    window.$message?.success($t("common.addSuccess"));
    closeCreateDrawer();
    await getData();
  }

  setCreateLoading(false);
}

async function openDetail(schedule_id: string) {
  openDetailDrawer();
  setDetailLoading(true);

  const { data: job, error } = await fetchGetSchedulerJob(schedule_id);

  if (!error) {
    detail.value = job;
  }

  setDetailLoading(false);
}

async function handleTogglePause(record: Api.Scheduler.Job) {
  const action = record.paused ? "resume" : "pause";

  setOperationLoading(action, record.id, true);

  const { error } = record.paused
    ? await fetchResumeSchedulerJob(record.id)
    : await fetchPauseSchedulerJob(record.id);

  if (!error) {
    window.$message?.success(
      record.paused
        ? $t("page.scheduler.jobs.resumeSuccess")
        : $t("page.scheduler.jobs.pauseSuccess"),
    );
    await getData();
  }

  setOperationLoading(action, record.id, false);
}

async function handleRun(record: Api.Scheduler.Job) {
  const action = "run";

  setOperationLoading(action, record.id, true);

  const { data: runResult, error } = await fetchRunSchedulerJob(record.id);

  if (!error) {
    window.$message?.success(
      $t("page.scheduler.jobs.runSuccess", { jobId: runResult.job_id }),
    );
    await getData();
  }

  setOperationLoading(action, record.id, false);
}

async function handleDelete(record: Api.Scheduler.Job) {
  const action = "delete";

  setOperationLoading(action, record.id, true);

  const { error } = await fetchDeleteSchedulerJob(record.id);

  if (!error) {
    window.$message?.success($t("common.deleteSuccess"));
    await getData();
  }

  setOperationLoading(action, record.id, false);
}

function openRuns(record: Api.Scheduler.Job) {
  router.push({
    name: "scheduler_runs",
    query: {
      schedule_id: record.id,
    },
  });
}

getData();
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <ACard
      :title="$t('page.scheduler.jobs.title')"
      variant="borderless"
      :body-style="{ flex: 1, overflow: 'hidden' }"
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
            <AButton size="small" ghost type="primary" @click="openCreateDrawer">
              <template #icon>
                <icon-ic-round-plus class="text-icon" />
              </template>
              {{ $t('common.add') }}
            </AButton>
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

      <ATable
        row-key="id"
        :row-selection="rowSelection"
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :scroll="{ x: tableScrollX }"
        :pagination="mobilePagination"
        size="small"
        class="h-full"
      />

      <JobDetailDrawer v-model:visible="detailVisible" :loading="detailLoading" :row-data="detail" />

      <JobOperateDrawer v-model:visible="operateVisible" :loading="createLoading" @submitted="handleCreateJob" />
    </ACard>
  </div>
</template>

<style scoped></style>
