export const formatDate = (iso) => (iso ? new Date(iso).toLocaleString() : '')

// A plain link to OpenStreetMap, no API key and no extra library
export const mapLink = (lat, lng) =>
  `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=16/${lat}/${lng}`

// "5 min ago"
export function timeAgo(iso) {
  const seconds = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000))
  if (seconds < 60) return 'just now'
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours} h ago`
  return `${Math.round(hours / 24)} d ago`
}