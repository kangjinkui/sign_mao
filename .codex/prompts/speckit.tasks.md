---
description: 설계 산출물을 바탕으로 실행 가능하고 의존성 순서가 보장된 tasks.md를 생성합니다.
handoffs:
  - label: 일관성 분석
    agent: speckit.analyze
    prompt: 프로젝트 일관성 분석 실행
    send: true
  - label: 구현 시작
    agent: speckit.implement
    prompt: 단계별 구현 시작
    send: true
---

## 사용자 입력

```text
$ARGUMENTS
```

입력이 비어 있지 않다면 반드시 고려해야 합니다.

## 개요

1. **준비**: 루트에서 `.specify/scripts/bash/check-prerequisites.sh --json` 실행
- `FEATURE_DIR`, `AVAILABLE_DOCS` 파싱
- 모든 경로는 절대경로

2. **설계 문서 로드** (`FEATURE_DIR`)
- 필수: `plan.md`, `spec.md`
- 선택: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`

3. **작업 생성 워크플로우**
- plan에서 스택/라이브러리/구조 추출
- spec에서 사용자 스토리와 우선순위(P1/P2/P3...) 추출
- data-model/contracts/research가 있으면 매핑 보강
- 사용자 스토리 중심으로 작업 구성
- 의존성 그래프와 병렬 실행 기회 도출
- 각 스토리가 독립 테스트 가능한지 검증

4. **tasks.md 생성** (템플릿: `.specify/templates/tasks-template.md`)
- 기능명 반영
- Phase 1: Setup
- Phase 2: Foundational
- Phase 3+: 사용자 스토리별 단계(우선순위 순)
- 최종: Polish/Cross-cutting
- 각 작업은 체크리스트 형식 엄수
- 파일 경로 명시
- 스토리별 독립 테스트 기준 포함
- MVP 우선 전략 포함

5. **결과 보고**
- 생성된 tasks.md 경로
- 전체 task 수
- 스토리별 task 수
- 병렬 작업 기회
- 스토리별 독립 테스트 기준
- 권장 MVP 범위(보통 US1)
- 형식 검증 결과

## 작업 생성 규칙

**중요**: 작업은 반드시 사용자 스토리 단위로 조직해야 합니다.

테스트는 기본 선택사항이며, spec에서 명시했거나 TDD 요청 시 생성합니다.

### 체크리스트 형식(필수)

모든 task는 아래 형식을 따릅니다.

```text
- [ ] [TaskID] [P?] [Story?] 파일 경로를 포함한 설명
```

구성요소:
1. 체크박스: `- [ ]`
2. Task ID: `T001`, `T002` ...
3. `[P]`: 병렬 가능할 때만
4. `[Story]`: 사용자 스토리 단계에서 필수 (`[US1]`, `[US2]`...)
5. 설명: 명확한 동작 + 정확한 파일 경로

예시:
- `- [ ] T001 Create project structure per implementation plan`
- `- [ ] T005 [P] Implement auth middleware in src/middleware/auth.py`
- `- [ ] T012 [P] [US1] Create User model in src/models/user.py`

### 조직 원칙

1. **사용자 스토리 우선**
- 각 스토리별 독립 단계 부여
- 모델/서비스/UI/API/테스트를 해당 스토리로 매핑

2. **계약 반영**
- 인터페이스 계약을 관련 스토리에 매핑
- 테스트가 필요하면 해당 스토리 단계에서 구현 전 계약 테스트 배치

3. **데이터 모델 반영**
- 엔터티를 필요한 스토리에 배치
- 다수 스토리에 공통이면 가장 이른 단계 또는 Setup 배치

4. **공통 인프라 분리**
- 공용 인프라: Setup
- 전체 차단 작업: Foundational
- 스토리 전용 설정: 해당 스토리 단계

### 단계 구조

- Phase 1: Setup
- Phase 2: Foundational
- Phase 3+: 사용자 스토리(P1 -> P2 -> P3)
- Final: Polish & Cross-Cutting
