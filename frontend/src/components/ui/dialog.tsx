import * as React from "react"
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog"
import { cn } from "cn"
import { Button } from "@/components/ui/button"
import { XIcon } from "lucide-react"

const Dialog = (props: React.ComponentProps<typeof DialogPrimitive.Root>): React.ReactElement => (
  <DialogPrimitive.Root data-slot="dialog" {...props} />
)
const DialogTrigger = (props: React.ComponentProps<typeof DialogPrimitive.Trigger>): React.ReactElement => (
  <DialogPrimitive.Trigger data-slot="dialog-trigger" {...props} />
)
const DialogPortal = (props: React.ComponentProps<typeof DialogPrimitive.Portal>): React.ReactElement => (
  <DialogPrimitive.Portal data-slot="dialog-portal" {...props} />
)
const DialogClose = (props: React.ComponentProps<typeof DialogPrimitive.Close>): React.ReactElement => (
  <DialogPrimitive.Close data-slot="dialog-close" {...props} />
)

function DialogOverlay({ className, ...props }: React.ComponentProps<typeof DialogPrimitive.Backdrop>): React.ReactElement {
  return (
    <DialogPrimitive.Backdrop
      data-slot="dialog-overlay"
      className={cn("fixed inset-0 isolate z-50 bg-black/10 duration-100", className)}
      {...props}
    />
  )
}

interface DialogContentProps extends React.ComponentProps<typeof DialogPrimitive.Popup> {
  showCloseButton?: boolean
}

function DialogContent({ className, children, showCloseButton = true, ...props }: DialogContentProps): React.ReactElement {
  return (
    <DialogPortal>
      <DialogOverlay />
      <DialogPrimitive.Popup
        data-slot="dialog-content"
        className={cn("fixed top-1/2 left-1/2 z-50 grid w-full max-w-[calc(100%-2rem)] -translate-x-1/2 -translate-y-1/2 gap-4 rounded-xl bg-popover p-4 text-sm text-popover-foreground ring-1 ring-foreground/10 duration-100 outline-none sm:max-w-md bg-white", className)}
        {...props}
      >
        {children}
        {showCloseButton && (
          <DialogPrimitive.Close data-slot="dialog-close" render={<Button variant="ghost" className="absolute top-2 right-2" size="icon-sm" />}>
            <XIcon />
            <span className="sr-only">Close</span>
          </DialogPrimitive.Close>
        )}
      </DialogPrimitive.Popup>
    </DialogPortal>
  )
}

function DialogHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>): React.ReactElement {
  return <div data-slot="dialog-header" className={cn("flex flex-col gap-2", className)} {...props} />
}

interface DialogFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  showCloseButton?: boolean
}

function DialogFooter({ className, showCloseButton = false, children, ...props }: DialogFooterProps): React.ReactElement {
  return (
    <div data-slot="dialog-footer" className={cn("-mx-4 -mb-4 flex flex-col-reverse gap-2 rounded-b-xl border-t bg-muted/50 p-4 sm:flex-row sm:justify-end", className)} {...props}>
      {children}
      {showCloseButton && <DialogPrimitive.Close render={<Button variant="outline" />}>Close</DialogPrimitive.Close>}
    </div>
  )
}

function DialogTitle({ className, ...props }: React.ComponentProps<typeof DialogPrimitive.Title>): React.ReactElement {
  return <DialogPrimitive.Title data-slot="dialog-title" className={cn("font-heading text-base leading-none font-medium", className)} {...props} />
}

function DialogDescription({ className, ...props }: React.ComponentProps<typeof DialogPrimitive.Description>): React.ReactElement {
  return <DialogPrimitive.Description data-slot="dialog-description" className={cn("text-sm text-muted-foreground", className)} {...props} />
}

export { Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogOverlay, DialogPortal, DialogTitle, DialogTrigger }

