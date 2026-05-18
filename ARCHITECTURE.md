# 🏗️ Architecture: Frontend-Backend Communication

## Tổng Quan Hệ Thống

```
┌──────────────────────────────────────────────────────────────────────┐
│                    CLIENT BROWSER (Port 3000)                        │
│                    ┌─────────────────────────┐                       │
│                    │   Next.js Frontend      │                       │
│                    │  - React Components    │                       │
│                    │  - TypeScript/UI Logic │                       │
│                    └────────────┬────────────┘                       │
│                                 │                                     │
│                        HTTP + Firebase Token                          │
│                                 │                                     │
│                    Network Layer (Axios)                              │
│                    - Request Interceptor ──────→ Add Token           │
│                    - Response Interceptor ←───── Handle 401          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼───────────┐
                    │   API Gateway/Proxy    │
                    │  (if applicable)       │
                    └────────────┬───────────┘
                                 │
                    HTTP/REST (Port 8000)
                                 │
┌────────────────────────────────▼───────────────────────────────────┐
│              BACKEND SERVER (FastAPI - Port 8000)                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Middleware Layer                                             │  │
│  │  ├─ Request logging + request_id                             │  │
│  │  ├─ CORS handling                                            │  │
│  │  └─ Exception handlers                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Security Layer                                              │  │
│  │  ├─ Firebase Token Verification                             │  │
│  │  ├─ get_current_user() dependency                           │  │
│  │  └─ Role-Based Access Control (RBAC)                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  API Routes                                                  │  │
│  │  ├─ /auth          (Authentication)                         │  │
│  │  ├─ /documents     (Document Management)                    │  │
│  │  ├─ /reviews       (Reviews)                                │  │
│  │  ├─ /approvals     (Approvals)                              │  │
│  │  └─ /qa            (Chat/QA)                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Business Logic Layer (Domain Models)                        │  │
│  │  ├─ User, Document, Review, Approval, etc.                  │  │
│  │  └─ Application Services (use cases)                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Data Layer                                                  │  │
│  │  ├─ PostgreSQL Database                                     │  │
│  │  ├─ Alembic Migrations                                      │  │
│  │  └─ SQLAlchemy ORM                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────┬───────────┴────────────┬────────────┐
        │            │                        │            │
   PostgreSQL     MinIO/GCS              Chroma DB      Redis
   (Database)   (File Storage)        (Vector Store)   (Cache)
```

---

