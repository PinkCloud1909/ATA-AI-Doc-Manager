"use client";

import { useState } from "react";
import { useDocumentList } from "@/hooks/useDocuments";
import { useRunbookList, useRunbook, useGenerateRunbook, useDeleteRunbook } from "@/hooks/useRunbooks";
import { useTranslation } from "@/i18n/LanguageContext";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import type { RunbookPurpose } from "@/types/runbook";
import { PURPOSE_LABELS } from "@/types/runbook";
import axios from "axios";

const PURPOSE_OPTIONS: RunbookPurpose[] = [
  "onboarding",
  "incident_response",
  "deployment",
  "troubleshooting",
  "training",
  "other",
];

function getError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as { detail?: string } | undefined;
    return data?.detail ?? err.message;
  }
  return (err as Error)?.message ?? "Unknown error";
}

export default function RunbooksPage() {
  const { t } = useTranslation();

  const [showGenerate, setShowGenerate] = useState(false);
  const [selectedDocIds, setSelectedDocIds] = useState<Set<string>>(new Set());
  const [purpose, setPurpose] = useState<RunbookPurpose>("other");
  const [title, setTitle] = useState("");
  const [selectedRunbook, setSelectedRunbook] = useState<string | null>(null);

  const { data: runbookList, isLoading } = useRunbookList({ page_size: 50 });
  const { data: runbookDetail, isLoading: isLoadingDetail } = useRunbook(selectedRunbook ?? "");
  const { data: documentList } = useDocumentList({ page_size: 100 });

  const generateMutation = useGenerateRunbook();
  const deleteMutation = useDeleteRunbook();

  const toggleDocument = (id: string) => {
    const next = new Set(selectedDocIds);
    if (next.has(id)) {
      next.delete(id);
    } else if (next.size < 10) {
      next.add(id);
    }
    setSelectedDocIds(next);
  };

  const handleGenerate = async () => {
    if (selectedDocIds.size === 0) {
      toast.error(t.runbooks.emptyDocuments);
      return;
    }
    try {
      await generateMutation.mutateAsync({
        document_ids: Array.from(selectedDocIds),
        purpose,
        title: title.trim() || undefined,
      });
      toast.success(t.runbooks.generatedSuccessfully ?? "Runbook generated");
      setShowGenerate(false);
      setSelectedDocIds(new Set());
      setTitle("");
    } catch (err) {
      toast.error(getError(err));
    }
  };

  const handleDelete = async (runbookId: string) => {
    if (!confirm(t.runbooks.deleteConfirm ?? "Delete this runbook?")) return;
    try {
      await deleteMutation.mutateAsync(runbookId);
      toast.success(t.runbooks.deletedSuccessfully ?? "Runbook deleted");
      if (selectedRunbook === runbookId) setSelectedRunbook(null);
    } catch (err) {
      toast.error(getError(err));
    }
  };

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "--";
    return new Date(dateStr).toLocaleDateString("en-US", { dateStyle: "medium" });
  };

  const runbooks = runbookList?.items ?? [];

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 min-w-0">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-on-surface">
            {t.runbooks.title}
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            {t.runbooks.subtitle}
          </p>
        </div>
        <button
          onClick={() => setShowGenerate(!showGenerate)}
          className="flex items-center gap-2 px-4 py-2 bg-tertiary text-on-tertiary rounded-lg font-semibold text-sm hover:bg-tertiary-dim transition-colors"
        >
          <span className="material-symbols-outlined text-sm">add</span>
          {t.runbooks.generateTitle}
        </button>
      </div>

      {showGenerate && (
        <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/15 shadow-sm p-6 space-y-5">
          <h2 className="text-lg font-bold text-on-surface">{t.runbooks.generateTitle}</h2>

          <div className="space-y-1.5">
            <label className="text-sm font-medium text-on-surface">
              {t.runbooks.titleLabel} <span className="text-on-surface-variant font-normal">({t.common.optional})</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t.runbooks.titlePlaceholder}
              className="w-full bg-surface-container-lowest border-none ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-inset focus:ring-tertiary rounded-lg px-3 py-2.5 text-sm text-on-surface"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium text-on-surface">{t.runbooks.promptLabel}</label>
            <select
              value={purpose}
              onChange={(e) => setPurpose(e.target.value as RunbookPurpose)}
              className="w-full bg-surface-container-lowest border-none ring-1 ring-inset ring-outline-variant/40 focus:ring-2 focus:ring-inset focus:ring-tertiary rounded-lg px-3 py-2.5 text-sm text-on-surface"
            >
              {PURPOSE_OPTIONS.map((p) => (
                <option key={p} value={p}>{PURPOSE_LABELS[p]}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium text-on-surface">
              {t.runbooks.selectDocuments}{" "}
              <span className="text-xs text-on-surface-variant">
                ({String(selectedDocIds.size)} selected)
              </span>
            </label>
            <div className="max-h-48 overflow-y-auto border border-outline-variant/20 rounded-lg">
              {(documentList?.items ?? []).map((doc) => {
                const docId = doc.document_id;
                const isSelected = selectedDocIds.has(docId);
                return (
                  <label
                    key={docId}
                    className={`flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-surface-container-low transition-colors ${
                      isSelected ? "bg-tertiary/5" : ""
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleDocument(docId)}
                      disabled={!isSelected && selectedDocIds.size >= 10}
                      className="rounded border-outline-variant text-tertiary focus:ring-tertiary"
                    />
                    <span className="text-sm text-on-surface truncate">
                      {doc.title}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={generateMutation.isPending || selectedDocIds.size === 0}
            className="w-full py-2.5 bg-tertiary hover:bg-tertiary-dim disabled:opacity-60 text-on-tertiary text-sm font-semibold rounded-lg transition-all"
          >
            {generateMutation.isPending ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                {t.runbooks.generating}
              </span>
            ) : (
              t.runbooks.generateButton
            )}
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-surface-container-lowest rounded-xl border border-outline-variant/15 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-outline-variant/10">
            <h2 className="text-sm font-semibold text-on-surface">{t.runbooks.title}</h2>
          </div>
          {isLoading ? (
            <div className="p-6 text-center text-sm text-on-surface-variant">{t.common.loading}</div>
          ) : runbooks.length === 0 ? (
            <div className="p-6 text-center text-sm text-on-surface-variant">{t.runbooks.noRunbooks}</div>
          ) : (
            <ul className="divide-y divide-outline-variant/10">
              {runbooks.map((rb) => (
                <li
                  key={rb.runbook_id}
                  className={`px-5 py-3 cursor-pointer hover:bg-surface-container-low transition-colors ${
                    selectedRunbook === rb.runbook_id ? "bg-tertiary/5 border-l-2 border-tertiary" : ""
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <button
                      onClick={() => setSelectedRunbook(selectedRunbook === rb.runbook_id ? null : rb.runbook_id)}
                      className="text-left flex-1 min-w-0"
                    >
                      <p className="text-sm font-medium text-on-surface truncate">
                        {rb.title || PURPOSE_LABELS[rb.purpose]}
                      </p>
                      <p className="text-xs text-on-surface-variant mt-0.5">
                        {PURPOSE_LABELS[rb.purpose]} · {formatDate(rb.created_at)}
                      </p>
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(rb.runbook_id); }}
                      className="p-1 text-on-surface-variant hover:text-error transition-colors shrink-0"
                      title={t.common.delete}
                    >
                      <span className="material-symbols-outlined text-[16px]">delete</span>
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="lg:col-span-2 bg-surface-container-lowest rounded-xl border border-outline-variant/15 shadow-sm p-6">
          {!selectedRunbook ? (
            <div className="flex flex-col items-center justify-center h-64 text-on-surface-variant">
              <span className="material-symbols-outlined text-4xl mb-3">auto_stories</span>
              <p className="text-sm">Select a runbook to view</p>
            </div>
          ) : isLoadingDetail ? (
            <div className="flex items-center justify-center h-64">
              <div className="w-6 h-6 border-2 border-tertiary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : runbookDetail ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-bold text-on-surface">
                  {runbookDetail.title || PURPOSE_LABELS[runbookDetail.purpose]}
                </h3>
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="px-2 py-0.5 text-xs rounded-full bg-surface-container-low text-on-surface-variant">
                    {PURPOSE_LABELS[runbookDetail.purpose]}
                  </span>
                  <span className="px-2 py-0.5 text-xs rounded-full bg-surface-container-low text-on-surface-variant">
                    {runbookDetail.status}
                  </span>
                  <span className="px-2 py-0.5 text-xs rounded-full bg-surface-container-low text-on-surface-variant">
                    {t.runbooks.created}: {formatDate(runbookDetail.created_at)}
                  </span>
                </div>
              </div>
              {runbookDetail.content ? (
                <div className="prose prose-sm max-w-none prose-headings:text-on-surface prose-p:text-on-surface-variant prose-strong:text-on-surface prose-a:text-tertiary">
                  <ReactMarkdown>{runbookDetail.content}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm text-on-surface-variant italic">{t.common.noResults}</p>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
