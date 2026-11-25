# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Write the small Python-engine fixture that the demo's vitest compares the
browser port against (M5, demo/src/engine.test.ts).

The fixture is exploratory test data, not a result: one tiny configuration
(N = 40, 120 steps, shock at step 60) per arm, run with the research engine
``swarm.simulate.run``. Because the browser sandbox uses its own random number
generator, the fixture records the engine's random inputs (initial positions,
headings, the shocked agents and their new headings, and every per-step noise
draw) so that the port can be driven with exactly the same inputs.

  .venv/bin/python scripts/make_sandbox_fixture.py

Output: demo/src/fixtures/engine_fixture.json (deterministic; no timestamps).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from swarm.config import SimConfig
from swarm.simulate import initial_state, run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "src" / "fixtures" / "engine_fixture.json"

BASE = dict(n_agents=40, density=1.0, noise=0.3, radius=1.0, speed=0.05, steps=120,
            t_disturb=60, window=60, pre_window=50, shock_fraction=0.5, sep_ratio=0.25,
            w_align=1.0, w_cohesion=0.5, collision_ratio=0.1, recovery_threshold=0.9,
            recovery_hold=10, boundary="periodic", neighbourhood="metric", index="cell", seed=7)


def build() -> dict:
    cfg0 = SimConfig(arm="A0", **BASE)
    x, theta, chosen, new, noise_rng = initial_state(cfg0)
    half = cfg0.noise * np.pi
    noise = [noise_rng.uniform(-half, half, size=cfg0.n_agents).tolist() for _ in range(cfg0.steps)]
    arms = {}
    for arm in ("A0", "A1", "A2"):
        res = run(SimConfig(arm=arm, **BASE), record_trajectory=True)
        m = res.metrics
        arms[arm] = {
            "phi": res.phi.tolist(),
            "x_final": res.trajectory["x"][-1].ravel().tolist(),
            "theta_final": res.trajectory["theta"][-1].tolist(),
            "x_step10": res.trajectory["x"][10].ravel().tolist(),
            "metrics": {k: m[k] for k in ("phi_pre", "phi_post", "tau", "tau_censored",
                                          "cohesion_post", "collisions_per_agent_per_100")},
        }
    return {
        "note": ("Exploratory test fixture for the demo engine port, produced by the research engine "
                 "swarm.simulate.run; not a research result."),
        "generator": "scripts/make_sandbox_fixture.py",
        "config": BASE,
        "box": cfg0.box,
        "init": {"x": x.ravel().tolist(), "theta": theta.tolist(), "shock_agents": chosen.tolist(),
                 "shock_headings": new.tolist(), "noise": noise},
        "arms": arms,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build(), separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
