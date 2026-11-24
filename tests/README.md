<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# tests/

Run with `uv run python -m pytest -q` (or `uv run python -m swarm.cli test`).

- `test_neighbors.py`: cell list versus brute force on 1,000 configurations with agents at the box edges (EXP-001 V1), a Hypothesis property test, torus wrap, ties at exactly r, small boxes, evaluation counts, invalid inputs, topological neighbours.
- `test_rules.py`: hand-computed 2- and 3-agent updates for A0, A1, A2 (V4); zero-vector and coincident-agent edge cases; differential test against loop implementations in `reference.py`.
- `test_metrics_geometry.py`: golden values and bounds for polarization, angle wrapping, wrapping and reflection, connected components (against BFS), recovery time, collision rate.
- `test_simulate.py`: bit-identical reruns (V2), invariants on every step (V3), common random numbers across arms, shock timing, full-run differential replay against the loop reference, cell list versus brute force on whole runs, extreme parameters, invalid configs.
- `test_pipeline.py`: experiment expansion, schema validation (fail closed), failed runs recorded, confirmatory runs refused while unfrozen, freeze-record check, serial versus parallel equality, config to results to report integration, bootstrap against a simple loop, decision rule.
