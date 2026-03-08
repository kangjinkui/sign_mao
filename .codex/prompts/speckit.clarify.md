---
description: 활성 기능 명세의 미정의 영역을 최대 5개 질문으로 보완하고 결과를 spec에 반영합니다.
handoffs:
  - label: 기술 계획 수립
    agent: speckit.plan
    prompt: 명세 기반 계획을 작성해줘. 사용 기술은...
---

## 사용자 입력

```text
$ARGUMENTS
```

입력이 비어 있지 않다면 반드시 고려해야 합니다.

## 개요

목표: 활성 기능 명세의 모호성/누락 의사결정을 줄이고, 확정 내용을 spec 파일에 직접 반영합니다.

참고: 이 절차는 기본적으로 `/speckit.plan` 전에 완료하는 것을 권장합니다.

## 실행 단계

1. 루트에서 1회 실행:

`.specify/scripts/bash/check-prerequisites.sh --json --paths-only`

JSON에서 최소 필드를 파싱합니다.
- `FEATURE_DIR`
- `FEATURE_SPEC`
- (선택) `IMPL_PLAN`, `TASKS`

파싱 실패 시 `/speckit.specify` 재실행 또는 브랜치 환경 점검을 안내하고 중단합니다.

2. 현재 spec를 로드하고 아래 분류로 상태를 판단합니다: `Clear / Partial / Missing`
- 기능 범위/행동
- 도메인/데이터 모델
- 상호작용/UX 흐름
- 비기능 품질(성능/확장성/신뢰성/관측성/보안/컴플라이언스)
- 외부 연동/의존성
- 실패/엣지 케이스
- 제약/트레이드오프
- 용어 일관성
- 완료 신호(검증 가능 수용 기준)
- TODO/모호 형용사

3. 내부적으로 우선순위 질문 큐(최대 5개)를 만듭니다.
- 아키텍처/데이터/테스트/UX/운영/컴플라이언스에 실질 영향이 있는 질문만
- 답변 형식은 아래 중 하나
  - 2~5개 상호배타 옵션
  - 5단어 이하 단답
- 이미 해결된 내용/사소 취향/계획 단계 세부사항은 제외

4. 순차 질의(상호작용)
- 한 번에 정확히 1개 질문만 제시
- 옵션형일 때:
  - 추천 옵션을 먼저 제시(1~2문장 근거)
  - 옵션 표 출력
  - 사용자에게 `A`/`yes`/`recommended`/직접 단답 응답을 허용
- 단답형일 때:
  - 제안 답변 + 짧은 근거
  - `yes`/`suggested` 수락 가능
- 답변이 모호하면 같은 질문에서만 재확인
- 종료 조건:
  - 핵심 모호성 조기 해소
  - 사용자 종료 의사(`done`, `no more`)
  - 질문 5개 도달

5. 답변 수락 직후 즉시 spec에 반영(증분 저장)
- 최초 반영 시 `## Clarifications`와 `### Session YYYY-MM-DD`를 보장
- 항목 추가:
  - `- Q: <question> → A: <final answer>`
- 적용 위치 예시:
  - 기능 모호성 → Functional Requirements
  - 사용자 행위/역할 → User Stories
  - 데이터 구조 → Data Model
  - 비기능 → 품질 속성 섹션(측정 가능 값으로)
  - 엣지/실패 → Edge Cases/Error Handling
  - 용어 충돌 → 용어 정규화
- 기존 문장과 충돌하면 중복 추가 대신 교체
- 각 반영 후 원자적으로 저장

6. 매 반영 후 검증
- 승인 답변당 Clarifications bullet 1개
- 총 질문 수 5 이하
- 반영 대상 모호성 잔존 없음
- 상충 문장 제거됨
- 허용 신규 헤딩만 사용
- 용어 일관성 유지

7. 업데이트된 spec를 `FEATURE_SPEC`에 기록

8. 완료 보고
- 질문/답변 수
- 수정된 spec 경로
- 변경 섹션 목록
- 분류별 상태 요약(Resolved/Deferred/Clear/Outstanding)
- 잔여 고영향 항목이 있으면 `/speckit.plan` 진행 여부 권고
- 다음 권장 명령 제시

## 동작 규칙

- 의미 있는 모호성이 없으면:
  - "No critical ambiguities detected worth formal clarification." 출력 후 진행 권고
- spec가 없으면 `/speckit.specify` 먼저 실행 안내
- 질문은 절대 5개 초과 금지
- 사용자가 중단하면 즉시 존중

우선순위 컨텍스트: $ARGUMENTS
