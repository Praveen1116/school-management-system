import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { getSetupStatus } from '@/api/setup'
import { getDashboardPath, extractError } from '@/utils/helpers'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import ErrorMessage from '@/components/ErrorMessage'

interface LoginFormState {
  email: string
  password: string
}

export default function Login(): React.ReactElement {
  const [form, setForm] = useState<LoginFormState>({ email: '', password: '' })
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const state = location.state
  const successMsg = typeof state === 'object' && state !== null && 'message' in state && typeof state.message === 'string'
    ? state.message
    : null

  useEffect(() => {
    getSetupStatus()
      .then((res) => {
        if (res.data.data.is_setup_required) {
          navigate('/setup', { replace: true })
        }
      })
      .catch(() => {})
  }, [navigate])

  function handleChange(e: React.ChangeEvent<HTMLInputElement>): void {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const userData = await login(form.email, form.password)
      navigate(getDashboardPath(userData.role), { replace: true })
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50 p-4">
      <Card className="w-full max-w-md shadow-sm border-slate-200 bg-white">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-slate-900">
            School Portal Login
          </CardTitle>
        </CardHeader>
        <CardContent>
          {successMsg && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-800 rounded text-xs font-medium">
              {successMsg}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-slate-700">Email Address</Label>
              <Input
                id="email"
                name="email"
                type="email"
                required
                value={form.email}
                onChange={handleChange}
                placeholder="name@school.demo"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="password" className="text-slate-700">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                value={form.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="mt-1"
              />
            </div>
            <Button
              type="submit"
              disabled={submitting}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white"
            >
              {submitting ? 'Signing in...' : 'Sign In'}
            </Button>
            <ErrorMessage message={error} />
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
