"""
토론 관련 엔드포인트 - 6모자 시스템 연동
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import asyncio
import json

from app.core.database import get_db
from app.services.discussion_service import DiscussionService

router = APIRouter()


class DiscussionRequest(BaseModel):
    """토론 요청 모델"""

    question: str
    session_id: str


class DiscussionResponse(BaseModel):
    """토론 응답 모델"""

    discussion_id: str
    status: str
    message: str


class StreamRequest(BaseModel):
    """스트림 요청 모델"""
    question: str
    session_id: str


@router.post("/start", response_model=DiscussionResponse)
async def start_discussion(
    request: DiscussionRequest, db: Session = Depends(get_db)
):
    """새 6모자 토론 시작"""
    try:
        service = DiscussionService(db)
        result = await service.start_discussion(request.question, request.session_id)

        return DiscussionResponse(
            discussion_id=result["discussion_id"],
            status="started",
            message="6모자 토론이 시작되었습니다.",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"토론 시작 실패: {str(e)}")


@router.post("/stream-test")
async def test_stream_request(request: StreamRequest):
    """스트림 요청 테스트"""
    return {
        "received": {
            "question": request.question,
            "session_id": request.session_id
        }
    }

@router.get("/test-stream")
async def test_stream_endpoint():
    """스트림 엔드포인트 테스트"""
    return {"status": "working", "endpoint": "/test-stream"}

@router.get("/stream")
async def stream_discussion(
    question: str,
    session_id: str,
    db: Session = Depends(get_db)
):
    """6모자 분석 진행 상황 스트리밍 (SSE)"""

    try:
        if not question or not session_id:
            raise HTTPException(status_code=400, detail="question과 session_id가 필요합니다.")

        service = DiscussionService(db)

        async def generate():
            """SSE 이벤트 생성기"""
            async for event in service.stream_discussion(question, session_id):
                yield event
                # 각 이벤트 사이에 약간의 지연 (실시간 느낌)
                await asyncio.sleep(0.1)

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스트리밍 실패: {str(e)}")


@router.get("/result/{discussion_id}")
async def get_discussion(discussion_id: str, db: Session = Depends(get_db)):
    """완료된 토론 조회"""
    # TODO: 데이터베이스에서 토론 기록 조회 구현

    return JSONResponse(
        status_code=200,
        content={
            "discussion_id": discussion_id,
            "status": "completed",
            "message": "토론 기록 조회 기능은 추후 구현 예정입니다.",
        },
    )


@router.post("/test-simple")
async def test_simple_discussion():
    """간단한 6모자 토론 테스트 (개발용)"""
    try:
        from app.agents.six_hat_graph import run_six_hat_discussion

        # 테스트 질문으로 6모자 토론 실행
        result = await run_six_hat_discussion(
            "인공지능의 미래에 대해 어떻게 생각하시나요?", "test_session"
        )

        return JSONResponse(
            status_code=200,
            content={
                "test_result": "success",
                "discussion_type": result.get("discussion_type", ""),
                "final_response": result.get("final_response", "")[:200] + "...",
                "total_responses": len(result.get("all_responses", [])),
                "quality_info": result.get("quality_info"),
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"테스트 실행 실패: {str(e)}")


@router.get("/health/check")
async def health_check():
    """6모자 시스템 헬스 체크"""
    try:
        # 기본 컴포넌트들 확인
        from app.agents.hat_agents import IntentClassifier, WhiteHatAgent

        classifier = IntentClassifier()
        agent = WhiteHatAgent()

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "components": {
                    "intent_classifier": "ok",
                    "hat_agents": "ok",
                    "langgraph": "ok",
                    "streaming": "ok",
                },
                "message": "6모자 시스템이 정상 작동 중입니다.",
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "message": "6모자 시스템에 문제가 있습니다.",
            },
        )