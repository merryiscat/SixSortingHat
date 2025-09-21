# **4. API 명세 (API Specification)**

**참조 문서**: [docs/0_architecture.md](docs/0_architecture.md), [docs/3_ui_design_system.md](docs/3_ui_design_system.md)

## **4.1 API 개요**

**Base URL**: `https://api.sixsortinghat.com/v1`
**프로토콜**: HTTP/HTTPS + Server-Sent Events (SSE)
**인증**: 세션 기반 (MVP에서는 무인증)
**데이터 형식**: JSON
**버전**: v1

### **4.1.1 공통 응답 구조**

#### **성공 응답**
```json
{
  "success": true,
  "data": {
    // 응답 데이터
  },
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_1234567890"
}
```

#### **오류 응답**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "사용자 입력이 유효하지 않습니다.",
    "details": "질문은 최소 3자 이상이어야 합니다."
  },
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_1234567890"
}
```

### **4.1.2 공통 오류 코드**

| 코드 | 설명 | HTTP 상태 |
|------|------|-----------|
| `INVALID_INPUT` | 입력 데이터 검증 실패 | 400 |
| `SESSION_NOT_FOUND` | 세션을 찾을 수 없음 | 404 |
| `INSUFFICIENT_COINS` | 코인 부족 | 403 |
| `DISCUSSION_IN_PROGRESS` | 토론이 진행 중 | 409 |
| `RATE_LIMITED` | 속도 제한 초과 | 429 |
| `LLM_SERVICE_ERROR` | LLM 서비스 오류 | 502 |
| `INTERNAL_ERROR` | 서버 내부 오류 | 500 |

## **4.2 핵심 API 엔드포인트**

### **4.2.1 세션 관리**

#### **POST /sessions**
새로운 채팅 세션을 생성합니다.

**요청 예시:**
```http
POST /v1/sessions
Content-Type: application/json

{
  "client_info": {
    "platform": "mobile",
    "version": "1.0.0",
    "user_agent": "SixSortingHat/1.0.0 (iOS; 15.0)"
  }
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "session_id": "sess_1234567890abcdef",
    "coins_remaining": 5,
    "coins_total": 5,
    "expires_at": "2024-03-15T18:30:00Z",
    "created_at": "2024-03-15T10:30:00Z"
  },
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_1234567890"
}
```

#### **GET /sessions/{session_id}**
세션 정보를 조회합니다.

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "session_id": "sess_1234567890abcdef",
    "coins_remaining": 3,
    "coins_total": 5,
    "status": "active",
    "discussions_count": 2,
    "last_activity": "2024-03-15T11:45:00Z",
    "created_at": "2024-03-15T10:30:00Z"
  }
}
```

### **4.2.2 토론 시작**

#### **POST /sessions/{session_id}/discussions**
새로운 6모자 토론을 시작합니다.

**요청 예시:**
```http
POST /v1/sessions/sess_1234567890abcdef/discussions
Content-Type: application/json

{
  "question": "새로운 사업 아이디어를 어떻게 검증할 수 있을까요?",
  "context": {
    "industry": "tech",
    "urgency": "medium"
  }
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "discussion_id": "disc_abcdef1234567890",
    "session_id": "sess_1234567890abcdef",
    "question": "새로운 사업 아이디어를 어떻게 검증할 수 있을까요?",
    "status": "intent_classification",
    "intent": null,
    "estimated_duration": "5-15분",
    "stream_url": "/v1/discussions/disc_abcdef1234567890/stream",
    "created_at": "2024-03-15T12:00:00Z"
  }
}
```

### **4.2.3 실시간 토론 스트림 (SSE)**

#### **GET /discussions/{discussion_id}/stream**
토론 진행 상황을 실시간으로 스트리밍합니다.

**요청 예시:**
```http
GET /v1/discussions/disc_abcdef1234567890/stream
Accept: text/event-stream
Cache-Control: no-cache
```

**SSE 이벤트 타입:**

1. **intent_classified** - 의도 분류 완료
```
event: intent_classified
data: {"intent": "complex", "will_proceed": true, "reasoning": "복합적 사고가 필요한 질문으로 판단됨"}
```

2. **hat_started** - 특정 모자 답변 시작
```
event: hat_started
data: {"hat": "white", "order": 1, "estimated_time": "30초"}
```

3. **hat_response** - 모자별 답변 완료
```
event: hat_response
data: {
  "hat": "white",
  "order": 1,
  "response": "사업 아이디어 검증을 위해서는 먼저 객관적인 시장 데이터를 수집해야 합니다...",
  "confidence": 0.95,
  "duration": "25초",
  "tools_used": ["web_search"],
  "completed_at": "2024-03-15T12:01:25Z"
}
```

