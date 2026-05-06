from fastapi import APIRouter
from app.api.v1.endpoints import chat, auth

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(chat.router)

# TODO: thêm các routers khác khi implement module tương ứng
# from app.api.v1.endpoints import documents, approvals, reports
# api_router.include_router(documents.router)
# api_router.include_router(approvals.router)
# api_router.include_router(reports.router)
