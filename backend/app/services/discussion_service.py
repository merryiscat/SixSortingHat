"""
토론 서비스 - 6모자 시스템과 SSE 스트리밍 연동
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.agents.six_hat_graph import create_six_hat_graph, create_initial_state
from app.services.session_service import SessionService


class DiscussionService:
    """토론 서비스 클래스"""

    def __init__(self, db: Session):
        self.db = db
        self.session_service = SessionService(db)
        self.graph = create_six_hat_graph()

    async def start_discussion(self, question: str, session_id: str) -> Dict[str, Any]:
        """
        6모자 토론 시작

        Args:
            question: 사용자 질문
            session_id: 세션 ID

        Returns:
            토론 시작 정보
        """
        # 임시로 세션 검증 완전히 건너뛰기 (6모자 시스템 테스트용)
        print(f"DEBUG: 세션 검증 건너뛰기 - session_id: {session_id}")
        # session = await self.session_service.get_session(session_id)
        # if not session:
        #     raise ValueError(f"유효하지 않은 세션입니다. 세션 ID: {session_id}")

        # coin_used = await self.session_service.use_coin(session_id)
        # if not coin_used:
        #     raise ValueError(f"코인이 부족합니다.")

        # 초기 상태 생성
        initial_state = create_initial_state(
            user_question=question, session_id=session_id, streaming_enabled=True
        )

        discussion_id = initial_state.get("discussion_id", "")

        return {
            "discussion_id": discussion_id,
            "status": "started",
            "question": question,
            "session_id": session_id,
        }

    async def stream_discussion(
        self, question: str, session_id: str
    ) -> AsyncGenerator[str, None]:
        """
        6모자 토론 스트리밍 생성기

        Args:
            question: 사용자 질문
            session_id: 세션 ID

        Yields:
            SSE 형식의 이벤트 스트림
        """
        try:
            print(f"DEBUG: stream_discussion 강제 실행 - question: {question}, session_id: {session_id}")

            # 강제로 6모자 시스템 실행 (세션 검증 완전 생략)
            from app.agents.six_hat_graph import create_six_hat_graph, create_initial_state

            # 바로 그래프 실행
            initial_state = create_initial_state(
                user_question=question, session_id=session_id, streaming_enabled=True
            )
            graph = create_six_hat_graph()
            config = {"configurable": {"thread_id": session_id}}

            print(f"DEBUG: 6모자 그래프 실행 시작!")

            # 스트리밍으로 그래프 실행
            async for event in graph.astream(initial_state, config=config):
                print(f"DEBUG: 그래프 이벤트: {event}")
                # 각 노드 완료 시 이벤트 발송
                for node_name, node_result in event.items():
                    await self._handle_node_event(node_name, node_result)

                    # 모자 노드인 경우 타이핑 효과를 위한 개별 이벤트 발생
                    if node_name in ["white_hat", "red_hat", "black_hat", "yellow_hat", "green_hat", "blue_hat"]:
                        async for typing_event in self._create_typing_events(node_name, node_result):
                            yield typing_event
                    else:
                        yield self._create_node_event(node_name, node_result)

            return  # 여기서 함수 종료

            # 기존 코드는 실행되지 않음
            discussion_info = await self.start_discussion(question, session_id)
            discussion_id = discussion_info["discussion_id"]

            # 토론 시작 이벤트
            yield self._create_sse_event(
                "discussion_started",
                {
                    "discussion_id": discussion_id,
                    "question": question,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            # 초기 상태 생성
            initial_state = create_initial_state(
                user_question=question, session_id=session_id
            )

            # 그래프 실행 설정
            config = {"configurable": {"thread_id": session_id}}

            # 스트리밍으로 그래프 실행
            async for event in self.graph.astream(initial_state, config=config):
                # 각 노드 완료 시 이벤트 발송
                for node_name, node_result in event.items():
                    await self._handle_node_event(node_name, node_result)
                    yield self._create_node_event(node_name, node_result)

            # 토론 완료 이벤트
            yield self._create_sse_event(
                "discussion_completed",
                {
                    "discussion_id": discussion_id,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            # 오류 이벤트
            yield self._create_sse_event(
                "error",
                {
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

    async def _create_typing_events(self, node_name: str, node_result: Dict):
        """모자 노드를 타이핑 효과를 위한 개별 이벤트로 분할"""
        timestamp = datetime.utcnow().isoformat()

        # 모자 정보 매핑
        hat_mapping = {
            "white_hat": {"color": "white", "name": "하얀 모자", "role": "객관적 정보 분석"},
            "red_hat": {"color": "red", "name": "빨간 모자", "role": "감정과 직감"},
            "black_hat": {"color": "black", "name": "검은 모자", "role": "비판적 분석"},
            "yellow_hat": {"color": "yellow", "name": "노란 모자", "role": "긍정적 측면"},
            "green_hat": {"color": "green", "name": "초록 모자", "role": "창의적 아이디어"},
            "blue_hat": {"color": "blue", "name": "파란 모자", "role": "토론 관리"},
        }

        if node_name in hat_mapping:
            hat_info = hat_mapping[node_name]
            hat_response = node_result.get(f"{node_name}_response", {})
            content = hat_response.get("content", "")

            # 모자 응답 시작 이벤트
            yield self._create_sse_event(
                "hat_response_start",
                {
                    "hat": hat_info,
                    "timestamp": timestamp,
                },
            )

            # 텍스트를 청크로 분할하여 전송
            if content:
                chunks = self._split_text_to_chunks(content, chunk_size=20)
                for chunk in chunks:
                    yield self._create_sse_event(
                        "hat_response_chunk",
                        {
                            "hat": hat_info,
                            "chunk": chunk,
                            "timestamp": timestamp,
                        },
                    )

            # 모자 응답 완료 이벤트
            yield self._create_sse_event(
                "hat_response_complete",
                {
                    "hat": hat_info,
                    "content": content,
                    "success": hat_response.get("success", True),
                    "timestamp": timestamp,
                },
            )

    async def _handle_node_event(self, node_name: str, node_result: Dict) -> None:
        """노드 이벤트 처리"""
        # 특정 노드에 대한 추가 처리 로직
        if node_name in [
            "white_hat",
            "red_hat",
            "black_hat",
            "yellow_hat",
            "green_hat",
            "blue_hat",
        ]:
            # 모자별 특별 처리
            pass
        elif node_name == "quality_check":
            # 품질 검증 처리
            pass

    def _create_node_event(self, node_name: str, node_result: Dict) -> str:
        """노드 결과를 SSE 이벤트로 변환"""
        timestamp = datetime.utcnow().isoformat()

        # 모자 노드 처리
        hat_mapping = {
            "white_hat": {"color": "white", "name": "하얀 모자", "role": "객관적 정보 분석"},
            "red_hat": {"color": "red", "name": "빨간 모자", "role": "감정과 직감"},
            "black_hat": {"color": "black", "name": "검은 모자", "role": "비판적 분석"},
            "yellow_hat": {"color": "yellow", "name": "노란 모자", "role": "긍정적 측면"},
            "green_hat": {"color": "green", "name": "초록 모자", "role": "창의적 아이디어"},
            "blue_hat": {"color": "blue", "name": "파란 모자", "role": "토론 관리"},
        }

        if node_name in hat_mapping:
            hat_info = hat_mapping[node_name]
            hat_response = node_result.get(f"{node_name}_response", {})
            content = hat_response.get("content", "")

            # 타이핑 효과를 위한 모자 이벤트 반환
            return self._create_sse_event(
                "hat_completed",
                {
                    "hat": hat_info,
                    "content": content,
                    "success": hat_response.get("success", True),
                    "timestamp": timestamp,
                },
            )

        elif node_name == "intent_classify":
            return self._create_sse_event(
                "intent_classified",
                {
                    "intent": node_result.get("intent", ""),
                    "timestamp": timestamp,
                },
            )

        elif node_name == "quality_check":
            return self._create_sse_event(
                "quality_checked",
                {
                    "passed": node_result.get("quality_check_passed", False),
                    "score": node_result.get("quality_score", 0),
                    "feedback": node_result.get("quality_feedback", ""),
                    "timestamp": timestamp,
                },
            )

        elif node_name == "recirculation":
            return self._create_sse_event(
                "recirculation_started",
                {
                    "iteration": node_result.get("iteration_count", 0),
                    "timestamp": timestamp,
                },
            )

        elif node_name in ["simple_response", "final_response"]:
            return self._create_sse_event(
                "final_response",
                {
                    "content": node_result.get("final_response", ""),
                    "discussion_type": node_result.get("discussion_type", ""),
                    "quality_info": node_result.get("quality_info"),
                    "timestamp": timestamp,
                },
            )

        else:
            # 기타 노드
            return self._create_sse_event(
                "node_completed",
                {
                    "node": node_name,
                    "stage": node_result.get("current_stage", ""),
                    "timestamp": timestamp,
                },
            )

    def _create_sse_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """SSE 이벤트 문자열 생성"""
        event_data = {"type": event_type, **data}
        return f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

    def _split_text_to_chunks(self, text: str, chunk_size: int = 30) -> list[str]:
        """텍스트를 청크 단위로 분할"""
        if not text:
            return []

        # 먼저 문장 단위로 분할 시도 (한국어)
        sentences = []
        current_sentence = ""

        for char in text:
            current_sentence += char
            # 문장 끝 표시 문자로 분할
            if char in '.!?。':
                sentences.append(current_sentence.strip())
                current_sentence = ""

        # 마지막 문장 처리
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        # 문장이 너무 길면 단어 단위로 재분할
        final_chunks = []
        for sentence in sentences:
            if len(sentence) <= chunk_size:
                final_chunks.append(sentence)
            else:
                # 긴 문장은 단어 단위로 분할
                words = sentence.split()
                current_chunk = ""

                for word in words:
                    if len(current_chunk + " " + word) <= chunk_size:
                        current_chunk += (" " + word) if current_chunk else word
                    else:
                        if current_chunk:
                            final_chunks.append(current_chunk)
                        current_chunk = word

                if current_chunk:
                    final_chunks.append(current_chunk)

        return final_chunks


class StreamingDiscussionManager:
    """스트리밍 토론 관리자 (싱글톤 패턴)"""

    _instance = None
    _active_discussions = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start_streaming_discussion(
        self, discussion_id: str, service: DiscussionService
    ) -> None:
        """스트리밍 토론 시작"""
        self._active_discussions[discussion_id] = service

    def stop_streaming_discussion(self, discussion_id: str) -> None:
        """스트리밍 토론 종료"""
        if discussion_id in self._active_discussions:
            del self._active_discussions[discussion_id]

    def get_active_discussions(self) -> Dict[str, DiscussionService]:
        """활성 토론 목록 반환"""
        return self._active_discussions.copy()