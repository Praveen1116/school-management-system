import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getMyStudents, getStudentReportCard } from '@/api/guardian'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import DataTable, { Column } from '@/components/DataTable'
import Spinner from '@/components/Spinner'
import ErrorMessage from '@/components/ErrorMessage'
import { extractError } from '@/utils/helpers'
import type { Student, ReportCardSubject, ReportCardExam } from '@/types'

export default function GuardianResults(): React.ReactElement {
  const [searchParams] = useSearchParams()
  const initialStudentId = searchParams.get('studentId') || ''

  const [students, setStudents] = useState<Student[]>([])
  const [selectedStudentId, setSelectedStudentId] = useState<string>(initialStudentId)
  const [reportCard, setReportCard] = useState<ReportCardSubject[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [resultsLoading, setResultsLoading] = useState<boolean>(false)
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
    setResultsLoading(true)
    setError(null)
    getStudentReportCard(selectedStudentId)
      .then((res) => setReportCard(res.data.data || []))
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setResultsLoading(false))
  }, [selectedStudentId])

  const totals = reportCard.reduce(
    (acc, sub) => {
      acc.obtained += sub.marks_obtained || 0
      acc.total += sub.total_marks || 0
      return acc
    },
    { obtained: 0, total: 0 }
  )

  const percentage = totals.total > 0 ? ((totals.obtained / totals.total) * 100).toFixed(1) : 0

  if (loading) return <Spinner />

  const examColumns: Column<ReportCardExam>[] = [
    { label: 'Exam Name', key: 'exam_name' },
    { label: 'Exam Date', key: 'exam_date' },
    { label: 'Marks Obtained', key: 'marks_obtained' },
    { label: 'Total Marks', key: 'total_marks' },
    { label: 'Grade', key: 'grade' },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Academic Results &amp; Report Card</h1>

      {students.length > 1 && (
        <div className="max-w-xs">
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

      <ErrorMessage message={error} />

      {resultsLoading ? (
        <Spinner />
      ) : reportCard.length > 0 ? (
        <div className="space-y-6">
          {reportCard.map((subject, idx) => (
            <Card key={subject.subject_id || idx} className="bg-white border-slate-200">
              <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-base font-bold text-slate-900">
                  {subject.subject_name} {subject.subject_code ? `(${subject.subject_code})` : ''}
                </CardTitle>
                <div className="text-sm font-semibold text-slate-800">
                  Subject Total: {subject.marks_obtained} / {subject.total_marks} ({subject.grade || 'N/A'})
                </div>
              </CardHeader>
              <CardContent>
                <DataTable<ReportCardExam>
                  columns={examColumns}
                  data={subject.exams || []}
                  emptyMessage="No exams recorded for this subject"
                />
              </CardContent>
            </Card>
          ))}

          <div className="p-4 bg-slate-100 rounded-md flex justify-between items-center text-slate-900 font-bold">
            <span>Overall Aggregate Performance</span>
            <span>
              {totals.obtained} / {totals.total} marks ({percentage}%)
            </span>
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-500 py-6 text-center">No academic records found for this student.</p>
      )}
    </div>
  )
}

