import React, { useState, useEffect } from 'react'
import { listUsers, deleteUser } from '@/api/users'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'
import DataTable, { Column } from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import ErrorMessage from '@/components/ErrorMessage'
import AdminFormModal from './AdminFormModal'
import { extractError, formatDate } from '@/utils/helpers'
import type { User } from '@/types'

export default function Admins(): React.ReactElement {
  const { user: currentUser } = useAuth()
  const [admins, setAdmins] = useState<User[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState<boolean>(false)

  useEffect(() => { loadAdmins() }, [])

  async function loadAdmins(): Promise<void> {
    try {
      setLoading(true)
      setError(null)
      const res = await listUsers({ role: 'admin' })
      setAdmins(res.data.data || [])
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleDeactivate(id: string): Promise<void> {
    if (!window.confirm('Deactivate this administrator?')) return
    try {
      await deleteUser(id)
      await loadAdmins()
    } catch (err: unknown) {
      alert(extractError(err))
    }
  }

  const columns: Column<User>[] = [
    { label: 'Name', render: (u: User) => <span className="font-medium text-slate-900">{u.full_name || '—'}</span> },
    { label: 'Email', key: 'email' },
    { label: 'Status', render: (u: User) => <StatusBadge status={u.is_active ? 'active' : 'inactive'} /> },
    { label: 'Joined', render: (u: User) => formatDate(u.created_at) },
    {
      label: 'Actions',
      render: (u: User) => (
        u.id !== currentUser?.id && u.is_active ? (
          <Button size="sm" variant="destructive" onClick={() => handleDeactivate(u.id)}>
            Deactivate
          </Button>
        ) : (
          <span className="text-xs text-slate-400 italic">{u.id === currentUser?.id ? 'You' : '—'}</span>
        )
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Administrator Accounts</h1>
          <p className="text-sm text-slate-500">Manage administrator access and invite additional school admins</p>
        </div>
        <Button onClick={() => setModalOpen(true)} className="bg-slate-900 text-white hover:bg-slate-800">
          Add Admin
        </Button>
      </div>

      <ErrorMessage message={error} />

      <DataTable<User>
        columns={columns}
        data={admins}
        loading={loading}
        emptyMessage="No administrators found"
      />

      <AdminFormModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={() => {
          setModalOpen(false)
          loadAdmins()
        }}
      />
    </div>
  )
}
