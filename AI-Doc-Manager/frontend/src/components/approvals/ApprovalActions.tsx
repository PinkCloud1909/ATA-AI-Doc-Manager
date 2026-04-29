"use client"

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { approvalsApi } from "@/lib/api/approvals"
import { documentKeys } from "@/hooks/useDocuments"
import { toast } from "sonner"

interface Props {
  documentId: string
  onDone?:    () => void
}

export function ApprovalActions({ documentId, onDone }: Props) {
  const qc = useQueryClient()
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [reason, setReason] = useState("")

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: documentKeys.all })
    onDone?.()
  }

  const submit   = useMutation({ mutationFn: () => approvalsApi.submit(documentId),   onSuccess: () => { toast.success("Đã gửi duyệt"); invalidate() } })
  const approve  = useMutation({ mutationFn: () => approvalsApi.approve(documentId),  onSuccess: () => { toast.success("Đã phê duyệt ✓"); invalidate() } })
  const reject   = useMutation({
    mutationFn: () => approvalsApi.reject(documentId, reason),
    onSuccess:  () => { toast.success("Đã từ chối"); setShowRejectModal(false); invalidate() },
  })

  return (
    <>
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => submit.mutate()}
          disabled={submit.isPending}
          className="px-3 py-1.5 text-sm bg-slate-700 hover:bg-slate-800 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          Gửi duyệt
        </button>
        <button
          onClick={() => approve.mutate()}
          disabled={approve.isPending}
          className="px-3 py-1.5 text-sm bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          ✓ Phê duyệt
        </button>
        <button
          onClick={() => setShowRejectModal(true)}
          className="px-3 py-1.5 text-sm bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-lg transition-colors"
        >
          Từ chối
        </button>
      </div>

      {/* Reject modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md space-y-4 shadow-2xl">
            <h3 className="font-semibold text-slate-800">Lý do từ chối</h3>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={4}
              placeholder="Nhập lý do từ chối tài liệu…"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg
                         focus:outline-none focus:ring-2 focus:ring-red-400 resize-none"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowRejectModal(false)}
                className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Huỷ
              </button>
              <button
                onClick={() => reject.mutate()}
                disabled={!reason.trim() || reject.isPending}
                className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg disabled:opacity-50"
              >
                {reject.isPending ? "Đang xử lý…" : "Xác nhận từ chối"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
