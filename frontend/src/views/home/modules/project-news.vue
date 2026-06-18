<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

defineOptions({
  name: 'ProjectNews'
});

interface NewsItem {
  id: number;
  content: string;
  time: string;
}

const newses = computed<NewsItem[]>(() => [
  { id: 1, content: $t('page.home.projectNews.desc1'), time: '2021-05-28 22:22:22' },
  { id: 2, content: $t('page.home.projectNews.desc2'), time: '2021-10-27 10:24:54' },
  { id: 3, content: $t('page.home.projectNews.desc3'), time: '2021-10-31 22:43:12' },
  { id: 4, content: $t('page.home.projectNews.desc4'), time: '2021-11-03 20:33:31' },
  { id: 5, content: $t('page.home.projectNews.desc5'), time: '2021-11-07 22:45:32' }
]);
</script>

<template>
  <ACard :title="$t('page.home.projectNews.title')" variant="borderless" size="small" class="card-wrapper">
    <template #extra>
      <a class="text-primary" href="javascript:;">{{ $t('page.home.projectNews.moreNews') }}</a>
    </template>
    <div class="flex-col-stretch">
      <div v-for="item in newses" :key="item.id" class="flex items-center gap-12px border-b border-b-#efeff5 py-10px">
        <SoybeanAvatar class="size-48px!" />
        <div class="min-w-0 flex-1">
          <p class="truncate text-14px text-base-text">{{ item.content }}</p>
          <p class="mt-4px text-12px text-#999">{{ item.time }}</p>
        </div>
      </div>
    </div>
  </ACard>
</template>

<style scoped></style>
