// lib/validation.ts
// Validation helpers matching OpenAPI schema constraints

export const VALIDATION = {
  username: { minLength: 3, maxLength: 100 },
  password: { minLength: 8, maxLength: 255 },
  roleName: { minLength: 1, maxLength: 50 },
  rejectReason: { minLength: 1, maxLength: 2000 },
  reviewGrade: { min: 1, max: 10 },
  reviewComment: { minLength: 1, maxLength: 2000 },
  documentTitle: { minLength: 1, maxLength: 500 },
  documentTypes: ["policy", "manual", "report", "other"] as const,
  statuses: [
    "draft",
    "pending_review",
    "approved",
    "rejected",
    "expired",
    "active",
    "archived",
  ] as const,
  runbookPurposes: [
    "onboarding",
    "incident_response",
    "deployment",
    "troubleshooting",
    "training",
    "other",
  ] as const,
  runbookDocIds: { minItems: 1, maxItems: 10 },
  bulkVectorizeIds: { minItems: 1, maxItems: 50 },
} as const;

export function validateUsername(v: string): string | null {
  if (!v || v.length < VALIDATION.username.minLength)
    return `Username must be at least ${VALIDATION.username.minLength} characters`;
  if (v.length > VALIDATION.username.maxLength)
    return `Username must be at most ${VALIDATION.username.maxLength} characters`;
  return null;
}

export function validatePassword(v: string): string | null {
  if (!v || v.length < VALIDATION.password.minLength)
    return `Password must be at least ${VALIDATION.password.minLength} characters`;
  if (v.length > VALIDATION.password.maxLength)
    return `Password must be at most ${VALIDATION.password.maxLength} characters`;
  return null;
}

export function validateRejectReason(v: string): string | null {
  if (!v || v.trim().length < VALIDATION.rejectReason.minLength)
    return "Rejection reason is required";
  if (v.length > VALIDATION.rejectReason.maxLength)
    return `Reason must be at most ${VALIDATION.rejectReason.maxLength} characters`;
  return null;
}

export function validateReviewGrade(g: number): string | null {
  if (!Number.isInteger(g) || g < VALIDATION.reviewGrade.min || g > VALIDATION.reviewGrade.max)
    return `Grade must be between ${VALIDATION.reviewGrade.min} and ${VALIDATION.reviewGrade.max}`;
  return null;
}

export function validateReviewComment(v: string): string | null {
  if (!v || v.trim().length < VALIDATION.reviewComment.minLength)
    return "Comment is required";
  if (v.length > VALIDATION.reviewComment.maxLength)
    return `Comment must be at most ${VALIDATION.reviewComment.maxLength} characters`;
  return null;
}

export function validateDocumentTitle(v: string): string | null {
  if (v && v.length > VALIDATION.documentTitle.maxLength)
    return `Title must be at most ${VALIDATION.documentTitle.maxLength} characters`;
  return null;
}
