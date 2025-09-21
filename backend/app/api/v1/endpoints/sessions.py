"""
세션 관리 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.session_service import SessionService

router = APIRouter()


@router.post("/create")
async def create_session(db: Session = Depends(get_db)):
    """새 토론 세션 생성"""
    session_service = SessionService(db)

    try:
        new_session = await session_service.create_session()

        return JSONResponse(
            status_code=201,
            content={
                "session_id": new_session.session_id,
                "coins_remaining": new_session.coins_remaining,
                "expires_at": new_session.expires_at.isoformat(),
                "status": new_session.status.value,
                "message": "새 세션이 생성되었습니다.",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 생성 실패: {str(e)}")


@router.get("/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """세션 정보 조회"""
    session_service = SessionService(db)

    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    return JSONResponse(
        status_code=200,
        content={
            "session_id": session.session_id,
            "coins_remaining": session.coins_remaining,
            "status": session.status.value,
            "expires_at": session.expires_at.isoformat(),
            "message": "세션 정보를 조회했습니다.",
        },
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """세션 종료"""
    session_service = SessionService(db)

    success = await session_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    return JSONResponse(
        status_code=200,
        content={"session_id": session_id, "message": "세션이 종료되었습니다."},
    )


@router.post("/{session_id}/use-coin")
async def use_coin(session_id: str, db: Session = Depends(get_db)):
    """코인 사용 (1개 차감)"""
    session_service = SessionService(db)

    success = await session_service.use_coin(session_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="코인을 사용할 수 없습니다. (세션이 없거나 코인이 부족함)",
        )

    # 업데이트된 세션 정보 반환
    session = await session_service.get_session(session_id)
    return JSONResponse(
        status_code=200,
        content={
            "session_id": session_id,
            "coins_remaining": session.coins_remaining if session else 0,
            "message": "코인이 사용되었습니다.",
        },
    )