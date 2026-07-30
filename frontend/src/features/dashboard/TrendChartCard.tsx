import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { TrendPeriod } from "@/types/timeline"

export interface TrendSeries {
  dataKey: string
  name: string
  color: string
  kind: "line" | "bar"
  unit?: string
  formatValue?: (value: number) => string
}

interface ChartPoint {
  date: string
  dateLabel: string
  [key: string]: string | number | null
}

function formatAxisDate(dateStr: string, period: TrendPeriod): string {
  const date = new Date(`${dateStr}T00:00:00Z`)
  if (period === "week") {
    return date.toLocaleDateString(undefined, { weekday: "short", timeZone: "UTC" })
  }
  return date.toLocaleDateString(undefined, { day: "numeric", month: "short", timeZone: "UTC" })
}

function ChartTooltip({
  active,
  payload,
  series,
}: {
  active?: boolean
  payload?: { payload: ChartPoint }[]
  series: TrendSeries[]
}) {
  if (!active || !payload || payload.length === 0) return null
  const point = payload[0].payload
  return (
    <div className="rounded-md border bg-popover px-3 py-2 text-xs shadow-sm">
      <p className="font-medium text-popover-foreground">{point.date}</p>
      {series.map((s) => {
        const raw = point[s.dataKey]
        const value = typeof raw === "number" ? raw : null
        return (
          <p key={s.dataKey} className="text-muted-foreground">
            {s.name}: {value === null ? "—" : s.formatValue ? s.formatValue(value) : value}
            {value !== null && s.unit ? ` ${s.unit}` : ""}
          </p>
        )
      })}
    </div>
  )
}

interface TrendChartCardProps<T extends { date: string }> {
  title: string
  period: TrendPeriod
  points: T[]
  series: TrendSeries[]
  hasData: (points: T[]) => boolean
  emptyMessage: string
  footnote?: string
}

export function TrendChartCard<T extends { date: string }>({
  title,
  period,
  points,
  series,
  hasData,
  emptyMessage,
  footnote,
}: TrendChartCardProps<T>) {
  const chartData: ChartPoint[] = points.map((point) => ({
    ...point,
    dateLabel: formatAxisDate(point.date, period),
  })) as unknown as ChartPoint[]

  const hasAnyData = hasData(points)
  const showLegend = series.length > 1

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {!hasAnyData ? (
          <p className="text-sm text-muted-foreground">{emptyMessage}</p>
        ) : (
          <>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <CartesianGrid vertical={false} stroke="var(--border)" />
                  <XAxis
                    dataKey="dateLabel"
                    tickLine={false}
                    axisLine={{ stroke: "var(--border)" }}
                    tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                    interval={period === "month" ? 4 : 0}
                  />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                    width={32}
                  />
                  <Tooltip content={<ChartTooltip series={series} />} />
                  {showLegend && (
                    <Legend
                      verticalAlign="top"
                      height={24}
                      wrapperStyle={{ fontSize: 11, color: "var(--muted-foreground)" }}
                    />
                  )}
                  {series.map((s) =>
                    s.kind === "bar" ? (
                      <Bar
                        key={s.dataKey}
                        dataKey={s.dataKey}
                        name={s.name}
                        fill={s.color}
                        isAnimationActive={false}
                        radius={[2, 2, 0, 0]}
                      />
                    ) : (
                      <Line
                        key={s.dataKey}
                        dataKey={s.dataKey}
                        name={s.name}
                        stroke={s.color}
                        strokeWidth={2}
                        dot={{ r: 2.5, fill: s.color, strokeWidth: 0 }}
                        isAnimationActive={false}
                        connectNulls={false}
                      />
                    )
                  )}
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            {footnote && <p className="mt-2 text-xs text-muted-foreground">{footnote}</p>}
          </>
        )}
      </CardContent>
    </Card>
  )
}
