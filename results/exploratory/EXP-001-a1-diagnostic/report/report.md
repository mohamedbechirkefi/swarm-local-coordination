<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-001 a1-diagnostic (exploratory)

**EXPLORATORY.** These are exploratory simulated runs made before the protocol freeze. They are not findings and are never pooled with confirmatory results.

- Generated: 2026-11-24T16:09:20.867551Z by `swarm.report` (code revision of the generator: 99cc0c444fdfbab6749970b92cad5ebb5c8c2841).
- Experiment: EXP-001; labels: exploratory.
- Runs: 16 recorded, 16 ok, 0 failed.
- Code revision(s) of the runs: 99cc0c444fdfbab6749970b92cad5ebb5c8c2841 (working tree dirty: False).
- Source files: `runs/*.json` (schema 1.0.0), `metrics.csv`, `run_manifest.json`.

## Per-arm summary (mean, SD across seeds)

| cell | arm | runs | phi_pre | phi_post | cohesion | collisions /agent/100 steps | tau median (censored) | evals/step | runtime s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rho=2, eta=0.1, r=1, w_cohesion=0, sep_ratio=0, steps=500 | A1 | 2 | 0.975 (0.001) | n/a | n/a | n/a | n/a (0) | 3567.605 (259.778) | 0.25 |
| rho=2, eta=0.1, r=1, w_cohesion=0.25, sep_ratio=0, steps=500 | A1 | 2 | 0.693 (0.328) | n/a | n/a | n/a | n/a (0) | 10329.026 (1500.693) | 0.97 |
| rho=2, eta=0.1, r=1, w_cohesion=0.5, sep_ratio=0, steps=500 | A1 | 2 | 0.631 (0.017) | n/a | n/a | n/a | n/a (0) | 9284.775 (399.092) | 0.84 |
| rho=2, eta=0.1, r=1, sep_ratio=0, steps=500 | A1 | 2 | 0.301 (0.083) | n/a | n/a | n/a | n/a (0) | 5155.204 (283.522) | 0.52 |
| rho=2, eta=0.1, r=1, w_cohesion=0, steps=500 | A1 | 2 | 0.969 (0.001) | n/a | n/a | n/a | n/a (0) | 3057.162 (320.113) | 0.23 |
| rho=2, eta=0.1, r=1, w_cohesion=0.25, steps=500 | A1 | 2 | 0.449 (0.021) | n/a | n/a | n/a | n/a (0) | 5953.056 (729.638) | 0.43 |
| rho=2, eta=0.1, r=1, w_cohesion=0.5, steps=500 | A1 | 2 | 0.251 (0.084) | n/a | n/a | n/a | n/a (0) | 5555.065 (945.355) | 0.41 |
| rho=2, eta=0.1, r=1, steps=500 | A1 | 2 | 0.060 (0.004) | n/a | n/a | n/a | n/a (0) | 2828.417 (81.310) | 0.29 |

## Runtime

- Mean runtime per run: 0.493 s (median 0.423 s, max 1.043 s), measured inside the worker, single thread.

