# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

프로젝트는 반드시 문서 기반으로 개발되어야 합니다.
***반드시*** 특정 작업을 완료한 후에는 CLAUDE.md 문서를 업데이트 하시오.
CLAUDE.md 문서에는 설계문서 경로들이 있습니다. 설계가 변경되거나 내용이 추가된 경우에는 경로를 확인하여 설계문서들을 업데이트/변경 하시오.

## 프로젝트 개요 (Project Overview)

SixSortingHat은 에드워드 드 보노의 6색깔 모자 사고법을 LLM으로 구현한 멀티 에이전트 챗봇 시스템입니다. 6개의 서로 다른 역할을 가진 AI 에이전트가 사용자의 질문에 대해 다각도로 토론하여 창의적이고 종합적인 답변을 제공합니다.

**현재 상태**: 설계 단계 (구현 코드 없음, 문서 기반 개발 준비)

## 문서 기반 개발 워크플로우

**중요**: 이 프로젝트는 반드시 문서 기반으로 개발되어야 합니다.

### 필수 규칙
1. 작업 완료 후 반드시 CLAUDE.md 업데이트
2. 설계 변경 시 해당 문서 업데이트
3. docs/ 폴더의 설계 문서를 기반으로 구현

### 개발 프로세스
1. [docs/6_master_execution_plan.md](docs/6_master_execution_plan.md)에서 다음 TASK 확인
2. TASK 상태를 "준비됨" → "진행 중"으로 변경
3. 관련 문서 참조하여 구현
4. 변경사항을 해당 docs 파일에 직접 업데이트
5. TASK 완료 시 상태를 "완료"로 변경

## 개발 환경 빠른 시작

### 백엔드 서버 실행
```bash
cd backend
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 의존성 설치 (필요시)
```bash
cd backend
uv add [패키지명]
```

### 웹 애플리케이션 접속
- **프론트엔드 앱**: http://localhost:8000/app/
- **Swagger UI**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health
- **6모자 시스템 테스트**: POST http://localhost:8000/api/v1/discussions/test-simple

### 환경 설정 파일
- **백엔드 환경변수**: `backend/.env` (OpenAI API 키 설정)
- **패키지 관리**: `backend/pyproject.toml` (uv 기반)
- **데이터베이스**: SQLite (개발용: `sixsortinghat_dev.db`)

### 주요 실행 명령어
```bash
# 서버 시작
cd backend && uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 테스트 실행
cd backend && uv run python test_six_hat_system.py

# 의존성 추가
cd backend && uv add [패키지명]

