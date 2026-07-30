import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import { DateRangeControls } from "@/features/timeline/DateRangeControls"
import { EVENT_TYPE_CONFIGS, EVENT_TYPE_ORDER } from "@/features/timeline/eventTypeConfig"
import { TimelineFeed } from "@/features/timeline/TimelineFeed"
import { isoDateDaysAgo, todayIsoDate, toRangeEndIso, toRangeStartIso } from "@/lib/dateRange"
import * as healthEventsService from "@/services/healthEventsService"
import * as timelineService from "@/services/timelineService"
import type { EventType, TimelineEvent } from "@/types/healthEvents"

export function HistoryPage() {
  const [start, setStart] = useState(() => isoDateDaysAgo(29))
  const [end, setEnd] = useState(() => todayIsoDate())
  const [typeFilter, setTypeFilter] = useState<EventType | "">("")
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    setIsLoading(true)
    setError(null)
    timelineService
      .getTimeline({
        start: toRangeStartIso(start),
        end: toRangeEndIso(end),
        eventTypes: typeFilter ? [typeFilter] : undefined,
        limit: 200,
      })
      .then((data) => {
        if (isMounted) setEvents(data)
      })
      .catch(() => {
        if (isMounted) setError("Couldn't load your history.")
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [start, end, typeFilter])

  async function handleDelete(event: TimelineEvent) {
    if (!window.confirm("Delete this entry? This can't be undone.")) return
    setDeletingId(event.id)
    try {
      await healthEventsService.deleteHealthEvent(event.event_type, event.id)
      setEvents((prev) => prev.filter((item) => item.id !== event.id))
    } catch {
      setError("Couldn't delete that entry. Please try again.")
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">History</h1>
        <Button asChild>
          <Link to="/events/new">Log event</Link>
        </Button>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <DateRangeControls
          start={start}
          end={end}
          onChange={(nextStart, nextEnd) => {
            setStart(nextStart)
            setEnd(nextEnd)
          }}
        />
        <div className="flex flex-col gap-1">
          <label htmlFor="type-filter" className="text-xs text-muted-foreground">
            Event type
          </label>
          <Select
            id="type-filter"
            value={typeFilter}
            onChange={(event) => setTypeFilter(event.target.value as EventType | "")}
          >
            <option value="">All types</option>
            {EVENT_TYPE_ORDER.map((type) => (
              <option key={type} value={type}>
                {EVENT_TYPE_CONFIGS[type].label}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}
      {!isLoading && (
        <TimelineFeed
          events={events}
          emptyMessage="No events match these filters."
          renderActions={(event) => (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to={`/events/${event.event_type}/${event.id}/edit`}>Edit</Link>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDelete(event)}
                disabled={deletingId === event.id}
              >
                {deletingId === event.id ? "Deleting…" : "Delete"}
              </Button>
            </>
          )}
        />
      )}
    </div>
  )
}
