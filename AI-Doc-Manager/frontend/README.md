# 🗂️ Runbook Platform — Frontend (GCP Edition)

> Next.js frontend cho hệ thống quản lý runbook tích hợp AI trên Google Cloud Platform.

---

## 📋 Mục lục

1. [Kiến trúc tổng quan](#1-kiến-trúc-tổng-quan)
2. [Cấu trúc thư mục](#2-cấu-trúc-thư-mục)
3. [Thay đổi so với kiến trúc cũ](#3-thay-đổi-so-với-kiến-trúc-cũ)
4. [Chi tiết từng file](#4-chi-tiết-từng-file)
5. [Luồng dữ liệu quan trọng](#5-luồng-dữ-liệu-quan-trọng)
6. [Setup & Deploy](#6-setup--deploy)

---

## 1. Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                       │
│                                                                 │
│  ┌──────────────┐    ┌─────────────────┐    ┌───────────────┐  │
│  │  Next.js     │    │    FastAPI       │    │  Gemini API   │  │
│  │  (Cloud Run) │───▶│  + Google ADK   │───▶│  (LLM)        │  │
│  └──────────────┘    │  (Cloud Run)    │    └───────────────┘  │
│                      └────────┬────────┘                        │
│  ┌──────────────┐             │                                  │
│  │  Firebase    │    ┌────────┴────────────────────┐            │
│  │  Auth        │    │                             │            │
│  │  (IAM/JWT)   │    ▼                             ▼            │
│  └──────────────┘  ┌──────────────┐    ┌──────────────────┐    │
│                    │  PostgreSQL   │    │  Vertex AI       │    │
│  ┌──────────────┐  │  (Cloud SQL) │    │  Vector Search   │    │
│  │  Google      │  └──────────────┘    └──────────────────┘    │
│  │  Cloud       │                                               │
│  │  Storage     │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Công nghệ | Ghi chú |
|---|---|---|
| UI | Next.js 14 (App Router) | Deploy trên Cloud Run |
| Auth | Firebase Authentication | Email/Password, Google SSO |
| Backend | FastAPI + Google ADK | Cloud Run |
| LLM | Gemini (via Vertex AI) | `gemini-1.5-pro` |
| Relational DB | PostgreSQL (Cloud SQL) | Quản lý metadata |
| Vector DB | Vertex AI Vector Search | Semantic search tài liệu |
| Object Storage | Google Cloud Storage | Lưu file docx/pdf |

---

## 2. Cấu trúc thư mục

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── providers.tsx               ← Firebase session sync + React Query
│   │   ├── (auth)/
│   │   │   └── login/page.tsx          ← Firebase email/password login
│   │   └── (main)/
│   │       ├── layout.tsx
│   │       ├── dashboard/page.tsx
│   │       ├── documents/
│   │       │   ├── page.tsx
│   │       │   ├── upload/page.tsx
│   │       │   └── [id]/page.tsx       ← GCS Signed URL download
│   │       ├── approvals/page.tsx
│   │       ├── chat/page.tsx
│   │       ├── generate/page.tsx
│   │       ├── reports/page.tsx
│   │       └── admin/
│   │           ├── users/page.tsx
│   │           └── roles/page.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   ├── documents/
│   │   │   ├── UploadForm.tsx          ← GCS 2-step upload với progress stages
│   │   │   ├── DocumentTable.tsx
│   │   │   ├── VersionHistory.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   └── ReviewForm.tsx
│   │   ├── approvals/
│   │   │   └── ApprovalActions.tsx
│   │   └── chat/
│   │       ├── ChatWindow.tsx
│   │       ├── MessageBubble.tsx
│   │       ├── SourceCitation.tsx      ← Hiển thị Vertex AI relevance score
│   │       └── VoiceInput.tsx
│   ├── lib/
│   │   ├── auth/
│   │   │   └── firebase.ts             ← Firebase init, signIn, getIdToken [MỚI]
│   │   ├── gcs/
│   │   │   └── index.ts                ← GCS URL builder, uploadToGcs [MỚI]
│   │   └── api/
│   │       ├── client.ts               ← Axios + Firebase token interceptor [CẬP NHẬT]
│   │       ├── auth.ts                 ← Firebase-based auth [CẬP NHẬT]
│   │       ├── documents.ts            ← GCS 2-step upload [CẬP NHẬT]
│   │       ├── approvals.ts
│   │       ├── chat.ts                 ← Async WebSocket cho Firebase token [CẬP NHẬT]
│   │       └── reports.ts
│   ├── hooks/
│   │   ├── useAuth.ts                  ← Firebase error codes [CẬP NHẬT]
│   │   ├── useDocuments.ts             ← Upload stage tracking, Signed URL [CẬP NHẬT]
│   │   ├── useChat.ts                  ← Async WS connection [CẬP NHẬT]
│   │   └── usePermission.ts
│   ├── stores/
│   │   ├── authStore.ts                ← Không lưu JWT nữa, chỉ lưu User profile [CẬP NHẬT]
│   │   └── chatStore.ts
│   └── types/
│       ├── document.ts                 ← Thêm GCS fields, Vertex AI fields [CẬP NHẬT]
│       ├── user.ts                     ← Thêm firebase_uid [CẬP NHẬT]
│       └── chat.ts                     ← Thêm vertex_distance, gcs_path [CẬP NHẬT]
├── next.config.ts                      ← GCS image domain, Cloud Run output [CẬP NHẬT]
├── Dockerfile                          ← Standalone output cho Cloud Run [CẬP NHẬT]
├── .env.example                        ← Firebase + GCS env vars [CẬP NHẬT]
└── package.json                        ← Thêm firebase SDK [CẬP NHẬT]
```

---

## 3. Thay đổi so với kiến trúc cũ

### 3.1 Authentication: Custom JWT → Firebase Auth

| | Cũ (MinIO + custom JWT) | Mới (GCP + Firebase) |
|---|---|---|
| Đăng nhập | POST `/auth/login` → custom JWT | Firebase `signInWithEmailAndPassword` |
| Token | JWT tự tạo, lưu localStorage | Firebase ID Token, tự rotate |
| Refresh | POST `/auth/refresh-token` | Firebase SDK tự động (không cần code) |
| Lưu trữ | `localStorage` thủ công | Firebase IndexedDB (automatic) |
| Axios header | `Bearer <custom_jwt>` | `Bearer <firebase_id_token>` |
| Token hết hạn | Interceptor gọi refresh endpoint | Firebase tự refresh, interceptor chỉ await `getIdToken()` |

**File thay đổi:**
```
lib/auth/firebase.ts     ← MỚI: Firebase init
lib/api/client.ts        ← interceptor dùng getCurrentIdToken() thay vì localStorage
lib/api/auth.ts          ← login = Firebase signIn + fetch /auth/me
stores/authStore.ts      ← bỏ accessToken/refreshToken, chỉ giữ User profile
app/providers.tsx        ← thêm FirebaseSessionSync để sync khi token rotate
```

### 3.2 Object Storage: MinIO → Google Cloud Storage

| | Cũ (MinIO) | Mới (GCS) |
|---|---|---|
| Upload | Multipart qua backend | **2-step**: Signed URL → PUT trực tiếp lên GCS |
| Download | MinIO presigned URL (1 request) | GCS Signed URL (lazy, TTL 15 phút) |
| File URL | `http://minio:9000/bucket/path` | `gs://bucket/path` hoặc `https://storage.googleapis.com/...` |
| URL builder | Không có | `lib/gcs/index.ts` → `gcsPublicUrl()`, `gcsFilename()` |
| Progress | `onUploadProgress` trong axios | `XMLHttpRequest` PUT trực tiếp lên GCS |

**Upload flow mới (3 bước):**
```
Frontend                Backend              GCS
   │                       │                  │
   │  POST /signed-url      │                  │
   │──────────────────────▶│                  │
   │  { signed_url, path } │                  │
   │◀──────────────────────│                  │
   │                       │                  │
   │  PUT file (XHR)       │                  │
   │─────────────────────────────────────────▶│
   │  200 OK               │                  │
   │◀─────────────────────────────────────────│
   │                       │                  │
   │  POST /confirm-upload  │                  │
   │──────────────────────▶│                  │
   │  Document record      │                  │
   │◀──────────────────────│                  │
```

**File thay đổi:**
```
lib/gcs/index.ts         ← MỚI: GCS utilities
lib/api/documents.ts     ← upload = 3-step flow, getDownloadUrl
hooks/useDocuments.ts    ← thêm stage tracking, useDownloadUrl
components/UploadForm    ← step indicator (signing/uploading/confirming)
components/[id]/page     ← download button dùng Signed URL
types/document.ts        ← thêm original_filename, size_bytes, vertex_index_id
```

### 3.3 Vector Search: ChromaDB → Vertex AI

Frontend không gọi Vertex AI trực tiếp (backend xử lý), nhưng response thay đổi:

| | Cũ (ChromaDB) | Mới (Vertex AI) |
|---|---|---|
| Relevance field | `relevance_score` (0-1) | `vertex_distance` (cosine) + `relevance_score` |
| Source display | `document_id` + `file_link` | `document_id` + `gcs_path` + `original_filename` |

**File thay đổi:**
```
types/chat.ts            ← thêm vertex_distance, gcs_path, original_filename
components/SourceCitation← hiển thị mini relevance bar từ vertex_distance
```

### 3.4 WebSocket: Local → Cloud Run

Cloud Run hỗ trợ WebSocket nhưng cần:
- Firebase token trong query param (WS không có Authorization header)
- Backend enable WebSocket support

```typescript
// Cũ: token từ localStorage, đồng bộ
const ws = new WebSocket(`ws://...?token=${localStorage.getItem("access_token")}`)

// Mới: token từ Firebase, async
const idToken = await getCurrentIdToken()  // await Firebase
const ws = new WebSocket(`wss://...?token=${idToken}`)
```

---

## 4. Chi tiết từng file

### `lib/auth/firebase.ts` ⭐ MỚI
Khởi tạo Firebase App (singleton pattern). Export:
- `signInAndGetToken(email, password)` — đăng nhập, trả về ID Token
- `getCurrentIdToken()` — lấy token hiện tại (auto-refresh nếu cần)
- `signOut()` — đăng xuất Firebase
- `onTokenRefresh(callback)` — subscribe khi token rotate

### `lib/gcs/index.ts` ⭐ MỚI
Tiện ích làm việc với GCS:
- `gcsPublicUrl(gcsPath)` — chuyển `gs://bucket/path` → HTTPS URL
- `uploadToGcs(signedUrl, file, onProgress)` — PUT trực tiếp lên GCS bằng XHR
- `gcsFilename(path)` — lấy tên file từ path
- `isPdf(filename)`, `isDocx(filename)` — kiểm tra loại file
- `formatFileSize(bytes)` — format kích thước file

### `lib/api/client.ts` 🔄 CẬP NHẬT
- Interceptor dùng `await getCurrentIdToken()` thay vì `localStorage.getItem`
- Không cần queue retry logic phức tạp (Firebase handle refresh)
- Redirect `/login` khi 401

### `lib/api/documents.ts` 🔄 CẬP NHẬT
- `getSignedUploadUrl(filename, contentType)` — lấy V4 Signed URL
- `upload(payload, onProgress)` — orchestrate 3 bước GCS upload
- `getDownloadUrl(id)` — lấy Signed URL để download (TTL 15 phút)

### `hooks/useDocuments.ts` 🔄 CẬP NHẬT
- `useUploadDocument()` — thêm `stage` tracking (signing/uploading/confirming)
- `useDownloadUrl(id, enabled)` — lazy fetch, staleTime 14 phút

### `app/providers.tsx` 🔄 CẬP NHẬT
- `FirebaseSessionSync` component: lắng nghe `onIdTokenChanged`
- Tự động fetch `/auth/me` khi Firebase session restore (reload trang)

---

## 5. Luồng dữ liệu quan trọng

### Authentication Flow
```
User nhập email/password
   → Firebase signInWithEmailAndPassword
   → Firebase lưu session (IndexedDB)
   → authApi.me() → FastAPI /auth/me
   → FastAPI verify Firebase ID Token (google-auth-library)
   → Trả về User + roles từ PostgreSQL
   → authStore.setUser(user)
   → redirect /dashboard
```

### Upload Flow (GCS)
```
User chọn file
   → UploadForm.handleSubmit()
   → useUploadDocument.mutateAsync()
   → [stage: signing]   POST /documents/signed-upload-url → signed_url, gcs_path
   → [stage: uploading] XHR PUT file → GCS (progress callback)
   → [stage: confirming] POST /documents/confirm-upload → Document record
   → React Query invalidate → danh sách cập nhật
```

### Chat Flow (Vertex AI + Gemini)
```
User gửi tin nhắn
   → useChat.sendMessage()
   → await getCurrentIdToken()       (Firebase, async)
   → new WebSocket(url?token=...)
   → WS onopen → send message
   
Backend (FastAPI + Google ADK):
   → Vertex AI Vector Search: tìm top-k tài liệu APPROVED
   → Nếu có kết quả: RAG với Gemini
   → Nếu không có: Gemini trực tiếp
   → Stream token-by-token qua WS

Frontend:
   → onToken → appendToken (streaming)
   → onSources → finalizeMessage (Vertex AI metadata)
   → onDone → setStreaming(false)
```

---

## 6. Setup & Deploy

### Local Development

```bash
cp .env.example .env.local
# Điền Firebase config và GCS settings

npm install
npm run dev
```

### Deploy lên Cloud Run

```bash
# Build image
docker build \
  --build-arg NEXT_PUBLIC_FIREBASE_API_KEY=$FIREBASE_API_KEY \
  --build-arg NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$FIREBASE_AUTH_DOMAIN \
  --build-arg NEXT_PUBLIC_FIREBASE_PROJECT_ID=$GCP_PROJECT_ID \
  --build-arg NEXT_PUBLIC_FIREBASE_APP_ID=$FIREBASE_APP_ID \
  --build-arg NEXT_PUBLIC_GCS_BASE_URL=$GCS_BASE_URL \
  --build-arg NEXT_PUBLIC_GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
  --build-arg NEXT_PUBLIC_API_URL=$BACKEND_CLOUD_RUN_URL/api/v1 \
  -t asia.gcr.io/$GCP_PROJECT_ID/runbook-frontend:latest .

# Push lên GCR
docker push asia.gcr.io/$GCP_PROJECT_ID/runbook-frontend:latest

# Deploy Cloud Run
gcloud run deploy runbook-frontend \
  --image asia.gcr.io/$GCP_PROJECT_ID/runbook-frontend:latest \
  --region asia-southeast1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars BACKEND_URL=$BACKEND_CLOUD_RUN_URL
```

### GCS Bucket CORS (bắt buộc cho Signed URL upload)

```json
[
  {
    "origin": ["https://your-frontend.run.app", "http://localhost:3000"],
    "method": ["PUT", "GET"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```

```bash
gsutil cors set cors.json gs://$GCS_BUCKET_NAME
```

### Firebase Setup

```bash
# Bật Email/Password trong Firebase Console
# Authentication → Sign-in method → Email/Password → Enable

# Thêm domain vào Authorized domains
# Authentication → Settings → Authorized domains → Add domain
# Thêm: your-frontend.run.app
```
