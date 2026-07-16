// types/runbook.ts
// Aligned with OpenAPI schemas

export type RunbookPurpose =
  | "onboarding"
  | "incident_response"
  | "deployment"
  | "troubleshooting"
  | "training"
  | "other";

/** POST /api/v1/runbooks/generate request body */
export interface RunbookGenerateRequest {
  document_ids: string[];
  purpose: RunbookPurpose;
  title?: string | null;
}

/** Full runbook detail returned by generate and GET /{id} */
export interface RunbookResponse {
  runbook_id: string;
  title: string;
  purpose: RunbookPurpose;
  document_ids: string[];
  content?: string | null;
  status: string;
  error_message?: string | null;
  created_by?: string | null;
  created_at?: string | null;
  modified_date?: string | null;
}

/** Lightweight summary for list views */
export interface RunbookListItem {
  runbook_id: string;
  title: string;
  purpose: RunbookPurpose;
  document_ids: string[];
  status: string;
  created_by?: string | null;
  created_at?: string | null;
}

/** Paginated runbook list */
export interface RunbookListResponse {
  items: RunbookListItem[];
  total: number;
  page: number;
  page_size: number;
}

/** DELETE response */
export interface RunbookDeleteResponse {
  detail: string;
}

/** UI labels for runbook purposes */
export const PURPOSE_LABELS: Record<RunbookPurpose, string> = {
  onboarding: "Onboarding",
  incident_response: "Incident Response",
  deployment: "Deployment",
  troubleshooting: "Troubleshooting",
  training: "Training",
  other: "Other",
};