## 📁 Frontend Directory Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── api/                # Next.js API routes (mock)
│   │   ├── (auth)/             # Auth routes group
│   │   │   ├── login/
│   │   │   └── signup/
│   │   └── (main)/             # Main app routes
│   │       ├── documents/
│   │       ├── reviews/
│   │       ├── approvals/
│   │       └── chat/
│   │
│   ├── components/             # Reusable Components
│   │   ├── documents/          # Document-related components
│   │   ├── reviews/
│   │   ├── approvals/
│   │   ├── chat/
│   │   └── layout/
│   │
│   ├── hooks/                  # Custom React Hooks
│   │   ├── useAuth.ts          # Auth state management
│   │   ├── useDocuments.ts     # Fetch & cache documents
│   │   ├── usePermission.ts    # Permission check
│   │   └── useChat.ts          # Chat websocket
│   │
│   ├── lib/                    # Utilities & Configuration
│   │   ├── api/                # ← API Client ← Backend
│   │   │   ├── client.ts       # Axios instance + interceptors
│   │   │   ├── auth.ts         # /auth endpoints
│   │   │   ├── documents.ts    # /documents endpoints
│   │   │   ├── reviews.ts      # /reviews endpoints
│   │   │   ├── approvals.ts    # /approvals endpoints
│   │   │   └── chat.ts         # /qa endpoints
│   │   │
│   │   ├── auth/               # Firebase Configuration
│   │   │   └── firebase.ts     # Firebase SDK setup
│   │   │
│   │   └── gcs/                # Google Cloud Storage
│   │       └── client.ts       # GCS upload helper
│   │
│   ├── stores/                 # State Management (Zustand)
│   │   ├── authStore.ts        # User + token state
│   │   ├── chatStore.ts        # Chat messages
│   │   └── documentStore.ts    # Documents cache
│   │
│   └── types/                  # TypeScript Types
│       ├── user.ts
│       ├── document.ts
│       ├── chat.ts
│       └── ...
│
└── .env.local                  # ← Config: API URL, Firebase, GCS
```

### 🔑 Key Frontend Files untuk Connect BE

| File                                                                            | Fungsi                            |
| ------------------------------------------------------------------------------- | --------------------------------- |
| [src/lib/api/client.ts](../AI-Doc-Manager/frontend/src/lib/api/client.ts)       | 🌐 Axios config + Token injection |
| [src/lib/api/auth.ts](../AI-Doc-Manager/frontend/src/lib/api/auth.ts)           | 🔐 /auth endpoints                |
| [src/lib/api/documents.ts](../AI-Doc-Manager/frontend/src/lib/api/documents.ts) | 📄 /documents endpoints           |
| [.env.local](#)                                                                 | ⚙️ NEXT_PUBLIC_API_URL config     |

---

## 📁 Backend Directory Structure

```
backend/
├── app/
│   ├── main.py                 # ← FastAPI app instance
│   │                            # ├─ Router registration
│   │                            # ├─ Middleware setup
│   │                            # └─ Exception handlers
│   │
│   ├── core/
│   │   ├── config.py           # Settings (env variables)
│   │   ├── db.py               # Database connection
│   │   ├── security.py         # Firebase token verification
│   │   ├── dependencies.py     # Dependency injection
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logging.py          # Logging config
│   │
│   ├── modules/                # Feature modules (clean architecture)
│   │   ├── iam/                # Identity & Access Management
│   │   │   ├── api/
│   │   │   │   └── router.py   # GET /auth/me, POST /auth/logout
│   │   │   ├── domain/         # User entity
│   │   │   └── infrastructure/ # Database access
│   │   │
│   │   ├── documents/          # Document Management
│   │   │   ├── api/
│   │   │   │   └── router.py   # GET/POST/PUT /documents
│   │   │   ├── domain/         # Document entity
│   │   │   ├── application/    # Use cases
│   │   │   └── infrastructure/ # DB + GCS access
│   │   │
│   │   ├── reviews/            # Review Module
│   │   │   ├── api/
│   │   │   │   └── router.py   # /reviews endpoints
│   │   │   └── ...
│   │   │
│   │   ├── approvals/          # Approval Module
│   │   │   ├── api/
│   │   │   │   └── router.py   # /approvals endpoints
│   │   │   └── ...
│   │   │
│   │   └── qa/                 # QA/Chat Module
│   │       ├── api/
│   │       │   └── router.py   # POST /qa/chat
│   │       └── ...
│   │
│   ├── shared/                 # Shared Code
│   │   ├── schemas.py          # Pydantic models
│   │   ├── enums.py            # Enums (DocumentType, etc)
│   │   ├── interfaces.py       # Abstract interfaces
│   │   ├── utils.py            # Helpers
│   │   └── adapters/           # External integrations
│   │       ├── chroma_vector_adapter.py
│   │       ├── gcs_storage_adapter.py
│   │       ├── vertex_ai_llm_adapter.py
│   │       └── ...
│   │
│   ├── alembic/                # Database Migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 20260420_0001_initial_schema.py
│   │       ├── 20260423_0002_add_reviews_and_approvals.py
│   │       └── ...
│   │
│   └── tests/                  # Automated Tests
│       ├── unit/
│       └── integration/
│
├── pyproject.toml              # Python dependencies
├── alembic.ini                 # Alembic config
└── Dockerfile                  # Container image
```

### 🔑 Key Backend Files để Hiểu API

| File                                                                                                 | Fungsi                                |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------- |
| [app/main.py](../AI-Doc-Manager/backend/app/main.py)                                                 | 🚀 FastAPI setup, router registration |
| [app/core/security.py](../AI-Doc-Manager/backend/app/core/security.py)                               | 🔐 Token verification                 |
| [app/modules/iam/api/router.py](../AI-Doc-Manager/backend/app/modules/iam/api/router.py)             | /auth endpoints                       |
| [app/modules/documents/api/router.py](../AI-Doc-Manager/backend/app/modules/documents/api/router.py) | /documents endpoints                  |
| [app/shared/schemas.py](../AI-Doc-Manager/backend/app/shared/schemas.py)                             | Request/Response models               |

---

## 🔄 Request-Response Flow Example

### **Flow 1: Fetch Documents**

```
FE: GET /documents?limit=20
    ├─ URL: http://localhost:8000/documents?limit=20
    ├─ Headers: Authorization: Bearer <firebase-token>
    └─ Timeout: 60s

        ↓ Network

