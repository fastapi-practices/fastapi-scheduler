<script setup lang="ts">
import { computed } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { useAuthStore } from '@/store/modules/auth';
import { $t } from '@/locales';

defineOptions({
  name: 'HeaderBanner'
});

const appStore = useAppStore();
const authStore = useAuthStore();

const gap = computed(() => (appStore.isMobile ? 0 : 16));

interface StatisticData {
  id: number;
  title: string;
  value: string;
}

const statisticData = computed<StatisticData[]>(() => [
  {
    id: 0,
    title: $t('page.home.projectCount'),
    value: '25'
  },
  {
    id: 1,
    title: $t('page.home.todo'),
    value: '4/16'
  },
  {
    id: 2,
    title: $t('page.home.message'),
    value: '12'
  }
]);
</script>

<template>
  <ACard variant="borderless" class="card-wrapper">
    <ARow :gutter="[gap, 16]">
      <ACol :xs="24" :sm="24" :md="18">
        <div class="flex-y-center">
          <div class="size-72px shrink-0 overflow-hidden rd-1/2">
            <img src="@/assets/imgs/soybean.jpg" class="size-full" />
          </div>
          <div class="pl-12px">
            <h3 class="text-18px font-semibold">
              {{ $t('page.home.greeting', { userName: authStore.userInfo.userName }) }}
            </h3>
            <p class="text-#999 leading-30px">{{ $t('page.home.weatherDesc') }}</p>
          </div>
        </div>
      </ACol>
      <ACol :xs="24" :sm="24" :md="6">
        <ASpace :size="24" class="w-full justify-end">
          <AStatistic v-for="item in statisticData" :key="item.id" class="whitespace-nowrap" v-bind="item" />
        </ASpace>
      </ACol>
    </ARow>
  </ACard>
</template>

<style scoped></style>
