"""
6모자 토론 시스템 노드 함수들
reference 프로젝트의 Node.py 패턴 적용
"""

import uuid
from typing import Dict, Any
from .six_hat_state import SixHatState, SimpleResponseState, EndState
from .hat_agents import (
    WhiteHatAgent,
    RedHatAgent,
    BlackHatAgent,
    YellowHatAgent,
    GreenHatAgent,
    BlueHatAgent,
    IntentClassifier,
    QualityChecker,
)


# reference 프로젝트의 데코레이터 패턴 적용 (현재는 간단하게)
def log_node_outputs(node_name: str, **kwargs):
    """노드 출력 로깅 데코레이터"""

    def decorator(func):
        async def wrapper(*args, **kwargs_inner):
            print(f"[START] Node [{node_name}]")
            result = await func(*args, **kwargs_inner)
            print(f"[DONE] Node [{node_name}]")
            return result

        return wrapper

    return decorator


# ──────────────────────── 초기 처리 노드들 ────────────────────────

@log_node_outputs("user_input_node")
async def user_input_node(state: SixHatState) -> SixHatState:
    """사용자 입력 처리 노드"""
    user_question = state["user_question"]
    session_id = state.get("session_id", str(uuid.uuid4()))
    discussion_id = f"disc_{session_id}_{int(__import__('time').time())}"

    # 기존 메시지에 새로운 사용자 입력 추가
    current_messages = state.get("messages", [])
    updated_messages = current_messages + [("user", user_question)]

    return {
        **state,
        "user_question": user_question,
        "session_id": session_id,
        "discussion_id": discussion_id,
        "messages": updated_messages,
        "current_stage": "input_processing",
        "streaming_enabled": state.get("streaming_enabled", True),
        "iteration_count": 0,
        "completed_hats": [],
        "all_responses": [],
    }


@log_node_outputs("intent_classify_node")
async def intent_classify_node(state: SixHatState) -> SixHatState:
    """의도 분류 노드"""
    user_question = state["user_question"]
    classifier = IntentClassifier()

    intent = await classifier.classify(user_question)

    return {
        **state,
        "intent": intent,
        "current_stage": "intent_classified",
    }


# ──────────────────────── 6모자 개별 노드들 ────────────────────────

@log_node_outputs("white_hat_node")
async def white_hat_node(state: SixHatState) -> SixHatState:
    """하얀 모자 노드 - 객관적 정보 분석"""
    user_question = state["user_question"]
    agent = WhiteHatAgent()

    # 컨텍스트 준비 (이전 모자들의 응답)
    context = {"previous_responses": state.get("all_responses", [])}

    response = await agent.think(user_question, context)

    # 응답을 전체 응답 목록에 추가
    all_responses = state.get("all_responses", [])
    all_responses.append(response)

    completed_hats = state.get("completed_hats", [])
    completed_hats.append("white")

    return {
        **state,
        "white_hat_response": response,
        "all_responses": all_responses,
        "completed_hats": completed_hats,
        "current_hat": "white",
        "current_stage": "white_hat_completed",
    }


@log_node_outputs("red_hat_node")
async def red_hat_node(state: SixHatState) -> SixHatState:
    """빨간 모자 노드 - 감정과 직감"""
    user_question = state["user_question"]
    agent = RedHatAgent()

    context = {"previous_responses": state.get("all_responses", [])}
    response = await agent.think(user_question, context)

    all_responses = state.get("all_responses", [])
    all_responses.append(response)

    completed_hats = state.get("completed_hats", [])
    completed_hats.append("red")

    return {
        **state,
        "red_hat_response": response,
        "all_responses": all_responses,
        "completed_hats": completed_hats,
        "current_hat": "red",
        "current_stage": "red_hat_completed",
    }


@log_node_outputs("black_hat_node")
async def black_hat_node(state: SixHatState) -> SixHatState:
    """검은 모자 노드 - 비판적 분석"""
    user_question = state["user_question"]
    agent = BlackHatAgent()

    context = {"previous_responses": state.get("all_responses", [])}
    response = await agent.think(user_question, context)

    all_responses = state.get("all_responses", [])
    all_responses.append(response)

    completed_hats = state.get("completed_hats", [])
    completed_hats.append("black")

    return {
        **state,
        "black_hat_response": response,
        "all_responses": all_responses,
        "completed_hats": completed_hats,
        "current_hat": "black",
        "current_stage": "black_hat_completed",
    }


@log_node_outputs("yellow_hat_node")
async def yellow_hat_node(state: SixHatState) -> SixHatState:
    """노란 모자 노드 - 긍정적 측면"""
    user_question = state["user_question"]
    agent = YellowHatAgent()

    context = {"previous_responses": state.get("all_responses", [])}
    response = await agent.think(user_question, context)

    all_responses = state.get("all_responses", [])
    all_responses.append(response)

    completed_hats = state.get("completed_hats", [])
    completed_hats.append("yellow")

    return {
        **state,
        "yellow_hat_response": response,
        "all_responses": all_responses,
        "completed_hats": completed_hats,
        "current_hat": "yellow",
        "current_stage": "yellow_hat_completed",
    }


