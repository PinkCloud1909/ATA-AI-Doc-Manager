"use client";

<<<<<<< Updated upstream
import { FormEvent, useState } from "react"
import { toast } from "sonner"
import { useCreateReview } from "@/hooks/useDocuments"

export function ReviewForm({ documentId }: { documentId: string }) {
  const [grade, setGrade] = useState(7)
  const [comment, setComment] = useState("")
  const { mutateAsync, isPending } = useCreateReview(documentId)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!comment.trim()) {
      toast.error("Vui lòng nhập nhận xét")
      return
    }

    try {
      await mutateAsync({ grade, comment })
      toast.success("Đã gửi đánh giá")
      setComment("")
    } catch {
      toast.error("Không gửi được đánh giá. Tài liệu cần ở trạng thái pending review hoặc approved.")
    }
  }
=======
import { useState } from "react";
import { toast } from "sonner";
import { useCreateReview } from "@/hooks/useDocuments";
import { getApiErrorMessage } from "@/lib/error-handler";
import { validateReviewComment, validateReviewGrade } from "@/lib/validation";

export function ReviewForm({ documentId }: { documentId: string }) {
  const [grade, setGrade] = useState(7);
  const [comment, setComment] = useState("");
  const mutation = useCreateReview(documentId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validateReviewGrade(grade) ?? validateReviewComment(comment);
    if (validationError) {
      toast.error(validationError);
      return;
    }
    try {
      await mutation.mutateAsync({ grade, comment: comment.trim() });
      toast.success("Review submitted successfully");
      setComment("");
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to submit review"));
    }
  };
>>>>>>> Stashed changes

  const gradeColor = grade >= 8 ? "text-emerald-600" : grade >= 5 ? "text-amber-600" : "text-red-600";

  return (
<<<<<<< Updated upstream
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-xl border border-slate-200 bg-slate-50 p-4"
    >
      <h3 className="text-sm font-semibold text-slate-700">Chấm điểm tài liệu</h3>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-sm text-slate-600">Điểm chất lượng</label>
          <span className={`text-2xl font-bold ${gradeColor}`}>{grade}</span>
        </div>
        <input
          type="range"
          min={1}
          max={10}
          value={grade}
          onChange={(event) => setGrade(Number(event.target.value))}
          className="w-full accent-blue-600"
        />
        <div className="flex justify-between text-xs text-slate-400">
          <span>1 - Rất kém</span>
          <span>10 - Xuất sắc</span>
        </div>
      </div>

      <div className="space-y-1">
        <label className="text-sm text-slate-600">Nhận xét</label>
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          rows={3}
          placeholder="Nhập nhận xét về chất lượng tài liệu"
          className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-60"
      >
        {isPending ? "Đang gửi..." : "Gửi đánh giá"}
=======
    <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-outline-variant/20 bg-surface-container-low p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-on-surface">Add your review</h3>
        <span className={`text-2xl font-black ${gradeColor}`}>{grade}/10</span>
      </div>
      <div>
        <label htmlFor="review-grade" className="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Quality score</label>
        <input id="review-grade" type="range" min={1} max={10} step={1} value={grade} onChange={(e) => setGrade(Number(e.target.value))} className="w-full accent-tertiary" />
        <div className="flex justify-between text-[11px] text-on-surface-variant"><span>1 — Poor</span><span>10 — Excellent</span></div>
      </div>
      <div>
        <label htmlFor="review-comment" className="mb-2 block text-xs font-bold uppercase tracking-wider text-on-surface-variant">Comment</label>
        <textarea id="review-comment" required maxLength={2000} rows={4} value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Share feedback about this document..." className="w-full resize-y rounded-lg border border-outline-variant/30 bg-white px-3 py-2 text-sm text-on-surface focus:border-tertiary focus:outline-none focus:ring-1 focus:ring-tertiary" />
        <p className="mt-1 text-right text-[11px] text-on-surface-variant">{comment.length}/2000</p>
      </div>
      <button type="submit" disabled={mutation.isPending} className="inline-flex items-center gap-2 rounded-lg bg-tertiary px-4 py-2.5 text-sm font-bold text-on-tertiary hover:bg-tertiary-dim disabled:opacity-60">
        {mutation.isPending && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />}
        {mutation.isPending ? "Submitting..." : "Submit review"}
>>>>>>> Stashed changes
      </button>
    </form>
  );
}
