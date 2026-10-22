import { useState } from 'react'
import { Link } from 'react-router'
import api, { errorMessages } from '../api'
import { UrgencyBadge } from '../components/Badges'
import PhotoPicker from '../components/PhotoPicker'

const EMPTY = { title: '', description: '', latitude: '', longitude: '' }

const LOCATION_ERRORS = {
  1: 'Location permission was denied. Allow it in the browser, or type the coordinates.',
  2: 'Your location is unavailable right now. Please type the coordinates.',
  3: 'Finding your location took too long. Try again, or type the coordinates.',
}

// Instant feedback only. The Django API validates everything again.
function validate(form) {
  const errors = []
  if (!form.title.trim()) errors.push('Please give the report a short title.')
  if (form.description.trim().length < 10) {
    errors.push('Please describe the emergency in at least 10 characters.')
  }
  const lat = Number(form.latitude)
  const lng = Number(form.longitude)
  if (form.latitude.trim() === '' || Number.isNaN(lat) || lat < -90 || lat > 90) {
    errors.push('Latitude must be a number between -90 and 90.')
  }
  if (form.longitude.trim() === '' || Number.isNaN(lng) || lng < -180 || lng > 180) {
    errors.push('Longitude must be a number between -180 and 180.')
  }
  return errors
}

// upload one photo at a time; return the files that failed
async function uploadPhotos(incidentId, list) {
  const failed = []
  for (const file of list) {
    const data = new FormData()
    data.append('image', file) // the field name must be "image"
    try {
      await api.post(`/incidents/${incidentId}/images/`, data)
    } catch {
      failed.push(file)
    }
  }
  return failed
}

export default function ReportIncident() {
  const [form, setForm] = useState(EMPTY)
  const [files, setFiles] = useState([])
  const [errors, setErrors] = useState([])
  const [busy, setBusy] = useState(false)
  const [locMsg, setLocMsg] = useState('')
  const [created, setCreated] = useState(null) // the saved incident, once it exists
  const [failed, setFailed] = useState([]) // photos that did not upload

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  function fillLocation() {
    if (!('geolocation' in navigator)) {
      setLocMsg('This browser cannot share its location. Please type the coordinates.')
      return
    }
    setLocMsg('Finding your location…')
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setForm((f) => ({
          ...f,
          latitude: pos.coords.latitude.toFixed(6),
          longitude: pos.coords.longitude.toFixed(6),
        }))
        setLocMsg(`Location found (accurate to about ${Math.round(pos.coords.accuracy)} m).`)
      },
      (err) => setLocMsg(LOCATION_ERRORS[err.code] || 'Could not get your location.'),
      { enableHighAccuracy: true, timeout: 10000 },
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (busy) return
    const problems = validate(form)
    if (problems.length) {
      setErrors(problems)
      return
    }
    setErrors([])
    setBusy(true)
    try {
      const { data } = await api.post('/incidents/', {
        title: form.title.trim(),
        description: form.description.trim(),
        latitude: Number(form.latitude),
        longitude: Number(form.longitude),
      })
      setCreated(data) // the report exists now, even if a photo fails below
      setFailed(await uploadPhotos(data.id, files))
    } catch (err) {
      setErrors(errorMessages(err))
    } finally {
      setBusy(false)
    }
  }

  async function retryFailed() {
    setBusy(true)
    setFailed(await uploadPhotos(created.id, failed))
    setBusy(false)
  }

  function reportAnother() {
    setForm(EMPTY)
    setFiles([])
    setCreated(null)
    setFailed([])
    setLocMsg('')
    setErrors([])
  }

  // ---- after the report is saved: show what the AI decided ----
  if (created) {
    return (
      <div className="card">
        <h2>Report received</h2>
        <p className="muted">Reference #{created.id}</p>

        <div className="notice">
          <div className="tags">
            <strong>AI assessment:</strong>
            <UrgencyBadge value={created.urgency} />
            <span className="chip">{created.category}</span>
            {created.department && <span className="chip">{created.department}</span>}
          </div>
          <p className="small">{created.ai_reason}</p>
          <p>
            {created.needs_review
              ? 'The system was not sure about this report, so a responder will review it.'
              : `Your report was sent to the ${created.department} team.`}
          </p>
        </div>

        {files.length > 0 &&
          (busy ? (
            <p className="muted">Uploading photos…</p>
          ) : failed.length === 0 ? (
            <p>All {files.length} photo(s) uploaded.</p>
          ) : (
            <div className="error">
              {failed.length} photo(s) could not be uploaded.{' '}
              <button type="button" className="secondary" onClick={retryFailed}>
                Try again
              </button>
            </div>
          ))}

        <div className="actions">
          <Link to={`/incidents/${created.id}`} className="button">View report</Link>
          <button type="button" className="secondary" onClick={reportAnother}>
            Report another
          </button>
        </div>
      </div>
    )
  }

  // ---- the form ----
  return (
    <div className="card">
      <h2>Report an emergency</h2>
      <div className="notice">
        In a life-threatening emergency, call your local emergency number first (112 in India).
        This system helps responders prioritise reports. It does not replace an emergency call.
      </div>

      <form className="form wide" onSubmit={handleSubmit} noValidate>
        <label>
          Title
          <input
            name="title"
            value={form.title}
            onChange={update}
            maxLength={200}
            placeholder="e.g. Fire in the market building"
          />
        </label>

        <label>
          What is happening?
          <textarea
            name="description"
            value={form.description}
            onChange={update}
            placeholder="How many people, any injuries, any danger nearby…"
          />
        </label>

        <div>
          <span className="label">Location</span>
          <div className="actions">
            <button type="button" className="secondary" onClick={fillLocation}>
              Use my location
            </button>
            {locMsg && <span className="muted small">{locMsg}</span>}
          </div>
          <div className="two">
            <label>
              Latitude
              <input
                name="latitude"
                inputMode="decimal"
                value={form.latitude}
                onChange={update}
                placeholder="18.520000"
              />
            </label>
            <label>
              Longitude
              <input
                name="longitude"
                inputMode="decimal"
                value={form.longitude}
                onChange={update}
                placeholder="73.850000"
              />
            </label>
          </div>
        </div>

        <div>
          <span className="label">Photos (optional)</span>
          <PhotoPicker files={files} onChange={setFiles} />
        </div>

        {errors.map((m) => (
          <div className="error" key={m}>{m}</div>
        ))}
        <button disabled={busy}>{busy ? 'Sending…' : 'Send report'}</button>
      </form>
    </div>
  )
}