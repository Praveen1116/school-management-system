import React from 'react'

interface Props {
  message?: string
}

export default function EmptyState({ message = 'No records found' }: Props): React.ReactElement {
  return (
    <div className="flex items-center justify-center py-12 text-sm text-slate-500">
      {message}
    </div>
  )
}

