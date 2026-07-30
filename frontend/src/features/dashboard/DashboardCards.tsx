import { useEffect, useState } from "react"

import { StatCard } from "@/features/dashboard/StatCard"
import * as healthEventsService from "@/services/healthEventsService"
import * as timelineService from "@/services/timelineService"
import type { SleepDetail, VitalsDetail } from "@/types/healthEvents"
import type { DailySummary } from "@/types/timeline"

function formatGlucoseUnit(unit: string): string {
  return unit === "mg_dl" ? "mg/dL" : "mmol/L"
}

export function DashboardCards() {
  const [summary, setSummary] = useState<DailySummary | null>(null)
  const [latestSleep, setLatestSleep] = useState<SleepDetail | null>(null)
  const [latestVitals, setLatestVitals] = useState<VitalsDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true
    Promise.all([
      timelineService.getDailySummary(),
      healthEventsService.getMostRecentHealthEvent("sleep"),
      healthEventsService.getMostRecentHealthEvent("vitals"),
    ])
      .then(([summaryData, sleepData, vitalsData]) => {
        if (!isMounted) return
        setSummary(summaryData)
        setLatestSleep(sleepData as unknown as SleepDetail | null)
        setLatestVitals(vitalsData as unknown as VitalsDetail | null)
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [])

  const placeholder = isLoading ? "…" : "—"

  const medicationTotal = (summary?.medications_taken ?? 0) + (summary?.medications_missed ?? 0)

  const bloodPressure =
    latestVitals?.blood_pressure_systolic != null && latestVitals?.blood_pressure_diastolic != null
      ? `${latestVitals.blood_pressure_systolic}/${latestVitals.blood_pressure_diastolic}`
      : null

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      <StatCard
        label="Glucose today"
        value={
          isLoading
            ? placeholder
            : summary?.latest_glucose
              ? `${summary.latest_glucose.value} ${formatGlucoseUnit(summary.latest_glucose.unit)}`
              : "—"
        }
        detail={
          summary?.glucose_average_mg_dl != null
            ? `avg ${summary.glucose_average_mg_dl} mg/dL today`
            : "No readings today"
        }
      />
      <StatCard
        label="Medication"
        value={isLoading ? placeholder : medicationTotal > 0 ? `${summary?.medications_taken}/${medicationTotal}` : "—"}
        detail={medicationTotal > 0 ? "doses taken today" : "None logged today"}
      />
      <StatCard
        label="Exercise today"
        value={isLoading ? placeholder : `${summary?.total_exercise_minutes ?? 0} min`}
      />
      <StatCard label="Meals logged" value={isLoading ? placeholder : (summary?.event_counts.meal ?? 0)} />
      <StatCard
        label="Sleep last night"
        value={isLoading ? placeholder : latestSleep ? `${latestSleep.hours_slept}h` : "—"}
        detail={latestSleep ? latestSleep.quality : "No sleep logged"}
      />
      <StatCard
        label="Stress today"
        value={isLoading ? placeholder : (summary?.average_stress_level ?? "—")}
        detail={summary?.average_stress_level != null ? "avg out of 10" : "None logged today"}
      />
      <StatCard
        label="Latest weight"
        value={isLoading ? placeholder : latestVitals?.weight_kg != null ? `${latestVitals.weight_kg} kg` : "—"}
      />
      <StatCard label="Latest BP" value={isLoading ? placeholder : (bloodPressure ?? "—")} detail="mmHg" />
    </div>
  )
}
