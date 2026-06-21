import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider'
import { SignIn } from './SignIn'

beforeEach(() => {
  localStorage.clear()
})

afterEach(() => {
  vi.restoreAllMocks()
})

function renderSignIn() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <SignIn />
      </AuthProvider>
    </MemoryRouter>,
  )
}

test('renders the phone step', async () => {
  renderSignIn()
  expect(await screen.findByRole('heading', { name: /aapnisociety/i })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /send code/i })).toBeInTheDocument()
})

test('requesting a code advances to the code step and shows the dev code', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify({ detail: 'OTP issued.', dev_code: '123456' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  )
  const user = userEvent.setup()
  renderSignIn()

  await user.type(await screen.findByPlaceholderText('+9199…'), '+919900001234')
  await user.click(screen.getByRole('button', { name: /send code/i }))

  await waitFor(() => expect(screen.getByText(/dev code/i)).toBeInTheDocument())
  expect(screen.getByText('123456')).toBeInTheDocument()
  expect(fetchMock).toHaveBeenCalledOnce()
})
