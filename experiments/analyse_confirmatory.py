# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Frozen confirmatory analysis of EXP-002 and EXP-003 (protocol v1.0).

Written and committed before any confirmatory output existed (M3, 2026-11-25).
It implements exactly the frozen analysis:

- EXP-002 (research/experiments/EXP-002/protocol.md sections 4, 9, 10):
  Delta = equal-weight mean over the 18 cells of the within-cell mean paired
  difference phi_post(A1) - phi_post(A0); stratified seed-level percentile
  bootstrap, 10,000 resamples, seed 20261124, 95% CI; decision rule with
  SESOI 0.05. Stop rule: more than 5% failed runs in any arm means no
  analysis. Per-cell differences with CIs are descriptive; the 10 cells where
  A0 is not orderable (rule R-BI) are flagged. A2 contrasts and secondary
  metrics are descriptive with CIs.
- EXP-003 (protocol sections 3 and 4): Delta_S per condition on the reduced
  cells, with the same bootstrap; S2 pairs its A1 runs with the EXP-002 A0
  runs of the same cell and seed. Classification against the EXP-002
  estimate and CI ("invalidated" / "weakened" / neither). S4 recomputes tau
  at thresholds 0.8 and 0.95 from the stored EXP-002 phi series.

Reading of EXP-003 section 4 fixed here before any data (DL-012): the
"EXP-002 point estimate" and "EXP-002 CI" are those of the primary pooled
Delta over 18 cells (primary reading). The classification against Delta
restricted to the 4 reduced cells is also reported (secondary reading).

Also checks every run's metrics against its stored phi series (metric
validation on known quantities). Outputs go to <results>/analysis/ and the
generated tables are written between GENERATED markers in the reports.

  python experiments/analyse_confirmatory.py exp002
  python experiments/analyse_confirmatory.py exp003
  python experiments/analyse_confirmatory.py check DIR   (metric validation only)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from swarm.analysis import decision, stratified_bootstrap  # noqa: E402
from swarm.manifest import environment, utc_now  # noqa: E402
from swarm.metrics import recovery_time  # noqa: E402
from swarm.runner import load_results  # noqa: E402

N_BOOT = 10_000
BOOT_SEED = 20261124
SESOI = 0.05
FAIL_STOP = 0.05
EXP002 = ROOT / "results" / "confirmatory" / "EXP-002"
EXP003 = {"S1": ROOT / "results" / "confirmatory" / "EXP-003-S1",
          "S2": ROOT / "results" / "confirmatory" / "EXP-003-S2",
          "S3": ROOT / "results" / "confirmatory" / "EXP-003-S3"}
BURNIN = ROOT / "results" / "exploratory" / "EXP-001-burnin-rule-decision.json"
REDUCED = [(0.5, 0.1, 1.0), (0.5, 0.5, 1.0), (2.0, 0.1, 1.0), (2.0, 0.5, 1.0)]
SECONDARY = ("phi_pre", "cohesion_post", "collisions_per_agent_per_100")


# ---------------------------------------------------------------- helpers

def cell_of(r: dict) -> tuple[float, float, float]:
    c = r["config"]
    return (float(c["density"]), float(c["noise"]), float(c["radius"]))


def cell_label(c: tuple) -> str:
    return f"rho={c[0]:g}, eta={c[1]:g}, r={c[2]:g}"


def not_orderable() -> set[tuple]:
    d = json.loads(BURNIN.read_text(encoding="utf-8"))
    return {tuple(float(v) for v in c) for c in d["not_orderable_cells"]}


def values(records: list[dict], arm: str, metric: str, pred=None) -> dict[tuple, dict[int, float]]:
    """{cell: {seed: value}} for ok runs of an arm with a non-null metric."""
    out: dict[tuple, dict[int, float]] = defaultdict(dict)
    for r in records:
        if r["config"]["arm"] != arm or r["status"] != "ok" or r["metrics"][metric] is None:
            continue
        if pred is not None and not pred(r):
            continue
        out[cell_of(r)][r["config"]["seed"]] = float(r["metrics"][metric])
    return out


def pair(treat: dict, ctrl: dict, cells=None) -> dict[tuple, np.ndarray]:
    """Paired differences per cell over seeds present in both arms."""
    out = {}
    for c in sorted(treat):
        if cells is not None and c not in cells:
            continue
        if c not in ctrl:
            continue
        common = sorted(set(treat[c]) & set(ctrl[c]))
        if common:
            out[c] = np.array([treat[c][s] - ctrl[c][s] for s in common])
    return out


