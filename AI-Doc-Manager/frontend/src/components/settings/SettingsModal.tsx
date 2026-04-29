"use client";
import { useState } from "react";
import GeneralTab from "./GeneralTab";
import SecurityTab from "./SecurityTab";

interface SettingsModalProps {
  onClose: () => void;
}

export default function SettingsModal({ onClose }: SettingsModalProps) {
  const [activeTab, setActiveTab] = useState<"general" | "security">("general");

  return (
    // Dimmed Background Overlay
    <div
      className="fixed inset-0 bg-inverse-surface/40 backdrop-blur-sm z-[100] flex items-center justify-center p-4 sm:p-8"
      onClick={onClose} // Đóng khi bấm ra ngoài
    >
      {/* Modal Container */}
      <div
        className="bg-surface-container-lowest w-full max-w-4xl h-[600px] min-h-[600px] rounded-xl flex overflow-hidden shadow-[0_10px_15px_-3px_rgba(43,52,55,0.08),0_4px_6px_-1px_rgba(43,52,55,0.04)] relative"
        onClick={(e) => e.stopPropagation()} // Ngăn chặn sự kiện click lan ra overlay
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors z-10 flex items-center justify-center"
        >
          <span className="material-symbols-outlined">close</span>
        </button>

        {/* Sidebar Navigation */}
        <div className="w-64 bg-surface-container-low border-r border-surface-variant/20 flex flex-col py-8 px-4 z-0">
          <h2 className="font-manrope font-bold text-xl text-on-surface px-4 mb-6">
            Cài đặt
          </h2>
          <nav className="flex flex-col gap-1">
            {/* Tab Chung */}
            <button
              onClick={() => setActiveTab("general")}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg font-inter text-sm font-medium transition-colors relative ${activeTab === "general" ? "bg-surface-container-lowest text-on-surface shadow-sm" : "text-on-surface-variant hover:bg-surface-container"}`}
            >
              {activeTab === "general" && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-tertiary rounded-r-full"></div>
              )}
              <span
                className="material-symbols-outlined text-xl"
                style={
                  activeTab === "general"
                    ? { fontVariationSettings: '"FILL" 1', color: "#0053dc" }
                    : {}
                }
              >
                tune
              </span>
              Chung
            </button>

            {/* Tab Bảo mật */}
            <button
              onClick={() => setActiveTab("security")}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg font-inter text-sm font-medium transition-colors relative ${activeTab === "security" ? "bg-surface-container-lowest text-on-surface shadow-sm" : "text-on-surface-variant hover:bg-surface-container"}`}
            >
              {activeTab === "security" && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-tertiary rounded-r-full"></div>
              )}
              <span
                className="material-symbols-outlined text-xl"
                style={
                  activeTab === "security"
                    ? { fontVariationSettings: '"FILL" 1', color: "#0053dc" }
                    : {}
                }
              >
                security
              </span>
              Bảo mật
            </button>
          </nav>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-surface-container-lowest overflow-y-auto p-8 lg:p-12 z-0">
          {activeTab === "general" && <GeneralTab />}
          {activeTab === "security" && <SecurityTab />}
        </div>
      </div>
    </div>
  );
}
