import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError, profileApi } from '../api/client'
import { useAuth } from '../auth/context'

export function Onboarding() {
  const { user, refreshUser } = useAuth()
  const navigate = useNavigate()
  const [displayName, setDisplayName] = useState(user?.full_name ?? '')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const isWorker = user?.primary_role === 'worker'

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      if (isWorker) {
        await profileApi.updateWorker({ display_name: displayName })
      } else {
        await profileApi.updateHousehold({ display_name: displayName })
      }
      await refreshUser()
      navigate('/')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not save profile.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="container">
      <h1>Set up your {isWorker ? 'worker' : 'household'} profile</h1>
      <p className="muted">
        Just the basics for now. Nothing here is public; details are revealed only with
        your consent.
      </p>
      <form onSubmit={submit}>
        <label>
          Display name
          <input
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder={isWorker ? 'How clients see you' : 'Household name'}
            required
          />
        </label>
        <button type="submit" disabled={busy || !displayName}>
          {busy ? 'Saving…' : 'Finish'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </main>
  )
}
