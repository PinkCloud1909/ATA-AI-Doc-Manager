"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { usePermission } from "@/hooks/usePermission";
import { useState } from "react";

interface NavItem {
  href: string;
  label: string;
  icon: string;
  show?: boolean;
}

export default function Sidebar() {
  const pathname = usePathname();
  const perm = usePermission();

  // State quản lý việc thu gọn/phóng to Sidebar
  const [isHovered, setIsHovered] = useState(false);

  // Cập nhật lại tên icon chuẩn theo Material Symbols
  const navItems: NavItem[] = [
    { href: "/dashboard", label: "Dashboard", icon: "dashboard" },
    { href: "/documents", label: "Tài liệu", icon: "description" },
    {
      href: "/approvals",
      label: "Phê duyệt",
      icon: "rate_review",
      show: perm.canApprove,
    },
    { href: "/chat", label: "Chat AI", icon: "forum" },
    {
      href: "/generate",
      label: "Tạo Runbook",
      icon: "play_circle",
      show: perm.canUpload,
    },
    // { href: "/reports", label: "Báo cáo", icon: "analytics" },
    {
      href: "/admin/users",
      label: "Người dùng",
      icon: "group",
      show: perm.canAdmin,
    },
    {
      href: "/admin/roles",
      label: "Phân quyền",
      icon: "admin_panel_settings",
      show: perm.canAdmin,
    },
  ];

  const visibleItems = navItems.filter((i) => i.show !== false);

  return (
    <aside
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      // Thay đổi độ rộng (w-64 vs w-20) dựa trên state isHovered với hiệu ứng mượt mà
      className={`hidden md:flex flex-col h-full bg-surface-container-low border-r border-transparent p-4 space-y-6 transition-all duration-300 ease-in-out z-50 overflow-hidden ${
        isHovered ? "w-64" : "w-20 items-center"
      }`}
    >
      {/* Header: Logo & Title */}
      <div
        className={`flex items-center gap-3 mb-4 w-full ${isHovered ? "px-2" : "justify-center"}`}
      >
        <div className="w-10 h-10 shrink-0 rounded-xl bg-primary flex items-center justify-center text-on-primary">
          <span className="material-symbols-outlined">architecture</span>
        </div>
        {/* Chỉ hiện chữ khi đang mở rộng (hover) */}
        {isHovered && (
          <div className="whitespace-nowrap transition-opacity duration-300">
            <div className="text-xl font-black text-on-surface tracking-tighter">
              The Workspace
            </div>
            <div className="text-xs text-on-surface-variant">
              KNOWLEDGE CURATOR
            </div>
          </div>
        )}
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 space-y-2 w-full">
        {visibleItems.map((item) => {
          // Kiểm tra xem item hiện tại có đang được active không
          const isActive = pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              title={!isHovered ? item.label : ""} // Hiện tooltip khi đang thu gọn
              className={`flex items-center gap-3 rounded-lg transition-all duration-200 overflow-hidden ${
                isHovered
                  ? "px-3 py-2"
                  : "justify-center py-2 w-10 h-10 mx-auto"
              } ${
                isActive
                  ? "text-tertiary bg-surface-container-lowest shadow-sm border-l-2 border-tertiary"
                  : "text-on-surface-variant hover:bg-surface-container hover:translate-x-1 border-l-2 border-transparent"
              }`}
            >
              <span
                className={`material-symbols-outlined ${isActive ? "font-bold" : ""}`}
              >
                {item.icon}
              </span>
              {isHovered && (
                <span
                  className={`font-medium text-sm whitespace-nowrap ${isActive ? "text-on-surface font-semibold" : ""}`}
                >
                  {item.label}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer Links (Support & Archive) */}
      <div className="mt-auto space-y-2 w-full pt-4 border-t border-outline-variant/10">
        <Link
          href="#"
          title={!isHovered ? "Support" : ""}
          className={`flex items-center gap-3 text-on-surface-variant rounded-lg transition-all duration-200 ${
            isHovered
              ? "px-3 py-2 hover:bg-surface-container hover:translate-x-1"
              : "justify-center py-2 w-10 h-10 mx-auto hover:bg-surface-container"
          }`}
        >
          <span className="material-symbols-outlined">help_outline</span>
          {isHovered && (
            <span className="font-medium text-sm whitespace-nowrap">
              Support
            </span>
          )}
        </Link>
        <Link
          href="#"
          title={!isHovered ? "Archive" : ""}
          className={`flex items-center gap-3 text-on-surface-variant rounded-lg transition-all duration-200 ${
            isHovered
              ? "px-3 py-2 hover:bg-surface-container hover:translate-x-1"
              : "justify-center py-2 w-10 h-10 mx-auto hover:bg-surface-container"
          }`}
        >
          <span className="material-symbols-outlined">archive</span>
          {isHovered && (
            <span className="font-medium text-sm whitespace-nowrap">
              Archive
            </span>
          )}
        </Link>
      </div>
    </aside>
  );
}