def boot(cells: dict[tuple, np.ndarray]) -> dict:
    return stratified_bootstrap({cell_label(c): v for c, v in cells.items()}, n_boot=N_BOOT,
                                seed=BOOT_SEED)


def failure_check(records: list[dict]) -> dict:
    by_arm: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_arm[r["config"]["arm"]].append(r)
    rates = {a: sum(r["status"] != "ok" for r in rs) / len(rs) for a, rs in sorted(by_arm.items())}
    failed = [{"run_id": r["run_id"], "error": r["error"]} for r in records if r["status"] != "ok"]
    return {"runs_by_arm": {a: len(rs) for a, rs in sorted(by_arm.items())}, "failure_rate_by_arm": rates,
            "failed_runs": failed, "stop": any(v > FAIL_STOP for v in rates.values())}


def check_metrics(records: list[dict]) -> dict:
    """Recompute phi_pre, phi_post and tau from the stored series; check bounds."""
    n = bad = 0
    problems = []
    for r in records:
        if r["status"] != "ok" or not r["series"]["phi"]:
            continue
        n += 1
        c, m = r["config"], r["metrics"]
        phi = np.asarray(r["series"]["phi"], dtype=float)
        td, w, pw = c["t_disturb"], c["window"], c["pre_window"]
        errs = []
        if phi.size != c["steps"]:
            errs.append("series length")
        if np.any(phi < 0) or np.any(phi > 1) or not np.all(np.isfinite(phi)):
            errs.append("phi out of [0, 1]")
        if abs(phi[td - pw:td].mean() - m["phi_pre"]) > 1e-12:
            errs.append("phi_pre")
        if abs(phi[td:td + w].mean() - m["phi_post"]) > 1e-12:
            errs.append("phi_post")
        tau, cens = recovery_time(phi, td, w, m["phi_pre"], c["recovery_threshold"], c["recovery_hold"])
        if tau != m["tau"] or cens != m["tau_censored"]:
            errs.append("tau")
        if not 0 < m["cohesion_post"] <= 1:
            errs.append("cohesion")
        if m["collisions_per_agent_per_100"] < 0:
            errs.append("collisions")
        if errs:
            bad += 1
            problems.append({"run_id": r["run_id"], "errors": errs})
    return {"runs_checked": n, "runs_with_mismatch": bad, "problems": problems[:50]}


def fmt(v, nd=3) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    return f"{v:.{nd}f}"


def ci(b: dict) -> str:
    return f"{fmt(b['estimate'])} [{fmt(b['ci_low'])}, {fmt(b['ci_high'])}]"


def write_generated(report: Path, blocks: dict[str, str]) -> None:
    """Replace the text between <!-- BEGIN GENERATED:k --> and <!-- END GENERATED:k -->."""
    if not report.exists():
        return
    text = report.read_text(encoding="utf-8")
    for k, body in blocks.items():
        pat = re.compile(rf"(<!-- BEGIN GENERATED:{k} -->\n).*?(<!-- END GENERATED:{k} -->)", re.S)
        if pat.search(text):
            text = pat.sub(lambda m: m.group(1) + body.rstrip() + "\n" + m.group(2), text)
    report.write_text(text, encoding="utf-8")


def _env() -> dict:
    e = environment()
    return {"generated_utc": utc_now(), "generator": "experiments/analyse_confirmatory.py",
            "generator_revision": e["git_revision"], "generator_tree_dirty": e["git_dirty"],
            "numpy": e["numpy"], "bootstrap": {"n_boot": N_BOOT, "seed": BOOT_SEED, "level": 0.95,
                                                "method": "stratified seed-level percentile"}}


# ---------------------------------------------------------------- EXP-002

