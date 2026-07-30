import * as React from "react"

import { cn } from "@/lib/utils"

// Native <input type="checkbox"> rather than @radix-ui/react-checkbox — this
// project doesn't need indeterminate state or custom keyboard handling, and a
// native checkbox is simpler and just as accessible for a plain on/off toggle.
interface CheckboxProps extends Omit<React.ComponentProps<"input">, "type" | "onChange"> {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
}

function Checkbox({ className, checked, onCheckedChange, ...props }: CheckboxProps) {
  return (
    <input
      type="checkbox"
      data-slot="checkbox"
      checked={checked}
      onChange={(event) => onCheckedChange(event.target.checked)}
      className={cn(
        "border-input size-4 shrink-0 rounded-[4px] border shadow-xs outline-none accent-primary focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    />
  )
}

export { Checkbox }
