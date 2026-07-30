import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react"

import { fetchCurrentUser, loginUser, registerUser } from "@/services/authService"
import { api } from "@/services/api"
import { getRefreshToken, setAccessToken, setRefreshToken } from "@/services/tokenStore"
import type { User } from "@/types/auth"

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  // True until the initial silent-refresh attempt (below) resolves, so route
  // guards don't redirect to /login before we've had a chance to restore the
  // session from the stored refresh token.
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    async function bootstrap() {
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        if (isMounted) setIsLoading(false)
        return
      }
      try {
        const response = await api.post<{ access_token: string }>("/api/auth/refresh", {
          refresh_token: refreshToken,
        })
        setAccessToken(response.data.access_token)
        const currentUser = await fetchCurrentUser()
        if (isMounted) setUser(currentUser)
      } catch {
        setAccessToken(null)
        setRefreshToken(null)
      } finally {
        if (isMounted) setIsLoading(false)
      }
    }

    bootstrap()
    return () => {
      isMounted = false
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    await loginUser(email, password)
    const currentUser = await fetchCurrentUser()
    setUser(currentUser)
  }, [])

  const register = useCallback(async (email: string, password: string) => {
    const newUser = await registerUser(email, password)
    setUser(newUser)
  }, [])

  const logout = useCallback(() => {
    setAccessToken(null)
    setRefreshToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, isAuthenticated: user !== null, isLoading, login, register, logout }),
    [user, isLoading, login, register, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
