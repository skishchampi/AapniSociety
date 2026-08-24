import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider'
import { tokens } from '../api/client'
import { Needs } from './Needs'

const USER = {
  id: 2,
  phone: '+919****0002',
  email: null,
  full_name: 'Household Test',
  primary_role: 'household',
  is_staff: false,
  date_joined: '2026-08-24T00:00:00Z',
  has_worker_profile: false,
  has_household_profile: true,
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

function renderNeeds() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Needs />
      </AuthProvider>
    </MemoryRouter>,
  )
}

test('household sees the post form and its needs list', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const url = reqUrl(input)
    if (url.endsWith('/api/v1/me/')) return json(USER)
    if (url.includes('/service-categories')) {
      return json([{ id: 7, key: 'maid', label: 'Maid', is_active: true }])
    }
    if (url.includes('/needs')) {
      return json([
        {
          id: 3,
          household: 1,
          category: 7,
          title: 'Evening cook',
          details: '',
          locality: null,
          status: 'open',
          created_at: '2026-08-24T00:00:00Z',
          updated_at: '2026-08-24T00:00:00Z',
        },
      ])
    }
    throw new Error(`unhandled ${url}`)
  })

  renderNeeds()
  expect(await screen.findByRole('heading', { name: /service needs/i })).toBeInTheDocument()
  expect(await screen.findByText(/evening cook/i)).toBeInTheDocument()
})

test('posting a need sends category and title', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = reqUrl(input)
    const method = init?.method ?? 'GET'
    if (url.endsWith('/api/v1/me/') && method === 'GET') return json(USER)
    if (url.includes('/service-categories')) {
      return json([{ id: 7, key: 'maid', label: 'Maid', is_active: true }])
    }
    if (url.includes('/needs') && method === 'GET') return json([])
    if (url.includes('/needs') && method === 'POST') {
      return json({
        id: 9,
        household: 1,
        category: 7,
        title: 'Morning help',
        details: '',
        locality: null,
        status: 'open',
        created_at: '',
        updated_at: '',
      })
    }
    throw new Error(`unhandled ${method} ${url}`)
  })

  const user = userEvent.setup()
  renderNeeds()

  await waitFor(() => expect(screen.getByRole('button', { name: /post need/i })).toBeEnabled())
  await user.type(screen.getByPlaceholderText(/morning help/i), 'Morning help')
  await user.click(screen.getByRole('button', { name: /post need/i }))

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(([url, init]) => {
        const u = reqUrl(url)
        const m = init?.method ?? 'GET'
        if (!(u.includes('/needs') && m === 'POST')) return false
        const body = JSON.parse(String(init?.body)) as { category: number; title: string }
        return body.category === 7 && body.title === 'Morning help'
      }),
    ).toBe(true),
  )
})
