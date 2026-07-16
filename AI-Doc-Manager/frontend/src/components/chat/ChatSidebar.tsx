"use client";

import { useTranslation } from "@/i18n/LanguageContext";
import { useChatStore } from "@/stores/chatStore";

export default function ChatSidebar() {
  const { t } = useTranslation();
  const sessionId = useChatStore((s) => s.sessionId);
  const clearMessages = useChatStore((s) => s.clearMessages);

  return (
    <aside className="flex flex-col h-full w-64 lg:w-72 border-r border-outline-variant/20 py-4 shrink-0 bg-surface-container-lowest">
      <div className="px-4 mb-4">
        <button
          type="button"
          onClick={clearMessages}
          className="w-full flex items-center justify-center gap-2 bg-tertiary text-on-tertiary px-4 py-2.5 rounded-lg font-medium transition-transform active:scale-95 shadow-sm"
        >
          <span className="material-symbols-outlined text-[20px]">add</span>
          <span>{t.chat.newConversation}</span>
        </button>
      </div>

      <div className="px-4 space-y-2">
        <p className="text-xs text-on-surface-variant font-medium uppercase tracking-wider">
          Current Session
        </p>
        <p className="text-[10px] text-on-surface-variant font-mono break-all bg-surface-container-low rounded px-2 py-1.5">
          {sessionId}
        </p>
        <p className="text-[11px] text-on-surface-variant">
          {t.chat.welcomeDescription}
        </p>
      </div>
    </aside>
  );
}
