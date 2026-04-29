/** @type {import('next').NextConfig} */
const nextConfig = {
  // "standalone" tạo ra bundle tối ưu cho Cloud Run
  output: "standalone",

  // Cho phép next/image phục vụ ảnh từ Google Cloud Storage
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "storage.googleapis.com",
        pathname: `/${process.env.GCS_BUCKET_NAME}/**`,
      },
    ],
  },

  // Proxy /api/* → FastAPI backend
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL ?? "http://localhost:8000"}/api/:path*`,
      },
    ];
  },

  // Security Headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://apis.google.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob: https://storage.googleapis.com",
              "connect-src 'self' https://*.googleapis.com wss: ws:",
            ].join("; "),
          },
        ],
      },
    ];
  },

  // Env vars exposed to browser
  env: {
    NEXT_PUBLIC_GCS_BUCKET_NAME: process.env.GCS_BUCKET_NAME ?? "",
    NEXT_PUBLIC_GCP_PROJECT_ID: process.env.GCP_PROJECT_ID ?? "",
  },
};

export default nextConfig;
