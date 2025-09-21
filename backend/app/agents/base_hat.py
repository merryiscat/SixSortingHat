"""
6모자 에이전트 기본 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config_dev import dev_settings as settings
from app.prompts import PromptManager


class BaseHat(ABC):
    """6모자 에이전트 기본 클래스"""

    def __init__(self, hat_color: str, hat_name: str, role_description: str):
        self.hat_color = hat_color
        self.hat_name = hat_name
        self.role_description = role_description

        # OpenAI LLM 초기화
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
            max_tokens=800,
        )

        # 해당 모자의 시스템 프롬프트 가져오기
        self.system_prompt = PromptManager.get_hat_prompt(hat_color)

    async def think(
        self, question: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        주어진 질문에 대해 해당 모자의 관점으로 사고

        Args:
            question: 사용자 질문
            context: 이전 모자들의 답변 등 컨텍스트

        Returns:
            해당 모자의 사고 결과
        """
        try:
            # 사용자 프롬프트 포맷팅
            user_prompt = PromptManager.format_user_prompt(
                question=question, context=context, hat_color=self.hat_color
            )

            # 메시지 구성
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_prompt),
            ]

            # LLM 호출
            response = await self.llm.ainvoke(messages)

            return {
                "hat_color": self.hat_color,
                "hat_name": self.hat_name,
                "role": self.role_description,
                "content": response.content,
                "success": True,
                "metadata": {
                    "model": settings.OPENAI_MODEL,
                    "temperature": 0.7,
                    "max_tokens": 800,
                },
            }

        except Exception as e:
            return {
                "hat_color": self.hat_color,
                "hat_name": self.hat_name,
                "role": self.role_description,
                "content": f"죄송합니다. {self.hat_name} 관점에서 답변을 생성하지 못했습니다.",
                "success": False,
                "error": str(e),
                "metadata": {"error_message": str(e)},
            }

    def get_info(self) -> Dict[str, str]:
        """모자 정보 반환"""
        return {
            "color": self.hat_color,
            "name": self.hat_name,
            "role": self.role_description,
        }