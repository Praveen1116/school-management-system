import React from 'react'
import { Badge } from '@/components/ui/badge'

export type Status =
  | 'present'
  | 'absent'
  | 'late'
  | 'paid'
  | 'partial'
  | 'partially_paid'
  | 'unpaid'
  | 'active'
  | 'inactive'

interface Props {
  status?: Status | string | null
}

const statusStyles: Record<string, string> = {
  present: 'bg-green-100 text-green-800 hover:bg-green-100 border-green-200',
  absent: 'bg-red-100 text-red-800 hover:bg-red-100 border-red-200',
  late: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100 border-yellow-200',
  paid: 'bg-green-100 text-green-800 hover:bg-green-100 border-green-200',
  partial: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100 border-yellow-200',
  partially_paid: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100 border-yellow-200',
  unpaid: 'bg-red-100 text-red-800 hover:bg-red-100 border-red-200',
  active: 'bg-green-100 text-green-800 hover:bg-green-100 border-green-200',
  inactive: 'bg-slate-100 text-slate-800 hover:bg-slate-100 border-slate-200',
}

export default function StatusBadge({ status }: Props): React.ReactElement | null {
  if (!status) return null
  const key = String(status).toLowerCase()
  const colorClass = statusStyles[key] || 'bg-slate-100 text-slate-800 border-slate-200'

  return (
    <Badge variant="outline" className={`font-medium capitalize ${colorClass}`}>
      {status}
    </Badge>
  )
}

