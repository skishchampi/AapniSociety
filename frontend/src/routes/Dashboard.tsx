import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/context'

export function Dashboard() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  async function handleSignOut() {
    await signOut()
    navigate('/signin')
  }

  if (!user) return null

  return (
    <main className="container">
      <h1>Welcome{user.full_name ? `, ${user.full_name}` : ''}</h1>
      <dl className="info">
        <dt>Phone</dt>
        <dd>{user.phone}</dd>
        <dt>Role</dt>
        <dd>{user.primary_role}</dd>
        <dt>Profile</dt>
        <dd>
          {user.has_worker_profile || user.has_household_profile
            ? 'complete'
            : 'incomplete'}
        </dd>
      </dl>
      <nav>
        <a href="/profile">Profile</a> · <a href="/membership">Membership</a> ·{' '}
        <a href="/needs">Needs</a> · <a href="/introductions">Introductions</a> ·{' '}
        <a href="/references">References</a> · <a href="/safety">Safety</a>
        {['moderator', 'operator', 'admin'].includes(user.primary_role) && (
          <>
            {' '}
            · <a href="/moderation">Moderation</a>
          </>
        )}
      </nav>
      <p className="muted">
        Cooperative Trust Pilot (0.1.0-alpha.5). All core pilot flows are active.
      </p>
      <button onClick={handleSignOut}>Sign out</button>
    </main>
  )
}
