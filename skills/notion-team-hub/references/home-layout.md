# 「프로젝트 홈」 레이아웃 템플릿

2026-10-27에 정리한 모양. 그 전 버전은 상단에 박스가 세 개 쌓이고, 영역 카드가
3열 + 2열로 나뉘어 너비가 어긋나고, 같은 DB가 위아래로 중복되고, 하단에 전체폭
연결 보기 4개가 세로로 늘어져서 "어지럽다"는 말을 들었다. 아래가 그걸 고친 모양이다.

고친 원리 네 가지. 새 프로젝트에서도 이 원리를 지키면 된다.

1. **상단 박스는 가로로.** 세로로 쌓으면 첫 화면이 전부 박스가 된다. 현황과 링크를 2열로 나눈다.
2. **영역 카드는 열 수를 통일한다.** 3열 + 2열로 나누면 두 번째 줄 너비가 1.5배가 되어 격자가 깨진다.
   영역이 5개면 6번째 칸을 만들어(Records 등) 3×2로 맞춘다. `ratio`를 명시해 둔다.
3. **DB는 한 번만.** 영역 카드에 원본 링크를 두면 하단 연결 보기와 중복된다. 위에는 원본, 아래는 보기로 역할을 나눈다.
4. **연결 보기는 탭으로 묶는다.** 전체폭 보기 4개를 세로로 쌓으면 페이지가 끝없이 길어진다.

## 전체 구조

```
커버(사진) + 아이콘
┌─────────────────┬─────────────────┐
│ 📅 진행 현황      │ 🔗 바로가기       │   ← columns ratio 50/50
└─────────────────┴─────────────────┘
> 🤝 협업 흐름 한 줄 (회색 인용)
▸ 📝 문서 작성 규칙 (토글 h3, 접힘)
───────────────────────────────────
## 📂 영역별 문서
┌────────┬────────┬────────┐
│ Plan   │ Data   │ Model  │          ← columns ratio 33/33/33
├────────┼────────┼────────┤
│Frontend│Backend │Records │          ← 같은 ratio로 한 줄 더
└────────┴────────┴────────┘
───────────────────────────────────
## 🗂️ 보드 · 기록 모아보기
[📋 칸반][📈 진행 현황][🏆 리더보드][📝 일지]   ← tabs
```

## 그대로 쓸 수 있는 틀

하위 페이지·DB는 이미 있는 것의 `<page url>` / `<database url>` 태그를 fetch해서
그대로 옮긴다. 새로 만들 때만 url 없이 쓴다.

```
<columns>
<column ratio="50">
<callout icon="📅" color="blue_bg">
<b>진행 현황</b>

- <b>기간</b> · MM/DD(요일) ~ MM/DD(요일) · 평일 N일
- <b>현재 단계</b> · 0. 준비
- <b>주제 · 타깃</b> · 미정
- <b>팀</b> · PM · FE · BE / 데이터 A · B / AI A · B
</callout>
</column>
<column ratio="50">
<callout icon="🔗" color="gray_bg">
<b>바로가기</b>

- 🐙 <b>깃허브</b> · [조직명](https://github.com/...)
- 💬 <b>슬랙</b> · 미정
- 🎨 <b>프론트 배포</b> · 미정
- ⚙️ <b>API 문서 (Swagger)</b> · 미정
</callout>
</column>
</columns>

<quote color="gray">
🤝 문서로 기준을 맞추고 → 칸반으로 매일 공유하고 → 슬랙으로 착수를 알리고 → 이슈 · PR로 작업하고 → 끝나면 정리해서 공유한다
</quote>

<toggle heading="h3" color="yellow">
📝 문서 작성 규칙

문서를 고칠 때마다 <b>버전을 올리고</b> 문서 맨 아래 「변경 이력」에 날짜 · 작성자 · 수정 사항을 한 줄 남겨 주세요. (v0.1 → v0.2 …, 팀 확정 시 v1.0)
</toggle>

---

## 📂 영역별 문서

<columns>
<column ratio="33">
<h3 color="red">
Plan
</h3>

<callout icon="📌" color="gray_bg">
<span color="gray">기획 · PM</span>

<page url="...">프로젝트 수행 계획</page>

<page url="...">기능명세서</page>
</callout>
</column>
<column ratio="33">
<h3 color="blue">
Data
</h3>
...
</column>
<column ratio="33">
<h3 color="green">
Model
</h3>
...
</column>
</columns>
```

두 번째 줄도 같은 `ratio="33"` 3열로 Web / Report / Records.
Records 칸에는 DB 원본 링크 세 개를 넣는다(`<database url=... inline="false">`).

색: Plan red · Data blue · Model green · Web orange · Report purple · Records gray.
(영역 이름은 프로젝트에 맞춘다. 2026-10 ML 프로젝트 기준 Plan / Data / Model / Web / Report / Records.
중요한 건 이름이 아니라 6칸을 3×2로 꽉 채우는 것이다.)
제목은 `<h3>`(영어 한 단어), 바로 아래 회색 콜아웃 안에 `<span color="gray">영역 · 담당역할</span>`.

## 탭 부분

```
---

## 🗂️ 보드 · 기록 모아보기

<tabs>
<tab icon="📋">
칸반 보드

<callout icon="💬" color="gray_bg">
데일리 스크럼에서 이 보드를 봅니다. <b>In Progress는 1인당 2장까지.</b>
</callout>

<database url="..." data-source-url="collection://..." inline="true"></database>
</tab>
<tab icon="📈">
진행 현황

<database url="..." data-source-url="collection://..." inline="true"></database>
</tab>
</tabs>
```

탭 제목은 여는 태그 바로 다음 줄의 본문이고, 자식은 빈 줄 뒤에 온다.
이미 있는 연결 보기를 탭 안으로 옮길 때는 **보기의 url을 그대로** 써야 설정(칸반·차트 모양)이 유지된다.

## 커버 사진

노션 기본 커버(`https://www.notion.so/images/page-cover/gradients_8.png` 등)도 되고,
Unsplash 직접 주소도 된다: `https://images.unsplash.com/photo-<id>?w=1920&q=85&auto=format&fit=crop`.

커버는 가로로 길고 납작하게 잘리고 그 위에 아이콘과 제목이 얹힌다. 그래서 **무늬가 적고 어두운 쪽**이
글씨가 또렷하다. 고를 때는 후보를 `?w=760&h=200&fit=crop`으로 열어 커버 비율에서 어떻게 보이는지
먼저 확인한다. 복잡한 패턴·알록달록한 사진은 제목이 묻힌다.
