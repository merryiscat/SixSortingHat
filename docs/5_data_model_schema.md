# **5. 데이터 모델 스키마 (Data Model Schema)**

**참조 문서**: [docs/0_architecture.md](docs/0_architecture.md), [docs/4_api_specification.md](docs/4_api_specification.md)

## **5.1 데이터 아키텍처 개요**

**데이터베이스**: PostgreSQL 15+
**ORM**: SQLAlchemy 2.0 (Python)
**마이그레이션**: Alembic
**캐시**: Redis 7.0+
**검색**: PostgreSQL Full-text Search
**백업**: pg_dump + AWS S3 (또는 로컬 스토리지)

### **데이터 플로우**
```
클라이언트 요청 → Redis 세션 확인 → PostgreSQL 데이터 조회/저장 → LangGraph 체크포인터 저장 → Redis 캐시 업데이트
```

### **데이터 분산 전략**
- **PostgreSQL**: 영구 데이터 (세션, 토론 기록, 체크포인터)
- **Redis**: 임시 데이터 (세션 캐시, 코인 상태, 진행 중인 토론)
- **메모리**: LangGraph 실행 중 상태

## **5.2 핵심 테이블 스키마**

### **5.2.1 Sessions 테이블**
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(32) UNIQUE NOT NULL,  -- 'sess_' prefix + 24자 랜덤
    coins_total INTEGER NOT NULL DEFAULT 5,
    coins_remaining INTEGER NOT NULL DEFAULT 5,
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, expired, terminated
    client_info JSONB,  -- platform, version, user_agent 등
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() + INTERVAL '8 hours'),

    CONSTRAINT sessions_coins_remaining_check CHECK (coins_remaining >= 0),
    CONSTRAINT sessions_coins_total_check CHECK (coins_total >= 0),
    CONSTRAINT sessions_status_check CHECK (status IN ('active', 'expired', 'terminated'))
);

-- 인덱스
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX idx_sessions_status ON sessions(status);
```

### **5.2.2 Discussions 테이블**
```sql
CREATE TABLE discussions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discussion_id VARCHAR(32) UNIQUE NOT NULL,  -- 'disc_' prefix + 24자 랜덤
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    context JSONB,  -- industry, urgency 등 추가 컨텍스트
    intent VARCHAR(20),  -- simple, complex
    status VARCHAR(20) NOT NULL DEFAULT 'intent_classification',
    -- 상태: intent_classification, in_progress, completed, failed, timeout
    rounds_completed INTEGER NOT NULL DEFAULT 0,
    total_duration INTERVAL,  -- 토론 소요 시간
    final_summary TEXT,
    metadata JSONB,  -- 통계, 성능 지표 등
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT discussions_status_check CHECK (
        status IN ('intent_classification', 'in_progress', 'completed', 'failed', 'timeout')
    ),
    CONSTRAINT discussions_rounds_check CHECK (rounds_completed >= 0)
);

-- 인덱스
CREATE INDEX idx_discussions_discussion_id ON discussions(discussion_id);
CREATE INDEX idx_discussions_session_id ON discussions(session_id);
CREATE INDEX idx_discussions_status ON discussions(status);
CREATE INDEX idx_discussions_created_at ON discussions(created_at);
CREATE INDEX idx_discussions_question_fulltext ON discussions USING gin(to_tsvector('korean', question));
```

### **5.2.3 Discussion_Rounds 테이블**
```sql
CREATE TABLE discussion_rounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discussion_id UUID NOT NULL REFERENCES discussions(id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL,
    hat_order JSONB NOT NULL,  -- 이번 라운드의 모자 순서 ['white', 'red', ...]
    quality_score DECIMAL(3,2),  -- 0.00 ~ 1.00
    quality_feedback TEXT,
    is_approved BOOLEAN,
    retry_reason TEXT,  -- 재시도가 필요한 이유
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT discussion_rounds_round_number_check CHECK (round_number > 0),
    CONSTRAINT discussion_rounds_quality_score_check CHECK (quality_score BETWEEN 0 AND 1),
    UNIQUE(discussion_id, round_number)
);

