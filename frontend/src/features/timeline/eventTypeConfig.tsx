import {
  AlertTriangle,
  Brain,
  Droplet,
  Dumbbell,
  HeartPulse,
  Moon,
  Pill,
  Utensils,
  type LucideIcon,
} from "lucide-react"

import type { EventType } from "@/types/healthEvents"

export type FieldKind = "text" | "number" | "datetime-local" | "select" | "textarea" | "checkbox"

export interface SelectOption {
  value: string
  label: string
}

export interface EventFieldConfig {
  name: string
  label: string
  kind: FieldKind
  options?: SelectOption[]
  required?: boolean
  min?: number
  max?: number
  step?: number | string
  placeholder?: string
  /** Used when the field is left blank on create — some backend Create
   * schemas default this to a concrete value (e.g. night_awakenings: int =
   * 0) rather than accepting null, so blank can't just mean "send null". */
  defaultValue?: number | string | boolean
}

export interface EventTypeConfig {
  type: EventType
  label: string
  icon: LucideIcon
  /** Fields beyond the common event_timestamp/notes every type already has.
   * "medication" additionally needs a medication_id select populated from
   * the patient's own medication list — handled as a special case in the
   * form component rather than a static option list here. */
  fields: EventFieldConfig[]
}

const GLUCOSE_READING_TYPE_OPTIONS: SelectOption[] = [
  { value: "fasting", label: "Fasting" },
  { value: "before_breakfast", label: "Before breakfast" },
  { value: "after_breakfast", label: "After breakfast" },
  { value: "before_lunch", label: "Before lunch" },
  { value: "after_lunch", label: "After lunch" },
  { value: "before_dinner", label: "Before dinner" },
  { value: "after_dinner", label: "After dinner" },
  { value: "bedtime", label: "Bedtime" },
  { value: "random", label: "Random" },
]

const SYMPTOM_TYPE_OPTIONS: SelectOption[] = [
  { value: "excessive_thirst", label: "Excessive thirst" },
  { value: "frequent_urination", label: "Frequent urination" },
  { value: "blurred_vision", label: "Blurred vision" },
  { value: "fatigue", label: "Fatigue" },
  { value: "dizziness", label: "Dizziness" },
  { value: "sweating", label: "Sweating" },
  { value: "confusion", label: "Confusion" },
  { value: "foot_pain", label: "Foot pain" },
  { value: "chest_pain", label: "Chest pain" },
  { value: "breathing_difficulty", label: "Breathing difficulty" },
  { value: "nausea", label: "Nausea" },
  { value: "vomiting", label: "Vomiting" },
  { value: "other", label: "Other" },
]

