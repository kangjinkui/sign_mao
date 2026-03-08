---

description: "기능 구현을 위한 작업 목록"
---

# 작업 목록: 200m 대형광고물 반경 판정

**입력**: `/specs/001-billboard-radius-check/`의 설계 문서
**선행 조건**: plan.md(필수), spec.md(필수), research.md, data-model.md, contracts/

**테스트**: 본 기능은 지오코딩/공간쿼리/판정규칙/API 계약/데이터 정규화를 포함하므로 테스트 필수
(최소: 단위 1개 + 통합 1개 이상).

**구성 원칙**: 작업은 사용자 스토리별로 묶어 각 스토리를 독립 구현/검증 가능하게 한다.

## 형식: `[ID] [P?] [Story] 설명`

- **[P]**: 병렬 수행 가능
- **[Story]**: 사용자 스토리 라벨(US1, US2, US3)
- 설명에는 정확한 파일 경로를 포함

## 경로 규칙

- 백엔드: `backend/app/`, `backend/tests/`
- 프론트엔드: `frontend/src/`, `frontend/tests/`

## 1단계: 준비 (공통 인프라)

- [X] T001 프로젝트 기본 디렉터리 생성 및 초기 파일 배치 (`backend/app`, `backend/tests`, `frontend/src`, `frontend/tests`)
- [X] T002 [P] 백엔드 의존성 정의 및 설치 스크립트 구성 (`backend/pyproject.toml` 또는 `backend/requirements.txt`)
- [X] T003 [P] 프론트엔드 의존성 정의 및 설치 스크립트 구성 (`frontend/package.json`)
- [X] T004 [P] 개발 환경 변수 샘플 파일 작성 (`backend/.env.example`, `frontend/.env.example`)
- [X] T005 [P] 로컬 실행 오케스트레이션 작성 (`docker-compose.yml` 또는 `Makefile`)

---

## 2단계: 기반 작업 (모든 스토리 차단)

- [X] T006 PostGIS 확장 포함 DB 초기화 및 마이그레이션 설정 (`backend/app/db/migrations/`)
- [X] T007 [P] 공통 오류 응답 스키마 구현 (`backend/app/schemas/error.py`)
- [X] T008 [P] 공통 API 라우팅/버전 프레임 구성 (`backend/app/api/v1/__init__.py`, `backend/app/main.py`)
- [X] T009 [P] 지오코딩 클라이언트 인터페이스와 어댑터 구성 (`backend/app/services/geocoding_client.py`)
- [X] T010 Billboard/ImportJobLog 기본 모델 구현 (`backend/app/models/billboard.py`, `backend/app/models/import_job_log.py`)
- [X] T011 [P] 공간 인덱스 및 상태 필터 쿼리 유틸 구현 (`backend/app/services/spatial_query.py`)
- [X] T012 [P] 데이터 계보 메타데이터 규약 구현 (`backend/app/services/import_lineage.py`)
- [X] T013 [P] 계약 테스트 기반 구성 (`backend/tests/contract/conftest.py`)
- [X] T014 [P] 통합 테스트 DB 픽스처 구성 (`backend/tests/integration/conftest.py`)

**체크포인트**: 기반 완료 후 사용자 스토리 작업 시작

---

## 3단계: 사용자 스토리 1 - 주소 기반 200m 판정 조회 (P1) 🎯

**목표**: 주소 입력으로 200m 반경 판정 결과(개수/목록/거리)를 API로 제공
**독립 테스트**: 유효 주소/무결과 주소/다중 후보 주소 3개 시나리오 통과

### 테스트 (필수)

- [X] T015 [P] [US1] 계약 테스트 작성: `POST /api/v1/check-radius` 성공/오류 스키마 (`backend/tests/contract/test_check_radius_contract.py`)
- [X] T016 [P] [US1] 단위 테스트 작성: 거리 포함 기준(`<=200m`), 상태 `ACTIVE` 필터 (`backend/tests/unit/test_spatial_query.py`)
- [X] T017 [P] [US1] 통합 테스트 작성: 단일 지오코딩, 무결과, 다중 후보 반환 (`backend/tests/integration/test_check_radius_flow.py`)
- [X] T045 [P] [US1] 단위 테스트 작성: 법정동/광고물종류 필터 조합 쿼리 (`backend/tests/unit/test_radius_filters.py`)
- [X] T046 [P] [US1] 통합 테스트 작성: 필터 파라미터 적용 시 결과 집합 검증 (`backend/tests/integration/test_check_radius_filters.py`)

### 구현

- [X] T018 [P] [US1] 반경 판정 요청/응답 스키마 구현 (`backend/app/schemas/check_radius.py`)
- [X] T019 [US1] 반경 판정 서비스 구현 (`backend/app/services/radius_check_service.py`)
- [X] T020 [US1] 지오코딩 다중 후보(최대 5개) 처리 로직 구현 (`backend/app/services/geocoding_resolution.py`)
- [X] T021 [US1] `POST /api/v1/check-radius` 엔드포인트 구현 (`backend/app/api/v1/check_radius.py`)
- [X] T022 [US1] 오류 코드 매핑 구현 (`VALIDATION_ERROR`, `GEOCODING_ERROR`, `INTERNAL_ERROR`) (`backend/app/api/error_handlers.py`)
- [X] T023 [US1] 요청/판정 이력 로깅 구현 (`backend/app/services/audit_log_service.py`)
- [X] T047 [US1] 법정동/광고물종류 필터 파라미터 처리 및 쿼리 연동 구현 (`backend/app/api/v1/check_radius.py`, `backend/app/services/radius_check_service.py`, `backend/app/services/spatial_query.py`)