BE: router.py - GET /documents
    ├─ Middleware: Log request, set request_id
    ├─ Security: Verify Firebase token
    ├─ Dependency: get_current_user() → Query PostgreSQL
    ├─ Handler: documents.list(current_user, skip=0, limit=20)
    │   ├─ Query: SELECT * FROM documents WHERE created_by=user_id
    │   └─ Pagination: Skip 0, Limit 20
    └─ Response: 200 OK + JSON

        ↓ Network

FE: axios response
    ├─ Status: 200 ✅
    ├─ Body: { items: [...], total: 150 }
    └─ JavaScript event: .then(response => setDocs(response.data.items))
```

### **Flow 2: Create Document (3 Steps)**

```
Step 1: Frontend → Backend
────────────────────────
FE: GET /documents/signed-upload-url?filename=doc.pdf&size=10000
BE: Response: { upload_url: "...", gcs_path: "gs://..." }

Step 2: Frontend → Google Cloud Storage (direct)
──────────────────────────────────────────────────
FE: PUT upload_url (with file binary)
GCS: Store file

Step 3: Frontend → Backend (Confirm)
────────────────────────────────────
FE: POST /documents/confirm-upload
    { gcs_path, filename, size, document_type }
BE: ├─ Insert into PostgreSQL
    ├─ Vector embed (cho RAG)
    └─ Response: 201 Created + document_id
```

---

## 🌐 Network Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Development Environment                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────┐          ┌──────────┐        ┌─────────────┐ │
│  │ Frontend  │          │ Backend  │        │ PostgreSQL  │ │
│  │ :3000     │◄────────►│ :8000    │◄──────►│ :5432       │ │
│  └───────────┘ HTTP/REST└──────────┘ TCP    └─────────────┘ │
│                                                               │
│                         Same Docker Network: app-network     │
│                         (Hostname: backend, postgres, etc)   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Docker Internal DNS:**

- Backend service name: `backend` → resolves to backend container IP
- Frontend config: `NEXT_PUBLIC_API_URL=http://backend:8000`
- ✅ Works because both in same network

---

## 📝 Communication Checklist

- [ ] **Cấu hình URL**: `NEXT_PUBLIC_API_URL` trỏ đúng backend
- [ ] **Token**: Firebase token được inject vào header
- [ ] **CORS**: Backend allow frontend origin
- [ ] **Database**: Backend connect được PostgreSQL
- [ ] **Health**: `curl http://localhost:8000/health` → 200
- [ ] **Logs**: Kiểm tra backend logs khi FE gọi

---

## 🔍 Debugging Tips

### 1. Check Frontend Config

```javascript
// DevTools Console
console.log(process.env.NEXT_PUBLIC_API_URL);
console.log(process.env.NEXT_PUBLIC_USE_MOCK);
```

### 2. Check Network Request

```
DevTools → Network → Click request
→ Check URL, Headers (Authorization), Status
```

### 3. Check Backend Logs

```bash
docker logs ai-doc-backend | tail -100
```

### 4. Test Backend Directly

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/health
```

### 5. Swagger UI

```
http://localhost:8000/docs → Test API endpoints interactively
```

---

## 📚 Related Documentation

- [FRONTEND_BACKEND_GUIDE.md](./FRONTEND_BACKEND_GUIDE.md) - Hướng dẫn chi tiết
- [QUICK_SETUP.md](./QUICK_SETUP.md) - Cấu hình nhanh
- [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Tài liệu endpoint
