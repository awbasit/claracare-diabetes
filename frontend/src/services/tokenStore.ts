// Token storage strategy (Sprint 1):
//
// - Access token lives ONLY in memory (this module-level variable). It's never
//   persisted, so it disappears on tab close/reload — the tradeoff is that
//   every fresh page load has to silently re-authenticate via the refresh
//   token before the user is usable again (see AuthContext's bootstrap effect).
//   In exchange, an XSS payload can't read a long-lived access token out of
//   storage; at worst it can use the one already loaded in memory.
// - Refresh token is persisted to localStorage so a reload doesn't force a
//   full re-login. The backend (Prompt 3) issues the refresh token as a JSON
//   response field, not a Set-Cookie header, so an httpOnly cookie isn't an
//   option without backend changes. localStorage is readable by any script
//   on the page, so this is weaker against XSS than httpOnly cookies would
//   be — moving refresh-token issuance to an httpOnly, SameSite cookie (plus
//   CSRF protection) is the recommended hardening before this ships to real
//   patients.

let accessToken: string | null = null

export function getAccessToken(): string | null {
  return accessToken
}

export function setAccessToken(token: string | null): void {
  accessToken = token
}

const REFRESH_TOKEN_KEY = "diawise.refresh_token"

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setRefreshToken(token: string | null): void {
  if (token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token)
  } else {
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }
}
