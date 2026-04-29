"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterPage() {
  // Giả định bạn có hàm register trong useAuth
  // Nếu chưa có, bạn cần thêm hàm này vào file useAuth.ts nhé
  const { register, isLoading, error } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError("");

    if (password !== confirmPassword) {
      setLocalError("Mật khẩu xác nhận không khớp.");
      return;
    }

    if (register) {
      await register(email, password);
    } else {
      setLocalError("Hàm register chưa được cài đặt trong useAuth.");
    }
  };

  const displayError = localError || error;

  return (
    <div className="bg-background min-h-screen flex items-center justify-center font-body text-on-surface antialiased p-4 selection:bg-secondary-container selection:text-on-secondary-container">
      <main className="w-full max-w-md p-8 sm:p-12 bg-surface-container-lowest rounded-xl shadow-[0_4px_6px_-1px_rgba(43,52,55,0.04),0_10px_15px_-3px_rgba(43,52,55,0.08)] flex flex-col gap-8 relative z-10">
        {/* Header */}
        <header className="text-center flex flex-col items-center gap-2">
          <div className="w-12 h-12 bg-surface-container-low rounded-lg flex items-center justify-center mb-4 text-primary">
            <span className="material-symbols-outlined text-2xl">
              architecture
            </span>
          </div>
          <h1 className="font-headline text-2xl font-bold tracking-tight text-on-surface">
            Đăng ký tài khoản
          </h1>
          <p className="text-on-surface-variant font-body text-sm">
            Tham gia Knowledge Curator ngay hôm nay.
          </p>
        </header>

        {/* Error Message */}
        {displayError && (
          <div className="bg-error-container/20 p-3 rounded-lg flex items-start gap-3 border border-error-container/30 -mt-2">
            <span className="material-symbols-outlined text-error text-xl shrink-0 mt-0.5">
              error
            </span>
            <p className="text-sm font-medium text-error leading-snug">
              {displayError}
            </p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="flex flex-col gap-1.5">
            <label
              className="font-label text-xs uppercase tracking-[0.05em] font-semibold text-on-surface-variant"
              htmlFor="email"
            >
              Email
            </label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline-variant text-sm">
                mail
              </span>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ten@congty.com"
                className="w-full bg-surface-container-low border-none rounded pl-10 pr-4 py-3 text-sm font-body text-on-surface placeholder:text-outline-variant focus:ring-0 focus:bg-surface-container-lowest focus:outline focus:outline-1 focus:outline-tertiary/30 transition-all"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label
              className="font-label text-xs uppercase tracking-[0.05em] font-semibold text-on-surface-variant"
              htmlFor="password"
            >
              Mật khẩu
            </label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline-variant text-sm">
                lock
              </span>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-surface-container-low border-none rounded pl-10 pr-4 py-3 text-sm font-body text-on-surface placeholder:text-outline-variant focus:ring-0 focus:bg-surface-container-lowest focus:outline focus:outline-1 focus:outline-tertiary/30 transition-all"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label
              className="font-label text-xs uppercase tracking-[0.05em] font-semibold text-on-surface-variant"
              htmlFor="confirm-password"
            >
              Xác nhận mật khẩu
            </label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline-variant text-sm">
                check_circle
              </span>
              <input
                id="confirm-password"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-surface-container-low border-none rounded pl-10 pr-4 py-3 text-sm font-body text-on-surface placeholder:text-outline-variant focus:ring-0 focus:bg-surface-container-lowest focus:outline focus:outline-1 focus:outline-tertiary/30 transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="mt-2 w-full bg-gradient-to-b from-primary to-primary-dim text-on-primary font-label text-sm font-medium py-3 rounded hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <span>{isLoading ? "Đang xử lý..." : "Đăng ký"}</span>
            {!isLoading && (
              <span
                className="material-symbols-outlined text-sm"
                style={{ fontVariationSettings: "'wght' 600" }}
              >
                arrow_forward
              </span>
            )}
          </button>
        </form>

        {/* Footer */}
        <footer className="text-center pt-2 border-t border-surface-variant/30">
          <p className="text-sm font-body text-on-surface-variant">
            Đã có tài khoản?
            <Link
              href="/login"
              className="text-tertiary hover:underline font-medium ml-1"
            >
              Đăng nhập
            </Link>
          </p>
        </footer>
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
