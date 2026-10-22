import { useCallback, useEffect, useState } from 'react'
import api, { clearTokens, getAccess, saveTokens } from '../api'
import { AuthContext } from './context'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  // if a token is stored we must ask the server who it belongs to, so start in "loading"
  const [loading, setLoading] = useState(Boolean(getAccess()))

  const logout = useCallback(() => {
    clearTokens()
    setUser(null)
  }, [])

  // on first load: stored token -> ask /auth/me/
  useEffect(() => {
    if (!getAccess()) return
    api
      .get('/auth/me/')
      .then((res) => setUser(res.data))
      .catch(() => clearTokens())
      .finally(() => setLoading(false))
  }, [])

  // the Axios interceptor fires this when the refresh token no longer works
  useEffect(() => {
    window.addEventListener('resq:logout', logout)
    return () => window.removeEventListener('resq:logout', logout)
  }, [logout])

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    saveTokens(data.access, data.refresh)
    setUser(data.user)
    return data.user
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}