import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { getDashboardPath } from '@/utils/helpers'
import Spinner from './Spinner'

interface Props {
  allowedRoles?: Array<'admin' | 'teacher' | 'guardian'>
}

export default function ProtectedRoute({ allowedRoles = [] }: Props): React.ReactElement {
  const { user, loading } = useAuth()

  if (loading) {
    return <Spinner />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to={getDashboardPath(user.role)} replace />
  }

  return <Outlet />
}

