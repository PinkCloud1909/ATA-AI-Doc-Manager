"use client";

import { ReviewForm } from "./ReviewForm";
import { useReviewList } from "@/hooks/useDocuments";
import { useTranslation } from "@/i18n/LanguageContext";

export function DocumentReviewPanel({
  documentId,
  averageGrade,
  reviewCount,
  canComment,
  status,
}: {
  documentId: string;
  averageGrade?: number | null;
  reviewCount: number;
  canComment: boolean;
  status: string;
}) {
  const { t } = useTranslation();
  const { data, isLoading, error } = useReviewList(documentId, { page_size: 100 });
  const reviews = data?.items ?? [];
  const reviewAllowed = status === "pending_review" || status === "approved";

  return (
    <section className="min-w-0 flex-1 overflow-y-auto rounded-xl border border-outline-variant/15 bg-white p-6 shadow-sm">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b border-outline-variant/15 pb-5">
        <div>
          <h2 className="text-2xl font-black text-on-surface">{t.documents.detail.reviews}</h2>
          <p className="mt-1 text-sm text-on-surface-variant">Comments and quality scores from document readers.</p>
        </div>
        <div className="flex items-center gap-3 rounded-xl bg-surface-container-low px-5 py-3">
          <span className="material-symbols-outlined text-amber-500">star</span>
          <span className="text-2xl font-black text-on-surface">{averageGrade != null ? averageGrade.toFixed(1) : "—"}</span>
          <span className="text-sm text-on-surface-variant">/ 10 · {reviewCount} review{reviewCount === 1 ? "" : "s"}</span>
        </div>
      </div>

      {canComment && reviewAllowed && <div className="mb-7"><ReviewForm documentId={documentId} /></div>}

      {isLoading ? (
        <div className="space-y-3">{[1, 2, 3].map((item) => <div key={item} className="h-24 animate-pulse rounded-xl bg-surface-container-low" />)}</div>
      ) : error ? (
        <p className="rounded-lg bg-error-container/20 p-4 text-sm text-error">Could not load reviews.</p>
      ) : reviews.length === 0 ? (
        <div className="py-16 text-center text-on-surface-variant">
          <span className="material-symbols-outlined text-5xl">reviews</span>
          <p className="mt-2 text-sm">{t.documents.detail.noReviews}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <article key={review.id} className="rounded-xl border border-outline-variant/15 p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-secondary-container text-sm font-black text-on-secondary-container">{(review.user_name ?? "U").slice(0, 1).toUpperCase()}</div>
                  <div>
                    <p className="font-bold text-on-surface">{review.user_name ?? "Unknown user"}</p>
                    <p className="text-xs text-on-surface-variant">{review.created_date ? new Date(review.created_date).toLocaleString() : ""}</p>
                  </div>
                </div>
                <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-3 py-1 text-sm font-black text-amber-700"><span className="material-symbols-outlined text-[17px]">star</span>{review.grade}/10</span>
              </div>
              <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-on-surface-variant">{review.comment}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
