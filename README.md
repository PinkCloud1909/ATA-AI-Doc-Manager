# AI-Doc-Manager

Repo nay co mot thu muc con `AI-Doc-Manager/`. Day moi la thu muc chua source that cua du an.

Trang thai hien tai:

- Backend FastAPI chay duoc bang Docker Compose trong `AI-Doc-Manager/backend/`.
- PostgreSQL va MinIO duoc chay kem backend.
- Frontend hien chua chay duoc vi cac file trong `AI-Doc-Manager/frontend/` dang rong, bao gom `package.json` va `Dockerfile`.

## Cach chay dung hien tai

1. Mo Docker Desktop va cho den khi Docker engine san sang.

Kiem tra:

```powershell
docker ps
```

Neu lenh nay khong bao loi Docker engine thi tiep tuc.

2. Chuyen vao thu muc backend:

```powershell
cd "G:\AT&A\Doc_M\ATA-AI-Doc-Manager\AI-Doc-Manager\backend"
```

3. Tao file moi truong neu chua co:

```powershell
Copy-Item .env.example .env
```

Neu file `.env` da ton tai, co the bo qua buoc nay.

4. Build va chay backend stack:

```powershell
docker compose up -d --build
```

Backend se tu dong chay migration va seed khi container `api` khoi dong.

## Dia chi sau khi chay

- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- PostgreSQL: localhost:5432
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001

Tai khoan mac dinh:

```text
username: admin
password: admin123
```

## Lenh quan ly

Xem container:

```powershell
docker compose ps
```

Xem log backend:

```powershell
docker compose logs -f api
```

Chay migration thu cong:

```powershell
docker compose exec api alembic upgrade head
```

Chay seed thu cong:

```powershell
docker compose exec api python scripts/seed.py
```

Dung cac container:

```powershell
docker compose down
```

Dung va xoa volume database/MinIO:

```powershell
docker compose down -v
```

## Luu y quan trong

Khong chay lenh nay o thoi diem hien tai:

```powershell
cd "G:\AT&A\Doc_M\ATA-AI-Doc-Manager\AI-Doc-Manager"
docker compose up --build
```

Ly do: root compose co service `frontend`, nhung `frontend/Dockerfile` va `frontend/package.json` dang rong, nen frontend se khong build duoc.

Neu chi can backend, luon chay trong:

```text
G:\AT&A\Doc_M\ATA-AI-Doc-Manager\AI-Doc-Manager\backend
```

## Development backend khong dung Docker

Chi dung cach nay neu ban da co PostgreSQL va MinIO dang chay rieng.

```powershell
cd "G:\AT&A\Doc_M\ATA-AI-Doc-Manager\AI-Doc-Manager\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

Backend se chay tai:

```text
http://localhost:8000
```
