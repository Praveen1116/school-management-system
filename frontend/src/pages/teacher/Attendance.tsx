import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { listClasses, getClassStudents } from '@/api/classes'
import { recordAttendance } from '@/api/attendance'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import ErrorMessage from '@/components/ErrorMessage'
import Spinner from '@/components/Spinner'
import { extractError } from '@/utils/helpers'
import type { Class, Student } from '@/types'

export default function TeacherAttendance(): React.ReactElement {
  const [classes, setClasses] = useState<Class[]>([])
  const [selectedClass, setSelectedClass] = useState<string>('')
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0])
  const [students, setStudents] = useState<Student[]>([])
  const [attendanceMap, setAttendanceMap] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState<boolean>(true)
  const [studentsLoading, setStudentsLoading] = useState<boolean>(false)
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  useEffect(() => {
    listClasses()
      .then((res) => setClasses(res.data.data || []))
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedClass) {
      setStudents([])
      return
    }
    setStudentsLoading(true)
    setError(null)
    setSuccessMsg(null)
    getClassStudents(selectedClass)
      .then((res) => {
        const list = res.data.data || []
        setStudents(list)
        const initialMap: Record<string, string> = {}
        list.forEach((s) => { initialMap[s.id] = 'present' })
        setAttendanceMap(initialMap)
      })
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setStudentsLoading(false))
  }, [selectedClass])

  async function handleSubmit(): Promise<void> {
    setSubmitting(true)
    setError(null)
    setSuccessMsg(null)
    let recorded = 0
    let skipped = 0
    try {
      for (const student of students) {
        try {
          await recordAttendance({
            student_id: student.id,
            class_id: selectedClass,
            attendance_date: date,
            session: 'full_day',
            status: attendanceMap[student.id] || 'present',
          })
          recorded += 1
        } catch (err: unknown) {
          if (axios.isAxiosError(err) && err.response?.status === 409) {
            skipped += 1
          } else {
            throw err
          }
        }
      }
      setSuccessMsg(`Attendance saved: ${recorded} recorded, ${skipped} already existed.`)
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Mark Attendance</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white p-4 rounded-md border border-slate-200">
        <div>
          <Label>Select Assigned Class</Label>
          <select
            value={selectedClass}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedClass(e.target.value)}
            className="w-full mt-1 border rounded p-2 text-sm bg-white"
          >
            <option value="">Choose a class</option>
            {classes.map((c) => <option key={c.id} value={c.id}>{c.name} {c.section}</option>)}
          </select>
        </div>
        <div>
          <Label>Attendance Date</Label>
          <Input type="date" value={date} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDate(e.target.value)} className="mt-1" />
        </div>
      </div>

      <ErrorMessage message={error} />
      {successMsg && <div className="p-3 bg-green-50 text-green-800 border border-green-200 rounded text-sm font-medium">{successMsg}</div>}

      {studentsLoading ? (
        <Spinner />
      ) : students.length > 0 ? (
        <div className="space-y-4 bg-white p-4 rounded-md border border-slate-200">
          <div className="divide-y divide-slate-100">
            {students.map((student) => (
              <div key={student.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">{student.full_name}</p>
                  <p className="text-xs text-slate-500">Roll: {student.roll_number}</p>
                </div>
                <select
                  value={attendanceMap[student.id] || 'present'}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setAttendanceMap(p => ({ ...p, [student.id]: e.target.value }))}
                  className="border rounded px-3 py-1.5 text-sm bg-white"
                >
                  <option value="present">Present</option>
                  <option value="absent">Absent</option>
                  <option value="late">Late</option>
                </select>
              </div>
            ))}
          </div>

          <Button onClick={handleSubmit} disabled={submitting} className="w-full bg-slate-900 text-white hover:bg-slate-800">
            {submitting ? 'Submitting Attendance...' : 'Submit Attendance'}
          </Button>
        </div>
      ) : selectedClass && <p className="text-sm text-slate-500 text-center py-6">No enrolled students in this class</p>}
    </div>
  )
}

