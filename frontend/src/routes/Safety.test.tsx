import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { geoApi, safetyApi } from '../api/client'
import { AuthContext } from '../auth/context'
import { Safety } from './Safety'

function renderAs(role: 'worker' | 'household') {
  return render(
    <AuthContext.Provider
      value={{
        user: {
          id: 1,
          phone: '+919876543210',
          email: null,
          full_name: role === 'worker' ? 'Kiran' : 'Shah Family',
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
        <Safety />
      </MemoryRouter>
    </AuthContext.Provider>,
  )
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('Safety', () => {
  it('worker blocks a household and posts a firsthand city safety note', async () => {
    vi.spyOn(safetyApi, 'blocks').mockResolvedValue([])
    vi.spyOn(safetyApi, 'safetyNotes').mockResolvedValue([])
    vi.spyOn(safetyApi, 'reports').mockResolvedValue([])
    vi.spyOn(geoApi, 'localities').mockResolvedValue([])
    const createBlock = vi.spyOn(safetyApi, 'createBlock').mockResolvedValue({
      id: 1,
      worker: 1,
      household: 8,
      reason: 'Unsafe conduct',
      created_at: '2026-08-24T00:00:00Z',
    })
    const createNote = vi.spyOn(safetyApi, 'createSafetyNote').mockResolvedValue({
      id: 2,
      locality: null,
      building: null,
      note_type: 'night_route_risk',
      evidence_level: 'firsthand',
      body: 'Dark lane near gate 2.',
      created_at: '2026-08-24T00:00:00Z',
      updated_at: '2026-08-24T00:00:00Z',
    })

    renderAs('worker')

    await userEvent.type(screen.getByLabelText('Household profile ID to block'), '8')
    await userEvent.click(screen.getByRole('button', { name: 'Block household' }))
    await waitFor(() => {
      expect(createBlock).toHaveBeenCalledWith({ household: 8, reason: undefined })
    })

    await userEvent.type(screen.getByLabelText('Safety note'), 'Dark lane near gate 2.')
    await userEvent.click(screen.getByRole('button', { name: 'Save safety note' }))
    await waitFor(() => {
      expect(createNote).toHaveBeenCalledWith({
        locality: undefined,
        note_type: 'night_route_risk',
        evidence_level: 'firsthand',
        body: 'Dark lane near gate 2.',
      })
    })
  })

  it('household never sees block controls or raw safety notes', async () => {
    const notesSpy = vi.spyOn(safetyApi, 'safetyNotes').mockResolvedValue([])
    const blocksSpy = vi.spyOn(safetyApi, 'blocks').mockResolvedValue([])
    vi.spyOn(safetyApi, 'reports').mockResolvedValue([])

    renderAs('household')

    expect(screen.getByText('File a confidential abuse report')).toBeInTheDocument()
    expect(screen.queryByText('City safety notes')).not.toBeInTheDocument()
    expect(screen.queryByText('Block a household')).not.toBeInTheDocument()
    expect(notesSpy).not.toHaveBeenCalled()
    expect(blocksSpy).not.toHaveBeenCalled()
  })
})
