# 📡 API Endpoints Reference

## Cấu trúc API Backend

```
Base URL: http://localhost:8000 (development)
API Prefix: /api/v1 (hoặc / tuỳ cấu hình)
Auth: Bearer Token (Firebase ID Token)
```

---

## 🔑 Authentication Endpoints

### 1. Lấy Profile Người Dùng Hiện Tại

```
GET /auth/me
Authorization: Bearer <firebase-token>

Response (200):
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "firebase_uid": "firebase-uid",
  "roles": ["admin", "reviewer"],
  "created_at": "2026-04-20T10:00:00Z"
}
```

**Frontend Call:**

```typescript
import { authApi } from "@/lib/api/auth";

const user = await authApi.me();
console.log(user.email);
```

### 2. Đăng Xuất

```
POST /auth/logout
Authorization: Bearer <firebase-token>

Response (200):
{ "message": "Logged out successfully" }
```

**Frontend Call:**

```typescript
await authApi.logout();
```

---

## 📄 Documents Endpoints

### 1. Danh Sách Documents

```
GET /documents?skip=0&limit=20&document_type=runbook&sort_by=created_at

Query Parameters:
  skip: int (offset, default=0)
  limit: int (page size, default=20)
  document_type: str (runbook, template, guideline, etc.)
  sort_by: str (created_at, updated_at, title)
  search: str (tìm kiếm trong tiêu đề/nội dung)

Response (200):
{
  "items": [
    {
      "id": "doc-uuid-1",
      "title": "API Documentation",
      "document_type": "runbook",
      "file_link": "gs://bucket/path/file.pdf",
      "created_by": "user-id",
      "created_at": "2026-04-20T10:00:00Z",
      "updated_at": "2026-04-21T15:30:00Z",
      "is_approved": true,
      "approval_status": "approved"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

**Frontend Call:**

```typescript
import { documentsApi } from "@/lib/api/documents";

const docs = await documentsApi.list({
  skip: 0,
  limit: 20,
  document_type: "runbook",
});
console.log(docs.items);
```

### 2. Chi Tiết Document

```
GET /documents/{document_id}

Response (200):
{
  "id": "doc-uuid",
  "title": "API Documentation",
  "description": "Complete API reference",
  "document_type": "runbook",
  "file_link": "gs://bucket/path/file.pdf",
  "content": "# Full document content...",
  "created_by": {
    "id": "user-id",
    "name": "John Doe"
  },
  "version": 1,
  "is_approved": true
}
```

**Frontend Call:**

```typescript
const doc = await documentsApi.getById("doc-uuid");
```

### 3. Tạo Document (Step 1: Lấy Signed Upload URL)

```
POST /documents/signed-upload-url

Request Body:
{
  "filename": "guide.pdf",
  "content_type": "application/pdf",
  "size_bytes": 1024000
}

Response (200):
{
  "upload_url": "https://storage.googleapis.com/bucket/...?signature=...",
  "gcs_path": "gs://bucket/path/guide.pdf",
  "expires_in": 3600
}
```

**Frontend Call:**

```typescript
// Step 1: Lấy upload URL
const uploadResponse = await documentsApi.getSignedUploadUrl({
  filename: file.name,
  content_type: file.type,
  size_bytes: file.size,
});

// Step 2: Upload file trực tiếp tới GCS (client-side)
await uploadToGcs(uploadResponse.upload_url, file);

// Step 3: Xem QUICK_SETUP.md → documents.ts
```

### 4. Confirm Upload Và Tạo Document (Step 2)

```
POST /documents/confirm-upload

Request Body:
{
  "gcs_path": "gs://bucket/path/guide.pdf",
  "original_filename": "guide.pdf",
  "content_type": "application/pdf",
  "size_bytes": 1024000,
  "document_type": "runbook",
  "document_group_id": null  # Hoặc ID group nếu version mới
}

Response (201):
{
  "id": "new-doc-uuid",
  "title": "guide.pdf",
  "file_link": "gs://bucket/path/guide.pdf",
  "created_at": "2026-04-20T10:00:00Z"
}
```

### 5. Cập Nhật Document

```
PUT /documents/{document_id}

Request Body:
{
  "title": "New Title",
  "description": "Updated description",
  "document_type": "template"
}

Response (200):
{
  "id": "doc-uuid",
  "title": "New Title",
  "updated_at": "2026-04-21T10:00:00Z"
}
```

### 6. Xóa Document

```
DELETE /documents/{document_id}

Response (204): No Content
```

---

## ✅ Reviews Endpoints

### 1. Danh Sách Review

```
GET /reviews?document_id={doc_id}&skip=0&limit=20

Response (200):
{
  "items": [
    {
      "id": "review-uuid",
      "document_id": "doc-uuid",
      "reviewer": { "id": "user-id", "name": "Jane Smith" },
      "comment": "Needs revision",
      "rating": 7,
      "status": "pending",  # pending, approved, rejected
      "created_at": "2026-04-20T10:00:00Z"
    }
  ],
  "total": 5
}
```

### 2. Tạo Review

```
POST /reviews

Request Body:
{
  "document_id": "doc-uuid",
  "comment": "Excellent documentation",
  "rating": 9,
  "status": "approved"
}

Response (201):
{
  "id": "new-review-uuid",
  "document_id": "doc-uuid",
  "rating": 9
}
```

### 3. Cập Nhật Review

```
PUT /reviews/{review_id}

