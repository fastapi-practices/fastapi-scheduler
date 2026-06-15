<script setup lang="ts">
import { computed, ref } from 'vue'
import { DownOutlined, SearchOutlined, UpOutlined } from '@antdv-next/icons'

import type { AdminSearchField } from '../types'

defineOptions({
  inheritAttrs: false,
})

const props = withDefaults(
  defineProps<{
    model: Record<string, any>
    fields: AdminSearchField[]
    loading?: boolean
    collapsedCount?: number
    colProps?: Record<string, any>
    actionColProps?: Record<string, any>
    submitText?: string
    resetText?: string
  }>(),
  {
    loading: false,
    collapsedCount: 2,
    colProps: () => ({ xs: 24, md: 12, xl: 8 }),
    actionColProps: () => ({ xs: 24, md: 12, xl: 8 }),
    submitText: '搜索',
    resetText: '重置',
  },
)

const emit = defineEmits<{
  'update:model': [value: Record<string, any>]
  search: [value: Record<string, any>]
  reset: [value: Record<string, any>]
}>()

const expanded = ref(true)
const visibleFields = computed(() => props.fields.filter((field) => !field.hidden))
const collapsible = computed(() => visibleFields.value.length > props.collapsedCount)
const renderedFields = computed(() =>
  collapsible.value && !expanded.value ? visibleFields.value.slice(0, props.collapsedCount) : visibleFields.value,
)

const cloneModel = (value: Record<string, any>) => ({ ...value })

const setFieldValue = (field: AdminSearchField, value: any) => {
  emit('update:model', {
    ...props.model,
    [field.key]: value,
  })
}

const fieldModel = (field: AdminSearchField) =>
  computed({
    get: () => props.model[field.key],
    set: (value) => setFieldValue(field, value),
  })

const getFieldColProps = (field: AdminSearchField) => field.colProps || props.colProps

const getRangePlaceholder = (field: AdminSearchField) => {
  if (Array.isArray(field.placeholder)) return field.placeholder
  if (typeof field.placeholder === 'string') return [field.placeholder, field.placeholder] as [string, string]
  return undefined
}

const getTextPlaceholder = (field: AdminSearchField) =>
  typeof field.placeholder === 'string' ? field.placeholder : undefined

const getDefaultValue = (field: AdminSearchField) => {
  if (field.defaultValue !== undefined) return field.defaultValue
  return field.type === 'dateRange' ? [] : undefined
}

const submit = () => {
  emit('search', cloneModel(props.model))
}

const reset = () => {
  const next = props.fields.reduce<Record<string, any>>((data, field) => {
    data[field.key] = getDefaultValue(field)
    return data
  }, cloneModel(props.model))
  emit('update:model', next)
  emit('reset', next)
}
</script>

