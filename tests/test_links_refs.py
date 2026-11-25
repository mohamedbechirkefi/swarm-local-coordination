# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""M6: relative Markdown links and manuscript references resolve."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts/check_links.py")
check_links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_links)


def test_relative_links_resolve():
    n, problems = check_links.check_links()
    assert n > 0
    assert problems == []


def test_references_match_bib():
    n, problems = check_links.check_references()
    assert n == 8
    assert problems == []


def test_checker_detects_broken_link_and_anchor(tmp_path):
    (tmp_path / "a.md").write_text("# Title\n\n[x](missing.md) [y](a.md#nope) [z](a.md#title)\n")
    md = tmp_path / "a.md"
    old = check_links.ROOT
    check_links.ROOT = tmp_path
    try:
        n, problems = check_links.check_links([md])
    finally:
        check_links.ROOT = old
    assert n == 3
    assert len(problems) == 2


def test_checker_detects_uncited_bib_entry(tmp_path):
    bib = tmp_path / "r.bib"
    bib.write_text("@article{a2000,\n  author = {Alpha, A.},\n  year = {2000}\n}\n"
                   "@article{b2001,\n  author = {Beta, B.},\n  year = {2001}\n}\n")
    ms = tmp_path / "m.md"
    ms.write_text("Alpha (2000) said so [@zeta].\n\n# References\n\n- Alpha, A. (2000). T.\n")
    n, problems = check_links.check_references(ms, bib)
    assert n == 2
    assert any("@zeta" in p for p in problems)
    assert any("b2001" in p and "not cited" in p for p in problems)
    assert any("b2001" in p and "reference list" in p for p in problems)