-- 인덱스
CREATE INDEX idx_discussion_rounds_discussion_id ON discussion_rounds(discussion_id);
CREATE INDEX idx_discussion_rounds_round_number ON discussion_rounds(discussion_id, round_number);
```

### **5.2.4 Hat_Responses 테이블**
```sql
CREATE TABLE hat_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID NOT NULL REFERENCES discussion_rounds(id) ON DELETE CASCADE,
    hat_type VARCHAR(10) NOT NULL,  -- white, red, black, yellow, green, blue
    hat_order INTEGER NOT NULL,  -- 이번 라운드에서의 순서 (1~6)
    response TEXT NOT NULL,
    confidence DECIMAL(3,2),  -- LLM 응답 신뢰도 0.00 ~ 1.00
    duration INTERVAL,  -- 응답 생성 시간
    token_usage JSONB,  -- input_tokens, output_tokens, total_tokens
    tools_used JSONB,  -- 사용된 도구 목록
    error_info JSONB,  -- 오류 발생 시 정보
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT hat_responses_hat_type_check CHECK (
        hat_type IN ('white', 'red', 'black', 'yellow', 'green', 'blue')
    ),
    CONSTRAINT hat_responses_hat_order_check CHECK (hat_order BETWEEN 1 AND 6),
    CONSTRAINT hat_responses_confidence_check CHECK (confidence BETWEEN 0 AND 1),
    UNIQUE(round_id, hat_type),
    UNIQUE(round_id, hat_order)
);

-- 인덱스
CREATE INDEX idx_hat_responses_round_id ON hat_responses(round_id);
CREATE INDEX idx_hat_responses_hat_type ON hat_responses(hat_type);
CREATE INDEX idx_hat_responses_hat_order ON hat_responses(round_id, hat_order);
CREATE INDEX idx_hat_responses_response_fulltext ON hat_responses USING gin(to_tsvector('korean', response));
```

### **5.2.5 LangGraph_Checkpoints 테이블 (LangGraph 체크포인터)**
```sql
CREATE TABLE langgraph_checkpoints (
    thread_id VARCHAR(255) NOT NULL,  -- discussion_id와 동일
    checkpoint_ns VARCHAR(255) NOT NULL DEFAULT '',
    checkpoint_id VARCHAR(255) NOT NULL,
    parent_checkpoint_id VARCHAR(255),
    type VARCHAR(50),
    checkpoint JSONB NOT NULL,  -- 전체 그래프 상태
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

-- 인덱스
CREATE INDEX idx_langgraph_checkpoints_thread_id ON langgraph_checkpoints(thread_id);
CREATE INDEX idx_langgraph_checkpoints_created_at ON langgraph_checkpoints(created_at);
```

### **5.2.6 System_Stats 테이블 (시스템 통계)**
```sql
CREATE TABLE system_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    UNIQUE(date, metric_name)
);

-- 인덱스
CREATE INDEX idx_system_stats_date ON system_stats(date);
CREATE INDEX idx_system_stats_metric_name ON system_stats(metric_name);
CREATE INDEX idx_system_stats_date_metric ON system_stats(date, metric_name);
```

## **5.3 Redis 세션 데이터 스키마**

### **5.3.1 세션 캐시**
```
키: session:{session_id}
TTL: 8시간
데이터 구조: Hash

HSET session:sess_1234567890abcdef
  id "sess_1234567890abcdef"
  coins_remaining "3"
  coins_total "5"
  status "active"
  last_activity "2024-03-15T12:30:00Z"
  expires_at "2024-03-15T18:30:00Z"
```

### **5.3.2 진행 중인 토론**
```
키: discussion:active:{discussion_id}
TTL: 1시간
데이터 구조: Hash

HSET discussion:active:disc_abcdef1234567890
  status "in_progress"
  current_hat "red"
  current_round "1"
  started_at "2024-03-15T12:00:00Z"
  session_id "sess_1234567890abcdef"
```

### **5.3.3 토론 진행 상태**
```
키: discussion:progress:{discussion_id}
TTL: 1시간
데이터 구조: List (순서 보장)

LPUSH discussion:progress:disc_abcdef1234567890
  '{"event":"hat_started","hat":"white","timestamp":"2024-03-15T12:00:30Z"}'
  '{"event":"hat_completed","hat":"white","timestamp":"2024-03-15T12:01:25Z"}'
  '{"event":"hat_started","hat":"red","timestamp":"2024-03-15T12:01:30Z"}'
