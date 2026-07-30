import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { EventForm } from "@/features/events/EventForm"
import { EVENT_TYPE_CONFIGS, EVENT_TYPE_ORDER } from "@/features/timeline/eventTypeConfig"
import * as healthEventsService from "@/services/healthEventsService"
import type { EventCreateInput, EventType } from "@/types/healthEvents"

export function AddEventPage() {
  const navigate = useNavigate()
  const [eventType, setEventType] = useState<EventType | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(values: Record<string, unknown>) {
    if (!eventType) return
    setIsSubmitting(true)
    setError(null)
    try {
      await healthEventsService.createHealthEvent(eventType, values as unknown as EventCreateInput)
      navigate("/timeline", { replace: true })
    } catch {
      setError("Couldn't save that entry. Please check the fields and try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-6 px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Log an event</h1>
        <Button variant="outline" asChild>
          <Link to="/dashboard">Cancel</Link>
        </Button>
      </div>

      {!eventType ? (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {EVENT_TYPE_ORDER.map((type) => {
            const config = EVENT_TYPE_CONFIGS[type]
            const Icon = config.icon
            return (
              <button
                key={type}
                type="button"
                onClick={() => setEventType(type)}
                className="flex flex-col items-center gap-2 rounded-lg border p-4 text-sm font-medium transition-colors hover:bg-accent"
              >
                <Icon className="size-5 text-muted-foreground" />
                {config.label}
              </button>
            )
          })}
        </div>
      ) : (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">{EVENT_TYPE_CONFIGS[eventType].label}</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setEventType(null)}>
                Change type
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <EventForm
              eventType={eventType}
              onSubmit={handleSubmit}
              isSubmitting={isSubmitting}
              submitLabel="Save"
              error={error}
            />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
