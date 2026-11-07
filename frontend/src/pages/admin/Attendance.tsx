import React, { useState, useEffect } from 'react'
import { listClasses } from '@/api/classes'
import { getClassAttendance, updateAttendance } from '@/api/attendance'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import DataTable, { Column } from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import ErrorMessage from '@/components/ErrorMessage'
import { formatDate, extractError } from '@/utils/helpers'
import type { Class, AttendanceRecord } from '@/types'

interface AttendanceCounts {
  total: number
  present: number
  absent: number
  late: number
}

export default function AdminAttendance(): React.ReactElement {
  const today = new Date().toISOString().split('T')[0]
  const lastWeek = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

  const [classes, setClasses] = useState<Class[]>([])
  const [selectedClass, setSelectedClass] = useState<string>('')
  const [dateFrom, setDateFrom] = useState<string>(lastWeek)
  const [dateTo, setDateTo] = useState<string>(today)
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listClasses().then((res) => setClasses(res.data.data || [])).catch(() => {})
  }, [])

  useEffect(() => {
    if (selectedClass && dateFrom && dateTo) {
      loadAttendance()
    }
  }, [selectedClass, dateFrom, dateTo])

  async function loadAttendance(): Promise<void> {
    try {
      setLoading(true)
      setError(null)
      const res = await getClassAttendance(selectedClass, { date_from: dateFrom, date_to: dateTo })
      const list = res.data.data?.records || []
      setRecords(list)
    } catch (err: unknown) {
      setError(extractError(err))
      setRecords([])
    } finally {
      setLoading(false)
    }
  }

  async function handleStatusChange(recordId: string, newStatus: string): Promise<void> {
    try {
      await updateAttendance(recordId, { status: newStatus })
      await loadAttendance()
    } catch (err: unknown) {
      alert(extractError(err))
    }
  }

  const counts: AttendanceCounts = records.reduce<AttendanceCounts>(
    (acc, r) => {
      acc.total += 1
      if (r.status === 'present') acc.present += 1
      else if (r.status === 'absent') acc.absent += 1
      else if (r.status === 'late') acc.late += 1
      return acc
    },
    { total: 0, present: 0, absent: 0, late: 0 }
  )

  const columns: Column<AttendanceRecord>[] = [
    { label: 'Student', render: (r: AttendanceRecord) => r.student_name || r.student_id },
    { label: 'Roll Number', key: 'roll_number' },
    { label: 'Date', render: (r: AttendanceRecord) => formatDate(r.attendance_date) },
    { label: 'Session', render: (r: AttendanceRecord) => r.session?.replace('_', ' ') },
    { label: 'Status', render: (r: AttendanceRecord) => <StatusBadge status={r.status} /> },
    {
      label: 'Actions',
      render: (r: AttendanceRecord) => (
        <select
          value={r.status}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleStatusChange(r.id, e.target.value)}
          className="border rounded px-2 py-1 text-xs bg-white"
        >
          <option value="present">Present</option>
          <option value="absent">Absent</option>
          <option value="late">Late</option>
        </select>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-900">Attendance Management</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-white p-4 rounded-md border">
        <div>
          <Label>Select Class</Label>
          <select
            value={selectedClass}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedClass(e.target.value)}
            className="w-full mt-1 border rounded p-2 text-sm bg-white"
          >
            <option value="">Choose a class</option>
            {classes.map((c) => (
              <option key={c.id} value={c.id}>{c.name} {c.section}</option>
            ))}
          </select>
        </div>
        <div>
          <Label>From Date</Label>
          <Input type="date" value={dateFrom} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDateFrom(e.target.value)} className="mt-1" />
        </div>
        <div>
          <Label>To Date</Label>
          <Input type="date" value={dateTo} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDateTo(e.target.value)} className="mt-1" />
        </div>
      </div>

      {selectedClass && (
        <div className="bg-slate-100 p-3 rounded text-sm font-medium text-slate-800 flex gap-6">
          <span>Total: <strong>{counts.total}</strong></span>
          <span className="text-green-700">Present: <strong>{counts.present}</strong></span>
          <span className="text-red-700">Absent: <strong>{counts.absent}</strong></span>
          <span className="text-yellow-700">Late: <strong>{counts.late}</strong></span>
        </div>
      )}

      <ErrorMessage message={error} />
      <DataTable<AttendanceRecord>
        columns={columns}
        data={records}
        loading={loading}
        emptyMessage={selectedClass ? 'No attendance records found for selected period' : 'Select a class to view attendance records'}
      />
    </div>
  )
}

