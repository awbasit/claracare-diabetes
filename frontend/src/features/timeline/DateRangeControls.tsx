import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface DateRangeControlsProps {
  start: string
  end: string
  onChange: (start: string, end: string) => void
}

export function DateRangeControls({ start, end, onChange }: DateRangeControlsProps) {
  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="flex flex-col gap-1">
        <Label htmlFor="range-start" className="text-xs text-muted-foreground">
          From
        </Label>
        <Input
          id="range-start"
          type="date"
          value={start}
          max={end}
          onChange={(event) => onChange(event.target.value, end)}
        />
      </div>
      <div className="flex flex-col gap-1">
        <Label htmlFor="range-end" className="text-xs text-muted-foreground">
          To
        </Label>
        <Input
          id="range-end"
          type="date"
          value={end}
          min={start}
          onChange={(event) => onChange(start, event.target.value)}
        />
      </div>
    </div>
  )
}
