import React, { useState, useEffect } from 'react'
import { getDashboard } from '@/api/reports'
import { formatAmount, formatDate, extractError } from '@/utils/helpers'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import Spinner from '@/components/Spinner'
import ErrorMessage from '@/components/ErrorMessage'
import DataTable, { Column } from '@/components/DataTable'
import type { DashboardStats, AuditLog } from '@/types'

export default function AdminDashboard(): React.ReactElement | null {
  const [data, setData] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboard()
  }, [])

  async function fetchDashboard(): Promise<void> {
    try {
      setLoading(true)
      setError(null)
      const res = await getDashboard()
      setData(res.data.data)
    } catch (err: unknown) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Spinner />
  if (error) return <ErrorMessage message={error} />
  if (!data) return null

  const auditColumns: Column<AuditLog>[] = [
    { label: 'Date', render: (row: AuditLog) => formatDate(row.created_at) },
    { label: 'Actor', render: (row: AuditLog) => row.actor_email || row.actor_id },
    { label: 'Action', key: 'action' },
    { label: 'Entity Type', key: 'entity_type' },
  ]

  return (
    <div className="space-y-6 p-1">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Admin Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Overview of school performance, attendance, and fee collections.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="shadow-sm">
          <CardHeader className="p-5 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Total Students</CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <p className="text-3xl font-extrabold text-slate-900">{data.total_students}</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="p-5 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Total Teachers</CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <p className="text-3xl font-extrabold text-slate-900">{data.total_teachers}</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="p-5 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Total Classes</CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <p className="text-3xl font-extrabold text-slate-900">{data.total_classes}</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="p-5 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Today's Attendance</CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <p className="text-3xl font-extrabold text-emerald-600">{data.todays_attendance_rate}%</p>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader className="p-5 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Fees Outstanding</CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <p className="text-3xl font-extrabold text-amber-600">{formatAmount(data.total_fees_outstanding)}</p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-3 pt-2">
        <h2 className="text-lg font-bold text-slate-900">Recent Audit Logs</h2>
        <DataTable<AuditLog>
          columns={auditColumns}
          data={data.recent_audit_logs || []}
          emptyMessage="No recent audit logs available"
        />
      </div>
    </div>
  )
}

