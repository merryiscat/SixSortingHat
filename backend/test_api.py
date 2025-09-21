"""
API 테스트 스크립트
"""

import asyncio
import httpx
import json


async def test_api():
    """API 엔드포인트 테스트"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("INFO: FastAPI 서버 테스트 시작\n")

        # 1. 헬스 체크
        print("1. 헬스 체크 테스트")
        response = await client.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")

        # 2. 루트 엔드포인트
        print("2. 루트 엔드포인트 테스트")
        response = await client.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")

        # 3. 세션 생성
        print("3. 세션 생성 테스트")
        response = await client.post(f"{base_url}/api/v1/sessions/create")
        print(f"Status: {response.status_code}")
        session_data = response.json()
        print(f"Response: {json.dumps(session_data, indent=2, ensure_ascii=False)}\n")

        if response.status_code == 201:
            session_id = session_data["session_id"]

            # 4. 세션 조회
            print("4. 세션 조회 테스트")
            response = await client.get(f"{base_url}/api/v1/sessions/{session_id}")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")

            # 5. 코인 사용
            print("5. 코인 사용 테스트")
            response = await client.post(f"{base_url}/api/v1/sessions/{session_id}/use-coin")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")

            # 6. 토론 시작 (더미)
            print("6. 토론 시작 테스트")
            discussion_payload = {
                "question": "인공지능의 미래에 대해 어떻게 생각하시나요?",
                "session_id": session_id
            }
            response = await client.post(
                f"{base_url}/api/v1/discussions/start",
                json=discussion_payload
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")

        print("SUCCESS: API 테스트 완료!")


if __name__ == "__main__":
    try:
        asyncio.run(test_api())
    except httpx.ConnectError:
        print("ERROR: 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print("서버 실행: cd backend && uv run python -m app.main")
    except Exception as e:
        print(f"ERROR: 테스트 실행 중 오류: {e}")