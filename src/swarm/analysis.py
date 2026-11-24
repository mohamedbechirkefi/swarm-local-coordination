# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Analysis: paired differences and the stratified seed-level bootstrap
(protocol section 7). Pure functions of validated result records.
"""

from __future__ import annotations

import json
from collections import defaultdict

import numpy as np


def cell_key(config: dict) -> str:
    """Cell identity: the config without arm and seed, as canonical JSON."""
    rest = {k: v for k, v in config.items() if k not in ("arm", "seed")}
    return json.dumps(rest, sort_keys=True)


def paired_differences(records: list[dict], metric: str, treat: str, control: str) -> dict[str, dict[int, float]]:
    """{cell: {seed: metric(treat) - metric(control)}} over ok runs present in both arms.

    Seeds missing in either arm (failed runs, null metric) are left out of
    the pairing; callers report them separately.
    """
    vals: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    for r in records:
        if r["status"] != "ok" or r["metrics"][metric] is None:
            continue
        vals[(cell_key(r["config"]), r["config"]["arm"])][r["config"]["seed"]] = float(r["metrics"][metric])
    out: dict[str, dict[int, float]] = {}
    for (cell, arm), by_seed in vals.items():
        if arm != treat or (cell, control) not in vals:
            continue
        ctrl = vals[(cell, control)]
        common = sorted(set(by_seed) & set(ctrl))
        if common:
            out[cell] = {s: by_seed[s] - ctrl[s] for s in common}
    return out


def stratified_bootstrap(cells: dict[str, np.ndarray], n_boot: int = 10_000, seed: int = 20261124,
                         level: float = 0.95) -> dict:
    """Equal-weight mean over cells of within-cell mean differences, with a
    percentile CI from resampling seeds with replacement within each cell.
    """
    if not cells:
        raise ValueError("no cells to bootstrap")
    if n_boot < 1 or not 0 < level < 1:
        raise ValueError("n_boot must be >= 1 and level in (0, 1)")
    arrays = [np.asarray(v, dtype=float) for _, v in sorted(cells.items())]
    if any(a.size == 0 for a in arrays):
        raise ValueError("every cell needs at least one paired difference")
    estimate = float(np.mean([a.mean() for a in arrays]))
    rng = np.random.Generator(np.random.PCG64(seed))
    boots = np.zeros(n_boot)
    for a in arrays:
        idx = rng.integers(0, a.size, size=(n_boot, a.size))
        boots += a[idx].mean(axis=1)
    boots /= len(arrays)
    alpha = (1 - level) / 2
    lo, hi = np.quantile(boots, [alpha, 1 - alpha])
    return {"estimate": estimate, "ci_low": float(lo), "ci_high": float(hi), "n_boot": n_boot,
            "seed": seed, "level": level, "n_cells": len(arrays),
            "n_pairs": int(sum(a.size for a in arrays))}


def decision(ci_low: float, ci_high: float, sesoi: float) -> str:
    """Protocol section 3 decision rule (planning; applies only to frozen confirmatory data)."""
    if ci_low > 0 or ci_high < 0:
        return "rejects H0"
    if -sesoi < ci_low and ci_high < sesoi:
        return "practically equivalent"
    return "inconclusive"
