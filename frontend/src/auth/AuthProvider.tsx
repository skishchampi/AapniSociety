import { useCallback, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { authApi, tokens } from '../api/client'
import type { Role, User } from '../api/client'
import { AuthContext } from './context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    if (!tokens.access) {
      setUser(null)
      return
    }
    try {
      setUser(await authApi.me())
    } catch {
      tokens.clear()
      setUser(null)
    }
  }, [])

  useEffect(() => {
    // Mount-time bootstrap: hydrate the session from the token store / API.
    // This is a valid "sync from external system" effect; the setState lands
    // after the async hydration, not as a synchronous cascading render.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refreshUser().finally(() => setLoading(false))
  }, [refreshUser])

  const signIn = useCallback(
    async (phone: string, code: string, role: Role, fullName = '') => {
      const res = await authApi.verifyOtp(phone, code, role, fullName)
      tokens.set(res.access, res.refresh)
      setUser(res.user)
      return res.user
    },
    [],
  )

  const signOut = useCallback(async () => {
    const refresh = tokens.refresh
    if (refresh) {
      try {
        await authApi.logout(refresh)
      } catch {
        /* best-effort */
      }
    }
    tokens.clear()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}
