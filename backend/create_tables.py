#!/usr/bin/env python3
"""
데이터베이스 테이블 생성 스크립트
"""

from app.core.database import engine, Base
from app.models.session import Session  # 모델 import 필요
from app.models.base import BaseModel

def create_tables():
    """모든 테이블 생성"""
    print("Creating database tables...")
    try:
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("SUCCESS: Database tables created successfully!")

        # 생성된 테이블 확인
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"INFO: Created tables: {tables}")

    except Exception as e:
        print(f"ERROR: Error creating tables: {e}")
        return False

    return True

if __name__ == "__main__":
    create_tables()