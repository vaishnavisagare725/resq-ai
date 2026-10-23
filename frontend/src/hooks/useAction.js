import { useState } from 'react'
import { errorMessages } from '../api'

// Wraps "run an async action" with busy and error state, so buttons don't repeat try/catch.
export default function useAction() {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function run(task) {
    setBusy(true)
    setError('')
    try {
      await task()
      return true
    } catch (err) {
      setError(errorMessages(err).join(' '))
      return false
    } finally {
      setBusy(false)
    }
  }

  return { busy, error, run }
}