```

### **5.3.4 속도 제한 (Rate Limiting)**
```
키: rate_limit:{endpoint}:{client_identifier}
TTL: 동적 (제한 정책에 따라)
데이터 구조: String (카운터)

SETEX rate_limit:post_discussions:sess_1234567890abcdef 3600 5
```

### **5.3.5 실시간 통계**
```
키: stats:realtime
TTL: 10분
데이터 구조: Hash

HSET stats:realtime
  active_sessions "45"
  discussions_in_progress "12"
  avg_response_time "2.3"
  last_updated "2024-03-15T12:30:00Z"
```

## **5.4 데이터 검증 및 제약조건**

### **5.4.1 입력 데이터 검증**

#### **Python Pydantic 모델**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class HatType(str, Enum):
    WHITE = "white"
    RED = "red"
    BLACK = "black"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"

class DiscussionStatus(str, Enum):
    INTENT_CLASSIFICATION = "intent_classification"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class CreateSessionRequest(BaseModel):
    client_info: Optional[Dict[str, Any]] = None

    @validator('client_info')
    def validate_client_info(cls, v):
        if v and not isinstance(v, dict):
            raise ValueError('client_info must be a dictionary')
        return v

class CreateDiscussionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    context: Optional[Dict[str, str]] = None

    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or whitespace only')
        return v.strip()

    @validator('context')
    def validate_context(cls, v):
        if v:
            allowed_keys = {'industry', 'urgency', 'domain'}
            if not set(v.keys()).issubset(allowed_keys):
                raise ValueError(f'Context keys must be from: {allowed_keys}')
        return v

class HatResponseCreate(BaseModel):
    round_id: str
    hat_type: HatType
    hat_order: int = Field(..., ge=1, le=6)
    response: str = Field(..., min_length=1, max_length=10000)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    token_usage: Optional[Dict[str, int]] = None
    tools_used: Optional[list] = None
```

### **5.4.2 데이터 무결성 제약조건**

#### **비즈니스 규칙 검증**
```sql
-- 세션의 코인은 절대 총 코인 수를 초과할 수 없음
ALTER TABLE sessions ADD CONSTRAINT sessions_coins_remaining_le_total
CHECK (coins_remaining <= coins_total);

-- 토론은 세션이 만료되기 전에 생성되어야 함
CREATE OR REPLACE FUNCTION check_discussion_before_session_expiry()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM sessions
        WHERE id = NEW.session_id
        AND expires_at < NOW()
    ) THEN
        RAISE EXCEPTION 'Cannot create discussion after session expiry';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_discussion_before_session_expiry
    BEFORE INSERT ON discussions
    FOR EACH ROW
    EXECUTE FUNCTION check_discussion_before_session_expiry();

-- 모자 응답은 해당 라운드에서 중복될 수 없음
-- (이미 UNIQUE 제약조건으로 처리됨)

-- 토론 완료 시간은 시작 시간보다 뒤여야 함
ALTER TABLE discussions ADD CONSTRAINT discussions_completed_after_started
CHECK (completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at);
```

### **5.4.3 애플리케이션 레벨 검증**

#### **세션 유효성 검사**
```python
async def validate_session(session_id: str) -> Session:
    session = await get_session(session_id)
    if not session:
        raise SessionNotFoundError(f"Session {session_id} not found")

    if session.status != 'active':
        raise SessionInvalidError(f"Session {session_id} is not active")

    if session.expires_at < datetime.utcnow():
        await expire_session(session_id)
        raise SessionExpiredError(f"Session {session_id} has expired")

    return session

async def validate_session_coins(session_id: str) -> bool:
    session = await validate_session(session_id)
    if session.coins_remaining <= 0:
        raise InsufficientCoinsError(f"No coins remaining in session {session_id}")
    return True
```

## **5.5 데이터 마이그레이션 스크립트**

