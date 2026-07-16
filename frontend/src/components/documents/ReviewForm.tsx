"use client"

import { useState } from "react"
import { useCreateReview } from "@/hooks/useDocuments"
import { toast } from "sonner"

export function ReviewForm({ documentId }: { documentId: string }) {
  const [grade,   setGrade]   = useState(7)
  const [comment, setComment] = useState("")
  const { mutateAsync, isPending } = useCreateReview(documentId)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!comment.trim()) { toast.error("Vui lòng nhập nhận xét"); return }
    await mutateAsync({ grade, comment })
    toast.success("Đã gửi đánh giá")
    setComment("")
  }

  const gradeColor =
    grade >= 8 ? "text-emerald-600" : grade >= 5 ? "text-amber-500" : "text-red-500"

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-slate-50 rounded-xl p-4 border border-slate-200">
      <h3 className="text-sm font-semibold text-slate-700">Chấm điểm tài liệu</h3>

      {/* Grade slider */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="text-sm text-slate-600">Điểm chất lượng</label>
          <span className={`text-2xl font-bold ${gradeColor}`}>{grade}</span>
        </div>
        <input
          type="range"
          min={1}
          max={10}
          value={grade}
          onChange={(e) => setGrade(Number(e.target.value))}
          className="w-full accent-blue-600"
        />
        <div className="flex justify-between text-xs text-slate-400">
          <span>1 — Rất kém</span>
          <span>10 — Xuất sắc</span>
        </div>
      </div>

      {/* Comment */}
      <div className="space-y-1">
        <label className="text-sm text-slate-600">Nhận xét</label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={3}
          placeholder="Nhập nhận xét về chất lượng tài liệu…"
          className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60
                   text-white text-sm font-medium rounded-lg transition-colors"
      >
        {isPending ? "Đang gửi…" : "Gửi đánh giá"}
      </button>
    </form>
  )
}
