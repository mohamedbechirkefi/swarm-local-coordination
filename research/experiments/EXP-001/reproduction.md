<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-001 reproduction (exploratory)

## Environment

```
cd /path/to/swarm-local-coordination
../.tools/py/bin/uv sync --frozen --all-groups --all-extras   # uv.lock: Python 3.12.1, numpy 2.5.4
.venv/bin/python -m pytest -q                                  # 133 passed at 075cf7c
```

## Smoke matrix and metric validation (EXPL-008, revision 075cf7c)

```
.venv/bin/python experiments/provenance.py prelaunch results/exploratory/EXP-001-smoke-m3 --config experiments/EXP-001/smoke_m3.json
nice -n 10 .venv/bin/python -m swarm.cli smoke --config experiments/EXP-001/smoke_m3.json --workers 2
.venv/bin/python experiments/provenance.py finalize results/exploratory/EXP-001-smoke-m3 --exit-status 0
.venv/bin/python experiments/analyse_confirmatory.py check results/exploratory/EXP-001-smoke-m3
```

Expected result:

- 15 runs, 0 failed.
- The metric check reports 0 mismatches (tolerance 1e-12).
- `metrics.csv` and the phi series equal those in `results/exploratory/EXP-001-smoke/`.

## Pre-freeze scans (revisions 99cc0c4 and 2330f79)

```
uv run --frozen python -m swarm.cli bench --config experiments/EXP-001/bench.json
uv run --frozen python -m swarm.cli run --config experiments/EXP-001/burnin_scan.json
uv run --frozen python -m swarm.cli run --config experiments/EXP-001/burnin_long.json
uv run --frozen python -m swarm.cli run --config experiments/EXP-001/a1_diagnostic.json
uv run --frozen python -m swarm.cli run --config experiments/EXP-001/burnin_rule.json --workers 8
uv run --frozen python experiments/EXP-001/apply_burnin_rule.py
uv run --frozen python experiments/EXP-001/summarise_exploratory.py
```

## Outputs and checksums

- **Smoke (M3).** `results/exploratory/EXP-001-smoke-m3/`. The SHA-256 of every raw file is in `raw_manifest.json`, and one provenance row per run is in `provenance.csv`.
- **Pre-freeze.**
  - Committed: `results/exploratory/EXP-001-*`.
  - Git-ignored and regenerable: the per-run files of the burn-in scans, which are about 8 MB each.
- **Schema.** Run result schema 1.0.0 (`src/swarm/schema.py`).
