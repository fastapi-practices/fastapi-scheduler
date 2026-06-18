<script setup lang="ts">
import { createReusableTemplate } from '@vueuse/core';
import type { RouteKey } from '@elegant-router/types';
import { useThemeStore } from '@/store/modules/theme';
import { useRouteStore } from '@/store/modules/route';
import { useRouterPush } from '@/hooks/common/router';

defineOptions({
  name: 'GlobalBreadcrumb'
});

const themeStore = useThemeStore();
const routeStore = useRouteStore();
const { routerPushByKey } = useRouterPush();

interface BreadcrumbContentProps {
  breadcrumb: App.Global.Menu;
}

const [DefineBreadcrumbContent, BreadcrumbContent] = createReusableTemplate<BreadcrumbContentProps>();

function handleClickMenu(key: RouteKey) {
  routerPushByKey(key);
}

function handleMenuClick({ key }: { key: string | number }) {
  handleClickMenu(key as RouteKey);
}
</script>

<template>
  <ABreadcrumb v-if="themeStore.header.breadcrumb.visible">
    <!-- define component start: BreadcrumbContent -->
    <DefineBreadcrumbContent v-slot="{ breadcrumb }">
      <div class="i-flex-y-center align-middle">
        <component :is="breadcrumb.icon" v-if="themeStore.header.breadcrumb.showIcon" class="mr-4px text-icon" />
        {{ breadcrumb.label }}
      </div>
    </DefineBreadcrumbContent>
    <!-- define component end: BreadcrumbContent -->

    <ABreadcrumbItem v-for="item in routeStore.breadcrumbs" :key="item.key">
      <ADropdown v-if="item.options?.length" :menu="{ items: item.options, onClick: handleMenuClick }">
        <BreadcrumbContent :breadcrumb="item" />
      </ADropdown>
      <BreadcrumbContent v-else :breadcrumb="item" />
    </ABreadcrumbItem>
  </ABreadcrumb>
</template>

<style scoped></style>
