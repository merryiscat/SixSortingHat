# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 이 문서의 성격

**이 프로젝트는 1차 구현이 중단된 후 재시작(rebuild) 단계입니다.**
저장소에 남아있는 코드는 "동작하는 제품"이 아니라 **참고용 유산(legacy)** 입니다.
이 문서는 새 구현에 **승계할 자산**과 **반복하면 안 되는 함정**만 정리합니다.

기존 CLAUDE.md(문서 기반 개발 워크플로우 안내)는 git 히스토리(`git show 8ae8c59:CLAUDE.md`)에 보존되어 있습니다.

---

## 0. 시크릿 위생 (처리 완료, 2026-07-27)

재시작에 앞서 아래는 모두 정리되었습니다. 새 구현에서도 이 상태를 유지하십시오.

- **노출됐던 OpenAI 키(`sk-TeCbZs...`)는 폐기됨.** git 히스토리에 문자열이 남아 있지만 무효하므로 추가 조치 불필요.
- `.env`, `backend/.env`, `backend/sixsortinghat_dev.db` **git 추적 해제** (`git rm --cached`). 파일은 작업 트리에 그대로 있습니다.
- 루트 `.gitignore`를 **UTF-8로 재작성**. 기존 파일은 UTF-16 LE라 git이 규칙을 전혀 읽지 못했습니다 — **에디터에서 `.gitignore`를 저장할 때 인코딩이 UTF-16으로 되돌아가지 않는지 주의하십시오.**
- `backend/.env.example` 추가. 새 키는 여기가 아니라 `backend/.env`(추적 제외)에 넣습니다.

---

## 1. 프로젝트 개요

SixSortingHat은 에드워드 드 보노의 6색깔 모자 사고법을 LLM 멀티 에이전트로 구현한 토론형 챗봇입니다.
6개 에이전트(하양=사실 / 빨강=감정 / 검정=위험 / 노랑=긍정 / 초록=창의 / 파랑=진행관리)가 순차적으로 사고를 확장하고, 파란 모자가 종합·품질 검증합니다.

원본 기획 백서: **[docs/0_architecture.md](docs/0_architecture.md)** — 이 프로젝트에서 가장 신뢰도 높은 문서이며, 재시작의 출발점입니다.

---

## 2. 승계 자산 (가치 순)

### A. 설계 문서 `docs/` — 신뢰도 등급 주의

| 문서 | 상태 | 승계 판단 |
|---|---|---|
| `0_architecture.md` | 원본 기획 백서, 내용 충실 | **그대로 승계**. 요구사항의 단일 진실원 |
| `1_goal_scope_definition.md` ~ `5_data_model_schema.md` | 상세 설계, 작성 완료 | 승계하되 **구현과 대조 필요** (아래 3장 갭 참고) |
| `6_master_execution_plan.md` | TASK-001~024 정의. **진행률 기록(70% 완료)은 부정확** | TASK 목록 구조만 승계, 상태값은 전부 리셋 |
| `7_unit_Integration_Test.md` (49줄), `8_bug_report.md` | **빈 템플릿 껍데기** (제목만 있고 내용 없음) | 승계 가치 없음. 새로 작성 |

### B. 프롬프트 자산 `backend/app/prompts/` — **재사용 가치 최상**
- `six_hats/{white,red,black,yellow,green,blue}_hat.py`: 모자별 시스템 프롬프트
- `intent/classification.py`: 단순/복합 질문 의도 분류
- `quality/verification.py`: 토론 품질 검증
- `__init__.py`의 `PromptManager`: 색상 키 → 프롬프트 매핑 + 이전 모자 답변을 컨텍스트로 포맷팅
- 프레임워크와 무관하게 **가장 먼저 이식할 부분**

### C. LangGraph 골격 `backend/app/agents/` — 구조 패턴만 승계
`reference/langgraph/{State,Node,Graph}.py` 패턴을 따른 3분할 구조:
- `six_hat_state.py`: `SixHatState` TypedDict (모자별 응답 + 진행 상태 + 품질 + `messages`)
- `six_hat_nodes.py`: 노드 함수 11개
- `six_hat_graph.py`: `StateGraph` 조립 + 조건부 라우팅

흐름: `user_input → intent_classify →(simple) simple_response` / `→(complex) white → red → black → yellow → green → blue → quality_check →(pass) final_response / (fail) recirculation → white...` (최대 3회)

### D. 프론트엔드 프로토타입 `frontend/*.html`
- Tailwind CDN 기반 단일 HTML 3종 (`index.html` 채팅, `home.html` 목록, `chat.html` 1292줄 완성형)
- **6모자 색상 시스템 CSS 변수**(`.hat-white` ~ `.hat-blue`)는 그대로 쓸 만함
- `chat.html`은 `fetch()` + 수동 스트림 파싱으로 SSE를 소비 (EventSource 아님 — POST/헤더 제약 회피용)
- `reference/ui/`에 원본 목업 존재

### E. 인프라
- `docker-compose.yml`: PostgreSQL 15 + Redis 7 (healthcheck 포함). 바로 재사용 가능
- `backend/alembic/`: 마이그레이션 뼈대 (`sessions` 테이블 1개뿐)

---

## 3. 설계 대비 구현 갭 — **재시작 시 반드시 확인할 목록**

`docs/6`은 "70% 완료"라고 기록하지만, 실제로는 **해피패스 데모 수준**입니다. 문서를 믿지 말고 아래를 기준으로 삼으십시오.

