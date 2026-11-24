# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""EXP-001 exploratory planning summary, computed only from result files.

Reads the smoke, burn-in scan and long burn-in outputs under
results/exploratory/ and writes results/exploratory/EXP-001-summary.json and
.md: runtime per run, projected EXP-002 matrix time, seed spread, and
degenerate cells. Exploratory planning numbers, not findings.

Usage: uv run python experiments/EXP-001/summarise_exploratory.py
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from swarm.manifest import REPO_ROOT, environment, utc_now
from swarm.runner import load_results

EXP = REPO_ROOT / "results" / "exploratory"
ORDER_THRESHOLD = 0.5  # descriptive: "ordered before the shock" if mean phi_pre >= 0.5
SEEDS_EXP002 = 10
WORKERS_ASSUMED = 8


def cell(r: dict) -> tuple[float, float, float]:
    c = r["config"]
    return (c["density"], c["noise"], c["radius"])


def main() -> None:
    smoke = load_results(EXP / "EXP-001-smoke")
    scan = load_results(EXP / "EXP-001-burnin-scan")
    long = load_results(EXP / "EXP-001-burnin-long")
    out: dict = {"label": "exploratory", "generated_utc": utc_now(), **environment(),
                 "sources": ["results/exploratory/EXP-001-smoke", "results/exploratory/EXP-001-burnin-scan",
                             "results/exploratory/EXP-001-burnin-long"],
                 "failed_runs": sum(r["status"] != "ok" for r in smoke + scan + long)}

    # Runtime: smoke cell at full length; per-cell scaling from the burn-in scan.
    smoke_cell = cell(smoke[0])
    smoke_rt = defaultdict(list)
    for r in smoke:
        smoke_rt[r["config"]["arm"]].append(r["manifest"]["runtime_s"])
    scan_rt = defaultdict(list)
    for r in scan:
        scan_rt[(cell(r), r["config"]["arm"])].append(r["manifest"]["runtime_s"])
    proj_cells = []
    total = 0.0
    for (c, arm), v in sorted(scan_rt.items()):
        factor = np.mean(v) / np.mean(scan_rt[(smoke_cell, arm)])
        per_run = float(np.mean(smoke_rt[arm]) * factor)
        total += per_run * SEEDS_EXP002
        proj_cells.append({"density": c[0], "noise": c[1], "radius": c[2], "arm": arm,
                           "projected_s_per_run": per_run})
    all_smoke = [x for v in smoke_rt.values() for x in v]
    out["runtime"] = {
        "smoke_cell": smoke_cell,
        "smoke_mean_s_per_run": float(np.mean(all_smoke)),
        "smoke_max_s_per_run": float(np.max(all_smoke)),
        "smoke_mean_s_per_run_by_arm": {a: float(np.mean(v)) for a, v in smoke_rt.items()},
        "projected_max_s_per_run": max(p["projected_s_per_run"] for p in proj_cells),
        "exp002_runs": len(proj_cells) * SEEDS_EXP002,
        "exp002_projected_serial_s": total,
        "exp002_projected_parallel_s": total / WORKERS_ASSUMED,
        "workers_assumed": WORKERS_ASSUMED,
        "method": "per-run cost of each (cell, arm) = smoke mean for the arm (T=1000) x ratio of "
                  "burn-in-scan mean runtimes (T=500) between that cell and the smoke cell; "
                  "linear parallel scaling assumed",
    }

    # Seed spread: paired differences in the smoke cell; between-seed SD of phi_pre in the scan.
    by = defaultdict(dict)
    for r in smoke:
        by[r["config"]["arm"]][r["config"]["seed"]] = r["metrics"]["phi_post"]
    spread = {}
    for t in ("A1", "A2"):
        d = np.array([by[t][s] - by["A0"][s] for s in sorted(by["A0"])])
        sd = float(d.std(ddof=1))
        spread[f"{t}-A0"] = {"pairs": int(d.size), "mean": float(d.mean()), "sd": sd,
                             "projected_ci_half_width_180_pairs": 1.96 * sd / math.sqrt(180)}
    out["seed_spread_smoke_phi_post"] = spread
    out["planning_sd_assumed"] = 0.2

    # Degenerate cells: arms not ordered before the shock.
    phi_pre = defaultdict(list)
    for r in scan:
        phi_pre[(cell(r), r["config"]["arm"])].append(r["metrics"]["phi_pre"])
    deg = []
    for (c, arm), v in sorted(phi_pre.items()):
        deg.append({"density": c[0], "noise": c[1], "radius": c[2], "arm": arm,
                    "phi_pre_mean": float(np.mean(v)), "phi_pre_sd": float(np.std(v, ddof=1)),
                    "ordered": bool(np.mean(v) >= ORDER_THRESHOLD)})
    out["order_threshold"] = ORDER_THRESHOLD
    out["burnin_scan"] = deg
    out["cells_ordered_by_arm"] = {a: sum(d["ordered"] for d in deg if d["arm"] == a)
                                   for a in ("A0", "A1", "A2")}
    out["random_heading_phi_reference"] = 1 / math.sqrt(200)

    # Burn-in length: A0 phi over [400, 500) versus [1900, 2000).
    bl = defaultdict(list)
    for r in long:
        phi = np.array(r["series"]["phi"])
        bl[cell(r)].append((float(phi[400:500].mean()), float(phi[1900:2000].mean())))
    out["burnin_long_A0"] = [{"density": c[0], "noise": c[1], "radius": c[2],
                              "phi_400_500": float(np.mean([a for a, _ in v])),
                              "phi_1900_2000": float(np.mean([b for _, b in v]))}
                             for c, v in sorted(bl.items())]

    (EXP / "EXP-001-summary.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")

    L = ["<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->",
         "# EXP-001 exploratory planning summary\n",
         "**EXPLORATORY.** Generated by `experiments/EXP-001/summarise_exploratory.py` from the result "
         "files listed below. Planning numbers for the owner's freeze decision, not findings.\n",
         f"- Generated {out['generated_utc']} at code revision {out['git_revision']}.",
         f"- Sources: {', '.join('`' + s + '`' for s in out['sources'])}; failed runs: {out['failed_runs']}.\n",
         "## Runtime\n"]
    rt = out["runtime"]
    L.append(f"- Smoke cell rho={smoke_cell[0]:g}, eta={smoke_cell[1]:g}, r={smoke_cell[2]:g}, T=1000: "
             f"mean {rt['smoke_mean_s_per_run']:.3f} s per run, max {rt['smoke_max_s_per_run']:.3f} s; by arm "
             + ", ".join(f"{a} {v:.3f} s" for a, v in sorted(rt["smoke_mean_s_per_run_by_arm"].items())) + ".")
    L.append(f"- Projected EXP-002 ({rt['exp002_runs']} runs): {rt['exp002_projected_serial_s'] / 60:.1f} min serial, "
             f"about {rt['exp002_projected_parallel_s'] / 60:.1f} min with {WORKERS_ASSUMED} workers; "
             f"most expensive cell {rt['projected_max_s_per_run']:.3f} s per run. Method: {rt['method']}.\n")
    L.append("## Seed spread (smoke cell, phi_post, 5 seeds)\n")
    L.append("| contrast | pairs | mean | SD | projected 95% CI half-width at 18 x 10 pairs |")
    L.append("| --- | --- | --- | --- | --- |")
    for k, v in spread.items():
        L.append(f"| {k} | {v['pairs']} | {v['mean']:.3f} | {v['sd']:.3f} | {v['projected_ci_half_width_180_pairs']:.3f} |")
    L.append(f"\nThe draft protocol assumed SD <= {out['planning_sd_assumed']}.\n")
    L.append(f"## Order before the shock (burn-in scan, 3 seeds, T = 500; ordered if mean phi_pre >= {ORDER_THRESHOLD})\n")
    L.append(f"Cells ordered, out of 18: " + ", ".join(f"{a} {n}" for a, n in out["cells_ordered_by_arm"].items())
             + f". Random headings give phi near 1/sqrt(N) = {out['random_heading_phi_reference']:.3f}.\n")
    L.append("| rho | eta | r | A0 phi_pre | A1 phi_pre | A2 phi_pre |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    tab = defaultdict(dict)
    for d in deg:
        tab[(d["density"], d["noise"], d["radius"])][d["arm"]] = d["phi_pre_mean"]
    for c, v in sorted(tab.items()):
        L.append(f"| {c[0]:g} | {c[1]:g} | {c[2]:g} | {v['A0']:.3f} | {v['A1']:.3f} | {v['A2']:.3f} |")
    L.append("\n## Burn-in length (A0, 2 seeds, T = 2000, no shock)\n")
    L.append("| rho | eta | r | mean phi over [400, 500) | mean phi over [1900, 2000) |")
    L.append("| --- | --- | --- | --- | --- |")
    for d in out["burnin_long_A0"]:
        L.append(f"| {d['density']:g} | {d['noise']:g} | {d['radius']:g} | {d['phi_400_500']:.3f} | {d['phi_1900_2000']:.3f} |")
    (EXP / "EXP-001-summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {EXP / 'EXP-001-summary.json'} and .md")


if __name__ == "__main__":
    main()
