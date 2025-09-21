"""
헬스 체크 엔드포인트
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def health_check():
    """시스템 헬스 체크"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "SixSortingHat API",
            "version": "0.1.0",
            "components": {
                "api": "up",
                "database": "checking",
                "redis": "checking",
                "ai_agents": "checking",
            },
        },
    )
