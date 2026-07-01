# Tài liệu Luồng Nghiệp vụ — AI-Doc-Manager (Knowledge Curator)

> **Phiên bản:** 1.0 | **Cập nhật:** 2026-06-03  
> **Môi trường:** Backend FastAPI :8000 | Frontend Next.js :3000

---

## Mục lục

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Luồng Quản lý Người dùng & Phân quyền](#2-luồng-quản-lý-người-dùng--phân-quyền)
3. [Luồng Vòng đời Tài liệu](#3-luồng-vòng-đời-tài-liệu)
4. [Luồng Duyệt & Review Tài liệu](#4-luồng-duyệt--review-tài-liệu)
5. [Luồng Vectorization AI](#5-luồng-vectorization-ai)
6. [Luồng Chat AI (RAG)](#6-luồng-chat-ai-rag)
7. [Luồng Sinh Runbook (Runbook Generation)](#7-luồng-sinh-runbook-runbook-generation)
8. [Bảng tổng hợp Quyền truy cập](#8-bảng-tổng-hợp-quyền-truy-cập)
9. [Xử lý lỗi & Các trường hợp ngoại lệ](#9-xử-lý-lỗi--các-trường-hợp-ngoại-lệ)
10. [Ví dụ Kịch bản Thực tế](#10-ví-dụ-kịch-bản-thực-tế)

---

## 1. Tổng quan hệ thống

**AI-Doc-Manager** là hệ thống quản lý tài liệu tri thức doanh nghiệp tích hợp AI, cho phép tổ chức lưu trữ, kiểm duyệt và khai thác thông tin từ tài liệu thông qua chat ngôn ngữ tự nhiên.

### Các tác nhân chính

| Tác nhân | Vai trò | Quyền hạn chính |
|----------|---------|-----------------|
| **Admin** | Quản trị viên hệ thống | Toàn quyền: quản lý user, roles, tất cả tài liệu |
| **Editor** | Người soạn thảo | Upload, sửa, tạo version mới, nộp duyệt |
| **Reviewer** | Người kiểm duyệt | Duyệt/từ chối, thêm review, đánh dấu hết hạn |
| **Viewer** | Người xem | Chỉ đọc tài liệu đã approved/expired |
| **User** | Người dùng cơ bản | Xem profile cá nhân |

### Kiến trúc tổng quan

```
┌────────────────────────────────────────────────────┐
│                  Frontend (Next.js)                │
│  Login │ Dashboard │ Documents │ Chat │ Admin       │
└───────────────────┬────────────────────────────────┘
                    │ HTTP/REST (/api/v1/*)
┌───────────────────▼────────────────────────────────┐
│              Backend (FastAPI)                     │
│  IAM │ Documents │ Reviews │ Vectorization │ QA    │
└──────┬─────────────┬──────────────┬────────────────┘
       │             │              │
  ┌────▼────┐  ┌─────▼────┐  ┌─────▼──────┐
  │PostgreSQL│  │  MinIO   │  │  ChromaDB  │
  │ (Users,  │  │ (Files)  │  │ (Vectors)  │
  │  Docs,   │  └──────────┘  └────────────┘
  │ Reviews) │         ↑ Gemini AI (Embedding + LLM)
  └──────────┘
```

---

## 2. Luồng Quản lý Người dùng & Phân quyền

### 2.1 Đăng ký tài khoản

```
Người dùng mới                  Hệ thống                     Database
      │                              │                             │
      │── POST /auth/register ──────►│                             │
      │   {username, password}       │                             │
      │                              │── Kiểm tra username trùng──►│
      │                              │◄── Không tồn tại ───────────│
      │                              │                             │
      │                              │── Hash password (bcrypt) ───│
      │                              │── Tạo User record ─────────►│
      │                              │── Gán role "user" mặc định─►│
      │                              │◄── Thành công ──────────────│
      │◄── 201 {id, username, ───────│
      │         roles: ["user"],     │
      │         permissions: [...]}  │
```

**Quy tắc nghiệp vụ:**
- Username phải là duy nhất trong hệ thống
- Password được hash bằng bcrypt (không lưu plaintext)
- Tài khoản mới tự động nhận role `user` (chỉ xem được profile)
- Admin cần gán thêm role `editor`/`reviewer`/`viewer` để cấp quyền thực sự

---

### 2.2 Đăng nhập & Xác thực JWT

```
Người dùng               API                    Database
    │                     │                         │
    │── POST /auth/login──►│                         │
    │   {username,password}│                         │
    │                     │── Tìm user theo username►│
    │                     │◄── User record ──────────│
    │                     │                         │
    │                     │── Verify bcrypt hash    │
    │                     │   (password vs hash)    │
    │                     │                         │
    │                     │── Load roles + privileges│
    │                     │   từ DB ───────────────►│
    │                     │◄── Roles & Permissions ──│
    │                     │                         │
    │                     │── Tạo JWT token         │
    │                     │   (exp: 60 phút)        │
    │◄── 200 {access_token,│                         │
    │    token_type: bearer│                         │
    │    expires_in: 3600} │                         │
```

**Cơ chế phân quyền (mỗi request):**
```
Request với JWT
      │
      ▼
Decode JWT → lấy user_id
      │
      ▼
Load user từ DB → lấy danh sách roles + privileges
      │
      ▼
Xây dựng permission_key = "METHOD:/api/v1/route/path"
Ví dụ: "POST:/api/v1/documents/upload"
      │
      ▼
Kiểm tra permission_key có trong privileges của user?
      │
  ┌───┴───┐
  │ Có   │ Không
  ▼       ▼
200 OK   403 Forbidden
```

---

### 2.3 Admin quản lý User & Role

```
Admin                    API Admin                 Database
  │                          │                         │
  │── POST /admin/users ─────►│                         │
  │   {username, password,   │                         │
  │    roles: ["editor"]}    │                         │
  │                          │── Tạo user + hash pwd──►│
  │                          │── Gán các roles ────────►│
  │◄── 201 UserResponse ─────│                         │
  │                          │                         │
  │── POST /admin/users      │                         │
  │        /{id}/roles ──────►│                         │
  │   {role_name: "reviewer"}│                         │
  │                          │── Thêm role assignment─►│
  │◄── 200 UserResponse ─────│                         │
  │                          │                         │
  │── DELETE /admin/users    │                         │
  │        /{id}/roles/{name}►│                         │
  │                          │── Xóa role assignment──►│
  │◄── 200 UserResponse ─────│                         │
```

**Roles có sẵn (seed tự động khi start):**

| Role | Mô tả | Privileges |
|------|-------|-----------|
| `admin` | Quản trị toàn hệ thống | 30 endpoints |
| `editor` | Soạn thảo tài liệu | 7 endpoints |
| `reviewer` | Kiểm duyệt tài liệu | 8 endpoints |
| `viewer` | Chỉ xem | 3 endpoints |
| `user` | Mặc định sau register | 1 endpoint (GET /auth/me) |

---

## 3. Luồng Vòng đời Tài liệu

### 3.1 Sơ đồ trạng thái tài liệu

```
                  ┌─────────────────────────────────────┐
                  │                                     │
            Upload│                             Tạo version mới
                  ▼                                     │
              ┌───────┐                                 │
              │ DRAFT │────────────────────────────────►┤
              └───────┘                                 │
                  │ Submit                              │
                  ▼                                     │
          ┌──────────────┐                              │
          │PENDING_REVIEW│                              │
          └──────────────┘                              │
           │           │                                │
      Approve│      Reject│                             │
           ▼           ▼                                │
       ┌────────┐  ┌────────┐                           │
       │APPROVED│  │REJECTED│───── Re-submit ──────────►│
       └────────┘  └────────┘      (→ PENDING_REVIEW)  │
           │                                            │
    Expire │  (hoặc khi version                        │
           │   mới được approved)                       │
           ▼                                            │
       ┌─────────┐                                      │
       │ EXPIRED │                                      │
       └─────────┘                                      │
                                                        │
       ┌──────────┐  ← Soft delete từ bất kỳ trạng thái│
       │ ARCHIVED │◄───────────────────────────────────┘
       └──────────┘
```

---

### 3.2 Luồng Upload Tài liệu

```
Editor              API Documents          MinIO          Database
  │                      │                   │                │
  │── POST /documents/upload ──────────────► │                │
  │   file: [PDF/DOCX/TXT]                  │                │
  │   document_type: policy/manual/...       │                │
  │   title: "..."  description: "..."       │                │
  │                      │                   │                │
  │                      │── Validate size   │                │
  │                      │   (max 50MB,      │                │
  │                      │   đọc 64KB/chunk) │                │
  │                      │                   │                │
  │                      │── Upload file ────►                │
  │                      │◄── object_key ────                │
  │                      │                   │                │
  │                      │── CREATE Document─────────────────►│
  │                      │   status: DRAFT   │                │
  │                      │   version: 1      │                │
  │                      │   group_id: UUID  │                │
  │◄── 201 {document_id, │                   │                │
  │         version: 1,  │                   │                │
  │         status: DRAFT}│                  │                │
```

**Định dạng file hỗ trợ:** PDF, DOCX, TXT (và các định dạng text khác)  
**Giới hạn kích thước:** 50 MB mỗi file  
**Metadata bắt buộc:** file (multipart form)  
**Metadata tùy chọn:** title, description, document_type (policy/manual/report/other)

---

### 3.3 Luồng Nộp duyệt

```
Editor            API Documents          Database
  │                    │                     │
  │── POST /documents/{id}/submit ──────────►│
  │                    │                     │
  │                    │── Kiểm tra trạng thái:
  │                    │   DRAFT hoặc REJECTED? ─────────────►│
  │                    │                     │
  │                    │── UPDATE status     │
  │                    │   → PENDING_REVIEW  │
  │                    │   submitted_by = user_id
  │                    │   submitted_at = now│
  │                    │   rejected_* = null (reset)
  │◄── 200 {status:    │                     │
  │    pending_review} │                     │
```

**Quy tắc:** Chỉ tài liệu ở trạng thái `DRAFT` hoặc `REJECTED` mới có thể nộp duyệt.

---

### 3.4 Luồng Tạo Phiên bản Mới

```
Editor            API Documents     MinIO        Database
  │                    │               │              │
  │── POST /documents/{id}/new-version►│              │
  │   file: [file mới]                │              │
  │                    │               │              │
  │                    │── Upload file►│              │
  │                    │◄── object_key─               │
  │                    │               │              │
  │                    │── Tìm max version            │
  │                    │   trong group_id────────────►│
  │                    │◄── max_version = N───────────│
  │                    │               │              │
  │                    │── CREATE Document            │
  │                    │   group_id = (same as source)│
  │                    │   version = N+1 ────────────►│
  │                    │   status = DRAFT             │
  │◄── 201 {version: N+1,              │              │
  │         status: DRAFT}             │              │
```

> 💡 **Lưu ý:** Tất cả các document cùng `document_group_id` là các phiên bản của cùng một tài liệu gốc. Khi version mới được approved, các version `APPROVED` cũ tự động chuyển sang `EXPIRED`.

---

## 4. Luồng Duyệt & Review Tài liệu

### 4.1 Luồng Duyệt (Approve/Reject)

```
Reviewer         API Approvals         API Documents        Database      Background
    │                 │                     │                   │              │
    │── GET /approvals/pending ────────────►│                   │              │
    │◄── [{doc_id, title, submitted_by,─────│                   │              │
    │      submitted_at, ...}]              │                   │              │
    │                                      │                   │              │
    │           [Xem xét tài liệu]         │                   │              │
    │                                      │                   │              │
    ├─── Trường hợp DUYỆT: ─────────────────────────────────────────────────── │
    │── POST /documents/{id}/approve ──────►│                   │              │
    │                                      │── Kiểm tra        │              │
    │                                      │   PENDING_REVIEW?─►│             │
    │                                      │── UPDATE status   │              │
    │                                      │   → APPROVED ─────►│             │
    │                                      │── Expire các      │              │
    │                                      │   version cũ ─────►│             │
    │◄── 200 {status: approved} ───────────│                   │              │
    │                                      │── Schedule task ──────────────────►
    │                                      │   vectorize()                     │
    │                                      │                                   │
    ├─── Trường hợp TỪ CHỐI: ──────────────────────────────────────────────────│
    │── POST /documents/{id}/reject ───────►│                   │              │
    │   {reason: "Cần bổ sung mục 3.2"}    │                   │              │
    │                                      │── UPDATE status   │              │
    │                                      │   → REJECTED ─────►│             │
    │                                      │   rejected_reason─►│             │
    │◄── 200 {status: rejected,            │                   │              │
    │         rejected_reason: "..."} ─────│                   │              │
```

**Quy tắc kinh doanh khi Approve:**
1. Tài liệu phải đang ở trạng thái `PENDING_REVIEW`
2. Các tài liệu `APPROVED` khác trong cùng `document_group_id` → tự động chuyển `EXPIRED`
3. Chỉ **1 version** ở trạng thái `APPROVED` tại một thời điểm
4. Vectorization tự động chạy ngầm (non-blocking)

**Quy tắc khi Reject:**
- Lý do từ chối (`reason`) là bắt buộc, không được để trống
- Editor có thể sửa và nộp lại → quay về `PENDING_REVIEW`

---

### 4.2 Luồng Đánh dấu Hết hạn

```
Reviewer/Admin         API Documents          Database
      │                      │                    │
      │── POST /documents/{id}/expire ───────────►│
      │                      │                    │
      │                      │── Kiểm tra         │
      │                      │   status = APPROVED?►│
      │                      │                    │
      │                      │── UPDATE status    │
      │                      │   → EXPIRED ───────►│
      │◄── 200 {status: expired} ────────────────  │
```

> Dùng khi tài liệu đã hết hiệu lực theo thời gian nhưng chưa có version mới thay thế.

---

### 4.3 Luồng Review & Đánh giá Chất lượng

```
Reviewer/Admin       API Reviews              Database
      │                   │                       │
      │── POST /documents/{id}/reviews ──────────►│
      │   {grade: "A",                            │
      │    comment: "Nội dung rõ ràng, đầy đủ"}  │
      │                   │                       │
      │                   │── INSERT review ───────►│
      │◄── 201 {review_id,│                       │
      │         grade: "A",                       │
      │         comment: "...",                   │
      │         created_date: ...} ───────────────│
      │                   │                       │
      │── GET /documents/{id}/reviews?page=1 ─────►│
      │◄── 200 {items: [...], total, page} ───────│
```

**Thang điểm:** A / B / C / D / F  
**Lưu ý:** Nhiều reviewer có thể review cùng một tài liệu. Không giới hạn số lượng review.

---

## 5. Luồng Vectorization AI

Vectorization là quá trình chuyển đổi nội dung tài liệu thành vector số học để phục vụ tìm kiếm ngữ nghĩa (semantic search).

### 5.1 Vectorization Tự động (sau khi Approve)

```
[Approve Document]
        │
        ▼
HTTP 200 trả về ngay cho Reviewer
        │
        │ (background task - non-blocking)
        ▼
┌─────────────────────────────────────────────────────────┐
│                 VECTORIZATION PIPELINE                  │
│                                                         │
│  1. Download file từ MinIO                              │
│         │                                               │
│         ▼                                               │
│  2. Trích xuất text                                     │
│     ┌──────────────────────────────────┐                │
│     │ PDF  → PyMuPDF                  │                │
│     │ DOCX → python-docx              │                │
│     │ TXT  → decode trực tiếp         │                │
│     └──────────────────────────────────┘                │
│         │                                               │
│         ▼                                               │
│  3. Chia nhỏ text thành chunks                          │
│     - Chunk size: 1000 ký tự                           │
│     - Overlap: 200 ký tự                               │
│     (đảm bảo ngữ cảnh không bị đứt đoạn)              │
│         │                                               │
│         ▼                                               │
│  4. Tạo embeddings (Gemini API)                        │
│     - Task type: RETRIEVAL_DOCUMENT                     │
│     - Batch size: 20 chunks/request                     │
│     - Validate: count match + dimension check           │
│         │                                               │
│         ▼                                               │
│  5. Lưu vào ChromaDB                                   │
│     - Upsert chunks + embeddings + metadata             │
│         │                                               │
│         ▼                                               │
│  6. Đánh dấu is_vectorized = true trong PostgreSQL     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Vectorization Thủ công

```
Admin/Reviewer        API Vectorization        Pipeline
      │                      │                     │
      │── POST /vectorization/{doc_id} ────────────►│
      │   ?force=false (mặc định)                  │
      │                      │                     │
      │                      │── Kiểm tra          │
      │                      │   is_vectorized?     │
      │                      │   → Nếu true và      │
      │                      │     !force: skip     │
      │                      │                     │
      │── POST /vectorization/bulk ────────────────►│
      │   {document_ids: [id1, id2, ...]}           │
      │   ?force=true                               │
      │                      │── Xử lý tuần tự     │
      │                      │   từng document      │
      │◄── 200 {results: [   │                     │
      │     {doc_id, is_vectorized,                 │
      │      chunk_count,                           │
      │      processing_time_ms},...]}              │
```

**Tham số `force=true`:** Re-vectorize dù tài liệu đã được vectorize trước đó. Hệ thống sẽ xóa chunks cũ trước khi tạo mới để tránh orphaned chunks.

---

## 6. Luồng Chat AI (RAG)

RAG (Retrieval-Augmented Generation): Hệ thống tìm kiếm ngữ nghĩa các tài liệu liên quan rồi dùng Gemini AI để trả lời dựa trên nội dung đó.

### 6.1 Luồng Chat đầy đủ

```
User              Frontend          API /qa/chat         ADK Agent         ChromaDB        Gemini
  │                  │                   │                    │                 │               │
  │── Gõ câu hỏi ──►│                   │                    │                 │               │
  │                  │── POST /qa/chat──►│                    │                 │               │
  │                  │   {message: "...",│                    │                 │               │
  │                  │    session_id?}   │                    │                 │               │
  │                  │                  │── Get/Create session (PostgreSQL)     │               │
  │                  │                  │                    │                 │               │
  │                  │                  │── ADK run_async() ►│                 │               │
  │                  │                  │                    │                 │               │
  │                  │                  │              [Phân tích intent]       │               │
  │                  │                  │                    │── search_documents(query)        │
  │                  │                  │                    │                 │               │
  │                  │                  │                    │── Embed query──────────────────►│
  │                  │                  │                    │   (QUESTION_ANSWERING task)     │
  │                  │                  │                    │◄── query_vector ───────────────│
  │                  │                  │                    │                 │               │
  │                  │                  │                    │── similarity search ───────────►│
  │                  │                  │                    │   top_k = 5     │               │
  │                  │                  │                    │◄── chunks + scores ─────────────│
  │                  │                  │                    │                                 │
  │                  │                  │                    │── Generate answer ─────────────►│
  │                  │                  │                    │   (context = retrieved chunks)  │
  │                  │                  │                    │◄── response text ───────────────│
  │                  │                  │◄── events ─────────│                                 │
  │                  │◄── 200 {session_id, response} ────────│                                 │
  │◄── Hiển thị ─────│                  │                    │                 │               │
```

### 6.2 Quy tắc của AI Agent

Agent được cấu hình với các quy tắc bắt buộc:

| Quy tắc | Mô tả |
|---------|-------|
| **Luôn search trước** | Bắt buộc gọi `search_documents()` trước khi trả lời bất kỳ câu hỏi nào về nội dung tài liệu |
| **Chỉ dùng nguồn retrieved** | Không được "bịa" thông tin — chỉ trả lời dựa trên chunks được tìm thấy |
| **Trích dẫn nguồn** | Khi trả lời phải đề cập tên tài liệu gốc |
| **Thừa nhận khi không tìm được** | Nếu không có chunks liên quan, nói thẳng thay vì phỏng đoán |
| **Câu hỏi chung** | Nếu người dùng chào hỏi/hỏi chung, được trả lời trực tiếp không cần search |

### 6.3 Session Management

```
Lần 1: User gửi message, KHÔNG có session_id
    → Hệ thống tạo session mới (UUID)
    → Lưu vào PostgreSQL qua ADK DatabaseSessionService
    → Trả về session_id trong response

Lần 2+: User gửi message, CÓ session_id
    → Hệ thống tìm session cũ trong DB
    → Nếu tìm thấy: tiếp tục conversation
    → Nếu không tìm thấy: tạo session mới
    → AI nhớ ngữ cảnh cuộc hội thoại trước
```

---

## 7. Luồng Sinh Runbook (Runbook Generation)

Hệ thống cho phép người dùng tổng hợp và biên soạn một tài liệu hướng dẫn kỹ thuật (Runbook) dưới định dạng Markdown dựa trên tập hợp các tài liệu đã được phê duyệt và vectorize.

### 7.1 Sơ đồ luồng sinh Runbook

```
Người dùng              FastAPI API            RunbookAgent         ChromaDB
    │                       │                       │                   │
    │── POST /runbooks ─────►                       │                   │
    │   /generate           │                       │                   │
    │   {document_ids[],    │                       │                   │
    │    purpose, title}    │                       │                   │
    │                       │── Validate docs ──────┼───────────────────┤
    │                       │   (exist & vectorized)│                   │
    │                       │                       │                   │
    │                       │── Tạo Runbook record ─┼───────────────────┤
    │                       │   status: "generating"│                   │
    │                       │                       │                   │
    │                       │── Kích hoạt Agent ───►│                   │
    │                       │   (Thiết lập context) │                   │
    │                       │                       │── search_knowledge_for_runbook()
    │                       │                       │   (Với document_ids filter)
    │                       │                       │   (Embedding query)
    │                       │                       │── semantic search ───►│
    │                       │                       │◄── chunks (filtered) ─│
    │                       │                       │                   │
    │                       │                       │── Synthesize &    │
    │                       │                       │   format Markdown │
    │                       │◄── Runbook content ───│                   │
    │                       │                       │                   │
    │                       │── UPDATE Runbook ─────┼───────────────────┤
    │                       │   status: "completed" │                   │
    │                       │   content: Markdown   │                   │
    │◄── 201 RunbookResponse│                       │                   │
```

### 7.2 Quy tắc nghiệp vụ

- **Ràng buộc đầu vào**: Danh sách `document_ids` phải chứa từ 1 đến 10 tài liệu.
- **Trạng thái tài liệu**: Tất cả các tài liệu được chỉ định bắt buộc phải ở trạng thái `APPROVED` (hoặc `EXPIRED`) và đã được vectorize hoàn tất (`is_vectorized=True`). Nếu có tài liệu chưa vectorize, hệ thống trả về lỗi `422 Validation Error`.
- **Phạm vi tìm kiếm của Agent**: Tool tìm kiếm tri thức của Agent (`search_knowledge_for_runbook`) sử dụng bộ lọc ChromaDB `{"document_id": {"$in": document_ids}}` để chỉ truy xuất thông tin từ các tài liệu được chọn, tránh tình trạng LLM trả lời lan man hoặc lấy nhầm tài liệu khác.
- **Cấu trúc Runbook mặc định**:
  - Title (Tiêu đề hướng dẫn)
  - Overview (Tổng quan và mục tiêu)
  - Prerequisites (Yêu cầu chuẩn bị/cài đặt)
  - Step-by-Step Procedure (Các bước thực hiện chi tiết)
  - Verification / Testing (Cách thức kiểm tra kết quả)
  - Troubleshooting (Xử lý các lỗi thường gặp)
  - References (Citations nguồn tài liệu sử dụng)

---

## 8. Bảng tổng hợp Quyền truy cập

### Quyền truy cập theo Role

| Hành động | admin | editor | reviewer | viewer | user |
|-----------|:-----:|:------:|:--------:|:------:|:----:|
| Xem profile (`/auth/me`) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Xem danh sách tài liệu | ✅ | ✅ | ✅ | ✅ | ❌ |
| Xem chi tiết tài liệu | ✅ | ✅ | ✅ | ✅ | ❌ |
| Upload tài liệu mới | ✅ | ✅ | ❌ | ❌ | ❌ |
| Sửa metadata | ✅ | ✅ | ❌ | ❌ | ❌ |
| Tạo phiên bản mới | ✅ | ✅ | ❌ | ❌ | ❌ |
| Nộp duyệt | ✅ | ✅ | ❌ | ❌ | ❌ |
| Xem hàng chờ duyệt | ✅ | ❌ | ✅ | ❌ | ❌ |
| Phê duyệt | ✅ | ❌ | ✅ | ❌ | ❌ |
| Từ chối | ✅ | ❌ | ✅ | ❌ | ❌ |
| Thêm review | ✅ | ❌ | ✅ | ❌ | ❌ |
| Đánh dấu hết hạn | ✅ | ❌ | ✅ | ❌ | ❌ |
| Soft delete | ✅ | ✅ | ❌ | ❌ | ❌ |
| Hard delete | ✅ | ❌ | ❌ | ❌ | ❌ |
| Vectorize tài liệu | ✅ | ❌ | ❌ | ❌ | ❌ |
| Chat AI | ✅ | ✅* | ✅* | ✅* | ❌ |
| Sinh runbook (`/runbooks/generate`) | ✅ | ✅ | ✅ | ✅ | ❌ |
| Xem danh sách/chi tiết/xóa runbook | ✅ | ✅ | ✅ | ✅ | ❌ |
| Quản lý users | ✅ | ❌ | ❌ | ❌ | ❌ |
| Quản lý roles | ✅ | ❌ | ❌ | ❌ | ❌ |

> *Chat AI hiện có trong seed nhưng cần admin cấp quyền `POST:/api/v1/qa/chat` cho từng role

### Tài liệu nhìn thấy theo Role (Status Visibility)

| Status | admin | editor | reviewer | viewer |
|--------|:-----:|:------:|:--------:|:------:|
| DRAFT | ✅ | ✅ | ❌ | ❌ |
| PENDING_REVIEW | ✅ | ✅ | ✅ | ❌ |
| APPROVED | ✅ | ✅ | ✅ | ✅ |
| REJECTED | ✅ | ✅ | ✅ | ❌ |
| EXPIRED | ✅ | ✅ | ✅ | ✅ |
| ARCHIVED | ✅ | ❌ | ❌ | ❌ |

---

## 9. Xử lý lỗi & Các trường hợp ngoại lệ

### 8.1 Mã lỗi HTTP

| HTTP Code | Loại lỗi | Khi nào xảy ra |
|-----------|----------|----------------|
| 400 | Bad Request | Dữ liệu đầu vào không hợp lệ |
| 401 | Unauthorized | Không có token hoặc token hết hạn |
| 403 | Forbidden | Không đủ quyền (role thiếu privilege) |
| 404 | Not Found | Tài liệu/User/Role không tồn tại |
| 409 | Conflict | Username trùng, Role đã assign, sai trạng thái |
| 422 | Validation Error | File rỗng, reason từ chối trống, file quá lớn |
| 500 | Internal Server Error | Lỗi bất ngờ nội bộ |
| 502 | External Service Error | Gemini API bị chặn, DB unreachable |
| 503 | Service Unavailable | Database không ready |

### 8.2 Các trường hợp ngoại lệ thường gặp

#### Upload thất bại
```
Nguyên nhân:
├── File > 50MB → 422 "File size exceeds maximum of 50 MB"
├── MinIO không chạy → 500 lỗi kết nối
└── File không có content → không bị chặn ở upload (chỉ lỗi khi vectorize)
```

#### Approve thất bại
```
Nguyên nhân:
├── Document không phải PENDING_REVIEW → 409 "Only pending documents can be approved"
└── Reviewer không có quyền → 403 Forbidden
```

#### Vectorization thất bại
```
Nguyên nhân (log trong background):
├── Không tải được file từ MinIO
├── Không trích xuất được text (file hỏng)
├── Gemini API key bị chặn → ExternalServiceError (502)
├── GOOGLE_API_KEY chưa set hoặc sai
└── Lỗi kết nối ChromaDB

→ Vectorization lỗi KHÔNG ảnh hưởng đến trạng thái APPROVED của tài liệu
→ Kiểm tra trạng thái: GET /vectorization/{doc_id}/status
→ Thử lại thủ công: POST /vectorization/{doc_id}?force=true
```

#### Chat không trả lời đúng
```
Nguyên nhân:
├── Tài liệu chưa được vectorize → search trả về rỗng
├── GOOGLE_API_KEY không có quyền Generative Language API
├── Câu hỏi quá chung chung, không match document nào
└── ChromaDB không có dữ liệu (chưa upload document nào)
```

### 8.3 Rollback & Nhất quán dữ liệu

| Tình huống | Cơ chế rollback |
|-----------|----------------|
| Upload file nhưng DB lỗi | File ở MinIO nhưng không có DB record → file "mồ côi" |
| Vectorize thành công nhưng DB lỗi | Xóa vectors từ ChromaDB trước khi báo lỗi |
| Xóa vectors thành công nhưng DB lỗi | Log cảnh báo "manual sync required" |
| Bulk vectorize: 1 item lỗi | Rollback session DB, tiếp tục các items khác |

---

## 10. Ví dụ Kịch bản Thực tế

### Kịch bản 1: Quy trình hoàn chỉnh tài liệu chính sách

```
1. [Admin] Tạo user "nguyen.van.a" với role "editor"
   POST /admin/users {username: "nguyen.van.a", roles: ["editor"]}

2. [Editor] Đăng nhập và upload chính sách mới
   POST /auth/login → JWT token
   POST /documents/upload
     file: "chinh_sach_bao_mat_2026.pdf"
     document_type: "policy"
     title: "Chính sách Bảo mật Thông tin 2026"

3. [Editor] Đọc lại, chỉnh sửa mô tả
   PUT /documents/{id} {description: "Phiên bản cập nhật Q2/2026"}

4. [Editor] Nộp duyệt
   POST /documents/{id}/submit

5. [Reviewer] Xem hàng chờ
   GET /approvals/pending → thấy tài liệu mới

6. [Reviewer] Xem chi tiết và download
   GET /documents/{id} → nhận presigned URL để download

7. [Reviewer] Thêm nhận xét
   POST /documents/{id}/reviews {grade: "B", comment: "Cần bổ sung mục 4.3"}

8. [Reviewer] Từ chối, yêu cầu chỉnh sửa
   POST /documents/{id}/reject {reason: "Thiếu quy định xử lý vi phạm"}

9. [Editor] Chỉnh sửa và nộp lại
   POST /documents/{id}/submit (từ REJECTED → PENDING_REVIEW)

10. [Reviewer] Phê duyệt
    POST /documents/{id}/approve
    → Hệ thống tự động vectorize ngầm

11. [Mọi user có quyền] Tra cứu qua Chat AI
    POST /qa/chat {message: "Quy định xử lý vi phạm bảo mật là gì?"}
    → AI tìm kiếm ChromaDB và trả lời với citation
```

### Kịch bản 2: Cập nhật phiên bản khi chính sách thay đổi

```
1. [Editor] Tạo version mới của tài liệu đã APPROVED
   POST /documents/{old_id}/new-version
     file: "chinh_sach_bao_mat_2026_v2.pdf"
   → Tạo document mới cùng group_id, version = 2, status = DRAFT

2. [Editor] Nộp duyệt version mới
   POST /documents/{new_id}/submit

3. [Reviewer] Duyệt version mới
   POST /documents/{new_id}/approve
   → Version 1 (APPROVED) → tự động EXPIRED
   → Version 2 → APPROVED
   → Vectorize version 2 ngầm

4. Viewer chỉ thấy version 2 (APPROVED) trong danh sách
   Version 1 hiển thị là EXPIRED (Viewer vẫn thấy)
```
