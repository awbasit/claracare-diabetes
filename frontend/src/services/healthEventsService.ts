import { api } from "@/services/api"
import type { EventCreateInput, EventType, EventUpdateInput } from "@/types/healthEvents"

// Every event type's CRUD lives at its own endpoint from Prompts 1-2 — this
// is just the path lookup; health_event_service on the backend is what
// actually enforces ownership and does the transactional create/update.
const EVENT_TYPE_PATHS: Record<EventType, string> = {
  glucose: "/api/patients/me/glucose",
  meal: "/api/patients/me/meals",
  medication: "/api/patients/me/medication-log",
  exercise: "/api/patients/me/exercise",
  sleep: "/api/patients/me/sleep",
  stress: "/api/patients/me/stress",
  symptom: "/api/patients/me/symptoms",
  vitals: "/api/patients/me/vitals",
}

// The per-type GET/{id} response (Prompts 1-2) is a flat object combining
// envelope fields (event_timestamp, notes, ...) and detail fields (value,
// unit, ... — whatever's specific to that type) at the same level — exactly
// the shape EventForm's initialValues expects, so no reshaping needed here.
export async function getHealthEvent(eventType: EventType, id: string): Promise<Record<string, unknown>> {
  const response = await api.get<Record<string, unknown>>(`${EVENT_TYPE_PATHS[eventType]}/${id}`)
  return response.data
}

export async function createHealthEvent(eventType: EventType, input: EventCreateInput): Promise<void> {
  await api.post(EVENT_TYPE_PATHS[eventType], input)
}

export async function updateHealthEvent(
  eventType: EventType,
  id: string,
  input: EventUpdateInput
): Promise<void> {
  await api.put(`${EVENT_TYPE_PATHS[eventType]}/${id}`, input)
}

export async function deleteHealthEvent(eventType: EventType, id: string): Promise<void> {
  await api.delete(`${EVENT_TYPE_PATHS[eventType]}/${id}`)
}

// For "latest X" dashboard cards (e.g. latest weight/BP, sleep last night)
// that aren't scoped to "today" the way /timeline/summary is — a patient
// might not log vitals daily, so this looks at the most recent entry ever,
// not just today's.
export async function getMostRecentHealthEvent(
  eventType: EventType
): Promise<Record<string, unknown> | null> {
  const response = await api.get<Record<string, unknown>[]>(EVENT_TYPE_PATHS[eventType], {
    params: { limit: 1 },
  })
  return response.data[0] ?? null
}
