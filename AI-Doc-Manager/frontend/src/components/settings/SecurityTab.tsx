"use client";
import { useState } from "react";

export default function SecurityTab() {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleUpdatePassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      alert("Mật khẩu không khớp!");
      return;
    }
    console.log("Đổi mật khẩu thành công!");
    // Gọi API đổi mật khẩu ở đây
  };

  return (
    <div className="animate-in fade-in duration-300">
      <header className="mb-8">
        <h1 className="font-headline text-3xl font-bold text-on-surface">
          Bảo mật
        </h1>
      </header>

      <section className="max-w-md bg-surface-container-lowest rounded-lg p-6 shadow-[0_1px_2px_0_rgba(43,52,55,0.05)] border border-outline-variant/15">
        <h2 className="font-headline text-xl font-semibold mb-6 text-on-surface">
          Đổi mật khẩu
        </h2>

        <form onSubmit={handleUpdatePassword} className="space-y-5">
          <div className="space-y-1.5">
            <label
              className="block font-label text-xs font-semibold uppercase tracking-wider text-on-surface-variant"
              htmlFor="new_password"
            >
              Mật khẩu mới
            </label>
            <input
              type="password"
              id="new_password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Nhập mật khẩu mới"
              className="w-full bg-surface-container-low border-transparent focus:border-tertiary/30 focus:bg-surface-container-lowest focus:ring-0 rounded px-4 py-2.5 text-sm font-body text-on-surface transition-all placeholder-outline"
            />
          </div>

          <div className="space-y-1.5">
            <label
              className="block font-label text-xs font-semibold uppercase tracking-wider text-on-surface-variant"
              htmlFor="confirm_password"
            >
              Xác nhận mật khẩu mới
            </label>
            <input
              type="password"
              id="confirm_password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Nhập lại mật khẩu mới"
              className="w-full bg-surface-container-low border-transparent focus:border-tertiary/30 focus:bg-surface-container-lowest focus:ring-0 rounded px-4 py-2.5 text-sm font-body text-on-surface transition-all placeholder-outline"
            />
          </div>

          <div className="pt-4">
            <button
              type="submit"
              className="bg-primary hover:bg-primary-dim text-on-primary font-body text-sm font-medium py-2 px-6 rounded transition-all shadow-sm"
            >
              Xác nhận
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
