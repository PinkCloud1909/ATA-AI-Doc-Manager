"use client";

import { useAuth } from "@/hooks/useAuth";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 w-full z-50 bg-white/80 backdrop-blur-xl flex justify-between items-center px-8 py-4 border-b border-outline-variant/10">
      <div className="flex items-center gap-8">
        <div className="md:hidden text-lg font-bold tracking-tighter text-on-surface">
          Architect SOC
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center bg-surface-container-low px-3 py-1.5 rounded-md">
          <span
            className="material-symbols-outlined text-[18px] text-on-surface-variant mr-2"
            data-icon="search"
          >
            search
          </span>
          <input
            className="bg-transparent border-none focus:ring-0 text-sm w-48 text-on-surface"
            placeholder="Tìm kiếm tài liệu..."
            type="text"
          />
        </div>
        <button
          className="material-symbols-outlined p-2 text-on-surface-variant hover:bg-surface-container rounded-md"
          data-icon="notifications"
        >
          notifications
        </button>
      </div>
    </header>
  );
}
