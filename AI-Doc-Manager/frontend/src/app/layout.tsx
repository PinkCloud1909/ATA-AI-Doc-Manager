import type { Metadata } from "next";
// Import 2 font nguyên bản của thiết kế từ thư viện tối ưu của Next.js
import { Inter, Manrope } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

// Cấu hình font Inter cho nội dung (body)
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

// Cấu hình font Manrope cho các tiêu đề (heading)
const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Runbook Platform",
  description: "Hệ thống quản lý tài liệu kỹ thuật tích hợp AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        {/* Nhúng bộ icon Material Symbols từ CDN */}
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      {/* - Nhúng 2 biến font vào body
        - Dùng bg-background và text-on-surface để màu nền/chữ chuẩn theo Material Design 3
      */}
      <body
        className={`${inter.variable} ${manrope.variable} font-body bg-background text-on-surface m-0 p-0 box-border`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