<template>
  <a-card v-bind="$attrs" size="small" class="admin-search-form">
    <a-form
      :model="model"
      layout="horizontal"
      size="middle"
      :colon="true"
      :label-col="{ flex: '78px' }"
      :wrapper-col="{ flex: '1 1 0' }"
      @finish="submit"
    >
      <a-row :gutter="[24, 16]" align="bottom">
        <a-col v-for="field in renderedFields" :key="field.key" v-bind="getFieldColProps(field)">
          <a-form-item :label="field.label" :name="field.key" v-bind="field.formItemProps">
            <slot
              v-if="field.type === 'custom'"
              :name="`field-${field.key}`"
              :field="field"
              :value="model[field.key]"
              :set-value="(value: any) => setFieldValue(field, value)"
            />
            <a-select
              v-else-if="field.type === 'select'"
              v-bind="field.componentProps"
              v-model:value="fieldModel(field).value"
              :allow-clear="field.clearable ?? true"
              :disabled="field.disabled"
              :placeholder="field.placeholder"
              :options="field.options ?? []"
              :show-search="field.showSearch ?? ((field.options?.length ?? 0) > 6)"
              option-filter-prop="label"
            />
            <a-range-picker
              v-else-if="field.type === 'dateRange'"
              v-bind="field.componentProps"
              v-model:value="fieldModel(field).value"
              :allow-clear="field.clearable ?? true"
              :disabled="field.disabled"
              :placeholder="getRangePlaceholder(field)"
            />
            <a-input-number
              v-else-if="field.type === 'number'"
              v-bind="field.componentProps"
              v-model:value="fieldModel(field).value"
              :disabled="field.disabled"
              :placeholder="getTextPlaceholder(field)"
              @pressEnter="submit"
            />
            <a-input
              v-else
              v-bind="field.componentProps"
              v-model:value="fieldModel(field).value"
              :allow-clear="field.clearable ?? true"
              :disabled="field.disabled"
              :placeholder="getTextPlaceholder(field)"
              @pressEnter="submit"
            />
          </a-form-item>
        </a-col>

        <a-col v-bind="actionColProps">
          <div class="admin-search-form__actions">
            <a-space wrap>
              <a-button :disabled="loading" @click="reset">{{ resetText }}</a-button>
              <a-button type="primary" :loading="loading" html-type="submit">
                <template #icon>
                  <SearchOutlined />
                </template>
                {{ submitText }}
              </a-button>
              <a-button type="link" class="admin-search-form__toggle" @click="expanded = !expanded">
                {{ expanded ? '收起' : '展开' }}
                <component :is="expanded ? UpOutlined : DownOutlined" />
              </a-button>
              <slot name="actions" :model="model" />
            </a-space>
          </div>
        </a-col>
      </a-row>
    </a-form>
  </a-card>
</template>

<style scoped>
.admin-search-form {
  min-width: 0;
  background: var(--surface-1);
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

.admin-search-form :deep(.ant-card-body) {
  padding: 18px 20px 18px 18px;
}

.admin-search-form :deep(.ant-form-item) {
  min-width: 0;
  margin-bottom: 0;
}

.admin-search-form :deep(.ant-form-item-label) {
  overflow: visible;
  flex: 0 0 78px !important;
}

.admin-search-form :deep(.ant-form-item-label > label) {
  height: 36px;
  color: var(--text-primary);
  font-weight: 600;
  white-space: nowrap;
}

.admin-search-form :deep(.ant-input) {
  width: 100%;
}

.admin-search-form :deep(.ant-picker),
.admin-search-form :deep(.ant-input-number),
.admin-search-form :deep(.ant-input-affix-wrapper),
.admin-search-form :deep(.ant-select-single .ant-select-selector) {
  width: 100%;
  min-height: 36px;
  border-radius: 6px;
}

.admin-search-form :deep(.ant-select) {
  width: 100%;
}

.admin-search-form :deep(.ant-select-single .ant-select-selector) {
  height: 36px;
}

.admin-search-form :deep(.ant-select-single .ant-select-selection-search-input),
.admin-search-form :deep(.ant-select-single .ant-select-selection-item),
.admin-search-form :deep(.ant-select-single .ant-select-selection-placeholder),
.admin-search-form :deep(.ant-input-number-input) {
  height: 34px;
  line-height: 34px;
}

.admin-search-form__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  width: 100%;
  min-height: 36px;
  min-width: 0;
}

.admin-search-form__actions :deep(.ant-btn) {
  height: 36px;
  border-radius: 6px;
  font-weight: 600;
}

.admin-search-form__toggle {
  display: inline-flex;
  gap: 4px;
  align-items: center;
  padding-inline: 0;
}

@media (max-width: 575px) {
  .admin-search-form :deep(.ant-card-body) {
    padding: 14px;
  }

  .admin-search-form__actions {
    justify-content: stretch;
  }

  .admin-search-form__actions :deep(.ant-space),
  .admin-search-form__actions :deep(.ant-space-item) {
    width: 100%;
  }

  .admin-search-form__actions :deep(.ant-btn) {
    width: 100%;
  }
}
</style>
