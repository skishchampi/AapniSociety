import { useEffect, useState } from 'react'
import { geoApi, safetyApi } from '../api/client'
import type {
  AbuseCategory,
  AbuseReport,
  EvidenceLevel,
  Locality,
  SafetyNote,
  SafetyNoteType,
  WorkerBlock,
} from '../api/client'
import { useAuth } from '../auth/context'

const MODERATOR_ROLES = ['moderator', 'operator', 'admin']

const ABUSE_CATEGORIES: { value: AbuseCategory; label: string }[] = [
  { value: 'harassment', label: 'Harassment' },
  { value: 'non_payment', label: 'Non-payment' },
  { value: 'caste_abuse', label: 'Caste abuse' },
  { value: 'communal_abuse', label: 'Communal abuse' },
  { value: 'coercion', label: 'Coercion' },
  { value: 'stalking', label: 'Stalking' },
  { value: 'unsafe_conduct', label: 'Unsafe conduct' },
]

const NOTE_TYPES: { value: SafetyNoteType; label: string }[] = [
  { value: 'transit_reliability', label: 'Transit reliability' },
  { value: 'night_route_risk', label: 'Night-route risk' },
  { value: 'hostile_institution', label: 'Hostile institution' },
  { value: 'police_or_official_warning', label: 'Police-station or official-contact warning' },
  { value: 'non_payment_pattern', label: 'Non-payment pattern' },
  { value: 'unsafe_building_or_household', label: 'Unsafe building or household pattern' },
]

