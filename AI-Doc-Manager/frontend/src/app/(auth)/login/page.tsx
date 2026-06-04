"use client"

import { FormEvent, useState } from "react"
import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"

export default function LoginPage() {
  const { login, isLoading, error } = useAuth()
  const [username, setUsername] = useState("admin")
  const [password, setPassword] = useState("admin123")

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    await login(username, password)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4 font-body text-on-surface antialiased selection:bg-secondary-container selection:text-on-secondary-container">
      <main className="z-10 w-full max-w-[420px] rounded-lg bg-surface-container-lowest p-8 shadow-[0_4px_6px_-1px_rgba(43,52,55,0.04),0_10px_15px_-3px_rgba(43,52,55,0.08)] sm:p-10">
        <div className="mb-8 text-center">
          <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-surface-container-low text-primary">
            <span className="material-symbols-outlined text-2xl">architecture</span>
          </div>
          <h1 className="mb-2 font-display text-2xl font-bold tracking-tight text-on-surface">
            Knowledge Curator
          </h1>
          <p className="text-sm text-on-surface-variant">
            Đăng nhập vào không gian làm việc của bạn
          </p>
        </div>

        {error && (
          <div className="mb-6 flex items-start gap-3 rounded-lg border border-error-container/30 bg-error-container/20 p-3">
            <span className="material-symbols-outlined mt-0.5 shrink-0 text-xl text-error">
              error
            </span>
            <p className="text-sm font-medium leading-snug text-error">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-on-surface" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="admin"
              className="w-full rounded-lg border-0 bg-surface-container-low px-4 py-3 text-sm text-on-surface outline-none transition-all placeholder:text-on-surface-variant/50 focus:bg-surface-container-lowest focus:ring-1 focus:ring-outline-variant/30"
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label
                className="block text-sm font-medium text-on-surface"
                htmlFor="password"
              >
                Mật khẩu
              </label>
              <Link
                href="#"
                className="text-sm font-medium text-tertiary transition-colors hover:text-tertiary-dim"
              >
                Quên mật khẩu?
              </Link>
            </div>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="admin123"
              className="w-full rounded-lg border-0 bg-surface-container-low px-4 py-3 text-sm text-on-surface outline-none transition-all placeholder:text-on-surface-variant/50 focus:bg-surface-container-lowest focus:ring-1 focus:ring-outline-variant/30"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-b from-primary to-primary-dim px-4 py-3 font-medium text-on-primary shadow-sm transition-all hover:opacity-90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? "Đang xác thực..." : "Đăng nhập"}
              {!isLoading && <ArrowRight size={18} />}
            </button>
          </div>
        </form>

        <div className="mt-8 text-center">
          <p className="text-sm text-on-surface-variant">
            Chưa có tài khoản?
            <Link
              href="/register"
              className="ml-1 font-medium text-tertiary transition-colors hover:text-tertiary-dim"
            >
              Đăng ký ngay
            </Link>
          </p>
        </div>
      </main>

      <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="absolute right-[-5%] top-[-10%] h-[40%] w-[40%] rounded-full bg-surface-container-low opacity-50 blur-3xl" />
        <div className="absolute bottom-[-10%] left-[-5%] h-[50%] w-[50%] rounded-full bg-surface-container-low opacity-30 blur-3xl" />
      </div>
    </div>
  )
}
