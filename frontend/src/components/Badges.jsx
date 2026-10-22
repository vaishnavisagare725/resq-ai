const STATUS_TEXT = { open: 'Open', assigned: 'Assigned', resolved: 'Resolved' }

export function UrgencyBadge({ value }) {
  return <span className={`badge ${value}`}>{value}</span>
}

export function StatusBadge({ value }) {
  return <span className={`chip status-${value}`}>{STATUS_TEXT[value] || value}</span>
}