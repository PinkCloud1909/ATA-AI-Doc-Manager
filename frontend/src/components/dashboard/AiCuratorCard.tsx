"use client";

import React from "react";
import { useDocumentList } from "@/hooks/useDocuments";
import { useTranslation, formatT } from "@/i18n/LanguageContext";

export default function AiCuratorCard() {
  const { t } = useTranslation();
  const { data } = useDocumentList({ page_size: 1 });
  const totalDocs = data?.total ?? 0;

  return (
    <div className="bg-tertiary text-on-tertiary p-8 rounded-xl relative overflow-hidden flex flex-col justify-between group">
      <div className="relative z-10">
        <span className="material-symbols-outlined text-[32px] mb-4">bolt</span>
        <h2 className="text-2xl font-bold tracking-tight mb-2">{t.dashboard.aiCurator}</h2>
        {totalDocs === 0 ? (
          <p className="text-sm opacity-80 leading-relaxed">
            {t.dashboard.uploadFirstDocument}
          </p>
        ) : (
          <p className="text-sm opacity-80 leading-relaxed">
            {formatT(t.dashboard.aiCuratorDesc, { count: totalDocs })}
          </p>
        )}
      </div>
      <div className="mt-8 relative z-10">
        <a
          href="/documents"
          className="inline-flex items-center gap-2 bg-white text-tertiary px-6 py-2.5 rounded-lg font-bold text-sm shadow-xl active:scale-95 transition-all hover:bg-surface-container-low"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          {t.dashboard.uploadDocument}
        </a>
      </div>
      <div className="absolute -right-12 -bottom-12 w-48 h-48 bg-white/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
      <div className="absolute right-0 top-0 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
    </div>
  );
}
