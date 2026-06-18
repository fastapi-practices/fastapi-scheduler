<script setup lang="ts">
import { computed } from 'vue';
import { useAppStore } from '@/store/modules/app';
import HeaderBanner from './modules/header-banner.vue';
import CardData from './modules/card-data.vue';
import LineChart from './modules/line-chart.vue';
import PieChart from './modules/pie-chart.vue';
import ProjectNews from './modules/project-news.vue';
import CreativityBanner from './modules/creativity-banner.vue';

const appStore = useAppStore();

const gap = computed(() => (appStore.isMobile ? 0 : 16));
</script>

<template>
  <ASpace vertical :size="16">
    <HeaderBanner />
    <CardData />
    <ARow :gutter="[gap, 16]">
      <ACol :xs="24" :sm="24" :md="14">
        <ACard variant="borderless" class="card-wrapper">
          <LineChart />
        </ACard>
      </ACol>
      <ACol :xs="24" :sm="24" :md="10">
        <ACard variant="borderless" class="card-wrapper">
          <PieChart />
        </ACard>
      </ACol>
    </ARow>
    <ARow :gutter="[gap, 16]">
      <ACol :xs="24" :sm="24" :md="14">
        <ProjectNews />
      </ACol>
      <ACol :xs="24" :sm="24" :md="10">
        <CreativityBanner />
      </ACol>
    </ARow>
  </ASpace>
</template>

<style scoped></style>
