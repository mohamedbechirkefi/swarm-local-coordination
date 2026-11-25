# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Export the published results for the M5 demo page (demo/public/data/results.json).

Reads committed results only (the frozen analysis outputs, the M4 exploratory analysis
and the EXP-002 experiment configuration), plus the claims register, the artifact
manifest, the experiment registry and the limitations list. Writes the shared template
schema "lab-demo-results" 1.0.0 with these project-specific top-level keys:

  per_cell   the 18 EXP-002 cells: A1 - A0 contrast with its CI, per-arm phi_pre and
             phi_post cell means, the R-BI flag (drawn by the page's forest plot and
             published window timeline);
  post_hoc   the M4 exploratory checks X1 to X5 (EXPL-M4-01), labelled exploratory;
  design     the fixed design values the page needs to draw the published timeline.

Every "display" and "interval_display" string is formatted from the committed value at
the precision the manuscript prints; tests/test_demo_export.py checks that each appears
verbatim in research/paper/manuscript.md (per-cell strings: in the EXP-002 report's
generated table, a documented exception). No timestamps, so the output is deterministic.

  .venv/bin/python scripts/export_demo_data.py          # write the file
  .venv/bin/python scripts/export_demo_data.py --check  # exit 1 if the file is stale
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "public" / "data" / "results.json"

EXP002 = "results/confirmatory/EXP-002/analysis/analysis.json"
EXP003 = "results/confirmatory/EXP-003-analysis/analysis.json"
M4 = "results/exploratory/M4-sensitivity/analysis.json"
EXP001 = "results/exploratory/EXP-001-summary.json"
CONFIG002 = "results/confirmatory/EXP-002/experiment_config.json"
CLAIMS = "research/claims_register.csv"
MANIFEST = "research/publication/artifact_manifest.json"
REGISTRY = "research/experiment_registry.csv"
LIMITS = "research/limitations.md"
EXEC003 = [f"results/confirmatory/EXP-003-{s}/execution.json" for s in ("S1", "S2", "S3")]
SOURCES = [EXP002, EXP003, *EXEC003, M4, EXP001, CONFIG002, CLAIMS, MANIFEST, REGISTRY, LIMITS]

# Limitations shown on the page, by item number in research/limitations.md.
LIMITATION_ITEMS = [13, 17, 18, 10, 16, 1, 2, 3, 4, 5, 6, 14]


class ExportError(RuntimeError):
    """A source is missing, inconsistent or does not support a displayed value."""


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel: str) -> dict:
    path = ROOT / rel
    if not path.is_file():
        raise ExportError(f"missing source {rel}")
    return json.loads(path.read_text(encoding="utf-8"))


def f3(x: float) -> str:
    return f"{x:.3f}"


def interval(lo: float, hi: float) -> str:
    return f"[{f3(lo)}, {f3(hi)}]"


def decide(lo: float, hi: float, sesoi: float) -> str:
    """Frozen decision rule (research/protocol.md, manuscript 4.3)."""
    if lo > 0 or hi < 0:
        return "rejects H0"
    if lo > -sesoi and hi < sesoi:
        return "practically equivalent"
    return "inconclusive"


def est(label: str, node: dict, unit: str = "polarization units", level: float = 0.95) -> dict:
    for k in ("estimate", "ci_low", "ci_high"):
        if not isinstance(node.get(k), (int, float)):
            raise ExportError(f"{label}: missing {k}")
    return {"label": label, "estimate": node["estimate"], "ci_low": node["ci_low"],
            "ci_high": node["ci_high"], "ci_level": level, "unit": unit,
            "display": f3(node["estimate"]), "interval_display": interval(node["ci_low"], node["ci_high"])}


