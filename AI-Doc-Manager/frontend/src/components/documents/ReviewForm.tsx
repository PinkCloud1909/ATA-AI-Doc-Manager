"use client"

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

  const gradeColor =
    grade >= 8 ? "text-emerald-600" : grade >= 5 ? "text-amber-500" : "text-red-500"

  return (
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
      </button>
    </form>
  )
}
