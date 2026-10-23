const CARDS = [
  { key: 'open', label: 'Open', filter: { status: 'open', urgency: '', review: false } },
  {
    key: 'critical_open',
    label: 'Critical, not taken',
    tone: 'critical',
    filter: { status: 'open', urgency: 'critical', review: false },
  },
  {
    key: 'needs_review_open',
    label: 'Needs review',
    filter: { status: 'open', urgency: '', review: true },
  },
  { key: 'assigned', label: 'In progress', filter: { status: 'assigned', urgency: '', review: false } },
  { key: 'resolved', label: 'Resolved', filter: { status: 'resolved', urgency: '', review: false } },
]

export default function SummaryCards({ data, filters, onPick }) {
  return (
    <div className="stats">
      {CARDS.map((c) => {
        const active =
          filters.status === c.filter.status &&
          filters.urgency === c.filter.urgency &&
          filters.review === c.filter.review
        return (
          <button
            key={c.key}
            type="button"
            className={`stat ${c.tone || ''} ${active ? 'active' : ''}`}
            aria-pressed={active}
            onClick={() => onPick(c.filter)}
          >
            <span className="num">{data ? data[c.key] : '–'}</span>
            <span className="lbl">{c.label}</span>
          </button>
        )
      })}
    </div>
  )
}