import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/features/auth/AuthContext"
import { DashboardCards } from "@/features/dashboard/DashboardCards"
import { TrendsSection } from "@/features/dashboard/TrendsSection"
import * as patientsService from "@/services/patientsService"
import type { PatientProfile } from "@/types/patient"

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

  const hasCompletedProfile = Boolean(profile?.medical_history)

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-10">
      <div className="flex items-center justify-between">
        <div>
          {/* The data model (Prompt 2) has no patient name field, only email — using it as the identifier. */}
          <p className="text-sm text-muted-foreground">Signed in as</p>
          <h1 className="text-xl font-semibold">{user?.email}</h1>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild>
            <Link to="/events/new">Log event</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/timeline">Timeline</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/history">History</Link>
          </Button>
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

      <DashboardCards />

      <TrendsSection />
    </div>
  )
}
