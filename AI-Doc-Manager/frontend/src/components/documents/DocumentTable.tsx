"use client";

import Link from "next/link";
import {
  DocumentListItem,
  DocumentStatus,
  DocumentType,
} from "@/types/document";
import { StatusBadge } from "./StatusBadge";
/*
const TYPE_LABEL: Record<DocumentType, string> = {
  [DocumentType.TEMPLATE]:          "Template",
  [DocumentType.CUSTOMER_SPECIFIC]: "Khách hàng",
  [DocumentType.COMMON_GUIDE]:      "Hướng dẫn chung",
}

interface Props {
  items:     DocumentListItem[]
  isLoading: boolean
}
*/

// Định nghĩa kiểu dữ liệu cho 1 tài liệu
export interface DocumentItem {
  id: string;
  name: string;
  category: string;
  type: string;
  status: "Approved" | "Pending" | "Draft";
  version: string;
  score: string;
  updatedAt: string;
  author: string;
  icon: string;
  iconColor: string;
  bgColor: string;
}

export default function DocumentTable({
  documents,
}: {
  documents: DocumentItem[];
}) {
  // Hàm phụ trợ để set màu cho Status Badge
  const getStatusStyle = (status: string) => {
    switch (status) {
      case "Approved":
        return "bg-green-50 text-green-700";
      case "Pending":
        return "bg-amber-50 text-amber-700";
      case "Draft":
        return "bg-neutral-100 text-neutral-600";
      default:
        return "bg-neutral-100 text-neutral-600";
    }
  };

  return (
    <div className="bg-surface-container-lowest rounded-2xl overflow-hidden shadow-sm border border-transparent">
      <table className="w-full text-left border-collapse">
        {/* ... (Giữ nguyên thẻ <thead>) ... */}
        <thead>
          <tr className="bg-surface-container-low/50">
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400">
              Tên tài liệu
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400">
              Trạng thái
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400 text-center">
              Version
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400 text-center">
              Điểm số
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400">
              Cập nhật
            </th>
            <th className="px-6 py-4 text-[11px] font-bold uppercase tracking-widest text-neutral-400 text-right">
              Hành động
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-container-low">
          {documents.length === 0 ? (
            <tr>
              <td
                colSpan={6}
                className="px-6 py-10 text-center text-on-surface-variant"
              >
                Không tìm thấy tài liệu nào phù hợp với bộ lọc.
              </td>
            </tr>
          ) : (
            documents.map((doc) => (
              <tr
                key={doc.id}
                className="hover:bg-surface-container-low/30 transition-colors group"
              >
                <td className="px-6 py-5">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-lg ${doc.bgColor} flex items-center justify-center ${doc.iconColor}`}
                    >
                      <span className="material-symbols-outlined">
                        {doc.icon}
                      </span>
                    </div>
                    <div>
                      <p className="font-semibold text-sm text-on-surface">
                        {doc.name}
                      </p>
                      <p className="text-[11px] text-neutral-400">
                        ID: {doc.id} • {doc.category}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <span
                    className={`px-3 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full ${getStatusStyle(doc.status)}`}
                  >
                    {doc.status}
                  </span>
                </td>
                <td className="px-6 py-5 text-center">
                  <span className="text-xs font-mono bg-surface-container-low px-2 py-0.5 rounded">
                    {doc.version}
                  </span>
                </td>
                <td className="px-6 py-5 text-center">
                  <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-surface-container-low rounded-lg">
                    <span className="text-sm font-bold text-on-surface">
                      {doc.score}
                    </span>
                    <div
                      className={`w-1.5 h-1.5 rounded-full ${doc.score === "--" ? "bg-neutral-300" : parseFloat(doc.score) >= 8 ? "bg-green-500" : "bg-amber-500"}`}
                    ></div>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <p className="text-xs text-on-surface">{doc.updatedAt}</p>
                  <p className="text-[10px] text-neutral-400">
                    bởi {doc.author}
                  </p>
                </td>
                <td className="px-6 py-5">
                  {/* ... (Giữ nguyên các nút Action) ... */}
                  <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {/* ĐÃ CHỈNH SỬA TẠI ĐÂY: Thay <button> bằng <Link> */}
                    <Link
                      href={`/documents/${doc.id}`}
                      className="p-2 hover:bg-surface-container-low rounded-lg text-neutral-500 transition-colors inline-flex items-center justify-center"
                      title="Xem"
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        visibility
                      </span>
                    </Link>
                    <button
                      className="p-2 hover:bg-surface-container-low rounded-lg text-neutral-500 transition-colors"
                      title="So sánh"
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        compare_arrows
                      </span>
                    </button>
                    <button
                      className="p-2 hover:bg-surface-container-low rounded-lg text-neutral-500 transition-colors"
                      title="Tạo Runbook"
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        play_circle
                      </span>
                    </button>
                    <button
                      className="p-2 hover:bg-surface-container-low rounded-lg text-neutral-500 transition-colors"
                      title="Chấm điểm"
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        grade
                      </span>
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      {/* ... (Giữ nguyên phần Pagination Area) ... */}
      <div className="px-6 py-4 flex items-center justify-between border-t border-surface-container-low bg-white">
        <p className="text-xs text-neutral-500 font-medium">
          Hiển thị 1-4 trên 24 tài liệu
        </p>
        <div className="flex items-center gap-2">
          <button
            className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-400 hover:bg-neutral-50 transition-colors disabled:opacity-50"
            disabled
          >
            <span className="material-symbols-outlined text-[18px]">
              chevron_left
            </span>
          </button>
          <button className="w-8 h-8 rounded-lg flex items-center justify-center bg-tertiary text-on-tertiary text-xs font-bold">
            1
          </button>
          <button className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-500 hover:bg-neutral-50 transition-colors text-xs font-bold">
            2
          </button>
          <button className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-500 hover:bg-neutral-50 transition-colors text-xs font-bold">
            3
          </button>
          <button className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-400 hover:bg-neutral-50 transition-colors">
            <span className="material-symbols-outlined text-[18px]">
              chevron_right
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
