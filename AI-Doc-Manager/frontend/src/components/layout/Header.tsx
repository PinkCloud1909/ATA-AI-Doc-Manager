"use client";

import { useAuthStore } from "@/stores/authStore";
import { useTranslation } from "@/i18n/LanguageContext";
import Link from "next/link";

export default function Header() {
  const user = useAuthStore((s) => s.user);
  const { t } = useTranslation();

  const getUserInitials = () => {
    const name = user?.username || "";
    return name.slice(0, 2).toUpperCase() || "U";
  };

  return (
    <header className="sticky top-0 w-full z-50 bg-white/80 backdrop-blur-xl flex justify-between items-center px-8 py-4 border-b border-outline-variant/10">
      <div className="flex items-center gap-8">
        <div className="md:hidden text-lg font-bold tracking-tighter text-on-surface">
          {t.common.appName}
        </div>
      </div>
      <div className="flex items-center gap-4">
        <Link
          href="/notifications"
          className="relative p-2 text-on-surface-variant hover:bg-surface-container rounded-md"
          aria-label={t.nav.notifications}
          title={t.nav.notifications}
        >
          <span className="material-symbols-outlined block">notifications</span>
        </Link>
        <div className="h-8 w-8 rounded-full bg-surface-dim overflow-hidden ml-2 flex items-center justify-center">
          <span className="text-xs font-bold text-on-surface-variant">
            {getUserInitials()}
          </span>
        </div>
      </div>
    </header>
  );
}
