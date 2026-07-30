import { Area, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { DailyGlucoseTrendPoint, TrendPeriod } from "@/types/timeline"

interface ChartPoint {
  date: string
  dateLabel: string
  average: number | null
  minimum: number | null
  maximum: number | null
  count: number
  range?: [number, number]
}

function formatAxisDate(dateStr: string, period: TrendPeriod): string {
  const date = new Date(`${dateStr}T00:00:00Z`)
  if (period === "week") {
    return date.toLocaleDateString(undefined, { weekday: "short", timeZone: "UTC" })
  }
  return date.toLocaleDateString(undefined, { day: "numeric", month: "short", timeZone: "UTC" })
}

function buildChartData(points: DailyGlucoseTrendPoint[], period: TrendPeriod): ChartPoint[] {
  return points.map((point) => ({
    date: point.date,
    dateLabel: formatAxisDate(point.date, period),
    average: point.average,
    minimum: point.minimum,
    maximum: point.maximum,
    count: point.count,
    range: point.minimum !== null && point.maximum !== null ? [point.minimum, point.maximum] : undefined,
  }))
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: { payload: ChartPoint }[] }) {
  if (!active || !payload || payload.length === 0) return null
  const point = payload[0].payload
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-xs shadow-sm">
      <p className="font-medium text-popover-foreground">{point.date}</p>
      {point.count === 0 ? (
        <p className="text-muted-foreground">No readings</p>
      ) : (
        <>
          <p className="text-muted-foreground">Average {point.average} mg/dL</p>
          <p className="text-muted-foreground">
            Range {point.minimum}&ndash;{point.maximum} mg/dL
          </p>
          <p className="text-muted-foreground">
            {point.count} reading{point.count === 1 ? "" : "s"}
          </p>
        </>
      )}
    </div>
  )
}

interface GlucoseTrendChartProps {
  period: TrendPeriod
  points: DailyGlucoseTrendPoint[]
}

export function GlucoseTrendChart({ period, points }: GlucoseTrendChartProps) {
  const chartData = buildChartData(points, period)
  const hasAnyReadings = chartData.some((point) => point.count > 0)

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Glucose trend</CardTitle>
      </CardHeader>
      <CardContent>
        {!hasAnyReadings ? (
          <p className="text-sm text-muted-foreground">No glucose readings in this period yet.</p>
        ) : (
          <>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <CartesianGrid vertical={false} stroke="var(--border)" />
                  <XAxis
                    dataKey="dateLabel"
                    tickLine={false}
                    axisLine={{ stroke: "var(--border)" }}
                    tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                    interval={period === "month" ? 4 : 0}
                  />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                    width={40}
                  />
                  <Tooltip content={<ChartTooltip />} />
                  <Area
                    dataKey="range"
                    stroke="none"
                    fill="var(--chart-glucose-band)"
                    fillOpacity={0.35}
                    isAnimationActive={false}
                    connectNulls={false}
                  />
                  <Line
                    dataKey="average"
                    stroke="var(--chart-glucose-line)"
                    strokeWidth={2}
                    dot={{ r: 3, fill: "var(--chart-glucose-line)", strokeWidth: 0 }}
                    isAnimationActive={false}
                    connectNulls={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              Shaded band shows each day&apos;s min&ndash;max range; the line shows the daily average.
            </p>
          </>
        )}
      </CardContent>
    </Card>
  )
}
