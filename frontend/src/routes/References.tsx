import { useEffect, useState } from 'react'
import { referencesApi } from '../api/client'
import type { ReferenceRequest, ReferenceVisibility, WorkerReference } from '../api/client'
import { useAuth } from '../auth/context'

const VISIBILITY_OPTIONS: { value: ReferenceVisibility; label: string }[] = [
  { value: 'private', label: 'Private (only you)' },
  { value: 'coop', label: 'Cooperative moderators' },
  { value: 'shared', label: 'Shared on routed introductions' },
]

export function References() {
  const { user } = useAuth()
  const [refs, setRefs] = useState<WorkerReference[] | null>(null)
  const [requests, setRequests] = useState<ReferenceRequest[] | null>(null)
  const [householdId, setHouseholdId] = useState('')
  const [introId, setIntroId] = useState('')
  const [body, setBody] = useState('')
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const role = user?.primary_role ?? ''
  const isWorker = role === 'worker'
  const isHousehold = role === 'household'

  useEffect(() => {
    let alive = true
    if (isWorker) {
      referencesApi
        .mine()
        .then((list) => {
          if (alive) setRefs(list)
        })
        .catch(() => {
          if (alive) setRefs([])
        })
    }
    referencesApi
      .listRequests()
      .then((list) => {
        if (alive) setRequests(list)
      })
      .catch(() => {
        if (alive) setRequests([])
      })
    return () => {
      alive = false
    }
  }, [isWorker])

  async function requestReference(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setNotice(null)
    const hhId = Number(householdId)
    if (!hhId) {
      setError('Enter a household profile ID.')
      return
    }
    setBusy(true)
    try {
      await referencesApi.createRequest({
        household: hhId,
        introduction: introId ? Number(introId) : undefined,
      })
      setRequests(await referencesApi.listRequests())
      setHouseholdId('')
      setIntroId('')
      setNotice('Reference request sent.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not send the request.')
    } finally {
      setBusy(false)
    }
  }

  async function changeVisibility(id: number, visibility: ReferenceVisibility) {
    setError(null)
    setNotice(null)
    try {
      const updated = await referencesApi.setVisibility(id, visibility)
      setRefs((prev) => (prev ?? []).map((r) => (r.id === id ? updated : r)))
      setNotice(`Visibility set to ${visibility}.`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not update visibility.')
    }
  }

  async function writeReference(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setNotice(null)
    const id = Number(introId)
    if (!id || !body.trim()) {
      setError('Enter an accepted introduction ID and a written reference.')
      return
    }
    setBusy(true)
    try {
      await referencesApi.create({ introduction: id, body: body.trim() })
      setRequests(await referencesApi.listRequests())
      setIntroId('')
      setBody('')
      setNotice('Reference saved. The worker controls its visibility.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save the reference.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="container">
      <h1>Portable references</h1>
      <p className="muted">
        References are private by default. Workers control who sees them. There is no
        public rating board.
      </p>

      {isWorker && (
        <>
          <h2>Your references</h2>
          {refs === null && <p className="muted">Loading…</p>}
          {refs !== null && refs.length === 0 && (
            <p className="muted">No references yet.</p>
          )}
          <ul>
            {(refs ?? []).map((ref) => (
              <li key={ref.id}>
                <strong>Intro #{ref.introduction}</strong>: {ref.body}
                <br />
                <label>
                  Visibility{' '}
                  <select
                    aria-label={`Visibility for reference ${ref.id}`}
                    value={ref.visibility}
                    onChange={(e) =>
                      void changeVisibility(ref.id, e.target.value as ReferenceVisibility)
                    }
                  >
                    {VISIBILITY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </label>
              </li>
            ))}
          </ul>

          <h2>Ask a household for a reference</h2>
          <form onSubmit={(e) => void requestReference(e)}>
            <label>
              Household profile ID
              <input
                type="number"
                min="1"
                value={householdId}
                onChange={(e) => setHouseholdId(e.target.value)}
                required
              />
            </label>
            <label>
              Introduction ID (optional)
              <input
                type="number"
                min="1"
                value={introId}
                onChange={(e) => setIntroId(e.target.value)}
              />
            </label>
            <button type="submit" disabled={busy}>
              Request reference
            </button>
          </form>
        </>
      )}

      {isHousehold && (
        <>
          <h2>Write a reference</h2>
          <form onSubmit={(e) => void writeReference(e)}>
            <label>
              Accepted introduction ID
              <input
                type="number"
                min="1"
                value={introId}
                onChange={(e) => setIntroId(e.target.value)}
                required
              />
            </label>
            <label>
              Reference note
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Describe the work done and reliability"
                required
              />
            </label>
            <button type="submit" disabled={busy}>
              Save reference
            </button>
          </form>
        </>
      )}

      {notice && <p className="muted">{notice}</p>}
      {error && <p className="error">{error}</p>}

      <h2>Reference requests</h2>
      {requests === null && <p className="muted">Loading…</p>}
      {requests !== null && requests.length === 0 && (
        <p className="muted">No reference requests yet.</p>
      )}
      <ul>
        {(requests ?? []).map((req) => (
          <li key={req.id}>
            #{req.id} — [{req.status}] household #{req.household}
            {req.introduction ? ` · intro #${req.introduction}` : ''}
          </li>
        ))}
      </ul>
    </main>
  )
}
