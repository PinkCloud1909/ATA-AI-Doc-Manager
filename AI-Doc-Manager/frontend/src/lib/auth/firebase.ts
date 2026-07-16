/**
 * lib/auth/firebase.ts
 *
 * Firebase Auth has been REMOVED from this project.
 * Backend uses JWT username/password authentication.
 *
 * This stub exists to prevent import errors from any remaining references.
 * New code should use @/lib/api/auth.ts (authApi) exclusively.
 */

// Stub exports — do NOT use in new code
export const firebaseAuth = null as unknown

/** @deprecated Use authApi.login() from @/lib/api/auth.ts */
export async function getCurrentIdToken(): Promise<string | null> {
  console.warn("Firebase auth is disabled. Use JWT from authApi.login().")
  return null
}

/** @deprecated */
export async function signInAndGetToken(): Promise<string> {
  throw new Error("Firebase auth is disabled. Use authApi.login() from @/lib/api/auth.ts")
}

/** @deprecated */
export async function signOut(): Promise<void> {
  // no-op
}

/** @deprecated */
export function onTokenRefresh(): () => void {
  return () => {} // no-op
}
