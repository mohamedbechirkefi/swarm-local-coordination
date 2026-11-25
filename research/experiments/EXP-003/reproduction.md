<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-003 reproduction

## Environment

As for EXP-002:

- the provenance revision `075cf7c`;
- `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`;
- `.venv/bin/python -m pytest -q`, which gives 133 passed.

## Runs (each config must match its canonical hash in research/protocol_freeze.json)

```
for c in S1 S2 S3; do
  .venv/bin/python experiments/provenance.py prelaunch results/confirmatory/EXP-003-$c --config experiments/EXP-003/config_$c.json
  nice -n 10 .venv/bin/python -m swarm.cli run --config experiments/EXP-003/config_$c.json --workers 2
  .venv/bin/python experiments/provenance.py finalize results/confirmatory/EXP-003-$c --exit-status 0
done
```

## Analysis (needs the EXP-002 runs and its analysis first; S2 and S4 use EXP-002 outputs)

```
.venv/bin/python experiments/analyse_confirmatory.py exp002
.venv/bin/python experiments/analyse_confirmatory.py exp003
for c in S1 S2 S3; do .venv/bin/python -m swarm.cli report --results results/confirmatory/EXP-003-$c; done
```

Running `exp003` writes:

- `results/confirmatory/EXP-003-analysis/analysis.json` and `fig_exp003_01_sensitivity.png`;
- the tables between the GENERATED markers in `report.md`.

## Outputs, checksums, tolerance

- **Raw per-run files.** `results/confirmatory/EXP-003-S{1,2,3}/runs/*.json`, 160 files each, about 13 MB per condition.
  - They are git-ignored and regenerated bit for bit on the same platform.
  - The SHA-256 of every raw file is in each `raw_manifest.json`.
- **Committed alongside.** `metrics.csv`, `run_manifest.json`, `execution.json`, `launch.json`, `provenance.csv` and `run.log`.
- **Expected values.**
  - 160 runs per condition, 0 failed.
  - Metric check: 0 mismatches at tolerance 1e-12.
  - Delta_S as in `report.md` section 8 (bootstrap seed 20261124, 10,000 resamples).
- **Provenance note.** The committed run manifests of 454 runs record `git_dirty: true` (DL-013). A clean reproduction at `075cf7c` records `false` but is otherwise expected to give identical outputs.
