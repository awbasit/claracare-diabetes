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

export interface DailyMealTrendPoint {
  date: string
  count: number
  average_carbs_g: number | null
}

export interface DailyMedicationTrendPoint {
  date: string
  taken_count: number
  missed_count: number
  adherence_pct: number | null
}

export interface DailyExerciseTrendPoint {
  date: string
  total_minutes: number
  session_count: number
}

export interface DailySleepTrendPoint {
  date: string
  average_hours: number | null
  average_quality_score: number | null
}

export interface DailyStressTrendPoint {
  date: string
  average_stress_level: number | null
  average_energy_level: number | null
}

export interface DailySymptomTrendPoint {
  date: string
  count: number
}

export interface DailyVitalsTrendPoint {
  date: string
  latest_weight_kg: number | null
  latest_blood_pressure_systolic: number | null
  latest_blood_pressure_diastolic: number | null
}

export interface TrendsResponse {
  period: TrendPeriod
  start_date: string
  end_date: string
  glucose_unit: GlucoseUnit
  glucose: DailyGlucoseTrendPoint[]
  meals: DailyMealTrendPoint[]
  medication: DailyMedicationTrendPoint[]
  exercise: DailyExerciseTrendPoint[]
  sleep: DailySleepTrendPoint[]
  stress: DailyStressTrendPoint[]
  symptoms: DailySymptomTrendPoint[]
  vitals: DailyVitalsTrendPoint[]
}
