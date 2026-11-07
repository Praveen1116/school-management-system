import React, { useState } from 'react'
import { createUser } from '@/api/users'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { extractError } from '@/utils/helpers'

interface Props {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function AdminFormModal({ isOpen, onClose, onSuccess }: Props): React.ReactElement {
  const [fullName, setFullName] = useState<string>('')
  const [email, setEmail] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [submitting, setSubmitting] = useState<boolean>(false)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()
    try {
      setSubmitting(true)
      await createUser({ email, password, role: 'admin', full_name: fullName })
      setFullName('')
      setEmail('')
      setPassword('')
      onSuccess()
    } catch (err: unknown) {
      alert(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open: boolean) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Administrator</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          <div>
            <Label htmlFor="admin-name">Full Name</Label>
            <Input
              id="admin-name"
              required
              value={fullName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFullName(e.target.value)}
              placeholder="e.g. Dr. Jane Smith"
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="admin-email">Email Address</Label>
            <Input
              id="admin-email"
              type="email"
              required
              value={email}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
              placeholder="admin@school.org"
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="admin-password">Password</Label>
            <Input
              id="admin-password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              placeholder="Minimum 8 characters"
              className="mt-1"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting} className="bg-slate-900 text-white">
              {submitting ? 'Creating...' : 'Create Admin'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

