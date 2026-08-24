import { useEffect, useState } from 'react'
import { membersApi } from '../api/client'
import type { MembershipRequest } from '../api/client'
import { useAuth } from '../auth/context'

function statusLabel(status: MembershipRequest['status']): string {
  if (status === 'pending') return 'Pending review'
  if (status === 'approved') return 'Approved'
  return 'Rejected'
}

export function Membership() {
  const { user, refreshUser } = useAuth()
  const [requests, setRequests] = useState<MembershipRequest[] | null>(null)
  const [roleSought, setRoleSought] = useState<'worker' | 'household'>(
    user?.primary_role === 'worker' ? 'household' : 'worker',
  )
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let alive = true
    membersApi
      .myMembershipRequests()
      .then((list) => {
        if (alive) setRequests(list)
      })
      .catch(() => {
        if (alive) setRequests([])
      })
    return () => {
      alive = false
    }
  }, [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setNotice(null)
    setBusy(true)
    try {
      await membersApi.requestMembership(roleSought)
      setRequests(await membersApi.myMembershipRequests())
      setNotice('Request sent. A cooperative moderator will review it.')
      await refreshUser()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not send the request.')
    } finally {
      setBusy(false)
    }
  }

  const hasPending = (requests ?? []).some((r) => r.status === 'pending')

  return (
    <main className="container">
      <h1>Cooperative membership</h1>
      <form onSubmit={submit}>
        <fieldset>
          <legend>Ask to join as</legend>
          <label>
            <input
              type="radio"
              name="role-sought"
              value="worker"
              checked={roleSought === 'worker'}
              onChange={() => setRoleSought('worker')}
            />
            Worker
          </label>
          <label>
            <input
              type="radio"
              name="role-sought"
              value="household"
              checked={roleSought === 'household'}
              onChange={() => setRoleSought('household')}
            />
            Household
          </label>
        </fieldset>
        <button type="submit" disabled={busy || hasPending}>
          {busy ? 'Sending…' : 'Send request'}
        </button>
      </form>
      {hasPending && (
        <p className="muted">You already have a request waiting for review.</p>
      )}
      {notice && <p className="muted">{notice}</p>}
      {error && <p className="error">{error}</p>}

      <h2>Your requests</h2>
      {requests === null && <p className="muted">Loading…</p>}
      {requests !== null && requests.length === 0 && (
        <p className="muted">No requests yet.</p>
      )}
      <ul>
        {(requests ?? []).map((r) => (
          <li key={r.id}>
            Join as {r.role_sought} — {statusLabel(r.status)}
            {r.status === 'rejected' && r.rejection_reason
              ? `: ${r.rejection_reason}`
              : ''}
          </li>
        ))}
      </ul>
    </main>
  )
}
