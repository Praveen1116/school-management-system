import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { listTeachers, deleteTeacher } from '@/api/teachers'
import { Button } from '@/components/ui/button'
import DataTable, { Column } from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import ErrorMessage from '@/components/ErrorMessage'
import { extractError } from '@/utils/helpers'
import type { Teacher } from '@/types'

export default function Teachers(): React.ReactElement {
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadTeachers()
  }, [])

  async function loadTeachers(): Promise<void> {
    try {
      setLoading(true)
      setError(null)
      const res = await listTeachers()
      setTeachers(res.data.data || [])
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id: string): Promise<void> {
    if (!window.confirm('Are you sure you want to delete this teacher?')) return
    try {
      await deleteTeacher(id)
      loadTeachers()
    } catch (err: unknown) {
      alert(extractError(err))
    }
  }

  const columns: Column<Teacher>[] = [
    { label: 'Name', key: 'full_name' },
    { label: 'Employee Code', key: 'employee_code' },
    { label: 'Email', render: (row: Teacher) => row.email || '—' },
    {
      label: 'Status',
      render: (row: Teacher) => <StatusBadge status={row.is_active ? 'active' : 'inactive'} />,
    },
    {
      label: 'Actions',
      render: (row: Teacher) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => navigate(`/admin/teachers/${row.id}/edit`)}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => handleDelete(row.id)}
          >
            Delete
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Teachers</h1>
        <Link to="/admin/teachers/new">
          <Button className="bg-slate-900 text-white hover:bg-slate-800">Add Teacher</Button>
        </Link>
      </div>

      <ErrorMessage message={error} />

      <DataTable<Teacher>
        columns={columns}
        data={teachers}
        loading={loading}
        emptyMessage="No teachers registered yet"
      />
    </div>
  )
}