### 설계에 있으나 미구현
- **모자 순서를 매 라운드 변경** (`docs/0` 섹션 2.2 명시 요구) → 미구현. `six_hat_graph.py`의 `hat_sequence_route()`는 정의만 되고 그래프에 연결되지 않은 **죽은 코드**이며, 실제 흐름은 고정 엣지 체인입니다.
- **재순환 시 쿼리 확장** → 미구현. `recirculation_node`는 `completed_hats`만 비우는데, 고정 엣지 구조라 아무 효과가 없습니다. 같은 질문으로 그대로 재실행됩니다.
- **LangChain Tool / MCP 연동** (웹검색·크롤링) → 전무
- **D3.js 논증 그래프 시각화**, **map-reduce + refine 하이브리드 요약** → 전무
- **PostgreSQL checkpointer** → 실제로는 `MemorySaver` (프로세스 재시작 시 상태 소실)
- **모바일 앱(RN/Flutter)** → 정적 HTML로 대체됨
- **LangSmith 관찰성** → 미설정

### 구현되었으나 깨져 있는 부분
- `discussion_service.py::stream_discussion` — 중간의 `return` 이후로 **약 50줄이 도달 불가 죽은 코드**. `discussion_started`/`discussion_completed` 이벤트가 실제로는 발송되지 않습니다.
- **세션·코인 검증이 통째로 주석 처리**되어 있습니다 (`start_discussion`, `stream_discussion`). MVP의 "세션당 5코인" 정책이 무력화된 상태.
- `QualityChecker.check_quality` — LLM 출력을 `"점수:"`, `"결과:"` 한국어 접두사 **문자열 파싱**. 형식이 어긋나면 조용히 기본값으로 떨어지고, **예외 발생 시 무조건 `passed=True`**로 통과시킵니다. → 새 구현에서는 `with_structured_output` / Pydantic 스키마 사용 권장.
- `simple_response_node` — LLM 호출이 아니라 `"안녕"`, `"누구"` 같은 **키워드 if문 하드코딩**.
- 설정 이중화 — `config.py`(Postgres)와 `config_dev.py`(SQLite)가 공존하는데 **앱 전체가 `dev_settings`를 하드 임포트**합니다. `config.py`는 사실상 미사용.
- Redis도 동일 — `database.py`가 `MemoryCache` 클래스로 대체 운영. 프로세스 로컬이라 다중 워커에서 깨집니다.
- 노드가 `{**state, ...}`로 **전체 상태를 반환** — LangGraph의 부분 업데이트 관례와 다르고, `messages`(`add_messages` 리듀서)와 충돌 소지가 있습니다.
- `simple_response_node` / `final_response_node`가 `SixHatState` 그래프 안에서 **다른 스키마(`EndState`)를 반환**합니다. 스키마 일관성 재설계 필요.
- 리스트 상태(`all_responses`, `completed_hats`)를 **in-place `append` 후 반환** — 병렬 실행·체크포인트 복원 시 위험.

### 기술 스택 재검토 필요
- 의존성 핀이 2023~2024년에 멈춰 있습니다: `fastapi==0.104.1`, `pydantic-settings 2.4`, `langgraph>=0.1.0`.
- `backend/requirements.txt`와 `pyproject.toml`의 버전이 **서로 다릅니다** (`langgraph==0.0.20` vs `>=0.1.0`). uv/`pyproject.toml` 기준으로 단일화하고 `requirements.txt`는 폐기 권장.
- `aioredis==2.0.1`은 유지보수 중단됨 (`redis-py`의 `redis.asyncio`로 흡수). 실제 코드도 이미 `redis.asyncio`를 씁니다 — 의존성만 잔재.
- LLM은 `gpt-4o-mini` 전제로 설계됨. 재시작 시 모델 선택 재검토 대상.

---

## 4. 기존 코드 실행 방법 (검증용)

키를 재발급해 `backend/.env`에 넣은 뒤:

```bash
cd backend
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- 앱: http://localhost:8000/app/ · Swagger: `/docs` · 헬스: `/health`
- 6모자 통합 스모크 테스트: `cd backend && uv run python test_six_hat_system.py`
  (pytest가 아닌 **`asyncio.run` 스크립트**입니다. 실제 OpenAI를 호출하므로 유료·비결정적이며, 단위 테스트는 존재하지 않습니다.)
- API 스모크: `cd backend && uv run python test_api.py`
- 마이그레이션: `cd backend && uv run alembic upgrade head`
- 인프라: `docker-compose up -d` (Postgres 5432, Redis 6379 — 현재 코드는 실제로 사용하지 않음)

---

## 5. 개발 원칙 (승계)

이 프로젝트는 **문서 기반 개발**을 유지합니다.

1. 구현 전 `docs/`의 해당 설계 문서를 먼저 갱신하고, 그 문서를 근거로 코드를 작성합니다.
2. 작업 완료 후 CLAUDE.md와 영향받는 설계 문서를 갱신합니다.
3. 변경 영역별 문서 매핑:
   - 기능 → `docs/2_detailed_functional_specification.md`
   - UI → `docs/3_ui_design_system.md`
   - API → `docs/4_api_specification.md`
   - 스키마 → `docs/5_data_model_schema.md`
   - TASK 상태 → `docs/6_master_execution_plan.md`
   - 테스트 → `docs/7_unit_Integration_Test.md`, 버그 → `docs/8_bug_report.md`
4. **레거시 코드를 근거로 삼지 마십시오.** 위 3장의 갭 목록에 해당하는 동작은 "구현됨"으로 간주하지 않습니다.

### MVP 범위 (docs/0 §6 기준, 유효)
- 인증 없음, 세션당 5코인 → 이후 OAuth2 + 결제
- 일방향 그룹채팅 UX → 이후 사용자 개입 포인트 추가
- 비용 무시하고 품질 우선 → 이후 토큰 최적화
- 텍스트 전용 (멀티모달 계획 없음)
- 배포 타겟: Docker 이미지 → 홈서버
