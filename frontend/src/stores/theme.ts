import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { theme as antdPresetTheme } from 'antdv-next'

const THEME_KEY = 'fastapi-scheduler.theme'

type AppTheme = 'light' | 'dark'

const readStoredTheme = (): AppTheme =>
  window.localStorage.getItem(THEME_KEY) === 'light' ? 'light' : 'dark'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<AppTheme>(readStoredTheme())
  const rootThemeClass = computed(() => `scheduler-theme-${theme.value}`)
  const menuTheme = computed(() => theme.value)
  const antdTheme = computed(() => ({
    algorithm:
      theme.value === 'dark' ? antdPresetTheme.darkAlgorithm : antdPresetTheme.defaultAlgorithm,
    token: {
      colorPrimary: '#1677ff',
      borderRadius: 6,
    },
    components: {
      Menu: {
        activeBarBorderWidth: 0,
        activeBarWidth: 0,
        darkItemBg: '#1f2024',
        darkSubMenuItemBg: 'transparent',
        darkItemColor: 'rgba(255, 255, 255, 0.72)',
        darkItemHoverBg: '#2b2e33',
        darkItemHoverColor: '#fff',
        darkItemSelectedBg: '#303338',
        darkItemSelectedColor: '#fff',
        subMenuItemSelectedColor: '#fff',
        itemHoverBg: '#f5f8ff',
        itemHoverColor: '#1677ff',
        subMenuItemBg: 'transparent',
        itemSelectedBg: '#e6f0ff',
        itemSelectedColor: '#1677ff',
      },
    },
  }))

  const applyTheme = (value: AppTheme) => {
    document.documentElement.dataset.theme = value
  }

  applyTheme(theme.value)

  const setTheme = (value: AppTheme) => {
    theme.value = value
    window.localStorage.setItem(THEME_KEY, value)
    applyTheme(value)
  }

  return {
    theme,
    menuTheme,
    antdTheme,
    rootThemeClass,
    setTheme,
  }
})
