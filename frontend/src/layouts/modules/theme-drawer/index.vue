<script setup lang="ts">
import { computed, ref } from 'vue';
import { SimpleScrollbar } from '@sa/materials';
import { useAppStore } from '@/store/modules/app';
import { $t } from '@/locales';
import AppearanceSettings from './modules/appearance/index.vue';
import LayoutSettings from './modules/layout/index.vue';
import GeneralSettings from './modules/general/index.vue';
import ConfigOperation from './modules/config-operation.vue';
import PresetSettings from './modules/preset/index.vue';

defineOptions({
  name: 'ThemeDrawer'
});

const appStore = useAppStore();
const activeTab = ref('appearance');

const drawerWidth = computed(() => {
  const width = 400;

  if (appStore.isMobile) {
    return Math.min(window.innerWidth * 0.9, width);
  }

  return width;
});

const tabOptions = computed(() => [
  { value: 'appearance', label: $t('theme.tabs.appearance') },
  { value: 'layout', label: $t('theme.tabs.layout') },
  { value: 'general', label: $t('theme.tabs.general') },
  { value: 'preset', label: $t('theme.tabs.preset') }
]);

const drawerStyles = {
  body: {
    padding: '0px'
  }
};
</script>

<template>
  <ADrawer
    v-model:open="appStore.themeDrawerVisible"
    :title="$t('theme.themeDrawerTitle')"
    :size="drawerWidth"
    :closable="{ placement: 'end' }"
    :styles="drawerStyles"
  >
    <SimpleScrollbar>
      <div class="px-24px py-16px">
        <ASegmented v-model:value="activeTab" :options="tabOptions" size="middle" block class="mb-16px bg-layout" />

        <div class="min-h-400px">
          <KeepAlive>
            <AppearanceSettings v-if="activeTab === 'appearance'" />
            <LayoutSettings v-else-if="activeTab === 'layout'" />
            <GeneralSettings v-else-if="activeTab === 'general'" />
            <PresetSettings v-else-if="activeTab === 'preset'" />
          </KeepAlive>
        </div>
      </div>
    </SimpleScrollbar>

    <template #footer>
      <ConfigOperation />
    </template>
  </ADrawer>
</template>

<style scoped></style>
