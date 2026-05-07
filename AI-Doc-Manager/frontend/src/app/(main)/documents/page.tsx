"use client";
import { useState } from "react";
import Link from "next/link";
import { useDocumentList } from "@/hooks/useDocuments";
//import { DocumentTable } from "@/components/documents/DocumentTable"
import { DocumentStatus, DocumentType } from "@/types/document";
import { usePermission } from "@/hooks/usePermission";

import UploadForm from "@/components/documents/UploadForm";
import DocumentFilters from "@/components/documents/DocumentFilters";
import DocumentStats from "@/components/documents/DocumentStats";

// Bắt buộc phải có dòng này vì ta dùng useState (Client Component)
import DocumentTable, {
  DocumentItem,
} from "@/components/documents/DocumentTable";

// Dữ liệu mẫu (Mock Data) giả lập việc gọi API
const mockData: DocumentItem[] = [
  {
    id: "DOC-2024-001",
    name: "Incident Response Plan v4",
    category: "Cyber Security",
    type: "Runbook",
    status: "Approved",
    version: "4.2.1",
    score: "9.5",
    updatedAt: "Hôm nay, 14:20",
    author: "Hoàng Nguyễn",
    icon: "description",
    bgColor: "bg-red-50",
    iconColor: "text-red-600",
  },
  {
    id: "DOC-2024-042",
    name: "Cloud Architecture Guideline",
    category: "Infrastructure",
    type: "SOP",
    status: "Pending",
    version: "1.0.5",
    score: "7.2",
    updatedAt: "Hôm qua, 09:15",
    author: "Minh Tú",
    icon: "menu_book",
    bgColor: "bg-blue-50",
    iconColor: "text-blue-600",
  },
  {
    id: "DOC-2024-058",
    name: "Monthly Security Audit Report",
    category: "Compliance",
    type: "SOP",
    status: "Draft",
    version: "0.9.0",
    score: "--",
    updatedAt: "12 Th04, 2024",
    author: "Alex Trần",
    icon: "edit_document",
    bgColor: "bg-neutral-100",
    iconColor: "text-neutral-600",
  },
  {
    id: "DOC-2024-012",
    name: "Data Privacy Policy 2024",
    category: "Legal",
    type: "Policy",
    status: "Approved",
    version: "2.1.0",
    score: "8.8",
    updatedAt: "08 Th04, 2024",
    author: "Minh Tú",
    icon: "policy",
    bgColor: "bg-green-50",
    iconColor: "text-green-600",
  },
];

export default function DocumentsPage() {
  // 1. Khai báo State cho các bộ lọc
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("Tất cả");
  const [typeFilter, setTypeFilter] = useState("Tất cả");

  // 2. Logic Lọc dữ liệu (Real-time)
  const filteredDocs = mockData.filter((doc) => {
    // Ép về chữ thường để tìm kiếm không phân biệt hoa thường
    const matchesSearch =
      doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.id.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "Tất cả" || doc.status === statusFilter;
    const matchesType = typeFilter === "Tất cả" || doc.type === typeFilter;

    // Phải thỏa mãn CẢ 3 điều kiện mới được hiển thị
    return matchesSearch && matchesStatus && matchesType;
  });

  //3. State quản lý việc mở/đóng Modal Upload
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* ... (Giữ nguyên phần Page Header có nút Tải lên) ... */}
        {/* Page Header */}
        <div className="flex justify-between items-end">
          <div className="space-y-1">
            <h2 className="text-3xl font-extrabold tracking-tight text-on-surface">
              Quản lý tài liệu
            </h2>
            <p className="text-on-surface-variant text-sm">
              Trung tâm lưu trữ và kiểm duyệt tri thức hệ thống Architect SOC.
            </p>
          </div>
          <div className="flex justify-between items-end">
            {/* ... */}
            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 transition-colors rounded-lg text-sm font-medium text-white"
            >
              <span className="material-symbols-outlined text-sm">
                upload_file
              </span>
              Tải lên
            </button>
          </div>
        </div>

        {/* Truyền State và hàm SetState xuống cho Filter */}
        <DocumentFilters
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
          typeFilter={typeFilter}
          setTypeFilter={setTypeFilter}
        />

        {/* Truyền danh sách ĐÃ ĐƯỢC LỌC xuống cho Table */}
        <DocumentTable documents={filteredDocs} />

        <DocumentStats />
      </div>
      {/* Hiển thị Modal Upload */}
      {isUploadModalOpen && (
        <UploadForm onClose={() => setIsUploadModalOpen(false)} />
      )}
    </div>
  );
}
