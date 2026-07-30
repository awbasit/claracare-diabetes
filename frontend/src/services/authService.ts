import { api } from "@/services/api"
import { setAccessToken, setRefreshToken } from "@/services/tokenStore"
import type { TokenPair, User } from "@/types/auth"

interface RegisterResponse {
  user: User
  tokens: TokenPair
}

export async function registerUser(email: string, password: string): Promise<User> {
  const response = await api.post<RegisterResponse>("/api/auth/register", { email, password })
  const { user, tokens } = response.data
  setAccessToken(tokens.access_token)
  setRefreshToken(tokens.refresh_token)
  return user
}

export async function loginUser(email: string, password: string): Promise<void> {
  const response = await api.post<TokenPair>("/api/auth/login", { email, password })
  setAccessToken(response.data.access_token)
  setRefreshToken(response.data.refresh_token)
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await api.get<User>("/api/auth/me")
  return response.data
}
