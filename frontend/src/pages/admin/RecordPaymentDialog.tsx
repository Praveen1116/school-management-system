import React, { useState } from 'react'
import { recordPayment } from '@/api/fees'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { formatAmount, extractError } from '@/utils/helpers'
import type { FeeInvoice } from '@/types'

export interface RecordPaymentDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  invoice: FeeInvoice | null
  onSuccess: () => void
}

interface PaymentFormState {
  amount_paid: string
  payment_ref: string
}

export default function RecordPaymentDialog({
  open,
  onOpenChange,
  invoice,
  onSuccess,
}: RecordPaymentDialogProps): React.ReactElement {
  const [form, setForm] = useState<PaymentFormState>({ amount_paid: '', payment_ref: '' })
  const [submitting, setSubmitting] = useState<boolean>(false)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    if (!invoice) return
    setSubmitting(true)
    try {
      await recordPayment(invoice.id, {
        amount_paid: Math.round(Number(form.amount_paid) * 100),
        payment_ref: form.payment_ref,
      })
      onOpenChange(false)
      setForm({ amount_paid: '', payment_ref: '' })
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
          <DialogTitle>Record Payment</DialogTitle>
        </DialogHeader>
        {invoice && (
          <form onSubmit={handleSubmit} className="space-y-3">
            <p className="text-sm text-slate-600">
              Student: <strong>{invoice.student_name}</strong> | Outstanding: <strong>{formatAmount(invoice.balance)}</strong>
            </p>
            <div>
              <Label>Amount (₹)</Label>
              <Input
                type="number"
                required
                min="0.01"
                step="0.01"
                value={form.amount_paid}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setForm((p) => ({ ...p, amount_paid: e.target.value }))
                }
                className="mt-1"
              />
            </div>
            <div>
              <Label>Payment Reference</Label>
              <Input
                required
                placeholder="e.g. UPI-123456 / CASH"
                value={form.payment_ref}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setForm((p) => ({ ...p, payment_ref: e.target.value }))
                }
                className="mt-1"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={submitting} className="bg-slate-900 text-white">
                {submitting ? 'Saving...' : 'Save Payment'}
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}

