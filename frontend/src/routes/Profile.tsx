import { useEffect, useState } from 'react'
import { ApiError, geoApi, membersApi, profileApi } from '../api/client'
import type {
  HouseholdProfile,
  Locality,
  ServiceCategory,
  WorkerProfile,
} from '../api/client'
import { useAuth } from '../auth/context'

const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] as const

function message(err: unknown, fallback: string): string {
  return err instanceof ApiError ? err.message : fallback
}

function WorkerFields({
  initial,
  categories,
  localities,
}: {
  initial: WorkerProfile
  categories: ServiceCategory[]
  localities: Locality[]
}) {
  const [displayName, setDisplayName] = useState(initial.display_name)
  const [languages, setLanguages] = useState(initial.languages.join(', '))
  const [rateFloor, setRateFloor] = useState(initial.default_rate_floor ?? '')
  const [categoryIds, setCategoryIds] = useState<number[]>(initial.service_categories)
  const [localityIds, setLocalityIds] = useState<number[]>(initial.localities_served)
  const [availabilityText, setAvailabilityText] = useState<Record<string, string>>(() => {
    const text: Record<string, string> = {}
    for (const day of DAYS) {
      const windows = initial.availability[day]
      if (Array.isArray(windows) && windows.length > 0) {
        text[day] = windows.join(', ')
      }
    }
    return text
  })
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)

  function toggle(list: number[], id: number, set: (next: number[]) => void) {
    set(list.includes(id) ? list.filter((x) => x !== id) : [...list, id])
  }

  function parseAvailability(): Record<string, string[]> {
    const availability: Record<string, string[]> = {}
    for (const day of DAYS) {
      const windows = (availabilityText[day] ?? '')
        .split(',')
        .map((w) => w.trim())
        .filter(Boolean)
      if (windows.length > 0) availability[day] = windows
    }
    return availability
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
        localities_served: localityIds,
        availability: parseAvailability(),
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
              onChange={() => toggle(categoryIds, cat.id, setCategoryIds)}
            />
            {cat.label}
          </label>
        ))}
        {categories.length === 0 && <p className="muted">No categories yet.</p>}
      </fieldset>
      <fieldset>
        <legend>Localities you serve</legend>
        {localities.map((loc) => (
          <label key={loc.id}>
            <input
              type="checkbox"
              checked={localityIds.includes(loc.id)}
              onChange={() => toggle(localityIds, loc.id, setLocalityIds)}
            />
            {loc.name}
          </label>
        ))}
        {localities.length === 0 && <p className="muted">No localities yet.</p>}
      </fieldset>
      <fieldset>
        <legend>Weekly availability</legend>
        <p className="muted">
          One window per line item, comma separated, like 09:00-13:00.
        </p>
        {DAYS.map((day) => (
          <label key={day}>
            {day}
            <input
              value={availabilityText[day] ?? ''}
              onChange={(e) =>
                setAvailabilityText((prev) => ({ ...prev, [day]: e.target.value }))
              }
              placeholder="09:00-13:00, 16:00-20:00"
            />
          </label>
        ))}
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
  const [localities, setLocalities] = useState<Locality[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    Promise.all([profileApi.getWorker(), membersApi.categories(), geoApi.localities()])
      .then(([profile, cats, locs]) => {
        if (!alive) return
        setInitial(profile)
        setCategories(cats.filter((c) => c.is_active))
        setLocalities(locs)
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
  return <WorkerFields initial={initial} categories={categories} localities={localities} />
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
