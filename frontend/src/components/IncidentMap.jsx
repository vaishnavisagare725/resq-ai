import { useEffect } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import { Link } from 'react-router'
import 'leaflet/dist/leaflet.css'
import { UrgencyBadge } from './Badges'

const COLORS = { critical: '#b42318', high: '#e8590c', medium: '#f59f00', low: '#2f9e44' }
const RADIUS = { critical: 12, high: 10, medium: 8, low: 7 }
const RESOLVED_COLOR = '#98a2b3'
const DEFAULT_CENTER = [20.5937, 78.9629] // India; change it to your own city
const DEFAULT_ZOOM = 5

// Zoom to show every pin, but ONLY when the set of incidents changes,
// so a refresh every 15 seconds doesn't undo what the user is looking at.
function FitToPoints({ points }) {
  const map = useMap()
  const idsKey = points.map((p) => p.id).join(',')

  useEffect(() => {
    if (points.length === 0) return
    if (points.length === 1) {
      map.setView([points[0].latitude, points[0].longitude], 15)
    } else {
      map.fitBounds(
        points.map((p) => [p.latitude, p.longitude]), // Leaflet order: [latitude, longitude]
        { padding: [40, 40], maxZoom: 15 },
      )
    }
    // only re-run when the incident ids change, not on every refresh
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idsKey, map])

  return null
}

export default function IncidentMap({ incidents, height = 420, linkToDetail = true, showLegend = true }) {
  return (
    <>
      <MapContainer
        center={DEFAULT_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height, width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitToPoints points={incidents} />
        {incidents.map((i) => {
          const resolved = i.status === 'resolved'
          const color = resolved ? RESOLVED_COLOR : COLORS[i.urgency] || RESOLVED_COLOR
          return (
            <CircleMarker
              key={i.id}
              center={[i.latitude, i.longitude]}
              radius={RADIUS[i.urgency] || 7}
              pathOptions={{ color, fillColor: color, fillOpacity: resolved ? 0.35 : 0.7, weight: 2 }}
            >
              <Popup>
                <strong>{i.title}</strong>
                <br />
                <UrgencyBadge value={i.urgency} /> {i.status}
                {linkToDetail && (
                  <>
                    <br />
                    <Link to={`/incidents/${i.id}`}>Open incident</Link>
                  </>
                )}
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>

      {showLegend && (
        <div className="legend">
          {Object.entries(COLORS).map(([name, color]) => (
            <span key={name}>
              <span className="dot" style={{ background: color }} /> {name}
            </span>
          ))}
        </div>
      )}
    </>
  )
}