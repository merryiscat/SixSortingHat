"""
데이터베이스 연결 및 세션 관리
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis

from app.core.config_dev import dev_settings as settings

# SQLAlchemy 설정
if "sqlite" in settings.DATABASE_URL:
    # SQLite 설정
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,  # 개발용으로 SQL 로그 활성화
    )
else:
    # PostgreSQL 설정
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()


# 데이터베이스 세션 의존성
def get_db():
    """데이터베이스 세션 생성 및 관리"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 임시 메모리 캐시 (Redis 대신 개발용)
_memory_cache = {}


async def get_redis():
    """Redis 연결 생성 (개발용은 메모리 캐시)"""
    if "memory" in settings.REDIS_URL:
        # 메모리 캐시 사용 (개발용)
        yield _memory_cache
    else:
        # 실제 Redis 사용 (프로덕션용)
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        try:
            yield redis_client
        finally:
            await redis_client.close()


# 캐시 클라이언트 (직접 사용)
class MemoryCache:
    """간단한 메모리 캐시 클래스"""

    def __init__(self):
        self._cache = {}

    async def set(self, key: str, value: str, ex: int = None):
        """값 설정"""
        self._cache[key] = value

    async def get(self, key: str):
        """값 조회"""
        return self._cache.get(key)

    async def delete(self, key: str):
        """값 삭제"""
        self._cache.pop(key, None)

    async def close(self):
        """연결 종료 (메모리 캐시는 아무것도 하지 않음)"""
        pass


if "memory" in settings.REDIS_URL:
    cache_client = MemoryCache()
else:
    cache_client = redis.from_url(
        settings.REDIS_URL, encoding="utf-8", decode_responses=True, max_connections=20
    )