<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

const emit = defineEmits<{
  (e: 'search'): void;
}>();

const model = defineModel<Api.Scheduler.RunSearchModel>('model', { required: true });

const searchItems = computed(() => [
  {
    key: 'schedule_id',
    label: $t('page.scheduler.runs.columns.scheduleId'),
    placeholder: $t('page.scheduler.runs.scheduleIdPlaceholder')
  }
]);
</script>

<template>
  <QuerySearchForm v-model:model="model" :items="searchItems" default-collapsed @search="emit('search')" />
</template>

<style scoped></style>
