"""작업 폴더에서 정리 후보를 찾아 크기순으로 보여 준다. 아무것도 지우지 않는다.

사용법:
    python scan.py <폴더> [--min-kb 0] [--unused-images]
    python scan.py <폴더> --docs        # 문서 목록과 '버전만 다른 같은 문서' 묶음

--unused-images: 폴더 안 텍스트 파일(.md .py .html .js .ts .json .css .txt)
                 어디에서도 이름이 나오지 않는 이미지를 '확인 필요'로 추가한다.
"""
import argparse
import os
import re
import sys

SKIP_DIRS = {".git"}
JUNK_DIRS = {
    ".playwright-mcp": "AI 작업 찌꺼기",
    "_workspace": "AI 작업 찌꺼기",
    "__pycache__": "캐시·빌드 출력",
    ".pytest_cache": "캐시·빌드 출력",
    ".mypy_cache": "캐시·빌드 출력",
    "node_modules": "캐시·빌드 출력",
    ".next": "캐시·빌드 출력",
    "dist": "캐시·빌드 출력",
    "build": "캐시·빌드 출력",
}
COPY_PAT = re.compile(r"(_old|_bak|_backup|_v\d+|복사본|사본| - copy|\(\d\))(\.[^.]+)?$", re.I)
JUNK_EXT = {".bak", ".tmp", ".log", ".orig"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
TEXT_EXT = {".md", ".py", ".html", ".htm", ".js", ".ts", ".tsx", ".json", ".css", ".txt", ".yml", ".yaml"}


def dir_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def scan(top, find_unused):
    found = []  # (분류, 크기, 경로)
    images, texts = [], []
    for root, dirs, files in os.walk(top):
        keep = []
        for d in dirs:
            if d in SKIP_DIRS:
                continue
            p = os.path.join(root, d)
            if d in JUNK_DIRS:
                found.append((JUNK_DIRS[d], dir_size(p), p + os.sep))
            else:
                keep.append(d)
        dirs[:] = keep
        for f in files:
            p = os.path.join(root, f)
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            stem, ext = os.path.splitext(f)
            ext = ext.lower()
            if f.startswith("~$"):
                found.append(("열려 있는 파일(건드리지 않음)", size, p))
            elif ext in JUNK_EXT or COPY_PAT.search(f):
                found.append(("사본·이전본", size, p))
            elif ext in IMG_EXT:
                images.append((size, p, f))
            if ext in TEXT_EXT and size < 5_000_000:
                texts.append(p)

    if find_unused and images:
        corpus = []
        for t in texts:
            try:
                with open(t, encoding="utf-8", errors="ignore") as fh:
                    corpus.append(fh.read())
            except OSError:
                pass
        blob = "\n".join(corpus)
        for size, p, name in images:
            if name not in blob and os.path.splitext(name)[0] not in blob:
                found.append(("안 쓰는 그림(확인 필요)", size, p))
    return found


DOC_EXT = {".md", ".txt", ".docx", ".hwp", ".pdf", ".pptx"}
VERSION_PAT = re.compile(
    r"(_?v\d+(\.\d+)*|_?최종\d*|_?final\d*|_?수정\d*|_?\d{4}-?\d{2}-?\d{2}|\(\d+\)|_?사본|_?복사본| - copy|_?old|_?new|_?\d+차)",
    re.I,
)


def docs(top):
    """문서를 폴더별로 나열하고, 버전 표시만 다른 같은 문서를 묶는다."""
    import datetime
    rows, families = [], {}
    for root, dirs, files in os.walk(top):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and d not in JUNK_DIRS]
        for f in files:
            stem, ext = os.path.splitext(f)
            if ext.lower() not in DOC_EXT or f.startswith("~$"):
                continue
            p = os.path.join(root, f)
            try:
                st = os.stat(p)
            except OSError:
                continue
            rows.append((root, f, st.st_size, st.st_mtime))
            key = (root, VERSION_PAT.sub("", stem).strip(" _-").lower(), ext.lower())
            families.setdefault(key, []).append((st.st_mtime, f))
    print(f"문서 {len(rows)}개\n")
    cur = None
    for root, f, size, mt in sorted(rows):
        if root != cur:
            cur = root
            print(f"## {os.path.relpath(root, top)}")
        day = datetime.datetime.fromtimestamp(mt).strftime("%m-%d")
        print(f"  {day}  {human(size):>9}  {f}")
    multi = [(k, v) for k, v in families.items() if len(v) > 1]
    if multi:
        print("\n## 버전만 다른 같은 문서 — 정본 하나를 정하고 나머지는 합치거나 보관")
        for (root, base, _), v in sorted(multi):
            v.sort(reverse=True)
            names = " / ".join(f"{n}{' (최신)' if i == 0 else ''}" for i, (_, n) in enumerate(v))
            print(f"  {os.path.relpath(root, top)}: {names}")


def main():
    try:  # Windows 콘솔(cp949)에서도 깨지지 않게
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--min-kb", type=int, default=0)
    ap.add_argument("--unused-images", action="store_true")
    ap.add_argument("--docs", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir(a.folder):
        sys.exit(f"폴더가 아닙니다: {a.folder}")
    if a.docs:
        docs(a.folder)
        return

    items = [x for x in scan(a.folder, a.unused_images) if x[1] >= a.min_kb * 1024]
    if not items:
        print("정리 후보 없음")
        return
    groups = {}
    for cat, size, p in items:
        groups.setdefault(cat, []).append((size, p))
    total = sum(s for _, s, _ in items)
    print(f"정리 후보 {len(items)}개 · 합계 {human(total)}  (아무것도 지우지 않았습니다)\n")
    n = 1
    for cat, rows in sorted(groups.items(), key=lambda kv: -sum(s for s, _ in kv[1])):
        rows.sort(reverse=True)
        print(f"## {cat} — {len(rows)}개 · {human(sum(s for s, _ in rows))}")
        for size, p in rows[:30]:
            print(f"  [{n}] {human(size):>9}  {os.path.relpath(p, a.folder)}")
            n += 1
        if len(rows) > 30:
            print(f"  … 외 {len(rows) - 30}개")
        print()


if __name__ == "__main__":
    main()