### **5.5.1 초기 스키마 생성 (Alembic)**
```python
# migrations/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    # Sessions 테이블 생성
    op.create_table(
        'sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', sa.String(32), nullable=False, unique=True),
        sa.Column('coins_total', sa.Integer, nullable=False, server_default='5'),
        sa.Column('coins_remaining', sa.Integer, nullable=False, server_default='5'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('client_info', JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('last_activity', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False,
                 server_default=sa.text("NOW() + INTERVAL '8 hours'")),
        sa.CheckConstraint('coins_remaining >= 0', name='sessions_coins_remaining_check'),
        sa.CheckConstraint('coins_total >= 0', name='sessions_coins_total_check'),
        sa.CheckConstraint("status IN ('active', 'expired', 'terminated')", name='sessions_status_check')
    )

    # 인덱스 생성
    op.create_index('idx_sessions_session_id', 'sessions', ['session_id'])
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])
    # ... 기타 테이블 및 인덱스

def downgrade():
    op.drop_table('sessions')
    # ... 기타 테이블 삭제
```

### **5.5.2 데이터 마이그레이션 예시**
```python
# migrations/versions/002_add_discussion_metadata.py
def upgrade():
    # metadata 컬럼 추가
    op.add_column('discussions', sa.Column('metadata', JSONB))

    # 기존 데이터에 기본값 설정
    op.execute("UPDATE discussions SET metadata = '{}' WHERE metadata IS NULL")

def downgrade():
    op.drop_column('discussions', 'metadata')
```

## **5.6 성능 최적화**

### **5.6.1 인덱스 최적화**

#### **복합 인덱스**
```sql
-- 세션별 토론 조회 최적화
CREATE INDEX idx_discussions_session_status_created
ON discussions(session_id, status, created_at DESC);

-- 토론 검색 최적화
CREATE INDEX idx_discussions_fulltext_status
ON discussions USING gin(to_tsvector('korean', question))
WHERE status = 'completed';

-- 모자별 응답 성능 분석
CREATE INDEX idx_hat_responses_hat_type_duration
ON hat_responses(hat_type, duration)
WHERE duration IS NOT NULL;
```

#### **부분 인덱스**
```sql
-- 활성 세션만 인덱싱
CREATE INDEX idx_sessions_active
ON sessions(last_activity)
WHERE status = 'active';

-- 진행 중인 토론만 인덱싱
CREATE INDEX idx_discussions_in_progress
ON discussions(created_at)
WHERE status = 'in_progress';
```

### **5.6.2 쿼리 최적화**

#### **효율적인 세션 조회**
```sql
-- 세션 정보와 함께 최근 토론 수 조회
SELECT
    s.*,
    COUNT(d.id) as discussions_count,
    MAX(d.created_at) as last_discussion_at
FROM sessions s
LEFT JOIN discussions d ON s.id = d.session_id
WHERE s.session_id = $1
GROUP BY s.id;
```

#### **토론 목록 페이징**
```sql
-- 효율적인 커서 기반 페이징
SELECT *
FROM discussions
WHERE session_id = $1
  AND created_at < $2  -- 커서
ORDER BY created_at DESC
LIMIT $3;
```

### **5.6.3 Redis 최적화**

#### **메모리 최적화**
```python
# Redis 설정 최적화
redis_config = {
    'maxmemory': '512mb',
    'maxmemory-policy': 'allkeys-lru',
    'save': '900 1 300 10 60 10000',  # 백그라운드 저장
    'rdbcompression': 'yes',
    'timeout': 300
}

# 연결 풀 최적화
redis_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50,
    retry_on_timeout=True,
    socket_keepalive=True,
    socket_keepalive_options={}
)
```

#### **배치 작업 최적화**
```python
# Redis 파이프라인 사용
async def update_session_activity(session_id: str):
    pipe = redis_client.pipeline()
    pipe.hset(f"session:{session_id}", "last_activity", datetime.utcnow().isoformat())
    pipe.expire(f"session:{session_id}", 28800)  # 8시간
    await pipe.execute()
```

## **5.7 백업 및 복구 전략**

### **5.7.1 PostgreSQL 백업**

#### **정기 백업 스크립트**
```bash
#!/bin/bash
# backup_postgres.sh

DB_NAME="sixsortinghat"
BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# 전체 데이터베이스 백업
pg_dump -h localhost -U postgres -d $DB_NAME \
  --format=custom \
  --compress=9 \
  --file="$BACKUP_DIR/${DB_NAME}_${DATE}.dump"

# 스키마만 백업
pg_dump -h localhost -U postgres -d $DB_NAME \
  --schema-only \
  --file="$BACKUP_DIR/${DB_NAME}_schema_${DATE}.sql"

# 7일 이상 된 백업 파일 삭제
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: ${DB_NAME}_${DATE}.dump"
```

