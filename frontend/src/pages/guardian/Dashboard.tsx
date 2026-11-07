import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getMyStudents } from '@/api/guardian'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import Spinner from '@/components/Spinner'
import ErrorMessage from '@/components/ErrorMessage'
import { extractError } from '@/utils/helpers'
import type { Student } from '@/types'

export default function GuardianDashboard(): React.ReactElement {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getMyStudents()
      .then((res) => setStudents(res.data.data || []))
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Guardian Portal</h1>
      <p className="text-sm text-slate-600">Access academic, attendance, and fee details for your children.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {students.map((student) => (
          <Card key={student.id} className="bg-white border-slate-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-bold text-slate-900">
                {student.full_name}
              </CardTitle>
              <p className="text-xs text-slate-500">Roll Number: {student.roll_number}</p>
            </CardHeader>
            <CardContent className="space-y-2 pt-2 border-t border-slate-100">
              <Link
                to={`/guardian/attendance?studentId=${student.id}`}
                className="block text-sm font-medium text-slate-800 hover:text-slate-900 hover:underline"
              >
                View Attendance &rarr;
              </Link>
              <Link
                to={`/guardian/results?studentId=${student.id}`}
                className="block text-sm font-medium text-slate-800 hover:text-slate-900 hover:underline"
              >
                View Results &amp; Report Card &rarr;
              </Link>
              <Link
                to={`/guardian/fees?studentId=${student.id}`}
                className="block text-sm font-medium text-slate-800 hover:text-slate-900 hover:underline"
              >
                View Fee Summary &rarr;
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

