"""
개발용 설정 (SQLite 사용)
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class DevelopmentSettings(BaseSettings):
    """개발용 애플리케이션 설정 (SQLite)"""

    # 애플리케이션 기본 설정
    PROJECT_NAME: str = "SixSortingHat"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    # SQLite 설정 (개발용)
    DATABASE_URL: str = "sqlite:///./sixsortinghat_dev.db"

    # Redis 설정 (개발용 - 메모리 캐시로 대체)
    REDIS_URL: str = "memory://"  # 임시로 메모리 캐시 사용

    # OpenAI API 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "test-key")  # 테스트용 기본값
    OPENAI_MODEL: str = "gpt-4o-mini"

    # 세션 관리 설정
    SESSION_COINS: int = 5
    SESSION_EXPIRE_HOURS: int = 24

    # 로깅 설정
    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 개발용 설정 인스턴스 생성
dev_settings = DevelopmentSettings()