# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Experiment runner: expand a validated experiment config into runs, execute
them (optionally in parallel), and serialize one validated result per run.

Failures are never dropped: a run that raises is written with status
"failed" and its error message (protocol section 8).
"""

from __future__ import annotations

import csv
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .config import ConfigError, SimConfig, canonical_hash
from .manifest import REPO_ROOT, config_frozen, environment, freeze_status, peak_rss_bytes, utc_now
from .schema import RESULT_SCHEMA_VERSION, read_result, validate_experiment, write_result
from .simulate import run as simulate

GRID_ORDER = ("density", "noise", "radius")


class RunRefused(RuntimeError):
    """The runner refuses to execute this configuration (gate or label rule)."""


def load_experiment(path: Path) -> dict:
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_experiment(cfg)
    return cfg


def check_allowed(exp: dict, root: Path = REPO_ROOT) -> None:
    """Fail closed on any label/gate inconsistency."""
    label, conf = exp["label"], exp["confirmatory"]
    if (label == "confirmatory") != conf:
        raise RunRefused(f"label {label!r} inconsistent with confirmatory={conf}")
    out = Path(exp["output_dir"])
    if out.is_absolute():
        raise RunRefused("output_dir must be relative to the repository root")
    if conf:
        if out.parts[:2] != ("results", "confirmatory") or ".." in out.parts:
            raise RunRefused("confirmatory outputs must go under results/confirmatory/")
        paths = ["research/protocol.md"]
        if "protocol_path" in exp:
            paths.append(exp["protocol_path"])
        frozen, reason = freeze_status(paths, root=root)
        if not frozen:
            raise RunRefused(f"refusing a confirmatory run: protocol not frozen ({reason}). "
                             "Freezing is the owner's decision (G-FREEZE).")
        frozen, reason = config_frozen(canonical_hash(exp), root=root)
        if not frozen:
            raise RunRefused(f"refusing a confirmatory run: configuration not frozen ({reason}). "
                             "A changed confirmatory configuration is a new freeze (G-FREEZE).")
    elif out.parts[:2] != ("results", "exploratory") or ".." in out.parts:
        raise RunRefused("exploratory outputs must go under results/exploratory/")


def _fmt(v: object) -> str:
    return f"{v:g}" if isinstance(v, float) else str(v)


def run_id_for(exp_id: str, cfg: SimConfig, grid_keys: list[str]) -> str:
    parts = [exp_id, cfg.arm]
    for k in grid_keys:
        if k != "arm":
            parts.append(f"{k}{_fmt(getattr(cfg, k))}")
    parts.append(f"s{cfg.seed}")
    return "_".join(parts)


def expand(exp: dict) -> list[tuple[str, SimConfig]]:
    """All (run_id, SimConfig) of the experiment, in a fixed order."""
    grid = exp["grid"]
    keys = sorted(grid, key=lambda k: (k != "arm", GRID_ORDER.index(k) if k in GRID_ORDER else 99, k))
    runs = []
    for values in itertools.product(*(grid[k] for k in keys)):
        for seed in exp["seeds"]:
            data = dict(exp["base"])
            data.update(dict(zip(keys, values)))
            data["seed"] = seed
            try:
                cfg = SimConfig.from_dict(data)
            except (ConfigError, TypeError) as exc:
                raise ConfigError(f"invalid cell {dict(zip(keys, values))}: {exc}") from None
            runs.append((run_id_for(exp["experiment_id"], cfg, keys), cfg))
    ids = [r for r, _ in runs]
    if len(set(ids)) != len(ids):
        raise ConfigError("duplicate run ids (grid values collide)")
    return runs


def execute_one(args: tuple) -> dict:
    """Run one simulation and build its validated result record."""
    exp_id, label, run_id, cfg_dict, store_series, command = args
    cfg = SimConfig.from_dict(cfg_dict)
    started = utc_now()
    t0 = time.perf_counter()
    status, error, metrics, timing, phi = "ok", None, None, None, None
    try:
        res = simulate(cfg)
        metrics, timing = res.metrics, res.timing
        phi = [float(v) for v in res.phi] if store_series else None
    except Exception as exc:  # recorded, never dropped
        status, error = "failed", f"{type(exc).__name__}: {exc}"
    runtime = time.perf_counter() - t0
    if metrics is None:
        metrics = {k: None for k in ("phi_pre", "phi_post", "tau", "tau_censored", "cohesion_post",
                                     "collisions_per_agent_per_100", "dist_evals_per_step")}
        timing = {"wall_s": None, "wall_s_per_step": None, "search_s_per_step": None}
    manifest = {"run_id": run_id, "config_hash": cfg.config_hash(), "seed": cfg.seed,
                **environment(), "started_utc": started, "finished_utc": utc_now(),
                "runtime_s": runtime, "peak_rss_bytes": peak_rss_bytes(), "command": command}
    return {"schema_version": RESULT_SCHEMA_VERSION, "record_type": "swarm.run_result",
            "experiment_id": exp_id, "run_id": run_id, "label": label, "status": status,
            "error": error, "config": cfg.to_dict(), "config_hash": cfg.config_hash(),
            "metrics": metrics, "timing": timing, "series": {"phi": phi}, "manifest": manifest}


METRIC_COLUMNS = ["phi_pre", "phi_post", "tau", "tau_censored", "cohesion_post",
                  "collisions_per_agent_per_100", "dist_evals_per_step"]
CONFIG_COLUMNS = ["arm", "density", "noise", "radius", "seed", "n_agents", "steps", "boundary",
                  "neighbourhood", "w_cohesion"]


def write_tables(records: list[dict], out: Path) -> None:
    """metrics.csv (one row per run) and run_manifest.json (all manifests)."""
    with open(out / "metrics.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["run_id", "label", "status", *CONFIG_COLUMNS, *METRIC_COLUMNS,
                    "wall_s", "config_hash"])
        for r in records:
            w.writerow([r["run_id"], r["label"], r["status"],
                        *(r["config"][c] for c in CONFIG_COLUMNS),
                        *("" if r["metrics"][m] is None else r["metrics"][m] for m in METRIC_COLUMNS),
                        r["manifest"]["runtime_s"], r["config_hash"]])
    (out / "run_manifest.json").write_text(
        json.dumps({"schema_version": RESULT_SCHEMA_VERSION,
                    "runs": [r["manifest"] for r in records]}, indent=1) + "\n", encoding="utf-8")


def run_experiment(exp: dict, workers: int = 1, root: Path = REPO_ROOT,
                   command: str | None = None) -> list[dict]:
    validate_experiment(exp)
    check_allowed(exp, root=root)
    runs = expand(exp)
    out = root / exp["output_dir"]
    (out / "runs").mkdir(parents=True, exist_ok=True)
    command = command or " ".join(["python -m swarm.cli", *sys.argv[1:]])
    store = exp.get("store_series", True)
    jobs = [(exp["experiment_id"], exp["label"], rid, cfg.to_dict(), store, command)
            for rid, cfg in runs]
    (out / "experiment_config.json").write_text(json.dumps(exp, indent=1) + "\n", encoding="utf-8")
    t0 = time.perf_counter()
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            records = list(pool.map(execute_one, jobs))
    else:
        records = [execute_one(j) for j in jobs]
    elapsed = time.perf_counter() - t0
    for rec in records:
        write_result(rec, out / "runs" / f"{rec['run_id']}.json")
    write_tables(records, out)
    summary = {"experiment_id": exp["experiment_id"], "label": exp["label"],
               "experiment_config_hash": canonical_hash(exp), "runs": len(records),
               "failed": sum(r["status"] == "failed" for r in records), "workers": workers,
               "elapsed_s": elapsed, "cpu_count": os.cpu_count(), **environment(),
               "finished_utc": utc_now()}
    (out / "execution.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    return records


def load_results(out: Path) -> list[dict]:
    """Read and validate every run result under out/runs (fail closed)."""
    files = sorted((Path(out) / "runs").glob("*.json"))
    if not files:
        raise FileNotFoundError(f"no run results under {out}/runs")
    return [read_result(f) for f in files]