4. **quality_check** - 파란 모자 품질 검증
```
event: quality_check
data: {
  "hat": "blue",
  "status": "checking",
  "criteria": ["completeness", "coherence", "relevance"],
  "current_round": 1
}
```

5. **quality_result** - 품질 검증 결과
```
event: quality_result
data: {
  "status": "approved",
  "score": 0.87,
  "feedback": "모든 관점에서 균형잡힌 분석이 완료되었습니다.",
  "needs_retry": false
}
```

6. **discussion_completed** - 토론 완료
```
event: discussion_completed
data: {
  "discussion_id": "disc_abcdef1234567890",
  "status": "completed",
  "total_duration": "8분 32초",
  "rounds_completed": 1,
  "final_summary": "사업 아이디어 검증을 위한 종합적인 접근 방안...",
  "completed_at": "2024-03-15T12:08:32Z"
}
```

7. **error** - 오류 발생
```
event: error
data: {
  "error_code": "LLM_SERVICE_ERROR",
  "message": "LLM 서비스에 일시적 문제가 발생했습니다.",
  "retry_after": 30,
  "recoverable": true
}
```

### **4.2.4 토론 조회**

#### **GET /discussions/{discussion_id}**
완료된 토론의 전체 내용을 조회합니다.

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "discussion_id": "disc_abcdef1234567890",
    "session_id": "sess_1234567890abcdef",
    "question": "새로운 사업 아이디어를 어떻게 검증할 수 있을까요?",
    "status": "completed",
    "intent": "complex",
    "rounds": [
      {
        "round_number": 1,
        "hat_responses": [
          {
            "hat": "white",
            "order": 1,
            "response": "사업 아이디어 검증을 위해서는...",
            "duration": "25초",
            "confidence": 0.95,
            "tools_used": ["web_search"]
          },
          // ... 다른 모자들의 응답
        ],
        "quality_check": {
          "score": 0.87,
          "approved": true,
          "feedback": "균형잡힌 분석 완료"
        }
      }
    ],
    "final_summary": "종합적인 검증 방안...",
    "total_duration": "8분 32초",
    "created_at": "2024-03-15T12:00:00Z",
    "completed_at": "2024-03-15T12:08:32Z"
  }
}
```

## **4.3 보조 API 엔드포인트**

### **4.3.1 세션 코인 관리**

#### **GET /sessions/{session_id}/coins**
세션의 코인 정보를 조회합니다.

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "coins_remaining": 3,
    "coins_total": 5,
    "coins_used": 2,
    "last_used_at": "2024-03-15T11:45:00Z",
    "reset_available": false,
    "reset_available_at": null
  }
}
```

### **4.3.2 토론 기록 조회**

#### **GET /sessions/{session_id}/discussions**
세션의 모든 토론 기록을 조회합니다.

**요청 파라미터:**
- `limit`: 조회할 토론 수 (기본값: 10, 최대: 50)
- `offset`: 건너뛸 토론 수 (기본값: 0)
- `status`: 토론 상태 필터 (`completed`, `in_progress`, `failed`)

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "discussions": [
      {
        "discussion_id": "disc_abcdef1234567890",
        "question": "새로운 사업 아이디어를 어떻게 검증할 수 있을까요?",
        "status": "completed",
        "duration": "8분 32초",
        "created_at": "2024-03-15T12:00:00Z",
        "summary": "시장 검증, 고객 검증, 기술 검증의 3단계 접근법..."
      }
    ],
    "pagination": {
      "total": 5,
      "limit": 10,
      "offset": 0,
      "has_more": false
    }
  }
}
```

### **4.3.3 헬스 체크**

#### **GET /health**
API 서버의 상태를 확인합니다.

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": "72h 15m 30s",
    "services": {
      "database": "healthy",
      "redis": "healthy",
      "llm_service": "healthy"
    },
    "timestamp": "2024-03-15T15:30:00Z"
  }
}
```

### **4.3.4 시스템 통계**

