import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { DemographicsStep } from "@/features/onboarding/DemographicsStep"
import { LifestyleStep } from "@/features/onboarding/LifestyleStep"
import { MedicalHistoryStep } from "@/features/onboarding/MedicalHistoryStep"
import { MedicationsStep } from "@/features/onboarding/MedicationsStep"
import * as patientsService from "@/services/patientsService"
import type {
  LifestyleProfileInput,
  MedicalHistoryInput,
  Medication,
  PatientProfile,
  PatientUpdateInput,
} from "@/types/patient"

type SaveStatus = "idle" | "saving" | "success" | "error"

export function ProfilePage() {
  const [profile, setProfile] = useState<PatientProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [demographicsStatus, setDemographicsStatus] = useState<SaveStatus>("idle")
  const [medicalHistoryStatus, setMedicalHistoryStatus] = useState<SaveStatus>("idle")
  const [lifestyleStatus, setLifestyleStatus] = useState<SaveStatus>("idle")

  useEffect(() => {
    let isMounted = true
    patientsService
      .getProfile()
      .then((data) => {
        if (isMounted) setProfile(data)
      })
      .catch(() => {
        if (isMounted) setLoadError("Couldn't load your profile.")
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [])

  async function handleSaveDemographics(value: PatientUpdateInput) {
    setDemographicsStatus("saving")
    try {
      const patient = await patientsService.updateProfile(value)
      setProfile((prev) => (prev ? { ...prev, patient } : prev))
      setDemographicsStatus("success")
    } catch {
      setDemographicsStatus("error")
    }
  }

  async function handleSaveMedicalHistory(value: MedicalHistoryInput) {
    setMedicalHistoryStatus("saving")
    try {
      const medicalHistory = await patientsService.upsertMedicalHistory(value)
      setProfile((prev) => (prev ? { ...prev, medical_history: medicalHistory } : prev))
      setMedicalHistoryStatus("success")
    } catch {
      setMedicalHistoryStatus("error")
    }
  }

  async function handleSaveLifestyle(value: LifestyleProfileInput) {
    setLifestyleStatus("saving")
    try {
      const lifestyleProfile = await patientsService.upsertLifestyleProfile(value)
      setProfile((prev) => (prev ? { ...prev, lifestyle_profile: lifestyleProfile } : prev))
      setLifestyleStatus("success")
    } catch {
      setLifestyleStatus("error")
    }
  }

  function handleMedicationsChange(medications: Medication[]) {
    setProfile((prev) => (prev ? { ...prev, medications } : prev))
  }

  if (isLoading) {
    return (
      <div className="flex min-h-svh items-center justify-center text-sm text-muted-foreground">Loading…</div>
    )
  }

  if (loadError || !profile) {
    return (
      <div className="flex min-h-svh items-center justify-center text-sm text-destructive">
        {loadError ?? "Profile unavailable."}
      </div>
    )
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-8 px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Your profile</h1>
        <Button variant="outline" asChild>
          <Link to="/dashboard">Back to dashboard</Link>
        </Button>
      </div>

      <section className="flex flex-col gap-2">
        <SectionHeader title="Demographics" status={demographicsStatus} />
        <DemographicsStep
          initialValue={profile.patient}
          isSaving={demographicsStatus === "saving"}
          submitLabel="Save"
          onSubmit={handleSaveDemographics}
        />
      </section>

      <section className="flex flex-col gap-2">
        <SectionHeader title="Medical history" status={medicalHistoryStatus} />
        <MedicalHistoryStep
          initialValue={profile.medical_history ?? {}}
          isSaving={medicalHistoryStatus === "saving"}
          submitLabel="Save"
          onSubmit={handleSaveMedicalHistory}
        />
      </section>

      <section className="flex flex-col gap-2">
        <SectionHeader title="Medications" />
        <MedicationsStep initialMedications={profile.medications} onChange={handleMedicationsChange} />
      </section>

      <section className="flex flex-col gap-2">
        <SectionHeader title="Lifestyle" status={lifestyleStatus} />
        <LifestyleStep
          initialValue={profile.lifestyle_profile ?? {}}
          isSaving={lifestyleStatus === "saving"}
          submitLabel="Save"
          onSubmit={handleSaveLifestyle}
        />
      </section>
    </div>
  )
}

function SectionHeader({ title, status }: { title: string; status?: SaveStatus }) {
  return (
    <div className="flex items-center justify-between">
      <h2 className="text-lg font-medium">{title}</h2>
      {status === "success" && <span className="text-sm text-muted-foreground">Saved</span>}
      {status === "error" && <span className="text-sm text-destructive">Couldn&apos;t save</span>}
    </div>
  )
}
