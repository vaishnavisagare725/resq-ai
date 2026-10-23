import { useState } from 'react'
import { Link } from 'react-router'
import { StatusBadge, UrgencyBadge } from '../components/Badges'
import LiveMap from '../components/LiveMap'
import Pager from '../components/Pager'
import useFetch from '../hooks/useFetch'
import { distanceKm, formatDate, mapLink } from '../utils'

const PAGE_SIZE = 20 // must match PAGE_SIZE in Django's REST_FRAMEWORK settings

export default function MyTasks() {
  const [tab, setTab] = useState('active') // 'active' or 'done'
  const [view, setView] = useState('list') // 'list' or 'map'
  const [page, setPage] = useState(1)
  const [here, setHere] = useState(null) // my position, once I ask for it
  const [locMsg, setLocMsg] = useState('')
  const [nearest, setNearest] = useState(false)

  const params = { sort: 'urgency', page }
  if (tab === 'active') params.active = 'true'
  else params.status = 'resolved'
  const { data, error, reload } = useFetch('/incidents/', params)

  function chooseTab(value) {
    setTab(value)
    setPage(1)
  }

  // ask for the location only when the worker clicks
  function findMe() {
    if (!('geolocation' in navigator)) {
      setLocMsg('This browser cannot share its location.')
      return
    }
    setLocMsg('Finding your location…')
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setHere({ lat: pos.coords.latitude, lng: pos.coords.longitude })
        setLocMsg('')
      },
      () => setLocMsg('Could not get your location, so distances are hidden.'),
      { enableHighAccuracy: true, timeout: 10000 },
    )
  }

  const km = (i) => (here ? distanceKm(here, { lat: i.latitude, lng: i.longitude }) : null)
  const rows = data
    ? nearest && here
      ? [...data.results].sort((a, b) => km(a) - km(b))
      : data.results
    : []

  return (
    <>
      <div className="card">
        <div className="actions" style={{ justifyContent: 'space-between' }}>
          <h2 style={{ margin: 0 }}>My tasks</h2>
          <div className="tabs">
            <button type="button" aria-pressed={view === 'list'} className={`tab ${view === 'list' ? 'active' : ''}`} onClick={() => setView('list')}>List</button>
            <button type="button" aria-pressed={view === 'map'} className={`tab ${view === 'map' ? 'active' : ''}`} onClick={() => setView('map')}>Map</button>
          </div>
        </div>
        <p className="muted small">Incidents you were assigned to as a field worker.</p>
      </div>

      {view === 'map' ? (
        <div className="card">
          <p className="muted small">Your active tasks. Tap a circle for details.</p>
          <LiveMap />
        </div>
      ) : (
        <div className="card">
          <div className="tabs">
            <button type="button" aria-pressed={tab === 'active'} className={`tab ${tab === 'active' ? 'active' : ''}`} onClick={() => chooseTab('active')}>Active</button>
            <button type="button" aria-pressed={tab === 'done'} className={`tab ${tab === 'done' ? 'active' : ''}`} onClick={() => chooseTab('done')}>Done</button>
          </div>

          <div className="actions" style={{ margin: '0.75rem 0' }}>
            <button type="button" className="secondary" onClick={findMe}>Use my location for distances</button>
            {here && (
              <label className="inline">
                <input type="checkbox" checked={nearest} onChange={(e) => setNearest(e.target.checked)} />
                Nearest first (this page)
              </label>
            )}
            {locMsg && <span className="muted small">{locMsg}</span>}
          </div>

          {error && (
            <div className="error" style={{ marginBottom: '0.75rem' }}>
              {error} <button type="button" className="secondary" onClick={reload}>Try again</button>
            </div>
          )}
          {!data && !error && <p className="muted">Loading…</p>}
          {data && data.results.length === 0 && (
            <p className="muted">{tab === 'active' ? 'No active tasks right now.' : 'No finished tasks yet.'}</p>
          )}

          {rows.length > 0 && (
            <>
              <ul className="list">
                {rows.map((i) => (
                  <li key={i.id}>
                    <div className="grow">
                      <Link to={`/incidents/${i.id}`}><strong>{i.title}</strong></Link>
                      <div className="muted small">
                        {formatDate(i.created_at)}
                        {i.assigned_to_name && ` · responder ${i.assigned_to_name}`}
                      </div>
                      <div className="muted small">
                        {i.latitude}, {i.longitude} ·{' '}
                        <a href={mapLink(i.latitude, i.longitude)} target="_blank" rel="noreferrer">map</a>
                        {here && ` · about ${km(i).toFixed(1)} km away (straight line)`}
                      </div>
                      <div className="tags">
                        <UrgencyBadge value={i.urgency} />
                        <StatusBadge value={i.status} />
                        <span className="chip">{i.category}</span>
                      </div>
                    </div>
                    <Link to={`/incidents/${i.id}`} className="button">Open</Link>
                  </li>
                ))}
              </ul>
              <Pager
                page={page}
                count={data.count}
                pageSize={PAGE_SIZE}
                hasPrev={Boolean(data.previous)}
                hasNext={Boolean(data.next)}
                onPage={setPage}
              />
            </>
          )}
        </div>
      )}
    </>
  )
}