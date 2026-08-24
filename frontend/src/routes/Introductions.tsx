import { useEffect, useState } from 'react'
import { introductionsApi } from '../api/client'
import type { Introduction, IntroductionEvent } from '../api/client'
import { useAuth } from '../auth/context'

const MODERATOR_ROLES = ['moderator', 'operator', 'admin']

function statusLabel(status: Introduction['status']): string {
  const labels: Record<Introduction['status'], string> = {
    requested: 'Awaiting moderator',
    routed: 'Waiting for the worker',
    accepted: 'Accepted',
    declined: 'Declined',
    withdrawn: 'Withdrawn',
  }
  return labels[status]
}

export function Introductions() {
  const { user } = useAuth()
  const [rows, setRows] = useState<Introduction[] | null>(null)
  const [workerId, setWorkerId] = useState('')
  const [note, setNote] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [busyId, setBusyId] = useState<number | null>(null)
  const [revealed, setRevealed] = useState<Record<number, string>>({})
  const [openEvents, setOpenEvents] = useState<Record<number, IntroductionEvent[]>>({})

  const role = user?.primary_role ?? ''
  const isModerator = MODERATOR_ROLES.includes(role)
  const isWorker = role === 'worker'
  const isHousehold = role === 'household'

  async function load() {
    try {
      setRows(await introductionsApi.mine())
    } catch {
      setRows([])
    }
  }

  useEffect(() => {
    let alive = true
    introductionsApi
      .mine()
      .then((list) => {
        if (alive) setRows(list)
      })
      .catch(() => {
        if (alive) setRows([])
      })
    return () => {
      alive = false
    }
  }, [])

  async function run(id: number, action: () => Promise<unknown>, done: string) {
    setError(null)
    setNotice(null)
    setBusyId(id)
    try {
      await action()
      await load()
      setNotice(done)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'That did not go through.')
    } finally {
      setBusyId(null)
    }
  }

  async function file(e: React.FormEvent) {
    e.preventDefault()
    const id = Number(workerId)
    if (!id) {
      setError('Enter a worker profile ID.')
      return
    }
    await run(0, () => introductionsApi.create({ worker: id, note: note || undefined }), 'Request sent to the cooperative.')
    setWorkerId('')
    setNote('')
  }

  async function reveal(id: number) {
    setError(null)
    setBusyId(id)
    try {
      const contact = await introductionsApi.revealContact(id)
      setRevealed((prev) => ({ ...prev, [id]: contact.phone }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not reveal contact.')
    } finally {
      setBusyId(null)
    }
  }

  async function toggleHistory(id: number) {
    if (openEvents[id]) {
      setOpenEvents((prev) => {
        const next = { ...prev }
        delete next[id]
        return next
      })
      return
    }
    try {
      const events = await introductionsApi.events(id)
      setOpenEvents((prev) => ({ ...prev, [id]: events }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load history.')
    }
  }

  return (
    <main className="container">
      <h1>Introductions</h1>
      <p className="muted">
        A household asks. A moderator routes. The worker decides. Contact
        details appear only when the worker reveals them.
      </p>

      {isHousehold && (
        <form onSubmit={(e) => void file(e)}>
          <label>
            Worker profile ID
            <input
              type="number"
              min="1"
              value={workerId}
              onChange={(e) => setWorkerId(e.target.value)}
              placeholder="e.g. 5"
              required
            />
          </label>
          <label>
            Note for the worker
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="What you need and when"
            />
          </label>
          <button type="submit">Ask for an introduction</button>
        </form>
      )}

      {notice && <p className="muted">{notice}</p>}
      {error && <p className="error">{error}</p>}

      <h2>{isModerator ? 'All introductions' : 'Your introductions'}</h2>
      {rows === null && <p className="muted">Loading…</p>}
      {rows !== null && rows.length === 0 && (
        <p className="muted">Nothing here yet.</p>
      )}
      <ul>
        {(rows ?? []).map((row) => (
          <li key={row.id}>
            <strong>#{row.id}</strong> — {statusLabel(row.status)}
            {' · '}
            {isWorker ? row.household_name || 'household hidden until routing' : row.worker_name || 'worker hidden until routing'}
            {row.note ? ` · ${row.note}` : ''}
            <br />
            {isModerator && row.status === 'requested' && (
              <button
                disabled={busyId === row.id}
                onClick={() => void run(row.id, () => introductionsApi.route(row.id), 'Routed to the worker.')}
              >
                Route to worker
              </button>
            )}
            {isWorker && row.status === 'routed' && (
              <>
                <button
                  disabled={busyId === row.id}
                  onClick={() => void run(row.id, () => introductionsApi.decide(row.id, 'accept'), 'Accepted.')}
                >
                  Accept
                </button>{' '}
                <button
                  disabled={busyId === row.id}
                  onClick={() => void run(row.id, () => introductionsApi.decide(row.id, 'decline'), 'Declined.')}
                >
                  Decline
                </button>
              </>
            )}
            {isWorker && row.status === 'accepted' && !revealed[row.id] && (
              <button disabled={busyId === row.id} onClick={() => void reveal(row.id)}>
                Reveal my contact
              </button>
            )}
            {revealed[row.id] && (
              <p className="muted">Your contact is shared: {revealed[row.id]}</p>
            )}
            {isHousehold &&
              (row.status === 'requested' || row.status === 'routed') && (
                <button
                  disabled={busyId === row.id}
                  onClick={() => void run(row.id, () => introductionsApi.withdraw(row.id), 'Withdrawn.')}
                >
                  Withdraw
                </button>
              )}{' '}
            <button onClick={() => void toggleHistory(row.id)}>
              {openEvents[row.id] ? 'Hide history' : 'History'}
            </button>
            {openEvents[row.id] && (
              <ol>
                {openEvents[row.id].map((event) => (
                  <li key={event.id}>
                    {event.what} — {event.created_at.slice(0, 16).replace('T', ' ')}
                  </li>
                ))}
              </ol>
            )}
          </li>
        ))}
      </ul>
    </main>
  )
}
