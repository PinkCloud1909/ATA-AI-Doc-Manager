import { describe, expect, it } from "vitest";

import {
  filterDocumentsByRole,
  type DocumentItem,
  type DocumentUserRole,
} from "./DocumentTable";

const documents: DocumentItem[] = [
  {
<<<<<<< Updated upstream
    id: "approved-doc",
    name: "Approved Document",
    category: "Security",
    type: "Runbook",
    status: "Approved",
    version: "1.0.0",
    score: "9.0",
    updatedAt: "Today",
    author: "Admin",
    icon: "description",
    iconColor: "text-green-600",
    bgColor: "bg-green-50",
  },
  {
    id: "expired-doc",
    name: "Expired Document",
    category: "Legal",
    type: "Policy",
    status: "Expired",
    version: "1.0.0",
    score: "8.0",
    updatedAt: "Yesterday",
    author: "Admin",
    icon: "policy",
    iconColor: "text-red-600",
    bgColor: "bg-red-50",
  },
  {
    id: "pending-doc",
    name: "Pending Document",
    category: "Infrastructure",
    type: "SOP",
    status: "Pending",
    version: "1.0.0",
    score: "7.0",
    updatedAt: "Yesterday",
    author: "Reviewer",
    icon: "menu_book",
    iconColor: "text-blue-600",
    bgColor: "bg-blue-50",
  },
  {
    id: "draft-doc",
    name: "Draft Document",
    category: "Compliance",
    type: "SOP",
    status: "Draft",
    version: "0.1.0",
    score: "--",
    updatedAt: "Last week",
    author: "Editor",
    icon: "edit_document",
    iconColor: "text-neutral-600",
    bgColor: "bg-neutral-100",
=======
    document_id: "approved-doc",
    document_group_id: "g1",
    title: "Approved Document",
    original_filename: "approved.pdf",
    document_type: "policy",
    status: "approved",
    version: 1,
    review_count: 1,
    average_review_grade: 8,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    document_id: "draft-doc",
    document_group_id: "g2",
    title: "Draft Document",
    original_filename: "draft.pdf",
    document_type: "manual",
    status: "draft",
    version: 1,
    review_count: 0,
    created_at: "2026-01-02T00:00:00Z",
>>>>>>> Stashed changes
  },
];

const documentIds = (items: DocumentItem[]) => items.map((item) => item.id);

describe("filterDocumentsByRole", () => {
  it("viewer chỉ thấy tài liệu Approved và Expired", () => {
    expect(documentIds(filterDocumentsByRole(documents, "viewer"))).toEqual([
      "approved-doc",
      "expired-doc",
    ]);
  });

  it.each(["editor", "approver"] satisfies DocumentUserRole[])(
    "%s thấy toàn bộ danh sách tài liệu",
    (role) => {
      expect(documentIds(filterDocumentsByRole(documents, role))).toEqual([
        "approved-doc",
        "expired-doc",
        "pending-doc",
        "draft-doc",
      ]);
    },
  );
});