Request Body:
{
  "comment": "Updated comment",
  "rating": 8
}

Response (200):
{
  "id": "review-uuid",
  "rating": 8,
  "updated_at": "2026-04-21T10:00:00Z"
}
```

---

## 🎯 Approvals Endpoints

### 1. Danh Sách Approval

```
GET /approvals?document_id={doc_id}&status=pending

Response (200):
{
  "items": [
    {
      "id": "approval-uuid",
      "document_id": "doc-uuid",
      "document_title": "API Guide",
      "requested_by": { "id": "user-id", "name": "John Doe" },
      "assigned_to": { "id": "approver-id", "name": "Manager" },
      "status": "pending",  # pending, approved, rejected
      "created_at": "2026-04-20T10:00:00Z"
    }
  ],
  "total": 3
}
```

### 2. Phê Duyệt Document

```
POST /approvals/{approval_id}/approve

Request Body:
{
  "comment": "Looks good!"
}

Response (200):
{
  "id": "approval-uuid",
  "status": "approved",
  "approved_at": "2026-04-21T10:00:00Z"
}
```

### 3. Từ Chối Document

```
POST /approvals/{approval_id}/reject

Request Body:
{
  "comment": "Need more details",
  "reason": "Incomplete information"
}

Response (200):
{
  "id": "approval-uuid",
  "status": "rejected",
  "rejected_at": "2026-04-21T10:00:00Z"
}
```

---

## 💬 QA (Chat) Endpoints

### 1. Chat với AI

```
POST /qa/chat

Request Body:
{
  "message": "What is the API endpoint for creating documents?",
  "document_id": "doc-uuid",  # Optional, provide context
  "conversation_id": "conv-uuid"  # Optional
}

Response (200):
{
  "response": "The API endpoint for creating documents is POST /documents/confirm-upload...",
  "conversation_id": "conv-uuid",
  "sources": ["doc-uuid-1", "doc-uuid-2"]
}
```

**Frontend Call:**

```typescript
import { qaApi } from "@/lib/api/chat";

const response = await qaApi.chat({
  message: "How to upload?",
  document_id: "doc-123",
});
```

---

## 🏥 Health Check

```
GET /health

Response (200):
{
  "status": "healthy",
  "timestamp": "2026-04-21T10:00:00Z"
}
```

---

## 📊 Common HTTP Status Codes

| Code    | Meaning       | Action                                   |
| ------- | ------------- | ---------------------------------------- |
| **200** | OK            | ✅ Thành công                            |
| **201** | Created       | ✅ Tạo thành công                        |
| **204** | No Content    | ✅ Xóa/Update thành công                 |
| **400** | Bad Request   | ❌ Request không hợp lệ (kiểm tra body)  |
| **401** | Unauthorized  | ❌ Token hết hạn (đăng xuất + đăng nhập) |
| **403** | Forbidden     | ❌ Không có quyền truy cập               |
| **404** | Not Found     | ❌ Resource không tồn tại                |
| **409** | Conflict      | ❌ Xung đột dữ liệu (bản ghi đã tồn tại) |
| **422** | Unprocessable | ❌ Validation error (xem response body)  |
| **500** | Server Error  | ❌ Backend lỗi (kiểm tra logs)           |

---

## 🔐 Error Response Format

```json
{
  "detail": "Error message here",
  "error_code": "INVALID_REQUEST",
  "request_id": "req-uuid-123",
  "timestamp": "2026-04-21T10:00:00Z"
}
```

---

## 🧪 Test Endpoint với Curl

```bash
# 1. Health Check
curl http://localhost:8000/health

# 2. Lấy Profile (cần token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/auth/me

# 3. List Documents
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/documents?limit=5"

# 4. Swagger UI (interactive)
open http://localhost:8000/docs
```

---

## 🎓 Frontend Examples

### Ví dụ 1: Tải danh sách documents khi mount component

```typescript
import { useEffect, useState } from "react"
import { documentsApi } from "@/lib/api/documents"
import { Document } from "@/types/document"

export function DocumentList() {
  const [docs, setDocs] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    documentsApi.list({ limit: 10 })
      .then(result => setDocs(result.items))
      .catch(err => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading...</div>
  return (
    <ul>
      {docs.map(doc => (
        <li key={doc.id}>{doc.title}</li>
      ))}
    </ul>
  )
}
```

### Ví dụ 2: Tạo Review

```typescript
const handleSubmitReview = async (docId: string, rating: number) => {
  try {
    const review = await reviewsApi.create({
      document_id: docId,
      rating: rating,
      comment: "Great documentation!",
    });
    console.log("Review created:", review);
  } catch (error) {
    console.error("Failed to create review:", error);
  }
};
```

### Ví dụ 3: Phê duyệt Document

```typescript
const handleApprove = async (approvalId: string) => {
  try {
    const result = await approvalsApi.approve(approvalId, {
      comment: "Approved!",
    });
    console.log("Approved:", result);
  } catch (error) {
    console.error("Approval failed:", error);
  }
};
```

---

## 📚 Liên kết

- [FRONTEND_BACKEND_GUIDE.md](./FRONTEND_BACKEND_GUIDE.md) - Hướng dẫn chi tiết
- [QUICK_SETUP.md](./QUICK_SETUP.md) - Cấu hình nhanh
- Swagger: http://localhost:8000/docs (khi backend chạy)
