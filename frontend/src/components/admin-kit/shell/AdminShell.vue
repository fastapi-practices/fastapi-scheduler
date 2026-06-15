<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  AppstoreOutlined,
  BarsOutlined,
  BellOutlined,
  BulbOutlined,
  CloseOutlined,
  ExportOutlined,
  FullscreenOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  PushpinOutlined,
  ReloadOutlined,
  SearchOutlined,
  TranslationOutlined,
  UserOutlined,
} from '@antdv-next/icons'

import type { AdminMenuItem, AdminMenuTheme } from '../types'

const props = withDefaults(
  defineProps<{
    brand?: string
    currentTitle?: string
    menuItems: AdminMenuItem[]
    selectedKeys: string[]
    menuTheme?: AdminMenuTheme
    rootThemeClass?: string
    themeMenuItems: AdminMenuItem[]
    themeSelectedKeys: string[]
    userMenuItems: AdminMenuItem[]
    userEmail?: string
    userName?: string
  }>(),
  {
    brand: 'FastAPI Scheduler',
    currentTitle: '',
    menuTheme: 'dark',
    rootThemeClass: '',
    userEmail: '',
    userName: 'admin',
  },
)

const emit = defineEmits<{
  navigate: [key: string]
  themeClick: [key: string]
  userClick: [key: string]
}>()

const mobileMenuOpen = ref(false)
const siderCollapsed = ref(false)
const menuOpenKeys = ref<string[]>([])
const searchOpen = ref(false)
const searchKeyword = ref('')
const closedTabKeys = ref<Set<string>>(new Set())

const flattenMenuItems = (items: AdminMenuItem[]): AdminMenuItem[] =>
  items.flatMap((item) => (item.children?.length ? [item, ...flattenMenuItems(item.children)] : [item]))
const findMenuPath = (items: AdminMenuItem[], key: string, parents: AdminMenuItem[] = []): AdminMenuItem[] => {
  for (const item of items) {
    const currentPath = [...parents, item]
    if (item.key === key) return currentPath
    if (item.children?.length) {
      const childPath = findMenuPath(item.children, key, currentPath)
      if (childPath.length) return childPath
    }
  }
  return []
}

const allMenuItems = computed(() => flattenMenuItems(props.menuItems))
const pageTitle = computed(() => props.currentTitle || allMenuItems.value[0]?.label || '')
const activeMenuItem = computed(() => allMenuItems.value.find((item) => props.selectedKeys.includes(item.key)))
const activeMenuPath = computed(() =>
  props.selectedKeys[0] ? findMenuPath(props.menuItems, props.selectedKeys[0]) : [],
)
const activeOpenKeys = computed(() => activeMenuPath.value.slice(0, -1).map((item) => item.key))
const openKeys = computed(() => (siderCollapsed.value ? [] : menuOpenKeys.value))
const pageMenuItems = computed(() => allMenuItems.value.filter((item) => item.path))
const tabItems = computed(() =>
  pageMenuItems.value.filter((item) => item.key === props.selectedKeys[0] || !closedTabKeys.value.has(item.key)),
)
const searchMenuItems = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  const items = pageMenuItems.value
  if (!keyword) return items
  return items.filter((item) => `${item.label} ${item.key}`.toLowerCase().includes(keyword))
})
const menuItemsForAntd = computed(() => props.menuItems as any[])
const themeMenuItemsForAntd = computed(() => props.themeMenuItems as any[])
const breadcrumbItems = computed(() =>
  activeMenuPath.value.map((item, index) => ({
    key: item.key,
    title: item.label,
    icon: item.icon,
    clickable: index < activeMenuPath.value.length - 1 && Boolean(item.path || item.children?.length),
  })),
)
const activeTabIndex = computed(() => tabItems.value.findIndex((item) => props.selectedKeys.includes(item.key)))

const onNavigate = ({ key }: { key: string }) => {
  emit('navigate', key)
  mobileMenuOpen.value = false
}

const onOpenChange = (keys: string[]) => {
  menuOpenKeys.value = keys
}

const onThemeMenuClick = ({ key }: { key: string }) => {
  emit('themeClick', key)
}

const onUserMenuClick = ({ key }: { key: string }) => {
  emit('userClick', key)
}

const handleTabClick = (item: AdminMenuItem) => {
  emit('navigate', item.key)
}

