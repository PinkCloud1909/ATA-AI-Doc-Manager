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
  apiKey:            process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "",
  authDomain:        process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "",
  projectId:         process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "",
  storageBucket:     process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "",
  appId:             process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "",
}

// Bọc logic khởi tạo vào hàm try/catch để không làm sập tiến trình build của Docker
const initFirebaseAuth = () => {
  try {
    // Nếu chưa có app nào thì khởi tạo, có rồi thì lấy dùng lại
    const firebaseApp = getApps().length ? getApp() : initializeApp(firebaseConfig)
    return getAuth(firebaseApp)
  } catch (error) {
    console.warn("⚠️ Bỏ qua lỗi khởi tạo Firebase (Thường do đang build Docker hoặc chạy Mock Login).")
    // Trả về một object rỗng để TypeScript và Next.js không bị crash
    return {} as ReturnType<typeof getAuth>
  }
}

export const firebaseAuth = initFirebaseAuth()

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
  return await credential.user.getIdToken()
}

/**
 * Lấy ID Token của user hiện tại (auto-refresh nếu sắp hết hạn).
 * Dùng trong Axios interceptor để luôn gửi token mới nhất.
 */
export async function getCurrentIdToken(): Promise<string | null> {
  // Tránh lỗi khi gọi thuộc tính trên object rỗng lúc build
  if (!firebaseAuth || !firebaseAuth.currentUser) return null
  
  const user = firebaseAuth.currentUser
  // forceRefresh = false → Firebase tự refresh nếu token còn < 5 phút
  return await user.getIdToken(false)
}

export async function signOut(): Promise<void> {
  const authLike = firebaseAuth as { signOut?: unknown }
  if (typeof authLike.signOut === "function") {
    await firebaseSignOut(firebaseAuth)
  }
}

/**
 * Subscribe để lắng nghe thay đổi token (rotate mỗi giờ).
 * Dùng trong Providers để cập nhật store khi token mới được issue.
 */
export function onTokenRefresh(callback: (user: User | null) => void) {
  const authLike = firebaseAuth as { onIdTokenChanged?: unknown }
  if (typeof authLike.onIdTokenChanged !== "function") {
    return () => {} // Trả về hàm rỗng nếu đang mock/build
  }
  return onIdTokenChanged(firebaseAuth, callback)
}
