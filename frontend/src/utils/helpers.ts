import axios from 'axios'

export function formatAmount(paise: number | undefined | null): string {
  if (paise == null) return '₹0.00'
  return `₹${(paise / 100).toFixed(2)}`
}

export function formatDate(isoString: string | undefined | null): string {
  if (!isoString) return ''
  try {
    return new Date(isoString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return isoString
  }
}

export function getDashboardPath(role: string): string {
  const paths: Record<string, string> = {
    admin: '/admin/dashboard',
    teacher: '/teacher/dashboard',
    guardian: '/guardian/dashboard',
  }
  return paths[role] || '/login'
}

export function extractError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data
    if (typeof data === 'object' && data !== null) {
      if ('error' in data && typeof data.error === 'object' && data.error !== null) {
        const errObj = data.error
        if (typeof errObj === 'object' && errObj !== null && 'message' in errObj && typeof errObj.message === 'string') {
          return errObj.message
        }
      }
      if ('detail' in data && typeof data.detail === 'string') {
        return data.detail
      }
      if ('message' in data && typeof data.message === 'string') {
        return data.message
      }
    }
    return err.message || 'Something went wrong'
  }
  if (err instanceof Error) return err.message
  return 'Something went wrong'
}
