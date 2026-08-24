import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider'
import { tokens } from '../api/client'
import { Membership } from './Membership'

const USER = {
  id: 1,
  phone: '+919****0001',
  email: null,
  full_name: 'Test',
  primary_role: 'household',
  is_staff: false,
  date_joined: '2026-08-24T00:00:00Z',
  has_worker_profile: false,
  has_household_profile: false,
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

test('sends a membership request as worker', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = reqUrl(input)
    const method = init?.method ?? 'GET'
    if (url.endsWith('/api/v1/me/') && method === 'GET') return json(USER)
    if (url.includes('/membership/requests/mine')) return json([])
    if (url.includes('/membership/request') && method === 'POST') {
      return json({ id: 1, role_sought: 'worker', status: 'pending', rejection_reason: '', created_at: '', reviewed_at: null })
    }
    throw new Error(`unhandled ${method} ${url}`)
  })

  const user = userEvent.setup()
  render(
    <MemoryRouter>
      <AuthProvider>
        <Membership />
      </AuthProvider>
    </MemoryRouter>,
  )

  await waitFor(() => expect(screen.getByRole('button', { name: /send request/i })).toBeEnabled())
  await user.click(screen.getByRole('button', { name: /send request/i }))

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(([url, init]) => {
        const u = reqUrl(url)
        const m = init?.method ?? 'GET'
        if (!(u.includes('/membership/request') && m === 'POST')) return false
        return (JSON.parse(String(init?.body)) as { role_sought: string }).role_sought === 'worker'
      }),
    ).toBe(true),
  )
  expect(await screen.findByText(/request sent/i)).toBeInTheDocument()
})
