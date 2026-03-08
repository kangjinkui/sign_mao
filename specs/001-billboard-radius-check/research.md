# 연구 결과: 200m 대형광고물 반경 판정

## 결정 1: 거리 계산 권위 계층
- **Decision**: 거리 판정은 DB(PostGIS)에서 `ST_DWithin(geography, geography, 200)`로만 수행.
- **Rationale**: 미터 단위 정확도와 결정론을 보장하고 헌장 원칙(지리정보 판단의 결정성)을 만족.
- **Alternatives considered**:
  - 앱 서버 Haversine 계산: 구현은 단순하지만 오차/일관성 이슈로 기각.
  - 프론트엔드 계산: 보안/감사 추적 불리로 기각.

## 결정 2: 지오코딩 다중 결과 처리
- **Decision**: 지오코딩 결과가 복수이면 후보 최대 5개를 반환하고 사용자 선택 후 판정.
- **Rationale**: 자동 선택 오판을 방지하면서 사용자 경험을 유지.
- **Alternatives considered**:
  - Top-1 자동 선택: 빠르지만 오판 리스크가 높아 기각.
  - 오류 반환 후 재입력만 허용: 보수적이나 UX 저하로 기각.

## 결정 3: 판정 데이터 상태 범위
- **Decision**: 상태 `유효(운영중)` 데이터만 판정 포함.
- **Rationale**: 허가 검토 시 현재 효력 데이터만 반영해야 업무 오판을 줄임.
- **Alternatives considered**:
  - 일시중지 포함: 정책 혼선 가능성으로 보류.
  - 전체 이력 포함: 과포함 위험으로 기각.

## 결정 4: 데이터 갱신 정책
- **Decision**: 운영자 수동 업로드만 지원(자동 배치 미지원).
- **Rationale**: 초기 운영 안정성과 감사 추적 단순화.
- **Alternatives considered**:
  - 주기 배치 동기화: 운영 복잡도 증가로 초기 제외.
  - 수동+자동 병행: 장애면적 증가로 초기 제외.

## 결정 5: API 계약 및 오류 표준
- **Decision**: `/api/v1` 버전 경로 사용, 오류 코드는 `VALIDATION_ERROR`, `GEOCODING_ERROR`, `INTERNAL_ERROR` 고정.
- **Rationale**: 클라이언트 처리 예측 가능성과 향후 버전 관리 용이성 확보.
- **Alternatives considered**:
  - 자유형 문자열 오류: 호환성/분석 난이도 증가로 기각.

## 결정 6: 성능 검증 기준
- **Decision**: p95 1초 목표, 동시 요청 부하 테스트로 검증.
- **Rationale**: 업무 체감 성능 목표와 헌장 성능 예산을 동시에 충족.
- **Alternatives considered**:
  - 평균 응답시간만 관리: tail latency 누락으로 기각.
