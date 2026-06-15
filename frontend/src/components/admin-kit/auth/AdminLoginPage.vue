<script setup lang="ts">
import type { FormInstance } from 'antdv-next'
import { computed, h, reactive, ref } from 'vue'
import { LockOutlined, ReloadOutlined, SafetyCertificateOutlined, UserOutlined } from '@antdv-next/icons'

import type { AdminLoginHighlight, AdminLoginPayload } from '../types'

const props = withDefaults(
  defineProps<{
    loading?: boolean
    errorMessage?: string
    highlights?: AdminLoginHighlight[]
    eyebrow?: string
    brandTitle?: string
    headline?: string
    headlineStrong?: string
    description?: string
    footnote?: string
    formTitle?: string
    formDescription?: string
    submitText?: string
    captchaEnabled?: boolean
    captchaImage?: string
    captchaLoading?: boolean
    captchaPlaceholder?: string
    captchaRefreshText?: string
  }>(),
  {
    loading: false,
    errorMessage: '',
    highlights: () => [],
    eyebrow: 'Admin Console',
    brandTitle: '管理后台',
    headline: '统一、清晰地管理',
    headlineStrong: '后台系统的关键数据与操作',
    description: '使用标准化登录、导航、搜索、表格和操作反馈，让后台页面保持一致、清楚、容易维护。',
    footnote: '适合需要快速搭建后台管理入口的业务系统。',
    formTitle: '欢迎登录',
    formDescription: '请输入管理员账号和密码。',
    submitText: '进入后台',
    captchaEnabled: false,
    captchaImage: '',
    captchaLoading: false,
    captchaPlaceholder: '请输入验证码',
    captchaRefreshText: '刷新验证码',
  },
)

const emit = defineEmits<{
  submit: [payload: AdminLoginPayload]
  refreshCaptcha: []
}>()

const formState = reactive<AdminLoginPayload>({
  username: '',
  password: '',
  captcha: '',
})
const formRef = ref<FormInstance>()

const rules = computed<Record<string, any[]>>(() => ({
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: ['blur', 'change'],
    },
    { min: 3, message: '用户名至少 3 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: ['blur', 'change'] },
    { min: 6, message: '密码至少 6 个字符', trigger: 'blur' },
  ],
  ...(props.captchaEnabled
    ? {
        captcha: [
          { required: true, message: '请输入验证码', trigger: ['blur', 'change'] },
          { min: 4, message: '验证码至少 4 个字符', trigger: 'blur' },
        ],
      }
    : {}),
}))

const submit = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  emit('submit', {
    username: formState.username.trim(),
    password: formState.password,
    captcha: formState.captcha?.trim(),
  })
}
</script>

<template>
  <a-layout class="vercel-login">
    <main class="vercel-login__stage">
      <section class="vercel-login__story" aria-labelledby="login-headline">
        <div class="vercel-login__brand">
          <a-avatar :size="40" class="vercel-login__mark">
            <template #icon>
              <SafetyCertificateOutlined />
            </template>
          </a-avatar>
          <div>
            <a-typography-text class="vercel-login__eyebrow">
              {{ eyebrow }}
            </a-typography-text>
            <a-typography-title :level="4" class="vercel-login__brand-title">
              {{ brandTitle }}
            </a-typography-title>
          </div>
        </div>

        <div class="vercel-login__hero">
          <h1 id="login-headline" class="vercel-login__headline">
            {{ headline }}
            <span>{{ headlineStrong }}</span>
          </h1>
          <a-typography-paragraph class="vercel-login__description">
            {{ description }}
          </a-typography-paragraph>
        </div>

        <div class="vercel-login__terminal" aria-hidden="true">
          <div class="vercel-login__terminal-bar">
            <span />
            <span />
            <span />
            <strong>license pipeline</strong>
          </div>
          <div class="vercel-login__terminal-body">
            <p><b>$</b> resolve project_license.policy</p>
            <p><i>✓</i> project keys synchronized</p>
            <p><i>✓</i> license payload signed</p>
            <p><i>✓</i> offline verification ready</p>
          </div>
        </div>
      </section>

      <aside class="vercel-login__access" aria-labelledby="login-form-title">
        <section class="vercel-login__card">
          <div class="vercel-login__card-head">
            <div>
              <a-typography-title id="login-form-title" :level="2" class="vercel-login__form-title">
                {{ formTitle }}
              </a-typography-title>
              <a-typography-paragraph class="vercel-login__form-description">
                {{ formDescription }}
              </a-typography-paragraph>
            </div>
            <span class="vercel-login__secure">TLS</span>
          </div>

          <a-form
            ref="formRef"
            :model="formState"
            :rules="rules"
            layout="vertical"
            scroll-to-first-error
            class="vercel-login__form"
            @finish="submit"
          >
            <a-form-item label="用户名" name="username" has-feedback html-for="login-username">
              <a-input
                id="login-username"
                v-model:value="formState.username"
                name="username"
                size="large"
                :prefix="h(UserOutlined)"
                placeholder="请输入用户名"
                autocomplete="username"
              />
            </a-form-item>
            <a-form-item label="密码" name="password" has-feedback html-for="login-password">
              <a-input-password
                id="login-password"
                v-model:value="formState.password"
                name="password"
                size="large"
                :prefix="h(LockOutlined)"
                placeholder="请输入密码"
                autocomplete="current-password"
              />
            </a-form-item>
            <a-form-item
              v-if="captchaEnabled"
              label="验证码"
              name="captcha"
              has-feedback
              html-for="login-captcha"
            >
              <div class="vercel-login__captcha">
                <a-input
                  id="login-captcha"
                  v-model:value="formState.captcha"
                  name="captcha"
                  size="large"
                  :prefix="h(SafetyCertificateOutlined)"
                  :placeholder="captchaPlaceholder"
                  autocomplete="one-time-code"
                  @pressEnter="submit"
                />
                <a-button
                  html-type="button"
                  class="vercel-login__captcha-button"
                  :loading="captchaLoading"
                  :title="captchaRefreshText"
                  :aria-label="captchaRefreshText"
                  @click="emit('refreshCaptcha')"
                >
                  <img
                    v-if="captchaImage && !captchaLoading"
                    class="vercel-login__captcha-image"
                    :src="captchaImage"
                    alt="验证码"
                  >
                  <ReloadOutlined v-else />
                </a-button>
              </div>
            </a-form-item>
            <a-alert
              v-if="errorMessage"
              class="vercel-login__error"
              type="error"
              :message="errorMessage"
              show-icon
            />
            <a-button
              type="primary"
              size="large"
              block
              :loading="loading"
              html-type="submit"
              class="vercel-login__submit"
            >
              {{ submitText }}
            </a-button>
          </a-form>

          <a-typography-paragraph class="vercel-login__footnote">
            {{ footnote }}
          </a-typography-paragraph>
        </section>
      </aside>
    </main>
  </a-layout>
