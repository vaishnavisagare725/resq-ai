import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router'
import api, { errorMessages } from '../api'
import { useAuth } from '../auth/useAuth'
import { StatusBadge, UrgencyBadge } from '../components/Badges'
import Pager from '../components/Pager'
import SummaryCards from '../components/SummaryCards'
import useFetch from '../hooks/useFetch'
import { timeAgo } from '../utils'

const PAGE_SIZE = 20 // must match PAGE_SIZE in Django's REST_FRAMEWORK settings
const REFRESH_MS = 15000
const TABS = [
  ['open', 'Open'],
  ['assigned', 'In progress'],
  ['resolved', 'Resolved'],
  ['', 'All'],
]

export default function Dashboard() {
  const { user } = useAuth()
  const location = useLocation()
  const flash = location.state?.flash
  const [filters, setFilters] = useState({ status: 'open', urgency: '', review: false, q: '', page: 1 })
  const [search, setSearch] = useState('')
  const [takingId, setTakingId] = useState(null)
  const [actionError, setActionError] = useState('')

  const params = { sort: 'urgency', page: filters.page }
  if (filters.status) params.status = filters.status
  if (filters.urgency) params.urgency = filters.urgency
  if (filters.review) params.needs_review = 'true'
  if (filters.q) params.q = filters.q

  const list = useFetch('/incidents/', params)
  const summary = useFetch('/incidents/summary/')
  const { reload: reloadList } = list
  const { reload: reloadSummary } = summary

  // polling: ask again every 15 seconds, but not while the tab is hidden
  useEffect(() => {
    const timer = setInterval(() => {
      if (!document.hidden) {
        reloadList()
        reloadSummary()
      }
    }, REFRESH_MS)
    return () => clearInterval(timer)
  }, [reloadList, reloadSummary])

  // any filter change goes back to page 1, unless the change itself sets the page
  function setFilter(change) {
    setFilters((f) => ({ ...f, page: 1, ...change }))
  }

  function refreshAll() {
    reloadList()
    reloadSummary()
  }

  async function take(id) {
    setTakingId(id)
    setActionError('')
    try {
      await api.post(`/incidents/${id}/take/`)
    } catch (err) {
      setActionError(errorMessages(err).join(' ')) // e.g. someone else took it first
    } finally {
      setTakingId(null)
      refreshAll()
    }
  }

  const canTake = (i) => user.role === 'responder' && i.status === 'open' && !i.assigned_to

  return (
    <>
      <div className="card">
        <div className="actions" style={{ justifyContent: 'space-between' }}>
          <h2 style={{ margin: 0 }}>
            Dashboard{' '}
            <span className="muted small">
              {user.role === 'admin' ? 'all departments' : `${user.department} department`}
            </span>
          </h2>
          <div className="actions">
            {list.updatedAt > 0 && (
              <span className="muted small">
                Updated {new Date(list.updatedAt).toLocaleTimeString()}
              </span>
            )}
            <button type="button" className="secondary" onClick={refreshAll}>Refresh</button>
          </div>
        </div>
        {flash && <div className="notice" style={{ marginTop: '1rem' }}>{flash}</div>}
        <SummaryCards data={summary.data} filters={filters} onPick={setFilter} />
      </div>

      <div className="card">
        <div className="tabs">
          {TABS.map(([value, label]) => (
            <button
              key={label}
              type="button"
              aria-pressed={filters.status === value}
              className={`tab ${filters.status === value ? 'active' : ''}`}
              onClick={() => setFilter({ status: value })}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="filters">
          <label>
            Urgency
            <select value={filters.urgency} onChange={(e) => setFilter({ urgency: e.target.value })}>
              <option value="">Any</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </label>
          <label className="inline">
            <input
              type="checkbox"
              checked={filters.review}
              onChange={(e) => setFilter({ review: e.target.checked })}
            />
            Needs review only
          </label>
          <form
            className="actions"
            onSubmit={(e) => {
              e.preventDefault()
              setFilter({ q: search.trim() })
            }}
          >
            <label>
              Search
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="title or description"
              />
            </label>
            <button>Search</button>
            {filters.q && (
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  setSearch('')
                  setFilter({ q: '' })
                }}
              >
                Clear
              </button>
            )}
          </form>
        </div>
      </div>

      <div className="card">
        {actionError && <div className="error" style={{ marginBottom: '0.75rem' }}>{actionError}</div>}
        {list.error && (
          <div className="error" style={{ marginBottom: '0.75rem' }}>
            {list.error}{' '}
            <button type="button" className="secondary" onClick={refreshAll}>Try again</button>
          </div>
        )}
        {!list.data && !list.error && <p className="muted">Loading…</p>}
        {list.data && list.data.results.length === 0 && (
          <p className="muted">No incidents match these filters.</p>
        )}

        {list.data && list.data.results.length > 0 && (
          <>
            <ul className="list queue">
              {list.data.results.map((i) => (
                <li key={i.id}>
                  <div className="grow">
                    <Link to={`/incidents/${i.id}`}><strong>{i.title}</strong></Link>
                    <div className="muted small">
                      #{i.id} · {i.reporter_name} · {timeAgo(i.created_at)}
                      {i.assigned_to_name && ` · taken by ${i.assigned_to_name}`}
                      {i.workers.length > 0 && ` · ${i.workers.length} worker(s)`}
                    </div>
                    <div className="tags">
                      <UrgencyBadge value={i.urgency} />
                      <StatusBadge value={i.status} />
                      <span className="chip">{i.category}</span>
                      {i.department && <span className="chip">{i.department}</span>}
                      {i.needs_review && <span className="chip">needs review</span>}
                    </div>
                  </div>
                  {canTake(i) && (
                    <button type="button" disabled={takingId === i.id} onClick={() => take(i.id)}>
                      {takingId === i.id ? 'Taking…' : 'Take'}
                    </button>
                  )}
                </li>
              ))}
            </ul>
            <Pager
              page={filters.page}
              count={list.data.count}
              pageSize={PAGE_SIZE}
              hasPrev={Boolean(list.data.previous)}
              hasNext={Boolean(list.data.next)}
              onPage={(p) => setFilter({ page: p })}
            />
          </>
        )}
      </div>
    </>
  )
}