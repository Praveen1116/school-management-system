import React, { useState, useEffect } from 'react'
import { getAuditLogs } from '@/api/reports'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import DataTable, { Column } from '@/components/DataTable'
import ErrorMessage from '@/components/ErrorMessage'
import { formatDate, extractError } from '@/utils/helpers'
import type { AuditLog } from '@/types'

export default function AuditLogs(): React.ReactElement {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [entityType, setEntityType] = useState<string>('')
  const [dateFrom, setDateFrom] = useState<string>('')
  const [dateTo, setDateTo] = useState<string>('')
  const [page, setPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)

  useEffect(() => {
    loadLogs()
  }, [page, entityType, dateFrom, dateTo])

  async function loadLogs(): Promise<void> {
    try {
      setLoading(true)
      setError(null)
      const params: { page: number; limit: number; entity_type?: string; date_from?: string; date_to?: string } = { page, limit: 20 }
      if (entityType) params.entity_type = entityType
      if (dateFrom) params.date_from = dateFrom
      if (dateTo) params.date_to = dateTo
      const res = await getAuditLogs(params)
      setLogs(res.data.data || [])
      setTotalPages(res.data.pagination?.pages || 1)
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  function getEntityLabel(r: AuditLog): string | null {
    const val = r.new_value || r.old_value
    if (!val) return null
    if (typeof val.full_name === 'string') {
      const roll = typeof val.roll_number === 'string' ? val.roll_number : (typeof val.roll === 'string' ? val.roll : '')
      return `${val.full_name}${roll ? ` (${roll})` : ''}`
    }
    if (typeof val.payment_ref === 'string') return `Ref: ${val.payment_ref}`
    if (typeof val.student === 'string' || typeof val.student_name === 'string') {
      const name = String(val.student || val.student_name)
      const st = typeof val.status === 'string' ? ` (${val.status})` : ''
      return `${name}${st}`
    }
    if (typeof val.grade === 'string') {
      const marks = typeof val.marks_obtained === 'number' ? val.marks_obtained : 0
      return `Grade ${val.grade} (${marks} marks)`
    }
    if (typeof val.name === 'string') return val.name
    return null
  }

  const columns: Column<AuditLog>[] = [
    { label: 'Date', render: (r: AuditLog) => formatDate(r.created_at) },
    { label: 'Actor', render: (r: AuditLog) => r.actor_email || r.actor_id },
    { label: 'Action', key: 'action' },
    { label: 'Entity Type', key: 'entity_type' },
    {
      label: 'Entity Details / ID',
      render: (r: AuditLog) => {
        const label = getEntityLabel(r)
        return (
          <div className="flex flex-col">
            {label && <span className="font-medium text-slate-800 text-xs">{label}</span>}
            <span className="font-mono text-xs text-slate-500" title={r.entity_id}>
              {label ? `${r.entity_id.slice(0, 8)}...` : r.entity_id}
            </span>
          </div>
        )
      },
    },
  ]

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-900">Audit Logs</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-white p-4 rounded-md border">
        <div>
          <Label>Filter by Entity Type</Label>
          <Input
            placeholder="e.g. student, fee_payment..."
            value={entityType}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => { setEntityType(e.target.value); setPage(1) }}
            className="mt-1"
          />
        </div>
        <div>
          <Label>From Date</Label>
          <Input type="date" value={dateFrom} onChange={(e: React.ChangeEvent<HTMLInputElement>) => { setDateFrom(e.target.value); setPage(1) }} className="mt-1" />
        </div>
        <div>
          <Label>To Date</Label>
          <Input type="date" value={dateTo} onChange={(e: React.ChangeEvent<HTMLInputElement>) => { setDateTo(e.target.value); setPage(1) }} className="mt-1" />
        </div>
      </div>

      <ErrorMessage message={error} />
      <DataTable<AuditLog> columns={columns} data={logs} loading={loading} emptyMessage="No audit logs recorded matching your filters" />

      {totalPages > 1 && (
        <div className="flex justify-between items-center pt-2">
          <span className="text-sm text-slate-600">Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
            <Button size="sm" variant="outline" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</Button>
          </div>
        </div>
      )}
    </div>
  )
}

