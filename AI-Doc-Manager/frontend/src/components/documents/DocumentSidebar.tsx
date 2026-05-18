"use client";

import React, { useState } from "react";

interface AIAssessment {
  score: string;
  label: string;
  summary: string;
  points: { isPositive: boolean; text: string }[];
}

interface ReviewerInfo {
  name: string;
  role: string;
  avatar: string;
  comment: string;
  statusLabel: string;
}

export interface DocumentDetailData {
  id: string;
  title: string;
  status: string; // "Draft" | "Pending" | "Approved" | "Rejected"
  version: string;
  aiAssessment: AIAssessment;
  reviewer?: ReviewerInfo | null;
}

interface DocumentSidebarProps {
  data: DocumentDetailData;
  userRole: "viewer" | "editor" | "approver";
}

export default function DocumentSidebar({
  data,
  userRole,
}: DocumentSidebarProps) {
  const [score, setScore] = useState<string>("");
  const [comment, setComment] = useState<string>("");

  // Chuẩn hóa trạng thái để làm logic (Giả sử BE trả về các keyword này)
  const normalizedStatus = data.status.toLowerCase();
  const isDraft =
    normalizedStatus.includes("nháp") || normalizedStatus.includes("draft");
  const isPending =
    normalizedStatus.includes("chờ") || normalizedStatus.includes("pending");
  const isApproved =
    normalizedStatus.includes("đã duyệt") ||
    normalizedStatus.includes("approved");
  const isRejected =
    normalizedStatus.includes("từ chối") ||
    normalizedStatus.includes("rejected");

  const handleApprove = () => {
    console.log("Approve", { score, comment });
  };

  const handleReject = () => {
    console.log("Reject", { score, comment });
  };

  return (
    <aside className="w-96 flex flex-col gap-6 overflow-y-auto pb-4 pr-2 custom-scrollbar shrink-0">
      {/* 1. THÔNG TIN TÀI LIỆU */}
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/15 shrink-0">
        <div className="flex justify-between items-start mb-4">
          <div>
            <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant font-semibold">
              Tài Liệu
            </span>
            <h3 className="font-headline font-bold text-lg text-on-surface mt-1">
              {data.title}
            </h3>
          </div>
          {/* Đổi màu Badge theo trạng thái */}
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              isApproved
                ? "bg-[#e6f4ea] text-[#1e4620]"
                : isRejected
                  ? "bg-[#fce8e6] text-[#c5221f]"
                  : isPending
                    ? "bg-[#fef7e0] text-[#b06000]"
                    : "bg-tertiary-container text-on-tertiary"
            }`}
          >
            {data.status}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div>
            <span className="text-xs text-on-surface-variant block mb-1">
              Mã Số
            </span>
            <span className="font-medium text-sm">{data.id}</span>
          </div>
          <div>
            <span className="text-xs text-on-surface-variant block mb-1">
              Phiên Bản
            </span>
            <span className="font-medium text-sm">{data.version}</span>
          </div>
        </div>
      </div>

      {/* 2. ĐÁNH GIÁ AI */}
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/15 shrink-0">
        <div className="flex items-center gap-2 mb-4">
          <span
            className="material-symbols-outlined text-tertiary"
            style={{ fontSize: "20px" }}
          >
            auto_awesome
          </span>
          <h4 className="font-headline font-semibold text-md text-on-surface">
            Đánh Giá AI
          </h4>
        </div>
        <div className="flex items-center gap-6 mb-6">
          <div className="relative w-16 h-16 flex items-center justify-center rounded-full bg-surface-container-low border-4 border-tertiary shrink-0">
            <span className="font-headline font-bold text-xl text-on-surface">
              {data.aiAssessment.score}
            </span>
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold text-on-surface">
              {data.aiAssessment.label}
            </p>
            <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
              {data.aiAssessment.summary}
            </p>
          </div>
        </div>
      </div>

      {/* 3. LỊCH SỬ NHẬN XÉT (Hiển thị nếu bị từ chối hoặc đã duyệt có comment) */}
      {data.reviewer && (isRejected || isApproved) && (
        <div
          className={`rounded-xl p-6 border shrink-0 ${isRejected ? "bg-[#fff7f6] border-[#fe8983]/30" : "bg-surface-container-lowest border-outline-variant/15"}`}
        >
          <h4
            className={`font-headline font-semibold text-sm mb-3 flex items-center gap-2 ${isRejected ? "text-[#9f403d]" : "text-on-surface"}`}
          >
            <span className="material-symbols-outlined text-[18px]">
              feedback
            </span>
            Phản hồi từ người duyệt
          </h4>
          <div className="flex items-center gap-3 mb-3">
            <img
              src={data.reviewer.avatar}
              alt="avatar"
              className="w-8 h-8 rounded-full object-cover"
            />
            <div>
              <p className="text-xs font-bold text-on-surface">
                {data.reviewer.name}
              </p>
              <p className="text-[10px] text-on-surface-variant">
                {data.reviewer.role}
              </p>
            </div>
            <span
              className={`ml-auto text-[10px] px-2 py-1 rounded font-bold ${isRejected ? "bg-[#fe8983]/20 text-[#9f403d]" : "bg-[#e6f4ea] text-[#1e4620]"}`}
            >
              {data.reviewer.statusLabel}
            </span>
          </div>
          <p
            className={`text-sm italic border-l-2 pl-3 ${isRejected ? "text-on-surface border-[#9f403d]/30" : "text-on-surface-variant border-outline-variant/30"}`}
          >
            "{data.reviewer.comment}"
          </p>
        </div>
      )}

      {/* 4. KHU VỰC HÀNH ĐỘNG THEO ROLE & STATUS */}
      <div className="mt-auto pt-4 shrink-0 flex flex-col gap-6">
        {/* === GIAO DIỆN APPROVER === */}
        {userRole === "approver" && (
          <>
            {isPending ? (
              // Trạng thái Pending: Hiện Form chấm điểm & Duyệt
              <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30 overflow-hidden">
                <div className="bg-surface-container-low px-6 py-3 border-b border-outline-variant/15">
                  <h4 className="font-headline font-semibold text-sm text-on-surface">
                    Khu Vực Phê Duyệt
                  </h4>
                </div>
                <div className="p-6 space-y-5">
                  <div className="space-y-2">
                    <label
                      className="text-xs font-bold text-on-surface-variant block uppercase tracking-wider"
                      htmlFor="reviewer-score"
                    >
                      Điểm số (0-10)
                    </label>
                    <input
                      id="reviewer-score"
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      placeholder="0.0"
                      value={score}
                      onChange={(e) => setScore(e.target.value)}
                      className="w-24 bg-surface-container-low border-none rounded-lg text-sm font-bold text-tertiary focus:ring-1 focus:ring-tertiary/30 px-3 py-2 text-center"
                    />
                  </div>
                  <div className="space-y-2">
                    <label
                      className="text-xs font-bold text-on-surface-variant block uppercase tracking-wider"
                      htmlFor="review-comments"
                    >
                      Nhận xét / Yêu cầu sửa
                    </label>
                    <textarea
                      id="review-comments"
                      rows={3}
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Nhập nhận xét..."
                      className="w-full bg-surface-container-low border-none rounded-lg text-sm text-on-surface focus:ring-1 focus:ring-tertiary/30 resize-none custom-scrollbar"
                    />
                  </div>
                  <div className="flex gap-3 pt-2">
                    <button
                      onClick={handleApprove}
                      className="flex-1 bg-[#4caf50] text-white py-2.5 rounded-lg font-medium text-sm hover:opacity-90 flex items-center justify-center gap-2 shadow-sm"
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        check_circle
                      </span>{" "}
                      Duyệt
                    </button>
                    <button
                      onClick={handleReject}
                      className="flex-1 bg-[#f44336] text-white py-2.5 rounded-lg font-medium text-sm hover:opacity-90 flex items-center justify-center gap-2 shadow-sm"
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        cancel
                      </span>{" "}
                      Từ chối
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              // Trạng thái khác: Không có form duyệt, chỉ báo trạng thái
              <div className="text-center py-4 bg-surface-container-low rounded-xl border border-surface-variant border-dashed">
                <span
                  className="material-symbols-outlined text-on-surface-variant mb-1"
                  style={{ fontSize: "24px" }}
                >
                  {isDraft
                    ? "edit_document"
                    : isApproved
                      ? "verified"
                      : "block"}
                </span>
                <p className="text-xs text-on-surface-variant font-medium px-4">
                  {isDraft &&
                    "Tài liệu đang ở dạng nháp. Chưa có yêu cầu phê duyệt."}
                  {isApproved && "Tài liệu này đã được phê duyệt."}
                  {isRejected &&
                    "Tài liệu đã bị từ chối. Đang chờ Editor cập nhật bản mới."}
                </p>
              </div>
            )}
          </>
        )}

        {/* === GIAO DIỆN EDITOR === */}
        {userRole === "editor" && (
          <div className="flex flex-col gap-3">
            {(isDraft || isRejected) && (
              <>
                <button className="w-full bg-tertiary text-on-tertiary py-3 rounded-lg font-semibold text-sm hover:bg-tertiary-dim transition-colors shadow-sm flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">
                    send
                  </span>
                  Gửi Yêu Cầu Phê Duyệt
                </button>
                <button className="w-full bg-surface-container border border-outline-variant/20 text-on-surface py-3 rounded-lg font-semibold text-sm hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">
                    upload
                  </span>
                  Tải Lên Bản Chỉnh Sửa
                </button>
              </>
            )}

            {isApproved && (
              <button className="w-full bg-surface-container border border-outline-variant/20 text-on-surface py-3 rounded-lg font-semibold text-sm hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2 shadow-sm">
                <span className="material-symbols-outlined text-[18px]">
                  note_add
                </span>
                Tạo Phiên Bản Mới (Draft)
              </button>
            )}

            {isPending && (
              <div className="text-center py-4 bg-surface-container-lowest rounded-xl border border-tertiary/30 bg-tertiary/5">
                <span
                  className="material-symbols-outlined text-tertiary mb-1 animate-pulse"
                  style={{ fontSize: "24px" }}
                >
                  hourglass_empty
                </span>
                <p className="text-xs text-tertiary font-bold px-4">
                  Tài liệu đang chờ phê duyệt. Không thể chỉnh sửa lúc này.
                </p>
              </div>
            )}
          </div>
        )}

        {/* === GIAO DIỆN VIEWER === */}
        {userRole === "viewer" && (
          <div className="text-center py-4 bg-surface-container-low rounded-xl border border-surface-variant border-dashed">
            <span
              className="material-symbols-outlined text-on-surface-variant mb-1"
              style={{ fontSize: "24px" }}
            >
              visibility
            </span>
            <p className="text-xs text-on-surface-variant font-medium">
              Bạn đang xem với quyền Viewer.
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
