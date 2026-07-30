import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import { GlucoseTrendChart } from "@/features/dashboard/GlucoseTrendChart"
import { TrendChartCard } from "@/features/dashboard/TrendChartCard"
import * as analyticsService from "@/services/analyticsService"
import type {
  DailyExerciseTrendPoint,
  DailyMealTrendPoint,
  DailyMedicationTrendPoint,
  DailySleepTrendPoint,
  DailyStressTrendPoint,
  DailySymptomTrendPoint,
  DailyVitalsTrendPoint,
  TrendPeriod,
  TrendsResponse,
} from "@/types/timeline"

export function TrendsSection() {
  const [period, setPeriod] = useState<TrendPeriod>("week")
  const [data, setData] = useState<TrendsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    setIsLoading(true)
    setError(null)
    analyticsService
      .getTrends(period)
      .then((response) => {
        if (isMounted) setData(response)
      })
      .catch(() => {
        if (isMounted) setError("Couldn't load trends.")
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [period])

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Trends</h2>
        <div className="flex gap-1">
          <Button
            type="button"
            variant={period === "week" ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setPeriod("week")}
          >
            Week
          </Button>
          <Button
            type="button"
            variant={period === "month" ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setPeriod("month")}
          >
            Month
          </Button>
        </div>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}

      {!isLoading && !error && data && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <GlucoseTrendChart period={period} points={data.glucose} />

          <TrendChartCard<DailyMealTrendPoint>
            title="Meals logged"
            period={period}
            points={data.meals}
            hasData={(points) => points.some((p) => p.count > 0)}
            emptyMessage="No meals logged in this period yet."
            footnote="Bars show meals logged per day."
            series={[{ dataKey: "count", name: "Meals", color: "var(--chart-meals)", kind: "bar" }]}
          />

          <TrendChartCard<DailyMedicationTrendPoint>
            title="Medication adherence"
            period={period}
            points={data.medication}
            hasData={(points) => points.some((p) => p.adherence_pct !== null)}
            emptyMessage="No medication logged in this period yet."
            footnote="Line shows the share of scheduled doses taken each day."
            series={[
              {
                dataKey: "adherence_pct",
                name: "Adherence",
                color: "var(--chart-medication)",
                kind: "line",
                unit: "%",
              },
            ]}
          />

          <TrendChartCard<DailyExerciseTrendPoint>
            title="Exercise minutes"
            period={period}
            points={data.exercise}
            hasData={(points) => points.some((p) => p.total_minutes > 0)}
            emptyMessage="No exercise logged in this period yet."
            footnote="Bars show total exercise minutes per day."
            series={[
              {
                dataKey: "total_minutes",
                name: "Minutes",
                color: "var(--chart-exercise)",
                kind: "bar",
                unit: "min",
              },
            ]}
          />

          <TrendChartCard<DailySleepTrendPoint>
            title="Sleep"
            period={period}
            points={data.sleep}
            hasData={(points) => points.some((p) => p.average_hours !== null)}
            emptyMessage="No sleep logged in this period yet."
            footnote="Line shows average hours slept per night."
            series={[
              {
                dataKey: "average_hours",
                name: "Hours slept",
                color: "var(--chart-sleep)",
                kind: "line",
                unit: "h",
              },
            ]}
          />

          <TrendChartCard<DailyStressTrendPoint>
            title="Stress & energy"
            period={period}
            points={data.stress}
            hasData={(points) =>
              points.some((p) => p.average_stress_level !== null || p.average_energy_level !== null)
            }
            emptyMessage="No stress logged in this period yet."
            footnote="Both scored 1–10."
            series={[
              {
                dataKey: "average_stress_level",
                name: "Stress",
                color: "var(--chart-stress-level)",
                kind: "line",
              },
              {
                dataKey: "average_energy_level",
                name: "Energy",
                color: "var(--chart-stress-energy)",
                kind: "line",
              },
            ]}
          />

          <TrendChartCard<DailySymptomTrendPoint>
            title="Symptoms logged"
            period={period}
            points={data.symptoms}
            hasData={(points) => points.some((p) => p.count > 0)}
            emptyMessage="No symptoms logged in this period yet."
            footnote="Bars show symptoms logged per day."
            series={[{ dataKey: "count", name: "Symptoms", color: "var(--chart-symptoms)", kind: "bar" }]}
          />

          <TrendChartCard<DailyVitalsTrendPoint>
            title="Weight"
            period={period}
            points={data.vitals}
            hasData={(points) => points.some((p) => p.latest_weight_kg !== null)}
            emptyMessage="No weight logged in this period yet."
            footnote="Line shows the latest weight reading logged each day."
            series={[
              {
                dataKey: "latest_weight_kg",
                name: "Weight",
                color: "var(--chart-vitals-weight)",
                kind: "line",
                unit: "kg",
              },
            ]}
          />

          <TrendChartCard<DailyVitalsTrendPoint>
            title="Blood pressure"
            period={period}
            points={data.vitals}
            hasData={(points) =>
              points.some(
                (p) => p.latest_blood_pressure_systolic !== null || p.latest_blood_pressure_diastolic !== null
              )
            }
            emptyMessage="No blood pressure logged in this period yet."
            footnote="Latest systolic/diastolic reading logged each day, in mmHg."
            series={[
              {
                dataKey: "latest_blood_pressure_systolic",
                name: "Systolic",
                color: "var(--chart-vitals-systolic)",
                kind: "line",
              },
              {
                dataKey: "latest_blood_pressure_diastolic",
                name: "Diastolic",
                color: "var(--chart-vitals-diastolic)",
                kind: "line",
              },
            ]}
          />
        </div>
      )}
    </div>
  )
}
