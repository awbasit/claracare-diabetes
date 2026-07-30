import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { EventForm } from "@/features/events/EventForm"
import { EVENT_TYPE_CONFIGS } from "@/features/timeline/eventTypeConfig"
import * as healthEventsService from "@/services/healthEventsService"
import type { EventType } from "@/types/healthEvents"

export function EditEventPage() {
  const params = useParams<{ eventType: string; id: string }>()
  const navigate = useNavigate()
  const [initialValues, setInitialValues] = useState<Record<string, unknown> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const eventType = params.eventType as EventType | undefined
  const id = params.id
  const isValidType = Boolean(eventType && eventType in EVENT_TYPE_CONFIGS)

  useEffect(() => {
    if (!isValidType || !eventType || !id) return
    let isMounted = true
    healthEventsService
      .getHealthEvent(eventType, id)
      .then((data) => {
        if (isMounted) setInitialValues(data)
      })
      .catch(() => {
        if (isMounted) setLoadError("Couldn't load this entry.")
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [eventType, id, isValidType])

  async function handleSubmit(values: Record<string, unknown>) {
    if (!eventType || !id) return
    setIsSubmitting(true)
    setSubmitError(null)
    try {
      await healthEventsService.updateHealthEvent(eventType, id, values)
      navigate("/history", { replace: true })
    } catch {
      setSubmitError("Couldn't save your changes. Please check the fields and try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!isValidType || !eventType) {
    return (
      <div className="flex min-h-svh items-center justify-center text-sm text-destructive">
        Unknown event type.
      </div>
    )
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-6 px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Edit {EVENT_TYPE_CONFIGS[eventType].label.toLowerCase()}</h1>
        <Button variant="outline" asChild>
          <Link to="/history">Cancel</Link>
        </Button>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {loadError && <p className="text-sm text-destructive">{loadError}</p>}

      {!isLoading && !loadError && initialValues && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{EVENT_TYPE_CONFIGS[eventType].label}</CardTitle>
          </CardHeader>
          <CardContent>
            <EventForm
              eventType={eventType}
              initialValues={initialValues}
              onSubmit={handleSubmit}
              isSubmitting={isSubmitting}
              submitLabel="Save changes"
              error={submitError}
            />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
