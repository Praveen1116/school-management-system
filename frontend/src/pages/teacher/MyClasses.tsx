import React, { useState, useEffect } from 'react'
import { listClasses, getClassStudents } from '@/api/classes'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import DataTable, { Column } from '@/components/DataTable'
import Spinner from '@/components/Spinner'
import ErrorMessage from '@/components/ErrorMessage'
import { extractError } from '@/utils/helpers'
import type { Class, Student } from '@/types'

export default function MyClasses(): React.ReactElement {
  const [classes, setClasses] = useState<Class[]>([])
  const [selectedClass, setSelectedClass] = useState<Class | null>(null)
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [studentsLoading, setStudentsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadClasses()
  }, [])

  async function loadClasses(): Promise<void> {
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

  async function handleSelectClass(cls: Class): Promise<void> {
    setSelectedClass(cls)
    try {
      setStudentsLoading(true)
      const res = await getClassStudents(cls.id)
      setStudents(res.data.data || [])
    } catch (err: unknown) {
      alert(extractError(err))
    } finally {
      setStudentsLoading(false)
    }
  }

  if (loading) return <Spinner />
  if (error) return <ErrorMessage message={error} />

  const studentColumns: Column<Student>[] = [
    { label: 'Roll Number', key: 'roll_number' },
    { label: 'Full Name', key: 'full_name' },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">My Assigned Classes</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {classes.map((c) => (
          <Card
            key={c.id}
            onClick={() => handleSelectClass(c)}
            className={`cursor-pointer transition-all border ${
              selectedClass?.id === c.id
                ? 'border-slate-900 shadow-md bg-slate-50'
                : 'border-slate-200 bg-white hover:border-slate-400'
            }`}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-bold text-slate-900">
                {c.name} {c.section}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-slate-600 space-y-1">
              <p>Academic Year: <strong>{c.academic_year}</strong></p>
              <p>Students: <strong>{c.studentCount}</strong></p>
            </CardContent>
          </Card>
        ))}
      </div>

      {selectedClass && (
        <div className="space-y-3 pt-4 border-t border-slate-200">
          <h2 className="text-xl font-bold text-slate-900">
            Enrolled Students in {selectedClass.name} {selectedClass.section}
          </h2>
          <DataTable<Student>
            columns={studentColumns}
            data={students}
            loading={studentsLoading}
            emptyMessage="No students currently enrolled in this class"
          />
        </div>
      )}
    </div>
  )
}

