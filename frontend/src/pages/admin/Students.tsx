import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { listStudents, deleteStudent } from '@/api/students'
import { listClasses } from '@/api/classes'
import { listUsers } from '@/api/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import DataTable, { Column } from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import ErrorMessage from '@/components/ErrorMessage'
import { extractError } from '@/utils/helpers'
import type { Student, Class } from '@/types'

export default function Students(): React.ReactElement {
  const [students, setStudents] = useState<Student[]>([])
  const [classes, setClasses] = useState<Class[]>([])
  const [guardians, setGuardians] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)
  const [search, setSearch] = useState<string>('')
  const [classFilter, setClassFilter] = useState<string>('')
  const navigate = useNavigate()

  useEffect(() => {
    listClasses().then((res) => setClasses(res.data.data || [])).catch(() => {})
    listUsers({ role: 'guardian' }).then((res) => {
      const map: Record<string, string> = {}
      ;(res.data.data || []).forEach((u) => { map[u.id] = u.email })
      setGuardians(map)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    loadStudents()
  }, [page, search, classFilter])

  async function loadStudents(): Promise<void> {
    try {
      setLoading(true)
      setError(null)
      const params: { page: number; limit: number; search?: string; class_id?: string } = { page, limit: 20 }
      if (search) params.search = search
      if (classFilter) params.class_id = classFilter
      const res = await listStudents(params)
      setStudents(res.data.data || [])
      setTotalPages(res.data.pagination?.pages || 1)
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id: string): Promise<void> {
    if (!window.confirm('Are you sure you want to delete this student?')) return
    try {
      await deleteStudent(id)
      loadStudents()
    } catch (err: unknown) {
      alert(extractError(err))
    }
  }

  const columns: Column<Student>[] = [
    { label: 'Name', key: 'full_name' },
    { label: 'Roll Number', key: 'roll_number' },
    {
      label: 'Guardian',
      render: (row: Student) => row.guardian_name || guardians[row.guardian_id] || row.guardian_id,
    },
    { label: 'Date of Birth', key: 'date_of_birth' },
    { label: 'Status', render: (row: Student) => <StatusBadge status={row.is_active ? 'active' : 'inactive'} /> },
    {
      label: 'Actions',
      render: (row: Student) => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => navigate(`/admin/students/${row.id}/edit`)}>Edit</Button>
          <Button size="sm" variant="destructive" onClick={() => handleDelete(row.id)}>Delete</Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Students</h1>
        <Link to="/admin/students/new">
          <Button className="bg-slate-900 text-white hover:bg-slate-800">Add Student</Button>
        </Link>
      </div>

      <div className="flex gap-4 bg-white p-3 rounded-md border">
        <Input
          placeholder="Search by student name or roll number..."
          value={search}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => { setSearch(e.target.value); setPage(1) }}
          className="max-w-sm"
        />
        <select
          value={classFilter}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => { setClassFilter(e.target.value); setPage(1) }}
          className="border rounded px-3 py-2 text-sm bg-white border-input"
        >
          <option value="">All Classes</option>
          {classes.map((c) => (
            <option key={c.id} value={c.id}>{c.name} {c.section}</option>
          ))}
        </select>
      </div>

      <ErrorMessage message={error} />
      <DataTable<Student> columns={columns} data={students} loading={loading} emptyMessage="No students found matching your criteria" />

      {totalPages > 1 && (
        <div className="flex justify-between items-center pt-2">
          <span className="text-sm text-slate-600">Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
            <Button size="sm" variant="outline" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</Button>
          </div>
        </div>
      )}
    </div>
  )
}

