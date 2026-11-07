import React, { useState, useEffect } from 'react'
import { listClasses, getClassStudents } from '@/api/classes'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import Spinner from '@/components/Spinner'
import ErrorMessage from '@/components/ErrorMessage'
import { extractError } from '@/utils/helpers'
import type { Class } from '@/types'

export default function TeacherDashboard(): React.ReactElement {
  const [classes, setClasses] = useState<Class[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  async function loadDashboard(): Promise<void> {
    try {
      setLoading(true)
      const res = await listClasses()
      const classList = res.data.data || []

      const enriched = await Promise.all(
        classList.map(async (c): Promise<Class> => {
          try {
            const sRes = await getClassStudents(c.id)
            return { ...c, studentCount: (sRes.data.data || []).length }
          } catch {
            return { ...c, studentCount: 0 }
          }
        })
      )
      setClasses(enriched)
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Spinner />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Teacher Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-white border-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Assigned Classes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-slate-900">{classes.length}</p>
          </CardContent>
        </Card>

        <Card className="bg-white border-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Total Enrolled Students</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-slate-900">
              {classes.reduce((sum, c) => sum + (c.studentCount || 0), 0)}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-900">My Classes &amp; Subjects</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {classes.map((c) => (
            <Card key={c.id} className="bg-white border-slate-200">
              <CardHeader>
                <CardTitle className="text-base font-bold text-slate-900">
                  {c.name} - Section {c.section}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm text-slate-600">
                <p>Academic Year: <strong>{c.academic_year}</strong></p>
                <p>Enrolled Students: <strong>{c.studentCount}</strong></p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}