const closeTab = (key: string) => {
  if (key === 'dashboard') return
  closedTabKeys.value = new Set([...closedTabKeys.value, key])
  if (!props.selectedKeys.includes(key)) return
  const nextItem = tabItems.value.find((item) => item.key !== key) || pageMenuItems.value[0]
  if (nextItem) emit('navigate', nextItem.key)
}

const closeCurrentTab = () => {
  const key = props.selectedKeys[0]
  if (key) closeTab(key)
}

const closeSideTabs = (side: 'left' | 'right') => {
  const currentIndex = activeTabIndex.value
  if (currentIndex < 0) return
  const nextClosed = new Set(closedTabKeys.value)
  tabItems.value.forEach((item, index) => {
    if (item.key !== 'dashboard' && (side === 'left' ? index < currentIndex : index > currentIndex)) {
      nextClosed.add(item.key)
    }
  })
  closedTabKeys.value = nextClosed
}

const closeOtherTabs = () => {
  const activeKey = props.selectedKeys[0]
  closedTabKeys.value = new Set(
    pageMenuItems.value.filter((item) => item.key !== 'dashboard' && item.key !== activeKey).map((item) => item.key),
  )
}

const closeAllTabs = () => {
  closedTabKeys.value = new Set(pageMenuItems.value.filter((item) => item.key !== 'dashboard').map((item) => item.key))
  emit('navigate', 'dashboard')
}

const reopenAllTabs = () => {
  closedTabKeys.value = new Set()
}

const openCurrentInNewWindow = () => {
  const item = activeMenuItem.value
  if (!item) return
  const routePath: Record<string, string> = {
    dashboard: '/dashboard',
    analysis: '/analysis',
    scheduler: '/scheduler',
    schedulerRuns: '/scheduler/runs',
  }
  window.open(`${window.location.origin}${routePath[item.key] || '/'}`, '_blank')
}

const openSearch = () => {
  searchOpen.value = true
}

const navigateFromSearch = (item: AdminMenuItem) => {
  closedTabKeys.value.delete(item.key)
  closedTabKeys.value = new Set(closedTabKeys.value)
  emit('navigate', item.key)
  searchOpen.value = false
  searchKeyword.value = ''
}

const handleKeydown = (event: KeyboardEvent) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    openSearch()
  }
}

const refreshPage = () => {
  window.location.reload()
}

const toggleFullscreen = () => {
  if (document.fullscreenElement) {
    void document.exitFullscreen()
    return
  }
  void document.documentElement.requestFullscreen()
}

