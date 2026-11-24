<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# SWARM: how order emerges without a leader (working title)

**Question.** How do local interaction rules affect collective coordination under disturbances?

**Status: M2 (core implementation), 2026-11-24.** The simulator, tests, result schema, runner, report generator and CLI exist. Only exploratory pre-freeze runs have been made; there is no finding. The research protocol is a draft awaiting the owner's freeze, with amendment proposals in `research/amendment_proposals.md`. This is a simulation study: nothing here is a claim about real animals, robots or distributed systems in general.

## What is planned

A 2-D self-propelled particle simulation comparing three rules under a matched heading disturbance:

- A0 alignment-only (baseline),
- A1 separation, cohesion and alignment,
- A2 centralized reference (global alignment).

Primary metric (draft): mean polarization over the 500 steps after the disturbance. See `research/protocol.md`.

| Experiment | Purpose | Status |
| --- | --- | --- |
| EXP-001 | Implementation verification and smoke matrix (exploratory) | exploratory run (pre-freeze) |
| EXP-002 | Primary comparison, 540 runs | planned |
| EXP-003 | Sensitivity analyses | planned |

## Repository map

- `master_prompt.md`: project specification (authority).
- `CLAUDE.md`, `roadmap.md`, `progress.md`: working rules, plan and journal.
- `research/`: protocol, feasibility, literature review, limitations, decision log, registries, experiment protocols, manuscript skeleton, publication checklists.
- `src/swarm/`: simulation package; `tests/`: test suite; `experiments/`: runnable configs; `results/exploratory/`: exploratory outputs.
- `demo/`, `articles/`: empty until M5.
- `data/manifest.json`: data provenance (synthetic only).

## Quick start (development)

```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen
```

    /Users/bechir/research/labs/.tools/py/bin/uv run python -m swarm.cli test
    /Users/bechir/research/labs/.tools/py/bin/uv run python -m swarm.cli smoke --config experiments/EXP-001/smoke.json
    /Users/bechir/research/labs/.tools/py/bin/uv run python -m swarm.cli report --results results/exploratory/EXP-001-smoke --pdf

All commands are listed in `CONTRIBUTING.md`.

## Data and licences

All data are synthetic (decision DL-003). Third-party dependencies keep their own licences (`uv.lock`).

## Licence

SWARM Source-Available Non-Commercial Research License v1.0 (`LicenseRef-SWARM-NC-Research-1.0`), a custom licence chosen by the owner; it is not an OSI-approved open-source licence. See `LICENSE`, `NOTICE.md`, `CLA.md`.

## Citation

See `CITATION.cff`.
