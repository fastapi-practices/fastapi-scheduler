<script setup lang="ts">
import { App as AntApp, ConfigProvider, message } from 'antdv-next'
import { storeToRefs } from 'pinia'
import { computed, h, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DashboardOutlined,
  HistoryOutlined,
  LineChartOutlined,
  ScheduleOutlined,
  SettingOutlined,
} from '@antdv-next/icons'

import { AdminShell, type AdminMenuItem } from '../components/admin-kit'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const { session, userName } = storeToRefs(authStore)
const { antdTheme, menuTheme, rootThemeClass, theme } = storeToRefs(themeStore)

const menuItems: AdminMenuItem[] = [
  {
    key: 'dashboard',
    label: '仪表盘',
    icon: DashboardOutlined,
    path: 'dashboard',
  },
  {
    key: 'analysis',
    label: '分析',
    icon: LineChartOutlined,
    path: 'analysis',
  },
  {
    key: 'schedulerCenter',
    label: '调度中心',
    icon: SettingOutlined,
    children: [
      {
        key: 'scheduler',
        label: '任务调度',
        icon: ScheduleOutlined,
        path: 'scheduler',
      },
      {
        key: 'schedulerRuns',
        label: '运行记录',
        icon: HistoryOutlined,
        path: 'schedulerRuns',
      },
    ],
  },
]
const consoleRouteNames = new Set(['dashboard', 'analysis', 'scheduler', 'schedulerRuns'])
const themeMenuItems: AdminMenuItem[] = [
  { key: 'light', label: '明亮主题' },
  { key: 'dark', label: '深色主题' },
]
const userMenuItems: AdminMenuItem[] = [{ key: 'logout', label: '退出登录', danger: true }]

const activeKey = computed(() =>
  typeof route.name === 'string' && consoleRouteNames.has(route.name) ? route.name : 'dashboard',
)
const selectedKeys = computed(() => [activeKey.value])
const themeSelectedKeys = computed(() => [theme.value])
const userEmail = computed(() => session.value?.user.email || '')
const findMenuItem = (items: AdminMenuItem[], key: string): AdminMenuItem | undefined => {
  for (const item of items) {
    if (item.key === key) return item
    const child = item.children ? findMenuItem(item.children, key) : undefined
    if (child) return child
  }
  return undefined
}
const currentTitle = computed(() => findMenuItem(menuItems, activeKey.value)?.label || '仪表盘')

const handleNavigate = async (key: string) => {
  if (key === 'schedulerCenter') {
    await router.push({ name: 'scheduler' })
    return
  }
  if (consoleRouteNames.has(key)) {
    await router.push({ name: key })
  }
}

const handleThemeClick = (key: string) => {
  if (key === 'light' || key === 'dark') {
    themeStore.setTheme(key)
  }
}

const handleUserClick = async (key: string) => {
  if (key === 'logout') {
    await authStore.logout()
    await router.replace({ name: 'login' })
    return
  }
  if (key === 'lock') {
    authStore.clearSession()
    await router.replace({ name: 'login' })
    return
  }
  message.info('该功能正在接入中')
}

watchEffect(() => {
  ConfigProvider.config({
    holderRender: (children) =>
      h(ConfigProvider, { theme: antdTheme.value }, () =>
        h(AntApp, { class: ['app-shell', rootThemeClass.value] }, () => children),
      ),
  })
})
</script>

<template>
  <a-config-provider :theme="antdTheme">
    <a-app :class="['app-shell', rootThemeClass]">
      <AdminShell
        brand="FastAPI Scheduler"
        :current-title="currentTitle"
        :menu-items="menuItems"
        :selected-keys="selectedKeys"
        :menu-theme="menuTheme"
        :root-theme-class="rootThemeClass"
        :theme-menu-items="themeMenuItems"
        :theme-selected-keys="themeSelectedKeys"
        :user-menu-items="userMenuItems"
        :user-email="userEmail"
        :user-name="userName"
        @navigate="handleNavigate"
        @theme-click="handleThemeClick"
        @user-click="handleUserClick"
      >
        <router-view />
      </AdminShell>
    </a-app>
  </a-config-provider>
</template>

<style>
.app-shell {
  height: 100vh;
  min-height: 0;
  overflow: hidden;
  color: var(--text-primary);
  background: var(--page-bg);
}
</style>
