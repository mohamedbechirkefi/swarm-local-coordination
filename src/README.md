<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# src/

Python package `swarm` (M2). Each concern is a separate module:

| Module | Role |
| --- | --- |
| `config.py` | Typed, validated `SimConfig` (units in docstring); canonical config hash. |
| `rng.py` | Seeded RNG streams (init, noise, disturbance) spawned from one seed, shared across arms. |
| `geometry.py` | Angle wrapping, minimum-image displacement, torus wrap, wall reflection. |
| `neighbors.py` | Brute-force reference, cell list, topological k-nearest; distance-evaluation counts. |
| `rules.py` | A0 alignment-only, A1 separation/cohesion/alignment, A2 centralized reference. |
| `metrics.py` | Polarization, largest connected component, recovery time, collision rate. |
| `simulate.py` | One run from a config to recorded series and metrics. |
| `schema.py` | Versioned JSON schemas (result 1.0.0, experiment 1.0.0), validated at export and import. |
| `manifest.py` | Run manifests (git revision, versions, OS, CPU, runtime, peak memory); protocol-freeze check. |
| `runner.py` | Experiment expansion, execution (serial or parallel), serialization, gate checks. |
| `analysis.py` | Paired differences, stratified seed bootstrap, decision rule. |
| `bench.py` | Neighbour-search benchmark. |
| `report.py` | Tables, figures, Markdown report and PDF (pandoc to Typst) from result files. |
| `cli.py` | `smoke`, `run`, `bench`, `report`, `test`. |
