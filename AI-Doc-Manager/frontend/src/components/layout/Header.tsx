"use client";

import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";

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
        <Link
          href="/notifications"
          className="relative p-2 text-on-surface-variant hover:bg-surface-container rounded-md"
          aria-label="Open notifications"
          title="Notifications"
        >
          <span className="material-symbols-outlined block" data-icon="notifications">
            notifications
          </span>
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-tertiary ring-2 ring-white" />
        </Link>
      </div>
    </header>
  );
}
