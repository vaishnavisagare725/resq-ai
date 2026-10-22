import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

// ---- token storage (localStorage for the MVP; see the notes about the risk) ----
export const getAccess = () => localStorage.getItem('access')
export const getRefresh = () => localStorage.getItem('refresh')

export function saveTokens(access, refresh) {
  localStorage.setItem('access', access)
  if (refresh) localStorage.setItem('refresh', refresh)
}

export function clearTokens() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
}

// ---- the shared API client ----
const api = axios.create({ baseURL: API_URL })

// 1. attach the access token to every request
api.interceptors.request.use((config) => {
  const token = getAccess()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 2. on a 401, get a new access token once, then retry the original request
let refreshing = null // shared, so several 401s at once trigger only one refresh

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const status = error.response?.status
    const isAuthCall =
      original?.url?.includes('/auth/login/') || original?.url?.includes('/auth/refresh/')

    if (status === 401 && original && !original._retry && !isAuthCall && getRefresh()) {
      original._retry = true
      try {
        refreshing =
          refreshing ||
          axios
            .post(`${API_URL}/auth/refresh/`, { refresh: getRefresh() })
            .finally(() => {
              refreshing = null
            })
        const { data } = await refreshing
        saveTokens(data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        clearTokens()
        window.dispatchEvent(new Event('resq:logout')) // tells AuthProvider to log out
      }
    }
    return Promise.reject(error)
  },
)

// turn a DRF error response into a list of readable messages
export function errorMessages(err) {
  if (!err.response) return ['Cannot reach the server. Is Django running?']
  const data = err.response.data
  if (typeof data === 'string') return ['Something went wrong on the server.']
  if (data?.detail) return [].concat(data.detail)
  if (data && typeof data === 'object') {
    return Object.entries(data).flatMap(([field, msgs]) =>
      [].concat(msgs).map((m) => `${field}: ${m}`),
    )
  }
  return ['Something went wrong.']
}

export default api