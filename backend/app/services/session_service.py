"""
세션 관리 서비스
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.session import Session as SessionModel, SessionStatus
from app.core.config_dev import dev_settings as settings
from app.core.database import cache_client


class SessionService:
    """세션 관리 서비스"""

    def __init__(self, db: Session):
        self.db = db

    async def create_session(self) -> SessionModel:
        """새 세션 생성"""
        session_id = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)

        # 데이터베이스에 세션 저장
        db_session = SessionModel(
            session_id=session_id,
            coins_remaining=settings.SESSION_COINS,
            status=SessionStatus.ACTIVE,
            expires_at=expires_at,
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)

        # 캐시에도 저장 (빠른 접근을 위해)
        session_data = {
            "session_id": session_id,
            "coins_remaining": settings.SESSION_COINS,
            "status": SessionStatus.ACTIVE.value,
            "expires_at": expires_at.isoformat(),
        }
        await cache_client.set(
            f"session:{session_id}",
            str(session_data),
            ex=settings.SESSION_EXPIRE_HOURS * 3600,
        )

        return db_session

    async def get_session(self, session_id: str) -> Optional[SessionModel]:
        """세션 조회"""
        # 먼저 캐시에서 조회
        cached_session = await cache_client.get(f"session:{session_id}")
        if cached_session:
            # 캐시에 있으면 데이터베이스에서 최신 정보 조회
            pass

        # 데이터베이스에서 조회
        db_session = (
            self.db.query(SessionModel)
            .filter(SessionModel.session_id == session_id)
            .first()
        )

        if db_session and db_session.expires_at < datetime.utcnow():
            # 만료된 세션인 경우 상태 업데이트
            db_session.status = SessionStatus.EXPIRED
            self.db.commit()
            await cache_client.delete(f"session:{session_id}")
            return None

        return db_session

    async def use_coin(self, session_id: str) -> bool:
        """코인 사용 (1개 차감)"""
        session = await self.get_session(session_id)
        if not session or session.coins_remaining <= 0:
            return False

        # 코인 차감
        session.coins_remaining -= 1
        self.db.commit()

        # 캐시 업데이트
        if session.coins_remaining > 0:
            session_data = {
                "session_id": session_id,
                "coins_remaining": session.coins_remaining,
                "status": session.status.value,
                "expires_at": session.expires_at.isoformat(),
            }
            await cache_client.set(
                f"session:{session_id}",
                str(session_data),
                ex=settings.SESSION_EXPIRE_HOURS * 3600,
            )
        else:
            # 코인이 모두 소진되면 캐시에서 제거
            await cache_client.delete(f"session:{session_id}")

        return True

    async def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        session = await self.get_session(session_id)
        if not session:
            return False

        # 세션 상태를 TERMINATED로 변경
        session.status = SessionStatus.TERMINATED
        self.db.commit()

        # 캐시에서도 제거
        await cache_client.delete(f"session:{session_id}")

        return True