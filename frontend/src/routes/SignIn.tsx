import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError, authApi } from '../api/client'
import type { Role } from '../api/client'
import { useAuth } from '../auth/context'

type Step = 'phone' | 'code'

export function SignIn() {
  const { signIn } = useAuth()
  const navigate = useNavigate()

  const [step, setStep] = useState<Step>('phone')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [role, setRole] = useState<Role>('household')
  const [fullName, setFullName] = useState('')
  const [devCode, setDevCode] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function requestCode(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const res = await authApi.requestOtp(phone)
      setDevCode(res.dev_code ?? null)
      setStep('code')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not send code.')
    } finally {
      setBusy(false)
    }
  }

  async function verify(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const user = await signIn(phone, code, role, fullName)
      const hasProfile =
        (user.primary_role === 'worker' && user.has_worker_profile) ||
        (user.primary_role === 'household' && user.has_household_profile)
      navigate(hasProfile ? '/' : '/onboarding')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not verify code.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="container">
      <h1>AapniSociety</h1>
      <p className="muted">Worker-led cooperative infrastructure</p>

      {step === 'phone' && (
        <form onSubmit={requestCode}>
          <label>
            I am a
            <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
              <option value="household">Household / tenant</option>
              <option value="worker">Worker</option>
            </select>
          </label>
          <label>
            Name (optional)
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your name"
            />
          </label>
          <label>
            Phone
            <input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+9199…"
              required
            />
          </label>
          <button type="submit" disabled={busy || !phone}>
            {busy ? 'Sending…' : 'Send code'}
          </button>
        </form>
      )}

      {step === 'code' && (
        <form onSubmit={verify}>
          {devCode && (
            <p className="dev-hint">Dev code: <strong>{devCode}</strong></p>
          )}
          <label>
            Enter the 6-digit code sent to {phone}
            <input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              inputMode="numeric"
              maxLength={6}
              required
            />
          </label>
          <button type="submit" disabled={busy || code.length < 4}>
            {busy ? 'Verifying…' : 'Verify & continue'}
          </button>
          <button type="button" className="link" onClick={() => setStep('phone')}>
            Use a different number
          </button>
        </form>
      )}

      {error && <p className="error">{error}</p>}
    </main>
  )
}
