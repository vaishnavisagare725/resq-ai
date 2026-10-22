import { useEffect, useMemo, useState } from 'react'

const same = (a, b) => a.name === b.name && a.size === b.size && a.lastModified === b.lastModified

export default function PhotoPicker({ files, onChange, max = 3, maxMb = 5 }) {
  const [problem, setProblem] = useState('')

  // temporary preview addresses, released when the list changes or the page closes
  const previews = useMemo(() => files.map((f) => URL.createObjectURL(f)), [files])
  useEffect(() => () => previews.forEach((u) => URL.revokeObjectURL(u)), [previews])

  function handlePick(e) {
    const picked = Array.from(e.target.files)
    e.target.value = '' // lets the same file be chosen again later

    const problems = []
    const accepted = []
    for (const f of picked) {
      if (files.some((x) => same(x, f))) continue // already added
      if (!f.type.startsWith('image/')) problems.push(`${f.name} is not an image.`)
      else if (f.size > maxMb * 1024 * 1024) problems.push(`${f.name} is larger than ${maxMb} MB.`)
      else accepted.push(f)
    }

    const room = Math.max(max - files.length, 0)
    if (accepted.length > room) problems.push(`You can add at most ${max} photos.`)
    setProblem(problems.join(' '))
    if (accepted.length) onChange([...files, ...accepted.slice(0, room)])
  }

  function remove(index) {
    setProblem('')
    onChange(files.filter((_, i) => i !== index))
  }

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        multiple
        onChange={handlePick}
        disabled={files.length >= max}
        aria-label="Add photos"
      />
      <p className="muted small">
        Up to {max} photos, {maxMb} MB each. {files.length}/{max} added.
      </p>
      {problem && <div className="error">{problem}</div>}
      {files.length > 0 && (
        <div className="photos">
          {files.map((f, i) => (
            <div className="thumb" key={`${f.name}-${f.size}-${f.lastModified}`}>
              <img src={previews[i]} alt={`Preview of ${f.name}`} />
              <button type="button" onClick={() => remove(i)} aria-label={`Remove ${f.name}`}>
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}