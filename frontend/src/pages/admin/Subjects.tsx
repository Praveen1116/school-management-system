import React, { useState, useEffect } from 'react'
import { listSubjects, createSubject, updateSubject, deleteSubject } from '@/api/subjects'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import DataTable, { Column } from '@/components/DataTable'
import ErrorMessage from '@/components/ErrorMessage'
import { extractError } from '@/utils/helpers'
import type { Subject } from '@/types'

interface SubjectFormState {
  name: string
  code: string
  total_marks: number | string
}

export default function Subjects(): React.ReactElement {
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState<boolean>(false)
  const [editing, setEditing] = useState<Subject | null>(null)
  const [form, setForm] = useState<SubjectFormState>({ name: '', code: '', total_marks: 100 })
  const [submitting, setSubmitting] = useState<boolean>(false)

  useEffect(() => {
    loadSubjects()
  }, [])

  async function loadSubjects(): Promise<void> {
    try {
      setLoading(true)
      const res = await listSubjects()
      setSubjects(res.data.data || [])
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  function openModal(sub: Subject | null = null): void {
    setEditing(sub)
    setForm(sub ? { name: sub.name, code: sub.code, total_marks: sub.total_marks } : { name: '', code: '', total_marks: 100 })
    setModalOpen(true)
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    setSubmitting(true)
    try {
      const payload = { ...form, total_marks: Number(form.total_marks) }
      if (editing) {
        await updateSubject(editing.id, payload)
      } else {
        await createSubject(payload)
      }
      setModalOpen(false)
      await loadSubjects()
    } catch (err: unknown) {
      alert(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id: string): Promise<void> {
    if (!window.confirm('Delete this subject?')) return
    try {
      await deleteSubject(id)
      await loadSubjects()
    } catch (err: unknown) {
      alert(extractError(err))
    }
  }

  const columns: Column<Subject>[] = [
    { label: 'Name', key: 'name' },
    { label: 'Code', key: 'code' },
    { label: 'Total Marks', key: 'total_marks' },
    {
      label: 'Actions',
      render: (row: Subject) => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => openModal(row)}>Edit</Button>
          <Button size="sm" variant="destructive" onClick={() => handleDelete(row.id)}>Delete</Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Subjects</h1>
        <Button onClick={() => openModal(null)} className="bg-slate-900 text-white">Add Subject</Button>
      </div>

      <ErrorMessage message={error} />
      <DataTable<Subject> columns={columns} data={subjects} loading={loading} />

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit Subject' : 'Add Subject'}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <Label htmlFor="sub_name">Name</Label>
              <Input id="sub_name" required value={form.name} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, name: e.target.value }))} placeholder="Mathematics" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="sub_code">Code</Label>
              <Input id="sub_code" required value={form.code} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, code: e.target.value }))} placeholder="MATH" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="sub_marks">Total Marks</Label>
              <Input id="sub_marks" type="number" required value={form.total_marks} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, total_marks: e.target.value }))} className="mt-1" />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={submitting} className="bg-slate-900 text-white">{submitting ? 'Saving...' : 'Save'}</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

