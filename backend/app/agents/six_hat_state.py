"""
6모자 토론 시스템 상태 정의
"""

from typing import Annotated, List, Dict, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class SixHatState(TypedDict):
    """6모자 토론 전체 상태"""

    # 기본 정보
    user_question: str
    session_id: str
    discussion_id: str

    # 의도 분류 결과
    intent: str  # 'simple' 또는 'complex'

    # 6모자 응답들
    white_hat_response: Optional[Dict]
    red_hat_response: Optional[Dict]
    black_hat_response: Optional[Dict]
    yellow_hat_response: Optional[Dict]
    green_hat_response: Optional[Dict]
    blue_hat_response: Optional[Dict]

    # 진행 상태 관리
    current_hat: str  # 현재 실행 중인 모자
    hat_sequence: List[str]  # 모자 실행 순서
    completed_hats: List[str]  # 완료된 모자들
    iteration_count: int  # 재순환 횟수

    # 품질 검증
    quality_check_passed: bool
    quality_score: int
    quality_feedback: str

    # 최종 결과
    final_synthesis: Optional[str]
    all_responses: List[Dict]  # 모든 모자의 응답 모음

    # 메시지 기록 (reference 프로젝트 패턴)
    messages: Annotated[list, add_messages]

    # 스트리밍용 상태
    streaming_enabled: bool
    current_stage: str  # 현재 진행 단계


class SimpleResponseState(TypedDict):
    """단순 질문 응답 상태"""

    user_question: str
    session_id: str
    response_type: str  # 'greeting', 'identity', 'simple_info'
    simple_response: str
    messages: Annotated[list, add_messages]


class EndState(TypedDict):
    """최종 출력 상태"""

    discussion_id: str
    final_response: str
    discussion_type: str  # 'simple' 또는 'complex'
    all_responses: List[Dict]
    quality_info: Optional[Dict]
    session_id: str