</template>

<style>
.vercel-login {
  --login-bg: #fafafa;
  --login-ink: #050505;
  --login-muted: rgba(5, 5, 5, 0.55);
  --login-line: #e8e8e8;
  --login-line-soft: rgba(5, 5, 5, 0.06);
  --login-panel: #ffffff;
  --login-input: #ffffff;
  --login-button: #050505;
  --login-button-ink: #ffffff;
  --login-focus: rgba(5, 5, 5, 0.08);
  position: relative;
  min-height: 100dvh;
  overflow: hidden;
  color: var(--login-ink);
  background: var(--login-bg);
}

.vercel-login::before {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  content: '';
  background-image:
    linear-gradient(var(--login-line-soft) 1px, transparent 1px),
    linear-gradient(90deg, var(--login-line-soft) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: linear-gradient(90deg, #000 0%, #000 46%, transparent 72%);
}

.vercel-login__stage {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 444px;
  min-height: 100dvh;
}

.vercel-login__story {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: clamp(48px, 6vw, 78px) clamp(42px, 6vw, 72px);
  border-right: 1px solid var(--login-line);
}

.vercel-login__brand {
  display: flex;
  gap: 14px;
  align-items: center;
}

.vercel-login__mark {
  color: #ffffff;
  background: #050505;
}

.vercel-login__eyebrow {
  display: block;
  margin-bottom: 2px;
  color: var(--login-muted);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

.vercel-login__brand-title,
.vercel-login__form-title {
  color: var(--login-ink) !important;
}

.vercel-login__brand-title {
  margin: 0 !important;
  font-size: 19px !important;
  letter-spacing: -0.035em;
}

.vercel-login__hero {
  max-width: 700px;
}

.vercel-login__headline {
  margin: 0;
  color: var(--login-ink);
  font-size: clamp(52px, 6vw, 76px);
  font-weight: 850;
  line-height: 0.98;
  letter-spacing: -0.08em;
  text-wrap: balance;
}

.vercel-login__headline span {
  display: block;
  color: #737373;
}

.vercel-login__description {
  max-width: 560px;
  margin: 20px 0 0 !important;
  color: var(--login-muted) !important;
  font-size: 15px;
  line-height: 1.85 !important;
  text-wrap: pretty;
}

.vercel-login__terminal {
  width: min(100%, 560px);
  background: var(--login-panel);
  border: 1px solid var(--login-line);
}

.vercel-login__terminal-bar {
  display: flex;
  gap: 7px;
  align-items: center;
  height: 39px;
  padding: 0 14px;
  border-bottom: 1px solid var(--login-line);
}

.vercel-login__terminal-bar span {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: rgba(5, 5, 5, 0.18);
}

.vercel-login__terminal-bar span:first-child {
  background: #050505;
}

.vercel-login__terminal-bar strong {
  margin-left: auto;
  color: var(--login-muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.vercel-login__terminal-body {
  padding: 16px 18px 18px;
  color: var(--login-muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  line-height: 1.9;
}

.vercel-login__terminal-body p {
  margin: 0;
}

.vercel-login__terminal-body b,
.vercel-login__terminal-body i {
  color: var(--login-ink);
  font-style: normal;
}

.vercel-login__access {
  display: grid;
  place-items: center;
  padding: clamp(40px, 6vw, 72px);
  background: var(--login-bg);
}

.vercel-login__card {
  width: 100%;
  max-width: 340px;
}

.vercel-login__card-head {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 30px;
}

.vercel-login__form-title {
  margin: 0 !important;
  font-size: 30px !important;
  line-height: 1.12 !important;
  letter-spacing: -0.06em;
}

.vercel-login__form-description {
  margin: 10px 0 0 !important;
  color: var(--login-muted) !important;
  font-size: 14px;
  line-height: 1.7 !important;
}

.vercel-login__secure {
  flex: none;
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 9px;
  color: var(--login-ink);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
  border: 1px solid var(--login-line);
}

.vercel-login__form .ant-form-item {
  margin-bottom: 20px;
}

.vercel-login__form .ant-form-item-label > label {
  color: var(--login-ink);
  font-size: 13px;
  font-weight: 750;
}

.vercel-login__form .ant-input-affix-wrapper {
  min-height: 46px;
  color: var(--login-ink);
  background: var(--login-input);
  border-color: var(--login-line);
  border-radius: 6px;
  box-shadow: none;
}

.vercel-login__form .ant-input-affix-wrapper:hover,
.vercel-login__form .ant-input-affix-wrapper-focused {
  border-color: var(--login-ink);
  box-shadow: 0 0 0 3px var(--login-focus);
}

.vercel-login__form .ant-input-prefix {
  color: var(--login-muted);
}

.vercel-login__captcha {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 132px;
  gap: 10px;
  align-items: stretch;
}

.vercel-login__captcha-button {
  height: 46px;
  padding: 0;
  overflow: hidden;
  line-height: 1;
  background: var(--login-input);
  border-color: var(--login-line);
  border-radius: 6px;
  box-shadow: none;
}

.vercel-login__captcha-button > span {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
}

.vercel-login__captcha-button:hover {
  border-color: var(--login-ink);
}

.vercel-login__captcha-image {
  display: block;
  width: 100%;
  height: 100%;
  padding: 2px 4px;
  object-fit: contain;
  background: #ffffff;
}

.vercel-login__error {
  margin-bottom: 16px;
}

.vercel-login__submit {
  height: 46px;
  margin-top: 2px;
  font-weight: 850;
  letter-spacing: 0.03em;
  color: var(--login-button-ink) !important;
  background: var(--login-button) !important;
  border: 0 !important;
  border-radius: 6px;
  box-shadow: none;
}

.vercel-login__submit:hover {
  opacity: 0.88;
}

.vercel-login__footnote {
  padding-top: 22px;
  margin: 26px 0 0 !important;
  color: var(--login-muted) !important;
  font-size: 12px;
  line-height: 1.76 !important;
  border-top: 1px solid var(--login-line);
}

:root[data-theme='dark'] .vercel-login {
  --login-bg: #050505;
  --login-ink: #fafafa;
  --login-muted: rgba(250, 250, 250, 0.58);
  --login-line: rgba(255, 255, 255, 0.12);
  --login-line-soft: rgba(255, 255, 255, 0.055);
  --login-panel: #0a0a0a;
  --login-input: #0a0a0a;
  --login-button: #fafafa;
  --login-button-ink: #050505;
  --login-focus: rgba(255, 255, 255, 0.12);
}

:root[data-theme='dark'] .vercel-login__mark {
  color: #050505;
  background: #fafafa;
}

:root[data-theme='dark'] .vercel-login__headline span {
  color: rgba(250, 250, 250, 0.58);
}

:root[data-theme='dark'] .vercel-login__terminal-bar span:first-child {
  background: #fafafa;
}

:root[data-theme='dark'] .vercel-login__form .ant-input,
:root[data-theme='dark'] .vercel-login__form .ant-input-password input {
  color: var(--login-ink);
}

@media (max-width: 960px) {
  .vercel-login {
    overflow: auto;
  }

  .vercel-login::before {
    mask-image: linear-gradient(#000, transparent 85%);
  }

  .vercel-login__stage {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .vercel-login__story {
    order: 2;
    gap: 52px;
    min-height: auto;
    border-top: 1px solid var(--login-line);
    border-right: 0;
  }

  .vercel-login__access {
    order: 1;
    min-height: auto;
    padding: 42px 24px;
  }

  .vercel-login__card {
    max-width: 420px;
  }

  .vercel-login__terminal {
    display: none;
  }
}

@media (max-width: 575px) {
  .vercel-login__story {
    gap: 40px;
    padding: 34px 24px 44px;
  }

  .vercel-login__access {
    padding: 36px 24px;
  }

  .vercel-login__headline {
    font-size: clamp(38px, 12vw, 48px);
  }

  .vercel-login__secure {
    display: none;
  }
}
</style>
