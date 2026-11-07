import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { listExams, enterResult } from '@/api/exams'
import { listClasses, getClassStudents } from '@/api/classes'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import ErrorMessage from '@/components/ErrorMessage'
import Spinner from '@/components/Spinner'
import { extractError } from '@/utils/helpers'
import type { Exam, Class, Student } from '@/types'

export default function TeacherResults(): React.ReactElement {
  const [exams, setExams] = useState<Exam[]>([])
  const [classes, setClasses] = useState<Class[]>([])
  const [selectedExamId, setSelectedExamId] = useState<string>('')
  const [selectedClassId, setSelectedClassId] = useState<string>('')
  const [students, setStudents] = useState<Student[]>([])
  const [marksMap, setMarksMap] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState<boolean>(true)
  const [studentsLoading, setStudentsLoading] = useState<boolean>(false)
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([listExams(), listClasses()])
      .then(([eRes, cRes]) => { setExams(eRes.data.data || []); setClasses(cRes.data.data || []) })
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setLoading(false))
  }, [])

  const selectedExam = exams.find((e) => e.id === selectedExamId)

  useEffect(() => {
    setSuccessMsg(null)
    setMarksMap({})
  }, [selectedExamId])

  useEffect(() => {
    if (!selectedClassId) { setStudents([]); setMarksMap({}); return }
    setStudentsLoading(true)
    setError(null)
    setSuccessMsg(null)
    getClassStudents(selectedClassId)
      .then((res) => {
        setStudents(res.data.data || [])
        setMarksMap({})
      })
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setStudentsLoading(false))
  }, [selectedClassId])

  async function handleSubmit(): Promise<void> {
    if (!selectedExamId) return
    setSubmitting(true)
    setError(null)
    setSuccessMsg(null)
    let entered = 0
    let skipped = 0
    try {
      for (const student of students) {
        const markVal = marksMap[student.id]
        if (markVal === '' || markVal == null) continue
        try {
          await enterResult(selectedExamId, { student_id: student.id, marks_obtained: Number(markVal) })
          entered += 1
        } catch (err: unknown) {
          if (axios.isAxiosError(err) && err.response?.status === 409) skipped += 1
          else throw err
        }
      }
      setSuccessMsg(`Results processed: ${entered} saved, ${skipped} already submitted.`)
      setMarksMap({})
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Enter Exam Results</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white p-4 rounded-md border border-slate-200">
        <div>
          <Label>Select Exam</Label>
          <select value={selectedExamId} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedExamId(e.target.value)} className="w-full mt-1 border rounded p-2 text-sm bg-white">
            <option value="">{exams.length === 0 ? 'No exams available for your subjects' : 'Choose Exam'}</option>
            {exams.map((ex) => <option key={ex.id} value={ex.id}>{ex.name} (Max: {ex.total_marks})</option>)}
          </select>
          {exams.length === 0 && <p className="text-xs text-amber-600 mt-1">No exams currently scheduled for your assigned subjects.</p>}
        </div>
        <div>
          <Label>Select Class</Label>
          <select value={selectedClassId} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedClassId(e.target.value)} className="w-full mt-1 border rounded p-2 text-sm bg-white">
            <option value="">Choose Class</option>
            {classes.map((c) => <option key={c.id} value={c.id}>{c.name} {c.section}</option>)}
          </select>
        </div>
      </div>

      <ErrorMessage message={error} />
      {successMsg && <div className="p-3 bg-green-50 text-green-800 border border-green-200 rounded text-sm font-medium">{successMsg}</div>}

      {studentsLoading ? (
        <Spinner />
      ) : students.length > 0 && selectedExam ? (
        <div className="space-y-4 bg-white p-4 rounded-md border border-slate-200">
          <div className="divide-y divide-slate-100">
            {students.map((student) => (
              <div key={student.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">{student.full_name}</p>
                  <p className="text-xs text-slate-500">Roll: {student.roll_number}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    min="0"
                    max={selectedExam.total_marks}
                    value={marksMap[student.id] ?? ''}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMarksMap((p) => ({ ...p, [student.id]: e.target.value }))}
                    placeholder={`0 - ${selectedExam.total_marks}`}
                    className="w-32 text-right"
                  />
                  <span className="text-xs text-slate-500">/ {selectedExam.total_marks}</span>
                </div>
              </div>
            ))}
          </div>

          <Button onClick={handleSubmit} disabled={submitting} className="w-full bg-slate-900 text-white hover:bg-slate-800">
            {submitting ? 'Saving Results...' : 'Submit Results'}
          </Button>
        </div>
      ) : null}
    </div>
  )
}

