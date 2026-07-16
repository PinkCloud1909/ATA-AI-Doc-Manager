"use client";

import { useState } from "react";
import {
  useApproveDocument,
  useRejectDocument,
} from "@/hooks/useDocuments";
import { useTranslation } from "@/i18n/LanguageContext";
import { toast } from "sonner";
import axios from "axios";

interface Props {
  documentId: string;
  onDone?: () => void;
}

function getError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as { detail?: string } | undefined;
    return data?.detail ?? err.message;
  }
  return (err as Error)?.message ?? "Unknown error";
}

export function ApprovalActions({ documentId, onDone }: Props) {
  const { t } = useTranslation();
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [reason, setReason] = useState("");

  const approve = useApproveDocument();
  const reject = useRejectDocument();

  const handleDone = () => onDone?.();

  const handleApprove = async () => {
    try {
      await approve.mutateAsync(documentId);
      toast.success(t.approvals.approve ?? "Approved");
      handleDone();
    } catch (err) {
      toast.error(getError(err));
    }
  };

  const handleReject = async () => {
    if (!reason.trim()) return;
    try {
      await reject.mutateAsync({ id: documentId, reason: reason.trim() });
      toast.success(t.approvals.reject ?? "Rejected");
      setShowRejectModal(false);
      setReason("");
      handleDone();
    } catch (err) {
      toast.error(getError(err));
    }
  };

  return (
    <>
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={handleApprove}
          disabled={approve.isPending}
          className="px-3 py-1.5 text-sm bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {approve.isPending ? "..." : (t.approvals.approve ?? "Approve")}
        </button>
        <button
          onClick={() => setShowRejectModal(true)}
          className="px-3 py-1.5 text-sm bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-lg transition-colors"
        >
          {t.approvals.reject ?? "Reject"}
        </button>
      </div>

      {showRejectModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md space-y-4 shadow-2xl">
            <h3 className="font-semibold text-slate-800">
              {t.approvals.rejectReason ?? "Rejection reason"}
            </h3>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={4}
              placeholder="Explain why this document is rejected..."
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-400 resize-none"
              maxLength={2000}
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setShowRejectModal(false); setReason(""); }}
                className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                {t.common.cancel ?? "Cancel"}
              </button>
              <button
                onClick={handleReject}
                disabled={!reason.trim() || reject.isPending}
                className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg disabled:opacity-50"
              >
                {reject.isPending
                  ? (t.common.loading ?? "...")
                  : (t.common.confirm ?? "Confirm")}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
