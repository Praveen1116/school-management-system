import React from 'react'

interface Props {
  message: string | null
}

export default function ErrorMessage({ message }: Props): React.ReactElement | null {
  if (!message) return null
  return (
    <div className="p-3 my-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md">
      {message}
    </div>
  )
}

