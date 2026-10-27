import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuth } from '../auth/useAuth'
import Login from './Login'

vi.mock('../auth/useAuth', () => ({ useAuth: vi.fn() }))

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<p>home page</p>} />
      </Routes>
    </MemoryRouter>,
  )
}

async function fillAndSubmit(username, password) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('Username'), username)
  await user.type(screen.getByLabelText('Password'), password)
  await user.click(screen.getByRole('button', { name: 'Log in' }))
}

describe('Login page', () => {
  beforeEach(() => vi.clearAllMocks())

  it('sends the trimmed username and the password', async () => {
    const login = vi.fn().mockResolvedValue({})
    useAuth.mockReturnValue({ user: null, login })
    renderLogin()
    await fillAndSubmit('  ravi  ', 'Secret-1')
    expect(login).toHaveBeenCalledWith('ravi', 'Secret-1')
  })

  it('says so when the password is wrong', async () => {
    useAuth.mockReturnValue({ user: null, login: vi.fn().mockRejectedValue({ response: { status: 401 } }) })
    renderLogin()
    await fillAndSubmit('ravi', 'wrong')
    expect(await screen.findByText('Wrong username or password.')).toBeInTheDocument()
  })

  it('says so when the server cannot be reached', async () => {
    useAuth.mockReturnValue({ user: null, login: vi.fn().mockRejectedValue({}) })
    renderLogin()
    await fillAndSubmit('ravi', 'Secret-1')
    expect(await screen.findByText(/Cannot reach the server/)).toBeInTheDocument()
  })

  it('skips the form when already logged in', () => {
    useAuth.mockReturnValue({ user: { username: 'ravi' }, login: vi.fn() })
    renderLogin()
    expect(screen.getByText('home page')).toBeInTheDocument()
  })
})