export interface ApiEnvelope<T> {
  code: number
  msg: string
  data: T
}

export interface CaptchaDetail {
  is_enabled: boolean
  expire_seconds: number
  uuid: string
  image: string
}

export interface UserInfo {
  id: number | string
  uuid: string
  username: string
  nickname: string
  avatar?: string | null
  email?: string | null
  phone?: string | null
  status: number
  is_superuser: boolean
  is_staff: boolean
  is_multi_login: boolean
  join_time: string
  last_login_time?: string | null
}

export interface LoginResponse {
  access_token: string
  access_token_expire_time: string
  session_uuid: string
  password_expire_days_remaining?: number | null
  user: UserInfo
}

export interface LoginPayload {
  username: string
  password: string
  uuid?: string
  captcha?: string
}

export interface StoredSession {
  token: string
  expiresAt: string
  sessionUuid: string
  user: UserInfo
}

export class ApiError extends Error {
  readonly status: number
  readonly code?: number

  constructor(message: string, status: number, code?: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1'
const SESSION_KEY = 'fastapi-scheduler.session'

const getExpireTime = (value: string) => new Date(value.replace(' ', 'T')).getTime()

const normalizeCaptchaImage = (image: string) => {
  if (!image || image.startsWith('data:')) return image
  return `data:image/png;base64,${image}`
}

export const clearStoredSession = () => {
  window.localStorage.removeItem(SESSION_KEY)
}

export const getStoredSession = (): StoredSession | null => {
  const raw = window.localStorage.getItem(SESSION_KEY)
  if (!raw) return null
  try {
    const session = JSON.parse(raw) as StoredSession
    if (!session.token || getExpireTime(session.expiresAt) <= Date.now()) {
      clearStoredSession()
      return null
    }
    return session
  } catch {
    clearStoredSession()
    return null
  }
}

export const setStoredSession = (login: LoginResponse) => {
  const session: StoredSession = {
    token: login.access_token,
    expiresAt: login.access_token_expire_time,
    sessionUuid: login.session_uuid,
    user: login.user,
  }
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session))
  return session
}

const getSessionToken = () => getStoredSession()?.token || ''

const buildHeaders = (init: RequestInit) => {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (typeof init.body === 'string') {
    headers.set('Content-Type', 'application/json')
  }
  const token = getSessionToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  return headers
}

const parseEnvelope = async <T>(response: Response): Promise<ApiEnvelope<T>> => {
  try {
    return (await response.json()) as ApiEnvelope<T>
  } catch {
    throw new ApiError(response.statusText || '响应格式错误', response.status)
  }
}

export const request = async <T>(path: string, init: RequestInit = {}): Promise<T> => {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...init,
    headers: buildHeaders(init),
  })
  const envelope = await parseEnvelope<T>(response)
  if (!response.ok || envelope.code !== 200) {
    throw new ApiError(envelope.msg || response.statusText || '请求失败', response.status, envelope.code)
  }
  return envelope.data
}

export const authApi = {
  async getCaptcha() {
    const data = await request<CaptchaDetail>('/auth/captcha')
    return {
      ...data,
      image: normalizeCaptchaImage(data.image),
    }
  },
  login(payload: LoginPayload) {
    return request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  logout() {
    return request<null>('/auth/logout', {
      method: 'POST',
    })
  },
}
