import { useEffect } from 'react'
import useFetch from '../hooks/useFetch'
import IncidentMap from './IncidentMap'

const REFRESH_MS = 15000

export default function LiveMap({ height = 460 }) {
  const { data, error, reload } = useFetch('/incidents/map/')

  useEffect(() => {
    const timer = setInterval(() => {
      if (!document.hidden) reload()
    }, REFRESH_MS)
    return () => clearInterval(timer)
  }, [reload])

  return (
    <div>
      {error && (
        <div className="error" style={{ marginBottom: '0.75rem' }}>
          {error}{' '}
          <button type="button" className="secondary" onClick={reload}>Try again</button>
        </div>
      )}
      {!data && !error && <p className="muted">Loading map…</p>}
      {data && data.results.length === 0 && (
        <p className="muted">No active incidents to show.</p>
      )}
      {data && data.results.length > 0 && <IncidentMap incidents={data.results} height={height} />}
      {data?.truncated && (
        <p className="muted small">Showing only the 500 most urgent incidents.</p>
      )}
    </div>
  )
}