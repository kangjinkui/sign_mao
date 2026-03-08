# 구현 계획: 200m 대형광고물 반경 판정

**브랜치**: `001-billboard-radius-check` | **작성일**: 2026-03-05 | **명세**: [/mnt/c/Users/user/sign_map/specs/001-billboard-radius-check/spec.md](/mnt/c/Users/user/sign_map/specs/001-billboard-radius-check/spec.md)
**입력**: `/specs/001-billboard-radius-check/spec.md`의 기능 명세

**참고**: 이 계획은 `/speckit.plan` 절차에 따라 작성되었습니다.

## 요약

이 기능은 주소 입력 기반으로 200m 반경 내 대형광고물(옥상전광/벽면전광) 존재 여부를 판정하고,
지도 및 목록으로 결과를 제시한다. 거리 판단은 PostGIS `ST_DWithin`(geography, meter)로 고정하며,
지오코딩 다중 결과는 후보 최대 5개를 제시하고 사용자 선택 후 판정한다. 데이터 갱신은
운영자 수동 업로드만 허용하며 적재 이력을 남긴다.

## 기술 맥락

**언어/버전**: Python 3.11 (backend), TypeScript 5.x (frontend)  
**핵심 의존성**: FastAPI, SQLAlchemy, psycopg, PostGIS, Kakao Maps JavaScript SDK  
**저장소**: PostgreSQL 16 + PostGIS, 원본 파일(`data/raw`)  
**테스트**: pytest, httpx(TestClient), Playwright(지도 렌더링 핵심 시나리오)  
**대상 플랫폼**: Linux 컨테이너 서버 + 최신 Chromium 기반 브라우저  
**프로젝트 유형**: 웹 애플리케이션(backend + frontend)  
**성능 목표**: 반경 판정 API p95 1초 이내  
**제약사항**: 수동 업로드만 허용, 상태 `유효(운영중)`만 판정 포함, 다중 지오코딩 후보 최대 5개  
**규모/범위**: 초기 기준 광고물 약 49건(제공 원본), 향후 수천 건까지 확장 고려

## 헌장 점검

*게이트: Phase 0 연구 시작 전 통과, Phase 1 설계 후 재점검 필수*

- `지리정보 정확성`: **통과**. 거리 계산은 PostGIS geography + `ST_DWithin`만 사용.
- `데이터 추적성`: **통과**. 원본 스냅샷 경로, 적재 이력(파일명/시각/규칙버전/성공실패건수) 포함.
- `테스트 원칙`: **통과**. 지오코딩/공간쿼리/판정 규칙에 단위+통합 테스트를 설계 산출물에 반영.
- `API 예측 가능성`: **통과**. 버전 경로(`/api/v1`), 안정 오류코드(`VALIDATION_ERROR`, `GEOCODING_ERROR`, `INTERNAL_ERROR`) 정의.
- `성능 예산`: **통과**. p95 1초 목표와 검증 시나리오(동시 요청 부하 테스트) 정의.

## 프로젝트 구조

### 문서 산출물 (기능 단위)

```text
specs/001-billboard-radius-check/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── check-radius.openapi.yaml
└── tasks.md
```

### 소스 코드 구조 (저장소 루트)

```text
backend/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── schemas/
│   └── db/
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    └── performance/

frontend/
├── src/
│   ├── pages/
│   ├── components/
│   └── services/
└── tests/
```

**구조 결정**: 웹 앱 구조(backend + frontend) 채택. 이유는 지도 렌더링(UI)과 공간 판정(API)을 분리해
확장성과 테스트 독립성을 확보하기 위함.

## 복잡도 추적

해당 없음. 헌장 점검 위반 없이 구현 가능.
