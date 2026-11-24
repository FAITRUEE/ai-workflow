<p align="center">
  <img src="docs/images/banner.svg" alt="AI와 일하는 방식 — 맡기고, 직접 재 보고, 확인한 것은 남긴다" width="100%">
</p>

<p align="center">
  <img src="docs/images/badge-plugin.svg" alt="Claude Code plugin">
  <img src="docs/images/badge-skills.svg" alt="skills 8">
  <img src="docs/images/badge-templates.svg" alt="templates 2">
  <img src="docs/images/badge-license.svg" alt="MIT license">
</p>

<p align="center">
  <a href="#-설치">설치</a> ·
  <a href="#-스킬-8종">스킬 8종</a> ·
  <a href="#-일하는-방식">일하는 방식</a> ·
  <a href="#-프로젝트에서-실제로-한-것">프로젝트 사례</a> ·
  <a href="#-양식">양식</a>
</p>

---

AI 코딩 도구는 코드를 빨리 써 주지만, 그만큼 **확인하지 않은 예상이 사실처럼 문서에 적히기 쉽습니다.**
이 저장소는 프로젝트마다 그 문제를 겪으며 굳힌 규칙과, 그 규칙을 Claude Code가 매번 따르도록 옮긴 **스킬 8종 · 양식 2종**입니다.

> **AI에게는 초안과 구현을, 저는 방향 · 기준 · 확인 · 병합을 맡깁니다.**

## ⚡ 설치

Claude Code에서 두 줄이면 됩니다.

```text
/plugin marketplace add FAITRUEE/ai-workflow
/plugin install ai-workflow@ai-workflow
```

플러그인 없이 쓰려면 `skills/` 아래에서 필요한 폴더만 `~/.claude/skills/`에 복사하세요. 설치 뒤에는 아래 예시처럼 평소 말투로 부탁하면 맞는 스킬이 알아서 켜집니다.

## 🧰 스킬 8종

| 묶음 | 스킬 | 한 줄 |
|---|---|---|
| **확인 · 검증** | [`assumption-check`](skills/assumption-check/SKILL.md) | "작동한다"고 적기 전에 실제로 통과시키고, 틀린 이유까지 남긴다 |
| | [`api-verify`](skills/api-verify/SKILL.md) | 서버를 띄워 가입부터 권한 확인까지 실제 API로 한 바퀴 돌린다 |
| | [`oof-error-analysis`](skills/oof-error-analysis/SKILL.md) | 분류 모델이 어디서 틀렸는지 구간별로 세고 틀린 행을 직접 본다 |
| **팀 협업** | [`slack-worklog`](skills/slack-worklog/SKILL.md) | [작업 시작] · [작업 정리] 슬랙 초안. 남의 [작업 시작]부터 읽는다 |
| | [`notion-team-hub`](skills/notion-team-hub/SKILL.md) | 노션 팀 공간을 정해진 틀로 깔고, 게스트 팀원도 AI로 읽게 연결한다 |
| | [`notion-publish`](skills/notion-publish/SKILL.md) | md 원고를 노션 정본에 반영. 현재본을 먼저 읽고 합치고, 남의 문서는 안 고친다 |
| | [`github-team-setup`](skills/github-team-setup/SKILL.md) | 조직 · 저장소 · PR 템플릿 · 브랜치 이름 자동 라벨을 첫날 깐다 |
| **기록** | [`contribution-audit`](skills/contribution-audit/SKILL.md) | 팀 프로젝트에서 내가 한 것만 git blame · PR로 가려 문서로 남긴다 |

### 확인 · 검증

#### ✅ `assumption-check` — 확인하고 적기

"작동한다"를 문서에 적기 전에 그 경로를 실제로 통과시키고, 틀렸으면 **무엇이 · 왜 · 얼마나 · 내가 왜 틀렸나** 네 가지를 남깁니다. 원인을 못 찾았으면 그럴듯한 설명 대신 "특정하지 못했다"고 씁니다.

- **이럴 때 켜집니다** — 설정 · 배포가 "된다"고 PR · 보고에 적으려 할 때, 측정값을 남에게 넘길 때, 테스트가 예상과 다를 때
- **이렇게 말해 보세요** — *"이거 진짜 되는 거 맞아? 확인해 봐"*, *"배포 시간 줄었다고 써도 돼?"*
- **시작된 곳** — SoftBank 해커톤 One Action. 캐시로 42초 줄인다던 AI의 예상이 실측으로는 20초 손해였던 일

#### 🖥️ `api-verify` — 서버 띄워서 실제 API로 확인

단위 테스트가 통과해도 실제 서버에서는 인증 필터 · 직렬화 · 설정 때문에 다르게 동작합니다. 서버를 백그라운드로 띄우고, 사용자가 밟는 순서 그대로 가입 → 로그인 → 데이터 만들기 → 설정 바꾸기 → **다른 사용자로 남의 데이터 조회(403이어야 함)** 까지 돌린 뒤 치웁니다.