watch(
  activeOpenKeys,
  (keys) => {
    menuOpenKeys.value = Array.from(new Set([...menuOpenKeys.value, ...keys]))
  },
  { immediate: true },
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <a-layout :class="['admin-shell-root', rootThemeClass, { 'admin-shell-root--collapsed': siderCollapsed }]">
    <a-layout-sider
      :width="240"
      :collapsed-width="64"
      :collapsed="siderCollapsed"
      :theme="menuTheme"
      :trigger="null"
      class="admin-shell-sider"
    >
      <div class="admin-shell-sidebar">
        <div class="admin-shell-brand">
          <slot name="brand-icon">
            <span class="admin-shell-brand-mark" />
          </slot>
          <span class="admin-shell-brand-title">{{ brand }}</span>
        </div>

        <div class="admin-shell-menu-zone">
          <a-menu
            mode="inline"
            :theme="menuTheme"
            :selected-keys="selectedKeys"
            :open-keys="siderCollapsed ? undefined : openKeys"
            :items="menuItemsForAntd"
            :inline-collapsed="siderCollapsed"
            class="admin-shell-menu"
            @click="onNavigate"
            @openChange="onOpenChange"
          />
        </div>

        <div class="admin-shell-sider-footer">
          <a-button type="text" class="admin-shell-icon-button" @click="siderCollapsed = !siderCollapsed">
            <template #icon>
              <MenuUnfoldOutlined v-if="siderCollapsed" />
              <MenuFoldOutlined v-else />
            </template>
          </a-button>
        </div>
      </div>
    </a-layout-sider>

    <a-drawer
      :open="mobileMenuOpen"
      placement="left"
      :size="300"
      :footer="null"
      root-class="admin-shell-mobile-drawer"
      @close="mobileMenuOpen = false"
    >
      <div class="admin-shell-mobile-menu">
        <div class="admin-shell-brand admin-shell-brand--mobile">
          <span class="admin-shell-brand-mark" />
          <span class="admin-shell-brand-title">{{ brand }}</span>
        </div>
        <a-menu
          mode="inline"
          :theme="menuTheme"
          :selected-keys="selectedKeys"
          :open-keys="openKeys"
          :items="menuItemsForAntd"
          class="admin-shell-menu"
          @click="onNavigate"
          @openChange="onOpenChange"
        />
      </div>
    </a-drawer>

    <a-layout class="admin-shell-main">
      <a-layout-header class="admin-shell-header">
        <div class="admin-shell-header-left">
          <a-button type="text" class="admin-shell-icon-button admin-shell-mobile-trigger" @click="mobileMenuOpen = true">
            <template #icon>
              <BarsOutlined />
            </template>
          </a-button>
          <a-button type="text" class="admin-shell-icon-button admin-shell-desktop-trigger" @click="siderCollapsed = !siderCollapsed">
            <template #icon>
              <MenuUnfoldOutlined v-if="siderCollapsed" />
              <MenuFoldOutlined v-else />
            </template>
          </a-button>
          <a-button type="text" class="admin-shell-icon-button" @click="refreshPage">
            <template #icon>
              <ReloadOutlined />
            </template>
          </a-button>
          <a-breadcrumb separator="›" class="admin-shell-breadcrumb">
            <a-breadcrumb-item v-for="(item, index) in breadcrumbItems" :key="item.key">
              <button
                v-if="item.clickable"
                type="button"
                class="admin-shell-breadcrumb-link"
                @click="emit('navigate', item.key)"
              >
                <component v-if="item.icon" :is="item.icon" />
                <span>{{ item.title }}</span>
              </button>
              <span v-else class="admin-shell-breadcrumb-current">
                <component v-if="item.icon" :is="item.icon" />
                <strong>{{ index === breadcrumbItems.length - 1 ? pageTitle : item.title }}</strong>
              </span>
            </a-breadcrumb-item>
          </a-breadcrumb>
        </div>

        <div class="admin-shell-header-right">
          <button type="button" class="admin-shell-search" @click="openSearch">
            <SearchOutlined />
            <span>搜索</span>
            <kbd>⌘ K</kbd>
          </button>
          <a-dropdown
            :trigger="['click']"
            placement="bottomRight"
            :menu="{
              items: themeMenuItemsForAntd,
              selectable: true,
              selectedKeys: themeSelectedKeys,
              onClick: onThemeMenuClick,
            }"
          >
            <a-button type="text" class="admin-shell-icon-button" aria-label="主题设置">
              <template #icon>
                <BulbOutlined />
              </template>
            </a-button>
          </a-dropdown>
          <a-button type="text" class="admin-shell-icon-button" aria-label="全屏" @click="toggleFullscreen">
            <template #icon>
              <FullscreenOutlined />
            </template>
          </a-button>
          <a-button type="text" class="admin-shell-icon-button" aria-label="语言">
            <template #icon>
              <TranslationOutlined />
            </template>
          </a-button>
          <a-button type="text" class="admin-shell-icon-button admin-shell-notice-button" aria-label="通知">
            <template #icon>
              <BellOutlined />
            </template>
          </a-button>
          <a-dropdown
            :trigger="['click']"
            placement="bottomRight"
            overlay-class-name="admin-shell-user-dropdown"
          >
            <a-button type="text" class="admin-shell-user-button">
              <a-avatar :size="34" class="admin-shell-user-avatar">
                <template #icon>
                  <UserOutlined />
                </template>
              </a-avatar>
              <span class="admin-shell-user-name">{{ userName }}</span>
            </a-button>
            <template #popupRender>
              <div class="admin-shell-user-panel">
                <div class="admin-shell-user-profile">
                  <a-avatar :size="54" class="admin-shell-user-avatar admin-shell-user-avatar--large">
                    <template #icon>
                      <UserOutlined />
                    </template>
                  </a-avatar>
                  <div class="admin-shell-user-meta">
                    <div class="admin-shell-user-title">
                      <strong>{{ userName }}</strong>
                      <span>Admin</span>
                    </div>
                    <p>{{ userEmail || 'scheduler@example.com' }}</p>
                  </div>
                </div>
                <button type="button" class="admin-shell-user-menu-item" @click="onUserMenuClick({ key: 'profile' })">
                  <UserOutlined />
                  <span>个人中心</span>
                </button>
                <button type="button" class="admin-shell-user-menu-item" @click="onUserMenuClick({ key: 'docs' })">
                  <span class="admin-shell-user-menu-icon">?</span>
                  <span>文档</span>
                </button>
                <button type="button" class="admin-shell-user-menu-item" @click="onUserMenuClick({ key: 'github' })">
                  <span class="admin-shell-user-menu-icon">G</span>
                  <span>GitHub</span>
                </button>
                <button type="button" class="admin-shell-user-menu-item" @click="onUserMenuClick({ key: 'help' })">
                  <span class="admin-shell-user-menu-icon">!</span>
                  <span>问题 & 帮助</span>
                </button>
                <div class="admin-shell-user-panel-divider" />
                <button type="button" class="admin-shell-user-menu-item" @click="onUserMenuClick({ key: 'lock' })">
                  <span class="admin-shell-user-menu-icon">L</span>
                  <span>锁定屏幕</span>
                  <kbd>⌥ L</kbd>
                </button>
                <div class="admin-shell-user-panel-divider" />
                <button type="button" class="admin-shell-user-menu-item" @click="onUserMenuClick({ key: 'logout' })">
                  <span class="admin-shell-user-menu-icon">↪</span>
                  <span>退出登录</span>
                  <kbd>⌥ Q</kbd>
                </button>
              </div>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>

      <div class="admin-shell-tabs">
        <div class="admin-shell-tab-prefix">‹</div>
        <div class="admin-shell-tabs-scroll">
          <button
            v-for="item in tabItems"
            :key="item.key"
            type="button"
            :class="['admin-shell-tab', { 'admin-shell-tab--active': selectedKeys.includes(item.key) }]"
            @click="handleTabClick(item)"
          >
            <component v-if="item.icon" :is="item.icon" />
            <span>{{ item.label }}</span>
            <CloseOutlined v-if="item.key !== 'dashboard'" class="admin-shell-tab-close" />
          </button>
        </div>
        <div class="admin-shell-tab-actions">
          <a-dropdown :trigger="['click']" placement="bottomRight" overlay-class-name="admin-shell-tab-dropdown">
            <a-button type="text" class="admin-shell-icon-button" aria-label="标签页管理">
              <template #icon>
                <AppstoreOutlined />
              </template>
            </a-button>
            <template #popupRender>
              <div class="admin-shell-tab-menu">
                <button type="button" class="admin-shell-tab-menu-item" @click="closeCurrentTab">
                  <CloseOutlined />
                  <span>关闭</span>
                </button>
                <button type="button" class="admin-shell-tab-menu-item">
                  <PushpinOutlined />
                  <span>固定</span>
                </button>
                <button type="button" class="admin-shell-tab-menu-item" @click="toggleFullscreen">
                  <FullscreenOutlined />
                  <span>最大化</span>
                </button>
                <button type="button" class="admin-shell-tab-menu-item" @click="refreshPage">
                  <ReloadOutlined />
                  <span>重新加载</span>
                </button>
                <button type="button" class="admin-shell-tab-menu-item" @click="openCurrentInNewWindow">
                  <ExportOutlined />
                  <span>在新窗口打开</span>
                </button>
                <div class="admin-shell-tab-menu-divider" />
                <button type="button" class="admin-shell-tab-menu-item" @click="closeSideTabs('left')">
                  <span class="admin-shell-tab-menu-icon">|←</span>
                  <span>关闭左侧标签页</span>
                </button>
                <button
                  type="button"
                  :disabled="activeTabIndex >= tabItems.length - 1"
                  class="admin-shell-tab-menu-item"
                  @click="closeSideTabs('right')"
                >
                  <span class="admin-shell-tab-menu-icon">→|</span>
                  <span>关闭右侧标签页</span>
                </button>
                <div class="admin-shell-tab-menu-divider" />
                <button type="button" class="admin-shell-tab-menu-item" @click="closeOtherTabs">
                  <span class="admin-shell-tab-menu-icon">↔</span>
                  <span>关闭其它标签页</span>
                </button>
                <button type="button" class="admin-shell-tab-menu-item" @click="closeAllTabs">
                  <span class="admin-shell-tab-menu-icon">⇄</span>
                  <span>关闭全部标签页</span>
                </button>
                <button type="button" class="admin-shell-tab-menu-item" @click="reopenAllTabs">
                  <span class="admin-shell-tab-menu-icon">↺</span>
                  <span>恢复默认</span>
                </button>
              </div>
            </template>
          </a-dropdown>
          <a-button type="text" class="admin-shell-icon-button" @click="refreshPage">
            <template #icon>
              <ReloadOutlined />
            </template>
          </a-button>
          <a-button type="text" class="admin-shell-icon-button" @click="toggleFullscreen">
            <template #icon>
              <FullscreenOutlined />
            </template>
          </a-button>
        </div>
      </div>

      <a-layout-content class="admin-shell-content">
        <div class="admin-shell-content-inner">
          <slot />
        </div>
      </a-layout-content>

      <a-modal
        v-model:open="searchOpen"
        title="搜索菜单"
        :footer="null"
        :width="560"
        root-class="admin-shell-search-modal"
        destroy-on-hidden
      >
        <a-input-search
          v-model:value="searchKeyword"
          size="large"
          allow-clear
          autofocus
          placeholder="搜索仪表盘、分析、任务调度、运行记录"
        />
        <div class="admin-shell-search-list">
          <button
            v-for="item in searchMenuItems"
            :key="item.key"
            type="button"
            class="admin-shell-search-item"
            @click="navigateFromSearch(item)"
          >
            <component v-if="item.icon" :is="item.icon" />
            <span>{{ item.label }}</span>
          </button>
          <a-empty v-if="!searchMenuItems.length" description="没有匹配的菜单" />
        </div>
      </a-modal>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.admin-shell-root {
  width: 100%;
  height: 100vh;
  min-height: 0;
  overflow: hidden;
  color: var(--text-primary);
  background: var(--page-bg);
}

