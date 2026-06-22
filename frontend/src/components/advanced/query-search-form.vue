<script setup lang="ts">
import type { CSSProperties } from 'vue';
import { computed, ref } from 'vue';
import { $t } from '@/locales';

defineOptions({
  name: 'QuerySearchForm'
});

type SearchItemType = 'input' | 'input-number' | 'select';

interface SearchItem {
  key: string;
  label: string;
  type?: SearchItemType;
  placeholder?: string;
  options?: CommonType.Option[];
  props?: Record<string, unknown>;
}

interface Props {
  items: SearchItem[];
  loading?: boolean;
  defaultCollapsed?: boolean;
  collapsedRows?: number;
  minItemWidth?: number;
  labelWidth?: number;
}

const props = withDefaults(defineProps<Props>(), {
  collapsedRows: 1,
  defaultCollapsed: false,
  labelWidth: 96,
  minItemWidth: 260
});

const emit = defineEmits<{
  (e: 'reset'): void;
  (e: 'search'): void;
}>();

const model = defineModel<Record<string, any>>('model', { required: true });
const formRef = ref();
const collapsed = ref(props.defaultCollapsed);

const labelCol = computed(() => ({
  style: {
    width: `${props.labelWidth}px`
  }
}));

const gridStyle = computed<CSSProperties>(() => ({
  gridTemplateColumns: `repeat(auto-fit, minmax(${props.minItemWidth}px, 1fr))`
}));

const visibleItems = computed(() => {
  if (!collapsed.value) {
    return props.items;
  }
  return props.items.slice(0, props.collapsedRows);
});

async function validate() {
  await formRef.value?.validate?.();
}

function reset() {
  for (const item of props.items) {
    model.value[item.key] = null;
  }
  emit('reset');
}

async function search() {
  await validate();
  emit('search');
}

function toggleCollapsed() {
  collapsed.value = !collapsed.value;
}
</script>

<template>
  <ACard variant="borderless" class="query-search-form card-wrapper">
    <AForm ref="formRef" :model="model" :colon="false" label-align="right" :label-col="labelCol">
      <div class="query-search-form__grid" :style="gridStyle">
        <AFormItem
          v-for="item in visibleItems"
          :key="item.key"
          :name="item.key"
          :label="item.label"
          class="query-search-form__item"
        >
          <slot :name="item.key" :item="item" :model="model">
            <AInputNumber
              v-if="item.type === 'input-number'"
              v-model:value="model[item.key]"
              class="w-full"
              :placeholder="item.placeholder"
              v-bind="item.props"
              @keyup.enter="search"
            />
            <ASelect
              v-else-if="item.type === 'select'"
              v-model:value="model[item.key]"
              allow-clear
              class="w-full"
              :placeholder="item.placeholder"
              :options="item.options"
              v-bind="item.props"
            />
            <AInput
              v-else
              v-model:value="model[item.key]"
              allow-clear
              :placeholder="item.placeholder"
              v-bind="item.props"
              @keyup.enter="search"
            />
          </slot>
        </AFormItem>

        <div class="query-search-form__action">
          <ASpace :size="12">
            <AButton class="query-search-form__button" @click="reset">
              {{ $t('common.reset') }}
            </AButton>
            <AButton type="primary" class="query-search-form__button" :loading="loading" @click="search">
              {{ $t('common.search') }}
            </AButton>
            <AButton type="link" class="query-search-form__collapse" @click="toggleCollapsed">
              <template #icon>
                <icon-mdi-chevron-down v-if="collapsed" />
                <icon-mdi-chevron-up v-else />
              </template>
              {{ collapsed ? $t('common.expand') : $t('common.collapse') }}
            </AButton>
          </ASpace>
        </div>
      </div>
    </AForm>
  </ACard>
</template>

<style scoped>
.query-search-form {
  flex-shrink: 0;
}

.query-search-form__grid {
  display: grid;
  gap: 16px 24px;
  align-items: start;
}

.query-search-form__item {
  margin-bottom: 0;
}

.query-search-form__action {
  display: flex;
  justify-content: flex-end;
  min-width: 260px;
}

.query-search-form__button {
  min-width: 72px;
}

.query-search-form__collapse {
  padding-inline: 0;
}
</style>
