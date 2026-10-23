export default function Pager({ page, count, pageSize, hasPrev, hasNext, onPage }) {
  const pages = Math.max(1, Math.ceil(count / pageSize))
  return (
    <div className="pager">
      <button type="button" className="secondary" disabled={!hasPrev} onClick={() => onPage(page - 1)}>
        ← Previous
      </button>
      <span className="muted small">
        Page {page} of {pages} · {count} incident(s)
      </span>
      <button type="button" className="secondary" disabled={!hasNext} onClick={() => onPage(page + 1)}>
        Next →
      </button>
    </div>
  )
}