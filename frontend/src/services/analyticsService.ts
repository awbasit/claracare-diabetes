import { api } from "@/services/api"
import type { GlucoseUnit } from "@/types/healthEvents"
import type { TrendPeriod, TrendsResponse } from "@/types/timeline"

export async function getTrends(
  period: TrendPeriod,
  glucoseUnit: GlucoseUnit = "mg_dl"
): Promise<TrendsResponse> {
  const response = await api.get<TrendsResponse>("/api/patients/me/analytics/trends", {
    params: { period, glucose_unit: glucoseUnit },
  })
  return response.data
}
