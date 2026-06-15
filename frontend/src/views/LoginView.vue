<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { DatabaseOutlined, SafetyCertificateOutlined, UserOutlined } from '@antdv-next/icons'

import {
  AdminLoginPage,
  type AdminLoginHighlight,
  type AdminLoginPayload,
} from '../components/admin-kit'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const { captchaEnabled, captchaImage, captchaLoading, loginError, loginLoading } = storeToRefs(authStore)

const loginHighlights: AdminLoginHighlight[] = [
  {
    icon: SafetyCertificateOutlined,
    title: '安全认证入口',
    note: '使用 fba JWT 认证与刷新令牌机制，后台访问统一走后端登录接口。',
  },
  {
    icon: DatabaseOutlined,
    title: '调度数据底座',
    note: '面向任务、执行记录和运行状态扩展后台页面，前端组件保持统一。',
  },
  {
    icon: UserOutlined,
    title: '管理员工作台',
    note: '登录后进入后台壳层，后续可接入用户、任务和配置管理模块。',
  },
]

const handleLogin = async (payload: AdminLoginPayload) => {
  if (await authStore.login(payload)) {
    await router.replace({ name: 'dashboard' })
  }
}

onMounted(() => {
  authStore.loadCaptcha()
})
</script>

<template>
  <AdminLoginPage
    :loading="loginLoading"
    :error-message="loginError"
    :highlights="loginHighlights"
    :captcha-enabled="captchaEnabled"
    :captcha-image="captchaImage"
    :captcha-loading="captchaLoading"
    eyebrow="FastAPI Console"
    brand-title="Scheduler Admin"
    headline="统一管理任务调度"
    headline-strong="运行状态与后台操作"
    description="基于 FastAPI Best Architecture 和 Antdv Next 组件体系构建后台入口，先完成认证闭环，再承载调度管理功能。"
    footnote="初始化测试用户通常为 admin / 123456。生产环境请及时修改默认凭据。"
    form-title="用户登录"
    form-description="请输入管理员账号、密码和验证码。"
    submit-text="进入仪表盘"
    @submit="handleLogin"
    @refresh-captcha="authStore.loadCaptcha"
  />
</template>
