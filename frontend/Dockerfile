# ── Stage 1: deps ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci


# ── Stage 2: build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Backend URL dùng cho Next.js rewrites trong next.config.mjs
ARG BACKEND_URL
ENV BACKEND_URL=$BACKEND_URL

# Build-time env vars public, được bake vào bundle Next.js
ARG NEXT_PUBLIC_API_URL=/api/v1
ARG NEXT_PUBLIC_FIREBASE_API_KEY
ARG NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ARG NEXT_PUBLIC_FIREBASE_PROJECT_ID
ARG NEXT_PUBLIC_FIREBASE_APP_ID
ARG NEXT_PUBLIC_GCS_BASE_URL
ARG NEXT_PUBLIC_GCS_BUCKET_NAME
ARG NEXT_PUBLIC_WS_URL
ARG NEXT_PUBLIC_USE_MOCK

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_FIREBASE_API_KEY=$NEXT_PUBLIC_FIREBASE_API_KEY
ENV NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ENV NEXT_PUBLIC_FIREBASE_PROJECT_ID=$NEXT_PUBLIC_FIREBASE_PROJECT_ID
ENV NEXT_PUBLIC_FIREBASE_APP_ID=$NEXT_PUBLIC_FIREBASE_APP_ID
ENV NEXT_PUBLIC_GCS_BASE_URL=$NEXT_PUBLIC_GCS_BASE_URL
ENV NEXT_PUBLIC_GCS_BUCKET_NAME=$NEXT_PUBLIC_GCS_BUCKET_NAME
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_USE_MOCK=$NEXT_PUBLIC_USE_MOCK

RUN npm run build


# ── Stage 3: runner ───────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=8080

# BACKEND_URL is injected at runtime by Cloud Run (--set-env-vars).
# Do NOT set it here — an empty build arg would override the runtime value.
# The build stage (builder) already baked the correct URL into the standalone
# output via the --build-arg passed during docker build.

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

USER node

EXPOSE 8080

CMD ["node", "server.js"]