.admin-shell-sider {
  height: 100vh;
  overflow: hidden;
  border-right: 1px solid var(--surface-border);
  background: var(--sider-surface) !important;
}

.admin-shell-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: var(--sider-surface);
}

.admin-shell-brand {
  display: flex;
  flex: 0 0 54px;
  gap: 12px;
  align-items: center;
  min-width: 0;
  padding: 0 14px;
  border-bottom: 0;
}

.admin-shell-brand-mark {
  position: relative;
  display: inline-block;
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  overflow: hidden;
  border-radius: 10px;
  background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 52%, #22c55e 100%);
  box-shadow: 0 10px 30px rgba(22, 119, 255, 0.28);
}

.admin-shell-brand-mark::after {
  position: absolute;
  right: -6px;
  bottom: -8px;
  width: 24px;
  height: 24px;
  content: '';
  background: rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  transform: rotate(35deg);
}

.admin-shell-brand-title {
  overflow: hidden;
  color: var(--text-primary);
  font-size: 19px;
  font-weight: 800;
  letter-spacing: -0.04em;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.admin-shell-root--collapsed .admin-shell-brand {
  justify-content: center;
  padding: 0;
}

.admin-shell-root--collapsed .admin-shell-brand-title {
  display: none;
}

.admin-shell-menu-zone {
  flex: 1 1 auto;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 12px 8px;
  background: var(--sider-surface);
  scrollbar-width: thin;
}

.admin-shell-menu-zone::-webkit-scrollbar,
.admin-shell-tabs-scroll::-webkit-scrollbar,
.admin-shell-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.admin-shell-menu-zone::-webkit-scrollbar-thumb,
.admin-shell-tabs-scroll::-webkit-scrollbar-thumb,
.admin-shell-content::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.26);
  border-radius: 999px;
}

