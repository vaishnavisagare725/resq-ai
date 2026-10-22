export default function Placeholder({ title, day }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <p className="muted">This page is built on {day}.</p>
    </div>
  )
}