import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { membersApi, referencesApi, safetyApi } from '../api/client'
import type {
  AbuseReport,
  AdminAuditLog,
  BargainingSummary,
  MembershipRequest,
} from '../api/client'
import { useAuth } from '../auth/context'

const MODERATOR_ROLES = ['moderator', 'operator', 'admin']

export function Moderation() {
  const { user, refreshUser } = useAuth()
  const [queue, setQueue] = useState<MembershipRequest[] | null>(null)
  const [summary, setSummary] = useState<BargainingSummary | null>(null)
  const [reports, setReports] = useState<AbuseReport[] | null>(null)
  const [auditLogs, setAuditLogs] = useState<AdminAuditLog[] | null>(null)
  const [reason, setReason] = useState('')
  const [resolutionNote, setResolutionNote] = useState('')
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
    referencesApi
      .bargainingSummary()
      .then((data) => {
        if (alive) setSummary(data)
      })
      .catch(() => {
        /* summary is optional in older test mocks */
      })
    safetyApi
      .reports()
      .then((list) => {
        if (alive) setReports(list)
      })
      .catch(() => {
        /* reports optional in older test mocks */
      })
    safetyApi
      .auditLog()
      .then((list) => {
        if (alive) setAuditLogs(list)
      })
      .catch(() => {
        /* audit log optional in older test mocks */
      })
    return () => {
      alive = false
    }
  }, [allowed])

  if (user === null || !allowed) return <Navigate to="/" replace />

  async function resolveReport(id: number, status: 'resolved' | 'dismissed') {
    setError(null)
    setBusyId(id)
    try {
      await safetyApi.resolveReport(id, status, resolutionNote)
      setReports(await safetyApi.reports())
      setAuditLogs(await safetyApi.auditLog())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not update the report.')
    } finally {
      setBusyId(null)
    }
  }

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

      {summary && (
        <section>
          <h2>Cooperative rate and demand summary</h2>
          <p className="muted">
            Aggregate cooperative economics only. Never shown to households.
          </p>
          <h3>By category</h3>
          <ul>
            {summary.by_category.map((row) => (
              <li key={row.category_id}>
                <strong>{row.category_label}</strong>: {row.worker_count} workers
                {row.avg_rate_floor ? ` (avg floor ₹${row.avg_rate_floor})` : ''} ·{' '}
                {row.need_count} needs · {row.below_floor_count} below floor
              </li>
            ))}
          </ul>
          <h3>By locality</h3>
          <ul>
            {summary.by_locality.map((row) => (
              <li key={row.locality_id}>
                <strong>{row.locality_name}</strong>: {row.worker_count} workers ·{' '}
                {row.need_count} needs
              </li>
            ))}
          </ul>
        </section>
      )}

      {reports && (
        <section>
          <h2>Abuse reports</h2>
          <label>
            Resolution note
            <input
              value={resolutionNote}
              onChange={(e) => setResolutionNote(e.target.value)}
              placeholder="Action taken by the cooperative"
            />
          </label>
          {reports.length === 0 && <p className="muted">No reports filed.</p>}
          <ul>
            {reports.map((rep) => (
              <li key={rep.id}>
                <strong>#{rep.id}</strong> [{rep.status}] {rep.category} — {rep.details}
                {rep.status === 'open' && (
                  <>
                    {' '}
                    <button
                      disabled={busyId === rep.id}
                      onClick={() => void resolveReport(rep.id, 'resolved')}
                    >
                      Resolve
                    </button>{' '}
                    <button
                      disabled={busyId === rep.id}
                      onClick={() => void resolveReport(rep.id, 'dismissed')}
                    >
                      Dismiss
                    </button>
                  </>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {auditLogs && (
        <section>
          <h2>Admin audit log</h2>
          {auditLogs.length === 0 && <p className="muted">No actions logged yet.</p>}
          <ul>
            {auditLogs.slice(0, 20).map((entry) => (
              <li key={entry.id}>
                {entry.created_at.slice(0, 16).replace('T', ' ')} — {entry.action} on{' '}
                {entry.target_type} #{entry.target_id}
                {entry.detail ? ` (${entry.detail})` : ''}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  )
}
