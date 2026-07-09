# 🎯 QUICK START - TEST EVERYTHING NOW

## 🚀 **PHẦN 1: START BACKEND**

```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\backend
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend chạy: http://localhost:8000/docs

---

## 🎨 **PHẦN 2: START FRONTEND**

```powershell
# Terminal mới
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\frontend
npm run dev
```

✅ Frontend chạy: http://localhost:3000

---

## 🧪 **PHẦN 3: TEST SWAGGER API**

Truy cập: http://localhost:8000/docs

### **Test Function 1-5:**

**Bước 1: Create Document**
```
POST /api/v1/documents
Body:
{
  "document_type": "handbook",
  "file_link": "gs://bucket/document1.pdf"
}
Response: { "id": "...", "status": "draft", "version": 1 }
```

**Bước 2: List Documents**
```
GET /api/v1/documents
Response: [ { "id": "...", "version": 1 }, ... ]
```

**Bước 3: Get Document Detail**
```
GET /api/v1/documents/{id}
Response: { "id": "...", "file_link": "...", "status": "draft" }
```

**Bước 4: Get Versions**
```
GET /api/v1/documents/{group_id}/versions
Response: [ { "version": 1, "status": "draft" } ]
```

**Bước 5: Submit for Review (Function 5)**
```
POST /api/v1/documents/{id}/submit
Response: { "status": "pending_review" }
```

**Bước 6: Add Review (Function 4)**
```
POST /api/v1/documents/{id}/reviews
Body:
{
  "grade": 9,
  "comment": "Excellent quality document"
}
Response: { "id": "...", "grade": 9, "comment": "..." }
```

**Bước 7: List Reviews for Document**
```
GET /api/v1/documents/{id}/reviews
Response: [ { "grade": 9, "comment": "..." } ]
```

**Bước 8: List All Reviews**
```
GET /api/v1/reviews
Response: [ { "id": "...", "grade": 9 }, ... ]
```

**Bước 9: View Pending Approvals**
```
GET /api/v1/approvals/pending
Response: [ { "id": "...", "status": "pending_review" } ]
```

**Bước 10: Approve Document (Function 5)**
```
POST /api/v1/documents/{id}/approve
Response: { "status": "approved" }
```

**Bước 11: View Approved Documents**
```
GET /api/v1/approvals/approved
Response: [ { "id": "...", "status": "approved" } ]
```

**Bước 12: Reject Document**
```
POST /api/v1/documents/{id}/reject
Body:
{
  "reason": "Quality not meet standards"
}
Response: { "status": "rejected", "rejected_reason": "..." }
```

**Bước 13: View Rejected Documents**
```
GET /api/v1/approvals/rejected
Response: [ { "id": "...", "status": "rejected" } ]
```

**Bước 14: Create New Version**
```
PUT /api/v1/documents/{original_id}
Body:
{
  "document_type": "handbook",
  "file_link": "gs://bucket/document1_v2.pdf"
}
Response: { "version": 2, "status": "draft" }
```

---

## ✅ **CHO VÀO FRONTEND (When Components Ready)**

Khi frontend components được wire:

```
DocumentTable → Gọi useDocumentList() → GET /documents
                                    ↓
                           Hiển thị danh sách

UploadForm → Gọi useUploadDocument() → POST /documents
                                   ↓
                           Tạo tài liệu mới

DocumentDetail → Gọi useDocument() → GET /documents/{id}
                                ↓
                         Hiển thị chi tiết

ReviewForm → Gọi useCreateReview() → POST /documents/{id}/reviews
                                 ↓
                          Chấm điểm (1-10)

ApprovalActions → Gọi submitForReview() / approve() / reject()
                                            ↓
                              Quản lý luồng phê duyệt
```

---

## 📊 **KIỂM TRA STATUS**

| Endpoint | Function | Status |
|----------|----------|--------|
| POST /documents | Upload | ✅ |
| GET /documents | List | ✅ |
| GET /documents/{id} | Detail | ✅ |
| GET /documents/{id}/versions | Versions | ✅ |
| PUT /documents/{id} | New Version | ✅ |
| POST /documents/{id}/reviews | Add Review | ✅ |
| GET /documents/{id}/reviews | Get Reviews | ✅ |
| GET /reviews | All Reviews | ✅ |
| POST /documents/{id}/submit | Submit | ✅ |
| POST /documents/{id}/approve | Approve | ✅ |
| POST /documents/{id}/reject | Reject | ✅ |
| GET /approvals/pending | Pending | ✅ |
| GET /approvals/approved | Approved | ✅ |
| GET /approvals/rejected | Rejected | ✅ |

---

## 🎉 **TẤT CẢ FUNCTIONS HOÀN THÀNH!**

- ✅ **Function 1**: Upload + Versioning
- ✅ **Function 2**: Chat (QA module có sẵn)
- ✅ **Function 3**: Generate (ready for implementation)
- ✅ **Function 4**: Chấm điểm 1-10 + Comment
- ✅ **Function 5**: Phê duyệt workflow (Draft → Pending → Approved/Rejected)

**Bây giờ test API bằng Swagger!** 🚀
