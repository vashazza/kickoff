#!/usr/bin/env python3
"""연구일지(logs/research_log.md)에 실험 항목을 추가/갱신하고 상단 요약표를 맞춘다.

- 최신 항목이 위로 온다 (ENTRIES:START 바로 아래에 삽입).
- 요약표도 최신 행이 위.
- 실험 번호는 기본 자동 (기존 최대 + 1). exp_00은 프로젝트 세팅용.
- 같은 번호가 이미 있으면 거부, --update 를 주면 그 항목과 요약 행을 교체.
- 로그 파일이 없으면 템플릿으로 새로 만든다.

사용 예
  python3 log_entry.py --log logs/research_log.md --title "규칙만 베이스라인" \
      --metric "Macro-F1 0.412" --summary "게이팅+규칙만, LLM off" --body-file /tmp/entry.md --mkdir output
  python3 log_entry.py --log logs/research_log.md --exp 3 --update --metric "Macro-F1 0.455" --body-file /tmp/entry.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

S_START, S_END = "<!-- SUMMARY:START -->", "<!-- SUMMARY:END -->"
E_START, E_END = "<!-- ENTRIES:START -->", "<!-- ENTRIES:END -->"
TABLE_HEAD = "| 실험 | 날짜 | 주 지표 | 한 줄 요약 |\n|---|---|---|---|"

LOG_TEMPLATE = f"""# 연구일지 — {{name}}

> 항목 추가는 `log_entry.py`(research-log 스킬)로. 최신 항목이 위에 오고, 아래 요약표는 자동 갱신된다.
> 마커 주석(`<!-- ... -->`)은 지우지 말 것.

## 요약

{S_START}
{TABLE_HEAD}
{S_END}

---

{E_START}
{E_END}
"""

BODY_SKELETON = """**목적**:
**변경 사항**:
**설정**:
**결과**:
| 지표 | 값 |
|---|---|
| {metric_name} | {metric_value} |
| 실행 시간 | |

