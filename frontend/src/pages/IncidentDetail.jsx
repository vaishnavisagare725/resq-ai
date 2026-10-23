import { useCallback } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { StatusBadge, UrgencyBadge } from '../components/Badges'
import IncidentActions from '../components/IncidentActions'
import useFetch from '../hooks/useFetch'
import { formatDate, mapLink } from '../utils'

export default function IncidentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const incident = useFetch(`/incidents/${id}/`)
  const history = useFetch(`/incidents/${id}/updates/`)
  const { reload: reloadIncident } = incident
  const { reload: reloadHistory } = history

  // called by the Actions panel after every successful action
  const refresh = useCallback(() => {
    reloadIncident()
    reloadHistory()
  }, [reloadIncident, reloadHistory])

  // the backend hides incidents you may not see, so a 404 can mean "no access"
  if (incident.status === 404) {
    return (
      <div className="card">
        <h2>Report not found</h2>
        <p className="muted">It may not exist, or you may not have access to it.</p>
        <Link to="/">Back to home</Link>
      </div>
    )
  }

  if (!incident.data) {
    if (incident.error) {
      return (
        <div className="card">
          <div className="error">{incident.error}</div>
          <button type="button" className="secondary" onClick={reloadIncident}>Try again</button>
        </div>
      )
    }
    return <p className="muted">Loading…</p>
  }

  const i = incident.data

  return (
    <>
      <p>
        <button type="button" className="secondary" onClick={() => navigate(-1)}>← Back</button>
      </p>
      {incident.error && <div className="error" style={{ marginBottom: '1rem' }}>{incident.error}</div>}

      <div className="card">
        <h2>{i.title}</h2>
        <div className="tags">
          <UrgencyBadge value={i.urgency} />
          <StatusBadge value={i.status} />
          <span className="chip">{i.category}</span>
          {i.department && <span className="chip">{i.department}</span>}
        </div>
        <p>{i.description}</p>
        <p className="muted small">Reported by {i.reporter_name} on {formatDate(i.created_at)}</p>
      </div>

      <IncidentActions incident={i} onChanged={refresh} />

      <div className="card">
        <h3>Location</h3>
        <p>
          {i.latitude}, {i.longitude}{' · '}
          <a href={mapLink(i.latitude, i.longitude)} target="_blank" rel="noreferrer">
            Open in OpenStreetMap
          </a>
        </p>
      </div>

      <div className="card">
        <h3>AI assessment</h3>
        <p className="muted">{i.ai_reason || 'No AI assessment was recorded for this report.'}</p>
        {i.needs_review && <div className="notice">A responder still needs to review this report.</div>}
      </div>

      <div className="card">
        <h3>People</h3>
        <p>Responder: {i.assigned_to_name || 'Not taken yet'}</p>
        <p>
          Field workers:{' '}
          {i.workers.length === 0 ? 'None yet' : i.workers.map((w) => w.username).join(', ')}
        </p>
      </div>

      <div className="card">
        <h3>Photos</h3>
        {i.images.length === 0 && <p className="muted">No photos.</p>}
        <div className="photos">
          {i.images.map((img, n) => (
            <a key={img.id} href={img.image} target="_blank" rel="noreferrer">
              <img src={img.image} alt={`Photo ${n + 1} of ${i.title}`} loading="lazy" />
            </a>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>History</h3>
        {history.error && !history.data && <div className="error">{history.error}</div>}
        {!history.data && !history.error && <p className="muted">Loading…</p>}
        {history.data?.length === 0 && <p className="muted">No updates yet.</p>}
        <ul className="timeline">
          {history.data?.map((u) => (
            <li key={u.id}>
              <strong>
                {u.old_status === u.new_status ? 'Update' : `${u.old_status} → ${u.new_status}`}
              </strong>
              <div>{u.note}</div>
              <div className="muted small">
                {u.updated_by_name || 'Someone'} · {formatDate(u.created_at)}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </>
  )
}