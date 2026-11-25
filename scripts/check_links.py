# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Check relative Markdown links and manuscript references (M6).

1. Every relative link or image target in a tracked Markdown file resolves to
   an existing file, and every ``#anchor`` resolves to a heading of the target
   (GitHub-style slugs). External links (http, https, mailto) are not fetched.
2. Every entry of ``research/paper/references.bib`` is cited in the body of
   the manuscript and listed in its reference list, every reference-list entry
   has a bib entry, and every pandoc citation key (``[@key]``) resolves.

    .venv/bin/python scripts/check_links.py      # exit status 1 on any problem
"""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^(```|~~~)")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout.split()
    return [ROOT / p for p in out if "node_modules/" not in p]


def strip_code(text: str) -> str:
    lines, inside = [], False
    for line in text.splitlines():
        if FENCE.match(line.strip()):
            inside = not inside
            lines.append("")
            continue
        lines.append("" if inside or line.startswith("    ") else re.sub(r"`[^`]*`", "", line))
    return "\n".join(lines)


def slug(heading: str) -> str:
    h = re.sub(r"[`*_]|<[^>]+>", "", heading.strip()).lower()
    h = unicodedata.normalize("NFKC", h)
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    seen: dict[str, int] = {}
    out = set()
    for line in strip_code(md.read_text(encoding="utf-8")).splitlines():
        m = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not m:
            continue
        s = slug(m.group(1))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    return out


def check_links(files: list[Path] | None = None) -> tuple[int, list[str]]:
    problems: list[str] = []
    count = 0
    for md in files if files is not None else tracked_markdown():
        for target in LINK.findall(strip_code(md.read_text(encoding="utf-8"))):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue  # external (http, https, mailto, ...)
            count += 1
            path, _, frag = target.partition("#")
            dest = (md.parent / path).resolve() if path else md
            rel = md.relative_to(ROOT)
            if not dest.exists():
                problems.append(f"{rel}: missing target {target}")
            elif frag and dest.suffix == ".md" and frag not in anchors(dest):
                problems.append(f"{rel}: missing anchor {target}")
    return count, problems


def bib_entries(bib: Path) -> dict[str, tuple[str, str]]:
    text = bib.read_text(encoding="utf-8")
    out = {}
    for key, body in re.findall(r"@\w+\{([^,]+),(.*?)\n\}", text, re.S):
        author = re.search(r"author\s*=\s*\{(.+?)\},?\n", body).group(1)
        surname = author.split(" and ")[0].split(",")[0]
        surname = re.sub(r"\{\\.\}|[{}\\']", "", surname).strip()
        year = re.search(r"year\s*=\s*\{(\d{4})\}", body).group(1)
        out[key.strip()] = (surname, year)
    return out


def check_references(manuscript: Path | None = None, bib: Path | None = None) -> tuple[int, list[str]]:
    manuscript = manuscript or ROOT / "research/paper/manuscript.md"
    bib = bib or ROOT / "research/paper/references.bib"
    text = manuscript.read_text(encoding="utf-8")
    body, _, refs = text.partition("\n# References")
    refs = refs.split("\n# ", 1)[0]
    entries = bib_entries(bib)
    problems = []
    for key in re.findall(r"@([A-Za-z][\w:-]*)", re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "", body)):
        if key not in entries:
            problems.append(f"citation key @{key} not in references.bib")
    ref_items = [line for line in refs.splitlines() if line.startswith("- ")]
    for key, (surname, year) in entries.items():
        if not re.search(rf"{re.escape(surname)}\b[^()]*?\(?{year}\)?", body):
            problems.append(f"bib entry {key} ({surname} {year}) not cited in the body")
        if not any(it[2:].startswith(surname) and f"({year})" in it for it in ref_items):
            problems.append(f"bib entry {key} ({surname} {year}) missing from the reference list")
    for it in ref_items:
        if not any(it[2:].startswith(s) and f"({y})" in it for s, y in entries.values()):
            problems.append(f"reference-list entry without bib entry: {it[:60]}")
    return len(entries), problems


def main() -> int:
    n_links, p1 = check_links()
    n_bib, p2 = check_references()
    for p in p1 + p2:
        print("FAIL", p)
    print(f"relative links checked: {n_links}, problems: {len(p1)}")
    print(f"bib entries checked: {n_bib}, problems: {len(p2)}")
    print("LINK-CHECK PASS" if not (p1 or p2) else "LINK-CHECK FAIL")
    return 1 if (p1 or p2) else 0


if __name__ == "__main__":
    sys.exit(main())
