"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { usePermission } from "@/hooks/usePermission";
import { useAuth } from "@/hooks/useAuth"; // Import hook useAuth
import { useState, useRef, useEffect } from "react";

interface NavItem {
  href: string;
  label: string;
  icon: string;
  show?: boolean;
}

export default function Sidebar() {
  const pathname = usePathname();
  const perm = usePermission();
  const { user, logout } = useAuth(); // Lấy thông tin user và hàm logout

  const [isHovered, setIsHovered] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  // Ref để xử lý click ra ngoài (click outside) đóng menu profile
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
    { href: "/dashboard", label: "Dashboard", icon: "dashboard" },
    { href: "/documents", label: "Documents", icon: "description" },
    {
      href: "/approvals",
      label: "Reviews",
      icon: "rate_review",
      show: perm.canApprove,
    },
    { href: "/chat", label: "AI Chat", icon: "forum" },
    // ... các menu khác
  ];

  const visibleItems = navItems.filter((i) => i.show !== false);

  return (
    <aside
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setIsProfileOpen(false); // Đóng menu nếu thu gọn sidebar
      }}
      className={`hidden md:flex flex-col h-full bg-surface-container-low border-r border-transparent py-4 transition-all duration-300 ease-in-out z-50 overflow-visible ${
        isHovered ? "w-64 px-4" : "w-20 px-2 items-center"
      }`}
    >
      {/* Header: Logo & Title */}
      <div
        className={`flex flex-col space-y-1 ${isHovered ? "px-3" : "items-center"}`}
      >
        {isHovered && (
          <h1 className="text-xl font-black text-on-surface font-headline tracking-tighter whitespace-nowrap">
            Architect SOC
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
                The Workspace
              </p>
              <p className="text-xs text-on-surface-variant">
                Knowledge Curator
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
              title={!isHovered ? item.label : ""}
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
                  {item.label}
                </span>
              )}
            </Link>
          );
        })}
      </nav>
      {/*
      {/* Support & Settings (Bottom Links) */
      /*}
      <div className="pt-6 border-t border-outline-variant/10 space-y-1 w-full mt-auto">
        <Link
          href="#"
          title={!isHovered ? "Support" : ""}
          className={`flex items-center gap-3 text-on-surface-variant rounded-lg transition-all duration-200 ${
            isHovered
              ? "px-3 py-2 hover:bg-surface-container hover:translate-x-1"
              : "justify-center py-2 w-12 h-12 mx-auto hover:bg-surface-container"
          }`}
        >
          <span className="material-symbols-outlined">help_outline</span>
          {isHovered && (
            <span className="font-medium text-sm whitespace-nowrap">
              Support
            </span>
          )}
        </Link>
      </div>
      */}
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
              <span className="font-medium">Hồ sơ</span>
            </Link>
            <Link
              href="/settings"
              className="flex items-center gap-3 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
            >
              <span className="material-symbols-outlined text-neutral-500 text-[20px]">
                settings
              </span>
              <span className="font-medium">Cài đặt</span>
            </Link>
            <div className="h-[1px] bg-neutral-100 my-1 mx-2"></div>
            <Link
              href="/help"
              className="flex items-center gap-3 px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-50 transition-colors"
            >
              <span className="material-symbols-outlined text-neutral-500 text-[20px]">
                help_outline
              </span>
              <span className="font-medium">Trợ giúp</span>
            </Link>
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <span className="material-symbols-outlined text-red-500 text-[20px]">
                logout
              </span>
              <span className="font-medium">Đăng xuất</span>
            </button>
          </div>
        )}

        {/* User Info Trigger */}
        <div
          onClick={() => isHovered && setIsProfileOpen(!isProfileOpen)}
          className={`flex items-center gap-3 py-2 rounded-lg transition-colors ${isHovered ? "px-3 cursor-pointer hover:bg-surface-container" : "justify-center"}`}
          title={!isHovered ? user?.email || "Profile" : ""}
        >
          <div className="w-9 h-9 rounded-full bg-surface-dim overflow-hidden flex-shrink-0">
            {/* Nếu user chưa có avatar, hiển thị ảnh mặc định hoặc chữ cái đầu */}
            <img
              className="w-full h-full object-cover"
              src={
                user?.photoURL ||
                "https://lh3.googleusercontent.com/aida-public/AB6AXuBuyuu8zmjPttIZPT3lGPo8DgSzcg7XZ1dUU2QchCDRKEjAjnQbJ7AwNGG8ODe2_JP_Hnwd_G5Y_dlXw30_-R5iUIo-ehH9KkWb1ugTW6mix2wQ6HEXzvhXMLR6HQoXHd0TpocZjhVwMK7S4vl-2L_pQmMBCB_8pAtQmEX7RDes8OQi9u7N0anfTkx6Olp0dOyHmR3V4u6rl8nYEnIOxTnmFF21C44lWo98Ju4VIhiHhnL-T1e90xB9mcRBTFEKYHV7yUcYcL3B_kD_"
              }
              alt="User avatar"
            />
          </div>
          {isHovered && (
            <div className="min-w-0">
              <p className="text-sm font-bold text-on-surface truncate">
                {user?.displayName || "Người dùng"}
              </p>
              <p className="text-[10px] text-on-surface-variant truncate uppercase">
                {perm.canAdmin ? "QUẢN TRỊ VIÊN" : "USER"}
              </p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
