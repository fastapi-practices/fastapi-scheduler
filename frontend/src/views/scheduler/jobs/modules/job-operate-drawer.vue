<script setup lang="ts">
import { computed, nextTick, reactive, watch } from 'vue';
import { Input } from 'antdv-next';
import { useAntdvForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'JobOperateDrawer'
});

const visible = defineModel<boolean>('visible', { required: true });

defineProps<{
  loading: boolean;
}>();

const emit = defineEmits<{
  (e: 'submitted', data: Api.Scheduler.CreateJobParam): void;
}>();

interface FormModel {
  id: string | null;
  task_id: string;
  trigger_type: Api.Scheduler.JobTriggerType;
  trigger_config: string;
  args: string;
  kwargs: string;
  paused: boolean;
  coalesce: Api.Scheduler.JobCoalesce;
  job_executor: string | null;
  misfire_grace_time: number | null;
  max_jitter: number | null;
  job_result_expiration_time: number;
  metadata: string;
  conflict_policy: Api.Scheduler.JobConflictPolicy;
}

const { formRef, validate, restoreValidation } = useAntdvForm();
const ATextarea = Input.TextArea;

const defaultTriggerConfig: Record<Exclude<Api.Scheduler.JobTriggerType, 'date'>, string> = {
  interval: '{\n  "seconds": 60\n}',
  cron: '{\n  "minute": "*/5"\n}'
};

const model = reactive<FormModel>(createDefaultModel());

const triggerTypeOptions = computed<CommonType.Option<Api.Scheduler.JobTriggerType>[]>(() => [
  { label: 'interval', value: 'interval' },
  { label: 'cron', value: 'cron' },
  { label: 'date', value: 'date' }
]);

const coalesceOptions = computed<CommonType.Option<Api.Scheduler.JobCoalesce>[]>(() => [
  { label: 'latest', value: 'latest' },
  { label: 'earliest', value: 'earliest' },
  { label: 'all', value: 'all' }
]);

const conflictPolicyOptions = computed<CommonType.Option<Api.Scheduler.JobConflictPolicy>[]>(() => [
  { label: 'exception', value: 'exception' },
  { label: 'replace', value: 'replace' },
  { label: 'do_nothing', value: 'do_nothing' }
]);

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => ({
  id: [],
  task_id: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  trigger_type: [{ required: true, message: $t('form.required'), trigger: 'change' }],
  trigger_config: [
    { required: true, message: $t('form.required'), trigger: 'blur' },
    { validator: createJsonValidator('object'), trigger: 'blur' }
  ],
  args: [{ validator: createJsonValidator('array'), trigger: 'blur' }],
  kwargs: [{ validator: createJsonValidator('object'), trigger: 'blur' }],
  paused: [],
  coalesce: [{ required: true, message: $t('form.required'), trigger: 'change' }],
  job_executor: [],
  misfire_grace_time: [],
  max_jitter: [],
  job_result_expiration_time: [{ required: true, message: $t('form.required'), trigger: 'blur' }],
  metadata: [{ validator: createJsonValidator('object'), trigger: 'blur' }],
  conflict_policy: [{ required: true, message: $t('form.required'), trigger: 'change' }]
}));

watch(
  () => visible.value,
  async open => {
    if (!open) {
      resetModel();
      return;
    }
    await nextTick();
    restoreValidation();
  }
);

function createDefaultModel(): FormModel {
  return {
    id: null,
    task_id: '',
    trigger_type: 'interval',
    trigger_config: getDefaultTriggerConfig('interval'),
    args: '[]',
    kwargs: '{}',
    paused: false,
    coalesce: 'latest',
    job_executor: null,
    misfire_grace_time: null,
    max_jitter: null,
    job_result_expiration_time: 0,
    metadata: '{}',
    conflict_policy: 'exception'
  };
}

function resetModel() {
  Object.assign(model, createDefaultModel());
}

function getDefaultTriggerConfig(triggerType: Api.Scheduler.JobTriggerType) {
  if (triggerType === 'date') {
    return `{\n  "run_time": "${new Date(Date.now() + 60_000).toISOString()}"\n}`;
  }
  return defaultTriggerConfig[triggerType];
}

function createJsonValidator(expectedType: 'array' | 'object') {
  return async (_rule: App.Global.FormRule, value: string) => {
    const parsed = parseJsonValue(value, expectedType === 'array' ? [] : {});
    const invalidArray = expectedType === 'array' && !Array.isArray(parsed);
    const invalidObject =
      expectedType === 'object' && (Array.isArray(parsed) || parsed === null || typeof parsed !== 'object');
    if (invalidArray || invalidObject) {
      return Promise.reject($t('page.scheduler.jobs.form.jsonInvalid'));
    }
    return Promise.resolve();
  };
}

function parseJsonValue<T>(value: string, fallback: T): T {
  const text = value.trim();
  if (!text) {
    return fallback;
  }
  return JSON.parse(text) as T;
}

