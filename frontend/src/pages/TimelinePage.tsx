import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { DateRangeControls } from "@/features/timeline/DateRangeControls"
import { TimelineFeed } from "@/features/timeline/TimelineFeed"
import { isoDateDaysAgo, todayIsoDate, toRangeEndIso, toRangeStartIso } from "@/lib/dateRange"
import * as timelineService from "@/services/timelineService"
import type { TimelineEvent } from "@/types/healthEvents"

export function TimelinePage() {
  const [start, setStart] = useState(() => isoDateDaysAgo(6))
  const [end, setEnd] = useState(() => todayIsoDate())
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    setIsLoading(true)
    setError(null)
    timelineService
      .getTimeline({ start: toRangeStartIso(start), end: toRangeEndIso(end), limit: 200 })
      .then((data) => {
        if (isMounted) setEvents(data)
      })
      .catch(() => {
        if (isMounted) setError("Couldn't load your timeline.")
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [start, end])

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Timeline</h1>
        <Button asChild>
          <Link to="/events/new">Log event</Link>
        </Button>
      </div>

      <DateRangeControls
        start={start}
        end={end}
        onChange={(nextStart, nextEnd) => {
          setStart(nextStart)
          setEnd(nextEnd)
        }}
      />

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}
      {!isLoading && !error && <TimelineFeed events={events} />}
    </div>
  )
}
