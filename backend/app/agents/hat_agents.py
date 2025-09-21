"""
6모자 개별 에이전트 클래스들
"""

from .base_hat import BaseHat


class WhiteHatAgent(BaseHat):
    """하얀 모자 - 객관적 정보와 사실 분석"""

    def __init__(self):
        super().__init__(
            hat_color="white",
            hat_name="하얀 모자",
            role_description="객관적 정보와 사실 분석",
        )


class RedHatAgent(BaseHat):
    """빨간 모자 - 감정과 직감"""

    def __init__(self):
        super().__init__(
            hat_color="red",
            hat_name="빨간 모자",
            role_description="감정과 직감",
        )


class BlackHatAgent(BaseHat):
    """검은 모자 - 비판적 분석과 위험 요소"""

    def __init__(self):
        super().__init__(
            hat_color="black",
            hat_name="검은 모자",
            role_description="비판적 분석과 위험 요소",
        )


class YellowHatAgent(BaseHat):
    """노란 모자 - 긍정적 측면과 기회"""

    def __init__(self):
        super().__init__(
            hat_color="yellow",
            hat_name="노란 모자",
            role_description="긍정적 측면과 기회",
        )


class GreenHatAgent(BaseHat):
    """초록 모자 - 창의적 아이디어와 대안"""

    def __init__(self):
        super().__init__(
            hat_color="green",
            hat_name="초록 모자",
            role_description="창의적 아이디어와 대안",
        )


class BlueHatAgent(BaseHat):
    """파란 모자 - 토론 관리와 품질 검증"""

    def __init__(self):
        super().__init__(
            hat_color="blue",
            hat_name="파란 모자",
            role_description="토론 관리와 품질 검증",
        )


class IntentClassifier:
    """의도 분류기"""

    def __init__(self):
        from langchain_openai import ChatOpenAI
        from app.core.config_dev import dev_settings as settings
        from app.prompts import PromptManager

        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1,  # 분류는 낮은 온도로
            max_tokens=50,
        )
        self.system_prompt = PromptManager.get_intent_classification_prompt()

    async def classify(self, question: str) -> str:
        """
        질문의 의도를 분류

        Returns:
            'simple' 또는 'complex'
        """
        try:
            from langchain_core.messages import SystemMessage, HumanMessage

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=question),
            ]

            response = await self.llm.ainvoke(messages)
            result = response.content.strip().lower()

            # 결과 검증
            if result in ["simple", "complex"]:
                return result
            else:
                # 기본값으로 complex 반환 (안전한 선택)
                return "complex"

        except Exception:
            # 오류 시 기본값으로 complex 반환
            return "complex"


class QualityChecker:
    """품질 검증기"""

    def __init__(self):
        from langchain_openai import ChatOpenAI
        from app.core.config_dev import dev_settings as settings
        from app.prompts import PromptManager

        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
            max_tokens=300,
        )
        self.system_prompt = PromptManager.get_quality_check_prompt()

    async def check_quality(self, question: str, responses: list) -> dict:
        """
        토론 품질을 검증

        Args:
            question: 원본 질문
            responses: 각 모자의 응답들

        Returns:
            {'passed': bool, 'score': int, 'feedback': str}
        """
        try:
            from langchain_core.messages import SystemMessage, HumanMessage

            # 응답들을 텍스트로 정리
            discussion_text = f"원본 질문: {question}\n\n"
            for i, response in enumerate(responses, 1):
                hat_name = response.get("hat_name", "알 수 없는 모자")
                content = response.get("content", "")
                discussion_text += f"{i}. {hat_name}: {content}\n\n"

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=discussion_text),
            ]

            response = await self.llm.ainvoke(messages)
            result_text = response.content.strip()

            # 결과 파싱
            lines = result_text.split("\n")
            score = 0
            passed = False
            feedback = ""

            for line in lines:
                if line.startswith("점수:"):
                    try:
                        score = int(line.split("/")[0].split(":")[1].strip())
                    except:
                        score = 50  # 기본값

                elif line.startswith("결과:"):
                    passed = "PASS" in line.upper()

                elif line.startswith("부족한 영역:"):
                    feedback = line.split(":", 1)[1].strip()

            return {"passed": passed, "score": score, "feedback": feedback}

        except Exception as e:
            # 오류 시 기본적으로 통과 처리
            return {"passed": True, "score": 70, "feedback": f"품질 검증 오류: {str(e)}"}