- **이럴 때 켜집니다** — 백엔드를 고친 뒤 "됐다"고 말하기 전
- **이렇게 말해 보세요** — *"서버 띄워서 확인해 봐"*, *"회원가입부터 끝까지 테스트해 줘"*
- **시작된 곳** — NowWhat(1인 · 3일). Windows에서 `curl`에 한글을 바로 넣으면 깨져 **403처럼 보이던** 함정까지 기록

#### 🔍 `oof-error-analysis` — 분류 모델의 실수 뜯어보기

점수 하나만 보지 않고 맞힘 · 놓침 · 잘못 판정을 구간별로 세고, 틀린 행을 피처와 함께 보고, 규칙 · 다른 모델과 비교합니다. 제출끼리 판정이 갈리는 행도 찾아 줍니다.

- **이럴 때 켜집니다** — 분류 대회 · 실험에서 점수가 정체됐을 때, 두 모델이 뭐가 다른지 알고 싶을 때
- **이렇게 말해 보세요** — *"어디서 틀렸는지 봐 줘"*, *"다음 피처 찾아 줘"*, *"#5랑 #6 뭐가 달라?"*
- **들어 있는 것** — `scripts/analyze.py`(numpy · pandas만 필요)

### 팀 협업

#### 💬 `slack-worklog` — [작업 시작] · [작업 정리] 초안

오늘 머지된 PR · 실험 기록 · 다음 할 일을 모아 슬랙 초안을 만듭니다. **보내는 건 사람이 하고**, 키 · 토큰은 절대 넣지 않으며, 착수 전에 **다른 사람의 [작업 시작]부터 읽어** 같은 일을 두 사람이 잡지 않게 합니다.

- **이렇게 말해 보세요** — *"작업 시작 메시지 써 줘"*, *"오늘 한 거 정리해서 슬랙에"*
- **시작된 곳** — One Action에서 같은 기능을 두 사람이 만드는 일이 두 번 생긴 뒤, 타운시그널에서 스킬로

#### 🗂️ `notion-team-hub` — 노션 팀 공간 + 팀원 AI 연결

새 팀 프로젝트의 노션(홈 · 문서 6장 · 칸반 · 실험 기록 · 일일진행일지)을 정해진 틀로 깔고, 다 만든 뒤 문서끼리 맞는지 점검합니다. **게스트 팀원도 각자 AI로 같은 노션을 읽게** 내부 통합 토큰 연결 · 검증 스크립트 · 설정법 공지문까지 다룹니다.

- **이럴 때 켜집니다** — 팀 프로젝트를 시작할 때, 팀원이 "게스트라 노션 연결이 안 된다"고 할 때, 노션이 어지러워졌을 때
- **이렇게 말해 보세요** — *"노션 팀 공간 만들어 줘"*, *"팀원들도 Claude로 노션 읽게 해 줘"*, *"문서들 다 맞는지 점검해 봐"*
- **들어 있는 것** — `references/`(홈 틀 · 팀원 연결 절차 · 공지문), `scripts/verify_notion_integration.py`(토큰으로 무엇이 보이는지 확인)

#### 📝 `notion-publish` — md 원고 → 노션 정본

노션이 정본, 로컬 md는 원고입니다. 원고를 그대로 붙이면 표가 깨지고, 그 사이 노션에서 고친 내용과 그림이 사라집니다. **현재본을 먼저 읽고 합치고**, 표를 노션 형식으로 바꾸고, 통째 교체 전엔 백업하고, **팀원 문서는 고치지 않습니다.**

- **이렇게 말해 보세요** — *"이 부분 노션에 반영해"*, *"노션 문서 고쳐 줘"*

#### 🐙 `github-team-setup` — 첫날 깔아 두는 GitHub 협업 체계

조직 하나 + `AI` · `BE` · `FE` 저장소, 조직 공통 PR · 이슈 템플릿, **브랜치 이름(`feat/` · `fix/` · `docs/`…)으로 PR 라벨이 자동으로 붙는** 워크플로, [필수] · [권장] · [의견]으로 나눈 리뷰, squash 병합. 실제로 쓰던 파일을 [`templates/`](skills/github-team-setup/templates)에 그대로 넣었습니다.

- **이렇게 말해 보세요** — *"깃허브 세팅해 줘"*, *"PR 템플릿 만들고 라벨 자동으로 붙게"*
- **시작된 곳** — 낙상 감지 · 온점 · 눈치 · 스터디 매칭 서비스에서 매번 같은 것을 깔던 일

### 기록

#### 🧾 `contribution-audit` — 내가 한 것만 가려 문서로

