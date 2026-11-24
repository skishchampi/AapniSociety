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

export interface WorkerProfile {
  id: number
  display_name: string
  languages: string[]
  service_categories: number[]
  localities_served: number[]
  availability: Record<string, unknown>
  default_rate_floor: string | null
  contact_visibility: 'private' | 'coop'
  created_at: string
  updated_at: string
}

export interface HouseholdProfile {
  id: number
  display_name: string
  building: number | null
  unit: number | null
  discoverable_to_coop: boolean
  created_at: string
  updated_at: string
}

export interface ServiceCategory {
  id: number
  key: string
  label: string
  is_active: boolean
}

export interface MembershipRequest {
  id: number
  role_sought: 'worker' | 'household'
  status: 'pending' | 'approved' | 'rejected'
  rejection_reason: string
  created_at: string
  reviewed_at: string | null
}

export interface ServiceNeed {
  id: number
  household: number
  category: number
  title: string
  details: string
  locality: number | null
  offered_rate: string | null
  matched_worker: number | null
  below_floor?: boolean | null
  status: 'open' | 'matched' | 'closed'
  created_at: string
  updated_at: string
}

export const profileApi = {
  getWorker: () => api<WorkerProfile>('/me/worker-profile/'),
  getHousehold: () => api<HouseholdProfile>('/me/household-profile/'),
  // PATCH, not PUT: a full PUT would reset fields the caller left out.
  updateWorker: (data: Partial<WorkerProfile>) =>
    api<WorkerProfile>('/me/worker-profile/', { method: 'PATCH', body: data }),
  updateHousehold: (data: Partial<HouseholdProfile>) =>
    api<HouseholdProfile>('/me/household-profile/', { method: 'PATCH', body: data }),
}

export const membersApi = {
  categories: () => api<ServiceCategory[]>('/service-categories/', { auth: false }),
  myMembershipRequests: () => api<MembershipRequest[]>('/membership/requests/mine/'),
  requestMembership: (role_sought: 'worker' | 'household') =>
    api<MembershipRequest>('/membership/request/', { method: 'POST', body: { role_sought } }),
  membershipQueue: () => api<MembershipRequest[]>('/membership/queue/'),
  reviewMembership: (id: number, action: 'approve' | 'reject', reason = '') =>
    api<MembershipRequest>(`/membership/requests/${id}/review/`, {
      method: 'POST',
      body: { action, reason },
    }),
  needs: () => api<ServiceNeed[]>('/needs/'),
  createNeed: (data: {
    category: number
    title: string
    details?: string
    offered_rate?: string
  }) => api<ServiceNeed>('/needs/', { method: 'POST', body: data }),
}

export interface Locality {
  id: number
  name: string
  slug: string
  city: number
}

export const geoApi = {
  localities: () => api<Locality[]>('/localities/', { auth: false }),
}

export interface SharedReference {
  id: number
  body: string
  created_at: string
}

export interface Introduction {
  id: number
  status: 'requested' | 'routed' | 'accepted' | 'declined' | 'withdrawn'
  category: number | null
  worker: number
  household: number
  worker_name: string
  household_name: string
  offered_rate?: string | null
  below_floor?: boolean | null
  shared_references?: SharedReference[]
  note: string
  created_at: string
}

export interface IntroductionEvent {
  id: number
  what: string
  detail: string
  created_at: string
}

export const introductionsApi = {
  create: (data: { worker: number; note?: string; offered_rate?: string }) =>
    api<Introduction>('/introductions/', { method: 'POST', body: data }),
  mine: () => api<Introduction[]>('/introductions/mine/'),
  route: (id: number) =>
    api<{ id: number; status: string }>(
      `/moderation/introductions/${id}/route/`,
      { method: 'POST' },
    ),
  decide: (id: number, action: 'accept' | 'decline') =>
    api<{ id: number; status: string }>(`/introductions/${id}/${action}/`, {
      method: 'POST',
    }),
  withdraw: (id: number) =>
    api<{ id: number; status: string }>(`/introductions/${id}/withdraw/`, {
      method: 'POST',
    }),
  revealContact: (id: number) =>
    api<{ revealed: boolean; phone: string; email: string | null }>(
      `/introductions/${id}/reveal-contact/`,
      { method: 'POST' },
    ),
  events: (id: number) => api<IntroductionEvent[]>(`/introductions/${id}/events/`),
}

