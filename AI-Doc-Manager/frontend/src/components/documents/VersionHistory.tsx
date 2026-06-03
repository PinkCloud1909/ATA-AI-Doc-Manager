"use client"

import { useVersionHistory } from "@/hooks/useDocuments"
import { StatusBadge } from "./StatusBadge"

interface Props {
  groupId:         string
  currentDocumentId: string
}

export function VersionHistory({ groupId, currentDocumentId }: Props) {
  const { data: versions, isLoading } = useVersionHistory(groupId)

  if (isLoading) return <p className="text-sm text-slate-400">Đang tải lịch sử…</p>
  if (!versions?.length) return null

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-slate-700">Lịch sử phiên bản</h3>
      <ul className="space-y-1.5">
        {[...versions].reverse().map((v) => {
          const isCurrent = v.id === currentDocumentId
          return (
            <li
              key={v.id}
              className={`flex items-center justify-between rounded-lg border px-3 py-2 text-sm
                ${isCurrent
                  ? "border-blue-200 bg-blue-50"
                  : "border-slate-200 bg-white hover:border-slate-300"
                }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`font-mono font-semibold ${
                    isCurrent ? "text-blue-700" : "text-slate-600"
                  }`}
                >
                  v{v.version}
                </span>
                {isCurrent && (
                  <span className="text-xs text-blue-500 font-medium">Hiện tại</span>
                )}
              </div>

              <div className="flex items-center gap-3">
                <StatusBadge status={v.status} />
                <span className="text-xs text-slate-400">
                  {new Date(v.created_at).toLocaleDateString("vi-VN")}
                </span>
                {!isCurrent && (
                  <a
                    href={`/documents/${v.id}`}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Xem
                  </a>
                )}
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
