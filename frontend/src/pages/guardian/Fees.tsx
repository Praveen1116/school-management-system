import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getMyStudents, getStudentFeeSummary } from '@/api/guardian'
import { Label } from '@/components/ui/label'
import DataTable, { Column } from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import Spinner from '@/components/Spinner'
import ErrorMessage from '@/components/ErrorMessage'
import { formatAmount, formatDate, extractError } from '@/utils/helpers'
import type { Student, FeeInvoice } from '@/types'

export default function GuardianFees(): React.ReactElement {
  const [searchParams] = useSearchParams()
  const initialStudentId = searchParams.get('studentId') || ''

  const [students, setStudents] = useState<Student[]>([])
  const [selectedStudentId, setSelectedStudentId] = useState<string>(initialStudentId)
  const [invoices, setInvoices] = useState<FeeInvoice[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [feesLoading, setFeesLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getMyStudents()
      .then((res) => {
        const list = res.data.data || []
        setStudents(list)
        if (!selectedStudentId && list.length > 0) {
          setSelectedStudentId(list[0].id)
        }
      })
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedStudentId) return
    setFeesLoading(true)
    setError(null)
    getStudentFeeSummary(selectedStudentId)
      .then((res) => setInvoices(res.data.data || []))
      .catch((err: unknown) => setError(extractError(err)))
      .finally(() => setFeesLoading(false))
  }, [selectedStudentId])

  const totals = invoices.reduce(
    (acc, inv) => {
      const paid = inv.total_paid != null ? inv.total_paid : (inv.amount_paid || 0)
      const out = inv.outstanding != null ? inv.outstanding : (inv.balance != null ? inv.balance : (inv.amount_due - paid))
      acc.due += inv.amount_due || 0
      acc.paid += paid
      acc.outstanding += out
      return acc
    },
    { due: 0, paid: 0, outstanding: 0 }
  )

  const columns: Column<FeeInvoice>[] = [
    { label: 'Description', key: 'description' },
    { label: 'Amount Due', render: (r: FeeInvoice) => formatAmount(r.amount_due) },
    { label: 'Total Paid', render: (r: FeeInvoice) => formatAmount(r.total_paid != null ? r.total_paid : (r.amount_paid || 0)) },
    { label: 'Outstanding', render: (r: FeeInvoice) => formatAmount(r.outstanding != null ? r.outstanding : (r.balance != null ? r.balance : (r.amount_due - (r.total_paid || 0)))) },
    { label: 'Status', render: (r: FeeInvoice) => <StatusBadge status={r.status || 'unpaid'} /> },
    { label: 'Due Date', render: (r: FeeInvoice) => formatDate(r.due_date) },
  ]

  if (loading) return <Spinner />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Fee Invoices &amp; Ledger</h1>

      {students.length > 1 && (
        <div className="max-w-xs">
          <Label>Select Child</Label>
          <select
            value={selectedStudentId}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedStudentId(e.target.value)}
            className="w-full mt-1 border border-slate-300 rounded p-2 text-sm bg-white"
          >
            {students.map((s) => (
              <option key={s.id} value={s.id}>{s.full_name} ({s.roll_number})</option>
            ))}
          </select>
        </div>
      )}

      <ErrorMessage message={error} />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-50 p-4 rounded-lg border">
        <div>
          <p className="text-xs text-slate-500 uppercase font-semibold">Total Amount Billed</p>
          <p className="text-2xl font-bold text-slate-900">{formatAmount(totals.due)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase font-semibold">Total Amount Paid</p>
          <p className="text-2xl font-bold text-green-700">{formatAmount(totals.paid)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase font-semibold">Total Outstanding</p>
          <p className="text-2xl font-bold text-red-700">{formatAmount(totals.outstanding)}</p>
        </div>
      </div>

      <DataTable<FeeInvoice>
        columns={columns}
        data={invoices}
        loading={feesLoading}
        emptyMessage="No fee invoices recorded for this student"
      />
    </div>
  )
}

