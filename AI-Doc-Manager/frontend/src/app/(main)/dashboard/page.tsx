"use client";

import { useQuery } from "@tanstack/react-query";
import { reportsApi, ReportSummary } from "@/lib/api/reports";
import Link from "next/link";
/*
const STAT_CARDS = (s: ReportSummary) => [
  { label: "Tổng tài liệu",  value: s.total,          color: "text-slate-700",   bg: "bg-slate-100", border: "border-slate-200" },
  { label: "Đã phê duyệt",   value: s.approved,        color: "text-emerald-700", bg: "bg-emerald-50", border: "border-emerald-100" },
  { label: "Chờ duyệt",      value: s.pending_review,  color: "text-amber-700",   bg: "bg-amber-50",   border: "border-amber-100" },
  { label: "Từ chối",        value: s.rejected,         color: "text-red-600",     bg: "bg-red-50",     border: "border-red-100" },
]

export default function DashboardPage() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ["reports", "summary"],
    queryFn:  reportsApi.getSummary,
  })

  const { data: activity } = useQuery({
    queryKey: ["reports", "activity"],
    queryFn:  () => reportsApi.getActivity(10),
  })

  return (
    <div className="space-y-6 min-w-0">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">Tổng quan hệ thống quản lý tài liệu</p>
      </div>

      {/* Summary cards /}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 min-w-0">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 bg-slate-100 rounded-xl animate-pulse" />
            ))
          : summary && STAT_CARDS(summary).map((card) => (
              <div key={card.label} className={`rounded-xl p-5 border ${card.bg} ${card.border} shadow-sm min-w-0`}>
                <p className="text-xs font-medium text-slate-500">{card.label}</p>
                <p className={`text-3xl font-bold mt-1 ${card.color}`}>{card.value}</p>
              </div>
            ))}
      </div>

      {/* Quick links /}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { href: "/documents/upload", label: "Upload tài liệu",   icon: "⬆" },
          { href: "/chat",             label: "Chat với AI",        icon: "◎" },
          { href: "/generate",         label: "Tạo Runbook bằng AI", icon: "✦" },
          { href: "/approvals",        label: "Phê duyệt",          icon: "✓" },
          { href: "/documents",        label: "Xem tài liệu",        icon: "◻" },
          { href: "/reports",          label: "Báo cáo",             icon: "▦" },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 p-4 bg-white rounded-xl border border-slate-200
                       hover:border-blue-300 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 group"
          >
            <span className="text-2xl">{item.icon}</span>
            <span className="text-sm font-medium text-slate-700 group-hover:text-blue-600 transition-colors">
              {item.label}
            </span>
          </Link>
        ))}
      </div>

      {/* Recent activity /}
      {activity && activity.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-700">Hoạt động gần đây</h2>
          </div>
          <ul className="divide-y divide-slate-100">
            {activity.map((item, i) => (
              <li key={i} className="flex items-center justify-between px-5 py-3 hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-slate-700">{item.user}</span>
                  <span className="text-sm text-slate-400">{item.action}</span>
                </div>
                <span className="text-xs text-slate-400">
                  {new Date(item.timestamp).toLocaleString("vi-VN")}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
*/
/* stitch*/
import SummaryCards from "@/components/reports/SummaryCards";
import StatusChart from "@/components/reports/StatusChart";
import ActivityTable from "@/components/reports/ActivityTable";
import AiCuratorCard from "@/components/reports/AiCuratorCard"; // Nếu bạn tạo file này

export default function DashboardPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Overview Stats Grid */}
      <SummaryCards />

      {/* Charts Section */}
      <StatusChart />

      {/* Recent Activity & Featured Knowledge */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <ActivityTable />
        <AiCuratorCard />
      </div>
    </div>
  );
}
