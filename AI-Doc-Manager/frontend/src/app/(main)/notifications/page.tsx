"use client";

import { useTranslation } from "@/i18n/LanguageContext";

export default function NotificationsPage() {
  const { t } = useTranslation();

  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-4 py-6 md:px-8">
      <div className="mb-7">
        <h1 className="text-3xl font-extrabold tracking-tight text-on-surface">
          {t.notifications.title}
        </h1>
        <p className="mt-2 text-sm text-on-surface-variant">
          {t.notifications.subtitle}
        </p>
      </div>

      <div className="mt-16 flex flex-col items-center justify-center text-center">
        <span
          className="material-symbols-outlined text-6xl text-on-surface-variant/30 mb-4"
          style={{ fontSize: "64px" }}
        >
          notifications_off
        </span>
        <h2 className="text-lg font-bold text-on-surface mb-2">
          {t.notifications.empty}
        </h2>
        <p className="text-sm text-on-surface-variant max-w-md">
          {t.notifications.underDevelopment}
        </p>
      </div>
    </div>
  );
}
