import React from "react";
import Link from "next/link";

// 1. Định nghĩa kiểu dữ liệu cho một Hoạt động
interface ActivityItem {
  id: string;
  user: string;
  action: string;
  target: string;
  timestamp: string;
  details?: string;
  type: "update" | "approve" | "comment";
}

// 2. Dữ liệu mock giả lập từ Backend trả về
const MOCK_ACTIVITIES: ActivityItem[] = [
  {
    id: "act-1",
    user: "Nguyễn Văn A",
    action: "đã cập nhật",
    target: "Quy trình ISO 2024",
    timestamp: "10 phút trước",
    details: "Chỉnh sửa nội dung mục 4.2 về quản lý rủi ro.",
    type: "update",
  },
  {
    id: "act-2",
    user: "Trần Thị B",
    action: "đã phê duyệt",
    target: "Hướng dẫn Onboarding",
    timestamp: "2 giờ trước",
    type: "approve",
  },
  {
    id: "act-3",
    user: "Lê Văn C",
    action: "đã để lại bình luận",
    target: "Chính sách bảo mật hệ thống", // Tuỳ chọn thêm target vào chuỗi hiển thị
    timestamp: "5 giờ trước",
    details: '"Cần bổ sung thêm ví dụ thực tế cho phần này."',
    type: "comment",
  },
];

export default function ActivityTable() {
  // 3. Hàm phụ trợ để lấy style (icon, màu sắc) tương ứng với từng loại hoạt động
  const getActivityStyle = (type: ActivityItem["type"]) => {
    switch (type) {
      case "update":
        return {
          icon: "edit_note",
          iconColor: "text-tertiary",
          bgColor: "bg-tertiary-container/10",
        };
      case "approve":
        return {
          icon: "verified",
          iconColor: "text-on-secondary-container",
          bgColor: "bg-secondary-container",
        };
      case "comment":
        return {
          icon: "add_comment",
          iconColor: "text-primary-dim",
          bgColor: "bg-surface-container-high",
        };
      default:
        return {
          icon: "notifications",
          iconColor: "text-on-surface-variant",
          bgColor: "bg-surface-container",
        };
    }
  };

  return (
    <div className="xl:col-span-2 bg-surface-container-lowest p-6 rounded-xl">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-bold text-on-surface">Hoạt động gần đây</h2>
        <Link
          href="/dashboard/activities"
          className="text-tertiary text-xs font-bold hover:underline transition-all"
        >
          Xem tất cả
        </Link>
      </div>

      {/* Danh sách Activity */}
      <div className="space-y-4">
        {MOCK_ACTIVITIES.length === 0 ? (
          <p className="text-sm text-on-surface-variant italic text-center py-4">
            Chưa có hoạt động nào gần đây.
          </p>
        ) : (
          MOCK_ACTIVITIES.map((activity) => {
            const style = getActivityStyle(activity.type);

            return (
              <div
                key={activity.id}
                className="flex items-start gap-4 p-3 hover:bg-surface-container-low rounded-lg transition-colors"
              >
                {/* Avatar / Icon */}
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${style.bgColor}`}
                >
                  <span
                    className={`material-symbols-outlined text-[20px] ${style.iconColor}`}
                  >
                    {style.icon}
                  </span>
                </div>

                {/* Nội dung chính */}
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <p className="text-sm font-semibold text-on-surface">
                      {activity.user}{" "}
                      <span className="font-normal text-on-surface-variant">
                        {activity.action}
                      </span>{" "}
                      "{activity.target}"
                    </p>
                    <span className="text-[10px] text-on-surface-variant font-medium whitespace-nowrap ml-2 mt-0.5">
                      {activity.timestamp}
                    </span>
                  </div>

                  {/* Chi tiết bổ sung (Text mô tả hoặc Badge trạng thái) */}
                  {activity.type === "approve" ? (
                    <div className="mt-1 flex gap-2">
                      <span className="bg-on-tertiary-fixed-variant text-[10px] px-2 py-0.5 rounded-full text-tertiary font-bold uppercase tracking-wider border border-tertiary/10">
                        Approved
                      </span>
                    </div>
                  ) : activity.details ? (
                    <p
                      className={`text-xs text-on-surface-variant mt-1 ${activity.type === "comment" ? "italic border-l-2 border-surface-variant pl-2" : ""}`}
                    >
                      {activity.details}
                    </p>
                  ) : null}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
