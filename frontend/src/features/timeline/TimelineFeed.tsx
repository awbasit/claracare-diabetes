import type { ReactNode } from "react"

import { EVENT_TYPE_CONFIGS } from "@/features/timeline/eventTypeConfig"
import { formatEventSummary } from "@/features/timeline/formatEventSummary"
import type { TimelineEvent } from "@/types/healthEvents"

function dayKey(isoTimestamp: string): string {
  return isoTimestamp.slice(0, 10)
}

function formatDayHeading(key: string): string {
  const date = new Date(`${key}T00:00:00Z`)
  const today = new Date()
  const todayKey = today.toISOString().slice(0, 10)
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const yesterdayKey = yesterday.toISOString().slice(0, 10)

  if (key === todayKey) return "Today"
  if (key === yesterdayKey) return "Yesterday"
  return date.toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  })
}

function formatTime(isoTimestamp: string): string {
  return new Date(isoTimestamp).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })
}

function groupByDay(events: TimelineEvent[]): [string, TimelineEvent[]][] {
  const groups = new Map<string, TimelineEvent[]>()
  for (const event of events) {
    const key = dayKey(event.event_timestamp)
    const existing = groups.get(key)
    if (existing) {
      existing.push(event)
    } else {
      groups.set(key, [event])
    }
  }
  return Array.from(groups.entries())
}

interface TimelineFeedProps {
  events: TimelineEvent[]
  renderActions?: (event: TimelineEvent) => ReactNode
  emptyMessage?: string
}

export function TimelineFeed({ events, renderActions, emptyMessage }: TimelineFeedProps) {
  if (events.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">{emptyMessage ?? "No events in this range."}</p>
    )
  }

  const groups = groupByDay(events)

  return (
    <div className="flex flex-col gap-6">
      {groups.map(([day, dayEvents]) => (
        <div key={day}>
          <h2 className="mb-2 text-sm font-semibold text-muted-foreground">{formatDayHeading(day)}</h2>
          <ul className="flex flex-col gap-2">
            {dayEvents.map((event) => {
              const config = EVENT_TYPE_CONFIGS[event.event_type]
              const Icon = config.icon
              return (
                <li
                  key={event.id}
                  className="flex items-start gap-3 rounded-lg border px-3 py-2.5"
                >
                  <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full bg-muted">
                    <Icon className="size-4 text-muted-foreground" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-medium">{config.label}</p>
                      <span className="text-xs text-muted-foreground">
                        {formatTime(event.event_timestamp)}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{formatEventSummary(event.detail)}</p>
                    {event.notes && <p className="mt-1 text-sm italic text-muted-foreground">{event.notes}</p>}
                  </div>
                  {renderActions && <div className="flex shrink-0 gap-1">{renderActions(event)}</div>}
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </div>
  )
}