export type ReferenceVisibility = 'private' | 'coop' | 'shared'

export interface WorkerReference {
  id: number
  introduction: number
  body: string
  rating: number | null
  visibility: ReferenceVisibility
  created_at: string
  updated_at: string
}

export interface ReferenceRequest {
  id: number
  worker: number
  household: number
  introduction: number | null
  status: 'pending' | 'written' | 'declined' | 'expired'
  created_at: string
  updated_at: string
}

export interface CategoryBargainingRow {
  category_id: number
  category_label: string
  worker_count: number
  avg_rate_floor: string | null
  min_rate_floor: string | null
  max_rate_floor: string | null
  need_count: number
  avg_offered_rate: string | null
  below_floor_count: number
}

export interface LocalityBargainingRow {
  locality_id: number
  locality_name: string
  worker_count: number
  need_count: number
  avg_offered_rate: string | null
}

export interface BargainingSummary {
  by_category: CategoryBargainingRow[]
  by_locality: LocalityBargainingRow[]
}

export const referencesApi = {
  mine: () => api<WorkerReference[]>('/me/references/'),
  create: (data: { introduction: number; body: string }) =>
    api<WorkerReference>('/references/', { method: 'POST', body: data }),
  setVisibility: (id: number, visibility: ReferenceVisibility) =>
    api<WorkerReference>(`/references/${id}/visibility/`, {
      method: 'PATCH',
      body: { visibility },
    }),
  listRequests: () => api<ReferenceRequest[]>('/reference-requests/'),
  createRequest: (data: { household: number; introduction?: number }) =>
    api<ReferenceRequest>('/reference-requests/', { method: 'POST', body: data }),
  bargainingSummary: () => api<BargainingSummary>('/moderation/bargaining-summary/'),
}

export interface WorkerBlock {
  id: number
  worker: number
  household: number
  reason: string
  created_at: string
}

export type AbuseCategory =
  | 'harassment'
  | 'non_payment'
  | 'caste_abuse'
  | 'communal_abuse'
  | 'coercion'
  | 'stalking'
  | 'unsafe_conduct'

export interface AbuseReport {
  id: number
  reported_household: number | null
  introduction: number | null
  category: AbuseCategory
  details: string
  status: 'open' | 'reviewing' | 'resolved' | 'dismissed'
  resolution_note: string
  reviewed_at: string | null
  created_at: string
  updated_at: string
}

export type SafetyNoteType =
  | 'transit_reliability'
  | 'night_route_risk'
  | 'hostile_institution'
  | 'police_or_official_warning'
  | 'non_payment_pattern'
  | 'unsafe_building_or_household'

export type EvidenceLevel = 'firsthand' | 'secondhand'

export interface SafetyNote {
  id: number
  locality: number | null
  building: number | null
  note_type: SafetyNoteType
  evidence_level: EvidenceLevel
  body: string
  created_at: string
  updated_at: string
}

export interface AdminAuditLog {
  id: number
  actor: number | null
  action: string
  target_type: string
  target_id: number
  detail: string
  created_at: string
}

export const safetyApi = {
  blocks: () => api<WorkerBlock[]>('/blocks/'),
  createBlock: (data: { household: number; reason?: string }) =>
    api<WorkerBlock>('/blocks/', { method: 'POST', body: data }),
  deleteBlock: (id: number) => api<void>(`/blocks/${id}/`, { method: 'DELETE' }),
  reports: () => api<AbuseReport[]>('/reports/'),
  createReport: (data: {
    reported_household?: number
    introduction?: number
    category: AbuseCategory
    details: string
  }) => api<AbuseReport>('/reports/', { method: 'POST', body: data }),
  resolveReport: (
    id: number,
    status: 'reviewing' | 'resolved' | 'dismissed',
    resolution_note = '',
  ) =>
    api<AbuseReport>(`/moderation/reports/${id}/resolve/`, {
      method: 'POST',
      body: { status, resolution_note },
    }),
  safetyNotes: () => api<SafetyNote[]>('/safety-notes/'),
  createSafetyNote: (data: {
    locality?: number
    building?: number
    note_type: SafetyNoteType
    evidence_level: EvidenceLevel
    body: string
  }) => api<SafetyNote>('/safety-notes/', { method: 'POST', body: data }),
  auditLog: () => api<AdminAuditLog[]>('/moderation/audit-log/'),
}
