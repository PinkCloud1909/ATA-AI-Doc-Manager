"use client";

import React, { useState } from "react";
import { usePermission } from "@/hooks/usePermission";

// 1. DỮ LIỆU MOCK
const RAW_DATA = {
  approved: 856,
  pending: 142,
  draft: 120,
  expired: 82,
};

// Hàm phụ trợ tính toán đường dẫn SVG cho từng lát cắt của Pie Chart
function createPieSlices(
  data: { label: string; value: number; color: string }[],
) {
  let cumulativePercent = 0;
  const total = data.reduce((sum, item) => sum + item.value, 0);

  return data.map((slice) => {
    const percent = slice.value / total;
    // Góc bắt đầu và kết thúc (Tính bằng Radian, bắt đầu từ đỉnh -90 độ)
    const startAngle = cumulativePercent * 2 * Math.PI - Math.PI / 2;
    cumulativePercent += percent;
    const endAngle = cumulativePercent * 2 * Math.PI - Math.PI / 2;

    // Tọa độ tâm và bán kính
    const cx = 100,
      cy = 100,
      r = 100;

    // Tọa độ vẽ đường cung
    const startX = cx + r * Math.cos(startAngle);
    const startY = cy + r * Math.sin(startAngle);
    const endX = cx + r * Math.cos(endAngle);
    const endY = cy + r * Math.sin(endAngle);

    // Cờ xác định vẽ cung lớn hay nhỏ (nếu > 50% thì = 1)
    const largeArcFlag = percent > 0.5 ? 1 : 0;

    // Đường dẫn SVG
    const pathData =
      percent === 1
        ? "" // Xử lý riêng nếu 1 lát cắt chiếm 100%
        : [
            `M ${cx} ${cy}`,
            `L ${startX} ${startY}`,
            `A ${r} ${r} 0 ${largeArcFlag} 1 ${endX} ${endY}`,
            "Z",
          ].join(" ");

    // Tọa độ đặt Text (Phần trăm) ở giữa lát cắt (nhân 0.65 để chữ nằm dịch vào trong)
    const midAngle = startAngle + (endAngle - startAngle) / 2;
    const textX = cx + r * 0.65 * Math.cos(midAngle);
    const textY = cy + r * 0.65 * Math.sin(midAngle);

    return { ...slice, pathData, textX, textY, percent, total };
  });
}

