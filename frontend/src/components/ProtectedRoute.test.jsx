import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuth } from '../auth/useAuth'
import ProtectedRoute from './ProtectedRoute'

vi.mock('../auth/useAuth', () => ({ useAuth: vi.fn() }))

function renderAt(props = {}) {
  return render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Routes>
        <Route path="/login" element={<p>login page</p>} />
        <Route path="/" element={<p>home page</p>} />
        <Route
          path="/dashboard"
          element={<ProtectedRoute {...props}><p>secret page</p></ProtectedRoute>}
        />
      </Routes>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  beforeEach(() => vi.clearAllMocks())

  it('waits while it checks who the user is', () => {
    useAuth.mockReturnValue({ user: null, loading: true })
    renderAt()
    expect(screen.getByText('Loading…')).toBeInTheDocument()
    expect(screen.queryByText('login page')).not.toBeInTheDocument()
  })

  it('sends a visitor to the login page', () => {
    useAuth.mockReturnValue({ user: null, loading: false })
    renderAt()
    expect(screen.getByText('login page')).toBeInTheDocument()
  })

  it('sends the wrong role home', () => {
    useAuth.mockReturnValue({ user: { role: 'citizen' }, loading: false })
    renderAt({ roles: ['responder', 'admin'] })
    expect(screen.getByText('home page')).toBeInTheDocument()
  })

  it('lets the right role in', () => {
    useAuth.mockReturnValue({ user: { role: 'responder' }, loading: false })
    renderAt({ roles: ['responder', 'admin'] })
    expect(screen.getByText('secret page')).toBeInTheDocument()
  })

  it('lets any logged-in user in when no roles are required', () => {
    useAuth.mockReturnValue({ user: { role: 'citizen' }, loading: false })
    renderAt()
    expect(screen.getByText('secret page')).toBeInTheDocument()
  })
})