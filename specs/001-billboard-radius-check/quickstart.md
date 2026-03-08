# Quickstart: 200m 대형광고물 반경 판정

## 1) 사전 준비

- PostgreSQL + PostGIS 실행
- 기본 원본 데이터 파일 존재 확인:
  - `/mnt/c/Users/user/sign_map/data/raw/billboards_rooftop_wall_2025-12-16.xlsx`
- 도커 실행 포트 확인:
  - Backend: `http://localhost:18100`
  - Frontend: `http://localhost:15173`

## 2) 기본 데이터 수동 적재

1. 운영자가 `/api/v1/import/billboards`에 파일 업로드
2. 시스템은 적재 작업(`job_id`)을 생성하고 `ImportJobLog`에 이력 저장
3. 적재 성공/실패 건수를 확인

## 3) 반경 판정 조회

1. `http://localhost:18100/api/v1/check-radius`에 주소 전송
2. 지오코딩 결과가 단일이면 즉시 판정
3. 지오코딩 결과가 복수면 후보 최대 5개 반환
4. 사용자가 후보를 선택해 재요청하면 최종 판정 반환

## 4) 수동 검증 시나리오

### 시나리오 A: 광고물 존재
- 입력: `서울 강남구 도산대로 306`
- 기대:
  - HTTP 200
  - `count >= 1`
  - 모든 `distance_m <= 200`

### 시나리오 B: 광고물 없음
- 입력: 데이터 외곽 주소
- 기대:
  - HTTP 200
  - `count = 0`
  - `items` 빈 배열

### 시나리오 C: 다중 지오코딩
- 입력: 모호한 주소
- 기대:
  - HTTP 422 또는 후보 포함 응답
  - 후보 최대 5개
  - 후보 선택 후 재요청 시 HTTP 200

### 시나리오 D: 오류 처리
- 입력: 빈 주소
- 기대:
  - HTTP 400
  - `code = VALIDATION_ERROR`

## 5) 성능 검증 기준

- 기준 부하에서 `/api/v1/check-radius` p95 <= 1초
- 측정 시 상태 `ACTIVE` 필터와 공간 인덱스(GIST) 적용 여부 확인

## 6) 문제 해결

- `포트 충돌`:
  - `docker compose ps`로 점유 포트 확인 후 `docker-compose.yml` published port 조정
- `지오코딩 후보 오류(422)`:
  - 응답의 `details.geocode_candidates`에서 후보 선택 후 `selected_candidate_id`로 재요청
- `업로드 실패`:
  - 확장자 `.xlsx` 여부와 헤더(2행 기준)를 점검