function handleTriggerTypeChange(value: Api.Scheduler.JobTriggerType) {
  model.trigger_config = getDefaultTriggerConfig(value);
}

async function handleSubmit() {
  await validate();
  emit('submitted', {
    id: model.id || null,
    task_id: model.task_id,
    trigger_type: model.trigger_type,
    trigger_config: parseJsonValue<Record<string, any>>(model.trigger_config, {}),
    args: parseJsonValue<any[]>(model.args, []),
    kwargs: parseJsonValue<Record<string, any>>(model.kwargs, {}),
    paused: model.paused,
    coalesce: model.coalesce,
    job_executor: model.job_executor || null,
    misfire_grace_time: model.misfire_grace_time,
    max_jitter: model.max_jitter,
    job_result_expiration_time: model.job_result_expiration_time,
    metadata: parseJsonValue<Record<string, any>>(model.metadata, {}),
    conflict_policy: model.conflict_policy
  });
}
</script>

<template>
  <ADrawer v-model:open="visible" :title="$t('page.scheduler.jobs.addTitle')" width="720px">
    <AForm ref="formRef" :model="model" :rules="rules" :colon="false" layout="vertical">
      <AFormItem name="id" :label="$t('page.scheduler.jobs.columns.id')">
        <AInput v-model:value="model.id" allow-clear :placeholder="$t('page.scheduler.jobs.form.idPlaceholder')" />
      </AFormItem>
      <AFormItem name="task_id" :label="$t('page.scheduler.jobs.columns.taskId')">
        <AInput
          v-model:value="model.task_id"
          allow-clear
          :placeholder="$t('page.scheduler.jobs.form.taskIdPlaceholder')"
        />
      </AFormItem>
      <AFormItem name="trigger_type" :label="$t('page.scheduler.jobs.columns.triggerType')">
        <ASelect v-model:value="model.trigger_type" :options="triggerTypeOptions" @change="handleTriggerTypeChange" />
      </AFormItem>
      <AFormItem name="trigger_config" :label="$t('page.scheduler.jobs.columns.triggerConfig')">
        <ATextarea v-model:value="model.trigger_config" :auto-size="{ minRows: 4, maxRows: 8 }" />
      </AFormItem>
      <div class="grid gap-16px md:grid-cols-2">
        <AFormItem name="coalesce" :label="$t('page.scheduler.jobs.columns.coalesce')">
          <ASelect v-model:value="model.coalesce" :options="coalesceOptions" />
        </AFormItem>
        <AFormItem name="conflict_policy" :label="$t('page.scheduler.jobs.form.conflictPolicy')">
          <ASelect v-model:value="model.conflict_policy" :options="conflictPolicyOptions" />
        </AFormItem>
        <AFormItem name="misfire_grace_time" :label="$t('page.scheduler.jobs.columns.misfireGraceTime')">
          <AInputNumber v-model:value="model.misfire_grace_time" class="w-full" :min="0" />
        </AFormItem>
        <AFormItem name="max_jitter" :label="$t('page.scheduler.jobs.columns.maxJitter')">
          <AInputNumber v-model:value="model.max_jitter" class="w-full" :min="0" />
        </AFormItem>
        <AFormItem name="job_result_expiration_time" :label="$t('page.scheduler.jobs.columns.jobResultExpirationTime')">
          <AInputNumber v-model:value="model.job_result_expiration_time" class="w-full" :min="0" />
        </AFormItem>
        <AFormItem name="job_executor" :label="$t('page.scheduler.jobs.columns.jobExecutor')">
          <AInput v-model:value="model.job_executor" allow-clear />
        </AFormItem>
      </div>
      <AFormItem name="args" :label="$t('page.scheduler.jobs.columns.args')">
        <ATextarea v-model:value="model.args" :auto-size="{ minRows: 2, maxRows: 6 }" />
      </AFormItem>
      <AFormItem name="kwargs" :label="$t('page.scheduler.jobs.columns.kwargs')">
        <ATextarea v-model:value="model.kwargs" :auto-size="{ minRows: 2, maxRows: 6 }" />
      </AFormItem>
      <AFormItem name="metadata" :label="$t('page.scheduler.jobs.columns.metadata')">
        <ATextarea v-model:value="model.metadata" :auto-size="{ minRows: 2, maxRows: 6 }" />
      </AFormItem>
      <AFormItem name="paused" :label="$t('page.scheduler.jobs.columns.paused')">
        <ASwitch v-model:checked="model.paused" />
      </AFormItem>
    </AForm>
    <template #footer>
      <ASpace class="w-full justify-end">
        <AButton @click="visible = false">{{ $t('common.cancel') }}</AButton>
        <AButton type="primary" :loading="loading" @click="handleSubmit">{{ $t('common.confirm') }}</AButton>
      </ASpace>
    </template>
  </ADrawer>
</template>

<style scoped></style>
