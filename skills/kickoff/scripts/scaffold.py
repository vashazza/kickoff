#!/usr/bin/env python3
"""Kickoff scaffold: archetype별 폴더 구조와 기본 파일을 만든다.

원칙
- 기존 파일·폴더는 절대 덮어쓰지 않는다 (created / skipped 로 보고).
- .gitignore는 빠진 줄만 끝에 추가한다.
- HANDOFF.md는 만들지 않는다 (Claude가 constraints.yaml을 보고 작성).
- 압축 해제·문서 이동은 하지 않는다.

사용 예
  python3 scaffold.py ./MyComp --archetype competition --name MyComp --pkg mycomp --dry-run
  python3 scaffold.py ./MyComp --archetype competition --name MyComp --pkg mycomp
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"

# (상대경로, 설명). 경로가 /로 끝나면 폴더. {pkg}는 패키지명으로 치환.
LAYOUTS: dict[str, list[tuple[str, str]]] = {
    "competition": [
        ("docs/", "대회 문서 사본 (규칙·평가·데이터 명세)"),
        ("data/raw/", "원본 해제본. 수정 금지"),
        ("data/processed/", "전처리 산출물"),
        ("data/labels/", "자가 라벨 (생성 코드·프롬프트 버전과 함께)"),
        ("src/{pkg}/", "파이썬 패키지"),
        ("src/{pkg}/__init__.py", ""),
        ("scripts/", "실행 스크립트 (mock, eval, build_submit)"),
        ("scripts/labeling/", "자가 라벨링 코드·프롬프트 (재현 대상)"),
        ("submit/", "평가 서버용 제출물"),
        ("output/", "실험별 결과 output/exp_NN/"),
        ("logs/", ""),
        ("logs/research_log.md", "연구일지"),
        ("notebooks/", "탐색용"),
        ("constraints.yaml", "구조화된 제약"),
        ("CLAUDE.md", "HANDOFF 포인터 + 절대 규칙"),
        ("README.md", "개요·실행 방법"),
    ],
    "research": [
        ("docs/", "제안서·메모"),
        ("docs/papers/", "참고 논문"),
        ("data/raw/", "원본. 수정 금지"),
        ("data/processed/", "전처리 산출물"),
        ("data/external/", "외부 공개 데이터 (라이선스 기록)"),
        ("src/{pkg}/", "파이썬 패키지"),
        ("src/{pkg}/__init__.py", ""),
        ("configs/", "실험 설정 yaml"),
        ("scripts/", "학습·평가·분석 실행 스크립트"),
        ("output/", "실험별 결과 output/exp_NN/ (설정 스냅샷 포함)"),
        ("logs/", ""),
        ("logs/research_log.md", "연구일지"),
        ("notebooks/", "탐색·분석"),
        ("paper/figures/", "논문 그림"),
        ("paper/tables/", "논문 표"),
        ("constraints.yaml", "구조화된 제약"),
        ("CLAUDE.md", "HANDOFF 포인터 + 절대 규칙"),
        ("README.md", "개요·실행 방법"),
    ],
}

GITIGNORE_COMMON = [
    "# kickoff",
    "data/raw/",
    "data/*.zip",
    "data/*.tar*",
    "output/",
    "__pycache__/",
    "*.pyc",
    ".ipynb_checkpoints/",
    ".venv/",
    ".env",
    "*.pt",
    "*.ckpt",
    "*.safetensors",
]
GITIGNORE_EXTRA = {
    "competition": ["submit/*.zip"],
    "research": ["wandb/", "mlruns/", "paper/*.pdf"],
}

# 파일 경로 → 템플릿 위치
FILE_TEMPLATES = {
    "logs/research_log.md": "common/research_log.md",
    "CLAUDE.md": "common/CLAUDE.md",
    "README.md": "common/README.md",
    "constraints.yaml": "{archetype}/constraints.yaml",
}


def to_pkg(name: str) -> str:
    pkg = re.sub(r"[^0-9a-zA-Z_]+", "_", name).strip("_").lower()
    if not pkg or pkg[0].isdigit():
        pkg = "proj_" + pkg
    return pkg


def render(text: str, name: str) -> str:
    return text.replace("{{NAME}}", name)


def build_tree(project: str, entries: list[tuple[str, str]]) -> str:
    """레이아웃을 tree 형태 문자열로 (HANDOFF §폴더 구조에 붙여넣기용)."""
    lines = [f"{project}/", "├── HANDOFF.md              # Claude Code가 가장 먼저 읽는 문서"]
    shown = []
    for path, desc in entries:
        if path.endswith("__init__.py") or (path.endswith("/") and not desc):
            continue
        shown.append((path, desc))
    for i, (path, desc) in enumerate(shown):
        last = i == len(shown) - 1
        branch = "└── " if last else "├── "
        label = branch + path
        lines.append(f"{label:<28}# {desc}" if desc else label)
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir")
    ap.add_argument("--archetype", required=True, choices=sorted(LAYOUTS))
    ap.add_argument("--name", help="프로젝트 표시 이름 (기본: 폴더명)")
    ap.add_argument("--pkg", help="파이썬 패키지명 (기본: 이름에서 생성)")
    ap.add_argument("--dry-run", action="store_true", help="만들 것만 출력")
    args = ap.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    name = args.name or root.name
    pkg = args.pkg or to_pkg(name)
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", pkg):
        print(f"error: 패키지명이 올바르지 않음: {pkg!r}", file=sys.stderr)
        return 2

    entries = [(p.replace("{pkg}", pkg), d) for p, d in LAYOUTS[args.archetype]]
    created, skipped = [], []

    if not args.dry_run:
        root.mkdir(parents=True, exist_ok=True)

    for rel, _desc in entries:
        target = root / rel
        if rel.endswith("/"):
            if target.exists():
                skipped.append(rel)
                continue
            created.append(rel)
            if not args.dry_run:
                target.mkdir(parents=True, exist_ok=True)
            continue

        if target.exists():
            skipped.append(rel)
            continue
        created.append(rel)
        if args.dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        tmpl = FILE_TEMPLATES.get(rel)
        if tmpl:
            src = TEMPLATES / tmpl.format(archetype=args.archetype)
            target.write_text(render(src.read_text(encoding="utf-8"), name), encoding="utf-8")
        else:
            target.write_text("", encoding="utf-8")

    # 빈 폴더 보존용 .gitkeep (git에서 무시되는 data/raw, output 제외)
    if not args.dry_run:
        for rel, _ in entries:
            if rel.endswith("/") and rel not in ("data/raw/", "output/"):
                d = root / rel
                if d.is_dir() and not any(d.iterdir()):
                    (d / ".gitkeep").write_text("", encoding="utf-8")

    # .gitignore: 빠진 줄만 추가
    gi = root / ".gitignore"
    wanted = GITIGNORE_COMMON + GITIGNORE_EXTRA[args.archetype]
    existing = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
    missing = [l for l in wanted if l not in existing]
    if missing and not args.dry_run:
        with gi.open("a", encoding="utf-8") as f:
            if existing and existing[-1].strip():
                f.write("\n")
            f.write("\n".join(missing) + "\n")

    mode = "DRY-RUN" if args.dry_run else "DONE"
    print(f"[{mode}] {root}  (archetype={args.archetype}, name={name}, pkg={pkg})")
    print(f"created ({len(created)}):")
    for c in created:
        print(f"  + {c}")
    print(f"skipped, already exists ({len(skipped)}):")
    for s in skipped:
        print(f"  = {s}")
    real_missing = [l for l in missing if not l.startswith("#")]
    print(f".gitignore: {'+' + str(len(real_missing)) + ' lines' if real_missing else 'no change'}")
    print("\n# HANDOFF.md 폴더 구조 섹션용 tree:")
    print(build_tree(name, entries))
    print("\n다음: HANDOFF.md 작성 (templates/%s/HANDOFF.md 구조 사용)" % args.archetype)
    return 0


if __name__ == "__main__":
    sys.exit(main())
