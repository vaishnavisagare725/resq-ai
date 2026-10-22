import { useEffect, useState } from 'react'
import api, { errorMessages } from '../api'

export default function useFetch(url, params = {}) {
  const paramsKey = JSON.stringify(params) // a stable text version, so a new object each render does not matter
  const [reload, setReload] = useState(0)
  const key = `${url}|${paramsKey}|${reload}`
  const [result, setResult] = useState({ key: '', data: null, error: '', status: 0 })

  useEffect(() => {
    let cancelled = false
    api
      .get(url, { params: JSON.parse(paramsKey) })
      .then((res) => {
        if (!cancelled) setResult({ key, data: res.data, error: '', status: res.status })
      })
      .catch((err) => {
        if (!cancelled) {
          setResult({
            key,
            data: null,
            error: errorMessages(err).join(' '),
            status: err.response?.status ?? 0,
          })
        }
      })
    return () => {
      cancelled = true
    }
  }, [url, paramsKey, key])

  const current = result.key === key // is this answer for the request we are showing now?
  return {
    data: current ? result.data : null,
    error: current ? result.error : '',
    status: current ? result.status : 0,
    loading: !current,
    reload: () => setReload((n) => n + 1),
  }
}