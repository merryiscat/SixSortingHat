"""
프롬프트 관리 시스템
"""

from typing import Dict, Optional
from .six_hats import (
    WHITE_HAT_SYSTEM_PROMPT,
    RED_HAT_SYSTEM_PROMPT,
    BLACK_HAT_SYSTEM_PROMPT,
    YELLOW_HAT_SYSTEM_PROMPT,
    GREEN_HAT_SYSTEM_PROMPT,
    BLUE_HAT_SYSTEM_PROMPT,
)
from .intent.classification import INTENT_CLASSIFICATION_PROMPT
from .quality.verification import QUALITY_CHECK_PROMPT


class PromptManager:
    """프롬프트 관리 클래스"""

    # 6모자 시스템 프롬프트 매핑
    HAT_PROMPTS = {
        "white": WHITE_HAT_SYSTEM_PROMPT,
        "red": RED_HAT_SYSTEM_PROMPT,
        "black": BLACK_HAT_SYSTEM_PROMPT,
        "yellow": YELLOW_HAT_SYSTEM_PROMPT,
        "green": GREEN_HAT_SYSTEM_PROMPT,
        "blue": BLUE_HAT_SYSTEM_PROMPT,
    }

    @classmethod
    def get_hat_prompt(cls, hat_color: str) -> Optional[str]:
        """특정 모자의 시스템 프롬프트 반환"""
        return cls.HAT_PROMPTS.get(hat_color)

    @classmethod
    def get_intent_classification_prompt(cls) -> str:
        """의도 분류 프롬프트 반환"""
        return INTENT_CLASSIFICATION_PROMPT

    @classmethod
    def get_quality_check_prompt(cls) -> str:
        """품질 검증 프롬프트 반환"""
        return QUALITY_CHECK_PROMPT

    @classmethod
    def get_all_hat_colors(cls) -> list:
        """모든 모자 색깔 목록 반환"""
        return list(cls.HAT_PROMPTS.keys())

    @classmethod
    def format_user_prompt(
        cls, question: str, context: Optional[Dict] = None, hat_color: str = None
    ) -> str:
        """사용자 질문을 모자별 프롬프트에 맞게 포맷팅"""
        formatted = f"질문: {question}\n\n"

        if context and "previous_responses" in context:
            formatted += "이전 모자들의 답변:\n"
            for i, response in enumerate(context["previous_responses"], 1):
                hat_name = response.get("hat_name", "알 수 없는 모자")
                content = response.get("content", "")[:200]
                formatted += f"{i}. {hat_name}: {content}...\n"
            formatted += "\n"

        if hat_color:
            hat_names = {
                "white": "하얀 모자",
                "red": "빨간 모자",
                "black": "검은 모자",
                "yellow": "노란 모자",
                "green": "초록 모자",
                "blue": "파란 모자",
            }
            hat_name = hat_names.get(hat_color, "모자")
            formatted += f"{hat_name}의 관점에서 위 질문에 대해 답변해주세요."

        return formatted