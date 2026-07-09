# 🚀 Quick Setup: Frontend gọi Backend

## 📌 Cách nhanh nhất

### 1️⃣ Cấu hình Frontend

Tạo file `.env.local` trong thư mục `frontend/`:

```bash
cd AI-Doc-Manager/frontend
# Copy từ .env.example
cp .env.example .env.local
```

**Chỉnh sửa `.env.local`:**

```env
# ─── Chế độ Mock (Development nhanh - không cần Backend)
NEXT_PUBLIC_USE_MOCK=true

# ─── Backend (Khi chạy Docker Compose hoặc backend thực)
# NEXT_PUBLIC_USE_MOCK=false
# NEXT_PUBLIC_API_URL=http://localhost:8000

# ─── Firebase (Nếu dùng auth thực)
NEXT_PUBLIC_FIREBASE_API_KEY=YOUR_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-gcp-project-id
# ... (xem .env.example)

# ─── GCS (Nếu dùng Google Cloud Storage)
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=runbook-documents
NEXT_PUBLIC_GCS_BASE_URL=https://storage.googleapis.com/runbook-documents
```

### 2️⃣ Chạy Frontend

#### **Option A: Mock Mode (Recommended for quick test)**

```bash
cd AI-Doc-Manager/frontend
npm install
NEXT_PUBLIC_USE_MOCK=true npm run dev
# Mở: http://localhost:3000
```

#### **Option B: Docker Compose (Full stack)**

```bash
cd AI-Doc-Manager

# Tạo .env root nếu chưa có
cat > .env << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ai_doc_manager
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
EOF

# Chạy toàn bộ stack
docker-compose up --build

# ✅ Frontend: http://localhost:3000
# ✅ Backend:  http://localhost:8000
# ✅ Swagger:  http://localhost:8000/docs
```

---

## ✅ Verify FE → BE Connection

### 1. Kiểm tra API Base URL

**Mở DevTools (F12) → Console:**

```javascript
// Xem config hiện tại
console.log(process.env.NEXT_PUBLIC_API_URL);
console.log(process.env.NEXT_PUBLIC_USE_MOCK);

// Hoặc xem trong Network tab:
// - Nếu mock: request tới `/api/...`
// - Nếu thực: request tới `http://localhost:8000/...`
```

### 2. Kiểm tra Network Request

**DevTools → Network tab:**

1. Thực hiện hành động (ví dụ: đăng nhập, lấy danh sách documents)
2. Xem request:
   - ✅ **URL**: `http://localhost:8000/...` hoặc `/api/...`
   - ✅ **Headers**: `Authorization: Bearer <token>`
   - ✅ **Status**: 200/201 (không 502, 401, CORS error)

### 3. Backend Health Check

```bash
# Kiểm tra backend sống
curl http://localhost:8000/health

# Kiểm tra Swagger docs
curl http://localhost:8000/docs
```

---

## 🛠️ Troubleshooting

### **Vấn đề: 502 Bad Gateway**

```
→ Backend không chạy
→ Giải pháp: docker-compose up --build
```

### **Vấn đề: CORS Error**

```
Access to XMLHttpRequest at 'http://localhost:8000/...'
from origin 'http://localhost:3000' has been blocked by CORS policy
```

→ Kiểm tra Backend CORS config
→ Đảm bảo `NEXT_PUBLIC_API_URL` trùng với Backend host

### **Vấn đề: 401 Unauthorized**

```
→ Firebase token hết hạn
→ Giải pháp: Đăng xuất + Đăng nhập lại
```

### **Vấn đề: Mock mode không hoạt động**

```
→ Kiểm tra: NEXT_PUBLIC_USE_MOCK=true
→ Nếu không có biến, sẽ mặc định = true
```

---

## 📖 Các tài liệu liên quan

- `FRONTEND_BACKEND_GUIDE.md` - Hướng dẫn chi tiết
- `.env.example` - Ví dụ cấu hình
- Backend Swagger: `http://localhost:8000/docs`

---

## 🎯 Lưu ý quan trọng

|                  | Mock Mode   | Docker Compose       |
| ---------------- | ----------- | -------------------- |
| **Setup**        | 2 phút      | 10 phút              |
| **Tốc độ**       | ⚡ Nhanh    | 🟡 Chậm (cold start) |
| **Database**     | ✗ Không     | ✅ Có (PostgreSQL)   |
| **Firebase**     | ✗ Không     | ✅ Có                |
| **Cloud Upload** | ✗ Không     | ✅ Có (MinIO)        |
| **Khi nào dùng** | Dev/Test UI | Test API thực        |
