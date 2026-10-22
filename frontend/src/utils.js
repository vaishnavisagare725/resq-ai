export const formatDate = (iso) => (iso ? new Date(iso).toLocaleString() : '')

// A plain link to OpenStreetMap, no API key and no extra library
export const mapLink = (lat, lng) =>
  `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=16/${lat}/${lng}`