---
description: 자연어 기능 설명으로부터 기능 명세를 생성하거나 업데이트합니다.
handoffs:
  - label: 기술 계획 수립
    agent: speckit.plan
    prompt: 이 명세 기반으로 계획을 만들어줘. 사용 기술은...
  - label: 명세 보완
    agent: speckit.clarify
    prompt: 명세 요구사항을 명확화해줘
    send: true
---

## 사용자 입력

```text
$ARGUMENTS
```

입력이 비어 있지 않다면 반드시 고려해야 합니다.

## 개요

트리거 메시지에서 `/speckit.specify` 뒤에 사용자가 입력한 텍스트가 곧 기능 설명입니다.
`$ARGUMENTS`가 그대로 보이더라도 이 대화 컨텍스트의 설명을 사용합니다.
빈 명령이 아니라면 재입력을 요구하지 않습니다.

## 실행 절차

1. **브랜치 짧은 이름 생성(2~4단어)**
- 기능 설명의 핵심 키워드를 추출
- 가능하면 동사-명사 형식 사용
- 기술 약어(OAuth2, API, JWT 등)는 유지
- 예시
  - "사용자 인증 추가" -> `user-auth`
  - "API OAuth2 연동" -> `oauth2-api-integration`

2. **기존 브랜치 확인 후 번호 결정**

a. 원격 최신화
```bash
git fetch --all --prune
```

b. 같은 short-name의 최대 번호 탐색
- 원격 브랜치
- 로컬 브랜치
- `specs/[번호]-[short-name]` 디렉터리

c. 다음 번호 계산: 최대값 N이면 `N+1`

d. 스크립트 1회 실행
`.specify/scripts/bash/create-new-feature.sh --json ... --number N+1 --short-name "..."`

중요:
- 3개 소스(원격/로컬/specs) 모두 확인
- short-name이 정확히 일치하는 항목만 매칭
- 없으면 1부터 시작
- 스크립트는 기능당 1회만 실행
- JSON 출력의 `BRANCH_NAME`, `SPEC_FILE`을 기준으로 후속 처리

3. `.specify/templates/spec-template.md` 로드

4. 아래 흐름으로 명세 작성

1) 사용자 설명 파싱
- 비어 있으면 오류: `No feature description provided`

2) 핵심 개념 추출
- 행위자, 행동, 데이터, 제약

3) 불명확 항목 처리
- 문맥/관행 기반으로 합리적 가정
- 정말 필요한 경우만 `[NEEDS CLARIFICATION: ...]` 사용
- 최대 3개
- 우선순위: 범위 > 보안/개인정보 > UX > 기술 세부

4) 사용자 시나리오/테스트 섹션 작성
- 사용자 흐름을 도출할 수 없으면 오류

5) 기능 요구사항 생성
- 모두 테스트 가능해야 함

6) 성공 기준 정의
- 측정 가능, 기술중립, 검증 가능

7) 데이터가 있으면 핵심 엔터티 정의

8) 완료 상태 반환: planning 가능

5. 템플릿 구조와 섹션 순서를 유지해 `SPEC_FILE`에 저장

6. **명세 품질 검증**

a. `FEATURE_DIR/checklists/requirements.md` 체크리스트 생성
- 필수 섹션 완성 여부
- 모호성/측정가능성/기술중립성 점검
- 수용 시나리오/엣지케이스/범위/가정 점검

b. 체크리스트 항목별 통과/실패 판정

c. 결과 처리
- 전부 통과: 다음 단계 진행
- 일부 실패(clarification 제외): spec 수정 후 재검증(최대 3회)
- `[NEEDS CLARIFICATION]` 남음:
  - 최대 3개 질문으로 정리
  - 각 질문에 옵션 표(A/B/C/Custom) 제공
  - 사용자 응답을 받아 spec 반영 후 재검증

d. 각 반복마다 체크리스트 파일 상태 업데이트

7. 완료 보고
- 브랜치명
- spec 경로
- 체크리스트 결과
- 다음 권장 단계(`/speckit.clarify` 또는 `/speckit.plan`)

## 일반 가이드

- 사용자에게 필요한 **무엇(WHAT)**, **왜(WHY)**에 집중
- 구현 방법(HOW) 금지: 기술 스택/API/코드 구조 서술 금지
- 비기술 이해관계자도 읽을 수 있게 작성
- spec 내부에 체크리스트를 삽입하지 않음

### AI 생성 시 원칙

1. 문맥 기반 합리적 가정
2. 가정은 Assumptions에 기록
3. clarification은 최대 3개로 제한
4. 테스트 가능한 요구사항 작성
5. 중요 영역만 질문(범위/보안/권한 등)

### 성공 기준 원칙

- 측정 가능(시간/비율/건수)
- 기술중립(특정 프레임워크/DB/도구 언급 금지)
- 사용자/비즈니스 관점
- 구현 상세 없이 검증 가능
