# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""M5 consistency test (master prompt 11.6, M5): the demo shows the same numbers as the paper.

1. Re-running the export in memory gives exactly the committed demo/public/data/results.json.
2. Every display and interval_display string of an experiment or post hoc estimate appears
   verbatim in research/paper/manuscript.md, and so does the "estimate [interval]" pair.
   Documented exceptions:
   - per-cell values (key per_cell) are not printed in the manuscript; they are checked
     against the generated per-cell table of research/experiments/EXP-002/report.md, row by row;
   - the EXP-001 smoke value is printed "-0.480, SD 0.059", so its pair is checked in that form.
3. Every decimal number in the public-facing texts (README, articles, demo README) appears in
   the manuscript, the EXP-002 report or the supplementary material.
"""

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = (ROOT / "research/paper/manuscript.md").read_text(encoding="utf-8")
REPORT002 = (ROOT / "research/experiments/EXP-002/report.md").read_text(encoding="utf-8")


def _export():
    spec = importlib.util.spec_from_file_location("export_demo_data", ROOT / "scripts" / "export_demo_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _committed() -> dict:
    return json.loads((ROOT / "demo/public/data/results.json").read_text(encoding="utf-8"))


def test_export_reproduces_committed_file():
    ex = _export()
    assert ex.render(ex.build()) == (ROOT / "demo/public/data/results.json").read_text(encoding="utf-8")


def test_schema_and_revision():
    d = _committed()
    assert d["schema"] == "lab-demo-results" and d["schema_version"] == "1.0.0"
    assert re.fullmatch(r"[0-9a-f]{40}", d["code_revision"])
    assert [e["id"] for e in d["experiments"]] == ["EXP-001", "EXP-002", "EXP-003", "EXP-004"]
    assert "generated" not in json.dumps(d)  # no timestamps


def test_every_display_string_is_in_the_manuscript():
    d = _committed()
    estimates = [x for e in d["experiments"] for x in e["estimates"]] + d["post_hoc"]["estimates"]
    assert len(estimates) == 26
    for x in estimates:
        assert x["display"] in MANUSCRIPT, x["label"]
        assert x["interval_display"] in MANUSCRIPT, x["label"]
        if x["interval_display"].startswith("["):
            assert f"{x['display']} {x['interval_display']}" in MANUSCRIPT, x["label"]
        else:  # documented exception: EXP-001 smoke value printed with its SD
            assert f"{x['display']}, {x['interval_display']}" in MANUSCRIPT, x["label"]


def test_exp004_is_registered_not_run():
    e = {x["id"]: x for x in _committed()["experiments"]}["EXP-004"]
    assert e["estimates"] == [] and "not run" in e["status"] and "not frozen" in e["status"]


def test_per_cell_rows_match_the_exp002_report_table():
    for c in _committed()["per_cell"]:
        a = c["arms"]
        flag = "A0 not aligned before the shock" if c["a0_not_aligned"] else ""
        cells = [c["cell"], flag] + [a[k]["phi_pre_display"] for k in ("A0", "A1", "A2")] \
            + [a[k]["phi_post_display"] for k in ("A0", "A1", "A2")] \
            + [f"{c['a1_a0']['display']} {c['a1_a0']['interval_display']}"]
        row = "| " + " | ".join(cells) + " |"
        assert row in REPORT002, row


def test_public_texts_use_manuscript_numbers():
    pool = MANUSCRIPT + REPORT002 + (ROOT / "research/paper/supplementary.md").read_text(encoding="utf-8")
    token = re.compile(r"(?<![\w.])[-+]?\d+\.\d+(?![\w.]*\d)")
    skip = re.compile(r"[0-9a-f]{12,}|\d+\.\d+\.\d+|10\.\d{4,}/\S+|M\d\.\d|section \d+\.\d+|11\.\d")
    for rel in ("README.md", "articles/medium.md", "articles/linkedin.md", "demo/README.md"):
        text = skip.sub(" ", (ROOT / rel).read_text(encoding="utf-8"))
        for tok in token.findall(text):
            assert tok in pool or tok.lstrip("-+") in pool, f"{rel}: {tok} not in manuscript or reports"
