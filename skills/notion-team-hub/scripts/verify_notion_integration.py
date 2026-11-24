"""내부 통합 토큰이 실제로 무엇을 보고 무엇을 쓸 수 있는지 확인한다.

토큰을 인자로 받지 않고 '파일 경로'로 받는 이유: 토큰이 명령줄·대화 기록에
평문으로 남지 않게 하려는 것이다. 파일은 git 저장소 밖(세션 스크래치패드)에 둔다.

사용법:
    python verify_notion_integration.py <토큰파일> [홈페이지ID]
    python verify_notion_integration.py <토큰파일> <홈페이지ID> --write <할일보드DB_ID>

--write는 테스트 카드를 만들었다 바로 휴지통에 넣는다. 보드에 잠깐 카드가
보이는 실제 변경이므로 사용자에게 먼저 물어보고 쓴다.
"""
import json
import sys
import urllib.error
import urllib.request

API = "https://api.notion.com/v1"


def call(headers, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def title_of(obj):
    if obj["object"] == "page":
        for prop in obj.get("properties", {}).values():
            if prop.get("type") == "title":
                return "".join(t["plain_text"] for t in prop["title"]) or "(제목없음)"
        return "(제목없음)"
    return "".join(t["plain_text"] for t in obj.get("title", [])) or "(제목없음)"


def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        print(__doc__)
        return 1
    token = open(args[0], encoding="utf-8").read().strip()
    home_id = args[1] if len(args) > 1 and not args[1].startswith("--") else None
    write_db = args[args.index("--write") + 1] if "--write" in args else None

    h = {
        "Authorization": "Bearer " + token,
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    status, me = call(h, "GET", "/users/me")
    if status != 200:
        print("토큰이 유효하지 않습니다:", me.get("code"), me.get("message"))
        return 1
    bot = me.get("bot", {})
    print("통합 이름 :", me.get("name"))
    print("워크스페이스:", bot.get("workspace_name"))

    status, users = call(h, "GET", "/users?page_size=1")
    print("사용자 정보 읽기 권한:", "켜짐 (팀원 이메일 조회 가능)" if status == 200 else "꺼짐")

    if home_id:
        status, _ = call(h, "GET", "/pages/" + home_id.replace("-", ""))
        if status == 200:
            print("홈 페이지 조회 : OK")
        else:
            print("홈 페이지 조회 : 실패(http %s) — 페이지에 통합 연결이 안 된 상태입니다." % status)

    status, res = call(h, "POST", "/search", {"page_size": 100})
    results = res.get("results", [])
    pages = [r for r in results if r["object"] == "page"]
    dbs = [r for r in results if r["object"] == "database"]
    print("\n접근 가능: 페이지 %d, 데이터베이스 %d (더 있음=%s)"
          % (len(pages), len(dbs), res.get("has_more")))
    if not results:
        print("  → 0건입니다. 「프로젝트 홈」에 통합을 연결하는 단계가 빠졌습니다.")
    for d in dbs:
        print("  DB   ", title_of(d))
    for p in pages:
        print("  page ", title_of(p))

    if write_db:
        print("\n[쓰기 테스트]")
        status, db = call(h, "GET", "/databases/" + write_db.replace("-", ""))
        if status != 200:
            print("  DB를 못 읽습니다:", db.get("message"))
            return 1
        title_prop = next(n for n, p in db["properties"].items() if p["type"] == "title")
        status, page = call(h, "POST", "/pages", {
            "parent": {"database_id": write_db},
            "properties": {title_prop: {"title": [
                {"text": {"content": "🧪 [테스트] 연결 확인용 — 자동 삭제됨"}}]}},
        })
        print("  1) 카드 생성 (삽입)      : http", status)
        if status != 200:
            print("     ->", page.get("message"))
            return 1
        pid = page["id"]
        status, _ = call(h, "PATCH", "/blocks/%s/children" % pid, {"children": [
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [
                {"text": {"content": "쓰기 권한 확인용 문단입니다."}}]}}]})
        print("  2) 본문 블록 추가 (삽입) : http", status)
        status, r = call(h, "PATCH", "/pages/" + pid, {"archived": True})
        print("  3) 카드 삭제 (업데이트)  : http", status, " archived =", r.get("archived"))
        print("  테스트 카드는 휴지통에 있습니다. 완전 삭제는 노션 휴지통에서 하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