팀 프로젝트를 서류에 쓸 때 가장 흔한 실수는 팀 결과를 내 것처럼 쓰는 것입니다. 커밋 · `git blame` · PR로 **최종 코드 중 내 줄**과 내 PR을 세고, "⚠️ 서류에 쓸 때 지킬 범위"와 "[확인 필요]"를 함께 남기는 문서 틀입니다.

- **이렇게 말해 보세요** — *"이 프로젝트 내 기여 정리해 줘"*, *"이거 서류에 써도 되는지 봐 줘"*
- **시작된 곳** — 프로젝트 13개를 이 틀로 정리

## 🔁 일하는 방식

<img src="docs/images/loop.svg" alt="1 맥락을 먼저 → 2 역할을 나눈다 → 3 직접 재 본다 → 4 남기고 스킬로" width="100%">

| 단계 | 하는 일 | 실제로 겪은 예 |
|---|---|---|
| **1. 맥락을 먼저** | AI가 작업 전에 읽는 안내 문서(CLAUDE.md)에 설계 결정 · 남은 과제 · 버린 설계를 적는다 | 남은 과제 목록에 *"AI 서버가 보내는 보호자 ID를 백엔드가 무시 중"* 을 적어 두고 추적하다 서버 간 계약을 정리 (낙상 감지) |
| **2. 역할을 나눈다** | AI끼리 영역을 나누고, AI는 PR까지만 올린다 | Claude는 3D 화면, Codex는 서버 · 모델 배포. 서로 찾은 문제는 고치지 않고 문서로 넘김 (눈치) |
| **3. 직접 재 본다** | AI의 예상은 재서 맞을 때만 쓴다. 측정 구간부터 고정한다 | *"캐시로 42초 절약"* → 실측 **20초 손해** (One Action) |
| **4. 남기고, 스킬로** | 확인한 것 · 틀린 이유를 문서에 쌓고, 반복되면 스킬로 만든다 | 대회 뒤 확인 절차를 `assumption-check`로 → 이후 프로젝트에서 계속 사용 |

### 👥 AI 두 개를 같이 쓸 때

<img src="docs/images/roles.svg" alt="Claude와 Codex가 COLLAB.md로 문제를 주고받고, 둘 다 PR을 올리면 사람이 결정하고 병합한다" width="100%">

AI 두 개를 동시에 쓰면 빠르지만, 서로의 코드를 고치기 시작하면 금방 엉킵니다. 그래서 **영역을 나누고, 상대 영역의 문제는 고치지 않고 적어 넘기게** 했습니다. 실제로 Codex가 화면 코드에서 *모델 학습 규격과 다른 이미지 전송* 을 찾아, 고칠 곳과 방법을 적어 Claude 쪽으로 넘겼습니다. → [`templates/COLLAB.md`](templates/COLLAB.md)

### 🌐 팀 전체가 AI로 일할 때

<img src="docs/images/team.svg" alt="GitHub·Notion·Slack 기록을 AI가 한 번에 읽고 대조한 뒤 작업, 게스트 팀원은 API 토큰으로 연결" width="100%">

팀원 모두 AI로 일하면 PR · 문서 · 대화가 빠르게 쌓입니다. 그래서 AI가 **GitHub · 노션 · 슬랙을 한 번에 읽고 대조한 뒤** 작업하게 했습니다.

- 슬랙에 `[작업 시작]` · `[작업 정리]`를 남기는 규칙을 두고, AI가 **팀원의 `[작업 시작]`을 먼저 확인**한 뒤 기록 초안을 쓰게 했습니다. 보내기 전엔 사람이 확인합니다. 같은 기능을 두 사람이 만드는 일이 두 번 생긴 뒤 만든 규칙이고, 그 뒤로 중복은 다시 없었습니다.
- 노션 무료 플랜이라 팀원을 게스트로 초대했는데, **게스트는 노션 AI 연결(MCP)이 막혀 있습니다.** 내부 통합 API 토큰으로 연결하는 절차를 `notion-team-hub` 스킬로 만들어 팀원들에게 공유했습니다.

## 📌 프로젝트에서 실제로 한 것

