import type { EventDetail } from "@/types/healthEvents"

function titleCase(value: string): string {
  return value
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

export function formatEventSummary(detail: EventDetail): string {
  switch (detail.event_type) {
    case "glucose": {
      const unit = detail.unit === "mg_dl" ? "mg/dL" : "mmol/L"
      return `${detail.value} ${unit} · ${titleCase(detail.reading_type)}`
    }
    case "meal":
      return `${titleCase(detail.meal_type)} · ${detail.food_items}`
    case "medication":
      return detail.taken ? "Taken" : `Missed${detail.missed_reason ? ` · ${detail.missed_reason}` : ""}`
    case "exercise":
      return `${titleCase(detail.exercise_type)} · ${detail.duration_minutes} min · ${titleCase(detail.intensity)}`
    case "sleep":
      return `${detail.hours_slept}h · ${titleCase(detail.quality)}`
    case "stress":
      return `Level ${detail.stress_level}/10 · ${titleCase(detail.mood)} mood`
    case "symptom":
      return `${titleCase(detail.symptom_type)} · ${titleCase(detail.severity)}`
    case "vitals": {
      const parts: string[] = []
      if (detail.weight_kg !== null) parts.push(`${detail.weight_kg} kg`)
      if (detail.blood_pressure_systolic !== null && detail.blood_pressure_diastolic !== null) {
        parts.push(`${detail.blood_pressure_systolic}/${detail.blood_pressure_diastolic} mmHg`)
      }
      if (detail.heart_rate !== null) parts.push(`${detail.heart_rate} bpm`)
      return parts.length > 0 ? parts.join(" · ") : "No values recorded"
    }
  }
}
