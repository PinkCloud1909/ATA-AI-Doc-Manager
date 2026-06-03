import DocumentPreview from "@/components/documents/DocumentPreview";
import DocumentSidebar, {
  DocumentDetailData,
} from "@/components/documents/DocumentSidebar";
import React from "react";
// Import hook kiểm tra quyền của bạn
// import { usePermission } from "@/hooks/usePermission";

// === DỮ LIỆU MOCK THEO TỪNG ID TÀI LIỆU ===

const MOCK_DOCUMENTS: Record<
  string,
  { preview: any; sidebar: DocumentDetailData }
> = {
  "DOC-2024-001": {
    preview: {
      title: "Kế Hoạch Ứng Phó Sự Cố v4",

      description:
        "Tài liệu này trình bày các quy trình tiêu chuẩn để xử lý các sự cố an ninh mạng trong tổ chức.",

      content: (
        <>
          <h2 className="text-2xl font-headline font-semibold mt-8 mb-4">
            1. Mục Đích
          </h2>

          <p>
            Cung cấp khuôn khổ có cấu trúc và có hệ thống để phát hiện, phân
            tích, ngăn chặn sự cố an ninh mạng.
          </p>

          <div className="bg-surface-container-low p-6 rounded-lg my-6 border-l-4 border-tertiary">
            <h3 className="font-headline font-semibold text-lg mb-2">
              Lưu ý Quan Trọng
            </h3>

            <p className="text-sm text-on-surface-variant">
              Liên hệ ngay với Trưởng nhóm SOC qua số khẩn cấp nội bộ khi có sự
              cố P1.
            </p>
          </div>
        </>
      ),
    },

    sidebar: {
      id: "DOC-2024-001",

      title: "Kế Hoạch Ứng Phó Sự Cố",

      status: "Approved",

      version: "v4.2.1",

      aiAssessment: {
        score: "8.5",

        label: "Khá Tốt",

        summary: "Cấu trúc rõ ràng, cần bổ sung chi tiết về phần phục hồi.",

        points: [
          {
            isPositive: true,

            text: "Phần 'Phạm Vi' được định nghĩa rất rõ ràng.",
          },

          {
            isPositive: false,

            text: "Cần chỉ định rõ thời gian cho bước 'Phục Hồi'.",
          },
        ],
      },

      reviewer: {
        name: "Trần Văn A",

        role: "Quản lý SOC",

        avatar:
          "https://lh3.googleusercontent.com/aida-public/AB6AXuA2hOD2ai6ZAcHaRwwVMTFaZe4-ihmKeOTfmGE8eNUcW3jwr7MUOy6mvsXmA_kaKNClwhR0d7f1W3kVC3M-1twZfS2wIKgkB5_D0UKxoAvqXYETbrPu1L-4hdKiM3wVS3S9Juc7Oxd6XF57XT5_njBbmGdsvXC3-mTc1z_N18HT0ejboaPJQ60mqZ4MxYuzkYo0ep7H-kPpYGwv-Ar-Ktk1Xo_T-MSGDy7rXTcwbKXz4cruGtgAhJgfVnuH_x881xRVCtXbUnRpzhmi",

        comment:
          "Vui lòng cập nhật số điện thoại khẩn cấp. Nó đã thay đổi vào tháng trước.",

        statusLabel: "Chờ Chỉnh Sửa",
      },
    },
  },

  "DOC-2024-042": {
    preview: {
      title: "Cloud Architecture Guideline",

      description: "Tiêu chuẩn thiết kế hạ tầng Cloud cho các dự án nội bộ.",

      content: (
        <>
          <h2 className="text-2xl font-headline font-semibold mt-8 mb-4">
            1. Kiến Trúc Mạng
          </h2>

          <p>
            Tất cả các dịch vụ nội bộ phải được đặt trong Private Subnet và giao
            tiếp qua VPC Peering.
          </p>

          <ul className="list-disc pl-6 space-y-2 mt-4">
            <li>Không mở public IP cho Database.</li>

            <li>Sử dụng NAT Gateway cho các truy cập ra ngoài internet.</li>
          </ul>
        </>
      ),
    },

    sidebar: {
      id: "DOC-2024-042",

      title: "Cloud Guideline",

      status: "Pending",

      version: "v1.0.5",

      aiAssessment: {
        score: "7.2",

        label: "Cần Cải Thiện",

        summary: "Thiếu phần cấu hình IAM Roles và bảo mật lưu trữ.",

        points: [
          {
            isPositive: true,

            text: "Kiến trúc mạng an toàn, tuân thủ AWS Well-Architected.",
          },

          {
            isPositive: false,

            text: "Thiếu hướng dẫn phân quyền IAM Role cho EKS.",
          },
        ],
      },

      reviewer: {
        name: "Minh Tú",

        role: "Cloud Architect",

        avatar:
          "https://lh3.googleusercontent.com/aida-public/AB6AXuA2hOD2ai6ZAcHaRwwVMTFaZe4-ihmKeOTfmGE8eNUcW3jwr7MUOy6mvsXmA_kaKNClwhR0d7f1W3kVC3M-1twZfS2wIKgkB5_D0UKxoAvqXYETbrPu1L-4hdKiM3wVS3S9Juc7Oxd6XF57XT5_njBbmGdsvXC3-mTc1z_N18HT0ejboaPJQ60mqZ4MxYuzkYo0ep7H-kPpYGwv-Ar-Ktk1Xo_T-MSGDy7rXTcwbKXz4cruGtgAhJgfVnuH_x881xRVCtXbUnRpzhmi",

        comment:
          "Vui lòng bổ sung phần IAM Roles và hướng dẫn bảo mật S3 Bucket.",

        statusLabel: "Chờ Chỉnh Sửa",
      },
    },
  },
};