| 프로젝트 | AI와 일한 방식 | 링크 |
|---|---|---|
| **눈치** — 해 눈부심 판정과 3D 운전 시뮬레이터 (4인 · 팀장) | Claude · Codex 영역 분담과 COLLAB.md · 사람마다 갈리던 정답 라벨을 GPT · Claude · Gemini에 같은 기준으로 판정시켜 갈리는 사진을 다시 검토(AI 답으로 정답을 바꾸지는 않음) · GitHub · 노션 · 슬랙 한 번에 읽기 | [시뮬레이터](https://nunchi-drive.vercel.app) · [GitHub](https://github.com/Nunchi-ML) |
| **One Action** — 세 지역 자동 배포 · 고장 버전 자동 중단 (SoftBank 해커톤 최우수상) | AI 예상은 실측해서만 채택 · 확인한 결정을 CLAUDE.md에 쌓기 · 대회 뒤 `assumption-check`로 | [gitops](https://github.com/Crystal-SBHackathon2026/gitops) |
| **타운시그널** — 창업 지원금으로 동네 추천 (5인 · CTO) | Claude Code가 노션 명세를 직접 읽고 쓰게 연결 · 노션에 올릴 때 현재본을 먼저 읽고 팀원 문서는 고치지 않는 규칙 · AI 요약문 숫자는 DB 값에서만 · `notion-publish` · `slack-worklog` | [서비스](https://town-signal.vercel.app) |
| **NowWhat** — 할 일 우선순위 추천 (1인 · 3일) | 기획 문서 다섯 개를 AI가 먼저 읽는 정본으로 · 화면 · 기능 번호를 파일 이름에 써서 코드와 대조 · 서버를 띄워 확인하는 스킬(`api-verify`) · 버린 설계 기록 | [web](https://github.com/FAITRUEE/NowWhat_web) · [server](https://github.com/FAITRUEE/NowWhat_was) |
| **낙상 감지** — 소리로 낙상을 감지해 보호자에게 알림 (5인 · 팀장, 기업 과제) | CLAUDE.md의 남은 과제 목록으로 서버 간 계약 구멍을 추적해 정리 | — |

## 📄 양식

| 파일 | 내용 |
|---|---|
| [`templates/CLAUDE.md`](templates/CLAUDE.md) | AI가 먼저 읽는 프로젝트 안내 문서. 기준 문서(정본) · 설계 결정 · **🔴 버린 설계** · **남은 과제** · 확인 규칙 · 작업 기록 규칙 |
| [`templates/COLLAB.md`](templates/COLLAB.md) | AI 두 개가 같이 일할 때. 역할 표 · 공통 규칙(PR까지만, 상대 영역은 적어 넘기기) · 주고받는 요청 표 · 넘겨받기 |

## 🗂 저장소 구조

```text
ai-workflow/
├── .claude-plugin/
│   ├── marketplace.json      # /plugin marketplace add 로 읽히는 목록
│   ├── plugin.json           # 플러그인 정보
│   └── icon.png
├── skills/
│   ├── assumption-check/     # 확인하고 적기
│   ├── api-verify/           # 서버 띄워 실제 API로 확인
│   ├── oof-error-analysis/   # + scripts/analyze.py
│   ├── slack-worklog/        # [작업 시작] · [작업 정리] 초안
│   ├── notion-team-hub/      # + references/ · scripts/verify_notion_integration.py
│   ├── notion-publish/       # md 원고 → 노션 정본
│   ├── github-team-setup/    # + templates/ (labeler · PR · 이슈 템플릿)
│   └── contribution-audit/   # 내 기여만 가려 문서로
├── templates/                # CLAUDE.md · COLLAB.md 양식
└── docs/images/              # README 그림
```

각 `SKILL.md`는 맨 위에 `name`과 `description`만 둡니다. Claude는 `description`을 보고 언제 이 스킬을 켤지 판단하므로, **"이럴 때 쓴다"를 사용자가 실제로 하는 말로** 적었습니다.

## ⚠️ 설치 전에

- 스킬은 Claude에게 일하는 방식을 알려 주는 문서이고, 일부는 **스크립트를 실행합니다.** 설치 전에 `scripts/`를 한 번 읽어 보세요.
- `verify_notion_integration.py`는 노션 토큰을 **명령줄이 아니라 파일 경로로** 받습니다. 토큰 파일은 git 저장소 밖에 두세요. 쓰기 확인(`--write`)은 보드에 테스트 카드를 잠깐 만들었다 지우는 실제 변경입니다.

## 🚧 아직 못 하는 것

이 저장소의 규칙대로, 한계도 같은 자리에 적습니다.

- 스킬은 제가 겪은 상황에 맞춰져 있습니다. `oof-error-analysis`는 **분류** 문제용이고 회귀에는 쓰지 않습니다.
- `notion-team-hub`의 토큰 방식은 팀원 전원이 같은 봇 권한으로 붙어서 **노션 편집 기록에 누가 썼는지 남지 않습니다.** 담당 칸을 직접 채우는 규칙으로 보완합니다.
- One Action의 배포 시간 수치는 **구간마다 1회 측정**한 값입니다. 반복 측정한 평균이 아닙니다.

## 기여 · 라이선스

제 작업 방식을 모은 저장소라 새 스킬 PR은 받지 않지만, 써 보고 막힌 점은 이슈로 남겨 주시면 반영합니다. [MIT](LICENSE)
