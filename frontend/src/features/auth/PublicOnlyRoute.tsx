import { useEffect, useState } from "react"
import { Navigate, Outlet } from "react-router-dom"

import { useAuth } from "@/features/auth/AuthContext"

// This only redirects based on the session state found when the route first
// resolves (i.e. someone loading /login or /register while already holding a
// valid session) — it deliberately does NOT react to `isAuthenticated`
// flipping true afterwards. Login/RegisterPage already navigate() explicitly
// on success (to different destinations — /dashboard vs /onboarding); if this
// component also redirected reactively on that same state change, the two
// would race, and this one always targets /dashboard regardless of which
// page triggered it.
export function PublicOnlyRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const [wasAuthenticatedOnLoad, setWasAuthenticatedOnLoad] = useState<boolean | null>(null)

  useEffect(() => {
    if (!isLoading && wasAuthenticatedOnLoad === null) {
      setWasAuthenticatedOnLoad(isAuthenticated)
    }
  }, [isLoading, isAuthenticated, wasAuthenticatedOnLoad])

  if (isLoading || wasAuthenticatedOnLoad === null) {
    return (
      <div className="flex min-h-svh items-center justify-center text-sm text-muted-foreground">
        Loading…
      </div>
    )
  }

  if (wasAuthenticatedOnLoad) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
