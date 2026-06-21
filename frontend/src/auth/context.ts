import { createContext, useContext } from 'react'
import type { Role, User } from '../api/client'

export interface AuthState {
  user: User | null
  loading: boolean
  signIn: (phone: string, code: string, role: Role, fullName?: string) => Promise<User>
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
}

export const AuthContext = createContext<AuthState | null>(null)

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}
