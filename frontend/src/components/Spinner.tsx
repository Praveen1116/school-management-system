import React from 'react'

export default function Spinner(): React.ReactElement {
  return (
    <div className="flex items-center justify-center h-32">
      <div className="w-6 h-6 border-2 border-slate-300 border-t-slate-700 rounded-full animate-spin" />
    </div>
  )
}

