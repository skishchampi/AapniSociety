import { useEffect, useState } from 'react'
import { ApiError, membersApi, profileApi } from '../api/client'
import type { ServiceCategory, WorkerProfile, HouseholdProfile } from '../api/client'
import { useAuth } from '../auth/context'

function message(err: unknown, fallback: string): string {
  return err instanceof ApiError ? err.message : fallback
}

function WorkerFields({
  initial,
  categories,
}: {
  initial: WorkerProfile
  categories: ServiceCategory[]
}) {
  const [displayName, setDisplayName] = useState(initial.display_name)
  const [languages, setLanguages] = useState(initial.languages.join(', '))
  const [rateFloor, setRateFloor] = useState(initial.default_rate_floor ?? '')
  const [categoryIds, setCategoryIds] = useState<number[]>(initial.service_categories)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)

  function toggleCategory(id: number) {
    setCategoryIds((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id],
    )
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSaved(false)
    setBusy(true)
    try {
      await profileApi.updateWorker({
        display_name: displayName,
        languages: languages
          .split(',')
          .map((l) => l.trim())
          .filter(Boolean),
        default_rate_floor: rateFloor === '' ? null : rateFloor,
        service_categories: categoryIds,
      })
      setSaved(true)
    } catch (err) {
      setError(message(err, 'Could not save your profile.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit}>
      <label>
        Display name
        <input
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          placeholder="How clients see you"
          required
        />
      </label>
      <label>
        Languages (comma separated)
        <input
          value={languages}
          onChange={(e) => setLanguages(e.target.value)}
          placeholder="gu, hi"
        />
      </label>
      <fieldset>
        <legend>Work categories</legend>
        {categories.map((cat) => (
          <label key={cat.id}>
            <input
              type="checkbox"
              checked={categoryIds.includes(cat.id)}
              onChange={() => toggleCategory(cat.id)}
            />
            {cat.label}
          </label>
        ))}
        {categories.length === 0 && <p className="muted">No categories yet.</p>}
      </fieldset>
      <label>
        Rate floor (₹ per month)
        <input
          type="number"
          min="0"
          value={rateFloor}
          onChange={(e) => setRateFloor(e.target.value)}
          placeholder="8000"
        />
      </label>
      <button type="submit" disabled={busy}>
        {busy ? 'Saving…' : 'Save profile'}
      </button>
      {saved && <p className="muted">Saved.</p>}
      {error && <p className="error">{error}</p>}
    </form>
  )
}

function HouseholdFields({ initial }: { initial: HouseholdProfile }) {
  const [displayName, setDisplayName] = useState(initial.display_name)
  const [discoverable, setDiscoverable] = useState(initial.discoverable_to_coop)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSaved(false)
    setBusy(true)
    try {
      await profileApi.updateHousehold({
        display_name: displayName,
        discoverable_to_coop: discoverable,
      })
      setSaved(true)
    } catch (err) {
      setError(message(err, 'Could not save your profile.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit}>
      <label>
        Household name
        <input
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          required
        />
      </label>
      <label>
        <input
          type="checkbox"
          checked={discoverable}
          onChange={(e) => setDiscoverable(e.target.checked)}
        />
        Visible to cooperative moderators
      </label>
      <button type="submit" disabled={busy}>
        {busy ? 'Saving…' : 'Save profile'}
      </button>
      {saved && <p className="muted">Saved.</p>}
      {error && <p className="error">{error}</p>}
    </form>
  )
}

function WorkerSection() {
  const [initial, setInitial] = useState<WorkerProfile | null>(null)
  const [categories, setCategories] = useState<ServiceCategory[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    Promise.all([profileApi.getWorker(), membersApi.categories()])
      .then(([profile, cats]) => {
        if (!alive) return
        setInitial(profile)
        setCategories(cats.filter((c) => c.is_active))
      })
      .catch((err) => {
        if (alive) setError(message(err, 'Could not load your profile.'))
      })
    return () => {
      alive = false
    }
  }, [])

  if (error) return <p className="error">{error}</p>
  if (!initial) return <p className="muted">Loading…</p>
  return <WorkerFields initial={initial} categories={categories} />
}

function HouseholdSection() {
  const [initial, setInitial] = useState<HouseholdProfile | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    profileApi
      .getHousehold()
      .then((profile) => {
        if (alive) setInitial(profile)
      })
      .catch((err) => {
        if (alive) setError(message(err, 'Could not load your profile.'))
      })
    return () => {
      alive = false
    }
  }, [])

  if (error) return <p className="error">{error}</p>
  if (!initial) return <p className="muted">Loading…</p>
  return <HouseholdFields initial={initial} />
}

export function Profile() {
  const { user } = useAuth()
  if (!user) return null
  const isWorker = user.primary_role === 'worker'

  return (
    <main className="container">
      <h1>Your {isWorker ? 'worker' : 'household'} profile</h1>
      <p className="muted">
        Nothing here is public. Contact details are revealed only with your consent.
      </p>
      {isWorker ? <WorkerSection /> : <HouseholdSection />}
    </main>
  )
}
