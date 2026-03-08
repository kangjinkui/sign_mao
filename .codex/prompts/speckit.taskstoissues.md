---
description: 기존 tasks를 의존성 순서의 GitHub 이슈로 변환합니다.
tools: ['github/github-mcp-server/issue_write']
---

## 사용자 입력

```text
$ARGUMENTS
```

입력이 비어 있지 않다면 반드시 고려해야 합니다.

## 개요

1. 루트에서 실행:
`.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`

2. 출력에서 `tasks` 파일 경로를 추출

3. Git 원격 URL 확인:

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> 원격이 GitHub URL일 때만 다음 단계 진행

4. tasks의 각 항목을 GitHub MCP 서버로 이슈 생성

> [!CAUTION]
> 원격 URL과 일치하지 않는 저장소에는 절대 이슈를 생성하지 않음
