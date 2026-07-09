# 🚀 HƯỚNG DẪN CHẠY ĐẦY ĐỦ - AI-DOC-MANAGER

---

## **📋 CHUẨN BỊ**

**Yêu cầu:**
- Python 3.11+ (KHÔNG dùng 3.14)
- Node.js 18+
- npm

**Kiểm tra:**
```powershell
python --version    # Phải >= 3.11
node --version      # Phải >= 18
npm --version
```

---

## **🔧 PHẦN 1: CHẠY BACKEND (Port 8000)**

### **Bước 1: Mở Terminal (PowerShell)**
```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\backend
```

### **Bước 2: Tạo Virtual Environment**
```powershell
# Nếu chưa có venv
python -m venv .venv

# Activate venv (PowerShell Windows)
.venv\Scripts\Activate.ps1

# Nếu lỗi, chạy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Rồi chạy lại: .venv\Scripts\Activate.ps1
```

**✅ Khi thành công, terminal sẽ show `(.venv)` ở đầu**

### **Bước 3: Cài Dependencies**
```powershell
pip install --upgrade pip

# Cài toàn bộ dependencies từ pyproject.toml
pip install -e .

# Hoặc cài từ requirements
pip install fastapi uvicorn sqlalchemy psycopg[binary] pydantic python-dotenv
```

**Chờ cài xong (~2-3 phút)**

### **Bước 4: Setup Database (SQLite Local)**
```powershell
python setup_db.py
```

**✅ Sẽ tạo file `dms_backend.db` - xác nhận bằng `ls` hoặc `dir`**

### **Bước 5: Chạy Backend Server**
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Khi thấy dòng này = Backend chạy được:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**📚 Kiểm tra API Docs:** Mở browser → http://localhost:8000/docs

---

## **🎨 PHẦN 2: CHẠY FRONTEND (Port 3000)**

### **Bước 1: Mở Terminal MỚI (PowerShell mới, KHÔNG dùng terminal backend)**
```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\frontend
```

### **Bước 2: Cài Dependencies**
```powershell
npm install
```

**Chờ cài xong (~1-2 phút)**

### **Bước 3: Tạo/Kiểm tra `.env.local`**
```powershell
# Xem có file không
ls .env.local

# Nếu chưa có, tạo file
# Dùng: New-Item, hoặc mở VS Code > New File > Đặt tên `.env.local`
```

**File `.env.local` nội dung:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_USE_MOCK=true
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDummyKey
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=dummy-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=dummy-project
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=dummy-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123def456
```

### **Bước 4: Chạy Frontend Dev Server**
```powershell
npm run dev
```

**✅ Khi thấy dòng này = Frontend chạy được:**
```
  ▲ Next.js 16.2.4
  - Local:        http://localhost:3000
```

---

## **✅ KIỂM TRA TOÀN BỘ HỆ THỐNG**

### **1. Backend API (Terminal 1)**
- Truy cập: http://localhost:8000/docs
- Test endpoint:
  ```
  GET /api/v1/documents - Lấy danh sách tài liệu
  POST /api/v1/documents - Upload tài liệu mới
  POST /api/v1/reviews - Chấm điểm tài liệu
  POST /api/v1/documents/{id}/approve - Phê duyệt
  ```

### **2. Frontend Web (Terminal 2)**
- Truy cập: http://localhost:3000
- Xem các trang:
  - Dashboard
  - Documents (Quản lý tài liệu)
  - Reviews (Chấm điểm - Function 4)
  - Approvals (Phê duyệt - Function 5)
  - Chat (QA - Vừa merge)

---

## **⚠️ LỖI THƯỜNG GẶP & GIẢI PHÁP**

### **Lỗi 1: `ModuleNotFoundError: No module named 'fastapi'`**
```powershell
# Kiểm tra venv đã activate chưa (phải có `(.venv)`)
# Nếu chưa: .venv\Scripts\Activate.ps1

# Cài lại dependencies
pip install -e .
```

### **Lỗi 2: `Port 8000 already in use`**
```powershell
# Chạy port khác
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### **Lỗi 3: `Port 3000 already in use`**
```powershell
npm run dev -- -p 3001
```

### **Lỗi 4: `Database is locked` (SQLite)**
```powershell
# Xóa DB cũ và tạo mới
del backend\dms_backend.db
python setup_db.py
```

### **Lỗi 5: `ExecutionPolicy` (PowerShell)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Rồi chạy lại: .venv\Scripts\Activate.ps1
```

### **Lỗi 6: Frontend lỗi `Cannot find module`**
```powershell
# Xóa node_modules và cài lại
rm -r node_modules package-lock.json
npm install
npm run dev
```

---

## **🎯 CHẠY NHANH (Recommended)**

**Terminal 1 - Backend:**
```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\backend
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend (mở terminal mới):**
```powershell
cd C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\frontend
npm run dev
```

**Thế là xong!** 🎉

---

## **📝 LƯU Ý QUAN TRỌNG**

| Thành phần | Port | URL | Status |
|-----------|------|-----|--------|
| **Backend API** | 8000 | http://localhost:8000 | ✅ |
| **API Docs** | 8000 | http://localhost:8000/docs | ✅ |
| **Frontend Web** | 3000 | http://localhost:3000 | ✅ |
| **Database** | SQLite | `dms_backend.db` | ✅ |

**Tất cả Function 1-5 + QA đã sẵn sàng!** ✨

---

## **❓ CÓ THẮC MẮC?**

Nếu gặp lỗi:
1. Check Python version: `python --version`
2. Check venv active: Có `(.venv)` không?
3. Share error message cho tôi

**Good luck! 🚀**
