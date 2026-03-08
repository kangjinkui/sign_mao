---
description: 입력된 원칙을 기반으로 프로젝트 헌장을 생성/수정하고 종속 템플릿과 동기화합니다.
handoffs:
  - label: 명세 작성
    agent: speckit.specify
    prompt: 업데이트된 헌장을 기준으로 기능 명세를 작성합니다. 만들고 싶은 기능은...
---

## 사용자 입력

```text
$ARGUMENTS
```

입력이 비어 있지 않다면 반드시 고려해야 합니다.

## 개요

대상 파일: `.specify/memory/constitution.md`

이 파일은 대괄호 플레이스홀더를 가진 템플릿입니다.
해야 할 일:
1. 값 수집/추론
2. 플레이스홀더 정확 치환
3. 종속 산출물에 변경 전파

파일이 없으면 `.specify/templates/constitution-template.md`에서 먼저 복사합니다.

## 실행 흐름

1. 기존 헌장 로드
- `[ALL_CAPS_IDENTIFIER]` 형식 플레이스홀더 전부 식별
- 사용자 요구 원칙 수가 템플릿과 다르면 사용자 요구를 우선

2. 값 수집/추론
- 사용자 입력에 값이 있으면 우선 사용
- 없으면 저장소 문맥(README/docs/기존 헌장)에서 추론
- 날짜 규칙:
  - `RATIFICATION_DATE`: 최초 제정일
  - `LAST_AMENDED_DATE`: 수정 시 오늘 날짜
- 버전(`CONSTITUTION_VERSION`)은 semver로 증가
  - MAJOR: 비호환 원칙 삭제/재정의
  - MINOR: 원칙/섹션 추가 또는 의무 지침의 실질 확장
  - PATCH: 의미 변화 없는 문구/오타/명료화

3. 헌장 초안 작성
- 가능한 한 모든 플레이스홀더 치환
- 남겨야 하는 토큰이 있다면 이유를 명시
- 헤딩 계층 유지
- 원칙 섹션은 테스트 가능한 규칙으로 작성
- 거버넌스에 개정 절차/버전 정책/준수 검토 포함

4. 일관성 전파 점검
- `.specify/templates/plan-template.md`의 Constitution Check 정렬
- `.specify/templates/spec-template.md`의 필수 섹션/제약 정렬
- `.specify/templates/tasks-template.md`의 원칙 반영 작업 유형 정렬
- `.specify/templates/commands/*.md`의 구식 참조 점검
- 런타임 가이드(README, docs 등) 원칙 참조 갱신

5. Sync Impact Report 생성
헌장 파일 최상단 HTML 주석으로 추가:
- 버전 변경: old -> new
- 수정 원칙 목록
- 추가/삭제 섹션
- 템플릿 반영 상태(✅/⚠)
- 유예 TODO

6. 최종 검증
- 설명 없는 대괄호 토큰 잔존 없음
- 버전 라인과 리포트 일치
- 날짜 ISO(YYYY-MM-DD)
- 원칙 문장이 선언적/검증 가능하며 모호 표현 최소화

7. 파일 저장
- `.specify/memory/constitution.md` 덮어쓰기

8. 사용자 보고
- 새 버전과 증가 근거
- 수동 후속 필요 파일
- 권장 커밋 메시지

## 스타일 규칙

- 템플릿의 헤딩 레벨 유지
- 긴 문장은 읽기 좋게 줄바꿈
- 섹션 사이 빈 줄 1개
- trailing whitespace 금지

핵심 정보가 정말 없으면 `TODO(<FIELD_NAME>): ...`를 남기고 Sync Report에 기록합니다.
