import { Navigate, useLocation } from 'react-router'
import { useAuth } from '../auth/useAuth'

// Convenience only: the real rules are enforced by the Django API.
export default function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <p className="muted">Loading…</p>
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}