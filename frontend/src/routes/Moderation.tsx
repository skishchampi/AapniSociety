import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { membersApi } from '../api/client'
import type { MembershipRequest } from '../api/client'
import { useAuth } from '../auth/context'

const MODERATOR_ROLES = ['moderator', 'operator', 'admin']

export function Moderation() {
  const { user, refreshUser } = useAuth()
  const [queue, setQueue] = useState<MembershipRequest[] | null>(null)
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busyId, setBusyId] = useState<number | null>(null)

  const allowed = user !== null && MODERATOR_ROLES.includes(user.primary_role)

  useEffect(() => {
    if (!allowed) return
    let alive = true
    membersApi
      .membershipQueue()
      .then((list) => {
        if (alive) setQueue(list)
      })
      .catch(() => {
        if (alive) setQueue([])
      })
    return () => {
      alive = false
    }
  }, [allowed])

  if (user === null || !allowed) return <Navigate to="/" replace />

  async function review(id: number, action: 'approve' | 'reject') {
    setError(null)
    setBusyId(id)
    try {
      await membersApi.reviewMembership(id, action, action === 'reject' ? reason : '')
      setQueue(await membersApi.membershipQueue())
      await refreshUser()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not record the review.')
    } finally {
      setBusyId(null)
    }
  }

  return (
    <main className="container">
      <h1>Membership queue</h1>
      <p className="muted">Approve joins as worker or household. Rejects need a reason.</p>
      <label>
        Rejection reason (used when you press Reject)
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Incomplete verification"
        />
      </label>
      {queue === null && <p className="muted">Loading…</p>}
      {queue !== null && queue.length === 0 && (
        <p className="muted">The queue is empty.</p>
      )}
      <ul>
        {(queue ?? []).map((request) => (
          <li key={request.id}>
            {request.role_sought} — {request.created_at.slice(0, 10)}{' '}
            <button
              disabled={busyId === request.id}
              onClick={() => void review(request.id, 'approve')}
            >
              Approve
            </button>{' '}
            <button
              disabled={busyId === request.id}
              onClick={() => void review(request.id, 'reject')}
            >
              Reject
            </button>
          </li>
        ))}
      </ul>
      {error && <p className="error">{error}</p>}
    </main>
  )
}
