import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider'
import { tokens } from '../api/client'
import { Profile } from './Profile'

const WORKER = {
  id: 5,
  phone: '+919****0005',
  email: null,
  full_name: 'Worker Test',
  primary_role: 'worker',
  is_staff: false,
  date_joined: '2026-08-24T00:00:00Z',
  has_worker_profile: true,
  has_household_profile: false,
}

const PROFILE = {
  id: 1,
  display_name: 'Asha',
  languages: ['gu'],
  service_categories: [1],
  localities_served: [],
  availability: {},
  default_rate_floor: null,
  contact_visibility: 'private',
  created_at: '',
  updated_at: '',
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

test('worker save carries localities and availability', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = reqUrl(input)
    const method = init?.method ?? 'GET'
    if (url.endsWith('/api/v1/me/') && method === 'GET') return json(WORKER)
    if (url.includes('/me/worker-profile') && method === 'GET') return json(PROFILE)
    if (url.includes('/service-categories')) {
      return json([{ id: 1, key: 'maid', label: 'Maid', is_active: true }])
    }
    if (url.includes('/localities')) {
      return json([{ id: 4, name: 'Maninagar', slug: 'maninagar', city: 1 }])
    }
    if (url.includes('/me/worker-profile') && method === 'PATCH') {
      return json({ ...PROFILE, ...JSON.parse(String(init?.body)) })
    }
    throw new Error(`unhandled ${method} ${url}`)
  })

  const user = userEvent.setup()
  render(
    <MemoryRouter>
      <AuthProvider>
        <Profile />
      </AuthProvider>
    </MemoryRouter>,
  )

  const localityBox = await screen.findByRole('checkbox', { name: /maninagar/i })
  await user.click(localityBox)
  const mondayInput = screen.getAllByPlaceholderText(/09:00-13:00/i)[0]
  await user.type(mondayInput, '09:00-13:00')

  await user.click(screen.getByRole('button', { name: /save profile/i }))

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(([url, init]) => {
        const u = reqUrl(url)
        const m = init?.method ?? 'GET'
        if (!(u.includes('/me/worker-profile') && m === 'PATCH')) return false
        const body = JSON.parse(String(init?.body)) as {
          localities_served: number[]
          availability: Record<string, string[]>
        }
        return (
          body.localities_served.includes(4) &&
          Array.isArray(body.availability.mon) &&
          body.availability.mon[0] === '09:00-13:00' &&
          body.availability.tue === undefined
        )
      }),
    ).toBe(true),
  )
  expect(await screen.findByText(/saved/i)).toBeInTheDocument()
})