@log_node_outputs("green_hat_node")
async def green_hat_node(state: SixHatState) -> SixHatState:
    """초록 모자 노드 - 창의적 아이디어"""
    user_question = state["user_question"]
    agent = GreenHatAgent()

    context = {"previous_responses": state.get("all_responses", [])}
    response = await agent.think(user_question, context)

    all_responses = state.get("all_responses", [])
    all_responses.append(response)

    completed_hats = state.get("completed_hats", [])
    completed_hats.append("green")

    return {
        **state,
        "green_hat_response": response,
        "all_responses": all_responses,
        "completed_hats": completed_hats,
        "current_hat": "green",
        "current_stage": "green_hat_completed",
    }


@log_node_outputs("blue_hat_node")
async def blue_hat_node(state: SixHatState) -> SixHatState:
    """파란 모자 노드 - 토론 관리 및 종합"""
    user_question = state["user_question"]
    agent = BlueHatAgent()

    context = {"previous_responses": state.get("all_responses", [])}
    response = await agent.think(user_question, context)

    all_responses = state.get("all_responses", [])
    all_responses.append(response)

    completed_hats = state.get("completed_hats", [])
    completed_hats.append("blue")

    return {
        **state,
        "blue_hat_response": response,
        "all_responses": all_responses,
        "completed_hats": completed_hats,
        "current_hat": "blue",
        "current_stage": "blue_hat_completed",
        "final_synthesis": response.get("content", ""),
    }


# ──────────────────────── 품질 검증 및 제어 노드들 ────────────────────────

@log_node_outputs("quality_check_node")
async def quality_check_node(state: SixHatState) -> SixHatState:
    """품질 검증 노드"""
    user_question = state["user_question"]
    all_responses = state.get("all_responses", [])

    checker = QualityChecker()
    quality_result = await checker.check_quality(user_question, all_responses)

    return {
        **state,
        "quality_check_passed": quality_result["passed"],
        "quality_score": quality_result["score"],
        "quality_feedback": quality_result["feedback"],
        "current_stage": "quality_checked",
    }


@log_node_outputs("recirculation_node")
async def recirculation_node(state: SixHatState) -> SixHatState:
    """재순환 준비 노드"""
    iteration_count = state.get("iteration_count", 0) + 1

    # 상태 초기화 (재토론을 위해)
    return {
        **state,
        "iteration_count": iteration_count,
        "completed_hats": [],
        "current_stage": "recirculation_started",
        # 기존 응답들은 유지하되, 새로운 라운드 시작
    }


# ──────────────────────── 단순 응답 노드들 ────────────────────────

@log_node_outputs("simple_response_node")
async def simple_response_node(state: SixHatState) -> EndState:
    """단순 질문 응답 노드"""
    user_question = state["user_question"]
    session_id = state.get("session_id", "")

    # 간단한 응답 생성 로직
    if any(greeting in user_question.lower() for greeting in ["안녕", "hello", "hi"]):
        simple_response = "안녕하세요! 저는 6모자 사고법을 활용하는 AI 토론 도우미입니다. 복잡한 문제에 대해 다각도로 분석해드릴 수 있습니다."
        response_type = "greeting"
    elif any(identity in user_question.lower() for identity in ["누구", "뭐야", "무엇", "정체"]):
        simple_response = "저는 Edward de Bono의 6모자 사고법을 기반으로 하는 AI 토론 시스템입니다. 복잡한 주제에 대해 6가지 관점에서 체계적으로 분석해드립니다."
        response_type = "identity"
    else:
        simple_response = "간단한 질문에 대한 답변입니다. 더 복잡한 주제라면 6모자 토론으로 깊이 있는 분석을 받아보시기 바랍니다."
        response_type = "simple_info"

    # 메시지에 응답 추가
    current_messages = state.get("messages", [])
    updated_messages = current_messages + [("assistant", simple_response)]

    return {
        "discussion_id": state.get("discussion_id", ""),
        "final_response": simple_response,
        "discussion_type": "simple",
        "all_responses": [{"content": simple_response, "type": response_type}],
        "quality_info": None,
        "session_id": session_id,
    }


@log_node_outputs("final_response_node")
async def final_response_node(state: SixHatState) -> EndState:
    """최종 응답 생성 노드"""
    discussion_id = state.get("discussion_id", "")
    final_synthesis = state.get("final_synthesis", "")
    all_responses = state.get("all_responses", [])
    session_id = state.get("session_id", "")

    # 품질 정보 정리
    quality_info = {
        "passed": state.get("quality_check_passed", False),
        "score": state.get("quality_score", 0),
        "feedback": state.get("quality_feedback", ""),
        "iterations": state.get("iteration_count", 0),
    }

    # 메시지에 최종 응답 추가
    current_messages = state.get("messages", [])
    updated_messages = current_messages + [("assistant", final_synthesis)]

    return {
        "discussion_id": discussion_id,
        "final_response": final_synthesis,
        "discussion_type": "complex",
        "all_responses": all_responses,
        "quality_info": quality_info,
        "session_id": session_id,
    }