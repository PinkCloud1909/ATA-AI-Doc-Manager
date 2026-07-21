"use client";
<<<<<<< Updated upstream
import { useState } from "react";

export default function SecurityTab() {
=======

import { useMemo, useState } from "react";
import { toast } from "sonner";
import { useTranslation } from "@/i18n/LanguageContext";
import { authApi } from "@/lib/api/auth";
import { getApiErrorMessage } from "@/lib/error-handler";
import { getPasswordPolicyChecks, validatePassword } from "@/lib/validation";

export default function SecurityTab() {
  const { t } = useTranslation();
  const [currentPassword, setCurrentPassword] = useState("");
>>>>>>> Stashed changes
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const policyChecks = useMemo(() => getPasswordPolicyChecks(newPassword), [newPassword]);

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
<<<<<<< Updated upstream
    if (newPassword !== confirmPassword) {
      alert("Mật khẩu không khớp!");
      return;
    }
    console.log("Đổi mật khẩu thành công!");
    // Gọi API đổi mật khẩu ở đây
=======
    const policyError = validatePassword(newPassword);
    if (policyError) {
      toast.error(policyError);
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error(t.auth.passwordMismatch);
      return;
    }

    setIsSubmitting(true);
    try {
      await authApi.changePassword(currentPassword, newPassword);
      toast.success(t.settings.passwordChanged);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      toast.error(getApiErrorMessage(error, t.settings.passwordChangeFailed));
    } finally {
      setIsSubmitting(false);
    }
>>>>>>> Stashed changes
  };

  const inputClass = "w-full rounded border-transparent bg-surface-container-low px-4 py-2.5 text-sm text-on-surface transition-all placeholder:text-outline focus:border-tertiary/30 focus:bg-surface-container-lowest focus:ring-0";

  return (
    <div className="animate-in fade-in duration-300">
      <header className="mb-8">
        <h1 className="font-headline text-3xl font-bold text-on-surface">
          Bảo mật
        </h1>
      </header>

<<<<<<< Updated upstream
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
=======
      <section className="max-w-lg rounded-lg border border-outline-variant/15 bg-surface-container-lowest p-6 shadow-sm">
        <h2 className="mb-6 font-headline text-xl font-semibold text-on-surface">
          {t.settings.changePassword}
        </h2>

        <form onSubmit={handleUpdatePassword} className="space-y-5">
          <PasswordField
            id="current_password"
            label={t.settings.currentPassword}
            value={currentPassword}
            onChange={setCurrentPassword}
            autoComplete="current-password"
            className={inputClass}
          />
          <PasswordField
            id="new_password"
            label={t.settings.newPassword}
            value={newPassword}
            onChange={setNewPassword}
            autoComplete="new-password"
            className={inputClass}
          />

          <ul className="grid gap-1.5 text-xs sm:grid-cols-2" aria-label="Password requirements">
            {policyChecks.map((check) => (
              <li key={check.label} className={`flex items-center gap-1.5 ${check.valid ? "text-emerald-700" : "text-on-surface-variant"}`}>
                <span className="material-symbols-outlined text-[15px]">
                  {check.valid ? "check_circle" : "radio_button_unchecked"}
                </span>
                {check.label}
              </li>
            ))}
          </ul>

          <PasswordField
            id="confirm_password"
            label={t.settings.confirmNewPassword}
            value={confirmPassword}
            onChange={setConfirmPassword}
            autoComplete="new-password"
            className={inputClass}
          />
>>>>>>> Stashed changes

          <div className="pt-4">
            <button
              type="submit"
              disabled={isSubmitting || !currentPassword || !newPassword || !confirmPassword}
              className="rounded bg-primary px-6 py-2 text-sm font-medium text-on-primary shadow-sm transition-all hover:bg-primary-dim disabled:cursor-not-allowed disabled:opacity-50"
            >
<<<<<<< Updated upstream
              Xác nhận
=======
              {isSubmitting ? t.common.loading : t.common.confirm}
>>>>>>> Stashed changes
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

function PasswordField({
  id,
  label,
  value,
  onChange,
  autoComplete,
  className,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete: string;
  className: string;
}) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-semibold uppercase tracking-wider text-on-surface-variant" htmlFor={id}>
        {label}
      </label>
      <input
        id={id}
        type="password"
        required
        maxLength={id === "current_password" ? 255 : 128}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete={autoComplete}
        className={className}
      />
    </div>
  );
}
