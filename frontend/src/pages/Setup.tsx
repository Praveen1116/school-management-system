import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { getSetupStatus, performSetup } from '@/api/setup'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import ErrorMessage from '@/components/ErrorMessage'
import Spinner from '@/components/Spinner'
import { extractError } from '@/utils/helpers'
import type { SetupPayload } from '@/types'

export default function Setup(): React.ReactElement {
  const navigate = useNavigate()
  const [checking, setChecking] = useState<boolean>(true)
  const [locked, setLocked] = useState<boolean>(false)
  const [form, setForm] = useState<SetupPayload>({
    school_name: '',
    school_code: '',
    full_name: '',
    email: '',
    password: '',
  })
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getSetupStatus()
      .then((res) => {
        if (!res.data.data.is_setup_required) {
          setLocked(true)
        }
      })
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setChecking(false))
  }, [])

  const setField = (key: keyof SetupPayload) => (e: React.ChangeEvent<HTMLInputElement>): void => {
    setForm((p) => ({ ...p, [key]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await performSetup(form)
      navigate('/login', {
        state: { message: 'Setup completed successfully! Please sign in with your administrator account.' },
      })
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (checking) return <Spinner />

  if (locked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <Card className="max-w-md w-full bg-white border-slate-200 text-center p-6 space-y-4">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-900">Setup Already Completed</CardTitle>
            <CardDescription className="text-slate-600">
              This school instance is already initialized. The setup route is permanently locked (403).
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/login">
              <Button className="w-full bg-slate-900 text-white">Go to Login</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-8">
      <Card className="max-w-lg w-full bg-white border-slate-200">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-slate-900">School Initial Setup</CardTitle>
          <CardDescription className="text-slate-600">
            Configure your school and create the primary administrator account. This setup can only be performed once.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-3 border-b border-slate-100 pb-4">
              <h3 className="text-xs uppercase font-bold text-slate-500 tracking-wider">School Details</h3>
              <div>
                <Label htmlFor="school_name">School Name</Label>
                <Input id="school_name" required value={form.school_name} onChange={setField('school_name')} placeholder="e.g. Green Valley High School" className="mt-1" />
              </div>
              <div>
                <Label htmlFor="school_code">School Code</Label>
                <Input id="school_code" required value={form.school_code} onChange={setField('school_code')} placeholder="e.g. GVHS-01" className="mt-1" />
              </div>
            </div>

            <div className="space-y-3 pt-1">
              <h3 className="text-xs uppercase font-bold text-slate-500 tracking-wider">Primary Administrator</h3>
              <div>
                <Label htmlFor="full_name">Full Name</Label>
                <Input id="full_name" required value={form.full_name} onChange={setField('full_name')} placeholder="e.g. Principal Jane Doe" className="mt-1" />
              </div>
              <div>
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" type="email" required value={form.email} onChange={setField('email')} placeholder="admin@school.edu" className="mt-1" />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" required minLength={6} value={form.password} onChange={setField('password')} placeholder="Minimum 6 characters" className="mt-1" />
              </div>
            </div>

            <ErrorMessage message={error} />
            <Button type="submit" disabled={submitting} className="w-full bg-slate-900 text-white mt-2">
              {submitting ? 'Initializing Instance...' : 'Complete Setup & Initialize School'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

