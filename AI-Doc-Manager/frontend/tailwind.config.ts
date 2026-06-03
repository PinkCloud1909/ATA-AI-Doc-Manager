import type { Config } from "tailwindcss";

const config: Config = {
  // Cấu hình content để Tailwind quét các file trong thư mục src
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx,css}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "surface-tint": "#5e5e5e",
        "inverse-primary": "#ffffff",
        "tertiary-fixed": "#3e76fe",
        "surface-container-highest": "#dbe4e7",
        "surface-container-lowest": "#ffffff",
        "surface-container-high": "#e3e9ec",
        "surface-bright": "#f8f9fa",
        "on-error-container": "#752121",
        "on-tertiary-fixed-variant": "#f9f7ff",
        "secondary-fixed-dim": "#c7d5ed",
        "on-secondary-fixed-variant": "#4e5c71",
        "error": "#9f403d",
        "background": "#f8f9fa",
        "on-primary-container": "#525252",
        "tertiary": "#0053dc",
        "on-surface": "#2b3437",
        "inverse-on-surface": "#9b9d9e",
        "on-tertiary-fixed": "#ffffff",
        "surface-container-low": "#f1f4f6",
        "surface": "#f8f9fa",
        "surface-dim": "#d1dce0",
        "on-secondary-fixed": "#324053",
        "on-background": "#2b3437",
        "primary-fixed-dim": "#d4d4d4",
        "primary-dim": "#525252",
        "outline-variant": "#abb3b7",
        "primary": "#5e5e5e",
        "on-tertiary": "#faf8ff",
        "secondary-dim": "#465468",
        "tertiary-fixed-dim": "#2d68f0",
        "outline": "#737c7f",
        "primary-container": "#e2e2e2",
        "secondary-fixed": "#d5e3fc",
        "tertiary-container": "#3e76fe",
        "secondary-container": "#d5e3fc",
        "surface-variant": "#dbe4e7",
        "on-secondary-container": "#455367",
        "on-primary-fixed": "#3f3f3f",
        "on-error": "#fff7f6",
        "on-surface-variant": "#586064",
        "primary-fixed": "#e2e2e2",
        "on-primary": "#f8f8f8",
        "secondary": "#526074",
        "tertiary-dim": "#0049c2",
        "on-secondary": "#f8f8ff",
        "error-dim": "#4e0309",
        "on-tertiary-container": "#000000",
        "on-primary-fixed-variant": "#5b5b5b",
        "surface-container": "#eaeff1",
        "inverse-surface": "#0c0f10",
        "error-container": "#fe8983",
      },
      borderRadius: {
        DEFAULT: "0.125rem",
        lg: "0.25rem",
        xl: "0.5rem",
        full: "0.75rem",
      },
      // Trong file tailwind.config.ts
      fontFamily: {
        headline: ["var(--font-manrope)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
        label: ["var(--font-inter)", "sans-serif"],
      },
    },
  },
  plugins: [
    // Bạn cần cài đặt 2 package này nếu muốn dùng các class của chúng:
    // npm install -D @tailwindcss/forms @tailwindcss/container-queries
    require("@tailwindcss/forms"),
    require("@tailwindcss/container-queries"),
  ],
};

export default config;