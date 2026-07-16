"use client";

import React, { useState } from "react";
import { useTranslation } from "@/i18n/LanguageContext";

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
  status: string;
  version: string;
  aiAssessment: AIAssessment;
  reviewer?: ReviewerInfo | null;
}

interface DocumentSidebarProps {
  data: DocumentDetailData;
  userRole: "viewer" | "editor" | "approver";
  onApprove?: (grade: number, comment: string) => void;
  onReject?: (grade: number, comment: string) => void;
  isApproving?: boolean;
  isRejecting?: boolean;
}

export default function DocumentSidebar({
  data,
  userRole,
  onApprove,
  onReject,
  isApproving = false,
  isRejecting = false,
}: DocumentSidebarProps) {
  const { t } = useTranslation();
  const [score, setScore] = useState<string>("");
  const [comment, setComment] = useState<string>("");

  const normalizedStatus = data.status.toLowerCase();
  const isDraft =
    normalizedStatus.includes("draft") || normalizedStatus.includes("nháp");
  const isPending =
    normalizedStatus.includes("pending") || normalizedStatus.includes("chờ");
  const isApproved =
    normalizedStatus.includes("approved") || normalizedStatus.includes("duyệt");
  const isRejected =
    normalizedStatus.includes("rejected") || normalizedStatus.includes("từ chối");

  const handleApprove = () => {
    const grade = parseFloat(score) || 0;
    onApprove?.(grade, comment);
  };

  const handleReject = () => {
    const grade = parseFloat(score) || 0;
    onReject?.(grade, comment);
  };

  const statusBadgeClass = isApproved
    ? "bg-[#e6f4ea] text-[#1e4620]"
    : isRejected
      ? "bg-[#fce8e6] text-[#c5221f]"
      : isPending
        ? "bg-[#fef7e0] text-[#b06000]"
        : "bg-tertiary-container text-on-tertiary";

  return (
    <aside className="w-96 flex flex-col gap-6 overflow-y-auto pb-4 pr-2 custom-scrollbar shrink-0">
      {/* 1. Document Info */}
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/15 shrink-0">
        <div className="flex justify-between items-start mb-4">
          <div>
            <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant font-semibold">
              {t.documents.title}
            </span>
            <h3 className="font-headline font-bold text-lg text-on-surface mt-1">
              {data.title}
            </h3>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusBadgeClass}`}>
            {data.status}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div>
            <span className="text-xs text-on-surface-variant block mb-1">ID</span>
            <span className="font-medium text-sm truncate block" title={data.id}>
              {data.id.length > 12 ? `${data.id.slice(0, 8)}...` : data.id}
            </span>
          </div>
          <div>
            <span className="text-xs text-on-surface-variant block mb-1">{t.common.version}</span>
            <span className="font-medium text-sm">{data.version}</span>
          </div>
        </div>
      </div>

      {/* 2. AI / Vectorization Status */}
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/15 shrink-0">
        <div className="flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined text-tertiary" style={{ fontSize: "20px" }}>
            auto_awesome
          </span>
          <h4 className="font-headline font-semibold text-md text-on-surface">
            {t.documents.detail.aiAssessment}
          </h4>
        </div>
        <div className="flex items-center gap-6 mb-6">
          <div className="relative w-16 h-16 flex items-center justify-center rounded-full bg-surface-container-low border-4 border-tertiary shrink-0">
            <span className="font-headline font-bold text-xl text-on-surface">
              {data.aiAssessment.score}
            </span>
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold text-on-surface">{data.aiAssessment.label}</p>
            <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
              {data.aiAssessment.summary}
            </p>
          </div>
        </div>
        {data.aiAssessment.points.length > 0 && (
          <div className="space-y-2">
            {data.aiAssessment.points.map((point, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs">
                <span
                  className={`material-symbols-outlined text-[16px] mt-0.5 ${
                    point.isPositive ? "text-green-600" : "text-amber-600"
                  }`}
                >
                  {point.isPositive ? "check_circle" : "info"}
                </span>
                <span className="text-on-surface-variant">{point.text}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Reviewer feedback */}
      {data.reviewer && (isRejected || isApproved) && (
        <div
          className={`rounded-xl p-6 border shrink-0 ${
            isRejected
              ? "bg-[#fff7f6] border-[#fe8983]/30"
              : "bg-surface-container-lowest border-outline-variant/15"
          }`}
        >
          <h4
            className={`font-headline font-semibold text-sm mb-3 flex items-center gap-2 ${
              isRejected ? "text-[#9f403d]" : "text-on-surface"
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">feedback</span>
            {t.documents.detail.reviewerFeedback}
          </h4>
          <div className="flex items-center gap-3 mb-3">
            {data.reviewer.avatar ? (
              <img
                src={data.reviewer.avatar}
                alt="avatar"
                className="w-8 h-8 rounded-full object-cover"
              />
            ) : (
              <div className="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center text-xs font-bold text-on-secondary-container">
                {data.reviewer.name.charAt(0)}
              </div>
            )}
            <div>
              <p className="text-xs font-bold text-on-surface">{data.reviewer.name}</p>
              <p className="text-[10px] text-on-surface-variant">{data.reviewer.role}</p>
            </div>
            <span
              className={`ml-auto text-[10px] px-2 py-1 rounded font-bold ${
                isRejected
                  ? "bg-[#fe8983]/20 text-[#9f403d]"
                  : "bg-[#e6f4ea] text-[#1e4620]"
              }`}
            >
              {data.reviewer.statusLabel}
            </span>
          </div>
          <p
            className={`text-sm italic border-l-2 pl-3 ${
              isRejected
                ? "text-on-surface border-[#9f403d]/30"
                : "text-on-surface-variant border-outline-variant/30"
            }`}
          >
            &ldquo;{data.reviewer.comment}&rdquo;
          </p>
        </div>
      )}

      {/* 4. Action Area by Role & Status */}
      <div className="mt-auto pt-4 shrink-0 flex flex-col gap-6">
        {/* APPROVER UI */}
        {userRole === "approver" && (
          <>
            {isPending ? (
              <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30 overflow-hidden">
                <div className="bg-surface-container-low px-6 py-3 border-b border-outline-variant/15">
                  <h4 className="font-headline font-semibold text-sm text-on-surface">
                    {t.approvals.title}
                  </h4>
                </div>
                <div className="p-6 space-y-5">
                  <div className="space-y-2">
                    <label
                      className="text-xs font-bold text-on-surface-variant block uppercase tracking-wider"
                      htmlFor="reviewer-score"
                    >
                      Score (0-10)
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
                      {t.documents.detail.rejectReason}
                    </label>
                    <textarea
                      id="review-comments"
                      rows={3}
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder={t.documents.detail.rejectReasonPlaceholder}
                      className="w-full bg-surface-container-low border-none rounded-lg text-sm text-on-surface focus:ring-1 focus:ring-tertiary/30 resize-none custom-scrollbar"
                    />
                  </div>
                  <div className="flex gap-3 pt-2">
                    <button
                      onClick={handleApprove}
                      disabled={isApproving || isRejecting}
                      className="flex-1 bg-[#4caf50] text-white py-2.5 rounded-lg font-medium text-sm hover:opacity-90 flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isApproving ? (
                        <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <span className="material-symbols-outlined text-[18px]">check_circle</span>
                      )}
                      {t.documents.detail.approve}
                    </button>
                    <button
                      onClick={handleReject}
                      disabled={isApproving || isRejecting}
                      className="flex-1 bg-[#f44336] text-white py-2.5 rounded-lg font-medium text-sm hover:opacity-90 flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isRejecting ? (
                        <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <span className="material-symbols-outlined text-[18px]">cancel</span>
                      )}
                      {t.documents.detail.reject}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 bg-surface-container-low rounded-xl border border-surface-variant border-dashed">
                <span className="material-symbols-outlined text-on-surface-variant mb-1" style={{ fontSize: "24px" }}>
                  {isDraft ? "edit_document" : isApproved ? "verified" : "block"}
                </span>
                <p className="text-xs text-on-surface-variant font-medium px-4">
                  {isDraft && t.status.draft}
                  {isApproved && t.status.approved}
                  {isRejected && t.status.rejected}
                </p>
              </div>
            )}
          </>
        )}

        {/* EDITOR UI */}
        {userRole === "editor" && (
          <div className="flex flex-col gap-3">
            {(isDraft || isRejected) && (
              <>
                <button className="w-full bg-tertiary text-on-tertiary py-3 rounded-lg font-semibold text-sm hover:bg-tertiary-dim transition-colors shadow-sm flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">send</span>
                  {t.documents.detail.submitForReview}
                </button>
                <button className="w-full bg-surface-container border border-outline-variant/20 text-on-surface py-3 rounded-lg font-semibold text-sm hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">upload</span>
                  {t.documents.detail.newVersion}
                </button>
              </>
            )}
            {isApproved && (
              <button className="w-full bg-surface-container border border-outline-variant/20 text-on-surface py-3 rounded-lg font-semibold text-sm hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2 shadow-sm">
                <span className="material-symbols-outlined text-[18px]">note_add</span>
                {t.documents.detail.newVersion}
              </button>
            )}
            {isPending && (
              <div className="text-center py-4 bg-surface-container-lowest rounded-xl border border-tertiary/30 bg-tertiary/5">
                <span className="material-symbols-outlined text-tertiary mb-1 animate-pulse" style={{ fontSize: "24px" }}>
                  hourglass_empty
                </span>
                <p className="text-xs text-tertiary font-bold px-4">
                  {t.status.pending_review}
                </p>
              </div>
            )}
          </div>
        )}

        {/* VIEWER UI */}
        {userRole === "viewer" && (
          <div className="text-center py-4 bg-surface-container-low rounded-xl border border-surface-variant border-dashed">
            <span className="material-symbols-outlined text-on-surface-variant mb-1" style={{ fontSize: "24px" }}>
              visibility
            </span>
            <p className="text-xs text-on-surface-variant font-medium">
              Viewer
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
