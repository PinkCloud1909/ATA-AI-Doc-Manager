"use client";

import { useTranslation } from "@/i18n/LanguageContext";

interface FilterProps {
  searchQuery: string;
  setSearchQuery: (val: string) => void;
  statusFilter: string;
  setStatusFilter: (val: string) => void;
  typeFilter: string;
  setTypeFilter: (val: string) => void;
}

export default function DocumentFilters({
  searchQuery,
  setSearchQuery,
  statusFilter,
  setStatusFilter,
  typeFilter,
  setTypeFilter,
}: FilterProps) {
  const { t } = useTranslation();

  const statusOptions = Object.entries(t.status) as [string, string][];
  const typeOptions = Object.entries(t.documentType) as [string, string][];

  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
      {/* Search */}
      <div className="md:col-span-5 bg-surface-container-lowest p-4 rounded-xl border border-transparent shadow-sm">
        <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 block mb-2">
          {t.common.search}
        </label>
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
            search
          </span>
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface-container-low border-none rounded-lg pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-tertiary/10"
            placeholder={t.documents.filters.searchPlaceholder}
            type="text"
          />
        </div>
      </div>

      {/* Status filter */}
      <div className="md:col-span-3 bg-surface-container-lowest p-4 rounded-xl border border-transparent shadow-sm">
        <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 block mb-2">
          {t.common.status}
        </label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-full bg-surface-container-low border-none rounded-lg py-2 text-sm focus:ring-0"
        >
          <option value={t.common.all}>{t.common.all}</option>
          {statusOptions.map(([key, label]) => (
            <option key={key} value={label}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {/* Type filter */}
      <div className="md:col-span-4 bg-surface-container-lowest p-4 rounded-xl border border-transparent shadow-sm flex items-end justify-between">
        <div className="flex-1">
          <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 block mb-2">
            {t.common.type}
          </label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="w-full bg-surface-container-low border-none rounded-lg py-2 text-sm focus:ring-0"
          >
            <option value={t.common.all}>{t.common.all}</option>
            {typeOptions.map(([key, label]) => (
              <option key={key} value={label}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={() => {
            setSearchQuery("");
            setStatusFilter(t.common.all);
            setTypeFilter(t.common.all);
          }}
          className="ml-3 text-tertiary text-sm font-semibold hover:underline whitespace-nowrap"
        >
          {t.documents.filters.clearFilters}
        </button>
      </div>
    </div>
  );
}
