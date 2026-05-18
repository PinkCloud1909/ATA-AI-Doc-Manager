# Hướng dẫn: Frontend gọi tới Backend

## 📋 Tổng quan kiến trúc

```
┌─────────────────────┐
│   Frontend (FE)     │  Next.js - Port 3000
│   React + TypeScript│
└──────────┬──────────┘
           │ HTTP/REST + Firebase Token
           │
┌──────────▼──────────┐
│   Backend (BE)      │  FastAPI - Port 8000
│   Python            │
│ ├─ /auth           │
│ ├─ /documents      │
│ ├─ /reviews        │
│ ├─ /approvals      │
│ └─ /qa             │
└─────────────────────┘
```

---

## 🔧 1. Cấu hình Base URL

### 1.1 Chỉnh sửa file `.env` hoặc `.env.local`

**Chế độ Mock (Development)**

```env
NEXT_PUBLIC_USE_MOCK=true
# API sẽ gọi local Next.js API routes (/api/...)
```

**Chế độ Real Backend (Production/Staging)**

```env
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_URL=http://localhost:8000
# Hoặc: https://backend.yourdomain.com
```

### 1.2 Cơ chế Auto-Config trong Docker Compose

File `docker-compose.yml` đã config sẵn:

```yaml
frontend:
  environment:
    NEXT_PUBLIC_API_URL: http://backend:8000 # DNS name trong container
```

✅ **Khi chạy Docker Compose, FE tự kết nối được BE**

---

## 🔑 2. Authentication Flow

### 2.1 Firebase Token

Frontend tự động gắn Firebase ID Token vào mỗi request:

```typescript
// lib/api/client.ts (đã cấu hình)
apiClient.interceptors.request.use(async (config) => {
  const token = await getCurrentIdToken(); // Từ Firebase SDK
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 2.2 Backend Verify Token

Backend tự động verify token:

```python
# app/core/security.py
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Verify Firebase ID Token bằng google-auth-library
    # Lấy firebase_uid từ token
    # Tra cứu User trong PostgreSQL
    return user
```

✅ **Không cần gọi /auth/login, Firebase handle toàn bộ**

---

## 📡 3. Cách gọi API từ Frontend

### 3.1 Pattern chung

```typescript
// lib/api/client.ts
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,
})

// Gọi API
const response = await apiClient.get("/documents")
const response = await apiClient.post("/documents", { ... })
```

### 3.2 Ví dụ: Gọi endpoint /auth/me

**Frontend (lib/api/auth.ts):**

```typescript
export const authApi = {
  me: async (): Promise<User> => {
    if (USE_MOCK) {
      return mockMe();
    }
    const { data } = await apiClient.get<User>("/auth/me");
    return data;
  },
};
```

**Backend (app/modules/iam/api/router.py):**

```python
@router.get("/me", response_model=UserResponse)
def get_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

---

## 📋 4. Endpoint Backend sẵn có

### 4.1 Authentication (/auth)

```
GET    /auth/me              → Lấy profile hiện tại
POST   /auth/logout          → Đăng xuất
```

### 4.2 Documents (/documents)

```
GET    /documents             → Danh sách documents
GET    /documents/{id}        → Chi tiết document
POST   /documents             → Tạo mới
PUT    /documents/{id}        → Cập nhật
DELETE /documents/{id}        → Xóa

POST   /documents/signed-upload-url   → Lấy URL upload
POST   /documents/confirm-upload      → Confirm upload thành công
```

### 4.3 Reviews (/reviews)

```
GET    /reviews               → Danh sách review
POST   /reviews               → Tạo review
PUT    /reviews/{id}          → Cập nhật review
```

### 4.4 Approvals (/approvals)

```
GET    /approvals             → Danh sách approval
POST   /approvals/{id}/approve    → Phê duyệt
POST   /approvals/{id}/reject     → Từ chối
```

### 4.5 QA (/qa)

```
POST   /qa/chat               → Chat với AI
```

---

## 🚀 5. Chạy Local Development

