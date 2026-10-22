import { Link, NavLink, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth'

const LINKS = {
  citizen: [['/report', 'Report'], ['/my-reports', 'My reports']],
  responder: [['/dashboard', 'Dashboard']],
  admin: [['/dashboard', 'Dashboard']],
  worker: [['/my-tasks', 'My tasks']],
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="navbar">
      <Link to="/" className="brand">ResQ AI</Link>
      <nav>
        {user &&
          (LINKS[user.role] || []).map(([to, label]) => (
            <NavLink key={to} to={to}>{label}</NavLink>
          ))}
      </nav>
      <div className="right">
        {user ? (
          <>
            <span>
              {user.username} <span className="chip">{user.role}</span>
            </span>
            <button onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <NavLink to="/login">Login</NavLink>
            <NavLink to="/register">Register</NavLink>
          </>
        )}
      </div>
    </header>
  )
}