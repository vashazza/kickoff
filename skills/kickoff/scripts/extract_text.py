#!/usr/bin/env python3
"""규칙·명세 문서에서 텍스트를 뽑는다 (읽기 전용, 원본은 건드리지 않음).

지원: .pdf .hwpx .hwp .docx .html/.htm .txt .md .csv .json .yaml
- 표준 라이브러리만으로 동작하는 형식: hwpx, docx, html, 텍스트류
- pdf: pdftotext(poppler) → pypdf 순으로 시도
- hwp(구형 바이너리): hwp5txt(pyhwp) 가 있으면 사용, 없으면 안내만 출력

사용 예
  python3 extract_text.py docs/*.pdf 규칙.hwpx --out /tmp/kickoff_text
"""
from __future__ import annotations

import argparse
import html.parser
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

TEXT_EXT = {".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".tsv"}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _xml_paragraphs(xml_bytes: bytes, para_tag: str, text_tag: str, tab_tag: str | None = None) -> list[str]:
    root = ET.fromstring(xml_bytes)
    out = []
    for p in root.iter():
        if _local(p.tag) != para_tag:
            continue
        parts = []
        for el in p.iter():
            t = _local(el.tag)
            if t == text_tag and el.text:
                parts.append(el.text)
            elif tab_tag and t == tab_tag:
                parts.append("\t")
        line = "".join(parts).strip()
        if line:
            out.append(line)
    return out


def from_hwpx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        sections = sorted(
            (n for n in z.namelist() if re.match(r"Contents/section\d+\.xml$", n)),
            key=lambda n: int(re.search(r"(\d+)", n.rsplit("/", 1)[-1]).group(1)),
        )
        if not sections:
            raise ValueError("hwpx 안에 Contents/section*.xml 이 없음")
        lines: list[str] = []
        for s in sections:
            lines += _xml_paragraphs(z.read(s), "p", "t", "tab")
    return "\n".join(lines)


def from_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        return "\n".join(_xml_paragraphs(z.read("word/document.xml"), "p", "t", "tab"))


class _HTMLText(html.parser.HTMLParser):
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "table"}

    def __init__(self):
        super().__init__()
        self.buf: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in self.BLOCK:
            self.buf.append("\n")
        elif tag in ("td", "th"):
            self.buf.append(" | ")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def from_html(path: Path) -> str:
    p = _HTMLText()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    text = "".join(p.buf)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def from_pdf(path: Path) -> str:
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as e:
        raise RuntimeError("pdftotext도 pypdf도 없음 → `pip install pypdf` 후 재시도") from e
    reader = PdfReader(str(path))
    pages = [f"--- p.{i + 1} ---\n{(pg.extract_text() or '').strip()}" for i, pg in enumerate(reader.pages)]
    text = "\n\n".join(pages)
    if len(re.sub(r"\s|--- p\.\d+ ---", "", text)) < 50:
        raise RuntimeError("텍스트가 거의 없음 — 스캔본일 수 있음 (OCR 필요)")
    return text


def from_hwp(path: Path) -> str:
    if shutil.which("hwp5txt"):
        r = subprocess.run(["hwp5txt", str(path)], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    raise RuntimeError("구형 .hwp — `pip install pyhwp` 후 재시도하거나, 한글에서 hwpx/pdf로 저장해 달라고 요청")


HANDLERS = {
    ".hwpx": from_hwpx,
    ".docx": from_docx,
    ".html": from_html,
    ".htm": from_html,
    ".pdf": from_pdf,
    ".hwp": from_hwp,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", required=True, help="추출 텍스트를 둘 폴더 (scratch 권장)")
    args = ap.parse_args()

    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for f in args.files:
        path = Path(f)
        ext = path.suffix.lower()
        try:
            if not path.is_file():
                raise FileNotFoundError("파일 없음")
            if ext in TEXT_EXT:
                text = path.read_text(encoding="utf-8", errors="replace")
            elif ext in HANDLERS:
                text = HANDLERS[ext](path)
            else:
                raise ValueError(f"지원하지 않는 형식 {ext}")
            dest = out / (path.name + ".txt")
            dest.write_text(text, encoding="utf-8")
            print(f"OK   {path}  →  {dest}  ({len(text):,} chars)")
            ok += 1
        except Exception as e:  # noqa: BLE001 — 파일별로 계속 진행
            print(f"FAIL {path}  ({e})")
            fail += 1
    print(f"\n{ok} ok, {fail} failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
