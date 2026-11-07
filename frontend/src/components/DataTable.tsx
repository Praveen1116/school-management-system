import React from 'react'
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table'
import Spinner from './Spinner'
import EmptyState from './EmptyState'

export interface Column<T> {
  key?: keyof T
  label: string
  render?: (row: T) => React.ReactNode
}

export interface Props<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  emptyMessage?: string
}

function getRowKey<T>(row: T, idx: number): string {
  if (typeof row === 'object' && row !== null && 'id' in row) {
    const idVal = row.id
    if (typeof idVal === 'string' || typeof idVal === 'number') {
      return String(idVal)
    }
  }
  return String(idx)
}

function renderCell<T>(col: Column<T>, row: T): React.ReactNode {
  if (col.render) {
    return col.render(row)
  }
  if (col.key !== undefined) {
    const val = row[col.key]
    if (typeof val === 'string' || typeof val === 'number') {
      return val
    }
  }
  return null
}

export default function DataTable<T>({
  columns = [],
  data = [],
  loading = false,
  emptyMessage = 'No records found',
}: Props<T>): React.ReactElement {
  if (loading) return <Spinner />

  if (!data || data.length === 0) {
    return <EmptyState message={emptyMessage} />
  }

  return (
    <div className="border border-slate-200 rounded-md overflow-hidden bg-white">
      <Table>
        <TableHeader className="bg-slate-50">
          <TableRow>
            {columns.map((col, idx) => (
              <TableHead key={String(col.key ?? col.label ?? idx)} className="text-slate-700 font-medium">
                {col.label}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((row, idx) => (
            <TableRow key={getRowKey(row, idx)}>
              {columns.map((col, cIdx) => (
                <TableCell key={String(col.key ?? col.label ?? cIdx)}>
                  {renderCell(col, row)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
