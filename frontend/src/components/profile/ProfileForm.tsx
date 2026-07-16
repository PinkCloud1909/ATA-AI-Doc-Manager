"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { usePermission } from "@/hooks/usePermission";
import { useTranslation } from "@/i18n/LanguageContext";

export default function ProfileForm() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const perm = usePermission();

  // Initialize state with current user data
  const [fullName, setFullName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");

  // Update state when user data is loaded
  useEffect(() => {
    if (user) {
      setFullName(user.username || "");
      setPhoneNumber((user as any).phoneNumber || "");
    }
  }, [user]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Call API to update information here
    console.log("Update:", { fullName, phoneNumber });
  };

  return (
    <div className="lg:col-span-8">
      <div className="bg-surface-container-lowest rounded-xl p-8 lg:p-10 border border-outline-variant/10 h-full">
        <div className="flex items-center justify-between mb-8">
          <h3 className="font-headline text-2xl font-bold text-on-background">
            {t.settings.general}
          </h3>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Full Name Field */}
            <div className="space-y-2">
              <label
                className="block font-body text-xs font-bold text-on-background uppercase tracking-widest opacity-80"
                htmlFor="fullName"
              >
                {t.common.name}
              </label>
              <div className="relative">
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-surface-container-low border-none rounded-lg py-3 px-4 text-on-background font-body text-base focus:bg-surface-container-lowest focus:ring-1 focus:ring-tertiary/30 transition-all outline-none"
                />
              </div>
            </div>

            {/* Phone Number Field */}
            <div className="space-y-2">
              <label
                className="block font-body text-xs font-bold text-on-background uppercase tracking-widest opacity-80"
                htmlFor="phoneNumber"
              >
                {t.common.optional}
              </label>
              <div className="relative">
                <input
                  id="phoneNumber"
                  type="tel"
                  placeholder={t.common.optional}
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="w-full bg-surface-container-low border-none rounded-lg py-3 px-4 text-on-background font-body text-base focus:bg-surface-container-lowest focus:ring-1 focus:ring-tertiary/30 transition-all outline-none"
                />
              </div>
            </div>

            {/* Email Field (Read-only) */}
            <div className="space-y-2">
              <label
                className="block font-body text-xs font-bold text-on-background uppercase tracking-widest opacity-80 flex items-center"
                htmlFor="email"
              >
                {t.profile.email}
                <span
                  className="material-symbols-outlined text-[14px] ml-1 opacity-50"
                  title={t.settings.general}
                >
                  lock
                </span>
              </label>
              <div className="relative">
                <input
                  id="email"
                  type="email"
                  readOnly
                  value={user?.username || ""}
                  className="w-full bg-surface-bright border-none rounded-lg py-3 px-4 text-on-surface-variant font-body text-base cursor-not-allowed opacity-80 outline-none"
                />
              </div>
              <p className="text-[11px] text-on-surface-variant mt-1 opacity-70">
                {t.settings.uiOnlyNotice}
              </p>
            </div>

            {/* Role Field (Read-only) */}
            <div className="space-y-2">
              <label className="block font-body text-xs font-bold text-on-background uppercase tracking-widest opacity-80">
                {t.profile.roles}
              </label>
              <div className="w-full bg-surface-bright border-none rounded-lg py-3 px-4 flex items-center">
                <span className="material-symbols-outlined mr-2 text-tertiary text-[18px]">
                  {perm.canAdmin ? "admin_panel_settings" : "person"}
                </span>
                <span className="text-on-background font-medium">
                  {perm.canAdmin ? t.admin.adminRole : t.admin.viewerRole}
                </span>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="h-px w-full bg-gradient-to-r from-transparent via-outline-variant/20 to-transparent my-8"></div>

          {/* Action Area */}
          <div className="flex items-center justify-end space-x-4 pt-2">
            <button
              type="button"
              className="px-5 py-2.5 rounded-md font-body text-sm font-semibold text-on-surface-variant hover:text-on-background hover:bg-surface-container-low transition-colors"
            >
              {t.common.cancel}
            </button>
            <button
              type="submit"
              className="px-6 py-2.5 rounded-md font-body text-sm font-semibold bg-primary text-on-primary shadow-sm hover:opacity-90 hover:shadow-md transition-all flex items-center bg-gradient-to-b from-primary to-primary-dim border border-primary-dim/50"
            >
              <span className="material-symbols-outlined mr-2 text-[18px]">
                save
              </span>
              {t.common.save}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
