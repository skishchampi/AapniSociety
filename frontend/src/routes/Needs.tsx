import { useEffect, useState } from 'react'
import { membersApi } from '../api/client'
import type { ServiceCategory, ServiceNeed } from '../api/client'
import { useAuth } from '../auth/context'

export function Needs() {
  const { user } = useAuth()
  const [needs, setNeeds] = useState<ServiceNeed[] | null>(null)
  const [categories, setCategories] = useState<ServiceCategory[]>([])
  const [categoryId, setCategoryId] = useState<string>('')
  const [title, setTitle] = useState('')
  const [details, setDetails] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let alive = true
    membersApi
      .categories()
      .then((cats) => {
        if (!alive) return
        setCategories(cats.filter((c) => c.is_active))
        if (cats.length > 0) setCategoryId(String(cats[0].id))
      })
      .catch(() => {
        /* the select shows an empty state */
      })
    membersApi
      .needs()
      .then((list) => {
        if (alive) setNeeds(list)
      })
      .catch(() => {
        if (alive) setNeeds([])
      })
    return () => {
      alive = false
    }
  }, [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setNotice(null)
    if (!categoryId) {
      setError('Pick a category.')
      return
    }
    setBusy(true)
    try {
      await membersApi.createNeed({
        category: Number(categoryId),
        title,
        details: details || undefined,
      })
      setNeeds(await membersApi.needs())
      setTitle('')
      setDetails('')
      setNotice('Need posted. The cooperative will help match it.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not post the need.')
    } finally {
      setBusy(false)
    }
  }

  const isHousehold = user?.primary_role === 'household'

  return (
    <main className="container">
      <h1>Service needs</h1>
      <p className="muted">
        Needs are visible only to the cooperative. Nothing is public.
      </p>

      {isHousehold && (
        <form onSubmit={submit}>
          <label>
            Category
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
            >
              {categories.map((cat) => (
                <option key={cat.id} value={String(cat.id)}>
                  {cat.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            What do you need?
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Morning help for two hours"
              required
            />
          </label>
          <label>
            Details
            <textarea
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              placeholder="Timing, frequency, anything else"
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Posting…' : 'Post need'}
          </button>
        </form>
      )}
      {!isHousehold && (
        <p className="muted">Only household accounts can post needs.</p>
      )}

      {notice && <p className="muted">{notice}</p>}
      {error && <p className="error">{error}</p>}

      <h2>{isHousehold ? 'Your needs' : 'All needs'}</h2>
      {needs === null && <p className="muted">Loading…</p>}
      {needs !== null && needs.length === 0 && (
        <p className="muted">No needs yet.</p>
      )}
      <ul>
        {(needs ?? []).map((need) => (
          <li key={need.id}>
            [{need.status}] {need.title} — {need.details || 'no details'}
          </li>
        ))}
      </ul>
    </main>
  )
}
