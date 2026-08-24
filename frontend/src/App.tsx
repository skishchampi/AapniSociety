import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthProvider'
import { useAuth } from './auth/context'
import { Dashboard } from './routes/Dashboard'
import { Membership } from './routes/Membership'
import { Moderation } from './routes/Moderation'
import { Needs } from './routes/Needs'
import { Onboarding } from './routes/Onboarding'
import { Profile } from './routes/Profile'
import { SignIn } from './routes/SignIn'

const queryClient = new QueryClient()

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <p className="container muted">Loading…</p>
  if (!user) return <Navigate to="/signin" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/signin" element={<SignIn />} />
            <Route
              path="/onboarding"
              element={
                <RequireAuth>
                  <Onboarding />
                </RequireAuth>
              }
            />
            <Route
              path="/profile"
              element={
                <RequireAuth>
                  <Profile />
                </RequireAuth>
              }
            />
            <Route
              path="/membership"
              element={
                <RequireAuth>
                  <Membership />
                </RequireAuth>
              }
            />
            <Route
              path="/needs"
              element={
                <RequireAuth>
                  <Needs />
                </RequireAuth>
              }
            />
            <Route
              path="/moderation"
              element={
                <RequireAuth>
                  <Moderation />
                </RequireAuth>
              }
            />
            <Route
              path="/"
              element={
                <RequireAuth>
                  <Dashboard />
                </RequireAuth>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
