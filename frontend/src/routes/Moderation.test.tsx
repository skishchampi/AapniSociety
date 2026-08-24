import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider'
import { tokens } from '../api/client'
import type { User } from '../api/client'
import { Moderation } from './Moderation'

function makeUser(primary_role: User['primary_role']): User {
  return {
    id: 9,
    phone: '+919****0009',
    email: null,
    full_name: 'Mod Test',
    primary_role,
    is_staff: false,
    date_joined: '2026-08-24T00:00:00Z',
    has_worker_profile: false,
    has_household_profile: false,
  }
}

const PENDING = [
  {
    id: 12,
    role_sought: 'worker',
    status: 'pending',
    rejection_reason: '',
    created_at: '2026-08-24T10:00:00Z',
    reviewed_at: null,
  },
]

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function reqUrl(input: RequestInfo | URL): string {
  if (typeof input === 'string') return input
  if (input instanceof URL) return input.href
  return input.url
}

beforeEach(() => {
  localStorage.clear()
  tokens.set('fake-access', 'fake-refresh')
})

afterEach(() => {
  vi.restoreAllMocks()
})

test('moderator can approve a pending request', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = reqUrl(input)
    const method = init?.method ?? 'GET'
    if (url.endsWith('/api/v1/me/') && method === 'GET') return json(makeUser('moderator'))
    if (url.includes('/membership/queue') && method === 'GET') return json(PENDING)
    if (url.includes('/membership/requests/12/review') && method === 'POST') {
      return json({ ...PENDING[0], status: 'approved', reviewed_at: '2026-08-24T11:00:00Z' })
    }
    if (url.includes('/membership/queue')) return json([])
    throw new Error(`unhandled ${method} ${url}`)
  })

  const user = userEvent.setup()
  render(
    <MemoryRouter>
      <AuthProvider>
        <Moderation />
      </AuthProvider>
    </MemoryRouter>,
  )

  expect(await screen.findByRole('heading', { name: /membership queue/i })).toBeInTheDocument()
  await user.click(await screen.findByRole('button', { name: /approve/i }))

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(([url, init]) => {
        const u = reqUrl(url)
        const m = init?.method ?? 'GET'
        if (!(u.includes('/membership/requests/12/review') && m === 'POST')) return false
        return (JSON.parse(String(init?.body)) as { action: string }).action === 'approve'
      }),
    ).toBe(true),
  )
})

test('non-moderators are sent away', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const url = reqUrl(input)
    if (url.endsWith('/api/v1/me/')) return json(makeUser('household'))
    throw new Error(`unhandled ${url}`)
  })

  render(
    <MemoryRouter>
      <AuthProvider>
        <Moderation />
      </AuthProvider>
    </MemoryRouter>,
  )

  await waitFor(() => expect(screen.queryByText(/membership queue/i)).not.toBeInTheDocument())
})
