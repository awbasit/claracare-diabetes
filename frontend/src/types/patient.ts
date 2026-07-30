export type Sex = "male" | "female" | "other"
export type DiabetesType = "type1" | "type2" | "gestational" | "prediabetes" | "other"

export interface Patient {
  id: string
  user_id: string
  age: number | null
  sex: Sex | null
  height_cm: number | null
  weight_kg: number | null
  bmi: number | null
  occupation: string | null
  work_schedule: string | null
  created_at: string
  updated_at: string
}

export interface PatientUpdateInput {
  age?: number | null
  sex?: Sex | null
  height_cm?: number | null
  weight_kg?: number | null
  occupation?: string | null
  work_schedule?: string | null
}

export interface MedicalHistory {
  id: string
  patient_id: string
  diabetes_type: DiabetesType | null
  years_since_diagnosis: number | null
  family_history: boolean
  family_history_notes: string | null
  latest_hba1c: number | null
  latest_blood_pressure_systolic: number | null
  latest_blood_pressure_diastolic: number | null
  latest_cholesterol: number | null
  has_kidney_disease: boolean
  has_eye_disease: boolean
  has_neuropathy: boolean
  comorbidities: string[]
  created_at: string
  updated_at: string
}

export interface MedicalHistoryInput {
  diabetes_type?: DiabetesType | null
  years_since_diagnosis?: number | null
  family_history?: boolean
  family_history_notes?: string | null
  latest_hba1c?: number | null
  latest_blood_pressure_systolic?: number | null
  latest_blood_pressure_diastolic?: number | null
  latest_cholesterol?: number | null
  has_kidney_disease?: boolean
  has_eye_disease?: boolean
  has_neuropathy?: boolean
  comorbidities?: string[]
}

export interface LifestyleProfile {
  id: string
  patient_id: string
  sleep_hours_avg: number | null
  exercise_frequency: string | null
  exercise_type: string | null
  smoking_status: string | null
  alcohol_use: string | null
  stress_level_baseline: number | null
  meal_schedule_notes: string | null
  created_at: string
  updated_at: string
}

export interface LifestyleProfileInput {
  sleep_hours_avg?: number | null
  exercise_frequency?: string | null
  exercise_type?: string | null
  smoking_status?: string | null
  alcohol_use?: string | null
  stress_level_baseline?: number | null
  meal_schedule_notes?: string | null
}

export interface Medication {
  id: string
  patient_id: string
  name: string
  dosage: string | null
  frequency: string | null
  time_of_day: string | null
  purpose: string | null
  prescribed_by: string | null
  duration: string | null
  side_effects: string | null
  missed_doses_notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface MedicationInput {
  name: string
  dosage?: string | null
  frequency?: string | null
  time_of_day?: string | null
  purpose?: string | null
  prescribed_by?: string | null
  duration?: string | null
  side_effects?: string | null
  missed_doses_notes?: string | null
  is_active?: boolean
}

export type MedicationUpdateInput = Partial<MedicationInput>

export interface BaselineAssessment {
  id: string
  patient_id: string
  completed_at: string | null
  notes: string | null
  raw_answers: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface PatientProfile {
  patient: Patient
  medical_history: MedicalHistory | null
  lifestyle_profile: LifestyleProfile | null
  medications: Medication[]
}
