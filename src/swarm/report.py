# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Report generator: tables and figures built only from validated result
files, then Markdown, and optionally PDF via pandoc -> Typst (DL-002).

Every number in the generated report is computed here from the run records
under ``<results>/runs``; nothing is typed by hand.
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np

from .analysis import cell_key, paired_differences
from .config import SimConfig
from .manifest import environment, utc_now
from .runner import load_results

PANDOC = os.environ.get("SWARM_PANDOC", "/Users/bechir/research/labs/.tools/pandoc")
TYPST_PYTHON = os.environ.get("SWARM_TYPST_PYTHON", "/Users/bechir/research/labs/.tools/py/bin/python")
MAINFONT = "Libertinus Serif"


def _cell_label(key: str) -> str:
    c = json.loads(key)
    label = f"rho={c['density']:g}, eta={c['noise']:g}, r={c['radius']:g}"
    defaults = SimConfig().to_dict()
    for k in ("w_cohesion", "sep_ratio", "w_align", "boundary", "neighbourhood", "n_agents", "steps"):
        if c.get(k) != defaults[k]:
            label += f", {k}={c[k]:g}" if isinstance(c[k], float) else f", {k}={c[k]}"
    return label


def _f(v: float | None, nd: int = 3) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    return f"{v:.{nd}f}"


def _stats(vals: list[float]) -> tuple[float, float, float, float]:
    a = np.asarray(vals, dtype=float)
    sd = float(a.std(ddof=1)) if a.size > 1 else float("nan")
    return float(a.mean()), sd, float(a.min()), float(a.max())


def summarise(records: list[dict]) -> dict:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in records:
        groups[(cell_key(r["config"]), r["config"]["arm"])].append(r)
    rows = []
    for (cell, arm), rs in sorted(groups.items()):
        ok = [r for r in rs if r["status"] == "ok"]
        row = {"cell": _cell_label(cell), "arm": arm, "runs": len(rs), "failed": len(rs) - len(ok)}
        for m in ("phi_pre", "phi_post", "cohesion_post", "collisions_per_agent_per_100",
                  "dist_evals_per_step"):
            vals = [r["metrics"][m] for r in ok if r["metrics"][m] is not None]
            row[m] = _stats(vals) if vals else None
        taus = [r["metrics"]["tau"] for r in ok if r["metrics"]["tau"] is not None]
        cens = [r for r in ok if r["metrics"]["tau_censored"]]
        row["tau_median"] = float(np.median(taus)) if taus else None
        row["tau_censored"] = len(cens)
        row["wall_s"] = _stats([r["manifest"]["runtime_s"] for r in rs])
        rows.append(row)
    return {"rows": rows}


def _figures(records: list[dict], outdir: Path, diffs: dict,
             label: str = "Exploratory") -> list[tuple[str, str, str]]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figs = []
    cells = sorted({cell_key(r["config"]) for r in records})
    arms = sorted({r["config"]["arm"] for r in records})
    colours = {"A0": "#1b6f8a", "A1": "#b5542b", "A2": "#555555"}
    with_series = [r for r in records if r["status"] == "ok" and r["series"]["phi"]]
    if with_series:
        fig, axes = plt.subplots(len(cells), 1, figsize=(7, 2.6 * len(cells)), squeeze=False)
        for ax, cell in zip(axes[:, 0], cells):
            for arm in arms:
                rs = [r for r in with_series if cell_key(r["config"]) == cell and r["config"]["arm"] == arm]
                for k, r in enumerate(rs):
                    ax.plot(r["series"]["phi"], color=colours.get(arm, "k"), lw=0.6, alpha=0.6,
                            label=f"{arm} (n={len(rs)} seeds)" if k == 0 else None)
            td = json.loads(cell)["t_disturb"]
            ax.axvline(td, color="k", ls=":", lw=0.8)
            ax.set_ylim(0, 1)
            ax.set_xlabel("step t")
            ax.set_ylabel("polarization phi(t)")
            ax.set_title(_cell_label(cell), fontsize=9)
            ax.legend(fontsize=7, loc="lower right")
        fig.tight_layout()
        name = "fig01_phi_timeseries.png"
        fig.savefig(outdir / name, dpi=150)
        plt.close(fig)
        figs.append(("FIG-01", name, "Polarization phi(t) (dimensionless, 0 to 1) for every seed "
                     "(one line per seed) and arm; dotted line marks the disturbance step t_d. "
                     f"{label} simulated data."))
    if diffs:
        fig, ax = plt.subplots(figsize=(7, 2.8))
        labels = []
        for k, (name, cells_d) in enumerate(sorted(diffs.items())):
            for cell, by_seed in sorted(cells_d.items()):
                vals = list(by_seed.values())
                ax.scatter([len(labels)] * len(vals), vals, s=14, color="#1b6f8a")
                labels.append(f"{name}\n{_cell_label(cell)}")
        ax.axhline(0, color="k", lw=0.6)
        ax.set_xticks(range(len(labels)), labels, fontsize=7)
        ax.set_ylabel("paired difference in phi_post")
        fig.tight_layout()
        fname = "fig02_paired_differences.png"
        fig.savefig(outdir / fname, dpi=150)
        plt.close(fig)
        figs.append(("FIG-02", fname, "Per-seed paired differences in phi_post (dimensionless) "
                     f"between arms within a cell, one dot per seed. {label}; not a test of H0."))
    return figs


