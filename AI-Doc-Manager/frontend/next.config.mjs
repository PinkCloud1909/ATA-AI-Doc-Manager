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
        // Use the NEXT_PUBLIC_ prefixed var (set via Dockerfile build arg)
        // with a fallback to the unprefixed name for backward compatibility.
        pathname: `/${process.env.NEXT_PUBLIC_GCS_BUCKET_NAME || process.env.GCS_BUCKET_NAME || ""}/**`,
      },
    ],
  },

  // Proxy /api/* → FastAPI backend
  async rewrites() {
    // Use explicit BACKEND_URL when provided. When developing locally
    // prefer localhost; in containerized deployments the service name
    // `backend` is resolvable via Docker network.
    const backendUrl =
      process.env.BACKEND_URL ||
      (process.env.NODE_ENV === "development"
        ? "http://localhost:8000"
        : "http://backend:8080");

    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
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
    // Use the NEXT_PUBLIC_ prefixed var (set via Dockerfile build arg)
    // with a fallback to the unprefixed name for backward compatibility.
    NEXT_PUBLIC_GCS_BUCKET_NAME: process.env.NEXT_PUBLIC_GCS_BUCKET_NAME ?? process.env.GCS_BUCKET_NAME ?? "",
    NEXT_PUBLIC_GCP_PROJECT_ID: process.env.NEXT_PUBLIC_GCP_PROJECT_ID ?? process.env.GCP_PROJECT_ID ?? "",
  },
};

export default nextConfig;
