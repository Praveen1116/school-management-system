import React, { useState } from 'react'
import { createClass, updateClass } from '@/api/classes'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import ErrorMessage from '@/components/ErrorMessage'
import { extractError } from '@/utils/helpers'
import type { Class } from '@/types'

interface ClassFormProps {
  initialData?: Class | null
  onSuccess?: () => void
  onCancel?: () => void
}

interface ClassFormState {
  name: string
  section: string
  academic_year: number | string
}

export default function ClassForm({ initialData = null, onSuccess, onCancel }: ClassFormProps): React.ReactElement {
  const isEdit = Boolean(initialData?.id)
  const [form, setForm] = useState<ClassFormState>({
    name: initialData?.name || '',
    section: initialData?.section || '',
    academic_year: initialData?.academic_year || 2026,
  })
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  function handleChange(e: React.ChangeEvent<HTMLInputElement>): void {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const payload = {
        name: form.name,
        section: form.section,
        academic_year: Number(form.academic_year),
      }
      if (isEdit && initialData) {
        await updateClass(initialData.id, payload)
      } else {
        await createClass(payload)
      }
      onSuccess?.()
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="className">Class Name</Label>
        <Input
          id="className"
          name="name"
          required
          value={form.name}
          onChange={handleChange}
          placeholder="e.g. Class 10"
          className="mt-1"
        />
      </div>

      <div>
        <Label htmlFor="section">Section</Label>
        <Input
          id="section"
          name="section"
          required
          value={form.section}
          onChange={handleChange}
          placeholder="e.g. A"
          className="mt-1"
        />
      </div>

      <div>
        <Label htmlFor="academic_year">Academic Year</Label>
        <Input
          id="academic_year"
          name="academic_year"
          type="number"
          required
          value={form.academic_year}
          onChange={handleChange}
          placeholder="2026"
          className="mt-1"
        />
      </div>

      <ErrorMessage message={error} />

      <div className="flex justify-end gap-2 pt-2">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={submitting} className="bg-slate-900 text-white">
          {submitting ? 'Saving...' : isEdit ? 'Update Class' : 'Create Class'}
        </Button>
      </div>
    </form>
  )
}

