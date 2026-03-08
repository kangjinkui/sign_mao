<!--
Sync Impact Report
- 버전 변경: 1.0.0 -> 1.0.1
- Modified principles: wording localization only (English -> Korean)
- Added sections: 없음
- Removed sections: 없음
- Templates requiring updates:
  - ✅ updated: .specify/templates/agent-file-template.md
  - ✅ updated: .specify/templates/checklist-template.md
  - ✅ updated: .specify/templates/constitution-template.md
  - ✅ updated: .specify/templates/plan-template.md
  - ✅ updated: .specify/templates/spec-template.md
  - ✅ updated: .specify/templates/tasks-template.md
  - ⚠ pending: .specify/templates/commands/*.md (디렉터리 없음)
- Follow-up TODOs: 없음
-->

# Sign Map 헌장

## 핵심 원칙

### I. 지리정보 판단의 결정성
허가 판단에 사용되는 거리 계산은 반드시 PostGIS의 미터 단위 geography 계산으로 수행한다.
애플리케이션 단의 근사 계산은 허가 판단에 사용하지 않는다.
동일 입력 좌표는 항상 동일한 결과와 추적 가능한 쿼리 파라미터를 반환해야 한다.

### II. 단일 데이터 원천과 감사 추적
`data/raw`는 변경하지 않는 원본 스냅샷 저장소로 사용한다.
정제/변환 데이터는 재현 가능한 스크립트로 파생 위치에 생성해야 한다.
적재와 반경 판정 결과는 원본 파일, 실행 시각, 규칙 버전을 추적 가능하게 남겨야 한다.

### III. 규정 민감 영역 테스트 원칙
지오코딩, 공간 쿼리, 허가 판정 기준, 데이터 정규화 변경 시 테스트를 필수로 작성한다.
구현 전 실패 테스트를 먼저 확인하고, 구현 후 통과를 검증한다.
최소 단위 테스트 1개와 통합 테스트 1개를 포함해야 한다.

### IV. API 계약과 오류 예측 가능성
외부 API는 버전이 명시된 요청/응답 스키마와 안정적인 오류 코드를 제공해야 한다.
유효성 오류, 지오코딩 오류, 내부 오류는 기계 판독 가능한 서로 다른 식별자를 사용한다.
호환성을 깨는 계약 변경은 API 계약 버전을 MAJOR로 올린다.

### V. 운영 단순성과 성능 예산
시스템은 명확한 데이터 흐름과 낮은 운영 복잡성을 우선한다.
핵심 판정 API는 합의된 부하에서 p95 1초 이내를 목표로 한다.
복잡성을 도입할 경우 더 단순한 대안을 기각한 이유를 계획 문서에 남긴다.

## 운영 제약

- 기본 백엔드는 Python(FastAPI) 또는 Node.js(Express/NestJS) 중 선택한다.
- 공간 저장소는 PostgreSQL + PostGIS를 권위 저장소로 사용한다.
- 공간 컬럼은 SRID를 명시하고 운영 쿼리는 인덱스를 사용해야 한다.
- 개인정보는 업무상 필요한 최소 필드만 수집한다.
- 운영 로그는 민감정보를 마스킹하면서 감사 가능성을 유지한다.

## 개발 워크플로우

- `/speckit.specify`는 독립 배포 가능한 사용자 스토리와 측정 가능한 인수 기준을 정의해야 한다.
- `/speckit.plan`은 구현 시작 전 헌장 점검 게이트를 통과해야 한다.
- `/speckit.tasks`는 데이터 품질, 공간 검증, API 계약, 관측성 작업을 반영해야 한다.
- PR에는 영향받는 헌장 원칙과 준수 증거(테스트, 샘플 응답, 쿼리 근거)를 포함한다.

## 거버넌스

이 헌장은 저장소의 다른 관행 문서보다 우선한다.
개정 시 다음을 충족해야 한다.
1. 변경 근거와 영향 분석 문서화
2. `.specify/templates/` 동기화 검증
3. 시맨틱 버전 업데이트 기록

버전 정책:
- MAJOR: 원칙 삭제/재정의 또는 거버넌스의 호환 불가 변경
- MINOR: 새 원칙/섹션 추가 또는 의무 지침의 실질 확장
- PATCH: 의미 변경 없는 표현/편집 개선

준수 검토는 계획 단계와 코드리뷰 단계에서 필수다.
예외는 담당자, 종료일, 완화 계획과 함께 명시해야 한다.

**버전**: 1.0.1 | **제정일**: 2026-03-05 | **최종 개정일**: 2026-03-05
