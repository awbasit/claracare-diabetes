import type { EventType, GlucoseDetail, GlucoseUnit } from "@/types/healthEvents"

export interface DailySummary {
  date: string
  event_counts: Record<EventType, number>
  total_events: number
  medications_taken: number
  medications_missed: number
  latest_glucose: GlucoseDetail | null
  latest_glucose_timestamp: string | null
  glucose_average_mg_dl: number | null
  total_exercise_minutes: number
  average_stress_level: number | null
}

export type TrendPeriod = "week" | "month"

export interface DailyGlucoseTrendPoint {
  date: string
  average: number | null
  minimum: number | null
  maximum: number | null
  count: number
}

export interface GlucoseTrendResponse {
  period: TrendPeriod
  unit: GlucoseUnit
  start_date: string
  end_date: string
  points: DailyGlucoseTrendPoint[]
}
