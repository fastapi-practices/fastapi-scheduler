<script setup lang="ts">
import { useThemeStore } from '@/store/modules/theme';
import { $t } from '@/locales';
import SettingItem from '../../../components/setting-item.vue';

defineOptions({
  name: 'ThemeColor'
});

const themeStore = useThemeStore();

function handleUpdateColor(color: string, key: App.Theme.ThemeColorKey) {
  themeStore.updateThemeColors(key, color);
}

const swatches: string[] = [
  '#3b82f6',
  '#6366f1',
  '#8b5cf6',
  '#a855f7',
  '#0ea5e9',
  '#06b6d4',
  '#f43f5e',
  '#ef4444',
  '#ec4899',
  '#d946ef',
  '#f97316',
  '#f59e0b',
  '#eab308',
  '#84cc16',
  '#22c55e',
  '#10b981'
];

const colorPresets = [
  {
    label: 'Preset',
    colors: swatches
  }
];

function handleColorPickerChange(value: unknown, key: App.Theme.ThemeColorKey) {
  const color =
    typeof value === 'string'
      ? value
      : typeof value === 'object' && value && 'toHexString' in value
        ? (value as { toHexString?: () => string }).toHexString?.()
        : undefined;

  if (color) {
    handleUpdateColor(color, key);
  }
}
</script>

<template>
  <ADivider>{{ $t('theme.appearance.themeColor.title') }}</ADivider>
  <div class="flex-col-stretch gap-12px">
    <SettingItem key="recommend-color" :label="$t('theme.appearance.recommendColor')">
      <template #suffix>
        <IconTooltip>
          <p>
            <span class="pr-12px">{{ $t('theme.appearance.recommendColorDesc') }}</span>
            <br />
            <a href="https://uicolors.app/create" target="_blank" rel="noopener noreferrer" class="text-gray">
              https://uicolors.app/create
            </a>
          </p>
        </IconTooltip>
      </template>
      <ASwitch v-model:checked="themeStore.recommendColor" />
    </SettingItem>

    <SettingItem
      v-for="(_, key) in themeStore.themeColors"
      :key="key"
      :label="$t(`theme.appearance.themeColor.${key}`)"
    >
      <template v-if="key === 'info'" #suffix>
        <ACheckbox v-model:checked="themeStore.isInfoFollowPrimary">
          {{ $t('theme.appearance.themeColor.followPrimary') }}
        </ACheckbox>
      </template>
      <div class="w-90px flex justify-end">
        <AColorPicker
          :value="themeStore.themeColors[key]"
          :disabled="key === 'info' && themeStore.isInfoFollowPrimary"
          disabled-alpha
          value-format="hex"
          :presets="colorPresets"
          @update:value="handleColorPickerChange($event, key)"
        />
      </div>
    </SettingItem>
  </div>
</template>

<style scoped></style>
