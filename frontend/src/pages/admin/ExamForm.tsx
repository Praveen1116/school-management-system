import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createExam, getExam } from '@/api/exams'
import { listSubjects } from '@/api/subjects'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import ErrorMessage from '@/components/ErrorMessage'
import Spinner from '@/components/Spinner'
import { extractError } from '@/utils/helpers'
import type { Subject } from '@/types'

interface ExamFormState {
  name: string
  subject_id: string
  total_marks: number | string
  exam_date: string
  grading_rule_set_name: string
}

export default function ExamForm(): React.ReactElement {
  const { id } = useParams<{ id: string }>()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState<ExamFormState>({
    name: '', subject_id: '', total_marks: 100, exam_date: '', grading_rule_set_name: 'Standard 2026',
  })
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [loading, setLoading] = useState<boolean>(isEdit)
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listSubjects().then((res) => setSubjects(res.data.data || [])).catch(() => {})
    if (id) {
      getExam(id)
        .then((res) => {
          const ex = res.data.data
          setForm({
            name: ex.name, subject_id: ex.subject_id, total_marks: ex.total_marks,
            exam_date: ex.exam_date, grading_rule_set_name: ex.grading_rule_set_name,
          })
        })
        .catch((err: unknown) => setError(extractError(err)))
        .finally(() => setLoading(false))
    }
  }, [id])

  const setField = (key: keyof ExamFormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>): void => {
    setForm(p => ({ ...p, [key]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await createExam({ ...form, total_marks: Number(form.total_marks) })
      navigate('/admin/exams')
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="max-w-xl mx-auto space-y-4">
      <Card className="bg-white border-slate-200">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-slate-900">{isEdit ? 'Edit Exam' : 'Create New Exam'}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Exam Name</Label>
              <Input id="name" required value={form.name} onChange={setField('name')} placeholder="Midterm 2026" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="subject_id">Subject</Label>
              <select id="subject_id" required value={form.subject_id} onChange={setField('subject_id')} className="w-full mt-1 border rounded p-2 text-sm bg-white">
                <option value="">Select Subject</option>
                {subjects.map((s) => <option key={s.id} value={s.id}>{s.name} ({s.code})</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label htmlFor="total_marks">Total Marks</Label>
                <Input id="total_marks" type="number" required value={form.total_marks} onChange={setField('total_marks')} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="exam_date">Exam Date</Label>
                <Input id="exam_date" type="date" required value={form.exam_date} onChange={setField('exam_date')} className="mt-1" />
              </div>
            </div>
            <div>
              <Label htmlFor="rule">Grading Rule Set Name</Label>
              <Input id="rule" required value={form.grading_rule_set_name} onChange={setField('grading_rule_set_name')} placeholder="Standard 2026" className="mt-1" />
            </div>
            <ErrorMessage message={error} />
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => navigate('/admin/exams')}>Cancel</Button>
              <Button type="submit" disabled={submitting} className="bg-slate-900 text-white">{submitting ? 'Saving...' : 'Save Exam'}</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
