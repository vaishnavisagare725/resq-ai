import { useState } from 'react'
import { Link, Navigate, useLocation } from 'react-router'
import { errorMessages } from '../api'
import { useAuth } from '../auth/useAuth'

export default function Login() {
  const { user, login } = useAuth()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  // once logged in, go back to the page the visitor wanted (or home)
  if (user) return <Navigate to={location.state?.from?.pathname || '/'} replace />

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(username.trim(), password)
    } catch (err) {
      setError(
        err.response?.status === 401
          ? 'Wrong username or password.'
          : errorMessages(err).join(' '),
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <h2>Log in</h2>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {error && <div className="error">{error}</div>}
        <button disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
      </form>
      <p className="muted">
        New here? <Link to="/register">Create a citizen account</Link>
      </p>
    </div>
  )
}