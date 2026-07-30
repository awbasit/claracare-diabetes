import { api } from "@/services/api"
import type { EventType, TimelineEvent } from "@/types/healthEvents"
import type { DailySummary } from "@/types/timeline"

export interface GetTimelineParams {
  start?: string
  end?: string
  eventTypes?: EventType[]
  limit?: number
  offset?: number
}

export async function getTimeline(params: GetTimelineParams = {}): Promise<TimelineEvent[]> {
  const response = await api.get<TimelineEvent[]>("/api/patients/me/timeline", {
    params: {
      start: params.start,
      end: params.end,
      event_types: params.eventTypes,
      limit: params.limit,
      offset: params.offset,
    },
    paramsSerializer: { indexes: null },
  })
  return response.data
}

export async function getDailySummary(date?: string): Promise<DailySummary> {
  const response = await api.get<DailySummary>("/api/patients/me/timeline/summary", {
    params: date ? { date } : {},
  })
  return response.data
}
