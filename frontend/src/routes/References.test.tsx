import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { referencesApi } from '../api/client'
import type { ReferenceRequest, WorkerReference } from '../api/client'
import { AuthContext } from '../auth/context'
import { References } from './References'

function renderAs(role: 'worker' | 'household') {
  return render(
    <AuthContext.Provider
      value={{
        user: {
          id: 1,
          phone: '+919876543210',
          email: null,
          full_name: role === 'worker' ? 'Meera' : 'Patel Family',
          primary_role: role,
          is_staff: false,
          date_joined: '2026-08-24T00:00:00Z',
          has_worker_profile: role === 'worker',
          has_household_profile: role === 'household',
        },
        loading: false,
        signIn: vi.fn(),
        refreshUser: vi.fn(),
        signOut: vi.fn(),
      }}
    >
      <MemoryRouter>
        <References />
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('References', () => {
  it('worker toggles reference visibility from private to shared', async () => {
    const ref: WorkerReference = {
      id: 7,
      introduction: 3,
      body: 'Punctual and thorough.',
      rating: null,
      visibility: 'private',
      created_at: '2026-08-24T00:00:00Z',
      updated_at: '2026-08-24T00:00:00Z',
    }
    vi.spyOn(referencesApi, 'mine').mockResolvedValue([ref])
    vi.spyOn(referencesApi, 'listRequests').mockResolvedValue([])
    const setVis = vi
      .spyOn(referencesApi, 'setVisibility')
      .mockResolvedValue({ ...ref, visibility: 'shared' })

    renderAs('worker')

    const select = await screen.findByLabelText('Visibility for reference 7')
    await userEvent.selectOptions(select, 'shared')

    await waitFor(() => {
      expect(setVis).toHaveBeenCalledWith(7, 'shared')
    })
    expect(await screen.findByText('Visibility set to shared.')).toBeInTheDocument()
  })

  it('household writes a reference for an accepted introduction', async () => {
    const pendingReq: ReferenceRequest = {
      id: 2,
      worker: 5,
      household: 9,
      introduction: 11,
      status: 'pending',
      created_at: '2026-08-24T00:00:00Z',
      updated_at: '2026-08-24T00:00:00Z',
    }
    vi.spyOn(referencesApi, 'listRequests').mockResolvedValue([pendingReq])
    const createRef = vi.spyOn(referencesApi, 'create').mockResolvedValue({
      id: 1,
      introduction: 11,
      body: 'Dependable cook.',
      rating: null,
      visibility: 'private',
      created_at: '2026-08-24T00:00:00Z',
      updated_at: '2026-08-24T00:00:00Z',
    })

    renderAs('household')

    await userEvent.type(screen.getByLabelText('Accepted introduction ID'), '11')
    await userEvent.type(screen.getByLabelText('Reference note'), 'Dependable cook.')
    await userEvent.click(screen.getByRole('button', { name: 'Save reference' }))

    await waitFor(() => {
      expect(createRef).toHaveBeenCalledWith({ introduction: 11, body: 'Dependable cook.' })
    })
    expect(
      await screen.findByText('Reference saved. The worker controls its visibility.'),
    ).toBeInTheDocument()
  })
})
