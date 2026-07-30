import { api } from "@/services/api"
import type { GlucoseUnit } from "@/types/healthEvents"
import type { GlucoseTrendResponse, TrendPeriod } from "@/types/timeline"

export async function getGlucoseTrend(
  period: TrendPeriod,
  unit: GlucoseUnit = "mg_dl"
): Promise<GlucoseTrendResponse> {
  const response = await api.get<GlucoseTrendResponse>("/api/patients/me/analytics/glucose-trend", {
    params: { period, unit },
  })
  return response.data
}