def build_report(results_dir: Path, title: str, pdf: bool = False, workers_assumed: int = 8) -> Path:
    results_dir = Path(results_dir)
    records = load_results(results_dir)
    exp_cfg_path = results_dir / "experiment_config.json"
    exp_cfg = json.loads(exp_cfg_path.read_text()) if exp_cfg_path.exists() else {}
    out = results_dir / "report"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    labels = sorted({r["label"] for r in records})
    exploratory = "exploratory" in labels
    summary = summarise(records)
    arms = sorted({r["config"]["arm"] for r in records})
    diffs = {}
    if "A0" in arms:
        for treat in [a for a in arms if a != "A0"]:
            d = paired_differences(records, "phi_post", treat, "A0")
            if d:
                diffs[f"{treat}-A0"] = d
    figs = _figures(records, out, diffs, "Exploratory" if exploratory else "Confirmatory")

    failed = [r for r in records if r["status"] == "failed"]
    walls = [r["manifest"]["runtime_s"] for r in records]
    mean_wall = float(np.mean(walls))
    full_runs = exp_cfg.get("full_matrix_runs")
    rev = sorted({r["manifest"]["git_revision"] for r in records})
    dirty = sorted({str(r["manifest"]["git_dirty"]) for r in records})

    L = []
    L.append(f"<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->")
    L.append(f"# {title}\n")
    if exploratory:
        L.append("**EXPLORATORY.** These are exploratory simulated runs made before the protocol "
                 "freeze. They are not findings and are never pooled with confirmatory results.\n")
    L.append(f"- Generated: {utc_now()} by `swarm.report` (code revision of the generator: "
             f"{environment()['git_revision']}).")
    L.append(f"- Experiment: {exp_cfg.get('experiment_id', 'unknown')}; labels: {', '.join(labels)}.")
    L.append(f"- Runs: {len(records)} recorded, {len(records) - len(failed)} ok, {len(failed)} failed.")
    L.append(f"- Code revision(s) of the runs: {', '.join(rev)} (working tree dirty: {', '.join(dirty)}).")
    L.append(f"- Source files: `runs/*.json` (schema 1.0.0), `metrics.csv`, `run_manifest.json`.\n")
    if failed:
        L.append("## Failed runs\n")
        L.append("| run_id | error |\n| --- | --- |")
        for r in failed:
            L.append(f"| {r['run_id']} | {r['error']} |")
        L.append("")

    L.append("## Per-arm summary (mean, SD across seeds)\n")
    L.append("| cell | arm | runs | phi_pre | phi_post | cohesion | collisions /agent/100 steps | "
             "tau median (censored) | evals/step | runtime s |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in summary["rows"]:
        def ms(k: str) -> str:
            s = row[k]
            return "n/a" if s is None else f"{_f(s[0])} ({_f(s[1])})"
        tau = "n/a" if row["tau_median"] is None else f"{row['tau_median']:g}"
        L.append(f"| {row['cell']} | {row['arm']} | {row['runs']} | {ms('phi_pre')} | {ms('phi_post')} | "
                 f"{ms('cohesion_post')} | {ms('collisions_per_agent_per_100')} | "
                 f"{tau} ({row['tau_censored']}) | {ms('dist_evals_per_step')} | "
                 f"{_f(row['wall_s'][0], 2)} |")
    L.append("")

    pair_rows = []
    if diffs:
        L.append("## Paired differences in phi_post (planning quantity)\n")
        L.append("Within-cell differences between arms for the same seed. The SD feeds the "
                 "sample-size check of `research/protocol.md` section 6. Not a test of H0.\n")
        L.append("| contrast | cell | pairs | mean | SD | min | max | projected 95% CI half-width, "
                 "18 cells x 10 seeds |")
        L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for name, cells_d in sorted(diffs.items()):
            for cell, by_seed in sorted(cells_d.items()):
                mean, sd, lo, hi = _stats(list(by_seed.values()))
                half = 1.96 * sd / math.sqrt(180) if not math.isnan(sd) else float("nan")
                pair_rows.append({"contrast": name, "cell": _cell_label(cell), "pairs": len(by_seed),
                                  "mean": mean, "sd": sd, "min": lo, "max": hi,
                                  "projected_half_width_180_pairs": half})
                L.append(f"| {name} | {_cell_label(cell)} | {len(by_seed)} | {_f(mean)} | {_f(sd)} | "
                         f"{_f(lo)} | {_f(hi)} | {_f(half)} |")
        L.append("")

    L.append("## Runtime\n")
    L.append(f"- Mean runtime per run: {_f(mean_wall, 3)} s (median {_f(float(np.median(walls)), 3)} s, "
             f"max {_f(max(walls), 3)} s), measured inside the worker, single thread.")
    proj = None
    if full_runs:
        serial = mean_wall * full_runs
        proj = {"full_matrix_runs": full_runs, "serial_s": serial,
                "workers_assumed": workers_assumed, "parallel_s": serial / workers_assumed}
        L.append(f"- Projection for {full_runs} runs at this mean: {_f(serial / 60, 1)} min serial, "
                 f"about {_f(serial / workers_assumed / 60, 1)} min with {workers_assumed} workers "
                 "(assumes linear scaling and the same per-run cost in every cell; a planning "
                 "estimate, not a measurement).")
    L.append("")

    if figs:
        L.append("## Figures\n")
        for fid, fname, cap in figs:
            L.append(f"![{fid}. {cap}]({fname})\n")

    with open(out / "summary_by_arm.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["cell", "arm", "runs", "failed", "metric", "mean", "sd", "min", "max"])
        for row in summary["rows"]:
            for m in ("phi_pre", "phi_post", "cohesion_post", "collisions_per_agent_per_100",
                      "dist_evals_per_step", "wall_s"):
                if row[m] is not None:
                    w.writerow([row["cell"], row["arm"], row["runs"], row["failed"], m, *row[m]])
    if pair_rows:
        with open(out / "paired_differences.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(pair_rows[0]))
            w.writeheader()
            w.writerows(pair_rows)
    (out / "report_data.json").write_text(json.dumps(
        {"label": "exploratory" if exploratory else "confirmatory", "runs": len(records),
         "failed": len(failed), "mean_runtime_s": mean_wall, "projection": proj,
         "paired_differences": pair_rows}, indent=1) + "\n", encoding="utf-8")
    md = out / "report.md"
    md.write_text("\n".join(L) + "\n", encoding="utf-8")
    if pdf:
        build_pdf(md)
    return md


def build_pdf(md: Path) -> Path:
    """Markdown -> Typst (pandoc, mainfont workaround) -> PDF (typst package)."""
    md = Path(md).resolve()
    typ = md.with_suffix(".typ")
    pdf = md.with_suffix(".pdf")
    subprocess.run([PANDOC, md.name, "-f", "markdown", "-t", "typst", "-s",
                    "-V", f"mainfont={MAINFONT}", "-o", typ.name], cwd=md.parent, check=True)
    code = ("import sys, typst; typst.compile(sys.argv[1], output=sys.argv[2], root=sys.argv[3])")
    subprocess.run([TYPST_PYTHON, "-I", "-c", code, str(typ), str(pdf), str(md.parent)],
                   cwd=md.parent, check=True)
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise RuntimeError(f"PDF not produced: {pdf}")
    return pdf
