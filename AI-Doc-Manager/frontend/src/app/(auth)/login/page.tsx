"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login, isLoading, error } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <div className="bg-background text-on-surface font-body antialiased min-h-screen flex items-center justify-center p-4 selection:bg-secondary-container selection:text-on-secondary-container">
      {/* Main Login Card */}
      <main className="w-full max-w-[420px] bg-surface-container-lowest rounded-lg p-8 sm:p-10 shadow-[0_4px_6px_-1px_rgba(43,52,55,0.04),0_10px_15px_-3px_rgba(43,52,55,0.08)] z-10">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-surface-container-low text-primary mb-4">
            <span className="material-symbols-outlined text-2xl">
              architecture
            </span>
          </div>
          <h1 className="font-display text-2xl font-bold tracking-tight text-on-surface mb-2">
            Knowledge Curator
          </h1>
          <p className="text-on-surface-variant text-sm font-label">
            Đăng nhập vào không gian làm việc của bạn
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-error-container/20 p-3 rounded-lg flex items-start gap-3 border border-error-container/30">
            <span className="material-symbols-outlined text-error text-xl shrink-0 mt-0.5">
              error
            </span>
            <p className="text-sm font-medium text-error leading-snug">
              {error}
            </p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Email Field */}
          <div className="space-y-1.5">
            <label
              className="block text-sm font-medium text-on-surface font-label"
              htmlFor="email"
            >
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="w-full bg-surface-container-low text-on-surface font-body text-sm rounded-lg px-4 py-3 border-0 outline-none focus:bg-surface-container-lowest focus:ring-1 focus:ring-outline-variant/30 transition-all placeholder:text-on-surface-variant/50"
            />
          </div>

          {/* Password Field */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label
                className="block text-sm font-medium text-on-surface font-label"
                htmlFor="password"
              >
                Mật khẩu
              </label>
              <Link
                href="#"
                className="text-sm font-medium text-tertiary hover:text-tertiary-dim transition-colors font-label"
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
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-surface-container-low text-on-surface font-body text-sm rounded-lg px-4 py-3 border-0 outline-none focus:bg-surface-container-lowest focus:ring-1 focus:ring-outline-variant/30 transition-all placeholder:text-on-surface-variant/50"
            />
          </div>

          {/* Submit Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-b from-primary to-primary-dim text-on-primary font-medium font-label py-3 px-4 rounded-lg shadow-sm hover:opacity-90 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isLoading ? "Đang xác thực..." : "Đăng nhập"}
              {!isLoading && (
                <span className="material-symbols-outlined text-sm">
                  arrow_forward
                </span>
              )}
            </button>
          </div>
        </form>

        {/* Footer Link */}
        <div className="mt-8 text-center">
          <p className="text-sm text-on-surface-variant font-label">
            Chưa có tài khoản?
            <Link
              href="/register"
              className="font-medium text-tertiary hover:text-tertiary-dim transition-colors ml-1"
            >
              Đăng ký ngay
            </Link>
          </p>
        </div>
      </main>

      {/* Background Decorative Elements */}
      <div
        aria-hidden="true"
        className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
      >
        <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[40%] bg-surface-container-low rounded-full blur-3xl opacity-50"></div>
        <div className="absolute bottom-[-10%] left-[-5%] w-[50%] h-[50%] bg-surface-container-low rounded-full blur-3xl opacity-30"></div>
      </div>
    </div>
  );
}
