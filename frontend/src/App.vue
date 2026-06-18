<script setup lang="ts">
import { computed } from 'vue';
import { theme } from 'antdv-next';
import type { ThemeConfig, WatermarkProps } from 'antdv-next';
import { useAppStore } from './store/modules/app';
import { useThemeStore } from './store/modules/theme';
import { antdvLocales } from './locales/antdv';

defineOptions({
  name: 'App'
});

const appStore = useAppStore();
const themeStore = useThemeStore();

const antdvTheme = computed<ThemeConfig>(() => {
  const algorithms = [theme.defaultAlgorithm];

  if (themeStore.darkMode) {
    algorithms.push(theme.darkAlgorithm);
  }

  return {
    ...themeStore.antdvTheme,
    algorithm: algorithms
  };
});

const antdvLocale = computed(() => {
  return antdvLocales[appStore.locale];
});

const watermarkProps = computed<WatermarkProps>(() => {
  return {
    content: themeStore.watermarkContent,
    width: 384,
    height: 384,
    font: {
      fontSize: 16
    },
    gap: [384, 384],
    offset: [12, 60],
    rotate: -15,
    zIndex: 9999
  };
});
</script>

<template>
  <AConfigProvider :theme="antdvTheme" :locale="antdvLocale" class="h-full">
    <AppProvider>
      <AWatermark v-if="themeStore.watermark.visible" v-bind="watermarkProps" class="h-full">
        <RouterView class="bg-layout" />
      </AWatermark>
      <RouterView v-else class="bg-layout" />
    </AppProvider>
  </AConfigProvider>
</template>

<style scoped></style>
