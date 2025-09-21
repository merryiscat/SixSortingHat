"""
6모자 토론 시스템 LangGraph 구성
reference 프로젝트의 Graph.py 패턴 적용
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .six_hat_state import SixHatState, EndState
from .six_hat_nodes import (
    user_input_node,
    intent_classify_node,
    white_hat_node,
    red_hat_node,
    black_hat_node,
    yellow_hat_node,
    green_hat_node,
    blue_hat_node,
    quality_check_node,
    recirculation_node,
    simple_response_node,
    final_response_node,
)


# ──────────────────────── 라우팅 함수들 ────────────────────────

def intent_route(state: SixHatState) -> str:
    """의도 분류 결과에 따른 라우팅"""
    intent = state.get("intent", "complex")
    return intent


def quality_route(state: SixHatState) -> str:
    """품질 검증 결과에 따른 라우팅"""
    quality_passed = state.get("quality_check_passed", False)
    iteration_count = state.get("iteration_count", 0)

    if quality_passed or iteration_count >= 3:
        return "approved"
    else:
        return "recirculate"


def hat_sequence_route(state: SixHatState) -> str:
    """다음 모자 결정 라우팅"""
    completed_hats = state.get("completed_hats", [])

    # 6모자 순서: white → red → black → yellow → green → blue
    hat_order = ["white", "red", "black", "yellow", "green", "blue"]

    for hat in hat_order:
        if hat not in completed_hats:
            return hat

    # 모든 모자 완료 시 품질 검증으로
    return "quality_check"


# ──────────────────────── 그래프 생성 함수 ────────────────────────

def create_six_hat_graph():
    """6모자 토론 시스템 그래프 생성"""

    # StateGraph 초기화
    builder = StateGraph(SixHatState)

    # ──────────── 노드 추가 ────────────

    # 초기 처리 노드들
    builder.add_node("user_input", user_input_node)
    builder.add_node("intent_classify", intent_classify_node)

    # 6모자 노드들
    builder.add_node("white_hat", white_hat_node)
    builder.add_node("red_hat", red_hat_node)
    builder.add_node("black_hat", black_hat_node)
    builder.add_node("yellow_hat", yellow_hat_node)
    builder.add_node("green_hat", green_hat_node)
    builder.add_node("blue_hat", blue_hat_node)

    # 제어 노드들
    builder.add_node("quality_check", quality_check_node)
    builder.add_node("recirculation", recirculation_node)

    # 응답 노드들
    builder.add_node("simple_response", simple_response_node)
    builder.add_node("final_response", final_response_node)

    # ──────────── 엣지 연결 ────────────

    # 시작점 설정
    builder.set_entry_point("user_input")

    # 기본 플로우
    builder.add_edge("user_input", "intent_classify")

    # 의도 분류에 따른 분기
    builder.add_conditional_edges(
        "intent_classify",
        intent_route,
        {
            "simple": "simple_response",
            "complex": "white_hat",  # 6모자 토론 시작
        },
    )

    # 6모자 순차 실행
    builder.add_edge("white_hat", "red_hat")
    builder.add_edge("red_hat", "black_hat")
    builder.add_edge("black_hat", "yellow_hat")
    builder.add_edge("yellow_hat", "green_hat")
    builder.add_edge("green_hat", "blue_hat")

    # 파란 모자 완료 후 품질 검증
    builder.add_edge("blue_hat", "quality_check")

    # 품질 검증 결과에 따른 분기
    builder.add_conditional_edges(
        "quality_check",
        quality_route,
        {
            "approved": "final_response",
            "recirculate": "recirculation",
        },
    )

    # 재순환 후 다시 하얀 모자부터 시작
    builder.add_edge("recirculation", "white_hat")

    # 종료점 설정
    builder.set_finish_point("simple_response")
    builder.set_finish_point("final_response")

    # ──────────── 체크포인터 설정 ────────────

    # MemorySaver로 중간 상태 저장
    memory = MemorySaver()
    app = builder.compile(checkpointer=memory)

    return app


# ──────────────────────── 편의 함수들 ────────────────────────

def create_initial_state(
    user_question: str, session_id: str = None, streaming_enabled: bool = True
) -> SixHatState:
    """초기 상태 생성"""
    import uuid

    if not session_id:
        session_id = str(uuid.uuid4())

    return {
        "user_question": user_question,
        "session_id": session_id,
        "discussion_id": "",
        "intent": "",
        "white_hat_response": None,
        "red_hat_response": None,
        "black_hat_response": None,
        "yellow_hat_response": None,
        "green_hat_response": None,
        "blue_hat_response": None,
        "current_hat": "",
        "hat_sequence": ["white", "red", "black", "yellow", "green", "blue"],
        "completed_hats": [],
        "iteration_count": 0,
        "quality_check_passed": False,
        "quality_score": 0,
        "quality_feedback": "",
        "final_synthesis": None,
        "all_responses": [],
        "messages": [],
        "streaming_enabled": streaming_enabled,
        "current_stage": "initialized",
    }


async def run_six_hat_discussion(user_question: str, session_id: str = None) -> EndState:
    """6모자 토론 실행 (테스트용)"""
    graph = create_six_hat_graph()
    initial_state = create_initial_state(user_question, session_id)

    # 그래프 실행
    config = {"configurable": {"thread_id": session_id or "test"}}
    result = await graph.ainvoke(initial_state, config=config)

    return result