import { SourceReference } from "@/types/chat"
import Link from "next/link"
import { gcsFilename } from "@/lib/gcs"

interface Props {
  sources:  SourceReference[]
  isFromKb: boolean
}

export function SourceCitation({ sources, isFromKb }: Props) {
  return (
    <div className="w-full rounded-xl border border-slate-200 bg-white p-3 space-y-2">
      {/* Header */}
      <div className="flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full ${isFromKb ? "bg-emerald-400" : "bg-amber-400"}`} />
        <span className="text-xs font-medium text-slate-500">
          {isFromKb
            ? `Từ ${sources.length} tài liệu đã phê duyệt (Vertex AI Search)`
            : "Câu trả lời từ Gemini AI (không tìm thấy tài liệu phù hợp)"}
        </span>
      </div>

      {/* Source list */}
      {sources.length > 0 && (
        <ul className="space-y-1.5">
          {sources.map((s) => {
            const score = s.relevance_score ?? (s.vertex_distance != null ? 1 - s.vertex_distance : undefined)
            return (
              <li key={s.document_id} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className="text-xs text-slate-400 font-mono shrink-0">v{s.version}</span>
                  <Link
                    href={`/documents/${s.document_id}`}
                    className="text-xs text-blue-600 hover:underline truncate"
                  >
                    {s.original_filename || gcsFilename(s.gcs_path)}
                  </Link>
                </div>

                {score != null && (
                  <div className="flex items-center gap-1 shrink-0">
                    {/* Mini relevance bar */}
                    <div className="w-12 h-1 bg-slate-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          score > 0.8 ? "bg-emerald-500" :
                          score > 0.6 ? "bg-amber-400" : "bg-slate-400"
                        }`}
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-400">
                      {(score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