def analyse_exp002() -> dict:
    records = load_results(EXP002)
    out = EXP002 / "analysis"
    out.mkdir(exist_ok=True)
    fc = failure_check(records)
    res = {"experiment_id": "EXP-002", "label": "confirmatory", **_env(), "runs": len(records),
           "failures": fc, "metric_check": check_metrics(records)}
    if fc["stop"]:
        res["stopped"] = "more than 5% failed runs in an arm (protocol section 8); no analysis"
        (out / "analysis.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
        return res
    flagged = not_orderable()
    post = {a: values(records, a, "phi_post") for a in ("A0", "A1", "A2")}
    d10 = pair(post["A1"], post["A0"])
    primary = boot(d10)
    primary["decision"] = decision(primary["ci_low"], primary["ci_high"], SESOI)
    primary["sesoi"] = SESOI
    res["primary"] = {"estimand": "Delta = mean over cells of mean paired phi_post(A1) - phi_post(A0)",
                      **primary}
    res["primary_restricted_to_exp003_cells"] = boot({c: v for c, v in d10.items() if c in REDUCED})
    refs = {"A2-A0": pair(post["A2"], post["A0"]), "A2-A1": pair(post["A2"], post["A1"])}
    res["reference_contrasts"] = {k: boot(v) for k, v in refs.items()}
    sec = {}
    for m in SECONDARY:
        vv = {a: values(records, a, m) for a in ("A0", "A1", "A2")}
        sec[m] = {"A1-A0": boot(pair(vv["A1"], vv["A0"])), "A2-A0": boot(pair(vv["A2"], vv["A0"]))}
    res["secondary_pooled"] = sec
    res["secondary_pooled_note"] = "descriptive, with CIs; no confirmatory claim (protocol section 7)"
    # per-cell table
    rows = []
    cells = sorted(post["A0"])
    for c in cells:
        row = {"cell": cell_label(c), "density": c[0], "noise": c[1], "radius": c[2],
               "a0_not_orderable_flag": c in flagged}
        for a in ("A0", "A1", "A2"):
            for m in ("phi_pre", "phi_post"):
                v = values(records, a, m).get(c, {})
                row[f"{a}_{m}_mean"] = float(np.mean(list(v.values()))) if v else None
            ok = [r for r in records if cell_of(r) == c and r["config"]["arm"] == a and r["status"] == "ok"]
            taus = [r["metrics"]["tau"] for r in ok if r["metrics"]["tau"] is not None]
            row[f"{a}_tau_median"] = float(np.median(taus)) if taus else None
            row[f"{a}_tau_censored"] = sum(bool(r["metrics"]["tau_censored"]) for r in ok)
            row[f"{a}_runs_ok"] = len(ok)
            row[f"{a}_wall_s_per_step"] = float(np.mean([r["timing"]["wall_s_per_step"] for r in ok])) if ok else None
            row[f"{a}_dist_evals_per_step"] = float(np.mean([r["metrics"]["dist_evals_per_step"] for r in ok])) if ok else None
        for k, dd in (("A1-A0", d10), ("A2-A0", refs["A2-A0"])):
            b = boot({c: dd[c]}) if c in dd else None
            row[f"{k}_pairs"] = 0 if b is None else b["n_pairs"]
            row[f"{k}_mean"] = None if b is None else b["estimate"]
            row[f"{k}_ci_low"] = None if b is None else b["ci_low"]
            row[f"{k}_ci_high"] = None if b is None else b["ci_high"]
        rows.append(row)
    res["per_cell"] = rows
    with open(out / "per_cell.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(out / "paired_differences_phi_post.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["contrast", "density", "noise", "radius", "seed", "difference"])
        for name, dd in (("A1-A0", post["A1"]), ("A2-A0", post["A2"]), ("A2-A1", post["A2"])):
            ctrl = post["A1"] if name == "A2-A1" else post["A0"]
            for c in sorted(dd):
                for s in sorted(set(dd[c]) & set(ctrl.get(c, {}))):
                    w.writerow([name, *c, s, dd[c][s] - ctrl[c][s]])
    # S4 inputs: tau at 0.8 and 0.95 from EXP-002 series (descriptive)
    res["s4_tau_thresholds"] = s4_tau(records)
    figs = figures_exp002(records, rows, primary, out)
    res["figures"] = figs
    (out / "analysis.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")
    write_generated(ROOT / "research" / "experiments" / "EXP-002" / "report.md", tables_exp002(res))
    return res


def s4_tau(records: list[dict]) -> list[dict]:
    rows = []
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for r in records:
        if r["status"] == "ok" and r["series"]["phi"] and r["config"]["arm"] in ("A0", "A1"):
            grouped[(cell_of(r), r["config"]["arm"])].append(r)
    for (c, arm), rs in sorted(grouped.items()):
        row = {"cell": cell_label(c), "arm": arm, "runs": len(rs)}
        for th in (0.8, 0.9, 0.95):
            taus, cens = [], 0
            for r in rs:
                cf = r["config"]
                t, cz = recovery_time(np.asarray(r["series"]["phi"]), cf["t_disturb"], cf["window"],
                                      r["metrics"]["phi_pre"], th, cf["recovery_hold"])
                cens += cz
                if t is not None:
                    taus.append(t)
            row[f"tau{th:g}_median"] = float(np.median(taus)) if taus else None
            row[f"tau{th:g}_censored"] = cens
        rows.append(row)
    return rows


def figures_exp002(records, rows, primary, out: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figs = []
    # Forest plot of per-cell A1 - A0 with CIs and the pooled estimate.
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ys = np.arange(len(rows))[::-1]
    for y, r in zip(ys, rows):
        filled = not r["a0_not_orderable_flag"]
        ax.errorbar(r["A1-A0_mean"], y, xerr=[[r["A1-A0_mean"] - r["A1-A0_ci_low"]],
                    [r["A1-A0_ci_high"] - r["A1-A0_mean"]]], fmt="o", color="#1b6f8a",
                    mfc="#1b6f8a" if filled else "white", ms=5, capsize=2)
    ax.axvspan(primary["ci_low"], primary["ci_high"], color="#b5542b", alpha=0.25,
               label=f"pooled Delta 95% CI ({primary['n_pairs']} pairs)")
    ax.axvline(primary["estimate"], color="#b5542b", lw=1.2, label="pooled Delta")
    ax.axvline(0, color="k", lw=0.7)
    for s in (-SESOI, SESOI):
        ax.axvline(s, color="k", ls=":", lw=0.7)
    ax.set_yticks(ys, [r["cell"] + (" *" if r["a0_not_orderable_flag"] else "") for r in rows], fontsize=7)
    ax.set_xlabel("paired difference in phi_post, A1 - A0 (dimensionless)")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(out / "fig_exp002_01_forest.png", dpi=150)
    plt.close(fig)
    figs.append({"id": "FIG-EXP002-01", "file": "fig_exp002_01_forest.png",
                 "caption": "Per-cell mean paired difference phi_post(A1) - phi_post(A0) with 95% "
                            "stratified-bootstrap CIs (20 seeds per cell; 10,000 resamples); shaded band "
                            "and solid line: pooled Delta and its CI; dotted lines: SESOI +/- 0.05. "
                            "Hollow markers and * mark the 10 cells where A0 is not aligned before the "
                            "shock (rule R-BI). Simulated data, confirmatory."})
    # Mean phi(t) per arm around the shock, with +/- 1.96 SE across seeds.
    cells = sorted({cell_of(r) for r in records})
    fig, axes = plt.subplots(6, 3, figsize=(9, 12), sharex=True, sharey=True)
    colours = {"A0": "#1b6f8a", "A1": "#b5542b", "A2": "#555555"}
    for ax, c in zip(axes.ravel(), cells):
        for arm in ("A0", "A1", "A2"):
            rs = [r for r in records if cell_of(r) == c and r["config"]["arm"] == arm
                  and r["status"] == "ok" and r["series"]["phi"]]
            if not rs:
                continue
            s = np.array([r["series"]["phi"][2800:3500] for r in rs])
            mu, se = s.mean(0), s.std(0, ddof=1) / math.sqrt(len(rs))
            t = np.arange(2800, 2800 + s.shape[1])
            ax.plot(t, mu, color=colours[arm], lw=0.8, label=f"{arm} (n={len(rs)})")
            ax.fill_between(t, mu - 1.96 * se, mu + 1.96 * se, color=colours[arm], alpha=0.25, lw=0)
        ax.axvline(3000, color="k", ls=":", lw=0.7)
        ax.set_title(cell_label(c) + (" *" if c in not_orderable() else ""), fontsize=7)
        ax.set_ylim(0, 1)
        ax.tick_params(labelsize=6)
    axes[0, 0].legend(fontsize=6)
    for ax in axes[-1]:
        ax.set_xlabel("step t", fontsize=7)
    for ax in axes[:, 0]:
        ax.set_ylabel("phi(t)", fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "fig_exp002_02_timeseries.png", dpi=150)
    plt.close(fig)
    figs.append({"id": "FIG-EXP002-02", "file": "fig_exp002_02_timeseries.png",
                 "caption": "Mean polarization phi(t) across 20 seeds per arm, steps 2800 to 3499, with "
                            "a band of +/- 1.96 standard errors across seeds; dotted line: shock at "
                            "t_d = 3000. * marks cells where A0 is not orderable (rule R-BI). Simulated "
                            "data, confirmatory."})
    return figs


def tables_exp002(res: dict) -> dict[str, str]:
    p = res["primary"]
    L = ["| quantity | value |", "| --- | --- |",
         f"| Runs recorded / failed | {res['runs']} / {len(res['failures']['failed_runs'])} |",
         f"| Cells / independent (cell, seed) pairs | {p['n_cells']} / {p['n_pairs']} |",
         f"| Delta = A1 - A0 in phi_post, 95% CI | {ci(p)} |",
         f"| Decision under the frozen rule (SESOI {SESOI}) | {p['decision']} |",
         f"| Delta restricted to the 4 EXP-003 cells (descriptive) | {ci(res['primary_restricted_to_exp003_cells'])} |"]
    for k, b in res["reference_contrasts"].items():
        L.append(f"| Reference {k} in phi_post (descriptive) | {ci(b)} |")
    for m, d in res["secondary_pooled"].items():
        for k, b in d.items():
            L.append(f"| Secondary {m}, {k} (descriptive) | {ci(b)} |")
    mc = res["metric_check"]
    L.append(f"| Metric check: runs recomputed from series / mismatches | {mc['runs_checked']} / {mc['runs_with_mismatch']} |")
    C = ["| cell | flag | A0 phi_pre | A1 phi_pre | A2 phi_pre | A0 phi_post | A1 phi_post | A2 phi_post | "
         "A1 - A0 [95% CI] | A2 - A0 [95% CI] |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["per_cell"]:
        C.append(f"| {r['cell']} | {'A0 not aligned before the shock' if r['a0_not_orderable_flag'] else ''} | "
                 f"{fmt(r['A0_phi_pre_mean'])} | {fmt(r['A1_phi_pre_mean'])} | {fmt(r['A2_phi_pre_mean'])} | "
                 f"{fmt(r['A0_phi_post_mean'])} | {fmt(r['A1_phi_post_mean'])} | {fmt(r['A2_phi_post_mean'])} | "
                 f"{fmt(r['A1-A0_mean'])} [{fmt(r['A1-A0_ci_low'])}, {fmt(r['A1-A0_ci_high'])}] | "
                 f"{fmt(r['A2-A0_mean'])} [{fmt(r['A2-A0_ci_low'])}, {fmt(r['A2-A0_ci_high'])}] |")
    S = ["| cell | A0 tau median (censored of 20) | A1 tau median (censored) | A2 tau median (censored) | "
         "A0 / A1 / A2 wall-clock ms per step | A0 / A1 / A2 distance evaluations per step |",
         "| --- | --- | --- | --- | --- | --- |"]
    for r in res["per_cell"]:
        S.append(f"| {r['cell']} | " + " | ".join(
            f"{fmt(r[f'{a}_tau_median'], 1)} ({r[f'{a}_tau_censored']})" for a in ("A0", "A1", "A2")) +
            " | " + " / ".join(fmt(1000 * r[f"{a}_wall_s_per_step"], 3) for a in ("A0", "A1", "A2")) +
            " | " + " / ".join(fmt(r[f"{a}_dist_evals_per_step"], 0) for a in ("A0", "A1", "A2")) + " |")
    F = [f"![{f['id']}. {f['caption']}](../../../results/confirmatory/EXP-002/analysis/{f['file']})\n"
         for f in res["figures"]]
    return {"exp002-primary": "\n".join(L), "exp002-cells": "\n".join(C), "exp002-secondary": "\n".join(S),
            "exp002-figures": "\n".join(F)}


# ---------------------------------------------------------------- EXP-003

def classify(b: dict, ref: dict) -> str:
    """EXP-003 section 4 invalidation criterion."""
    est = ref["estimate"]
    if (est > 0 and b["ci_high"] < 0) or (est < 0 and b["ci_low"] > 0):
        return "invalidated"
    ref_excludes = ref["ci_low"] > 0 or ref["ci_high"] < 0
    if b["ci_low"] <= 0 <= b["ci_high"] and ref_excludes:
        return "weakened"
    return "neither invalidated nor weakened"


def analyse_exp003() -> dict:
    a2 = json.loads((EXP002 / "analysis" / "analysis.json").read_text(encoding="utf-8"))
    if "primary" not in a2:
        raise SystemExit("EXP-002 analysis missing or stopped; EXP-003 needs its estimate")
    ref_full = a2["primary"]
    ref_red = a2["primary_restricted_to_exp003_cells"]
    exp2 = load_results(EXP002)
    a0_exp2 = values(exp2, "A0", "phi_post")
    res = {"experiment_id": "EXP-003", "label": "confirmatory", **_env(),
           "reference_primary": {k: ref_full[k] for k in ("estimate", "ci_low", "ci_high", "n_pairs")},
           "reference_restricted": {k: ref_red[k] for k in ("estimate", "ci_low", "ci_high", "n_pairs")},
           "reading": "primary: classified against the pooled EXP-002 Delta (18 cells); secondary: against "
                      "EXP-002 Delta restricted to the 4 reduced cells (DL-012)", "conditions": {}}
    for name, d in EXP003.items():
        if not (d / "runs").exists():
            res["conditions"][name] = {"status": "no results"}
            continue
        recs = load_results(d)
        fc = failure_check(recs)
        entry = {"runs": len(recs), "failures": fc, "metric_check": check_metrics(recs)}
        if fc["stop"]:
            entry["stopped"] = "more than 5% failed runs in an arm; no analysis"
            res["conditions"][name] = entry
            continue
        if name == "S2":
            for wc, sub in (("0.25", "S2a"), ("1", "S2b")):
                a1 = values(recs, "A1", "phi_post", pred=lambda r, w=float(wc): r["config"]["w_cohesion"] == w)
                dd = pair(a1, a0_exp2, cells=set(REDUCED))
                b = boot(dd)
                res["conditions"][sub] = {**entry, "w_cohesion": float(wc), "delta_s": b,
                                          "control": "EXP-002 A0 runs, same cells and seeds",
                                          "per_cell": {cell_label(c): {"mean": float(v.mean()), "pairs": int(v.size)}
                                                       for c, v in dd.items()},
                                          "verdict_primary": classify(b, ref_full),
                                          "verdict_secondary": classify(b, ref_red)}
        else:
            dd = pair(values(recs, "A1", "phi_post"), values(recs, "A0", "phi_post"))
            b = boot(dd)
            pre = boot(pair(values(recs, "A1", "phi_pre"), values(recs, "A0", "phi_pre")))
            res["conditions"][name] = {**entry, "delta_s": b, "phi_pre_A1_minus_A0": pre,
                                       "per_cell": {cell_label(c): {"mean": float(v.mean()), "pairs": int(v.size)}
                                                    for c, v in dd.items()},
                                       "verdict_primary": classify(b, ref_full),
                                       "verdict_secondary": classify(b, ref_red)}
    res["S4"] = {"source": "EXP-002 series (no new runs)", "rows": a2.get("s4_tau_thresholds", [])}
    out = ROOT / "results" / "confirmatory" / "EXP-003-analysis"
    out.mkdir(parents=True, exist_ok=True)
    res["figures"] = figures_exp003(res, out)
    (out / "analysis.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")
    write_generated(ROOT / "research" / "experiments" / "EXP-003" / "report.md", tables_exp003(res))
    return res


def figures_exp003(res: dict, out: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    items = [("EXP-002 (18 cells)", res["reference_primary"]),
             ("EXP-002 (4 reduced cells)", res["reference_restricted"])]
    for k in ("S1", "S2a", "S2b", "S3"):
        c = res["conditions"].get(k, {})
        if "delta_s" in c:
            items.append((k, c["delta_s"]))
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ys = np.arange(len(items))[::-1]
    for y, (lab, b) in zip(ys, items):
        ax.errorbar(b["estimate"], y, xerr=[[b["estimate"] - b["ci_low"]], [b["ci_high"] - b["estimate"]]],
                    fmt="o", color="#b5542b" if lab.startswith("EXP-002") else "#1b6f8a", capsize=3)
    ax.axvline(0, color="k", lw=0.7)
    for s in (-SESOI, SESOI):
        ax.axvline(s, color="k", ls=":", lw=0.7)
    ax.set_yticks(ys, [lab for lab, _ in items], fontsize=8)
    ax.set_xlabel("Delta: A1 - A0 in phi_post (dimensionless), 95% CI")
    fig.tight_layout()
    fig.savefig(out / "fig_exp003_01_sensitivity.png", dpi=150)
    plt.close(fig)
    return [{"id": "FIG-EXP003-01", "file": "fig_exp003_01_sensitivity.png",
             "caption": "Delta (A1 - A0 in phi_post) with 95% stratified-bootstrap CIs (20 seeds per cell, "
                        "10,000 resamples) for EXP-002 (all 18 cells and the 4 reduced cells) and each "
                        "EXP-003 condition: S1 topological k = 7, S2a/S2b w_c = 0.25/1.0, S3 reflecting walls. "
                        "Dotted lines: SESOI +/- 0.05. Simulated data, confirmatory."}]


def tables_exp003(res: dict) -> dict[str, str]:
    L = ["| condition | runs (failed) | Delta_S [95% CI] | pairs | verdict vs pooled EXP-002 | "
         "verdict vs EXP-002 on the 4 cells |", "| --- | --- | --- | --- | --- | --- |",
         f"| EXP-002, 18 cells (reference) | | {ci(res['reference_primary'])} | {res['reference_primary']['n_pairs']} | | |",
         f"| EXP-002, 4 reduced cells (reference) | | {ci(res['reference_restricted'])} | {res['reference_restricted']['n_pairs']} | | |"]
    for k in ("S1", "S2a", "S2b", "S3"):
        c = res["conditions"].get(k)
        if not c or "delta_s" not in c:
            L.append(f"| {k} | {'' if not c else c.get('runs', '')} | not analysed ({(c or {}).get('stopped', (c or {}).get('status', 'missing'))}) | | | |")
            continue
        L.append(f"| {k} | {c['runs']} ({len(c['failures']['failed_runs'])}) | {ci(c['delta_s'])} | "
                 f"{c['delta_s']['n_pairs']} | {c['verdict_primary']} | {c['verdict_secondary']} |")
    P = ["| condition | cell | mean A1 - A0 in phi_post | pairs |", "| --- | --- | --- | --- |"]
    for k in ("S1", "S2a", "S2b", "S3"):
        c = res["conditions"].get(k, {})
        for cell, v in c.get("per_cell", {}).items():
            P.append(f"| {k} | {cell} | {fmt(v['mean'])} | {v['pairs']} |")
    S4 = ["| cell | arm | tau median at 0.8 (censored) | at 0.9 (censored) | at 0.95 (censored) |",
          "| --- | --- | --- | --- | --- |"]
    for r in res["S4"]["rows"]:
        S4.append(f"| {r['cell']} | {r['arm']} | {fmt(r['tau0.8_median'], 1)} ({r['tau0.8_censored']}) | "
                  f"{fmt(r['tau0.9_median'], 1)} ({r['tau0.9_censored']}) | "
                  f"{fmt(r['tau0.95_median'], 1)} ({r['tau0.95_censored']}) |")
    F = [f"![{f['id']}. {f['caption']}](../../../results/confirmatory/EXP-003-analysis/{f['file']})\n"
         for f in res["figures"]]
    return {"exp003-main": "\n".join(L), "exp003-cells": "\n".join(P), "exp003-s4": "\n".join(S4),
            "exp003-figures": "\n".join(F)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("what", choices=["exp002", "exp003", "check"])
    p.add_argument("dir", nargs="?")
    a = p.parse_args(argv)
    if a.what == "check":
        recs = load_results(Path(a.dir))
        r = check_metrics(recs)
        print(json.dumps({"runs": len(recs), **failure_check(recs), **r}, indent=1))
        return 0 if r["runs_with_mismatch"] == 0 else 1
    if a.what == "exp002":
        r = analyse_exp002()
        if "primary" in r:
            print(f"EXP-002: Delta {ci(r['primary'])}, {r['primary']['decision']}; "
                  f"metric mismatches {r['metric_check']['runs_with_mismatch']}")
        else:
            print(r.get("stopped"))
        return 0
    r = analyse_exp003()
    for k, c in r["conditions"].items():
        print(k, ci(c["delta_s"]) if "delta_s" in c else c.get("stopped", c.get("status")),
              c.get("verdict_primary", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
