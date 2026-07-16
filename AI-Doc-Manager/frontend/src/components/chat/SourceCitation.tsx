import type { SourceReference } from "@/types/chat";
import Link from "next/link";

interface Props {
  sources: SourceReference[];
  isFromKb: boolean;
}

export function SourceCitation({ sources, isFromKb }: Props) {
  return (
    <div className="w-full rounded-xl border border-slate-200 bg-white p-3 space-y-2">
      <div className="flex items-center gap-1.5">
        <span
          className={`w-2 h-2 rounded-full ${isFromKb ? "bg-emerald-400" : "bg-amber-400"}`}
        />
        <span className="text-xs font-medium text-slate-500">
          {isFromKb
            ? `From ${sources.length} approved documents`
            : "Response from AI (no matching documents found)"}
        </span>
      </div>

      {sources.length > 0 && (
        <ul className="space-y-1.5">
          {sources.map((s, idx) => {
            const score = s.score;
            return (
              <li key={s.document_id ?? idx} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className="text-xs text-slate-400 font-mono shrink-0">
                    {s.chunk_index != null ? `#${s.chunk_index}` : ""}
                  </span>
                  <Link
                    href={s.document_id ? `/documents/${s.document_id}` : "#"}
                    className="text-xs text-blue-600 hover:underline truncate"
                  >
                    {s.original_filename || s.title || "Unknown source"}
                  </Link>
                </div>

                {score != null && (
                  <div className="flex items-center gap-1 shrink-0">
                    <div className="w-12 h-1 bg-slate-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          score > 0.8
                            ? "bg-emerald-500"
                            : score > 0.6
                              ? "bg-amber-400"
                              : "bg-slate-400"
                        }`}
                        style={{ width: `${Math.min(score * 100, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-400">
                      {(score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
