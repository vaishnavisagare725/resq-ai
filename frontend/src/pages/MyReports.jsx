import { useState } from 'react'
import { Link } from 'react-router'
import { StatusBadge, UrgencyBadge } from '../components/Badges'
import useFetch from '../hooks/useFetch'
import { formatDate } from '../utils'

const PAGE_SIZE = 20 // must match PAGE_SIZE in Django's REST_FRAMEWORK settings

export default function MyReports() {
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('')
  const { data, error, loading, reload } = useFetch(
    '/incidents/',
    status ? { page, status } : { page },
  )

  function changeStatus(e) {
    setStatus(e.target.value)
    setPage(1) // a new filter starts again from page 1
  }

  const pages = data ? Math.max(1, Math.ceil(data.count / PAGE_SIZE)) : 1

  return (
    <div className="card">
      <div className="actions" style={{ justifyContent: 'space-between' }}>
        <h2 style={{ margin: 0 }}>My reports</h2>
        <Link to="/report" className="button">New report</Link>
      </div>

      <label style={{ maxWidth: 200, margin: '1rem 0' }}>
        Show
        <select value={status} onChange={changeStatus}>
          <option value="">All reports</option>
          <option value="open">Open</option>
          <option value="assigned">Assigned</option>
          <option value="resolved">Resolved</option>
        </select>
      </label>

      {loading && <p className="muted">Loading…</p>}

      {error && (
        <div className="error">
          {error}{' '}
          <button type="button" className="secondary" onClick={reload}>Try again</button>{' '}
          <button type="button" className="secondary" onClick={() => setPage(1)}>First page</button>
        </div>
      )}

      {data && data.results.length === 0 && (
        <p className="muted">No reports here yet.</p>
      )}

      {data && data.results.length > 0 && (
        <>
          <ul className="list links">
            {data.results.map((i) => (
              <li key={i.id}>
                <Link to={`/incidents/${i.id}`} className="item">
                  <div>
                    <strong>{i.title}</strong>
                    <div className="muted small">
                      {formatDate(i.created_at)} · {i.images.length} photo(s)
                    </div>
                  </div>
                  <div className="tags">
                    <UrgencyBadge value={i.urgency} />
                    <StatusBadge value={i.status} />
                  </div>
                </Link>
              </li>
            ))}
          </ul>

          <div className="pager">
            <button
              type="button"
              className="secondary"
              disabled={!data.previous}
              onClick={() => setPage(page - 1)}
            >
              ← Previous
            </button>
            <span className="muted small">
              Page {page} of {pages} · {data.count} report(s)
            </span>
            <button
              type="button"
              className="secondary"
              disabled={!data.next}
              onClick={() => setPage(page + 1)}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  )
}