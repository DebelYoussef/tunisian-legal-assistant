// JWT token management with localStorage

const TOKEN_KEY = 'auth_token'

/**
 * Save JWT access token to localStorage
 */
export function saveTokens(accessToken: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, accessToken)
  } catch (error) {
    console.error('[v0] Failed to save token:', error)
  }
}

/**
 * Save user data to localStorage (optional, not provided by backend)
 */
export function saveUser(): void {
  // User data is fetched separately via /auth/me endpoint if needed
}

/**
 * Get JWT access token from localStorage
 */
export function getAccessToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch (error) {
    console.error('[v0] Failed to get token:', error)
    return null
  }
}

/**
 * Clear all authentication data
 */
export function clearAuth(): void {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch (error) {
    console.error('[v0] Failed to clear auth:', error)
  }
}

/**
 * Check if user is authenticated (has a valid token)
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null
}
