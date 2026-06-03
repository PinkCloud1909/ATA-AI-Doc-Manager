"use client";

import SummaryCards from "@/components/reports/SummaryCards";
import StatusChart from "@/components/reports/StatusChart";
import ActivityTable from "@/components/reports/ActivityTable";
// Import AiCuratorCard nếu bạn có component này
import AiCuratorCard from "@/components/reports/AiCuratorCard";

export default function DashboardPage() {
  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 min-w-0">
      {/* Header Dashboard */}
      <div>
        <h1 className="text-3xl font-extrabold text-on-surface tracking-tight">
          Dashboard
        </h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Tổng quan hệ thống quản lý tài liệu tri thức
        </p>
      </div>

      {/* Khối Pie Chart và Thống kê nhanh */}
      <SummaryCards />

      {/* Khối Biểu đồ cột */}
      <StatusChart />

      {/* Khối Hoạt động & AI Insights ở dưới cùng */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <ActivityTable />
        <AiCuratorCard />
      </div>
    </div>
  );
}
