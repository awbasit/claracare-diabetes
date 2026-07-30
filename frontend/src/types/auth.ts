export type UserRole = "patient" | "clinician" | "admin"

export interface User {
  id: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}
