# 데이터 모델: 200m 대형광고물 반경 판정

## 1. Billboard

설명: 반경 판정의 기준이 되는 대형광고물 마스터 데이터.

주요 필드:
- `id` (PK, bigint)
- `serial_no` (int, 원본 연번)
- `ad_type` (enum: `ROOFTOP_LED`, `WALL_LED`)
- `company_name` (varchar)
- `permit_date` (date)
- `size_text` (text)
- `display_address` (varchar)
- `legal_dong` (varchar)
- `status` (enum: `ACTIVE`, `INACTIVE`, `REMOVED`; 기본 판정 포함은 `ACTIVE`)
- `lat` (numeric)
- `lng` (numeric)
- `geom` (geography(Point,4326), GIST index)
- `created_at` (timestamp)
- `updated_at` (timestamp)

검증 규칙:
- `lat/lng`가 있으면 `geom` 필수 생성
- `status=ACTIVE`만 판정 대상
- 좌표 누락/비정상 행은 적재 실패 처리

## 2. RadiusCheckRequest

설명: 반경 판정 요청/입력 기록.

주요 필드:
- `id` (UUID, PK)
- `input_address` (varchar)
- `selected_geocode_address` (varchar, nullable)
- `input_lat` (numeric, nullable)
- `input_lng` (numeric, nullable)
- `radius_m` (int, default 200)
- `requested_at` (timestamp)
- `requester_id` (varchar, nullable)

상태 전이:
- `RECEIVED -> GEOCODED -> COMPLETED`
- 실패 시 `RECEIVED/GEOCODED -> FAILED`

## 3. RadiusCheckResult

설명: 요청에 대한 판정 결과 스냅샷.

주요 필드:
- `id` (UUID, PK)
- `request_id` (UUID, FK -> RadiusCheckRequest)
- `count` (int)
- `result_items` (jsonb: company/ad_type/address/distance_m)
- `evaluated_at` (timestamp)
- `result_status` (enum: `FOUND`, `NOT_FOUND`, `ERROR`)

검증 규칙:
- `count = result_items.length`
- `distance_m <= 200`만 포함

## 4. ImportJobLog

설명: 원본 업로드/적재 이력.

주요 필드:
- `id` (UUID, PK)
- `source_file_name` (varchar)
- `source_file_path` (varchar)
- `source_file_hash` (varchar, nullable)
- `rule_version` (varchar)
- `started_at` (timestamp)
- `finished_at` (timestamp)
- `success_count` (int)
- `failed_count` (int)
- `error_summary` (text, nullable)
- `created_by` (varchar)

검증 규칙:
- 적재 종료 시 `success_count + failed_count >= 1`
- 실패 행은 별도 에러 로그 테이블 또는 파일로 추적 가능해야 함

## 관계 요약
- `RadiusCheckRequest (1) -> (1) RadiusCheckResult`
- `ImportJobLog`는 `Billboard` 적재 배치와 논리적으로 연결(배치 ID로 추적)
