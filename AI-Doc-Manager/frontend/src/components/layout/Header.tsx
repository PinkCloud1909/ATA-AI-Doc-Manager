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
        {/* <div className="hidden md:flex items-center gap-6">
          <a
            className="text-on-surface font-semibold border-b-2 border-on-surface text-sm pb-1"
            href="#"
          >
            Network Status
          </a>
          <a
            className="text-on-surface-variant hover:text-on-surface transition-colors text-sm"
            href="#"
          >
            Logs
          </a>
        </div> */}
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
        <button
          className="material-symbols-outlined p-2 text-on-surface-variant hover:bg-surface-container rounded-md"
          data-icon="settings"
        >
          settings
        </button>
        <div className="h-8 w-8 rounded-full bg-surface-dim overflow-hidden ml-2">
          <img
            alt="User profile"
            data-alt="close-up portrait of a professional male architect with glasses and a friendly smile in soft studio lighting"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuAuSdmwoTcwyok06kPxSl6Xp0KKg4FWvWzcPzZUrOAD1AQVuuG07pmq7LyG4ZZpqnSL4GFFt93AhIZIvqGMkywM7fEq_R3TAQYCYI4LhgDIqYSchoIv73Hb8NC8TGfxbOo-8SOhYmUHEpYutvCOYLn_gZa5UOh-O7meu2FNFltXxE85FpXB8zlKBpUkDaAYbyoyoGCX1FG1qwymyfnr58blDHZZ6k7fN-aEIkmCfHYqQg1Ugs904K4sV4g0NVFLpqYPEDOtsYvBPhp1"
            className=""
          />
        </div>
      </div>
    </header>
  );
}