.admin-shell-menu {
  border-inline-end: 0 !important;
  background: transparent !important;
}

.admin-shell-menu :deep(.ant-menu),
.admin-shell-menu :deep(.ant-menu-sub),
.admin-shell-menu :deep(.ant-menu-inline),
.admin-shell-menu :deep(.ant-menu-submenu),
.admin-shell-menu :deep(.ant-menu-submenu-inline),
.admin-shell-menu :deep(.ant-menu-submenu .ant-menu),
.admin-shell-menu :deep(.ant-menu-submenu .ant-menu-sub),
.admin-shell-menu :deep(.ant-menu-submenu .ant-menu-inline) {
  border-inline-end: 0 !important;
  background: transparent !important;
}

:global(.admin-shell-menu.ant-menu-light .ant-menu-sub.ant-menu-inline),
:global(.admin-shell-menu.ant-menu-light .ant-menu-submenu .ant-menu-sub),
:global(.admin-shell-menu.ant-menu-light .ant-menu-submenu .ant-menu-inline),
:global(.admin-shell-menu.ant-menu-dark .ant-menu-sub.ant-menu-inline),
:global(.admin-shell-menu.ant-menu-dark .ant-menu-submenu .ant-menu-sub),
:global(.admin-shell-menu.ant-menu-dark .ant-menu-submenu .ant-menu-inline) {
  background: transparent !important;
}