**관찰**:
**다음 할 일**:
**산출물**: {artifact}
"""


def cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()


def exp_id(n: int) -> str:
    return f"exp_{n:02d}"


def section(text: str, start: str, end: str) -> tuple[int, int]:
    a, b = text.find(start), text.find(end)
    if a < 0 or b < 0 or b < a:
        raise SystemExit(f"error: 마커 {start} / {end} 를 찾을 수 없음. 로그 파일 상단 구조를 확인하세요.")
    return a + len(start), b


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", required=True)
    ap.add_argument("--exp", default="auto", help="번호 (예: 3, 03, exp_03) 또는 auto")
    ap.add_argument("--title", help="한 줄 제목 (새 항목이면 필수)")
    ap.add_argument("--metric", help='주 지표, 예: "Macro-F1 0.512"')
    ap.add_argument("--summary", help="요약표용 한 줄 (기본: 제목)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--body-file", help="본문 마크다운 파일")
    g.add_argument("--body", help="본문 문자열")
    ap.add_argument("--date", help="기본: 오늘 (갱신 시에는 기존 날짜 유지)")
    ap.add_argument("--update", action="store_true", help="같은 번호 항목을 교체")
    ap.add_argument("--mkdir", metavar="OUTPUT_ROOT", help="OUTPUT_ROOT/exp_NN 폴더 생성")
    ap.add_argument("--name", help="새 로그 파일 생성 시 프로젝트 이름")
    args = ap.parse_args()

    log = Path(args.log)
    if not log.exists():
        name = args.name or log.resolve().parent.parent.name
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(LOG_TEMPLATE.format(name=name), encoding="utf-8")
        print(f"created {log}")
    text = log.read_text(encoding="utf-8")

    s0, s1 = section(text, S_START, S_END)
    table = text[s0:s1]
    existing = sorted({int(m) for m in re.findall(r"^\|\s*exp_(\d+)\s*\|", table, flags=re.M)})

    if args.exp == "auto":
        if args.update:
            raise SystemExit("error: --update 에는 번호를 지정하세요")
        n = (max(existing) + 1) if existing else 1
    else:
        m = re.fullmatch(r"(?:exp_)?(\d+)", args.exp.strip())
        if not m:
            raise SystemExit(f"error: 번호 형식이 잘못됨: {args.exp}")
        n = int(m.group(1))
    eid = exp_id(n)

    if n in existing and not args.update:
        raise SystemExit(f"error: {eid} 가 이미 있음. 결과를 갱신하려면 --update")
    if args.update and n not in existing:
        raise SystemExit(f"error: {eid} 가 없어서 갱신할 수 없음")

    old_entry = re.search(rf"<!-- {eid}:START -->\n(.*?)<!-- {eid}:END -->\n?", text, flags=re.S)
    old_title = None
    if old_entry:
        h = re.search(rf"^## \[[^\]]*\] {eid} — (.+)$", old_entry.group(1), flags=re.M)
        old_title = h.group(1).strip() if h else None
    title = args.title or old_title
    if not title:
        raise SystemExit("error: --title 이 필요함")
    old_cells = None
    for line in table.splitlines():
        if re.match(rf"^\|\s*{eid}\s*\|", line):
            # 이스케이프되지 않은 | 로 분리: ['', exp, date, metric, summary, '']
            old_cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)][1:-1]
    keep = args.update and old_cells and len(old_cells) == 4
    summary = args.summary or (old_cells[3] if keep else None) or title
    args.date = args.date or (old_cells[1] if keep else None) or dt.date.today().isoformat()
    args.metric = args.metric or (old_cells[2] if keep else None) or "-"

    artifact = ""
    if args.mkdir:
        rel = os.path.relpath(Path(args.mkdir) / eid, log.resolve().parent.parent)
        artifact = (rel if not rel.startswith("..") else str(Path(args.mkdir) / eid)) + "/"
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8").strip() + "\n"
    elif args.body:
        body = args.body.strip() + "\n"
    elif old_entry:
        # 본문 없이 갱신 → 기존 본문 유지 (요약표의 지표/요약만 바뀜)
        body = re.sub(r"^## .*\n+", "", old_entry.group(1), count=1).strip() + "\n"
    else:
        mname, _, mval = args.metric.partition(" ")
        body = BODY_SKELETON.format(metric_name=mname or "주 지표", metric_value=mval, artifact=artifact)

    entry = f"<!-- {eid}:START -->\n## [{args.date}] {eid} — {title}\n\n{body}\n<!-- {eid}:END -->\n"
    row = f"| {eid} | {args.date} | {cell(args.metric)} | {cell(summary)} |"

    # 요약표 갱신: 헤더 유지, 같은 번호 행 제거 후 맨 위에 삽입, 번호 내림차순 정렬
    rows = [l for l in table.strip().splitlines() if re.match(r"^\|\s*exp_\d+\s*\|", l)]
    rows = [r for r in rows if not re.match(rf"^\|\s*{eid}\s*\|", r)] + [row]
    rows.sort(key=lambda r: -int(re.match(r"^\|\s*exp_(\d+)", r).group(1)))
    new_table = "\n" + TABLE_HEAD + "\n" + "\n".join(rows) + "\n"
    text = text[:s0] + new_table + text[s1:]

    # 항목 갱신
    if old_entry:
        text = text.replace(old_entry.group(0), entry, 1)
    else:
        e0, _ = section(text, E_START, E_END)
        text = text[:e0] + "\n" + entry + text[e0:]
    text = re.sub(r"\n{3,}", "\n\n", text)
    log.write_text(text, encoding="utf-8")

    if args.mkdir:
        d = Path(args.mkdir) / eid
        d.mkdir(parents=True, exist_ok=True)
        print(f"mkdir {d}")
    print(f"{'updated' if old_entry else 'added'} {eid} — {title}")
    print(eid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