# 데이터베이스 마이그레이션
cd backend && uv run alembic upgrade head
```

## 핵심 아키텍처

### 시스템 구조
- **백엔드**: Python + FastAPI + LangGraph (uv 패키지 관리)
- **프론트엔드**: 모바일 앱 (Android/iOS)
- **통신**: Server-Sent Events (SSE)
- **데이터**: PostgreSQL/Redis

### 6개 에이전트 역할
- **하얀 모자**: 객관적 정보와 사실
- **빨간 모자**: 감정과 직관
- **검은 모자**: 위험과 비판적 사고
- **노란 모자**: 긍정과 낙관
- **초록 모자**: 창의성과 새로운 아이디어
- **파란 모자**: 사고 과정 관리와 통제

### LangGraph 워크플로우
1. 의도 분류 → 6개 모자 순차 실행
2. 각 에이전트는 이전 답변 참조하여 확장
3. 파란 모자가 최종 검증 및 품질 체크
4. 품질 미달 시 재순환, 합격 시 결과 출력

## 문서 구조 및 참조

### 순차 참조 패턴
각 문서는 이전 번호 문서들을 참조합니다:
- 1번 → 0번 참조
- 2번 → 0번 + 1번 참조
- n번 → 0번 + (n-1)번까지 참조

### 핵심 문서 목록
- **[docs/0_architecture.md](docs/0_architecture.md)**: 전체 시스템 아키텍처
- **[docs/1_goal_scope_definition.md](docs/1_goal_scope_definition.md)**: 프로젝트 목표 및 범위
- **[docs/2_detailed_functional_specification.md](docs/2_detailed_functional_specification.md)**: 상세 기능 명세
- **[docs/3_ui_design_system.md](docs/3_ui_design_system.md)**: UI 디자인 시스템
- **[docs/4_api_specification.md](docs/4_api_specification.md)**: API 명세
- **[docs/5_data_model_schema.md](docs/5_data_model_schema.md)**: 데이터 모델 스키마
- **[docs/6_master_execution_plan.md](docs/6_master_execution_plan.md)**: 실행 계획 및 TASK 관리
- **[docs/7_unit_Integration_Test.md](docs/7_unit_Integration_Test.md)**: 테스트 전략
- **[docs/8_bug_report.md](docs/8_bug_report.md)**: 버그 리포트 및 이슈 추적

## 개발 영역별 참조 가이드

### 백엔드 개발 시
- **LangGraph 구현**: [docs/0_architecture.md](docs/0_architecture.md) 섹션 2
- **API 엔드포인트**: [docs/4_api_specification.md](docs/4_api_specification.md)
- **데이터 모델**: [docs/5_data_model_schema.md](docs/5_data_model_schema.md)

### 프론트엔드 개발 시
- **UI 컴포넌트**: [docs/3_ui_design_system.md](docs/3_ui_design_system.md)
- **사용자 플로우**: [docs/2_detailed_functional_specification.md](docs/2_detailed_functional_specification.md)
- **API 연동**: [docs/4_api_specification.md](docs/4_api_specification.md)

### 테스트 및 품질 관리
- **테스트 전략**: [docs/7_unit_Integration_Test.md](docs/7_unit_Integration_Test.md)
- **버그 추적**: [docs/8_bug_report.md](docs/8_bug_report.md)

## 기술 스택

### 백엔드
- **언어**: Python
- **프레임워크**: FastAPI
- **AI 오케스트레이션**: LangGraph (LangChain)
- **LLM**: GPT-4o-mini (MVP), 추후 특화 모델 고려
- **데이터베이스**: PostgreSQL (체크포인터), Redis (세션)
- **도구**: LangSmith (관찰성)

### 프론트엔드
- **플랫폼**: 크로스플랫폼 모바일 앱
- **통신**: SSE (Server-Sent Events)
- **시각화**: D3.js (WebView 내 렌더링)
- **UI 패턴**: 그룹 채팅 형태 (6개 아바타)

### 배포
- **컨테이너**: Docker
- **타겟**: 홈서버 배포

## 변경사항 기록 원칙

구현 중 변경사항이 발생하면 해당 영역의 문서를 직접 업데이트:

- **API 변경** → [docs/4_api_specification.md](docs/4_api_specification.md)
- **기능 추가/변경** → [docs/2_detailed_functional_specification.md](docs/2_detailed_functional_specification.md)
- **UI 컴포넌트 변경** → [docs/3_ui_design_system.md](docs/3_ui_design_system.md)
- **데이터 스키마 변경** → [docs/5_data_model_schema.md](docs/5_data_model_schema.md)
- **버그 발견** → [docs/8_bug_report.md](docs/8_bug_report.md)
- **테스트 케이스 추가** → [docs/7_unit_Integration_Test.md](docs/7_unit_Integration_Test.md)

## MVP 특징

### 인증
- MVP: 무인증, 세션당 5코인 제공
- 확장: OAuth2 SNS 로그인 + 결제 시스템

### 사용성
- MVP: 일방향 답변 수신 (그룹 채팅 형태)
- 확장: 사용자 개입 포인트 추가 (파란 모자 역할 등)

### 비용 관리
- MVP: 품질 우선, 비용 제약 무시
- 확장: 토큰 최적화, 적응형 모델 호출

## 토큰 효율적 개발 가이드

- CLAUDE.md는 네비게이션 용도로만 사용
- 실제 상세 정보는 필요한 docs 파일만 선택적으로 참조
- 문서 간 중복 최소화, 실시간 동기화 유지

## 프로젝트 상태 확인

현재 모든 문서가 템플릿 상태이므로, 구현 시작 전에 다음 순서로 문서 완성 필요:
1. docs/1_goal_scope_definition.md 작성
2. docs/2_detailed_functional_specification.md 작성
3. 순차적으로 나머지 문서 완성
4. docs/6_master_execution_plan.md에서 구체적인 TASK 정의
5. 실제 구현 시작