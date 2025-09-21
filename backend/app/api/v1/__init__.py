"""
API v1 라우터
"""

from fastapi import APIRouter

from .endpoints import health, sessions, discussions

api_router = APIRouter()

# 각 엔드포인트 라우터 포함
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(
    discussions.router, prefix="/discussions", tags=["discussions"]
)
