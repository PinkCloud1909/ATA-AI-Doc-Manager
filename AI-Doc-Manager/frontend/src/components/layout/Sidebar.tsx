"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { usePermission } from "@/hooks/usePermission";
import { useAuth } from "@/hooks/useAuth";
import { useState, useRef, useEffect } from "react";
import SettingsModal from "@/components/settings/SettingsModal";
import { useTranslation } from "@/i18n/LanguageContext";

interface NavItem {
  href: string;
  translationKey: string;
  icon: string;
  show?: boolean;
}

export default function Sidebar() {
  const pathname = usePathname();
  const perm = usePermission();
  const { user, logout } = useAuth();
  const { t } = useTranslation();

  const [isHovered, setIsHovered] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const profileMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        profileMenuRef.current &&
        !profileMenuRef.current.contains(event.target as Node)
      ) {
        setIsProfileOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navItems: NavItem[] = [
    { href: "/dashboard", translationKey: "nav.dashboard", icon: "dashboard" },
    { href: "/documents", translationKey: "nav.documents", icon: "description" },
    {
      href: "/approvals",
      translationKey: "nav.approvals",
      icon: "rate_review",
      show: perm.canApprove,
    },
    { href: "/chat", translationKey: "nav.chat", icon: "forum" },
    { href: "/runbooks", translationKey: "nav.runbooks", icon: "auto_stories" },
    {
      href: "/admin/users",
      translationKey: "nav.admin",
      icon: "manage_accounts",
      show: perm.canAdmin,
    },
  ];

  const visibleItems = navItems.filter((i) => i.show !== false);

  // Resolve translation key to string
  const tr = (key: string): string => {
    const parts = key.split(".");
    let val: unknown = t;
    for (const part of parts) {
      if (val && typeof val === "object" && part in val) {
        val = (val as Record<string, unknown>)[part];
      } else {
        return key;
      }
    }
    return typeof val === "string" ? val : key;
  };

  const getUserInitials = () => {
    const name = user?.username || "";
    return name.slice(0, 2).toUpperCase() || "U";
  };

  return (
    <>
      <aside
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => {
          setIsHovered(false);
          setIsProfileOpen(false);
        }}
        className={`flex flex-col h-full bg-surface-container-low border-r border-transparent py-4 transition-all duration-300 ease-in-out z-[70] overflow-visible shrink-0 ${
          isHovered
            ? "w-64 px-4 absolute md:relative shadow-[4px_0_24px_rgba(0,0,0,0.15)] md:shadow-none h-full"
            : "w-16 md:w-20 px-1 md:px-2 items-center relative"
        }`}
      >
        {/* Header: Logo & Title */}
        <div
          className={`flex flex-col space-y-1 ${isHovered ? "px-3" : "items-center"}`}
        >
          {isHovered && (
            <h1 className="text-xl font-black text-on-surface font-headline tracking-tighter whitespace-nowrap">
              {t.common.appName}
            </h1>
          )}
          <div
            className={`flex items-center gap-2 ${isHovered ? "pt-4" : "pt-2"}`}
          >
            <div className="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center overflow-hidden shrink-0">
              <span className="material-symbols-outlined text-primary">
                architecture
              </span>
            </div>
            {isHovered && (
              <div className="whitespace-nowrap transition-opacity duration-300">
                <p className="text-sm font-bold font-headline text-on-surface">
                  {t.common.appName}
                </p>
                <p className="text-xs text-on-surface-variant">
                  {t.common.appTagline}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 space-y-1 mt-6 w-full">
          {visibleItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                title={!isHovered ? tr(item.translationKey) : ""}
                className={`flex items-center gap-3 rounded-lg transition-all duration-200 overflow-hidden ${
                  isHovered
                    ? "px-3 py-2"
                    : "justify-center py-2 w-12 h-12 mx-auto"
                } ${
                  isActive
                    ? "text-on-surface bg-surface-container-lowest shadow-sm border-l-2 border-tertiary"
                    : "text-on-surface-variant hover:bg-surface-container hover:translate-x-1 border-l-2 border-transparent"
                }`}
              >
                <span
                  className={`material-symbols-outlined ${isActive ? "text-tertiary" : ""}`}
                  style={isActive ? { fontVariationSettings: '"FILL" 1' } : {}}
                >
                  {item.icon}
                </span>
                {isHovered && (
                  <span
                    className={`font-medium text-sm whitespace-nowrap ${isActive ? "font-semibold" : ""}`}
                  >
                    {tr(item.translationKey)}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Profile & Dropdown Menu */}
        <div
          className="pt-4 mt-2 border-t border-outline-variant/10 relative w-full"
          ref={profileMenuRef}
        >
          {/* Popup Menu */}
          {isProfileOpen && isHovered && (
            <div className="absolute bottom-full left-0 md:left-3 mb-2 w-56 bg-white rounded-xl shadow-xl border border-neutral-100 py-2 z-50 animate-in fade-in slide-in-from-bottom-2 duration-200">
              <Link
                href="/profile"
                className="flex items-center gap-3 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
              >
                <span className="material-symbols-outlined text-neutral-500 text-[20px]">
                  person
                </span>
                <span className="font-medium">{t.nav.profile}</span>
              </Link>

              <button
                onClick={() => {
                  setIsSettingsOpen(true);
                  setIsProfileOpen(false);
                }}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
              >
                <span className="material-symbols-outlined text-neutral-500 text-[20px]">
                  settings
                </span>
                <span className="font-medium">{t.nav.settings}</span>
              </button>

              <div className="h-[1px] bg-neutral-100 my-1 mx-2"></div>
              <button
                onClick={logout}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <span className="material-symbols-outlined text-red-500 text-[20px]">
                  logout
                </span>
                <span className="font-medium">{t.auth.logout}</span>
              </button>
            </div>
          )}

          {/* User Info Trigger */}
          <div
            onClick={() => isHovered && setIsProfileOpen(!isProfileOpen)}
            className={`flex items-center gap-3 py-2 rounded-lg transition-colors ${isHovered ? "px-3 cursor-pointer hover:bg-surface-container" : "justify-center"}`}
            title={!isHovered ? user?.username || "Profile" : ""}
          >
            <div className="w-9 h-9 rounded-full bg-surface-dim overflow-hidden flex-shrink-0 flex items-center justify-center">
              <span className="text-xs font-bold text-on-surface-variant">
                {getUserInitials()}
              </span>
            </div>
            {isHovered && (
              <div className="min-w-0">
                <p className="text-sm font-bold text-on-surface truncate">
                  {user?.username || t.nav.profile}
                </p>
                <p className="text-[10px] text-on-surface-variant truncate uppercase">
                  {perm.canAdmin ? "ADMIN" : "USER"}
                </p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Settings Modal */}
      {isSettingsOpen && (
        <SettingsModal onClose={() => setIsSettingsOpen(false)} />
      )}
    </>
  );
}
