<script setup lang="ts">
import { computed, useSlots } from 'vue'

defineOptions({
  inheritAttrs: false,
})

const props = withDefaults(
  defineProps<{
    title?: string
    description?: string
    columns?: any[]
    dataSource?: any[]
    rowKey?: string | ((record: any, index?: number) => string | number)
    loading?: boolean | Record<string, any>
    size?: 'small' | 'middle' | 'large'
    scroll?: Record<string, any>
    scrollX?: number | string | true
    scrollY?: number | string
    pagination?: false | Record<string, any>
    bordered?: boolean
    showHeader?: boolean
    sticky?: boolean | Record<string, any>
    tableLayout?: 'auto' | 'fixed'
    emptyText?: string
    fill?: boolean
  }>(),
  {
    title: '',
    description: '',
    columns: () => [],
    dataSource: () => [],
    rowKey: 'id',
    loading: false,
    size: 'small',
    scroll: undefined,
    scrollX: 'max-content',
    scrollY: undefined,
    pagination: undefined,
    bordered: false,
    showHeader: true,
    sticky: false,
    tableLayout: undefined,
    emptyText: '暂无数据',
    fill: false,
  },
)

const slots = useSlots()
const reservedSlotNames = ['title', 'description', 'toolbar', 'extra', 'empty']
const tableSlotNames = computed(() =>
  Object.keys(slots).filter((name) => {
    if (reservedSlotNames.includes(name)) return false
    if (name === 'emptyText' && (slots.empty || props.emptyText)) return false
    return true
  }),
)
const resolvedPagination = computed(() =>
  props.pagination === undefined
    ? {
        pageSize: 20,
        size: 'small',
        showSizeChanger: true,
        showQuickJumper: false,
        pageSizeOptions: ['10', '20', '50', '100'],
        showTotal: (total: number) => `共 ${total} 条记录`,
      }
    : props.pagination,
)
const resolvedScroll = computed(() => {
  if (props.scroll) return props.scroll
  const scroll: Record<string, any> = {}
  if (props.scrollX) scroll.x = props.scrollX
  if (props.scrollY) scroll.y = props.scrollY
  return Object.keys(scroll).length > 0 ? scroll : undefined
})
</script>

<template>
  <a-card size="small" :class="['admin-data-table', { 'admin-data-table--fill': fill }]">
    <template v-if="title || description || $slots.title || $slots.description" #title>
      <div class="admin-data-table__heading">
        <div class="admin-data-table__title">
          <slot name="title">{{ title }}</slot>
        </div>
        <div v-if="description || $slots.description" class="admin-data-table__description">
          <slot name="description">{{ description }}</slot>
        </div>
      </div>
    </template>
    <template v-if="$slots.toolbar || $slots.extra" #extra>
      <a-space wrap class="admin-data-table__toolbar">
        <slot name="toolbar" />
        <slot name="extra" />
      </a-space>
    </template>

    <div class="admin-data-table__wrap">
      <a-table
        v-bind="$attrs"
        :size="size"
        :row-key="rowKey"
        :columns="columns || []"
        :data-source="dataSource || []"
        :loading="loading"
        :scroll="resolvedScroll"
        :pagination="resolvedPagination"
        :bordered="bordered"
        :show-header="showHeader"
        :sticky="sticky"
        :table-layout="tableLayout"
      >
        <template v-if="$slots.empty || emptyText" #emptyText>
          <slot name="empty">
            <a-empty :description="emptyText" />
          </slot>
        </template>
        <template v-for="name in tableSlotNames" #[name]="slotProps">
          <slot :name="name" v-bind="slotProps || {}" />
        </template>
      </a-table>
    </div>
  </a-card>
</template>

