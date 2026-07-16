"use client";
import { useState } from "react";
import { useTranslation } from "@/i18n/LanguageContext";

export default function GeneralTab() {
  const { t, language, setLanguage } = useTranslation();
  const [theme, setTheme] = useState("light");
  const [autoGrade, setAutoGrade] = useState(true);

  return (
    <div className="max-w-2xl animate-in fade-in duration-300">
      <h3 className="font-headline font-bold text-2xl text-on-surface mb-8">
        {t.settings.general}
      </h3>

      <div className="space-y-10">
        {/* Section: Theme */}
        <section>
          <h4 className="font-inter text-sm font-semibold text-on-surface uppercase tracking-wider mb-4">
            {t.settings.theme}
          </h4>
          <div className="flex items-center gap-4">
            {/* Light Option */}
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
                  {t.settings.themeLight}
                </span>
              </div>
            </label>

            {/* Dark Option */}
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
                  {t.settings.themeDark}
                </span>
              </div>
            </label>
          </div>
        </section>

        <div className="h-px w-full bg-surface-variant/50"></div>

        {/* Section: Auto Grade */}
        <section className="flex items-center justify-between">
          <div>
            <h4 className="font-inter text-base font-semibold text-on-surface">
              {t.settings.autoGrade}
            </h4>
            <p className="font-inter text-sm text-on-surface-variant mt-1">
              {t.settings.autoGradeDesc}
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

        {/* Section: Language */}
        <section>
          <h4 className="font-inter text-sm font-semibold text-on-surface uppercase tracking-wider mb-4">
            {t.settings.language}
          </h4>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setLanguage("vi")}
              className={`px-6 py-2.5 rounded-lg font-inter text-sm font-semibold border-2 transition-all ${
                language === "vi"
                  ? "border-tertiary bg-tertiary-container/20 text-tertiary"
                  : "border-transparent bg-surface-container-low text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
              }`}
            >
              {t.settings.languageVietnamese}
            </button>
            <button
              type="button"
              onClick={() => setLanguage("en")}
              className={`px-6 py-2.5 rounded-lg font-inter text-sm font-semibold border-2 transition-all ${
                language === "en"
                  ? "border-tertiary bg-tertiary-container/20 text-tertiary"
                  : "border-transparent bg-surface-container-low text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
              }`}
            >
              {t.settings.languageEnglish}
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
