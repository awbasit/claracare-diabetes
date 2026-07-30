import { api } from "@/services/api"
import type {
  BaselineAssessment,
  LifestyleProfile,
  LifestyleProfileInput,
  MedicalHistory,
  MedicalHistoryInput,
  Medication,
  MedicationInput,
  MedicationUpdateInput,
  Patient,
  PatientProfile,
  PatientUpdateInput,
} from "@/types/patient"

export async function getProfile(): Promise<PatientProfile> {
  const response = await api.get<PatientProfile>("/api/patients/me/profile")
  return response.data
}

export async function updateProfile(input: PatientUpdateInput): Promise<Patient> {
  const response = await api.put<Patient>("/api/patients/me/profile", input)
  return response.data
}

export async function upsertMedicalHistory(input: MedicalHistoryInput): Promise<MedicalHistory> {
  const response = await api.put<MedicalHistory>("/api/patients/me/medical-history", input)
  return response.data
}

export async function upsertLifestyleProfile(input: LifestyleProfileInput): Promise<LifestyleProfile> {
  const response = await api.put<LifestyleProfile>("/api/patients/me/lifestyle", input)
  return response.data
}

export async function listMedications(): Promise<Medication[]> {
  const response = await api.get<Medication[]>("/api/patients/me/medications")
  return response.data
}

export async function createMedication(input: MedicationInput): Promise<Medication> {
  const response = await api.post<Medication>("/api/patients/me/medications", input)
  return response.data
}

export async function updateMedication(id: string, input: MedicationUpdateInput): Promise<Medication> {
  const response = await api.put<Medication>(`/api/patients/me/medications/${id}`, input)
  return response.data
}

export async function deleteMedication(id: string): Promise<void> {
  await api.delete(`/api/patients/me/medications/${id}`)
}

export async function submitBaselineAssessment(
  notes: string | null,
  rawAnswers: Record<string, unknown>
): Promise<BaselineAssessment> {
  const response = await api.post<BaselineAssessment>("/api/patients/me/baseline-assessment", {
    notes,
    raw_answers: rawAnswers,
  })
  return response.data
}
