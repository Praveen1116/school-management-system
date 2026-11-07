import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getMyStudents, getStudentAttendance } from '@/api/guardian'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import DataTable, { Column } from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import ErrorMessage from '@/components/ErrorMessage'
import { formatDate, extractError } from '@/utils/helpers'
import type { Student, AttendanceRecord, AttendanceSummary } from '@/types'

interface GuardianAttendanceData {
  records: AttendanceRecord[]
  summary?: AttendanceSummary
  attendance_rate?: number
}

export default function GuardianAttendance(): React.ReactElement {
  const [searchParams] = useSearchParams()
  const initialStudentId = searchParams.get('studentId') || ''

  const [students, setStudents] = useState<Student[]>([])
  const [selectedStudentId, setSelectedStudentId] = useState<string>(initialStudentId)
  const [dateFrom, setDateFrom] = useState<string>(() => {
    const d = new Date()
    d.setDate(d.getDate() - 30)
    return d.toISOString().split('T')[0]
  })
  const [dateTo, setDateTo] = useState<string>(() => new Date().toISOString().split('T')[0])
  const [attendanceData, setAttendanceData] = useState<GuardianAttendanceData | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getMyStudents()
      .then((res) => {
        const list = res.data.data || []
        setStudents(list)
        if (!selectedStudentId && list.length > 0) {
          setSelectedStudentId(list[0].id)
        }
      })
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedStudentId) return
    loadAttendance()
  }, [selectedStudentId, dateFrom, dateTo])

  async function loadAttendance(): Promise<void> {
    try {
      setLoading(true)
      setError(null)
      const res = await getStudentAttendance(selectedStudentId, {
        date_from: dateFrom,
        date_to: dateTo,
      })
      setAttendanceData(res.data.data)
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  const records = attendanceData?.records || []
  const summary = attendanceData?.summary || {
    total: records.length,
    present: records.filter((r) => r.status === 'present').length,
    absent: records.filter((r) => r.status === 'absent').length,
    late: records.filter((r) => r.status === 'late').length,
    percentage: attendanceData?.attendance_rate || 0,
  }

  const columns: Column<AttendanceRecord>[] = [
    { label: 'Date', render: (r: AttendanceRecord) => formatDate(r.attendance_date) },
    { label: 'Session', render: (r: AttendanceRecord) => r.session?.replace('_', ' ') },
    { label: 'Status', render: (r: AttendanceRecord) => <StatusBadge status={r.status} /> },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Attendance History</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-white p-4 rounded-md border border-slate-200">
        {students.length > 1 && (
          <div>
            <Label>Select Child</Label>
            <select
              value={selectedStudentId}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedStudentId(e.target.value)}
              className="w-full mt-1 border border-slate-300 rounded p-2 text-sm bg-white"
            >
              {students.map((s) => (
                <option key={s.id} value={s.id}>{s.full_name} ({s.roll_number})</option>
              ))}
            </select>
          </div>
        )}
        <div>
          <Label>From Date</Label>
          <Input type="date" value={dateFrom} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDateFrom(e.target.value)} className="mt-1" />
        </div>
        <div>
          <Label>To Date</Label>
          <Input type="date" value={dateTo} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDateTo(e.target.value)} className="mt-1" />
        </div>
      </div>

      <div className="bg-slate-100 p-4 rounded-md flex flex-wrap gap-6 text-sm font-medium text-slate-800">
        <span>Total: <strong>{summary.total ?? records.length}</strong></span>
        <span className="text-green-700">Present: <strong>{summary.present}</strong></span>
        <span className="text-red-700">Absent: <strong>{summary.absent}</strong></span>
        <span className="text-yellow-700">Late: <strong>{summary.late}</strong></span>
        {summary.percentage != null && <span className="text-slate-900">Attendance: <strong>{summary.percentage}%</strong></span>}
      </div>

      <ErrorMessage message={error} />
      <DataTable<AttendanceRecord> columns={columns} data={records} loading={loading} emptyMessage="No attendance records found for this period" />
    </div>
  )
}

