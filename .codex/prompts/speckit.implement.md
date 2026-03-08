---
description: tasks.md에 정의된 작업을 순서대로 실행하여 구현을 진행합니다.
---

## 사용자 입력

```text
$ARGUMENTS
```

입력이 비어 있지 않다면 반드시 고려해야 합니다.

## 개요

1. 루트에서 실행:
`.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`

JSON에서 `FEATURE_DIR`, `AVAILABLE_DOCS`를 파싱합니다.

2. **체크리스트 상태 확인** (`FEATURE_DIR/checklists/`가 있을 때)
- 각 체크리스트 파일에 대해 집계
  - 전체: `- [ ]`, `- [X]`, `- [x]`
  - 완료: `- [X]`, `- [x]`
  - 미완료: `- [ ]`
- 표 출력:

```text
| Checklist | Total | Completed | Incomplete | Status |
|-----------|-------|-----------|------------|--------|
| ux.md     | 12    | 12        | 0          | ✓ PASS |
| test.md   | 8     | 5         | 3          | ✗ FAIL |
```

- 하나라도 미완료면 중단 후 질문:
  - "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
- 사용자가 `yes/proceed/continue`이면 진행, 아니면 중단

3. 구현 컨텍스트 로드
- 필수: `tasks.md`, `plan.md`
- 선택: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`

4. 프로젝트 설정 검증
- 실제 프로젝트 상태를 보고 ignore 파일 생성/검증
  - git repo면 `.gitignore`
  - Docker 관련이면 `.dockerignore`
  - ESLint/Prettier/npm/Terraform/Helm 관련 ignore 처리
- 기존 ignore가 있으면 필수 패턴만 보강
- 없으면 기술 스택에 맞는 기본 패턴으로 생성

5. `tasks.md` 구조 파싱
- 단계(Setup/Tests/Core/Integration/Polish)
- 의존성(순차/병렬)
- Task 세부(ID/설명/경로/[P])

6. 계획에 따라 구현 실행
- 단계별 완료 후 다음 단계 진행
- 의존성 준수
- TDD 지시가 있으면 테스트 선행
- 같은 파일 수정 task는 순차 실행
- 단계 완료마다 검증

7. 실행 규칙
- Setup 선행
- 필요 시 테스트를 먼저 작성
- Core 구현(모델/서비스/API/CLI)
- 통합 작업(DB/미들웨어/외부연동/로깅)
- 마무리(단위테스트/성능/문서)

8. 진행/오류 처리
- task 완료마다 진행 보고
- 비병렬 task 실패 시 중단
- 병렬 task는 성공분 진행, 실패분 보고
- 디버깅 가능한 오류 문맥 제공
- **중요**: 완료 task는 `tasks.md`에서 `[X]`로 체크

9. 완료 검증
- 필수 task 완료 여부
- 구현 결과가 명세와 부합하는지
- 테스트 통과 및 요구 커버리지
- 기술 계획 준수 여부
- 최종 요약 보고

참고: tasks가 없거나 불완전하면 `/speckit.tasks` 재생성을 안내합니다.
