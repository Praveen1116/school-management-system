import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createStudent, getStudent, updateStudent } from '@/api/students'
import { listUsers } from '@/api/auth'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import ErrorMessage from '@/components/ErrorMessage'
import Spinner from '@/components/Spinner'
import { extractError } from '@/utils/helpers'
import type { User } from '@/types'

interface StudentFormState {
  full_name: string
  roll_number: string
  date_of_birth: string
  guardian_id: string
}

export default function StudentForm(): React.ReactElement {
  const { id } = useParams<{ id: string }>()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState<StudentFormState>({ full_name: '', roll_number: '', date_of_birth: '', guardian_id: '' })
  const [guardians, setGuardians] = useState<User[]>([])
  const [loading, setLoading] = useState<boolean>(isEdit)
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listUsers({ role: 'guardian' }).then((res) => setGuardians(res.data.data || [])).catch(() => {})
    if (isEdit && id) {
      getStudent(id)
        .then((res) => {
          const s = res.data.data
          setForm({ full_name: s.full_name || '', roll_number: s.roll_number || '', date_of_birth: s.date_of_birth || '', guardian_id: s.guardian_id || '' })
        })
        .catch((err: unknown) => setError(extractError(err)))
        .finally(() => setLoading(false))
    }
  }, [id, isEdit])

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      if (isEdit && id) await updateStudent(id, form)
      else await createStudent(form)
      navigate('/admin/students')
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
          <CardTitle className="text-xl font-bold text-slate-900">{isEdit ? 'Edit Student' : 'Add New Student'}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="full_name">Full Name</Label>
              <Input id="full_name" name="full_name" required value={form.full_name} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, full_name: e.target.value }))} placeholder="Student full name" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="roll_number">Roll Number</Label>
              <Input id="roll_number" name="roll_number" required value={form.roll_number} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, roll_number: e.target.value }))} placeholder="e.g. STU101" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="date_of_birth">Date of Birth</Label>
              <Input id="date_of_birth" name="date_of_birth" type="date" required value={form.date_of_birth} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, date_of_birth: e.target.value }))} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="guardian_id">Guardian</Label>
              <select id="guardian_id" name="guardian_id" required value={form.guardian_id} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setForm(p => ({ ...p, guardian_id: e.target.value }))} className="w-full mt-1 border rounded-md p-2 text-sm bg-white">
                <option value="">Select Guardian</option>
                {guardians.map(g => <option key={g.id} value={g.id}>{g.email}</option>)}
              </select>
            </div>
            <ErrorMessage message={error} />
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => navigate('/admin/students')}>Cancel</Button>
              <Button type="submit" disabled={submitting} className="bg-slate-900 text-white">{submitting ? 'Saving...' : isEdit ? 'Update Student' : 'Create Student'}</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

