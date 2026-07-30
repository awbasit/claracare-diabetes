export type EventType =
  | "glucose"
  | "meal"
  | "medication"
  | "exercise"
  | "sleep"
  | "stress"
  | "symptom"
  | "vitals"

export type EventSource = "manual" | "imported"

export type GlucoseUnit = "mg_dl" | "mmol_l"
export type GlucoseReadingType =
  | "fasting"
  | "before_breakfast"
  | "after_breakfast"
  | "before_lunch"
  | "after_lunch"
  | "before_dinner"
  | "after_dinner"
  | "bedtime"
  | "random"
export type MealType = "breakfast" | "lunch" | "dinner" | "snack"
export type ExerciseIntensity = "light" | "moderate" | "vigorous"
export type SleepQuality = "poor" | "fair" | "good" | "excellent"
export type Mood = "low" | "neutral" | "good" | "high"
export type SymptomType =
  | "excessive_thirst"
  | "frequent_urination"
  | "blurred_vision"
  | "fatigue"
  | "dizziness"
  | "sweating"
  | "confusion"
  | "foot_pain"
  | "chest_pain"
  | "breathing_difficulty"
  | "nausea"
  | "vomiting"
  | "other"
export type SymptomSeverity = "mild" | "moderate" | "severe"

// --- Detail payloads — mirror the backend's discriminated union exactly
// (app/health_events/timeline/schemas.py) so the timeline feed, dashboard
// cards, and history list can all render off one shape without per-field
// switches, only a single switch on `event_type`.

export interface GlucoseDetail {
  event_type: "glucose"
  value: number
  unit: GlucoseUnit
  reading_type: GlucoseReadingType
  confidence: number | null
  manually_entered: boolean
}

export interface MealDetail {
  event_type: "meal"
  meal_type: MealType
  food_items: string
  estimated_carbs_g: number | null
  estimated_calories: number | null
  portion_size: string | null
  drink: string | null
}

export interface MedicationDetail {
  event_type: "medication"
  medication_id: string
  scheduled_time: string | null
  actual_time: string
  taken: boolean
  missed_reason: string | null
}

export interface ExerciseDetail {
  event_type: "exercise"
  exercise_type: string
  duration_minutes: number
  intensity: ExerciseIntensity
  calories_burned: number | null
  heart_rate_avg: number | null
}

export interface SleepDetail {
  event_type: "sleep"
  bedtime: string
  wake_time: string
  hours_slept: number
  quality: SleepQuality
  night_awakenings: number
}

export interface StressDetail {
  event_type: "stress"
  stress_level: number
  mood: Mood
  energy_level: number | null
}

export interface SymptomDetail {
  event_type: "symptom"
  symptom_type: SymptomType
  severity: SymptomSeverity
  duration_notes: string | null
}

export interface VitalsDetail {
  event_type: "vitals"
  weight_kg: number | null
  blood_pressure_systolic: number | null
  blood_pressure_diastolic: number | null
  heart_rate: number | null
}

export type EventDetail =
  | GlucoseDetail
  | MealDetail
  | MedicationDetail
  | ExerciseDetail
  | SleepDetail
  | StressDetail
  | SymptomDetail
  | VitalsDetail

export interface TimelineEvent {
  id: string
  patient_id: string
  event_type: EventType
  event_timestamp: string
  notes: string | null
  source: EventSource
  created_at: string
  updated_at: string
  detail: EventDetail
}

// --- Create inputs — match each type's *Create pydantic schema. Update
// inputs are the same shape with everything optional (matches the backend's
// exclude_unset partial-update semantics).

export interface GlucoseCreateInput {
  event_timestamp: string
  value: number
  unit: GlucoseUnit
  reading_type: GlucoseReadingType
  notes?: string | null
}

export interface MealCreateInput {
  event_timestamp: string
  meal_type: MealType
  food_items: string
  estimated_carbs_g?: number | null
  estimated_calories?: number | null
  portion_size?: string | null
  drink?: string | null
  notes?: string | null
}

export interface MedicationCreateInput {
  event_timestamp: string
  medication_id: string
  scheduled_time?: string | null
  actual_time: string
  taken: boolean
  missed_reason?: string | null
  notes?: string | null
}

export interface ExerciseCreateInput {
  event_timestamp: string
  exercise_type: string
  duration_minutes: number
  intensity: ExerciseIntensity
  calories_burned?: number | null
  heart_rate_avg?: number | null
  notes?: string | null
}

export interface SleepCreateInput {
  event_timestamp: string
  bedtime: string
  wake_time: string
  hours_slept: number
  quality: SleepQuality
  night_awakenings?: number
  notes?: string | null
}

export interface StressCreateInput {
  event_timestamp: string
  stress_level: number
  mood: Mood
  energy_level?: number | null
  notes?: string | null
}

export interface SymptomCreateInput {
  event_timestamp: string
  symptom_type: SymptomType
  severity: SymptomSeverity
  duration_notes?: string | null
  notes?: string | null
}

export interface VitalsCreateInput {
  event_timestamp: string
  weight_kg?: number | null
  blood_pressure_systolic?: number | null
  blood_pressure_diastolic?: number | null
  heart_rate?: number | null
  notes?: string | null
}

export type EventCreateInput =
  | GlucoseCreateInput
  | MealCreateInput
  | MedicationCreateInput
  | ExerciseCreateInput
  | SleepCreateInput
  | StressCreateInput
  | SymptomCreateInput
  | VitalsCreateInput

export type EventUpdateInput = Partial<EventCreateInput>
