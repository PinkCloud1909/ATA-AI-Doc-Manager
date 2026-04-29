/**
 * lib/auth/firebase.ts
 *
 * Khởi tạo Firebase App và export các services cần thiết.
 * Firebase được dùng để:
 *  1. Đăng nhập bằng Email/Password (hoặc Google SSO nếu cần)
 *  2. Lấy ID Token → gửi lên FastAPI để verify qua Google IAM
 *  3. Auto-refresh ID Token (Firebase tự handle, hết hạn sau 1 giờ)
 */

import { initializeApp, getApps, getApp } from "firebase/app"
import {
  getAuth,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onIdTokenChanged,
  type User,
} from "firebase/auth"

const firebaseConfig = {
  apiKey:            process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain:        process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  projectId:         process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
  storageBucket:     process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET!,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID!,
  appId:             process.env.NEXT_PUBLIC_FIREBASE_APP_ID!,
}

// Singleton pattern — tránh khởi tạo nhiều lần khi Next.js hot-reload
const firebaseApp = getApps().length ? getApp() : initializeApp(firebaseConfig)
export const firebaseAuth = getAuth(firebaseApp)

// ── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Đăng nhập và trả về Firebase ID Token.
 * Backend sẽ verify token này qua google.oauth2.id_token.verify_firebase_token()
 */
export async function signInAndGetToken(
  email: string,
  password: string,
): Promise<string> {
  const credential = await signInWithEmailAndPassword(firebaseAuth, email, password)
  return credential.user.getIdToken()
}

/**
 * Lấy ID Token của user hiện tại (auto-refresh nếu sắp hết hạn).
 * Dùng trong Axios interceptor để luôn gửi token mới nhất.
 */
export async function getCurrentIdToken(): Promise<string | null> {
  const user = firebaseAuth.currentUser
  if (!user) return null
  // forceRefresh = false → Firebase tự refresh nếu token còn < 5 phút
  return user.getIdToken(false)
}

export async function signOut(): Promise<void> {
  await firebaseSignOut(firebaseAuth)
}

/**
 * Subscribe để lắng nghe thay đổi token (rotate mỗi giờ).
 * Dùng trong Providers để cập nhật store khi token mới được issue.
 */
export function onTokenRefresh(callback: (user: User | null) => void) {
  return onIdTokenChanged(firebaseAuth, callback)
}
