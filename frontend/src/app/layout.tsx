import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "AI Doc Manager",
  description: "AI-powered document management system with RAG search",
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
        className="font-body bg-background text-on-surface m-0 p-0 box-border"
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
