"""
6모자 시스템 테스트 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.six_hat_graph import run_six_hat_discussion


async def test_simple_question():
    """단순 질문 테스트"""
    print("=== 단순 질문 테스트 ===")
    try:
        result = await run_six_hat_discussion("안녕하세요", "test_simple")
        print("SUCCESS: 단순 질문 처리 완료")
        print(f"Discussion Type: {result.get('discussion_type', 'N/A')}")
        print(f"Response: {result.get('final_response', '')[:100]}")
        return True
    except Exception as e:
        print(f"ERROR: 단순 질문 테스트 실패 - {e}")
        return False


async def test_complex_question():
    """복합 질문 테스트"""
    print("\n=== 복합 질문 테스트 ===")
    try:
        result = await run_six_hat_discussion(
            "AI가 인간 사회에 미치는 영향은 무엇인가요?", "test_complex"
        )
        print("SUCCESS: 복합 질문 처리 완료")
        print(f"Discussion Type: {result.get('discussion_type', 'N/A')}")
        print(f"Total Responses: {len(result.get('all_responses', []))}")

        quality_info = result.get('quality_info', {})
        print(f"Quality Score: {quality_info.get('score', 'N/A')}")
        print(f"Quality Passed: {quality_info.get('passed', 'N/A')}")
        print(f"Iterations: {quality_info.get('iterations', 'N/A')}")

        final_response = result.get('final_response', '')
        print(f"Final Response Preview: {final_response[:150]}...")
        return True
    except Exception as e:
        print(f"ERROR: 복합 질문 테스트 실패 - {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_hat_agents():
    """개별 모자 에이전트 테스트"""
    print("\n=== 개별 모자 에이전트 테스트 ===")
    try:
        from app.agents.hat_agents import WhiteHatAgent, IntentClassifier

        # 의도 분류기 테스트
        classifier = IntentClassifier()
        simple_intent = await classifier.classify("안녕하세요")
        complex_intent = await classifier.classify("AI의 장단점을 분석해주세요")

        print(f"Intent Classification Test:")
        print(f"  '안녕하세요' -> {simple_intent}")
        print(f"  'AI의 장단점을 분석해주세요' -> {complex_intent}")

        # 하얀 모자 테스트
        white_hat = WhiteHatAgent()
        response = await white_hat.think("AI란 무엇인가요?")

        print(f"White Hat Test:")
        print(f"  Success: {response.get('success', False)}")
        print(f"  Content Preview: {response.get('content', '')[:100]}...")

        return True
    except Exception as e:
        print(f"ERROR: 개별 에이전트 테스트 실패 - {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """메인 테스트 실행"""
    print("6모자 시스템 종합 테스트 시작")
    print("=" * 50)

    results = []

    # 개별 컴포넌트 테스트
    results.append(await test_hat_agents())

    # 단순 질문 테스트
    results.append(await test_simple_question())

    # 복합 질문 테스트
    results.append(await test_complex_question())

    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약:")
    print(f"성공: {sum(results)}/{len(results)}")

    if all(results):
        print("모든 테스트 통과! 6모자 시스템이 정상 작동합니다.")
    else:
        print("일부 테스트 실패. 시스템 점검이 필요합니다.")


if __name__ == "__main__":
    asyncio.run(main())