// Hàm sinh dữ liệu dự phòng cho các ID không có sẵn trong Mock Data

const getDocumentData = (id: string) => {
  if (MOCK_DOCUMENTS[id]) return MOCK_DOCUMENTS[id];

  // Dữ liệu Fallback

  return {
    preview: {
      title: `Tài Liệu Cấu Hình ${id}`,

      description: `Tài liệu tự động tạo để hiển thị cho ID: ${id}`,

      content: (
        <>
          <h2 className="text-2xl font-headline font-semibold mt-8 mb-4">
            Nội Dung Đang Cập Nhật
          </h2>

          <p>
            Chưa có dữ liệu chi tiết cho tài liệu này trên hệ thống. Vui lòng
            liên hệ người tạo tài liệu để biết thêm chi tiết.
          </p>
        </>
      ),
    },

    sidebar: {
      id: id,

      title: `Tài liệu ${id}`,

      status: "Draft",

      version: "v1.0.0",

      aiAssessment: {
        score: "--",

        label: "Chưa Đánh Giá",

        summary: "Tài liệu mới, AI Curator chưa tiến hành phân tích.",

        points: [],
      },

      reviewer: null,
    },
  };
};

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function DocumentDetailPage({ params }: PageProps) {
  const resolvedParams = await params;
  const documentId = resolvedParams.id;
  const docData = getDocumentData(documentId);

  // === GIẢ LẬP LOGIC PHÂN QUYỀN ===
  // Trong thực tế, bạn sẽ lấy từ hook ở Client Component,
  // hoặc check JWT/Session ở Server Component.
  // Ví dụ: const perm = usePermission();
  // let userRole = 'viewer';
  // if (perm.canApprove) userRole = 'approver';
  // else if (perm.canEdit) userRole = 'editor';

  const currentUserRole: "viewer" | "editor" | "approver" = "approver"; // Đổi giá trị này để test UI

  return (
    <div className="p-8 flex gap-8 h-[calc(100vh-4rem)] overflow-hidden">
      {/* Cột trái: Nội dung tài liệu */}
      <DocumentPreview
        title={docData.preview.title}
        description={docData.preview.description}
        content={docData.preview.content}
      />

      {/* Cột phải: Sidebar phân quyền */}
      <DocumentSidebar
        data={docData.sidebar}
        userRole={currentUserRole} // Truyền Role vào đây
      />
    </div>
  );
}