def claims_by_experiment() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    with open(ROOT / CLAIMS, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            cid = row["claim_id"]
            hits = sorted(set(re.findall(r"EXP(\d{3})", row["result_id"])))
            if "R-M4" in row["result_id"]:
                hits.append("M4")
            for h in hits:
                out.setdefault(h if h == "M4" else f"EXP-{h}", []).append(cid)
    return out


def manifest_claims() -> set[str]:
    m = load(MANIFEST)
    return {c for a in m["artifacts"] for c in a.get("claims", [])}


def registry() -> dict[str, dict]:
    with open(ROOT / REGISTRY, newline="", encoding="utf-8") as fh:
        return {r["experiment_id"]: r for r in csv.DictReader(fh)}


def limitations() -> list[str]:
    text = (ROOT / LIMITS).read_text(encoding="utf-8")
    items = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^(\d+)\. (.+)$", text, re.M)}
    out = []
    for k in LIMITATION_ITEMS:
        if k not in items:
            raise ExportError(f"limitation {k} not found")
        out.append(re.sub(r"\*\*|`", "", items[k]))
    return out


def build() -> dict:
    a2, a3, m4, s1, cfg = load(EXP002), load(EXP003), load(M4), load(EXP001), load(CONFIG002)
    reg = registry()
    claims = claims_by_experiment()
    mapped = manifest_claims()
    for ids in claims.values():
        for cid in ids:
            if cid not in mapped:
                raise ExportError(f"claim {cid} is not mapped in the artifact manifest")

    rev = a2["generator_revision"]
    if a3["generator_revision"] != rev or not re.fullmatch(r"[0-9a-f]{40}", rev):
        raise ExportError("EXP-002 and EXP-003 analyses disagree on the code revision")
    pri = a2["primary"]
    sesoi = pri["sesoi"]
    verdict = decide(pri["ci_low"], pri["ci_high"], sesoi)
    if verdict != pri["decision"]:
        raise ExportError(f"frozen rule gives {verdict!r}, analysis.json says {pri['decision']!r}")
    if a2["failures"]["failed_runs"] or a2["metric_check"]["runs_with_mismatch"]:
        raise ExportError("EXP-002 has failed runs or metric mismatches; the page text assumes none")

    sp, rc = a2["secondary_pooled"], a2["reference_contrasts"]
    exp002 = {
        "id": "EXP-002", "kind": "confirmatory",
        "title": "Local rules and recovery from a heading disturbance (primary)",
        "status": f"confirmatory, complete: {a2['runs']} of {a2['runs']} runs, 0 failed",
        "verdict": f"{verdict} (95% CI excludes 0; SESOI {sesoi}). The same gap exists before the shock, "
                   "so this is a difference in sustained order, not in recovery.",
        "estimates": [
            est("Delta = A1 - A0, phi_post (primary)", pri),
            est("A1 - A0, phi_pre (descriptive)", sp["phi_pre"]["A1-A0"]),
            est("A2 - A0, phi_post (reference)", rc["A2-A0"]),
            est("A2 - A1, phi_post (reference)", rc["A2-A1"]),
            est("A1 - A0, cohesion C (descriptive)", sp["cohesion_post"]["A1-A0"], unit="fraction of agents"),
            est("A1 - A0, collisions (descriptive)", sp["collisions_per_agent_per_100"]["A1-A0"],
                unit="per agent per 100 steps"),
            est("A2 - A0, cohesion C (descriptive)", sp["cohesion_post"]["A2-A0"], unit="fraction of agents"),
            est("A2 - A0, collisions (descriptive)", sp["collisions_per_agent_per_100"]["A2-A0"],
                unit="per agent per 100 steps"),
        ],
        "claim_ids": claims.get("EXP-002", []),
        "report_path": "research/experiments/EXP-002/report.md",
        "notes": [
            f"{pri['n_cells']} cells x 20 matched seeds = {pri['n_pairs']} (cell, seed) pairs; stratified seed "
            f"bootstrap, {pri['n_boot']:,} resamples, 95% CI. The interval is conditional on the tested cells.",
            "A1 was weakly ordered before the shock in every cell (cell-mean phi_pre 0.097 to 0.229).",
            "A0 is not aligned before the shock in 10 of 18 cells (rule R-BI); those cells stay in the pooled "
            "estimate and are flagged.",
        ],
    }

    conds = a3["conditions"]
    names = {"S1": "S1 topological k = 7", "S2a": "S2a w_c = 0.25", "S2b": "S2b w_c = 1.0",
             "S3": "S3 reflecting walls"}
    verdicts = {c["verdict_primary"] for c in conds.values()} | {c["verdict_secondary"] for c in conds.values()}
    if verdicts != {"neither invalidated nor weakened"}:
        raise ExportError(f"unexpected EXP-003 verdicts {verdicts}")
    execs = [load(e) for e in EXEC003]
    runs3 = sum(e["runs"] for e in execs)
    if any(e["failed"] for e in execs) or runs3 != 480:
        raise ExportError("EXP-003 execution records do not show 480 runs with 0 failed")
    exp003 = {
        "id": "EXP-003", "kind": "confirmatory",
        "title": "Sensitivity of the EXP-002 contrast to modelling choices",
        "status": f"confirmatory, complete: {runs3} of {runs3} runs, 0 failed",
        "verdict": "No condition invalidates or weakens the EXP-002 result (frozen EXP-003 criteria).",
        "estimates": [est("EXP-002, 18 cells (reference)", a3["reference_primary"]),
                      est("EXP-002, 4 reduced cells (reference)", a3["reference_restricted"])]
                     + [est(f"Delta_S, {names[k]}", conds[k]["delta_s"]) for k in ("S1", "S2a", "S2b", "S3")],
        "claim_ids": claims.get("EXP-003", []),
        "report_path": "research/experiments/EXP-003/report.md",
        "notes": ["Four reduced cells (rho 0.5 and 2, eta 0.1 and 0.5, r = 1), 20 seeds each (80 pairs per "
                  "condition). The magnitude increases with the cohesion weight.",
                  "S4 (recovery thresholds 0.8 and 0.95) needed no new runs; it is descriptive."],
    }
    if any(c["failures"]["failed_runs"] for c in conds.values()):
        raise ExportError("EXP-003 has failed runs; the page text assumes none")

    smoke = s1["seed_spread_smoke_phi_post"]["A1-A0"]
    exp001 = {
        "id": "EXP-001", "kind": "exploratory",
        "title": "Implementation verification and smoke matrix (exploratory)",
        "status": "exploratory by design, complete",
        "verdict": "Not a hypothesis test. Verification checks V1 to V4 pass (cell list equals brute force on "
                   "every benchmarked step; runs are bit-identical on repeat).",
        "estimates": [{"label": "A1 - A0, phi_post, smoke cell, draft design (5 seeds; disclosure)",
                       "estimate": smoke["mean"], "ci_low": None, "ci_high": None, "ci_level": None,
                       "unit": "polarization units", "display": f3(smoke["mean"]),
                       "interval_display": f"SD {f3(smoke['sd'])}"}],
        "claim_ids": claims.get("EXP-001", []),
        "report_path": "research/experiments/EXP-001/report.md",
        "notes": ["The smoke value comes from the draft design (w_c 1, t_d 500), not the frozen one; it was seen "
                  "before the freeze and is disclosed. No interval was computed for it; the SD over 5 seeds is shown."],
    }

    r4 = reg["EXP-004"]
    if not r4["status"].startswith("registered, not frozen") or r4["protocol_hash"]:
        raise ExportError("EXP-004 registry status changed; re-check the page text")
    exp004 = {
        "id": "EXP-004", "kind": "registered",
        "title": "Recovery with matched pre-shock order",
        "status": "registered, not frozen; not run",
        "verdict": "None: no run of any kind has been made. The protocol is a v0.1 draft with 8 parameters open "
                   "for the owner, and the freeze needs the owner's decision.",
        "estimates": [],
        "claim_ids": claims.get("EXP-004", []),
        "report_path": "none (not run); protocol draft research/experiments/EXP-004/protocol.md",
        "notes": ["Planned primary outcome: the change score phi_post - phi_pre, with a manipulation check that "
                  "pre-shock order is matched."],
    }
    for e in (exp001, exp002, exp003):
        if not (ROOT / e["report_path"]).is_file():
            raise ExportError(f"missing report {e['report_path']}")

    # Per-cell EXP-002 values (forest plot and published window timeline).
    per_cell = []
    for c in a2["per_cell"]:
        lo, hi, m = c["A1-A0_ci_low"], c["A1-A0_ci_high"], c["A1-A0_mean"]
        per_cell.append({
            "cell": c["cell"], "density": c["density"], "noise": c["noise"], "radius": c["radius"],
            "a0_not_aligned": bool(c["a0_not_orderable_flag"]),
            "a1_a0": {"estimate": m, "ci_low": lo, "ci_high": hi, "ci_level": 0.95,
                      "display": f3(m), "interval_display": interval(lo, hi)},
            "arms": {arm: {"phi_pre": c[f"{arm}_phi_pre_mean"], "phi_post": c[f"{arm}_phi_post_mean"],
                           "phi_pre_display": f3(c[f"{arm}_phi_pre_mean"]),
                           "phi_post_display": f3(c[f"{arm}_phi_post_mean"])} for arm in ("A0", "A1", "A2")},
        })
    if len(per_cell) != 18 or sum(p["a0_not_aligned"] for p in per_cell) != 10:
        raise ExportError("per-cell table does not have 18 cells with 10 flagged")

    x = m4["results"]
    x5 = x["X5_exp003_change_score"]
    post_hoc = {
        "id": "EXPL-M4-01",
        "label": "exploratory, post hoc (chosen after the confirmatory results were seen; changes no verdict)",
        "claim_ids": claims.get("M4", []),
        "source": M4,
        "estimates": [
            est("X1 change score phi_post - phi_pre, all 18 cells", x["X1_change_score_all"]),
            est("X1 change score, 8 cells where A0 aligns", x["X1_change_score_orderable8"]),
            est("X2 phi_post, 8 cells where A0 aligns", x["X2_phi_post_orderable8"]),
            est("X2 phi_pre, 8 cells where A0 aligns", x["X2_phi_pre_orderable8"]),
            est("X2 phi_post, 10 flagged cells", x["X2_phi_post_flagged10"]),
            est("X3 phi_post, 7 cells with matched pre-shock order", x["X3_phi_post_matched"]),
            est("X4 early drop over [t_d, t_d + 50)", x["X4_drop_all"]),
        ] + [est(f"X5 change score, {k}", x5[k]["change_score"]) for k in ("S1", "S2a", "S2b", "S3")],
    }

    b = cfg["base"]
    boot = a2["bootstrap"]
    seeds = cfg["seeds"]
    assumptions = [
        {"name": "Agents", "value": f"N = {b['n_agents']}, constant speed v0 = {b['speed']} u per step, 2-D, "
                                     "synchronous updates", "source": CONFIG002},
        {"name": "Boundary and neighbours", "value": f"{b['boundary']} box; {b['neighbourhood']} neighbourhood "
                                                      "of radius r", "source": CONFIG002},
        {"name": "Grid", "value": "density rho in {0.5, 1, 2}, noise eta in {0.1, 0.3, 0.5}, radius r in {0.5, 1}",
         "source": CONFIG002},
        {"name": "Disturbance", "value": f"at t_d = {b['t_disturb']}, a fraction {b['shock_fraction']} of agents "
                                          "receive uniform random headings (same agents and headings in every arm)",
         "source": CONFIG002},
        {"name": "Windows", "value": f"phi_pre over the {b['pre_window']} steps before t_d; phi_post over the "
                                      f"{b['window']} steps from t_d", "source": CONFIG002},
        {"name": "Rule A1", "value": f"repulsion within r_s = {b['sep_ratio']} r has priority; otherwise "
                                      f"w_a = {b['w_align']:g} alignment plus w_c = {b['w_cohesion']} cohesion",
         "source": CONFIG002},
        {"name": "Rule A2", "value": "global mean heading of all agents plus the same noise; an idealised "
                                      "reference, not a local rule", "source": CONFIG002},
        {"name": "Seeds", "value": f"{seeds[0]} to {seeds[-1]} ({len(seeds)} per cell), the same in every arm",
         "source": CONFIG002},
        {"name": "Smallest effect of interest", "value": f"{sesoi} polarization units", "source": EXP002},
        {"name": "Uncertainty", "value": f"{boot['method']} bootstrap, {boot['n_boot']:,} resamples, seed "
                                          f"{boot['seed']}, {round(boot['level'] * 100)}% CI", "source": EXP002},
    ]

    return {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "SWARM",
        "question": "How do local interaction rules affect collective coordination under disturbances?",
        "status_label": "Independent research manuscript / preprint draft, not peer-reviewed. "
                        "All results are simulated.",
        "code_revision": rev,
        "sources": [{"path": p, "sha256": sha256(p)} for p in SOURCES],
        "experiments": [exp001, exp002, exp003, exp004],
        "assumptions": assumptions,
        "limitations": limitations(),
        "per_cell": per_cell,
        "post_hoc": post_hoc,
        "design": {"t_disturb": b["t_disturb"], "pre_window": b["pre_window"], "window": b["window"],
                   "sesoi": sesoi, "primary": exp002["estimates"][0]},
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        same = OUT.is_file() and OUT.read_text(encoding="utf-8") == text
        print("results.json up to date" if same else "results.json STALE")
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
