import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import api, { errorMessages } from '../api'
import { useAuth } from '../auth/useAuth'

const ROLE_TEXT = {
  citizen: 'Report emergencies and follow their progress.',
  responder: 'Take cases in your department, correct the AI, and assign workers.',
  worker: 'See the incidents you are assigned to and resolve them.',
  admin: 'You can see and manage everything.',
}

export default function Home() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    api
      .get('/incidents/', { params: { sort: 'urgency' } })
      .then((res) => {
        if (!cancelled) setData(res.data)
      })
      .catch((err) => {
        if (!cancelled) setError(errorMessages(err).join(' '))
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <>
      <div className="card">
        <h2>Welcome, {user.username}</h2>
        <p>
          <span className="chip">{user.role}</span>{' '}
          {user.department && <span className="chip">{user.department}</span>}
        </p>
        <p className="muted">{ROLE_TEXT[user.role]}</p>
      </div>

      <div className="card">
        <h3>Incidents you can see {data && `(${data.count})`}</h3>
        {error && <div className="error">{error}</div>}
        {!data && !error && <p className="muted">Loading…</p>}
        {data && data.results.length === 0 && <p className="muted">Nothing here yet.</p>}
        <ul className="list">
          {data?.results.slice(0, 5).map((i) => (
            <li key={i.id}>
              <Link to={`/incidents/${i.id}`}>{i.title}</Link>
              <span>
                <span className={`badge ${i.urgency}`}>{i.urgency}</span>{' '}
                <span className="chip">{i.status}</span>
              </span>
            </li>
          ))}
        </ul>
      </div>
    </>
  )
}