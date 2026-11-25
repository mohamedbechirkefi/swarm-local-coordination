<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-002 reproduction

## Environment

```
cd /path/to/swarm-local-coordination
git checkout 075cf7c        # provenance revision of every run (in a separate clone)
../.tools/py/bin/uv sync --frozen --all-groups --all-extras   # uv.lock: Python 3.12.1, numpy 2.5.4, matplotlib 3.11.2, jsonschema 4.26.0
.venv/bin/python -m pytest -q                                  # 133 passed
```

## Runs (the runner refuses the config unless its canonical hash is in research/protocol_freeze.json)

```
.venv/bin/python experiments/provenance.py prelaunch results/confirmatory/EXP-002 --config experiments/EXP-002/config.json
nice -n 10 .venv/bin/python -m swarm.cli run --config experiments/EXP-002/config.json --workers 2
.venv/bin/python experiments/provenance.py finalize results/confirmatory/EXP-002 --exit-status 0
```

## Analysis, figures and generated tables

```
.venv/bin/python experiments/analyse_confirmatory.py exp002
.venv/bin/python -m swarm.cli report --results results/confirmatory/EXP-002
```

Running `exp002` writes:

- `results/confirmatory/EXP-002/analysis/`: `analysis.json`, `per_cell.csv`, `paired_differences_phi_post.csv`, `fig_exp002_01_forest.png` and `fig_exp002_02_timeseries.png`;
- the tables between the GENERATED markers in `report.md`.

## Outputs, checksums, tolerance

- **Raw per-run files.** `results/confirmatory/EXP-002/runs/*.json`, 1080 files, about 88 MB.
  - They are git-ignored. On the same platform they are regenerated bit for bit by the commands above.
  - The SHA-256 of every raw file is in `results/confirmatory/EXP-002/raw_manifest.json`.
- **Committed alongside.** `metrics.csv`, `run_manifest.json`, `execution.json`, `launch.json`, `provenance.csv` and `run.log`.
- **Expected values.**
  - 1080 runs, 0 failed.
  - Metric check: 0 mismatches at tolerance 1e-12.
  - Delta -0.307 [-0.313, -0.302] (bootstrap seed 20261124, 10,000 resamples).
- **Schema.** Run result schema 1.0.0.
- **Other platforms.** Floating-point results may differ in the last digits on another platform; this is documented and not eliminated (limitation 8).