### 5.1 Option A: Mock Mode (Nhanh nhất)

```bash
# Terminal 1: Frontend chỉ
cd AI-Doc-Manager/frontend
npm install
npm run dev
# Truy cập: http://localhost:3000
# API dùng mock data → không cần Backend
```

### 5.2 Option B: Real Backend (Docker Compose)

```bash
# Terminal: Từ thư mục gốc
cd AI-Doc-Manager
docker-compose up --build
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# Docs:      http://localhost:8000/docs (Swagger)
```

**Kiểm tra kết nối:**

```bash
# Terminal: Curl test
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/auth/me
```

---

## 🔍 6. Debugging

### 6.1 Network Tab (Chrome DevTools)

1. Mở DevTools → Network tab
2. Thực hiện action → Xem request
3. Kiểm tra:
   - ✅ Status: 200/201
   - ✅ Headers: `Authorization: Bearer ...`
   - ✅ URL: `http://localhost:8000/...`

### 6.2 Backend Logs

```bash
# Nếu chạy Docker
docker logs ai-doc-backend
```

### 6.3 Swagger UI (Backend)

```
http://localhost:8000/docs
```

- Xem tất cả endpoint
- Test trực tiếp (nếu có JWT token)

---

## 📝 7. Tạo API Module mới

### 7.1 Frontend (lib/api/mymodule.ts)

```typescript
import apiClient from "./client";

export const myModuleApi = {
  list: async () => {
    const { data } = await apiClient.get("/mymodule");
    return data;
  },

  create: async (payload: MyPayload) => {
    const { data } = await apiClient.post("/mymodule", payload);
    return data;
  },
};
```

### 7.2 Backend (app/modules/mymodule/api/router.py)

```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/mymodule", tags=["MyModule"])

@router.get("")
def list_items(current_user: User = Depends(get_current_user)):
    # Logic
    return items

@router.post("")
def create_item(payload: MyPayload, current_user: User = Depends(get_current_user)):
    # Logic
    return created_item
```

### 7.3 Register trong Backend (app/main.py)

```python
from app.modules.mymodule.api.router import router as mymodule_router

app.include_router(mymodule_router)
```

---

## ⚡ 8. Một số lưu ý

### 8.1 CORS

- Backend FastAPI đã cấu hình CORS cho FE
- `http://localhost:3000` được phép

### 8.2 Timeout

- Frontend set `timeout: 60_000` ms (60s) vì Cloud Run có cold start chậm
- Backend có health check

### 8.3 Error Handling

- 401 Unauthorized → Redirect về /login (Firebase token hết hạn)
- 403 Forbidden → Kiểm tra quyền user
- 500 Server Error → Kiểm tra backend logs

### 8.4 Database

- PostgreSQL là source of truth
- RAG/Vector search: Chroma vector DB
- File storage: GCS hoặc MinIO

---

## 🎯 Checklist: Đảm bảo FE gọi được BE

- [ ] `.env` hoặc `.env.local` có `NEXT_PUBLIC_API_URL` đúng
- [ ] Backend đang chạy và accessible
- [ ] Firebase config đúng (hoặc dùng mock mode)
- [ ] DevTools → Network tab → Xem request header có `Authorization: Bearer ...`
- [ ] Swagger UI → `http://localhost:8000/docs` → Test endpoint trực tiếp
- [ ] Logs không có error
- [ ] Response trả về đúng format

---

## 📞 Troubleshooting

| Vấn đề               | Giải pháp                                         |
| -------------------- | ------------------------------------------------- |
| **502 Bad Gateway**  | Backend không chạy, kiểm tra `docker-compose up`  |
| **401 Unauthorized** | Firebase token hết hạn, đăng xuất + đăng nhập lại |
| **CORS Error**       | Backend CORS config, hoặc FE địa chỉ không đúng   |
| **Network Timeout**  | Backend đang cold start, chờ 30s                  |
| **Empty Response**   | Kiểm tra response type mismatch, logs backend     |
