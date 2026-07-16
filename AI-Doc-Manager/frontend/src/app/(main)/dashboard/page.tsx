"use client";

import { useTranslation } from "@/i18n/LanguageContext";
import SummaryCards from "@/components/dashboard/SummaryCards";
import StatusChart from "@/components/dashboard/StatusChart";
import ActivityTable from "@/components/dashboard/ActivityTable";
// Import AiCuratorCard nếu bạn có component này
import AiCuratorCard from "@/components/dashboard/AiCuratorCard";

export default function DashboardPage() {
  const { t } = useTranslation();
  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 min-w-0">
      {/* Header Dashboard */}
      <div>
        <h1 className="text-3xl font-extrabold text-on-surface tracking-tight">
          {t.dashboard.title}
        </h1>
        <p className="text-sm text-on-surface-variant mt-1">
          {t.dashboard.subtitle}
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
