import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { message } from 'antdv-next'

import {
  ApiError,
  authApi,
  clearStoredSession,
  getStoredSession,
  setStoredSession,
  type CaptchaDetail,
  type LoginPayload,
  type StoredSession,
} from '../api/auth'
import { getErrorMessage } from '../utils/format'

export const useAuthStore = defineStore('auth', () => {
  const session = ref<StoredSession | null>(getStoredSession())
  const loginLoading = ref(false)
  const loginError = ref('')
  const captcha = ref<CaptchaDetail | null>(null)
  const captchaLoading = ref(false)

  const isAuthenticated = computed(() => Boolean(session.value))
  const userName = computed(() => session.value?.user.nickname || session.value?.user.username || 'admin')
  const captchaEnabled = computed(() => captcha.value?.is_enabled ?? true)
  const captchaImage = computed(() => captcha.value?.image || '')

  const clearSession = () => {
    clearStoredSession()
    session.value = null
  }

  const loadCaptcha = async () => {
    captchaLoading.value = true
    try {
      captcha.value = await authApi.getCaptcha()
    } catch (error) {
      captcha.value = null
      message.error(getErrorMessage(error, '验证码加载失败'))
    } finally {
      captchaLoading.value = false
    }
  }

  const login = async (payload: LoginPayload) => {
    loginLoading.value = true
    loginError.value = ''
    try {
      const loginResponse = await authApi.login({
        username: payload.username,
        password: payload.password,
        captcha: payload.captcha,
        uuid: captcha.value?.uuid,
      })
      session.value = setStoredSession(loginResponse)
      message.success('登录成功')
      if (loginResponse.password_expire_days_remaining !== null && loginResponse.password_expire_days_remaining !== undefined) {
        message.info(`密码将在 ${loginResponse.password_expire_days_remaining} 天后过期`)
      }
      return true
    } catch (error) {
      loginError.value = getErrorMessage(error, '登录失败，请检查账号、密码或验证码')
      if (captchaEnabled.value) {
        await loadCaptcha()
      }
      return false
    } finally {
      loginLoading.value = false
    }
  }

  const logout = async (showMessage = true) => {
    try {
      if (session.value) {
        await authApi.logout()
      }
    } catch (error) {
      if (!(error instanceof ApiError)) {
        message.warning(getErrorMessage(error, '退出登录请求失败'))
      }
    } finally {
      clearSession()
      if (showMessage) message.success('已退出登录')
    }
  }

  return {
    session,
    isAuthenticated,
    userName,
    loginLoading,
    loginError,
    captcha,
    captchaEnabled,
    captchaImage,
    captchaLoading,
    loadCaptcha,
    login,
    logout,
    clearSession,
  }
})
