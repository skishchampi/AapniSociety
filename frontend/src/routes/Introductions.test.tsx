import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider'
import { tokens } from '../api/client'
import type { User } from '../api/client'
import { Introductions } from './Introductions'

function makeUser(primary_role: User['primary_role']): User {
  return {
    id: 3,
    phone: '+919****0003',
    email: null,
    full_name: 'Role Test',
    primary_role,
    is_staff: false,
    date_joined: '2026-08-24T00:00:00Z',
    has_worker_profile: primary_role === 'worker',
    has_household_profile: primary_role === 'household',
  }
}

const ROUTED_ROW = {
  id: 11,
  status: 'routed',
  category: null,
  worker: 1,
  household: 2,
  worker_name: 'Asha',
  household_name: 'Sharma household',
  note: 'Two hours daily',
  created_at: '2026-08-24T10:00:00Z',
}

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

test('household files an introduction by worker id', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = reqUrl(input)
    const method = init?.method ?? 'GET'
    if (url.endsWith('/api/v1/me/') && method === 'GET') return json(makeUser('household'))
    if (url.includes('/introductions/mine')) return json([])
    if (url.includes('/introductions') && method === 'POST') {
      return json({ ...ROUTED_ROW, id: 20, status: 'requested', worker_name: '' })
    }
    throw new Error(`unhandled ${method} ${url}`)
  })

  const user = userEvent.setup()
  render(
    <MemoryRouter>
      <AuthProvider>
        <Introductions />
      </AuthProvider>
    </MemoryRouter>,
  )

  await waitFor(() =>
    expect(screen.getByRole('button', { name: /ask for an introduction/i })).toBeEnabled(),
  )
  await user.type(screen.getByPlaceholderText(/e\.g\. 5/i), '5')
  await user.click(screen.getByRole('button', { name: /ask for an introduction/i }))

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(([url, init]) => {
        const u = reqUrl(url)
        const m = init?.method ?? 'GET'
        if (!(u.includes('/introductions') && m === 'POST' && !u.includes('reveal'))) {
          return false
        }
        return (JSON.parse(String(init?.body)) as { worker: number }).worker === 5
      }),
    ).toBe(true),
  )
})

test('worker accepts a routed introduction and reveals contact after', async () => {
  let status = 'routed'
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = reqUrl(input)
    const method = init?.method ?? 'GET'
    if (url.endsWith('/api/v1/me/') && method === 'GET') return json(makeUser('worker'))
    if (url.includes('/introductions/mine')) {
      return json([{ ...ROUTED_ROW, status }])
    }
    if (url.includes('/introductions/11/accept')) {
      status = 'accepted'
      return json({ id: 11, status: 'accepted' })
    }
    if (url.includes('/introductions/11/reveal-contact')) {
      return json({ revealed: true, phone: '+919****0201', email: null })
    }
    throw new Error(`unhandled ${method} ${url}`)
  })

  const user = userEvent.setup()
  render(
    <MemoryRouter>
      <AuthProvider>
        <Introductions />
      </AuthProvider>
    </MemoryRouter>,
  )

  await user.click(await screen.findByRole('button', { name: /accept/i }))
  await waitFor(() => expect(screen.getByText(/accepted\./i)).toBeInTheDocument())

  await user.click(await screen.findByRole('button', { name: /reveal my contact/i }))
  expect(await screen.findByText(/\+919\*\*\*\*0201/)).toBeInTheDocument()

  const acceptCalls = fetchMock.mock.calls.filter(([url]) => reqUrl(url).includes('/accept'))
  expect(acceptCalls.length).toBe(1)
})