.admin-shell-menu :deep(.ant-menu-item),
.admin-shell-menu :deep(.ant-menu-submenu-title) {
  height: 44px !important;
  margin: 3px 0 !important;
  width: auto !important;
  border-radius: 8px !important;
  border-inline-end: 0 !important;
  color: var(--text-secondary) !important;
  font-weight: 650;
}

.admin-shell-menu :deep(.ant-menu-item)::after,
.admin-shell-menu :deep(.ant-menu-submenu-title)::after {
  display: none !important;
  width: 0 !important;
  content: none !important;
  border-inline-end: 0 !important;
}

.admin-shell-menu :deep(.ant-menu-item:hover),
.admin-shell-menu :deep(.ant-menu-submenu-title:hover) {
  color: #1677ff !important;
  background: #f5f8ff !important;
}

.admin-shell-menu :deep(.ant-menu-item-selected) {
  color: #1677ff !important;
  background: #e6f0ff !important;
  box-shadow: none;
}

.admin-shell-menu :deep(.ant-menu-submenu-selected > .ant-menu-submenu-title) {
  color: #1677ff !important;
  background: transparent !important;
}

.admin-shell-menu :deep(.ant-menu-item .anticon),
.admin-shell-menu :deep(.ant-menu-submenu-title .anticon) {
  font-size: 17px;
}

.scheduler-theme-light.admin-shell-root .admin-shell-brand {
  flex-basis: 56px;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu-zone {
  padding: 20px 16px;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-item),
.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-title) {
  height: 52px !important;
  margin: 5px 0 !important;
  padding-inline: 18px !important;
  color: rgba(0, 0, 0, 0.88) !important;
  font-size: 18px;
  font-weight: 700;
  border-radius: 14px !important;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-sub .ant-menu-item) {
  padding-left: 70px !important;
  font-weight: 700;
  background: transparent !important;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-item .anticon),
.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-title .anticon) {
  min-width: 22px;
  margin-inline-end: 16px;
  color: currentColor;
  font-size: 21px;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-title-content) {
  font-size: 18px;
  line-height: 52px;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-sub .ant-menu-title-content) {
  font-size: 18px;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-arrow) {
  color: currentColor;
  transform: scale(1.18);
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-item:hover),
.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-title:hover) {
  color: #1677ff !important;
  background: #f5f8ff !important;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-item-selected) {
  color: #1677ff !important;
  background: #e6f0ff !important;
}

