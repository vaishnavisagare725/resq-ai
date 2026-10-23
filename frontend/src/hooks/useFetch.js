import { useCallback, useEffect, useState } from 'react'
import api, { errorMessages } from '../api'

export default function useFetch(url, params = {}) {
  const paramsKey = JSON.stringify(params) // a stable text version of the params
  const [reload, setReload] = useState(0)
  const key = `${url}|${paramsKey}|${reload}`
  const [result, setResult] = useState({ key: '', url: '', data: null, error: '', status: 0, at: 0 })

  useEffect(() => {
    let cancelled = false
    api
      .get(url, { params: JSON.parse(paramsKey) })
      .then((res) => {
        if (!cancelled) {
          setResult({ key, url, data: res.data, error: '', status: res.status, at: Date.now() })
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setResult((prev) => ({
            key,
            url,
            data: prev.url === url ? prev.data : null, // keep what we already had for this URL
            error: errorMessages(err).join(' '),
            status: err.response?.status ?? 0,
            at: prev.url === url ? prev.at : 0,
          }))
        }
      })
    return () => {
      cancelled = true
    }
  }, [url, paramsKey, key])

  const reloadNow = useCallback(() => setReload((n) => n + 1), [])
  const current = result.key === key // is the answer for the request we are showing now?
  return {
    data: result.url === url ? result.data : null, // stale-while-revalidate
    error: current ? result.error : '',
    status: current ? result.status : 0,
    loading: !current,
    updatedAt: result.url === url ? result.at : 0,
    reload: reloadNow,
  }
}