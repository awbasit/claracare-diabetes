import { useEffect, useState, type FormEvent } from "react"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { EVENT_TYPE_CONFIGS, type EventFieldConfig } from "@/features/timeline/eventTypeConfig"
import * as patientsService from "@/services/patientsService"
import type { EventType } from "@/types/healthEvents"
import type { Medication } from "@/types/patient"

interface EventFormProps {
  eventType: EventType
  initialValues?: Record<string, unknown>
  onSubmit: (values: Record<string, unknown>) => void
  isSubmitting: boolean
  submitLabel: string
  error?: string | null
}

// "2026-01-01T08:00:00Z" -> "2026-01-01T08:00" for <input type="datetime-local">
function toDatetimeLocal(value: unknown): string {
  if (typeof value !== "string" || !value) return ""
  return value.slice(0, 16)
}

function buildInitialState(
  eventType: EventType,
  initialValues: Record<string, unknown> | undefined
): Record<string, unknown> {
  const config = EVENT_TYPE_CONFIGS[eventType]
  const state: Record<string, unknown> = {
    event_timestamp: toDatetimeLocal(initialValues?.event_timestamp) || toDatetimeLocal(new Date().toISOString()),
    notes: (initialValues?.notes as string) ?? "",
  }
  for (const field of config.fields) {
    const raw = initialValues?.[field.name]
    if (field.kind === "datetime-local") {
      state[field.name] = toDatetimeLocal(raw)
    } else if (field.kind === "checkbox") {
      state[field.name] = Boolean(raw)
    } else {
      state[field.name] = raw ?? field.defaultValue ?? ""
    }
  }
  if (eventType === "medication") {
    state.medication_id = (initialValues?.medication_id as string) ?? ""
  }
  return state
}

export function EventForm({
  eventType,
  initialValues,
  onSubmit,
  isSubmitting,
  submitLabel,
  error,
}: EventFormProps) {
  const config = EVENT_TYPE_CONFIGS[eventType]
  const [values, setValues] = useState<Record<string, unknown>>(() =>
    buildInitialState(eventType, initialValues)
  )
  const [medications, setMedications] = useState<Medication[]>([])

  useEffect(() => {
    if (eventType !== "medication") return
    let isMounted = true
    patientsService
      .listMedications()
      .then((list) => {
        if (isMounted) setMedications(list)
      })
      .catch(() => {
        if (isMounted) setMedications([])
      })
    return () => {
      isMounted = false
    }
  }, [eventType])

  function setField(name: string, value: unknown) {
    setValues((prev) => ({ ...prev, [name]: value }))
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()

    const payload: Record<string, unknown> = {
      event_timestamp: new Date(values.event_timestamp as string).toISOString(),
      notes: values.notes || null,
    }
    for (const field of config.fields) {
      const raw = values[field.name]
      if (field.kind === "number") {
        payload[field.name] =
          raw === "" || raw === null || raw === undefined ? (field.defaultValue ?? null) : Number(raw)
      } else if (field.kind === "checkbox") {
        payload[field.name] = Boolean(raw)
      } else if (field.kind === "datetime-local") {
        payload[field.name] = raw ? new Date(raw as string).toISOString() : null
      } else {
        payload[field.name] = raw === "" ? null : raw
      }
    }
    if (eventType === "medication") {
      payload.medication_id = values.medication_id
    }

    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Label htmlFor="event_timestamp">When</Label>
        <Input
          id="event_timestamp"
          type="datetime-local"
          required
          value={values.event_timestamp as string}
          onChange={(event) => setField("event_timestamp", event.target.value)}
        />
      </div>

      {eventType === "medication" && (
        <div className="flex flex-col gap-2">
          <Label htmlFor="medication_id">Medication</Label>
          <Select
            id="medication_id"
            required
            value={values.medication_id as string}
            onChange={(event) => setField("medication_id", event.target.value)}
          >
            <option value="">Select a medication</option>
            {medications.map((medication) => (
              <option key={medication.id} value={medication.id}>
                {medication.name}
              </option>
            ))}
          </Select>
          {medications.length === 0 && (
            <p className="text-sm text-muted-foreground">
              No medications on file yet — add one from your profile first.
            </p>
          )}
        </div>
      )}

      {config.fields.map((field) => (
        <FieldInput
          key={field.name}
          field={field}
          value={values[field.name]}
          onChange={(value) => setField(field.name, value)}
        />
      ))}

      <div className="flex flex-col gap-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          value={values.notes as string}
          onChange={(event) => setField("notes", event.target.value)}
        />
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving…" : submitLabel}
      </Button>
    </form>
  )
}

function FieldInput({
  field,
  value,
  onChange,
}: {
  field: EventFieldConfig
  value: unknown
  onChange: (value: unknown) => void
}) {
  const id = `field-${field.name}`

  if (field.kind === "select") {
    return (
      <div className="flex flex-col gap-2">
        <Label htmlFor={id}>{field.label}</Label>
        <Select
          id={id}
          required={field.required}
          value={(value as string) ?? ""}
          onChange={(event) => onChange(event.target.value)}
        >
          <option value="">Select…</option>
          {field.options?.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      </div>
    )
  }

  if (field.kind === "textarea") {
    return (
      <div className="flex flex-col gap-2">
        <Label htmlFor={id}>{field.label}</Label>
        <Textarea
          id={id}
          required={field.required}
          value={(value as string) ?? ""}
          onChange={(event) => onChange(event.target.value)}
        />
      </div>
    )
  }

  if (field.kind === "checkbox") {
    return (
      <div className="flex items-center gap-2">
        <Checkbox id={id} checked={Boolean(value)} onCheckedChange={onChange} />
        <Label htmlFor={id} className="font-normal">
          {field.label}
        </Label>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      <Label htmlFor={id}>{field.label}</Label>
      <Input
        id={id}
        type={field.kind}
        required={field.required}
        min={field.min}
        max={field.max}
        step={field.step}
        value={(value as string) ?? ""}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  )
}
