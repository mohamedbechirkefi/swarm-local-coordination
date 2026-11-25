# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Evidence audit (M4): trace every decimal number in the publication texts to committed outputs.

For each document, every decimal token (for example -0.307 or 1138.7) is looked up in the
numeric values of the committed result files listed in SOURCES, at the printed precision
(round half to even and half away from zero are both accepted; the sign may be dropped in
prose, so the absolute value is also accepted). Integers are not checked automatically
(they are design parameters, counts and identifiers) and are reviewed by hand in
research/publication/evidence_audit.md. Hashes and dates are skipped.

Output: research/publication/number_audit.json, listing for every token the source files
and JSON paths where it was found, or "UNMATCHED".

  .venv/bin/python experiments/audit_numbers.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = ["research/paper/manuscript.md", "research/paper/supplementary.md",
        "research/publication/m4_interpretation.md", "research/publication/review_pass_2.md",
        "research/publication/evidence_audit.md",
        "research/claims_register.csv", "research/limitations.md",
        "research/experiments/EXP-001/report.md", "research/experiments/EXP-002/report.md",
        "research/experiments/EXP-003/report.md"]

SOURCES = ["results/confirmatory/EXP-002/analysis/analysis.json",
           "results/confirmatory/EXP-002/analysis/per_cell.csv",
           "results/confirmatory/EXP-002/execution.json",
           "results/confirmatory/EXP-002/launch.json",
           "results/confirmatory/EXP-003-analysis/analysis.json",
           "results/confirmatory/EXP-003-S1/execution.json",
           "results/confirmatory/EXP-003-S2/execution.json",
           "results/confirmatory/EXP-003-S3/execution.json",
           "results/confirmatory/EXP-003-S1/launch.json",
           "results/confirmatory/EXP-003-S2/launch.json",
           "results/confirmatory/EXP-003-S3/launch.json",
           "results/exploratory/M4-sensitivity/analysis.json",
           "results/exploratory/EXP-001-summary.json",
           "results/exploratory/EXP-001-burnin-rule-decision.json",
           "research/protocol_freeze.json",
           "experiments/EXP-002/config.json",
           "experiments/EXP-003/config_S1.json",
           "experiments/EXP-003/config_S2.json",
           "experiments/EXP-003/config_S3.json",
           "results/exploratory/EXP-001-smoke-m3/execution.json",
           "results/exploratory/EXP-001-smoke-m3/launch.json"]

# Values stated in the frozen protocol text rather than in a result file (design constants and
# pre-freeze diagnostics quoted in the protocol); each is checked against research/protocol.md.
PROTOCOL_TEXT = "research/protocol.md"

TOKEN = re.compile(r"(?<![\w.])[-+]?\d+\.\d+(?![\w.]*\d)")
SKIP = re.compile(r"arXiv:\S+|[0-9a-f]{12,}|\d{4}-\d{2}-\d{2}|\d+\.\d+\.\d+|10\.\d{4,}/\S+"
                  r"|(?:Sections?|section|sections) \d+\.\d+(?: (?:and|to) \d+\.\d+)?|^#+ \d+\.\d+|\(1\d\.\d\)", re.M)
# Method constants that are not results: 1.96 (normal quantile used for the +/- 1.96 standard-error band
# in FIG-EXP002-02, defined in experiments/analyse_confirmatory.py).
CONSTANTS = {"1.96": "method constant (figure band), experiments/analyse_confirmatory.py"}


def flatten(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, f"{path}[{i}]")
    elif isinstance(obj, bool) or obj is None:
        return
    elif isinstance(obj, (int, float)):
        yield path, float(obj)
    elif isinstance(obj, str):
        try:
            yield path, float(obj)
        except ValueError:
            return


def load_sources() -> list[tuple[str, str, float]]:
    vals = []
    for rel in SOURCES:
        p = ROOT / rel
        if not p.exists():
            continue
        if p.suffix == ".csv":
            with open(p, newline="", encoding="utf-8") as fh:
                for i, row in enumerate(csv.DictReader(fh)):
                    for k, v in row.items():
                        try:
                            vals.append((rel, f"row{i}.{k}", float(v)))
                        except (TypeError, ValueError):
                            pass
        else:
            for path, v in flatten(json.loads(p.read_text(encoding="utf-8"))):
                vals.append((rel, path, v))
    # unit conversion: reports print wall-clock per step in milliseconds
    vals += [(s, p + " (x1000, ms)", v * 1000) for s, p, v in vals if "wall_s_per_step" in p]
    return vals


def matches(token: str, v: float) -> bool:
    nd = len(token.split(".")[1])
    q = Decimal(1).scaleb(-nd)
    target = Decimal(token.lstrip("+"))
    d = Decimal(repr(v))
    for cand in (d, -d):
        for mode in (ROUND_HALF_EVEN, ROUND_HALF_UP):
            if cand.quantize(q, rounding=mode) == target:
                return True
    return False


def main() -> int:
    vals = load_sources()
    proto = (ROOT / PROTOCOL_TEXT).read_text(encoding="utf-8")
    report = {"generated_by": "experiments/audit_numbers.py", "sources": SOURCES, "documents": {}}
    total = unmatched = 0
    for rel in DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if rel.endswith("claims_register.csv"):
            # the manuscript_section column holds section numbers, not results
            with open(ROOT / rel, newline="", encoding="utf-8") as fh:
                text = "\n".join(" ".join(v for k, v in row.items() if k != "manuscript_section")
                                  for row in csv.DictReader(fh))
        text = SKIP.sub(" ", text)
        found = {}
        for tok in TOKEN.findall(text):
            if tok in found:
                continue
            if tok in CONSTANTS:
                found[tok] = [CONSTANTS[tok]]
                continue
            hits = [f"{s}:{p}" for s, p, v in vals if matches(tok, v)]
            if not hits and re.search(r"(?<![\d.])" + re.escape(tok.lstrip("+-")) + r"(?![\d])", proto):
                hits = [f"{PROTOCOL_TEXT} (text)"]
            found[tok] = hits[:5] if hits else "UNMATCHED"
        n_un = sum(v == "UNMATCHED" for v in found.values())
        total += len(found)
        unmatched += n_un
        report["documents"][rel] = {"distinct_decimal_tokens": len(found), "unmatched": n_un, "tokens": found}
    report["totals"] = {"distinct_tokens": total, "unmatched": unmatched}
    out = ROOT / "research" / "publication" / "number_audit.json"
    out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for rel, d in report["documents"].items():
        print(f"{rel}: {d['distinct_decimal_tokens']} tokens, {d['unmatched']} unmatched",
              [t for t, h in d["tokens"].items() if h == "UNMATCHED"])
    print(f"total {total}, unmatched {unmatched}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
