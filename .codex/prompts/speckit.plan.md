---
description: plan 템플릿 기반으로 구현 계획 워크플로우를 수행해 설계 산출물을 생성합니다.
handoffs:
  - label: 작업 생성
    agent: speckit.tasks
    prompt: 계획을 작업으로 분해해줘
    send: true
  - label: 체크리스트 생성
    agent: speckit.checklist
    prompt: 다음 도메인에 대한 체크리스트를 만들어줘...
---

## 사용자 입력

```text
$ARGUMENTS
```

입력이 비어 있지 않다면 반드시 고려해야 합니다.

## 개요

1. **준비**: 루트에서 실행
`.specify/scripts/bash/setup-plan.sh --json`

JSON에서 `FEATURE_SPEC`, `IMPL_PLAN`, `SPECS_DIR`, `BRANCH` 파싱.

2. **컨텍스트 로드**
- `FEATURE_SPEC`
- `.specify/memory/constitution.md`
- `IMPL_PLAN` 템플릿(이미 복사됨)

3. **계획 워크플로우 실행**
- Technical Context 채우기(미정은 `NEEDS CLARIFICATION`)
- Constitution Check 채우기
- 게이트 평가(정당화 없는 위반은 ERROR)
- Phase 0: `research.md` 생성(모든 미정 해소)
- Phase 1: `data-model.md`, `contracts/`, `quickstart.md` 생성
- Phase 1: agent context 업데이트 스크립트 실행
- 설계 후 Constitution Check 재평가

4. **종료/보고**
- Phase 2 계획 완료 시 종료
- 브랜치, `IMPL_PLAN` 경로, 생성 산출물 보고

## Phase 0: 개요 및 리서치

1. Technical Context의 미정 항목 추출
- `NEEDS CLARIFICATION`별 리서치 태스크
- 의존성별 베스트 프랙티스 태스크
- 연동별 패턴 태스크

2. 리서치 에이전트 작업 생성

```text
For each unknown in Technical Context:
  Task: "Research {unknown} for {feature context}"
For each technology choice:
  Task: "Find best practices for {tech} in {domain}"
```

3. 결과를 `research.md`로 통합
- Decision
- Rationale
- Alternatives considered

산출물: `research.md`(미정 항목 해소 완료)

## Phase 1: 설계 및 계약

선행조건: `research.md` 완료

1. 기능 명세에서 엔터티 추출 → `data-model.md`
- 엔터티명/필드/관계
- 요구사항 기반 검증 규칙
- 상태 전이(해당 시)

2. 외부 인터페이스가 있으면 계약 정의 → `contracts/`
- 사용자/타 시스템에 노출되는 인터페이스 식별
- 프로젝트 유형에 맞는 계약 형식 문서화
- 내부 전용 프로젝트면 생략 가능

3. Agent 컨텍스트 업데이트
- `.specify/scripts/bash/update-agent-context.sh codex` 실행
- 현재 계획의 신규 기술만 추가
- 수동 추가 구간은 보존

산출물: `data-model.md`, `contracts/*`, `quickstart.md`, agent 컨텍스트 파일

## 핵심 규칙

- 절대경로 사용
- 게이트 실패 또는 미해결 미정 항목이 있으면 ERROR
