import { useState } from "react"
import { useNavigate } from "react-router-dom"

import { DemographicsStep } from "@/features/onboarding/DemographicsStep"
import { LifestyleStep } from "@/features/onboarding/LifestyleStep"
import { MedicalHistoryStep } from "@/features/onboarding/MedicalHistoryStep"
import { MedicationsStep } from "@/features/onboarding/MedicationsStep"
import { ReviewStep } from "@/features/onboarding/ReviewStep"
import * as patientsService from "@/services/patientsService"
import type { LifestyleProfileInput, MedicalHistoryInput, Medication, PatientUpdateInput } from "@/types/patient"

const STEP_LABELS = ["Demographics", "Medical history", "Medications", "Lifestyle", "Review"] as const

export interface OnboardingData {
  demographics: PatientUpdateInput
  medicalHistory: MedicalHistoryInput
  medications: Medication[]
  lifestyle: LifestyleProfileInput
}

const initialData: OnboardingData = {
  demographics: {},
  medicalHistory: {},
  medications: [],
  lifestyle: {},
}

export function OnboardingWizard() {
  const navigate = useNavigate()
  const [stepIndex, setStepIndex] = useState(0)
  const [data, setData] = useState<OnboardingData>(initialData)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  function goBack() {
    setError(null)
    setStepIndex((index) => Math.max(0, index - 1))
  }

  async function saveDemographics(input: PatientUpdateInput) {
    setIsSaving(true)
    setError(null)
    try {
      await patientsService.updateProfile(input)
      setData((prev) => ({ ...prev, demographics: input }))
      setStepIndex((index) => index + 1)
    } catch {
      setError("Couldn't save your details. Please try again.")
    } finally {
      setIsSaving(false)
    }
  }

  async function saveMedicalHistory(input: MedicalHistoryInput) {
    setIsSaving(true)
    setError(null)
    try {
      await patientsService.upsertMedicalHistory(input)
      setData((prev) => ({ ...prev, medicalHistory: input }))
      setStepIndex((index) => index + 1)
    } catch {
      setError("Couldn't save your medical history. Please try again.")
    } finally {
      setIsSaving(false)
    }
  }

  function proceedFromMedications(medications: Medication[]) {
    setData((prev) => ({ ...prev, medications }))
    setStepIndex((index) => index + 1)
  }

  async function saveLifestyle(input: LifestyleProfileInput) {
    setIsSaving(true)
    setError(null)
    try {
      await patientsService.upsertLifestyleProfile(input)
      setData((prev) => ({ ...prev, lifestyle: input }))
      setStepIndex((index) => index + 1)
    } catch {
      setError("Couldn't save your lifestyle profile. Please try again.")
    } finally {
      setIsSaving(false)
    }
  }

  async function submitBaseline(notes: string) {
    setIsSaving(true)
    setError(null)
    try {
      await patientsService.submitBaselineAssessment(notes || null, {
        demographics: data.demographics,
        medical_history: data.medicalHistory,
        medications: data.medications.map((medication) => medication.name),
        lifestyle: data.lifestyle,
      })
      navigate("/dashboard", { replace: true })
    } catch {
      setError("Couldn't submit your baseline assessment. Please try again.")
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-svh max-w-2xl flex-col justify-center gap-6 px-4 py-10">
      <div>
        <p className="text-sm text-muted-foreground">
          Step {stepIndex + 1} of {STEP_LABELS.length}
        </p>
        <div className="mt-2 flex gap-1">
          {STEP_LABELS.map((label, index) => (
            <div
              key={label}
              className={`h-1 flex-1 rounded-full ${index <= stepIndex ? "bg-primary" : "bg-muted"}`}
            />
          ))}
        </div>
        <h1 className="mt-3 text-xl font-semibold">{STEP_LABELS[stepIndex]}</h1>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      {stepIndex === 0 && (
        <DemographicsStep initialValue={data.demographics} isSaving={isSaving} onSubmit={saveDemographics} />
      )}
      {stepIndex === 1 && (
        <MedicalHistoryStep
          initialValue={data.medicalHistory}
          isSaving={isSaving}
          onBack={goBack}
          onSubmit={saveMedicalHistory}
        />
      )}
      {stepIndex === 2 && (
        <MedicationsStep initialMedications={data.medications} onBack={goBack} onNext={proceedFromMedications} />
      )}
      {stepIndex === 3 && (
        <LifestyleStep initialValue={data.lifestyle} isSaving={isSaving} onBack={goBack} onSubmit={saveLifestyle} />
      )}
      {stepIndex === 4 && (
        <ReviewStep data={data} isSaving={isSaving} onBack={goBack} onSubmit={submitBaseline} />
      )}
    </div>
  )
}
