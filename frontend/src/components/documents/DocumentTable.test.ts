import { describe, expect, it } from "vitest";
import type { DocumentListItem } from "@/types/document";

const documents: DocumentListItem[] = [
  {
    document_id: "approved-doc",
    document_group_id: "g1",
    title: "Approved Document",
    original_filename: "approved.pdf",
    document_type: "policy",
    status: "approved",
    version: 1,
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
    created_at: "2026-01-02T00:00:00Z",
  },
];

describe("DocumentListItem type", () => {
  it("has correct required fields", () => {
    for (const doc of documents) {
      expect(doc.document_id).toBeTruthy();
      expect(doc.title).toBeTruthy();
      expect(doc.status).toBeTruthy();
    }
  });

  it("filters by status correctly", () => {
    const approved = documents.filter((d) => d.status === "approved");
    expect(approved).toHaveLength(1);
    expect(approved[0].document_id).toBe("approved-doc");
  });
});
