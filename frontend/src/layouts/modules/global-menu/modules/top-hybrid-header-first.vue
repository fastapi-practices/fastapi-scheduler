<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { SimpleScrollbar } from '@sa/materials';
import type { RouteKey } from '@elegant-router/types';
import { GLOBAL_HEADER_MENU_ID, GLOBAL_SIDER_MENU_ID } from '@/constants/app';
import { useAppStore } from '@/store/modules/app';
import { useRouteStore } from '@/store/modules/route';
import { useRouterPush } from '@/hooks/common/router';
import { useMenu, useMixMenuContext } from '../context';

defineOptions({
  name: 'TopHybridHeaderFirst'
});

const route = useRoute();
const appStore = useAppStore();
const routeStore = useRouteStore();
const { routerPushByKeyWithMetaQuery } = useRouterPush();
const {
  firstLevelMenus,
  secondLevelMenus,
  activeFirstLevelMenuKey,
  handleSelectFirstLevelMenu,
  activeDeepestLevelMenuKey
} = useMixMenuContext('TopHybridHeaderFirst');
const { selectedKey } = useMenu();

const expandedKeys = ref<string[]>([]);

/**
 * Handle first level menu select
 * @param key RouteKey
 */
function handleSelectMenu(key: RouteKey) {
  handleSelectFirstLevelMenu(key);

  // if there are second level menus, select the deepest one by default
  activeDeepestLevelMenuKey();
}

function handleFirstMenuClick({ key }: { key: string | number }) {
  handleSelectMenu(key as RouteKey);
}

function handleRouteMenuClick({ key }: { key: string | number }) {
  routerPushByKeyWithMetaQuery(key as RouteKey);
}

function updateExpandedKeys() {
  if (appStore.siderCollapse || !selectedKey.value) {
    expandedKeys.value = [];
    return;
  }
  expandedKeys.value = routeStore.getSelectedMenuKeyPath(selectedKey.value);
}

watch(
  () => route.name,
  () => {
    updateExpandedKeys();
  },
  { immediate: true }
);
</script>

<template>
  <Teleport :to="`#${GLOBAL_HEADER_MENU_ID}`">
    <AMenu
      mode="horizontal"
      :selected-keys="activeFirstLevelMenuKey ? [activeFirstLevelMenuKey] : []"
      :items="firstLevelMenus"
      :inline-indent="18"
      @click="handleFirstMenuClick"
    />
  </Teleport>
  <Teleport :to="`#${GLOBAL_SIDER_MENU_ID}`">
    <SimpleScrollbar>
      <AMenu
        v-model:open-keys="expandedKeys"
        mode="inline"
        :selected-keys="selectedKey ? [selectedKey] : []"
        :inline-collapsed="appStore.siderCollapse"
        :items="secondLevelMenus"
        :inline-indent="18"
        @click="handleRouteMenuClick"
      />
    </SimpleScrollbar>
  </Teleport>
</template>

<style scoped></style>
