import axios, { type InternalAxiosRequestConfig } from "axios"

import { getAccessToken, getRefreshToken, setAccessToken, setRefreshToken } from "@/services/tokenStore"

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

export const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
})

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`)
  }
  return config
})

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retried?: boolean
}

// A silent-refresh can be triggered by several requests failing with 401 at
// once; share one in-flight refresh call so they all wait on the same result
// instead of each firing their own POST /api/auth/refresh.
let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return null

  try {
    // Plain axios, not the `api` instance — going through `api` here would
    // re-enter this same response interceptor on failure.
    const response = await axios.post<{ access_token: string }>(`${baseURL}/api/auth/refresh`, {
      refresh_token: refreshToken,
    })
    setAccessToken(response.data.access_token)
    return response.data.access_token
  } catch {
    setAccessToken(null)
    setRefreshToken(null)
    return null
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined

    if (error.response?.status !== 401 || !originalRequest || originalRequest._retried) {
      return Promise.reject(error)
    }

    if (!getRefreshToken()) {
      return Promise.reject(error)
    }

    originalRequest._retried = true
    refreshPromise ??= refreshAccessToken().finally(() => {
      refreshPromise = null
    })

    const newAccessToken = await refreshPromise
    if (!newAccessToken) {
      window.location.assign("/login")
      return Promise.reject(error)
    }

    originalRequest.headers.set("Authorization", `Bearer ${newAccessToken}`)
    return api(originalRequest)
  }
)