**체크포인트**: US1 단독 배포/검증 가능

---

## 4단계: 사용자 스토리 2 - 지도 시각화 확인 (P2)

**목표**: 지도에서 검색 위치/200m 원/광고물 마커와 목록을 동기화해 표시
**독립 테스트**: 검색 결과 수와 지도 마커 수가 일치, 후보 선택 후 재조회 가능

### 테스트 (필수)

- [X] T024 [P] [US2] 프론트 서비스 단위 테스트: 결과 매핑/후보 선택 상태 (`frontend/tests/unit/radiusResultMapper.test.ts`)
- [X] T025 [P] [US2] UI 통합 테스트: 지도 요소 3종 렌더링/목록 동기화 (`frontend/tests/integration/radius-map-flow.test.tsx`)
- [X] T026 [P] [US2] E2E 테스트: 주소 검색 -> 후보 선택 -> 지도 반영 (`frontend/tests/e2e/check-radius-map.spec.ts`)

### 구현

- [X] T027 [P] [US2] API 호출 클라이언트 구현 (`frontend/src/services/checkRadiusApi.ts`)
- [X] T028 [P] [US2] 검색 폼/후보 선택 컴포넌트 구현 (`frontend/src/components/AddressSearchForm.tsx`)
- [X] T029 [US2] 지도 레이어(검색마커/200m원/광고물마커) 구현 (`frontend/src/components/BillboardMap.tsx`)
- [X] T030 [US2] 결과 목록 컴포넌트 구현 (`frontend/src/components/RadiusResultList.tsx`)
- [X] T031 [US2] 페이지 조립 및 상태관리 구현 (`frontend/src/pages/RadiusCheckPage.tsx`)

**체크포인트**: US2 독립 검증 가능, US1 API와 연동 완료

---

## 5단계: 사용자 스토리 3 - 기본 데이터 적재 및 이력 추적 (P3)

**목표**: 원본 엑셀 수동 업로드 적재와 이력 추적 제공
**독립 테스트**: 주어진 원본 파일 적재 시 성공/실패 건수 및 이력 저장 확인

### 테스트 (필수)

- [X] T032 [P] [US3] 계약 테스트 작성: `POST /api/v1/import/billboards` (`backend/tests/contract/test_import_billboards_contract.py`)
- [X] T033 [P] [US3] 단위 테스트 작성: 행 정규화/유효성 검증 (`backend/tests/unit/test_import_parser.py`)
- [X] T034 [P] [US3] 통합 테스트 작성: 수동 업로드 적재 + ImportJobLog 저장 (`backend/tests/integration/test_import_flow.py`)

### 구현

- [X] T035 [P] [US3] 엑셀 파서 및 정규화 로직 구현 (`backend/app/services/import_parser.py`)
- [X] T036 [P] [US3] 적재 서비스 구현 (`backend/app/services/billboard_import_service.py`)
- [X] T037 [US3] 수동 업로드 엔드포인트 구현 (`backend/app/api/v1/import_billboards.py`)
- [X] T038 [US3] ImportJobLog 저장 및 조회 구현 (`backend/app/services/import_job_service.py`)
- [X] T039 [US3] 원본 파일 기본 경로/권한 검증 구현 (`backend/app/services/upload_validation.py`)

**체크포인트**: US3 독립 검증 가능, 운영 수동 적재 절차 완료

---

## 6단계: 마무리 (공통 개선)

- [X] T040 [P] OpenAPI 계약과 실제 응답 정합성 점검 및 문서 보완 (`specs/001-billboard-radius-check/contracts/check-radius.openapi.yaml`, `backend/app/api/v1/`)
- [X] T041 [P] 성능 검증 스크립트 작성 및 p95 1초 목표 측정 (`backend/tests/performance/test_check_radius_perf.py`)
- [X] T042 [P] 운영 가이드 보강(수동 적재/장애 대응/로그 확인) (`specs/001-billboard-radius-check/quickstart.md`)
- [X] T043 코드 정리 및 공통 모듈 리팩터링 (`backend/app/services/`, `frontend/src/services/`)
- [X] T044 전체 테스트 실행 및 회귀 확인 (`backend/tests/`, `frontend/tests/`)

## 의존성 및 실행 순서

- 1단계 완료 후 2단계 진행
- 2단계 완료 전 사용자 스토리 작업 금지
- 2단계 완료 후 US1 -> US2/US3 병렬 진행 가능
- 릴리스 MVP는 US1 완료 시점
- US2/US3는 독립 검증 후 순차 또는 병렬 배포 가능

## 병렬 실행 예시

```bash
# US1 테스트 병렬
T015 + T016 + T017

# US2 구현 병렬(컴포넌트 분리)
T027 + T028 + T030

# US3 테스트 병렬
T032 + T033 + T034
```

## 구현 전략

### MVP 우선

1. 1단계(준비) 완료
2. 2단계(기반) 완료
3. 3단계(US1) 완료
4. API 중심 MVP 검증 후 데모

### 점진 확장

1. US2 지도 시각화 추가
2. US3 수동 적재/이력 관리 추가
3. 마무리 단계에서 성능/운영 문서/회귀 완료

## 비고

- `[P]` 표시는 파일 충돌이 없는 병렬 가능 작업
- 각 스토리는 독립 구현/검증이 가능하도록 구성
- 구현 중 완료된 항목은 `[X]`로 즉시 체크
