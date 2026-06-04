"use client"

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { approvalsApi } from "@/lib/api/approvals"
import { documentKeys } from "@/hooks/useDocuments"

interface Props {
  documentId: string
  onDone?: () => void
  showSubmit?: boolean
  showApprove?: boolean
}

export function ApprovalActions({
  documentId,
  onDone,
  showSubmit = true,
  showApprove = true,
}: Props) {
  const qc = useQueryClient()
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [reason, setReason] = useState("")

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: documentKeys.all })
    qc.invalidateQueries({ queryKey: ["approvals"] })
    onDone?.()
  }

  const submit = useMutation({
    mutationFn: () => approvalsApi.submit(documentId),
    onSuccess: () => {
      toast.success("Đã gửi phê duyệt")
      invalidate()
    },
    onError: () => toast.error("Không gửi phê duyệt được"),
  })

  const approve = useMutation({
    mutationFn: () => approvalsApi.approve(documentId),
    onSuccess: () => {
      toast.success("Đã phê duyệt")
      invalidate()
    },
    onError: () => toast.error("Không phê duyệt được"),
  })

  const reject = useMutation({
    mutationFn: () => approvalsApi.reject(documentId, reason),
    onSuccess: () => {
      toast.success("Đã từ chối")
      setShowRejectModal(false)
      setReason("")
      invalidate()
    },
    onError: () => toast.error("Không từ chối được"),
  })

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {showSubmit && (
          <button
            type="button"
            onClick={() => submit.mutate()}
            disabled={submit.isPending}
            className="rounded-lg bg-slate-700 px-3 py-1.5 text-sm text-white transition-colors hover:bg-slate-800 disabled:opacity-50"
          >
            Gửi duyệt
          </button>
        )}
        {showApprove && (
          <>
            <button
              type="button"
              onClick={() => approve.mutate()}
              disabled={approve.isPending}
              className="rounded-lg bg-emerald-600 px-3 py-1.5 text-sm text-white transition-colors hover:bg-emerald-700 disabled:opacity-50"
            >
              Phê duyệt
            </button>
            <button
              type="button"
              onClick={() => setShowRejectModal(true)}
              className="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-sm text-red-600 transition-colors hover:bg-red-100"
            >
              Từ chối
            </button>
          </>
        )}
      </div>

      {showRejectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md space-y-4 rounded-xl bg-white p-6 shadow-2xl">
            <h3 className="font-semibold text-slate-800">Lý do từ chối</h3>
            <textarea
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              rows={4}
              placeholder="Nhập lý do từ chối tài liệu"
              className="w-full resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowRejectModal(false)}
                className="rounded-lg px-4 py-2 text-sm text-slate-600 hover:bg-slate-100"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={() => reject.mutate()}
                disabled={!reason.trim() || reject.isPending}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-50"
              >
                Xác nhận từ chối
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