#### **복구 스크립트**
```bash
#!/bin/bash
# restore_postgres.sh

BACKUP_FILE=$1
DB_NAME="sixsortinghat"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 데이터베이스 복구
pg_restore -h localhost -U postgres -d $DB_NAME \
  --clean \
  --if-exists \
  --verbose \
  $BACKUP_FILE

echo "Restore completed from: $BACKUP_FILE"
```

### **5.7.2 Redis 백업**

#### **RDB 스냅샷 백업**
```bash
#!/bin/bash
# backup_redis.sh

REDIS_CLI="redis-cli"
BACKUP_DIR="/backup/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# 백그라운드 저장 트리거
$REDIS_CLI BGSAVE

# 저장 완료 대기
while [ $($REDIS_CLI LASTSAVE) -eq $($REDIS_CLI LASTSAVE) ]; do
    sleep 1
done

# RDB 파일 복사
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/dump_${DATE}.rdb"

echo "Redis backup completed: dump_${DATE}.rdb"
```

### **5.7.3 재해 복구 계획**

#### **복구 우선순위**
1. **PostgreSQL 복구**: 핵심 데이터 복구
2. **Redis 복구**: 세션 및 캐시 데이터 복구
3. **애플리케이션 재시작**: 서비스 정상화

#### **자동 복구 스크립트**
```python
# disaster_recovery.py
import subprocess
import logging
from datetime import datetime

class DisasterRecovery:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def check_database_health(self):
        """데이터베이스 상태 확인"""
        try:
            # PostgreSQL 연결 테스트
            result = subprocess.run(['pg_isready', '-h', 'localhost'],
                                   capture_output=True, text=True)
            if result.returncode != 0:
                return False

            # Redis 연결 테스트
            result = subprocess.run(['redis-cli', 'ping'],
                                   capture_output=True, text=True)
            if 'PONG' not in result.stdout:
                return False

            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    async def restore_from_backup(self, backup_type='latest'):
        """백업에서 복구"""
        try:
            if backup_type == 'latest':
                # 최신 백업 파일 찾기
                backup_file = self.find_latest_backup()

            # 복구 실행
            await self.restore_postgres(backup_file)
            await self.restore_redis()

            self.logger.info(f"Disaster recovery completed at {datetime.utcnow()}")
            return True

        except Exception as e:
            self.logger.error(f"Disaster recovery failed: {e}")
            return False
```

### **5.7.4 데이터 아카이빙**

#### **오래된 데이터 아카이빙**
```sql
-- 30일 이상 된 완료된 토론 아카이빙
CREATE TABLE discussions_archive (LIKE discussions INCLUDING ALL);

-- 아카이빙 프로시저
CREATE OR REPLACE FUNCTION archive_old_discussions()
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- 아카이브 테이블로 이동
    WITH archived AS (
        DELETE FROM discussions
        WHERE status = 'completed'
          AND completed_at < NOW() - INTERVAL '30 days'
        RETURNING *
    )
    INSERT INTO discussions_archive
    SELECT * FROM archived;

    GET DIAGNOSTICS archived_count = ROW_COUNT;

    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- 월별 아카이빙 작업 스케줄
SELECT cron.schedule('archive-discussions', '0 2 1 * *', 'SELECT archive_old_discussions();');
```

### **5.7.5 모니터링 및 알림**

#### **데이터베이스 상태 모니터링**
```python
# monitoring.py
async def monitor_database_metrics():
    """데이터베이스 메트릭 수집"""
    metrics = {
        'postgres': {
            'connections': await get_postgres_connection_count(),
            'size': await get_database_size(),
            'slow_queries': await get_slow_query_count(),
        },
        'redis': {
            'memory_usage': await get_redis_memory_usage(),
            'hit_rate': await get_redis_hit_rate(),
            'connected_clients': await get_redis_client_count(),
        }
    }

    # 임계값 확인 및 알림
    await check_thresholds_and_alert(metrics)

    return metrics
```
