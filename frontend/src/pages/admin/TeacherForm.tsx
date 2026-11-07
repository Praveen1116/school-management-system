import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createTeacher, getTeacher, updateTeacher } from '@/api/teachers'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import ErrorMessage from '@/components/ErrorMessage'
import Spinner from '@/components/Spinner'
import { extractError } from '@/utils/helpers'

interface TeacherFormState {
  full_name: string
  employee_code: string
  email: string
  password: string
}

export default function TeacherForm(): React.ReactElement {
  const { id } = useParams<{ id: string }>()
  const isEdit = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState<TeacherFormState>({ full_name: '', employee_code: '', email: '', password: '' })
  const [loading, setLoading] = useState<boolean>(isEdit)
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isEdit && id) {
      getTeacher(id)
        .then((res) => {
          const t = res.data.data
          setForm({ full_name: t.full_name || '', employee_code: t.employee_code || '', email: t.email || '', password: '' })
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
      if (isEdit && id) {
        await updateTeacher(id, { full_name: form.full_name, employee_code: form.employee_code })
      } else {
        await createTeacher(form)
      }
      navigate('/admin/teachers')
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
          <CardTitle className="text-xl font-bold text-slate-900">{isEdit ? 'Edit Teacher' : 'Add New Teacher'}</CardTitle>
          {!isEdit && <p className="text-xs text-slate-500 mt-1">Note: Creates user account and teacher record.</p>}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="full_name">Full Name</Label>
              <Input id="full_name" required value={form.full_name} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, full_name: e.target.value }))} placeholder="e.g. John Doe" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="employee_code">Employee Code</Label>
              <Input id="employee_code" required value={form.employee_code} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, employee_code: e.target.value }))} placeholder="e.g. TCH003" className="mt-1" />
            </div>
            {!isEdit && (
              <>
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" type="email" required value={form.email} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, email: e.target.value }))} placeholder="teacher@school.demo" className="mt-1" />
                </div>
                <div>
                  <Label htmlFor="password">Initial Password</Label>
                  <Input id="password" type="password" required value={form.password} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, password: e.target.value }))} placeholder="••••••••" className="mt-1" />
                </div>
              </>
            )}
            <ErrorMessage message={error} />
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => navigate('/admin/teachers')}>Cancel</Button>
              <Button type="submit" disabled={submitting} className="bg-slate-900 text-white">{submitting ? 'Saving...' : isEdit ? 'Update Teacher' : 'Create Teacher'}</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

