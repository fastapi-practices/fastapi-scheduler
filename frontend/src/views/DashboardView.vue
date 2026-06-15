<script setup lang="ts">
import { computed, h } from 'vue'
import { storeToRefs } from 'pinia'
import { Tag, TypographyText } from 'antdv-next'
import { CheckCircleOutlined, ClockCircleOutlined } from '@antdv-next/icons'

import { useAuthStore } from '../stores/auth'
import { formatDateTime } from '../utils/format'

const authStore = useAuthStore()
const { session } = storeToRefs(authStore)

const user = computed(() => session.value?.user)
const accountActive = computed(() => user.value?.status === 1)
const accessExpireTime = computed(() => formatDateTime(session.value?.expiresAt))
const lastLoginTime = computed(() => formatDateTime(user.value?.last_login_time))
const apiBase = import.meta.env.VITE_API_BASE || '/api/v1'
const authDescriptionItems = computed(() => [
  { key: 'uuid', label: '用户 UUID', content: user.value?.uuid || '-' },
  { key: 'nickname', label: '昵称', content: user.value?.nickname || '-' },
  {
    key: 'status',
    label: '账号状态',
    content: h(Tag, { color: accountActive.value ? 'success' : 'default' }, () =>
      accountActive.value ? '启用' : '停用',
    ),
  },
  { key: 'is_staff', label: '是否管理员', content: user.value?.is_staff ? '是' : '否' },
  { key: 'is_superuser', label: '是否超级管理员', content: user.value?.is_superuser ? '是' : '否' },
  { key: 'last_login_time', label: '最后登录时间', content: lastLoginTime.value },
  {
    key: 'session_uuid',
    label: '会话 UUID',
    content: h(TypographyText, { code: true }, () => session.value?.sessionUuid || '-'),
  },
])
</script>

<template>
  <div class="dashboard-grid">
    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :md="8">
        <a-card class="dashboard-card" variant="borderless">
          <a-statistic title="登录用户" :value="user?.username || '-'">
            <template #prefix>
              <CheckCircleOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :md="8">
        <a-card class="dashboard-card" variant="borderless">
          <a-statistic title="令牌过期时间" :value="accessExpireTime">
            <template #prefix>
              <ClockCircleOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :md="8">
        <a-card class="dashboard-card" variant="borderless">
          <a-statistic title="API 前缀" :value="apiBase" />
        </a-card>
      </a-col>
    </a-row>

    <a-card title="认证信息" size="small" class="dashboard-info-card">
      <a-descriptions :column="1" bordered size="small" :items="authDescriptionItems" />
    </a-card>
  </div>
</template>

<style scoped>
.dashboard-grid {
  display: grid;
  gap: 16px;
}

.dashboard-card {
  min-height: 124px;
  background: var(--surface-1);
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

.dashboard-info-card {
  overflow: hidden;
  background: var(--surface-1);
  border-color: var(--surface-border);
  border-radius: 6px;
}
</style>
