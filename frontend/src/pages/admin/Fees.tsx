import React, { useState, useEffect } from 'react'
import { listInvoices, createInvoice, getBalance } from '@/api/fees'
import { listStudents } from '@/api/students'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import DataTable, { Column } from '@/components/DataTable'
import StatusBadge from '@/components/StatusBadge'
import ErrorMessage from '@/components/ErrorMessage'
import { formatAmount, formatDate, extractError } from '@/utils/helpers'
import RecordPaymentDialog from './RecordPaymentDialog'
import type { FeeInvoice, Student } from '@/types'

interface InvoiceFormState {
  student_id: string
  description: string
  amount_due: string
  due_date: string
}

type FeeTab = 'all' | 'unpaid' | 'partial' | 'paid'

export default function Fees(): React.ReactElement {
  const [invoices, setInvoices] = useState<FeeInvoice[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [activeTab, setActiveTab] = useState<FeeTab>('all')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [invoiceModalOpen, setInvoiceModalOpen] = useState<boolean>(false)
  const [invoiceForm, setInvoiceForm] = useState<InvoiceFormState>({ student_id: '', description: '', amount_due: '', due_date: '' })
  const [paymentModalOpen, setPaymentModalOpen] = useState<boolean>(false)
  const [selectedInvoice, setSelectedInvoice] = useState<FeeInvoice | null>(null)

  useEffect(() => { loadData() }, [])

  async function loadData(): Promise<void> {
    try {
      setLoading(true)
      const [invRes, stuRes] = await Promise.all([listInvoices(), listStudents({ limit: 100 })])
      const sList = stuRes.data.data || []
      const stuMap: Record<string, string> = Object.fromEntries(sList.map(s => [s.id, `${s.full_name} (${s.roll_number})`]))
      setStudents(sList)
      const rawInvoices = invRes.data.data || []
      const enriched = await Promise.all(rawInvoices.map(async (inv): Promise<FeeInvoice> => {
        try {
          const b = (await getBalance(inv.id)).data.data
          const status = b.status || ((b.total_paid || 0) === 0 ? 'unpaid' : (b.outstanding === 0 ? 'paid' : 'partial'))
          return {
            ...inv, student_name: stuMap[inv.student_id] || inv.student_id,
            amount_paid: b.total_paid || 0, balance: b.outstanding != null ? b.outstanding : inv.amount_due, status,
          }
        } catch {
          return { ...inv, student_name: stuMap[inv.student_id] || inv.student_id, amount_paid: 0, balance: inv.amount_due, status: 'unpaid' }
        }
      }))
      setInvoices(enriched)
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  const filtered = invoices.filter(inv => {
    if (activeTab === 'unpaid') return inv.status === 'unpaid'
    if (activeTab === 'partial') return inv.status === 'partially_paid' || inv.status === 'partial'
    if (activeTab === 'paid') return inv.status === 'paid'
    return true
  })

  async function handleInvoiceSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    try {
      await createInvoice({ ...invoiceForm, amount_due: Math.round(Number(invoiceForm.amount_due) * 100) })
      setInvoiceModalOpen(false)
      await loadData()
    } catch (err: unknown) {
      alert(extractError(err))
    }
  }

  const columns: Column<FeeInvoice>[] = [
    { label: 'Student', render: (r: FeeInvoice) => r.student_name || r.student_id },
    { label: 'Description', key: 'description' },
    { label: 'Amount Due', render: (r: FeeInvoice) => formatAmount(r.amount_due) },
    { label: 'Total Paid', render: (r: FeeInvoice) => formatAmount(r.amount_paid) },
    { label: 'Outstanding', render: (r: FeeInvoice) => formatAmount(r.balance) },
    { label: 'Status', render: (r: FeeInvoice) => <StatusBadge status={r.status || 'unpaid'} /> },
    { label: 'Due Date', render: (r: FeeInvoice) => formatDate(r.due_date) },
    {
      label: 'Actions',
      render: (r: FeeInvoice) => r.status !== 'paid' ? (
        <Button size="sm" variant="outline" onClick={() => { setSelectedInvoice(r); setPaymentModalOpen(true) }}>
          Record Payment
        </Button>
      ) : null,
    },
  ]

  const tabs: FeeTab[] = ['all', 'unpaid', 'partial', 'paid']

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Fee Invoices</h1>
        <Button onClick={() => setInvoiceModalOpen(true)} className="bg-slate-900 text-white">Create Invoice</Button>
      </div>

      <div className="flex gap-2 border-b">
        {tabs.map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 text-sm font-medium border-b-2 capitalize ${activeTab === tab ? 'border-slate-900 text-slate-900 font-bold' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
            {tab}
          </button>
        ))}
      </div>

      <ErrorMessage message={error} />
      <DataTable<FeeInvoice> columns={columns} data={filtered} loading={loading} emptyMessage={`No ${activeTab === 'all' ? '' : activeTab} invoices found`} />

      <Dialog open={invoiceModalOpen} onOpenChange={setInvoiceModalOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create Invoice</DialogTitle></DialogHeader>
          <form onSubmit={handleInvoiceSubmit} className="space-y-3">
            <div>
              <Label>Student</Label>
              <select required value={invoiceForm.student_id} onChange={(e) => setInvoiceForm(p => ({ ...p, student_id: e.target.value }))} className="w-full mt-1 border rounded p-2 text-sm bg-white">
                <option value="">Select Student</option>
                {students.map(s => <option key={s.id} value={s.id}>{s.full_name} ({s.roll_number})</option>)}
              </select>
            </div>
            <div><Label>Description</Label><Input required placeholder="e.g. Tuition Term 1" value={invoiceForm.description} onChange={(e) => setInvoiceForm(p => ({ ...p, description: e.target.value }))} className="mt-1" /></div>
            <div><Label>Amount (₹)</Label><Input type="number" required min="1" step="0.01" value={invoiceForm.amount_due} onChange={(e) => setInvoiceForm(p => ({ ...p, amount_due: e.target.value }))} className="mt-1" /></div>
            <div><Label>Due Date</Label><Input type="date" required value={invoiceForm.due_date} onChange={(e) => setInvoiceForm(p => ({ ...p, due_date: e.target.value }))} className="mt-1" /></div>
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => setInvoiceModalOpen(false)}>Cancel</Button>
              <Button type="submit" className="bg-slate-900 text-white">Create Invoice</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <RecordPaymentDialog open={paymentModalOpen} onOpenChange={setPaymentModalOpen} invoice={selectedInvoice} onSuccess={() => loadData()} />
    </div>
  )
}
