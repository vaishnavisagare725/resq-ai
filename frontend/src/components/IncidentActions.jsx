import { useState } from 'react'
import { useNavigate } from 'react-router'
import api from '../api'
import { useAuth } from '../auth/useAuth'
import useAction from '../hooks/useAction'
import useFetch from '../hooks/useFetch'

const URGENCIES = ['low', 'medium', 'high', 'critical']
const CATEGORIES = ['fire', 'medical', 'flood', 'accident', 'other']

function Section({ title, children }) {
  return (
    <div className="action">
      <h4>{title}</h4>
      {children}
    </div>
  )
}

function Take({ incident, onChanged }) {
  const { busy, error, run } = useAction()
  return (
    <Section title="Take the case">
      <p className="muted small">Taking it makes you the responsible responder for this incident.</p>
      <button
        type="button"
        disabled={busy}
        onClick={() =>
          run(async () => {
            await api.post(`/incidents/${incident.id}/take/`)
            await onChanged()
          })
        }
      >
        {busy ? 'Taking…' : 'Take this case'}
      </button>
      {error && <div className="error">{error}</div>}
    </Section>
  )
}

function Triage({ incident, onChanged }) {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { busy, error, run } = useAction()
  const [urgency, setUrgency] = useState(incident.urgency)
  const [category, setCategory] = useState(incident.category)
  const [note, setNote] = useState('')
  const changed = urgency !== incident.urgency || category !== incident.category

  async function submit(e) {
    e.preventDefault()
    const body = { note }
    if (urgency !== incident.urgency) body.urgency = urgency
    if (category !== incident.category) body.category = category
    await run(async () => {
      const { data } = await api.post(`/incidents/${incident.id}/triage/`, body)
      setNote('')
      // re-routed to another department: this responder can no longer see it
      if (user.role === 'responder' && data.department && data.department !== user.department) {
        navigate('/dashboard', {
          state: { flash: `Incident #${data.id} was moved to the ${data.department} department.` },
        })
        return
      }
      await onChanged()
    })
  }

  return (
    <Section title="Correct the AI">
      <p className="muted small">AI said: {incident.ai_reason || 'no explanation recorded'}</p>
      <form className="form wide" onSubmit={submit}>
        <div className="two">
          <label>
            Urgency
            <select value={urgency} onChange={(e) => setUrgency(e.target.value)}>
              {URGENCIES.map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </label>
          <label>
            Category
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>
        </div>
        <label>
          Note (optional)
          <input
            value={note}
            onChange={(e) => setNote(e.target.value)}
            maxLength={300}
            placeholder="Why are you changing it?"
          />
        </label>
        {error && <div className="error">{error}</div>}
        <button disabled={busy || !changed}>{busy ? 'Saving…' : 'Save correction'}</button>
      </form>
    </Section>
  )
}

function Workers({ incident, onChanged }) {
  const { busy, error, run } = useAction()
  const [selected, setSelected] = useState([])
  const available = useFetch('/workers/', incident.department ? { department: incident.department } : {})

  const candidates = (available.data || []).filter(
    (w) => !incident.workers.some((x) => x.id === w.id),
  )

  function toggle(id) {
    setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]))
  }

  function add() {
    return run(async () => {
      await api.post(`/incidents/${incident.id}/add-workers/`, { worker_ids: selected })
      setSelected([])
      await onChanged()
    })
  }

  function remove(id) {
    return run(async () => {
      await api.post(`/incidents/${incident.id}/remove-workers/`, { worker_ids: [id] })
      await onChanged()
    })
  }

  return (
    <Section title="Field workers">
      {!incident.department && (
        <div className="notice">Set the category first, so the incident gets a department.</div>
      )}
      {incident.workers.length === 0 && <p className="muted">No workers assigned yet.</p>}
      {incident.workers.map((w) => (
        <div className="person" key={w.id}>
          <span>{w.username}</span>
          <button type="button" className="secondary" disabled={busy} onClick={() => remove(w.id)}>
            Remove
          </button>
        </div>
      ))}

      {available.loading && !available.data && <p className="muted">Loading workers…</p>}
      {available.error && <div className="error">{available.error}</div>}
      {candidates.length > 0 ? (
        <>
          <div className="checks">
            {candidates.map((w) => (
              <label className="inline" key={w.id}>
                <input
                  type="checkbox"
                  checked={selected.includes(w.id)}
                  onChange={() => toggle(w.id)}
                />
                {w.username} <span className="muted small">({w.department})</span>
              </label>
            ))}
          </div>
          <button type="button" disabled={busy || selected.length === 0} onClick={add}>
            {busy ? 'Saving…' : 'Add selected'}
          </button>
        </>
      ) : (
        available.data && <p className="muted small">No more workers available in this department.</p>
      )}
      {error && <div className="error">{error}</div>}
    </Section>
  )
}

function Resolve({ incident, onChanged }) {
  const { busy, error, run } = useAction()
  const [note, setNote] = useState('')

  function submit(e) {
    e.preventDefault()
    if (!window.confirm('Mark this incident as resolved? This cannot be undone.')) return
    run(async () => {
      await api.post(`/incidents/${incident.id}/resolve/`, { note })
      await onChanged()
    })
  }

  return (
    <Section title="Resolve">
      <form className="form wide" onSubmit={submit}>
        <label>
          What was done? (optional)
          <textarea value={note} onChange={(e) => setNote(e.target.value)} maxLength={500} />
        </label>
        {error && <div className="error">{error}</div>}
        <button disabled={busy}>{busy ? 'Saving…' : 'Mark as resolved'}</button>
      </form>
    </Section>
  )
}

// Shows only the actions this user may do. The API checks every one of them again.
export default function IncidentActions({ incident, onChanged }) {
  const { user } = useAuth()
  const isAdmin = user.role === 'admin'
  const isResponder = user.role === 'responder'
  const open = incident.status !== 'resolved'
  const owner = isResponder && incident.assigned_to_name === user.username
  const workerOnIt = user.role === 'worker' && incident.workers.some((w) => w.id === user.id)

  const canTake = isResponder && open && !incident.assigned_to
  const canTriage = open && (isAdmin || (isResponder && (!incident.assigned_to || owner)))
  const canWorkers = open && (isAdmin || owner)
  const canResolve = incident.status === 'assigned' && (isAdmin || owner || workerOnIt)

  if (!canTake && !canTriage && !canWorkers && !canResolve) return null

  return (
    <div className="card">
      <h3>Actions</h3>
      {canTake && <Take incident={incident} onChanged={onChanged} />}
      {canTriage && <Triage incident={incident} onChanged={onChanged} />}
      {canWorkers && <Workers incident={incident} onChanged={onChanged} />}
      {canResolve && <Resolve incident={incident} onChanged={onChanged} />}
    </div>
  )
}