import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/features/auth/AuthContext"
import * as patientsService from "@/services/patientsService"
import type { DiabetesType, PatientProfile } from "@/types/patient"

const DIABETES_TYPE_LABELS: Record<DiabetesType, string> = {
  type1: "Type 1",
  type2: "Type 2",
  gestational: "Gestational",
  prediabetes: "Prediabetes",
  other: "Other",
}

export function DashboardPage() {
  const { user, logout } = useAuth()
  const [profile, setProfile] = useState<PatientProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true
    patientsService
      .getProfile()
      .then((data) => {
        if (isMounted) setProfile(data)
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => {
      isMounted = false
    }
  }, [])

  const activeMedicationCount = profile?.medications.filter((medication) => medication.is_active).length ?? 0
  const hasCompletedProfile = Boolean(profile?.medical_history)
  const diabetesType = profile?.medical_history?.diabetes_type ?? null

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-10">
      <div className="flex items-center justify-between">
        <div>
          {/* The data model (Prompt 2) has no patient name field, only email — using it as the identifier. */}
          <p className="text-sm text-muted-foreground">Signed in as</p>
          <h1 className="text-xl font-semibold">{user?.email}</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to="/profile">Edit profile</Link>
          </Button>
          <Button variant="ghost" onClick={logout}>
            Log out
          </Button>
        </div>
      </div>

      {!isLoading && !hasCompletedProfile && (
        <Card className="border-dashed">
          <CardHeader>
            <CardTitle className="text-base">Finish setting up your profile</CardTitle>
            <CardDescription>Complete onboarding so your care team has your full picture.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link to="/onboarding">Continue onboarding</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="BMI" value={isLoading ? "…" : (profile?.patient.bmi?.toString() ?? "—")} />
        <StatCard
          label="Diabetes type"
          value={isLoading ? "…" : diabetesType ? DIABETES_TYPE_LABELS[diabetesType] : "—"}
        />
        <StatCard label="Active medications" value={isLoading ? "…" : activeMedicationCount.toString()} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Health timeline</CardTitle>
          <CardDescription>No health timeline yet — this will show up in a future update.</CardDescription>
        </CardHeader>
      </Card>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-2xl">{value}</CardTitle>
      </CardHeader>
    </Card>
  )
}
