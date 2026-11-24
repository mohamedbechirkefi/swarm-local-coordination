# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Neighbour-computation benchmark (EXP-001 protocol section 6): cell list
versus brute force, A0 only, exact evaluation counts and wall-clock per step.
"""

from __future__ import annotations

import csv
import itertools
import json
import time
from pathlib import Path

import numpy as np

from .config import SimConfig
from .manifest import REPO_ROOT, environment, utc_now
from .neighbors import metric_pairs
from .rules import align_only
from .geometry import wrap_angle, wrap_positions
from .simulate import _directed, initial_state


def bench_one(cfg: SimConfig, steps: int) -> dict:
    """Advance A0 for `steps` steps; time each index on the same states."""
    x, theta, _, _, noise_rng = initial_state(cfg)
    L, half = cfg.box, cfg.noise * np.pi
    t_cell = t_brute = 0.0
    ev_cell = ev_brute = 0
    mismatch = 0
    for _ in range(steps):
        t0 = time.perf_counter()
        pc = metric_pairs(x, L, cfg.radius, True, "cell")
        t1 = time.perf_counter()
        pb = metric_pairs(x, L, cfg.radius, True, "brute")
        t2 = time.perf_counter()
        t_cell += t1 - t0
        t_brute += t2 - t1
        ev_cell += pc.evals
        ev_brute += pb.evals
        if not (np.array_equal(pc.i, pb.i) and np.array_equal(pc.j, pb.j)):
            mismatch += 1
        recv, other, _, _ = _directed(pc)
        theta = wrap_angle(align_only(theta, recv, other) + noise_rng.uniform(-half, half, cfg.n_agents))
        x = wrap_positions(x + cfg.speed * np.stack([np.cos(theta), np.sin(theta)], 1), L)
    return {"cell_s_per_step": t_cell / steps, "brute_s_per_step": t_brute / steps,
            "cell_evals_per_step": ev_cell / steps, "brute_evals_per_step": ev_brute / steps,
            "mismatched_steps": mismatch}


def run_bench(spec: dict, root: Path = REPO_ROOT) -> list[dict]:
    out = root / spec["output_dir"]
    if Path(spec["output_dir"]).parts[:2] != ("results", "exploratory"):
        raise ValueError("benchmark outputs must go under results/exploratory/")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for n, rho, r, rep in itertools.product(spec["n_agents"], spec["density"], spec["radius"],
                                            range(spec["repeats"])):
        cfg = SimConfig(arm="A0", n_agents=n, density=rho, radius=r, noise=spec["noise"],
                        steps=spec["steps"], t_disturb=spec["steps"], window=0, pre_window=0,
                        seed=spec["seed_base"] + rep)
        rows.append({"n_agents": n, "density": rho, "radius": r, "repeat": rep, "seed": cfg.seed,
                     **bench_one(cfg, spec["steps"])})
    with open(out / "bench.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "bench_manifest.json").write_text(json.dumps(
        {"label": "exploratory", "spec": spec, **environment(), "finished_utc": utc_now()},
        indent=1) + "\n", encoding="utf-8")
    return rows