#### **GET /stats**
시스템 전체 통계 정보를 조회합니다.

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "total_sessions": 1234,
    "total_discussions": 5678,
    "avg_discussion_duration": "7분 23초",
    "success_rate": 0.95,
    "active_sessions": 45,
    "most_common_topics": [
      "비즈니스 전략",
      "창업 아이디어",
      "의사결정",
      "문제 해결"
    ]
  }
}
```

## **4.4 오류 처리 및 상태 코드**

### **4.4.1 HTTP 상태 코드**
- `200 OK`: 성공적인 조회
- `201 Created`: 리소스 생성 성공
- `202 Accepted`: 비동기 처리 시작
- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 실패 (향후 구현)
- `403 Forbidden`: 코인 부족 등 권한 문제
- `404 Not Found`: 리소스를 찾을 수 없음
- `409 Conflict`: 리소스 상태 충돌
- `429 Too Many Requests`: 속도 제한 초과
- `500 Internal Server Error`: 서버 내부 오류
- `502 Bad Gateway`: LLM 서비스 오류
- `503 Service Unavailable`: 서비스 일시적 불가

### **4.4.2 재시도 정책**

#### **자동 재시도 대상**
- `429 Too Many Requests`: 1초 후 재시도
- `502 Bad Gateway`: 5초 후 재시도
- `503 Service Unavailable`: 10초 후 재시도

#### **재시도 제한**
- 최대 재시도 횟수: 3회
- 지수 백오프 적용: 1초, 2초, 4초
- 총 재시도 시간 제한: 30초

#### **재시도 불가 오류**
- `400 Bad Request`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict`

## **4.5 속도 제한 (Rate Limiting)**

### **4.5.1 제한 정책**

| 엔드포인트 | 제한 | 시간 창 |
|-----------|------|---------|
| `POST /sessions` | 10회 | 1시간 |
| `POST /discussions` | 100회 | 1시간 |
| `GET /discussions/{id}/stream` | 50회 | 10분 |
| `GET /*` | 1000회 | 1시간 |

### **4.5.2 제한 초과 응답**

**응답 헤더:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1647345600
Retry-After: 3600
```

**응답 본문:**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "속도 제한을 초과했습니다.",
    "details": "1시간 후에 다시 시도해주세요."
  },
  "retry_after": 3600
}
```

## **4.6 개발자 가이드**

### **4.6.1 SDK 및 라이브러리**

#### **JavaScript/TypeScript SDK**
```typescript
import { SixSortingHatClient } from '@sixsortinghat/sdk';

const client = new SixSortingHatClient({
  baseURL: 'https://api.sixsortinghat.com/v1',
  timeout: 30000
});

// 세션 생성
const session = await client.createSession({
  platform: 'mobile',
  version: '1.0.0'
});

// 토론 시작
const discussion = await client.startDiscussion(session.id, {
  question: '새로운 사업 아이디어를 어떻게 검증할까요?'
});

// 실시간 스트림 구독
client.subscribeToDiscussion(discussion.id, {
  onHatResponse: (data) => console.log('Hat response:', data),
  onCompleted: (data) => console.log('Discussion completed:', data),
  onError: (error) => console.error('Error:', error)
});
```

### **4.6.2 에러 처리 예시**

```typescript
try {
  const discussion = await client.startDiscussion(sessionId, { question });
} catch (error) {
  switch (error.code) {
    case 'INSUFFICIENT_COINS':
      // 새 세션 생성 안내
      showNewSessionDialog();
      break;
    case 'DISCUSSION_IN_PROGRESS':
      // 진행 중인 토론 있음
      redirectToActiveDiscussion();
      break;
    case 'LLM_SERVICE_ERROR':
      // 서비스 오류 - 재시도 옵션 제공
      showRetryDialog();
      break;
    default:
      // 일반적인 오류 처리
      showErrorMessage(error.message);
  }
}
```

### **4.6.3 SSE 연결 관리**

```typescript
class DiscussionStream {
  private eventSource: EventSource;

  connect(discussionId: string) {
    this.eventSource = new EventSource(
      `/v1/discussions/${discussionId}/stream`
    );

    this.eventSource.addEventListener('hat_response', (event) => {
      const data = JSON.parse(event.data);
      this.onHatResponse(data);
    });

    this.eventSource.addEventListener('error', (event) => {
      console.error('SSE Error:', event);
      // 자동 재연결 로직
      setTimeout(() => this.connect(discussionId), 5000);
    });
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
    }
  }
}
```

### **4.6.4 성능 최적화 가이드**

#### **요청 최적화**
- 불필요한 요청 최소화
- 적절한 캐싱 헤더 활용
- 압축 지원 (`Accept-Encoding: gzip`)

#### **SSE 최적화**
- 연결 풀링으로 동시 연결 수 제한
- 적절한 하트비트 구현
- 연결 끊김 시 자동 재연결

#### **에러 복구**
- Circuit Breaker 패턴 적용
- 적절한 타임아웃 설정
- 우아한 성능 저하 (Graceful Degradation)