export const EVENT_TYPE_CONFIGS: Record<EventType, EventTypeConfig> = {
  glucose: {
    type: "glucose",
    label: "Glucose",
    icon: Droplet,
    fields: [
      { name: "value", label: "Value", kind: "number", required: true, step: "0.1" },
      {
        name: "unit",
        label: "Unit",
        kind: "select",
        required: true,
        options: [
          { value: "mg_dl", label: "mg/dL" },
          { value: "mmol_l", label: "mmol/L" },
        ],
      },
      {
        name: "reading_type",
        label: "Reading type",
        kind: "select",
        required: true,
        options: GLUCOSE_READING_TYPE_OPTIONS,
      },
    ],
  },
  meal: {
    type: "meal",
    label: "Meal",
    icon: Utensils,
    fields: [
      {
        name: "meal_type",
        label: "Meal type",
        kind: "select",
        required: true,
        options: [
          { value: "breakfast", label: "Breakfast" },
          { value: "lunch", label: "Lunch" },
          { value: "dinner", label: "Dinner" },
          { value: "snack", label: "Snack" },
        ],
      },
      { name: "food_items", label: "Food items", kind: "textarea", required: true },
      { name: "estimated_carbs_g", label: "Estimated carbs (g)", kind: "number", step: "0.1" },
      { name: "estimated_calories", label: "Estimated calories", kind: "number" },
      { name: "portion_size", label: "Portion size", kind: "text" },
      { name: "drink", label: "Drink", kind: "text" },
    ],
  },
  medication: {
    type: "medication",
    label: "Medication",
    icon: Pill,
    fields: [
      { name: "scheduled_time", label: "Scheduled time", kind: "datetime-local" },
      { name: "actual_time", label: "Actual time", kind: "datetime-local", required: true },
      { name: "taken", label: "Taken", kind: "checkbox" },
      { name: "missed_reason", label: "Missed reason (if not taken)", kind: "text" },
    ],
  },
  exercise: {
    type: "exercise",
    label: "Exercise",
    icon: Dumbbell,
    fields: [
      { name: "exercise_type", label: "Exercise type", kind: "text", required: true },
      { name: "duration_minutes", label: "Duration (minutes)", kind: "number", required: true },
      {
        name: "intensity",
        label: "Intensity",
        kind: "select",
        required: true,
        options: [
          { value: "light", label: "Light" },
          { value: "moderate", label: "Moderate" },
          { value: "vigorous", label: "Vigorous" },
        ],
      },
      { name: "calories_burned", label: "Calories burned", kind: "number" },
      { name: "heart_rate_avg", label: "Average heart rate", kind: "number" },
    ],
  },
  sleep: {
    type: "sleep",
    label: "Sleep",
    icon: Moon,
    fields: [
      { name: "bedtime", label: "Bedtime", kind: "datetime-local", required: true },
      { name: "wake_time", label: "Wake time", kind: "datetime-local", required: true },
      { name: "hours_slept", label: "Hours slept", kind: "number", required: true, step: "0.1" },
      {
        name: "quality",
        label: "Quality",
        kind: "select",
        required: true,
        options: [
          { value: "poor", label: "Poor" },
          { value: "fair", label: "Fair" },
          { value: "good", label: "Good" },
          { value: "excellent", label: "Excellent" },
        ],
      },
      {
        name: "night_awakenings",
        label: "Night awakenings",
        kind: "number",
        min: 0,
        defaultValue: 0,
      },
    ],
  },
  stress: {
    type: "stress",
    label: "Stress",
    icon: Brain,
    fields: [
      { name: "stress_level", label: "Stress level (1-10)", kind: "number", required: true, min: 1, max: 10 },
      {
        name: "mood",
        label: "Mood",
        kind: "select",
        required: true,
        options: [
          { value: "low", label: "Low" },
          { value: "neutral", label: "Neutral" },
          { value: "good", label: "Good" },
          { value: "high", label: "High" },
        ],
      },
      { name: "energy_level", label: "Energy level (1-10)", kind: "number", min: 1, max: 10 },
    ],
  },
  symptom: {
    type: "symptom",
    label: "Symptom",
    icon: AlertTriangle,
    fields: [
      {
        name: "symptom_type",
        label: "Symptom",
        kind: "select",
        required: true,
        options: SYMPTOM_TYPE_OPTIONS,
      },
      {
        name: "severity",
        label: "Severity",
        kind: "select",
        required: true,
        options: [
          { value: "mild", label: "Mild" },
          { value: "moderate", label: "Moderate" },
          { value: "severe", label: "Severe" },
        ],
      },
      { name: "duration_notes", label: "Duration notes", kind: "text" },
    ],
  },
  vitals: {
    type: "vitals",
    label: "Vitals",
    icon: HeartPulse,
    fields: [
      { name: "weight_kg", label: "Weight (kg)", kind: "number", step: "0.1" },
      { name: "blood_pressure_systolic", label: "Blood pressure — systolic", kind: "number" },
      { name: "blood_pressure_diastolic", label: "Blood pressure — diastolic", kind: "number" },
      { name: "heart_rate", label: "Heart rate", kind: "number" },
    ],
  },
}

export const EVENT_TYPE_ORDER: EventType[] = [
  "glucose",
  "meal",
  "medication",
  "exercise",
  "sleep",
  "stress",
  "symptom",
  "vitals",
]
