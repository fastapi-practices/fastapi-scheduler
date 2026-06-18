<script setup lang="ts">
import type { RouteKey } from '@elegant-router/types';
import { GLOBAL_HEADER_MENU_ID } from '@/constants/app';
import { useRouteStore } from '@/store/modules/route';
import { useRouterPush } from '@/hooks/common/router';
import { useMenu } from '../context';

defineOptions({
  name: 'HorizontalMenu'
});

const routeStore = useRouteStore();
const { routerPushByKeyWithMetaQuery } = useRouterPush();
const { selectedKey } = useMenu();

function handleMenuClick({ key }: { key: string | number }) {
  routerPushByKeyWithMetaQuery(key as RouteKey);
}
</script>

<template>
  <Teleport :to="`#${GLOBAL_HEADER_MENU_ID}`">
    <AMenu
      mode="horizontal"
      :selected-keys="selectedKey ? [selectedKey] : []"
      :items="routeStore.menus"
      :inline-indent="18"
      @click="handleMenuClick"
    />
  </Teleport>
</template>

<style scoped></style>