export default function SummaryCards() {
  const perm = usePermission();

  // Xác định Role (Giả định dựa trên quyền hạn)
  const role = perm.canApprove
    ? "approver"
    : perm.canUpload
      ? "editor"
      : "viewer";

  // 2. CHUẨN BỊ DỮ LIỆU DỰA TRÊN ROLE
  const chartData =
    role === "viewer"
      ? [
          { label: "Approved", value: RAW_DATA.approved, color: "#0053dc" }, // Tertiary
          {
            label: "Other",
            value: RAW_DATA.pending + RAW_DATA.draft + RAW_DATA.expired,
            color: "#9ca3af",
          }, // Slate-400
        ]
      : [
          { label: "Approved", value: RAW_DATA.approved, color: "#0053dc" }, // Tertiary
          { label: "Pending", value: RAW_DATA.pending, color: "#f59e0b" }, // Amber-500
          { label: "Draft", value: RAW_DATA.draft, color: "#9ca3af" }, // Slate-400
          { label: "Expired", value: RAW_DATA.expired, color: "#ef4444" }, // Red-500
        ];

  // Loại bỏ các lát cắt có value = 0 để biểu đồ không bị lỗi hiển thị
  const filteredData = chartData.filter((d) => d.value > 0);
  const slices = createPieSlices(filteredData);
  const totalDocs = filteredData.reduce((sum, item) => sum + item.value, 0);

  // 3. STATE CHO TOOLTIP
  const [tooltip, setTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    label: string;
    value: number;
    percent: number;
  }>({
    visible: false,
    x: 0,
    y: 0,
    label: "",
    value: 0,
    percent: 0,
  });

  const handleMouseMove = (e: React.MouseEvent, slice: any) => {
    // Tính toán vị trí chuột so với viewport để đặt tooltip
    setTooltip({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      label: slice.label,
      value: slice.value,
      percent: slice.percent,
    });
  };

  const handleMouseLeave = () => setTooltip({ ...tooltip, visible: false });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative">
      {/* TOOLTIP NỔI */}
      {tooltip.visible && (
        <div
          className="fixed z-50 bg-inverse-surface text-on-tertiary-fixed px-3 py-2 rounded-lg shadow-xl text-sm font-medium pointer-events-none transform -translate-x-1/2 -translate-y-full mt-[-10px]"
          style={{ left: tooltip.x, top: tooltip.y }}
        >
          <div className="flex flex-col items-center">
            <span className="font-bold opacity-80 uppercase tracking-widest text-[10px]">
              {tooltip.label}
            </span>
            <span>{tooltip.value} tài liệu</span>
          </div>
          {/* Mũi tên chỉ xuống của tooltip */}
          <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-inverse-surface"></div>
        </div>
      )}

      {/* KHỐI 1 & 2: BIỂU ĐỒ VÀ CHÚ THÍCH */}
      <div className="lg:col-span-2 bg-surface-container-lowest p-6 lg:p-8 rounded-xl border border-outline-variant/15 shadow-sm flex flex-col sm:flex-row items-center gap-10">
        {/* SVG PIE CHART */}
        <div className="relative w-48 h-48 shrink-0 drop-shadow-sm hover:drop-shadow-md transition-shadow">
          <svg
            viewBox="0 0 200 200"
            className="w-full h-full rounded-full transform hover:scale-105 transition-transform duration-300"
          >
            {slices.length === 1 ? (
              // Nếu chỉ có 1 data (100%), vẽ nguyên hình tròn
              <circle
                cx="100"
                cy="100"
                r="100"
                fill={slices[0].color}
                onMouseMove={(e) => handleMouseMove(e, slices[0])}
                onMouseLeave={handleMouseLeave}
              />
            ) : (
              // Vẽ các lát cắt
              slices.map((slice, index) => (
                <g
                  key={index}
                  className="hover:opacity-90 transition-opacity cursor-pointer"
                >
                  <path
                    d={slice.pathData}
                    fill={slice.color}
                    stroke="#ffffff" // Viền trắng phân cách các lát cắt
                    strokeWidth="1.5"
                    onMouseMove={(e) => handleMouseMove(e, slice)}
                    onMouseLeave={handleMouseLeave}
                  />
                  {/* Hiển thị phần trăm > 5% mới in chữ để tránh bị chèn ép */}
                  {slice.percent > 0.05 && (
                    <text
                      x={slice.textX}
                      y={slice.textY}
                      fill="#ffffff"
                      fontSize="14"
                      fontWeight="bold"
                      fontFamily="Inter"
                      textAnchor="middle"
                      alignmentBaseline="middle"
                      className="pointer-events-none"
                    >
                      {Math.round(slice.percent * 100)}%
                    </text>
                  )}
                </g>
              ))
            )}
          </svg>
        </div>

        {/* CHÚ THÍCH (LEGEND) VÀ THỐNG KÊ */}
        <div className="flex-1 w-full space-y-5">
          <div>
            <h3 className="text-xl font-bold text-on-surface tracking-tight">
              Tổng quan trạng thái
            </h3>
            <p className="text-sm text-on-surface-variant mt-0.5">
              Tổng cộng có <strong>{totalDocs}</strong> tài liệu trong hệ thống.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {filteredData.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-surface-container-low transition-colors border border-transparent hover:border-outline-variant/10"
              >
                <div
                  className="w-4 h-4 rounded-full shrink-0 shadow-sm"
                  style={{ backgroundColor: item.color }}
                ></div>
                <div>
                  <p className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">
                    {item.label}
                  </p>
                  <p className="text-lg font-extrabold text-on-surface">
                    {item.value}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* KHỐI 3: NHẮC VIỆC KHẨN CẤP */}
      <div className="bg-surface-container-lowest p-6 lg:p-8 rounded-xl border border-outline-variant/15 shadow-sm flex flex-col justify-between group hover:border-error/30 transition-colors relative overflow-hidden">
        <div className="absolute -right-6 -top-6 w-32 h-32 bg-error/5 rounded-full blur-3xl group-hover:bg-error/10 transition-colors"></div>

        <div>
          <div className="w-12 h-12 rounded-full bg-error-container flex items-center justify-center text-error mb-5">
            <span className="material-symbols-outlined text-[24px]">
              priority_high
            </span>
          </div>
          <h3 className="text-lg font-bold text-on-surface mb-2">
            Cần xử lý ngay
          </h3>
          <p className="text-sm text-on-surface-variant leading-relaxed">
            Hệ thống phát hiện{" "}
            <strong className="text-error">12 tài liệu Pending</strong> đang bị
            quá hạn phê duyệt. Cần kiểm tra để tránh tắc nghẽn luồng dữ liệu.
          </p>
        </div>

        {/* Nút này chỉ hiện hữu ích nếu là Editor/Approver, nhưng ta cứ giữ hiển thị chung */}
        <button className="w-full mt-6 py-3 rounded-lg bg-surface-container text-on-surface font-semibold text-sm hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2">
          Chuyển đến hàng đợi
          <span className="material-symbols-outlined text-[18px]">
            arrow_forward
          </span>
        </button>
      </div>
    </div>
  );
}
