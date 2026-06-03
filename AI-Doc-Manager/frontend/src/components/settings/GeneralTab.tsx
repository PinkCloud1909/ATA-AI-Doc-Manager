"use client";
import { useState } from "react";

export default function GeneralTab() {
  const [theme, setTheme] = useState("light");
  const [autoGrade, setAutoGrade] = useState(true);
  const [language, setLanguage] = useState("vi");

  return (
    <div className="max-w-2xl animate-in fade-in duration-300">
      <h3 className="font-headline font-bold text-2xl text-on-surface mb-8">
        Chung
      </h3>

      <div className="space-y-10">
        {/* Section: Giao diện */}
        <section>
          <h4 className="font-inter text-sm font-semibold text-on-surface uppercase tracking-wider mb-4">
            Giao diện
          </h4>
          <div className="flex items-center gap-4">
            {/* Option Sáng */}
            <label className="flex flex-col items-center gap-3 cursor-pointer group">
              <div
                className={`w-32 h-20 rounded-lg border-2 flex flex-col p-2 gap-1 shadow-sm transition-all bg-background ${theme === "light" ? "border-tertiary" : "border-transparent hover:border-outline-variant"}`}
              >
                <div className="w-full h-3 bg-surface-container-lowest rounded shadow-sm"></div>
                <div className="w-full h-full bg-surface-container-lowest rounded shadow-sm"></div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="radio"
                  name="theme"
                  value="light"
                  checked={theme === "light"}
                  onChange={() => setTheme("light")}
                  className="text-tertiary focus:ring-tertiary"
                />
                <span
                  className={`font-inter text-sm font-medium ${theme === "light" ? "text-on-surface" : "text-on-surface-variant group-hover:text-on-surface"}`}
                >
                  Sáng
                </span>
              </div>
            </label>

            {/* Option Tối */}
            <label className="flex flex-col items-center gap-3 cursor-pointer group">
              <div
                className={`w-32 h-20 rounded-lg border-2 flex flex-col p-2 gap-1 transition-all bg-inverse-surface ${theme === "dark" ? "border-tertiary" : "border-transparent hover:border-outline-variant"}`}
              >
                <div className="w-full h-3 bg-secondary-dim rounded"></div>
                <div className="w-full h-full bg-secondary-dim rounded"></div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="radio"
                  name="theme"
                  value="dark"
                  checked={theme === "dark"}
                  onChange={() => setTheme("dark")}
                  className="text-tertiary focus:ring-tertiary"
                />
                <span
                  className={`font-inter text-sm font-medium ${theme === "dark" ? "text-on-surface" : "text-on-surface-variant group-hover:text-on-surface"}`}
                >
                  Tối
                </span>
              </div>
            </label>
          </div>
        </section>

        <div className="h-px w-full bg-surface-variant/50"></div>

        {/* Section: Tự động chấm điểm */}
        <section className="flex items-center justify-between">
          <div>
            <h4 className="font-inter text-base font-semibold text-on-surface">
              Tự động chấm điểm tài liệu
            </h4>
            <p className="font-inter text-sm text-on-surface-variant mt-1">
              AI sẽ tự động đánh giá và chấm điểm các tài liệu được tải lên.
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={autoGrade}
              onChange={() => setAutoGrade(!autoGrade)}
            />
            <div className="w-11 h-6 bg-surface-container-high peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-tertiary"></div>
          </label>
        </section>

        <div className="h-px w-full bg-surface-variant/50"></div>

        {/* Section: Ngôn ngữ */}
        <section>
          <h4 className="font-inter text-sm font-semibold text-on-surface uppercase tracking-wider mb-4">
            Ngôn ngữ
          </h4>
          <div className="relative w-64">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="block w-full appearance-none bg-surface-container-low border border-transparent text-on-surface font-inter text-sm rounded-lg px-4 py-2.5 pr-8 focus:outline-none focus:ring-2 focus:ring-tertiary focus:bg-surface-container-lowest transition-colors cursor-pointer"
            >
              <option value="vi">Tiếng Việt</option>
              <option value="en">Tiếng Anh</option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-on-surface-variant">
              <span className="material-symbols-outlined text-xl">
                expand_more
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
