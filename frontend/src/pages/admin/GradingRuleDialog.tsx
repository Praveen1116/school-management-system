import React, { useState } from 'react'
import { createGradingRule } from '@/api/exams'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { extractError } from '@/utils/helpers'

interface RuleFormState {
  name: string
  grade_label: string
  min_marks: number | string
  max_marks: number | string
}

export interface GradingRuleDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export default function GradingRuleDialog({
  open,
  onOpenChange,
  onSuccess,
}: GradingRuleDialogProps): React.ReactElement {
  const [ruleForm, setRuleForm] = useState<RuleFormState>({
    name: 'Standard 2026',
    grade_label: '',
    min_marks: 0,
    max_marks: 100,
  })
  const [submitting, setSubmitting] = useState<boolean>(false)

  async function handleRuleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createGradingRule({
        ...ruleForm,
        min_marks: Number(ruleForm.min_marks),
        max_marks: Number(ruleForm.max_marks),
      })
      onOpenChange(false)
      onSuccess()
    } catch (err: unknown) {
      alert(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Grading Rule</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleRuleSubmit} className="space-y-3">
          <div>
            <Label>Rule Set Name</Label>
            <Input
              required
              value={ruleForm.name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setRuleForm((p) => ({ ...p, name: e.target.value }))
              }
              className="mt-1"
            />
          </div>
          <div>
            <Label>Grade Label</Label>
            <Input
              required
              placeholder="A, B, C, etc."
              value={ruleForm.grade_label}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setRuleForm((p) => ({ ...p, grade_label: e.target.value }))
              }
              className="mt-1"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label>Min Marks</Label>
              <Input
                type="number"
                required
                value={ruleForm.min_marks}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setRuleForm((p) => ({ ...p, min_marks: e.target.value }))
                }
                className="mt-1"
              />
            </div>
            <div>
              <Label>Max Marks</Label>
              <Input
                type="number"
                required
                value={ruleForm.max_marks}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setRuleForm((p) => ({ ...p, max_marks: e.target.value }))
                }
                className="mt-1"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting} className="bg-slate-900 text-white">
              {submitting ? 'Saving...' : 'Save Rule'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

