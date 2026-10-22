import { useState } from 'react'
import { Link, Navigate } from 'react-router'
import api, { errorMessages } from '../api'
import { useAuth } from '../auth/useAuth'

export default function Register() {
  const { user, login } = useAuth()
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' })
  const [errors, setErrors] = useState([])
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/" replace />

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (form.password !== form.confirm) {
      setErrors(['Passwords do not match.'])
      return
    }
    setErrors([])
    setBusy(true)
    try {
      const username = form.username.trim()
      await api.post('/auth/register/', { username, email: form.email.trim(), password: form.password })
      await login(username, form.password) // log the new citizen in straight away
    } catch (err) {
      setErrors(errorMessages(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <h2>Create a citizen account</h2>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          Username
          <input name="username" value={form.username} onChange={update} required />
        </label>
        <label>
          Email (optional)
          <input name="email" type="email" value={form.email} onChange={update} />
        </label>
        <label>
          Password
          <input name="password" type="password" value={form.password} onChange={update} required />
        </label>
        <label>
          Confirm password
          <input name="confirm" type="password" value={form.confirm} onChange={update} required />
        </label>
        {errors.map((m) => (
          <div className="error" key={m}>{m}</div>
        ))}
        <button disabled={busy}>{busy ? 'Creating…' : 'Create account'}</button>
      </form>
      <p className="muted">
        Already registered? <Link to="/login">Log in</Link>
      </p>
    </div>
  )
}