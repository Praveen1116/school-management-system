import React from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import StatusBadge from './StatusBadge'
import { Button } from '@/components/ui/button'

const NAV_LINKS: Record<string, Array<{ label: string; to: string }>> = {
  admin: [
    { label: 'Dashboard', to: '/admin/dashboard' },
    { label: 'Admins', to: '/admin/admins' },
    { label: 'Students', to: '/admin/students' },
    { label: 'Teachers', to: '/admin/teachers' },
    { label: 'Classes', to: '/admin/classes' },
    { label: 'Subjects', to: '/admin/subjects' },
    { label: 'Attendance', to: '/admin/attendance' },
    { label: 'Exams', to: '/admin/exams' },
    { label: 'Fees', to: '/admin/fees' },
    { label: 'Audit Logs', to: '/admin/audit-logs' },
  ],
  teacher: [
    { label: 'Dashboard', to: '/teacher/dashboard' },
    { label: 'My Classes', to: '/teacher/classes' },
    { label: 'Attendance', to: '/teacher/attendance' },
    { label: 'Results', to: '/teacher/results' },
  ],
  guardian: [
    { label: 'Dashboard', to: '/guardian/dashboard' },
    { label: 'Attendance', to: '/guardian/attendance' },
    { label: 'Results', to: '/guardian/results' },
    { label: 'Fees', to: '/guardian/fees' },
  ],
}

export default function Layout(): React.ReactElement {
  const { user, logout } = useAuth()
  const links = (user && NAV_LINKS[user.role]) || []

  return (
    <div className="flex h-screen bg-slate-50">
      <aside className="w-64 border-r border-slate-200 bg-white flex flex-col justify-between">
        <div>
          <div className="h-16 flex items-center px-6 border-b border-slate-200">
            <span className="font-bold text-slate-900 text-lg">School Portal</span>
          </div>
          <nav className="p-4 space-y-1">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-100 text-slate-900 font-semibold'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="p-4 border-t border-slate-200">
          <Button
            variant="outline"
            className="w-full text-slate-700"
            onClick={logout}
          >
            Logout
          </Button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-6">
          <span className="text-sm font-medium text-slate-600">
            Welcome back, <strong className="text-slate-900">{user?.email}</strong>
          </span>
          <StatusBadge status={user?.role} />
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