.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-selected > .ant-menu-submenu-title),
.scheduler-theme-light.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-open > .ant-menu-submenu-title) {
  color: #1677ff !important;
  background: transparent !important;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-brand {
  flex-basis: 56px;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-sider {
  border-right-color: rgba(255, 255, 255, 0.08);
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu-zone {
  padding: 20px 16px;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-item),
.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-title) {
  height: 52px !important;
  margin: 5px 0 !important;
  padding-inline: 18px !important;
  color: rgba(255, 255, 255, 0.72) !important;
  font-size: 18px;
  font-weight: 700;
  border-radius: 14px !important;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-sub .ant-menu-item) {
  padding-left: 70px !important;
  font-weight: 700;
  background: transparent !important;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-item .anticon),
.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-title .anticon) {
  min-width: 22px;
  margin-inline-end: 16px;
  color: currentColor;
  font-size: 21px;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-title-content) {
  font-size: 18px;
  line-height: 52px;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-sub .ant-menu-title-content) {
  font-size: 18px;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-arrow) {
  color: currentColor;
  transform: scale(1.18);
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-item:hover),
.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-title:hover) {
  color: #fff !important;
  background: #2b2e33 !important;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-item-selected) {
  color: #fff !important;
  background: #303338 !important;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-selected > .ant-menu-submenu-title),
.scheduler-theme-dark.admin-shell-root .admin-shell-menu :deep(.ant-menu-submenu-open > .ant-menu-submenu-title) {
  color: #fff !important;
  background: transparent !important;
}

.scheduler-theme-dark.admin-shell-root .admin-shell-sider-footer {
  border-top-color: rgba(255, 255, 255, 0.08);
}

.admin-shell-sider-footer {
  display: flex;
  flex: 0 0 46px;
  align-items: center;
  justify-content: flex-start;
  padding: 0 14px;
  background: var(--sider-surface);
  border-top: 1px solid var(--surface-border);
}

.admin-shell-sider .admin-shell-icon-button {
  color: var(--text-secondary) !important;
}

.admin-shell-sider .admin-shell-icon-button:hover {
  color: var(--text-primary) !important;
  background: var(--control-bg) !important;
}

.admin-shell-main {
  height: 100vh;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  background: var(--page-bg) !important;
}

.admin-shell-header {
  display: flex;
  flex: 0 0 52px;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  min-width: 0;
  padding: 0 16px !important;
  line-height: 1;
  background: var(--shell-surface) !important;
  border-bottom: 1px solid var(--surface-border);
}

.admin-shell-header-left,
.admin-shell-header-right,
.admin-shell-breadcrumb,
.admin-shell-tabs-scroll,
.admin-shell-tab-actions {
  display: flex;
  align-items: center;
  min-width: 0;
}

.admin-shell-header-left {
  gap: 8px;
}

.admin-shell-header-right {
  flex: 0 0 auto;
  gap: 8px;
}

.admin-shell-breadcrumb {
  gap: 8px;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 32px;
  white-space: nowrap;
}

.admin-shell-breadcrumb :deep(ol) {
  display: inline-flex;
  align-items: center;
  min-width: 0;
  height: 32px;
}

.admin-shell-breadcrumb :deep(li) {
  display: inline-flex;
  align-items: center;
  min-width: 0;
  height: 32px;
}

.admin-shell-breadcrumb :deep(.ant-breadcrumb-separator) {
  display: inline-flex;
  align-items: center;
  height: 32px;
  color: var(--text-tertiary);
  line-height: 32px;
}

.admin-shell-breadcrumb :deep(.ant-breadcrumb-link),
.admin-shell-breadcrumb-current,
.admin-shell-breadcrumb-link {
  display: inline-flex;
  gap: 7px;
  align-items: center;
  max-width: 260px;
  height: 32px;
  line-height: 32px;
}

.admin-shell-breadcrumb-link {
  height: 28px;
  padding: 0 6px;
  color: var(--text-secondary);
  font: inherit;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 6px;
}

.admin-shell-breadcrumb-link:hover {
  color: var(--text-primary);
  background: var(--control-bg);
}

.admin-shell-breadcrumb strong,
.admin-shell-breadcrumb-current strong {
  overflow: hidden;
  color: var(--text-primary);
  font-weight: 750;
  text-overflow: ellipsis;
}

.admin-shell-breadcrumb-separator {
  color: var(--text-tertiary);
}

.admin-shell-search {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  height: 34px;
  min-width: 132px;
  padding: 0 10px;
  color: var(--text-secondary);
  font: inherit;
  cursor: pointer;
  background: var(--control-bg);
  border: 1px solid var(--surface-border);
  border-radius: 999px;
}

.admin-shell-search:hover {
  color: var(--text-primary);
  border-color: rgba(22, 119, 255, 0.42);
}

.admin-shell-search kbd {
  padding: 2px 6px;
  color: var(--text-secondary);
  font-size: 12px;
  background: var(--surface-2);
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

.admin-shell-icon-button,
.admin-shell-user-button {
  color: var(--text-secondary) !important;
}

.admin-shell-icon-button {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  padding: 0 !important;
  border-radius: 9px;
}

.admin-shell-icon-button:hover,
.admin-shell-user-button:hover {
  color: var(--text-primary) !important;
  background: var(--control-bg) !important;
}

.admin-shell-user-button {
  display: inline-flex !important;
  gap: 8px;
  align-items: center;
  height: 38px;
  padding: 0 4px 0 8px !important;
}

.admin-shell-notice-button {
  position: relative;
}

.admin-shell-notice-button::after {
  position: absolute;
  top: 6px;
  right: 7px;
  width: 7px;
  height: 7px;
  content: '';
  background: #1677ff;
  border: 1px solid var(--shell-surface);
  border-radius: 999px;
}

.admin-shell-user-avatar {
  color: #fff;
  background: linear-gradient(135deg, #f59e0b, #ec4899, #22c55e);
}

.admin-shell-tabs {
  display: flex;
  flex: 0 0 40px;
  min-width: 0;
  height: 40px;
  background: var(--shell-surface);
  border-bottom: 1px solid var(--surface-border);
}

.admin-shell-tabs-scroll {
  flex: 1 1 auto;
  gap: 6px;
  min-width: 0;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 5px 8px;
}

.admin-shell-tab-prefix {
  display: inline-flex;
  flex: 0 0 34px;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  font-size: 20px;
  border-right: 1px solid var(--surface-border);
}

.admin-shell-tab {
  display: inline-flex;
  flex: 0 0 auto;
  gap: 8px;
  align-items: center;
  height: 29px;
  padding: 0 12px;
  color: var(--text-secondary);
  font: inherit;
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 9px;
}

.admin-shell-tab:hover,
.admin-shell-tab--active {
  color: var(--text-primary);
  background: var(--control-bg);
  border-color: var(--surface-border);
}

.admin-shell-tab-close {
  color: var(--text-tertiary);
  font-size: 11px;
}

.admin-shell-tab-actions {
  flex: 0 0 auto;
  gap: 4px;
  padding: 4px 8px;
  border-left: 1px solid var(--surface-border);
}

.admin-shell-tab-menu,
.admin-shell-user-panel {
  min-width: 236px;
  overflow: hidden;
  color: var(--text-primary);
  background: var(--surface-1);
  border: 1px solid var(--surface-border);
  border-radius: 10px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
}

.admin-shell-tab-menu {
  padding: 6px 0;
}

.admin-shell-tab-menu-item,
.admin-shell-user-menu-item {
  display: flex;
  gap: 10px;
  align-items: center;
  width: 100%;
  min-height: 38px;
  padding: 0 14px;
  color: var(--text-primary);
  font: inherit;
  font-size: 14px;
  font-weight: 750;
  text-align: left;
  cursor: pointer;
  background: transparent;
  border: 0;
}

.admin-shell-tab-menu-item:hover,
.admin-shell-user-menu-item:hover {
  background: var(--control-bg);
}

.admin-shell-tab-menu-item:disabled {
  color: var(--text-tertiary);
  cursor: not-allowed;
  background: transparent;
}

.admin-shell-tab-menu-icon,
.admin-shell-user-menu-icon {
  display: inline-flex;
  flex: 0 0 18px;
  justify-content: center;
  color: var(--text-secondary);
  font-weight: 850;
}

.admin-shell-tab-menu-divider,
.admin-shell-user-panel-divider {
  height: 1px;
  margin: 4px 0;
  background: var(--surface-border);
}

.admin-shell-user-panel {
  min-width: 304px;
  max-width: min(304px, calc(100vw - 24px));
}

.admin-shell-user-profile {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid var(--surface-border);
}

.admin-shell-user-avatar--large {
  flex: 0 0 auto;
}

.admin-shell-user-meta {
  min-width: 0;
}

.admin-shell-user-title {
  display: flex;
  gap: 10px;
  align-items: center;
}

.admin-shell-user-title strong {
  font-size: 17px;
}

.admin-shell-user-title span {
  padding: 2px 10px;
  color: #7ee2a8;
  font-size: 13px;
  font-weight: 850;
  background: rgba(34, 197, 94, 0.12);
  border-radius: 999px;
}

.admin-shell-user-meta p {
  margin: 6px 0 0;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 650;
}

.admin-shell-user-menu-item kbd {
  margin-left: auto;
  color: var(--text-tertiary);
  font-size: 12px;
}

.admin-shell-search-list {
  display: grid;
  gap: 6px;
  margin-top: 14px;
}

.admin-shell-search-item {
  display: flex;
  gap: 10px;
  align-items: center;
  width: 100%;
  padding: 12px 14px !important;
  color: var(--text-primary);
  font: inherit;
  font-weight: 750;
  text-align: left;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 8px;
}

.admin-shell-search-item:hover {
  background: var(--control-bg);
}

.admin-shell-content {
  flex: 1 1 auto;
  min-width: 0;
  min-height: 0;
  overflow: auto;
  padding: 16px 18px;
  background: var(--page-bg);
}

.admin-shell-content-inner {
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
  max-width: none;
}

:global(.admin-shell-tab-dropdown),
:global(.admin-shell-user-dropdown) {
  max-width: calc(100vw - 24px);
}

.admin-shell-mobile-trigger {
  display: none !important;
}

.admin-shell-mobile-menu {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.admin-shell-brand--mobile {
  flex: 0 0 56px;
  padding: 0 4px 16px;
  border-bottom: 0;
}

:global(.admin-shell-mobile-drawer .ant-drawer-body) {
  height: 100%;
  padding: 0;
  overflow: hidden;
  background: var(--shell-surface);
}

@media (max-width: 1199px) {
  .admin-shell-sider,
  .admin-shell-desktop-trigger,
  .admin-shell-user-name,
  .admin-shell-search,
  .admin-shell-header-right .admin-shell-icon-button[aria-label='语言'] {
    display: none !important;
  }

  .admin-shell-mobile-trigger {
    display: inline-flex !important;
  }

  .admin-shell-content {
    padding: 12px;
  }
}
</style>
