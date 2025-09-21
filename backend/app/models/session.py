"""
세션 관련 모델
"""

from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.models.base import BaseModel


class SessionStatus(enum.Enum):
    """세션 상태"""

    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class Session(BaseModel):
    """토론 세션 모델"""

    __tablename__ = "sessions"

    session_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    coins_remaining = Column(Integer, default=5)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)
    expires_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Session(id={self.id}, session_id={self.session_id}, coins={self.coins_remaining})>"