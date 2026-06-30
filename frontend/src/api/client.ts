// Minimal typed API client: bearer auth + one-shot refresh-on-401.
// Token storage uses localStorage for dev simplicity; httponly-cookie hardening
// is a beta.1 security task (see docs/plans/0.1.0-alpha.1-foundations.md §7).

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const ACCESS_KEY = 'as.access'
const REFRESH_KEY = 'as.refresh'

export const tokens = {
  get access() {
    return localStorage.getItem(ACCESS_KEY)
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY)
  },
  set(access: string, refresh: string) {
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  setAccess(access: string) {
    localStorage.setItem(ACCESS_KEY, access)
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

export type Role = 'worker' | 'household' | 'connector' | 'moderator' | 'operator' | 'admin'

export interface User {
  id: number
  phone: string
  email: string | null
  full_name: string
  primary_role: Role
  is_staff: boolean
  date_joined: string
  has_worker_profile: boolean
  has_household_profile: boolean
}

export interface VerifyResponse {
  access: string
  refresh: string
  user: User
  created: boolean
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function tryRefresh(): Promise<boolean> {
  const refresh = tokens.refresh
  if (!refresh) return false
  const res = await fetch(`${API_BASE}/api/v1/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
  if (!res.ok) return false
  const data = (await res.json()) as { access: string; refresh?: string }
  // ROTATE_REFRESH_TOKENS is on server-side: a rotated refresh is returned and
  // the old one is blacklisted, so persist it or the next refresh fails.
  if (data.refresh) tokens.set(data.access, data.refresh)
  else tokens.setAccess(data.access)
  return true
}

interface RequestOpts {
  method?: string
  body?: unknown
  auth?: boolean
}

export async function api<T>(path: string, opts: RequestOpts = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = opts

  const doFetch = () => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (auth && tokens.access) headers.Authorization = `Bearer ${tokens.access}`
    return fetch(`${API_BASE}/api/v1${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  }

  let res = await doFetch()
  if (res.status === 401 && auth && (await tryRefresh())) {
    res = await doFetch()
  }

  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      detail = data.detail ?? JSON.stringify(data)
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, detail)
  }

  if (res.status === 205 || res.status === 204) return undefined as T
  return (await res.json()) as T
}

// ── Endpoint helpers ──────────────────────────────────
export const authApi = {
  requestOtp: (phone: string) =>
    api<{ detail: string; dev_code?: string }>('/auth/otp/request/', {
      method: 'POST',
      body: { phone },
      auth: false,
    }),
  verifyOtp: (phone: string, code: string, primary_role: Role, full_name = '') =>
    api<VerifyResponse>('/auth/otp/verify/', {
      method: 'POST',
      body: { phone, code, primary_role, full_name },
      auth: false,
    }),
  logout: (refresh: string) =>
    api<void>('/auth/logout/', { method: 'POST', body: { refresh } }),
  me: () => api<User>('/me/'),
}

export const profileApi = {
  upsertWorker: (data: Record<string, unknown>) =>
    api('/me/worker-profile/', { method: 'PUT', body: data }),
  upsertHousehold: (data: Record<string, unknown>) =>
    api('/me/household-profile/', { method: 'PUT', body: data }),
}
