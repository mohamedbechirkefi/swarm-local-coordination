# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Apply the pre-stated burn-in rule R-BI (research/protocol.md section 13).

Reads the A0-only, no-shock series in results/exploratory/EXP-001-burnin-rule
and writes results/exploratory/EXP-001-burnin-rule-decision.{json,md}:

- m_c(t): mean over seeds of the mean phi over steps [t - 100, t), per cell c;
- cell c is orderable if m_c(T_MAX) >= 0.5;
- t_d is the smallest candidate t with m_c(t) >= 0.5 in every orderable cell
  (T_MAX if none qualifies, with the cells still below 0.5 listed).

It also projects the wall-clock of the amended confirmatory matrices from
measured runtimes (budget headroom as measured). Only pre-shock A0
polarization is read; no post-disturbance outcome exists in these files.

Usage: uv run python experiments/EXP-001/apply_burnin_rule.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from swarm.manifest import REPO_ROOT, environment, utc_now
from swarm.runner import load_results

SRC = REPO_ROOT / "results" / "exploratory" / "EXP-001-burnin-rule"
SMOKE = REPO_ROOT / "results" / "exploratory" / "EXP-001-smoke"
OUT = REPO_ROOT / "results" / "exploratory" / "EXP-001-burnin-rule-decision"
CANDIDATES = (500, 1000, 1500, 2000, 3000, 4000)
T_MAX = CANDIDATES[-1]
WIN = 100
ALIGNED = 0.5
WINDOW_POST = 500
SEEDS = 20
WORKERS_ASSUMED = 8


def choose_t_d(m: dict[tuple, dict[int, float]]) -> tuple[int, list[tuple], list[tuple]]:
    """The rule itself, separated for testing: returns (t_d, orderable, still_below)."""
    orderable = sorted(c for c, v in m.items() if v[T_MAX] >= ALIGNED)
    for t in CANDIDATES:
        if all(m[c][t] >= ALIGNED for c in orderable):
            return t, orderable, []
    return T_MAX, orderable, [c for c in orderable if m[c][T_MAX] < ALIGNED]


def main() -> None:
    recs = load_results(SRC)
    if any(r["status"] != "ok" for r in recs):
        raise SystemExit("failed runs present; the rule is not applied")
    series = defaultdict(list)
    per_step = defaultdict(list)
    for r in recs:
        c = r["config"]
        assert c["arm"] == "A0" and c["window"] == 0 and c["steps"] == T_MAX
        key = (c["density"], c["noise"], c["radius"])
        series[key].append(np.asarray(r["series"]["phi"]))
        per_step[key].append(r["manifest"]["runtime_s"] / c["steps"])
    m = {k: {t: float(np.mean([s[t - WIN:t].mean() for s in v])) for t in CANDIDATES}
         for k, v in series.items()}
    t_d, orderable, below = choose_t_d(m)
    T = t_d + WINDOW_POST

    # Budget: A0 seconds per step per cell (this scan) x arm ratio from the smoke cell (EXPL-002).
    smoke = load_results(SMOKE)
    arm_rt = defaultdict(list)
    for r in smoke:
        arm_rt[r["config"]["arm"]].append(r["manifest"]["runtime_s"])
    ratio = {a: float(np.mean(v) / np.mean(arm_rt["A0"])) for a, v in arm_rt.items()}
    a0 = {k: float(np.mean(v)) for k, v in per_step.items()}
    exp002 = sum(a0[k] * ratio[a] * T * SEEDS for k in a0 for a in ("A0", "A1", "A2"))
    reduced = [k for k in a0 if k[0] in (0.5, 2.0) and k[1] in (0.1, 0.5) and k[2] == 1.0]
    # EXP-003 upper bound: 4 conditions x (A0, A1) x 4 cells x 20 seeds, priced as the metric cell.
    exp003 = sum(a0[k] * ratio[a] * T * SEEDS * 4 for k in reduced for a in ("A0", "A1"))

    out = {"label": "exploratory", "rule": "R-BI", "generated_utc": utc_now(), **environment(),
           "source": "results/exploratory/EXP-001-burnin-rule", "runs": len(recs),
           "candidates": list(CANDIDATES), "aligned_threshold": ALIGNED, "window": WIN,
           "m": [{"density": k[0], "noise": k[1], "radius": k[2],
                  **{f"t{t}": v for t, v in m[k].items()}} for k in sorted(m)],
           "orderable_cells": [list(c) for c in orderable],
           "not_orderable_cells": [list(c) for c in sorted(m) if c not in orderable],
           "still_below_at_t_d": [list(c) for c in below],
           "t_d": t_d, "steps": T,
           "budget": {"arm_runtime_ratio_vs_A0_smoke": ratio,
                      "a0_s_per_step_by_cell": {str(k): v for k, v in sorted(a0.items())},
                      "exp002_runs": 18 * 3 * SEEDS, "exp002_serial_s": exp002,
                      "exp002_s_with_workers": exp002 / WORKERS_ASSUMED,
                      "exp003_runs_upper_bound": 4 * 2 * 4 * SEEDS, "exp003_serial_s": exp003,
                      "exp003_s_with_workers": exp003 / WORKERS_ASSUMED,
                      "workers_assumed": WORKERS_ASSUMED,
                      "method": "per-run cost = A0 s/step in this scan for the cell x (arm mean / A0 mean "
                                "runtime in the smoke cell, EXPL-002) x steps; linear parallel scaling assumed; "
                                "topological and reflecting conditions priced as metric periodic"}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{OUT}.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    lines = ["<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->",
             "# Burn-in rule R-BI: decision", "",
             f"**EXPLORATORY.** Generated by `experiments/EXP-001/apply_burnin_rule.py` from "
             f"`results/exploratory/EXP-001-burnin-rule` ({len(recs)} A0 runs, no shock) at "
             f"{out['generated_utc']}, revision {out['git_revision']}.", "",
             f"Rule: a cell is orderable if m(4000) >= {ALIGNED}; t_d is the smallest candidate in "
             f"{list(CANDIDATES)} with m(t_d) >= {ALIGNED} in every orderable cell.", "",
             "| rho | eta | r | " + " | ".join(f"m({t})" for t in CANDIDATES) + " | orderable |",
             "| --- | --- | --- | " + " | ".join("---" for _ in CANDIDATES) + " | --- |"]
    for k in sorted(m):
        lines.append(f"| {k[0]:g} | {k[1]:g} | {k[2]:g} | "
                     + " | ".join(f"{m[k][t]:.3f}" for t in CANDIDATES)
                     + f" | {'yes' if k in orderable else 'no'} |")
    lines += ["", f"**Result:** t_d = {t_d}, T = {T}. Orderable cells: {len(orderable)} of {len(m)}."
              + (f" Still below {ALIGNED} at t_d: {below}." if below else ""), "",
              f"**Budget (measured):** EXP-002 {out['budget']['exp002_runs']} runs, "
              f"{exp002 / 60:.1f} min serial, about {exp002 / WORKERS_ASSUMED / 60:.1f} min with "
              f"{WORKERS_ASSUMED} workers; EXP-003 at most {out['budget']['exp003_runs_upper_bound']} runs, "
              f"{exp003 / 60:.1f} min serial, about {exp003 / WORKERS_ASSUMED / 60:.1f} min with "
              f"{WORKERS_ASSUMED} workers. Arm runtime ratios vs A0 (smoke cell): "
              + ", ".join(f"{a} {v:.2f}" for a, v in sorted(ratio.items())) + "."]
    Path(f"{OUT}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[-3:]))


if __name__ == "__main__":
    main()
