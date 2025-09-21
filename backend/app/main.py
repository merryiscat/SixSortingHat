"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from app.core.config_dev import dev_settings as settings
from app.api.v1 import api_router

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="SixSortingHat API",
    description="육모자 사고법 기반 AI 토론 시스템",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "SixSortingHat API",
            "version": "0.1.0",
        },
    )

# API 라우터 포함
app.include_router(api_router, prefix="/api/v1")

# 정적 파일 서빙 (프론트엔드)
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
print(f"Frontend path: {frontend_path}")
if os.path.exists(frontend_path):
    print(f"Frontend directory exists, mounting at /app")
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"Frontend directory not found at {frontend_path}")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