<style scoped>
.admin-data-table {
  min-width: 0;
  max-width: 100%;
  background: var(--surface-1);
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

.admin-data-table--fill {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
}

.admin-data-table :deep(.ant-card-head),
.admin-data-table :deep(.ant-card-head-wrapper),
.admin-data-table :deep(.ant-card-head-title),
.admin-data-table :deep(.ant-card-body),
.admin-data-table__wrap {
  min-width: 0;
  max-width: 100%;
}

.admin-data-table :deep(.ant-card-head-wrapper) {
  gap: 12px;
}

.admin-data-table :deep(.ant-card-head) {
  min-height: 56px;
  padding: 0 10px;
  border-bottom: 0;
}

.admin-data-table :deep(.ant-card-body) {
  padding: 0 10px 10px;
}

.admin-data-table--fill :deep(.ant-card-body) {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
}

.admin-data-table :deep(.ant-card-head-title) {
  overflow: hidden;
}

.admin-data-table__heading {
  min-width: 0;
}

.admin-data-table__title {
  overflow: hidden;
  color: var(--text-primary);
  font-size: 17px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.admin-data-table__description {
  margin-top: 2px;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 400;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.admin-data-table__toolbar {
  justify-content: flex-end;
}

.admin-data-table__toolbar :deep(.ant-btn) {
  height: 34px;
  border-radius: 8px;
  font-weight: 700;
}

.admin-data-table__toolbar :deep(.ant-btn-circle) {
  width: 34px;
  min-width: 34px;
  padding-inline: 0;
}

.admin-data-table__wrap {
  min-height: 0;
  overflow: hidden;
  border: 1px solid var(--surface-border);
  border-radius: 4px;
}

.admin-data-table--fill .admin-data-table__wrap,
.admin-data-table--fill .admin-data-table__wrap :deep(.ant-table-wrapper),
.admin-data-table--fill .admin-data-table__wrap :deep(.ant-spin-nested-loading),
.admin-data-table--fill .admin-data-table__wrap :deep(.ant-spin-container) {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
}

.admin-data-table__wrap :deep(.ant-table-wrapper),
.admin-data-table__wrap :deep(.ant-spin-nested-loading),
.admin-data-table__wrap :deep(.ant-spin-container) {
  min-width: 0;
  max-width: 100%;
}

.admin-data-table__wrap :deep(.ant-table),
.admin-data-table__wrap :deep(.ant-table-container),
.admin-data-table__wrap :deep(.ant-table-content) {
  max-width: 100%;
}

.admin-data-table--fill .admin-data-table__wrap :deep(.ant-table) {
  flex: 1 1 auto;
  min-height: 0;
}

.admin-data-table__wrap :deep(.ant-table) {
  color: var(--text-primary);
  background: var(--surface-1);
}

.admin-data-table__wrap :deep(.ant-table-thead > tr > th) {
  height: 40px;
  padding: 10px 12px;
  color: var(--text-secondary);
  font-weight: 800;
  background: var(--table-head-bg, var(--surface-2));
  border-color: var(--surface-border);
}

.admin-data-table__wrap :deep(.ant-table-tbody > tr > td) {
  height: 41px;
  padding: 8px 12px;
  color: var(--text-primary);
  font-weight: 600;
  background: var(--surface-1);
  border-color: var(--surface-border);
}

.admin-data-table__wrap :deep(.ant-table-tbody > tr:hover > td) {
  background: var(--table-row-hover-bg, var(--control-bg));
}

.admin-data-table__wrap :deep(.ant-table-cell-fix-right),
.admin-data-table__wrap :deep(.ant-table-cell-fix-left) {
  background: var(--surface-1);
}

.admin-data-table__wrap :deep(.ant-table-tbody > tr:hover > .ant-table-cell-fix-right),
.admin-data-table__wrap :deep(.ant-table-tbody > tr:hover > .ant-table-cell-fix-left) {
  background: var(--table-row-hover-bg, var(--control-bg));
}

.admin-data-table__wrap :deep(.ant-btn-link) {
  height: auto;
  padding: 0;
  font-weight: 700;
}

.admin-data-table__wrap :deep(.ant-table-cell) {
  word-break: break-word;
}

.admin-data-table__wrap :deep(.ant-table-pagination.ant-pagination) {
  align-items: center;
  margin: 14px 0 0;
  padding: 0 4px;
}

.admin-data-table__wrap :deep(.ant-pagination-total-text) {
  order: -2;
  flex: 0 0 auto;
  margin-inline-end: 12px;
  color: var(--text-primary);
  font-weight: 700;
}

.admin-data-table__wrap :deep(.ant-pagination-options) {
  order: -1;
  margin-inline-start: 0;
  margin-inline-end: auto;
}

.admin-data-table__wrap :deep(.ant-pagination-options .ant-select) {
  min-width: 108px;
}

.admin-data-table__wrap :deep(.ant-pagination-item),
.admin-data-table__wrap :deep(.ant-pagination-prev),
.admin-data-table__wrap :deep(.ant-pagination-next),
.admin-data-table__wrap :deep(.ant-pagination-jump-prev),
.admin-data-table__wrap :deep(.ant-pagination-jump-next) {
  border-radius: 7px;
}

@media (max-width: 575px) {
  .admin-data-table :deep(.ant-card-head-wrapper) {
    align-items: flex-start;
    flex-direction: column;
  }

  .admin-data-table :deep(.ant-card-extra),
  .admin-data-table__toolbar {
    width: 100%;
  }
}
</style>
