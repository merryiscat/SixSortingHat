-- SixSortingHat 데이터베이스 초기화 스크립트

-- UTF-8 인코딩 설정
SET client_encoding = 'UTF8';

-- 한국어 검색을 위한 확장 모듈 활성화 (선택사항)
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 세션 관련 인덱스용 btree_gin 확장 (선택사항)
-- CREATE EXTENSION IF NOT EXISTS btree_gin;

-- 초기 설정 완료 확인
SELECT 'Database initialized successfully' as status;