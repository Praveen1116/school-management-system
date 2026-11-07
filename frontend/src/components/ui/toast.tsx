import * as React from "react"
import { Toast as ToastPrimitive } from "@base-ui/react/toast"
import { cn } from "cn"
import { Button } from "@/components/ui/button"
import { XIcon, CircleCheckIcon, InfoIcon, TriangleAlertIcon, OctagonXIcon, Loader2Icon } from "lucide-react"

const toast = ToastPrimitive.createToastManager()
const ToastProvider = (props: React.ComponentProps<typeof ToastPrimitive.Provider>): React.ReactElement => <ToastPrimitive.Provider {...props} />
const ToastPortal = (props: React.ComponentProps<typeof ToastPrimitive.Portal>): React.ReactElement => <ToastPrimitive.Portal data-slot="toast-portal" {...props} />

const ToastViewport = ({ className, ...props }: React.ComponentProps<typeof ToastPrimitive.Viewport>): React.ReactElement => (
  <ToastPrimitive.Viewport data-slot="toast-viewport" className={cn("pointer-events-none fixed inset-x-4 bottom-4 z-50 mx-auto w-auto max-w-sm outline-none sm:right-4 sm:left-auto sm:mx-0 sm:w-full", className)} {...props} />
)

const Toast = ({ className, ...props }: React.ComponentProps<typeof ToastPrimitive.Root>): React.ReactElement => (
  <ToastPrimitive.Root data-slot="toast" className={cn("group/toast pointer-events-auto absolute right-0 bottom-0 z-[calc(1000-var(--toast-index))] w-full origin-bottom rounded-2xl border bg-popover text-popover-foreground shadow-lg will-change-transform outline-none select-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50", className)} {...props} />
)

const ToastContent = ({ className, ...props }: React.ComponentProps<typeof ToastPrimitive.Content>): React.ReactElement => (
  <ToastPrimitive.Content data-slot="toast-content" className={cn("flex h-full items-center gap-3 overflow-hidden p-4 transition-opacity duration-250 ease-[cubic-bezier(0.22,1,0.36,1)]", className)} {...props} />
)

const ToastTitle = ({ className, ...props }: React.ComponentProps<typeof ToastPrimitive.Title>): React.ReactElement => <ToastPrimitive.Title data-slot="toast-title" className={cn("text-sm font-medium", className)} {...props} />
const ToastDescription = ({ className, ...props }: React.ComponentProps<typeof ToastPrimitive.Description>): React.ReactElement => <ToastPrimitive.Description data-slot="toast-description" className={cn("text-sm text-muted-foreground", className)} {...props} />
const ToastAction = ({ className, render = <Button variant="outline" size="sm" />, ...props }: React.ComponentProps<typeof ToastPrimitive.Action>): React.ReactElement => <ToastPrimitive.Action data-slot="toast-action" render={render} className={cn("shrink-0", className)} {...props} />

function ToastClose({ className, children, render = <Button variant="ghost" size="icon-sm" />, ...props }: React.ComponentProps<typeof ToastPrimitive.Close>): React.ReactElement {
  return (
    <ToastPrimitive.Close data-slot="toast-close" aria-label="Close toast" render={render} className={cn("relative shrink-0 text-muted-foreground after:absolute hover:text-foreground", className)} {...props}>
      {children ?? <XIcon aria-hidden="true" />}
    </ToastPrimitive.Close>
  )
}

function ToastIcon({ type }: { type?: string }): React.ReactElement | null {
  const icons: Record<string, React.ReactElement> = { success: <CircleCheckIcon />, info: <InfoIcon />, warning: <TriangleAlertIcon />, error: <OctagonXIcon className="text-destructive" />, loading: <Loader2Icon className="animate-spin" /> }
  const icon = type ? icons[type] : null
  if (!icon) return null
  return <span data-slot="toast-icon" className="shrink-0 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4">{icon}</span>
}

function ToastList(): React.ReactElement[] {
  const { toasts } = ToastPrimitive.useToastManager()
  return toasts.map((t) => (
    <Toast key={t.id} toast={t}>
      <ToastContent>
        <ToastIcon type={t.type} />
        <div className="flex min-w-0 flex-1 flex-col gap-1"><ToastTitle /><ToastDescription /></div>
        <ToastAction /><ToastClose />
      </ToastContent>
    </Toast>
  ))
}

function Toaster({ children, toastManager = toast, ...props }: React.ComponentProps<typeof ToastProvider> & { toastManager?: typeof toast }): React.ReactElement {
  return (
    <ToastProvider toastManager={toastManager} {...props}>
      {children}
      <ToastPortal><ToastViewport><ToastList /></ToastViewport></ToastPortal>
    </ToastProvider>
  )
}

const createToastManager = ToastPrimitive.createToastManager
const useToastManager = ToastPrimitive.useToastManager

export { Toaster, Toast, ToastAction, ToastClose, ToastContent, ToastDescription, ToastPortal, ToastProvider, ToastTitle, ToastViewport, createToastManager, toast, useToastManager }

