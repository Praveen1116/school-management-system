import React, { useState, useEffect } from 'react'
import { listClasses, getClassStudents, listAssignments, createAssignment, deleteAssignment } from '@/api/classes'
import { listSubjects } from '@/api/subjects'
import { listTeachers } from '@/api/teachers'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import DataTable, { Column } from '@/components/DataTable'
import ErrorMessage from '@/components/ErrorMessage'
import ClassForm from './ClassForm'
import { extractError } from '@/utils/helpers'
import type { Class, ClassSubjectAssignment, Subject, Teacher, Student } from '@/types'

interface AssignFormState {
  class_id: string
  subject_id: string
  teacher_id: string
  academic_year: number
}

export default function Classes(): React.ReactElement {
  const [classes, setClasses] = useState<Class[]>([])
  const [assignments, setAssignments] = useState<ClassSubjectAssignment[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [classModalOpen, setClassModalOpen] = useState<boolean>(false)
  const [editingClass, setEditingClass] = useState<Class | null>(null)
  const [studentsModalOpen, setStudentsModalOpen] = useState<boolean>(false)
  const [enrolledStudents, setEnrolledStudents] = useState<Student[]>([])
  const [assignModalOpen, setAssignModalOpen] = useState<boolean>(false)
  const [assignForm, setAssignForm] = useState<AssignFormState>({ class_id: '', subject_id: '', teacher_id: '', academic_year: 2026 })

  useEffect(() => { loadData() }, [])

  async function loadData(): Promise<void> {
    try {
      setLoading(true)
      const [c, a, s, t] = await Promise.all([listClasses(), listAssignments(), listSubjects(), listTeachers()])
      setClasses(c.data.data || []); setAssignments(a.data.data || []); setSubjects(s.data.data || []); setTeachers(t.data.data || [])
    } catch (err: unknown) { setError(extractError(err)) }
    finally { setLoading(false) }
  }

  const classMap = Object.fromEntries(classes.map(c => [c.id, `${c.name} ${c.section}`]))
  const subjectMap = Object.fromEntries(subjects.map(s => [s.id, `${s.name} (${s.code})`]))
  const teacherMap = Object.fromEntries(teachers.map(t => [t.id, t.full_name]))

  async function viewStudents(classId: string): Promise<void> {
    try {
      const res = await getClassStudents(classId)
      setEnrolledStudents(res.data.data || []); setStudentsModalOpen(true)
    } catch (err: unknown) { alert(extractError(err)) }
  }

  async function handleAssignSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    try {
      await createAssignment({ ...assignForm, academic_year: Number(assignForm.academic_year) })
      setAssignModalOpen(false); loadData()
    } catch (err: unknown) { alert(extractError(err)) }
  }

  async function handleDeleteAssignment(id: string): Promise<void> {
    if (!window.confirm('Delete this assignment?')) return
    try { await deleteAssignment(id); loadData() }
    catch (err: unknown) { alert(extractError(err)) }
  }

  const classColumns: Column<Class>[] = [
    { label: 'Name', key: 'name' }, { label: 'Section', key: 'section' }, { label: 'Academic Year', key: 'academic_year' },
    { label: 'Actions', render: (r: Class) => (
      <div className="flex gap-2">
        <Button size="sm" variant="outline" onClick={() => viewStudents(r.id)}>View Students</Button>
        <Button size="sm" variant="outline" onClick={() => { setEditingClass(r); setClassModalOpen(true) }}>Edit</Button>
      </div>
    )}
  ]

  const assignColumns: Column<ClassSubjectAssignment>[] = [
    { label: 'Class', render: (r: ClassSubjectAssignment) => classMap[r.class_id] || `${r.class_name || ''} ${r.section || ''}` || r.class_id },
    { label: 'Subject', render: (r: ClassSubjectAssignment) => subjectMap[r.subject_id] || r.subject_name || r.subject_id },
    { label: 'Teacher', render: (r: ClassSubjectAssignment) => teacherMap[r.teacher_id] || r.teacher_name || r.teacher_id },
    { label: 'Academic Year', key: 'academic_year' },
    { label: 'Actions', render: (r: ClassSubjectAssignment) => <Button size="sm" variant="destructive" onClick={() => handleDeleteAssignment(r.id)}>Delete</Button> }
  ]

  return (
    <div className="space-y-8">
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-900">Classes</h1>
          <Button onClick={() => { setEditingClass(null); setClassModalOpen(true) }} className="bg-slate-900 text-white">Add Class</Button>
        </div>
        <ErrorMessage message={error} />
        <DataTable<Class> columns={classColumns} data={classes} loading={loading} />
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-900">Subject Assignments</h2>
          <Button onClick={() => setAssignModalOpen(true)} variant="outline">Add Assignment</Button>
        </div>
        <DataTable<ClassSubjectAssignment> columns={assignColumns} data={assignments} loading={loading} />
      </div>

      <Dialog open={classModalOpen} onOpenChange={setClassModalOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editingClass ? 'Edit Class' : 'Add Class'}</DialogTitle></DialogHeader>
          <ClassForm initialData={editingClass} onSuccess={() => { setClassModalOpen(false); loadData() }} onCancel={() => setClassModalOpen(false)} />
        </DialogContent>
      </Dialog>

      <Dialog open={studentsModalOpen} onOpenChange={setStudentsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Enrolled Students</DialogTitle></DialogHeader>
          <DataTable<Student> columns={[{ label: 'Roll Number', key: 'roll_number' }, { label: 'Name', key: 'full_name' }]} data={enrolledStudents} emptyMessage="No students enrolled" />
        </DialogContent>
      </Dialog>

      <Dialog open={assignModalOpen} onOpenChange={setAssignModalOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Assign Teacher to Subject</DialogTitle></DialogHeader>
          <form onSubmit={handleAssignSubmit} className="space-y-3">
            <div><Label>Class</Label><select required value={assignForm.class_id} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setAssignForm(p => ({ ...p, class_id: e.target.value }))} className="w-full mt-1 border rounded p-2 text-sm bg-white"><option value="">Select Class</option>{classes.map(c => <option key={c.id} value={c.id}>{c.name} {c.section}</option>)}</select></div>
            <div><Label>Subject</Label><select required value={assignForm.subject_id} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setAssignForm(p => ({ ...p, subject_id: e.target.value }))} className="w-full mt-1 border rounded p-2 text-sm bg-white"><option value="">Select Subject</option>{subjects.map(s => <option key={s.id} value={s.id}>{s.name} ({s.code})</option>)}</select></div>
            <div><Label>Teacher</Label><select required value={assignForm.teacher_id} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setAssignForm(p => ({ ...p, teacher_id: e.target.value }))} className="w-full mt-1 border rounded p-2 text-sm bg-white"><option value="">Select Teacher</option>{teachers.map(t => <option key={t.id} value={t.id}>{t.full_name}</option>)}</select></div>
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => setAssignModalOpen(false)}>Cancel</Button>
              <Button type="submit" className="bg-slate-900 text-white">Save Assignment</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