export function Safety() {
  const { user } = useAuth()
  const role = user?.primary_role ?? ''
  const isWorker = role === 'worker'
  const isModerator = MODERATOR_ROLES.includes(role)
  const canReadNotes = isWorker || isModerator

  const [blocks, setBlocks] = useState<WorkerBlock[] | null>(null)
  const [reports, setReports] = useState<AbuseReport[] | null>(null)
  const [notes, setNotes] = useState<SafetyNote[] | null>(null)
  const [localities, setLocalities] = useState<Locality[]>([])

  const [blockHouseholdId, setBlockHouseholdId] = useState('')
  const [blockReason, setBlockReason] = useState('')

  const [reportHouseholdId, setReportHouseholdId] = useState('')
  const [reportCategory, setReportCategory] = useState<AbuseCategory>('harassment')
  const [reportDetails, setReportDetails] = useState('')

  const [noteLocality, setNoteLocality] = useState('')
  const [noteType, setNoteType] = useState<SafetyNoteType>('night_route_risk')
  const [evidenceLevel, setEvidenceLevel] = useState<EvidenceLevel>('firsthand')
  const [noteBody, setNoteBody] = useState('')

  const [notice, setNotice] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    if (isWorker) {
      safetyApi
        .blocks()
        .then((list) => {
          if (alive) setBlocks(list)
        })
        .catch(() => {
          if (alive) setBlocks([])
        })
    }
    if (canReadNotes) {
      safetyApi
        .safetyNotes()
        .then((list) => {
          if (alive) setNotes(list)
        })
        .catch(() => {
          if (alive) setNotes([])
        })
      geoApi
        .localities()
        .then((list) => {
          if (alive) setLocalities(list)
        })
        .catch(() => {
          /* optional locality selector */
        })
    }
    safetyApi
      .reports()
      .then((list) => {
        if (alive) setReports(list)
      })
      .catch(() => {
        if (alive) setReports([])
      })
    return () => {
      alive = false
    }
  }, [isWorker, canReadNotes])

  async function submitBlock(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setNotice(null)
    const hhId = Number(blockHouseholdId)
    if (!hhId) {
      setError('Enter a household profile ID.')
      return
    }
    try {
      await safetyApi.createBlock({ household: hhId, reason: blockReason || undefined })
      setBlocks(await safetyApi.blocks())
      setBlockHouseholdId('')
      setBlockReason('')
      setNotice('Household blocked.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not block household.')
    }
  }

  async function unblock(id: number) {
    setError(null)
    setNotice(null)
    try {
      await safetyApi.deleteBlock(id)
      setBlocks(await safetyApi.blocks())
      setNotice('Block removed.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not remove block.')
    }
  }

  async function submitReport(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setNotice(null)
    if (!reportDetails.trim()) {
      setError('Describe what happened.')
      return
    }
    try {
      await safetyApi.createReport({
        reported_household: reportHouseholdId ? Number(reportHouseholdId) : undefined,
        category: reportCategory,
        details: reportDetails.trim(),
      })
      setReports(await safetyApi.reports())
      setReportHouseholdId('')
      setReportDetails('')
      setNotice('Confidential report sent to cooperative moderators.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not file report.')
    }
  }

  async function submitNote(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setNotice(null)
    if (!noteBody.trim()) {
      setError('Write the safety note.')
      return
    }
    try {
      await safetyApi.createSafetyNote({
        locality: noteLocality ? Number(noteLocality) : undefined,
        note_type: noteType,
        evidence_level: evidenceLevel,
        body: noteBody.trim(),
      })
      setNotes(await safetyApi.safetyNotes())
      setNoteBody('')
      setNotice('Safety note saved for workers and moderators.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save safety note.')
    }
  }

  return (
    <main className="container">
      <h1>Safety and reports</h1>
      <p className="muted">
        Blocks, abuse reports, and city safety notes are confidential. Raw safety notes
        are never shown to households, landlords, or RWAs.
      </p>

      {notice && <p className="muted">{notice}</p>}
      {error && <p className="error">{error}</p>}

      {isWorker && (
        <section>
          <h2>Block a household</h2>
          <form onSubmit={(e) => void submitBlock(e)}>
            <label>
              Household profile ID to block
              <input
                type="number"
                min="1"
                value={blockHouseholdId}
                onChange={(e) => setBlockHouseholdId(e.target.value)}
                required
              />
            </label>
            <label>
              Private reason (optional)
              <input
                value={blockReason}
                onChange={(e) => setBlockReason(e.target.value)}
                placeholder="Never shared with the household"
              />
            </label>
            <button type="submit">Block household</button>
          </form>
          {blocks !== null && blocks.length > 0 && (
            <ul>
              {blocks.map((b) => (
                <li key={b.id}>
                  Household #{b.household} {b.reason ? `— ${b.reason}` : ''}{' '}
                  <button onClick={() => void unblock(b.id)}>Unblock</button>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {canReadNotes && (
        <section>
          <h2>City safety notes</h2>
          <form onSubmit={(e) => void submitNote(e)}>
            <label>
              Note type
              <select
                value={noteType}
                onChange={(e) => setNoteType(e.target.value as SafetyNoteType)}
              >
                {NOTE_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Evidence level
              <select
                value={evidenceLevel}
                onChange={(e) => setEvidenceLevel(e.target.value as EvidenceLevel)}
              >
                <option value="firsthand">Firsthand experience</option>
                <option value="secondhand">Secondhand report</option>
              </select>
            </label>
            {localities.length > 0 && (
              <label>
                Locality (optional)
                <select
                  value={noteLocality}
                  onChange={(e) => setNoteLocality(e.target.value)}
                >
                  <option value="">Any / city-wide</option>
                  {localities.map((loc) => (
                    <option key={loc.id} value={String(loc.id)}>
                      {loc.name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <label>
              Safety note
              <textarea
                value={noteBody}
                onChange={(e) => setNoteBody(e.target.value)}
                placeholder="Share route risks, transit issues, or unsafe patterns"
                required
              />
            </label>
            <button type="submit">Save safety note</button>
          </form>
          {notes !== null && notes.length === 0 && (
            <p className="muted">No safety notes yet.</p>
          )}
          <ul>
            {(notes ?? []).map((n) => (
              <li key={n.id}>
                [{n.evidence_level}] <strong>{n.note_type}</strong>: {n.body}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2>File a confidential abuse report</h2>
        <form onSubmit={(e) => void submitReport(e)}>
          <label>
            Category
            <select
              value={reportCategory}
              onChange={(e) => setReportCategory(e.target.value as AbuseCategory)}
            >
              {ABUSE_CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Household profile ID (optional)
            <input
              type="number"
              min="1"
              value={reportHouseholdId}
              onChange={(e) => setReportHouseholdId(e.target.value)}
            />
          </label>
          <label>
            Report details
            <textarea
              value={reportDetails}
              onChange={(e) => setReportDetails(e.target.value)}
              placeholder="What happened and when"
              required
            />
          </label>
          <button type="submit">File report</button>
        </form>
        <h3>Your filed reports</h3>
        {reports !== null && reports.length === 0 && (
          <p className="muted">No reports filed.</p>
        )}
        <ul>
          {(reports ?? []).map((r) => (
            <li key={r.id}>
              #{r.id} [{r.status}] {r.category} — {r.details}
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
