<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24: Session M0 (bootstrap and feasibility) with M1 drafts

**Milestone:** M0, then M1 drafts. **Next bounded task at start:** create the control files and propose the protocol.

### State found

`git status`: `On branch main, nothing to commit, working tree clean`. One commit (`860dba4`, master prompt and the owner's licence package). `master_prompt.md` left unchanged.

### Commands run and actual outputs

- `sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize` -> `Apple M1 Pro`, `10`, `17179869184`.
- `sysctl -n hw.physicalcpu hw.perflevel0.physicalcpu hw.perflevel1.physicalcpu` -> `10`, `8`, `2`.
- `sw_vers` -> macOS 15.3.1, build 24D70.
- `df -h /Users/bechir` -> 129 GiB available of 460 GiB.
- `/usr/local/bin/python3 --version` -> `Python 3.12.1`.
- `.tools/py/bin/uv --version` -> `uv 0.9.5 (d5f39331a 2025-10-21)`.
- `.tools/py/bin/python -c "import typst, pypdf, PIL"` -> typst `0.15.0`, pypdf `6.20.0`, pillow `11.3.0`.
- `.tools/pandoc --version` -> `pandoc 3.6.3`.
- `helix/.tools/node/bin/node --version` (read-only) -> `v22.23.3`.
- `git --version` -> `git version 2.42.1`.
- `which tex pdflatex xelatex typst` -> not found for all four (exit 1).
- Literature: WebSearch and WebFetch on 8 sources; metadata checked with `curl https://api.crossref.org/works/<DOI>` for all 8 (matches recorded in `research/literature_review.md`). Failures: UPenn repository HTTP 403 and dblp bot block for Jadbabaie et al. (Crossref used instead); a first arXiv guess (`cs/0205078`) was an unrelated paper and was discarded.
- `.tools/py/bin/uv lock` -> `Using CPython 3.12.1 interpreter at: /Library/Frameworks/Python.framework/Versions/3.12/bin/python3`, `Resolved 25 packages in 54ms`, exit 0. Resolved: numpy 2.5.4, jsonschema 4.26.0, matplotlib 3.11.2, pytest 9.2.0, hypothesis 6.170.15 (with `exclude-newer = 2026-11-10`).
- `.tools/py/bin/uv sync --frozen` -> installed the locked set into `.venv/` (git-ignored), exit 0; `import numpy, jsonschema, matplotlib, swarm` printed `2.5.4 3.11.2 0.0.0`.
- `.venv/bin/pytest -q` -> `no tests ran in 0.57s` (no tests exist yet; this is not a passing test count).
- Toolchain smoke (exploratory, EXPL-000): pandoc to Typst, then `typst.compile` -> first attempt `TypstError: font fallback list must not be empty`; with `-V mainfont="Libertinus Serif"` -> 3-page PDF (outside the repo, scratchpad), page 1 inspected. `pandoc manuscript.md -t latex -s -o manuscript.tex` -> exit 0.

### Files created

`CLAUDE.md`, `roadmap.md`, `progress.md`, `README.md`, `CITATION.cff`, `pyproject.toml`, `uv.lock`, `src/swarm/__init__.py`, `src/README.md`, `tests/README.md`, `experiments/README.md`, `results/README.md`, `demo/README.md`, `articles/README.md`, `data/manifest.json`, `research/{decision_log.md, literature_review.md, protocol.md, feasibility.md, limitations.md, claims_register.csv, experiment_journal.jsonl, experiment_registry.csv}`, `research/paper/{manuscript.md, manuscript.tex, references.bib, supplementary.md, figures/README.md}`, `research/experiments/EXP-00{1,2,3}/protocol.md`, `research/publication/{artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md}`. Appended development commands to `CONTRIBUTING.md`.

### Decisions

DL-001 (owner's licence), DL-002 (pandoc to Typst toolchain), DL-003 (simulation-only data), DL-004 (dependency date cut-off).

### Not done, and why

- No simulator, tests or experiments: M2 work; confirmatory runs need the owner's freeze.
- No `report.md`, `config.json`, `run_manifest.json`, `metrics.csv` in EXP folders and no `manuscript.pdf`: creating them before results would be placeholders (master prompt 11.1 forbids it).
- Full texts of cited papers not read; disturbance-recovery literature not yet searched (M1).
- Dependency licences not yet listed (M6).

### Decisions the owner must make

1. Freeze or amend the draft protocol (arms, primary metric phi_post, SESOI 0.05, 10 seeds, grid). Freezing is the owner's (G-FREEZE).
2. Confirm the nondirectional H1 (or choose a direction before any run).
3. Confirm the simulation-only data scope (DL-003).
4. Confirm the toolchain decision (DL-002).

### Outstanding risks

Uninformative cells where A0 is disordered before the shock; periodic-boundary artefacts; A1 is one parameterisation; compute estimate unmeasured until EXP-001.

### Next action

M2: implement A0 with brute-force and cell-list neighbours, metrics and tests; then EXP-001 (exploratory) to measure runtime and paired-difference spread for the freeze decision.

## 2026-11-24: Session M2 (core implementation, exploratory EXP-001 work)

**Milestone:** M2. **Next bounded task at start:** implement A0 with brute-force and cell-list neighbours, metrics and tests, then A1 and A2, schemas, manifests, runner, report generator and CLI; then the exploratory EXP-001 smoke. The protocol is not frozen; no confirmatory run was made and no protocol was hash-frozen.

### State found

`git status`: clean on `main` at `33846c6`. Control files read in the order of `CLAUDE.md`.

### Implemented

`src/swarm/`: `config.py` (validated `SimConfig`, config hash), `rng.py` (init, noise and disturbance streams from one seed, shared across arms), `geometry.py`, `neighbors.py` (brute-force reference, cell list, topological k-nearest), `rules.py` (A0, then A1 and A2), `metrics.py`, `simulate.py`, `schema.py` (result and experiment schemas 1.0.0, validated at write and read), `manifest.py` (run manifests; freeze check, DL-005), `runner.py`, `analysis.py` (paired differences, stratified seed bootstrap, decision rule), `bench.py`, `report.py` (tables, figures, Markdown, PDF via pandoc to Typst with `-V mainfont="Libertinus Serif"`), `cli.py` (`smoke`, `run`, `bench`, `report`, `test`). Package version 0.1.0 (`uv lock`: only the project version changed). Reflecting walls, topological neighbours and the cohesion weight are implemented for EXP-003.

### Commands and actual outputs

- `uv run --frozen python -m pytest -q` (final): `107 passed` (counts per run of the suite this session: first run 1 failed / 6 passed with `-x`, then 6 failed / 99 passed, then 105 passed, then 107 passed after adding the A1-to-A0 reduction tests).
- Failures found and fixed: (1) `wrap_angle` changed in-range values by rounding (0.3 became 0.29999999999999982), DL-007; (2) my differential replay test compared the pre-shock heading at t_d although the trajectory stores the shocked state, a test error; (3) the bare `uv run pytest` entry point resolved to a Python without `hypothesis`; `uv run python -m pytest` is used and documented.
- `uv run --frozen python -m swarm.cli smoke` (built-in tiny config): `6 runs written to results/exploratory/cli-smoke (0 failed)`; `report --pdf` produced a 3-page PDF.
- Commit `57f66f3` (code), then EXP-001 smoke at that revision: 15 runs, mean 0.385 s per run (EXPL-001). Manifests showed `git_dirty: True` because the dirty check counted the untracked output files; fixed (untracked files ignored), outputs deleted and regenerated at `99cc0c4`.
- At `99cc0c4`, exploratory runs, all 0 failed: smoke 15 runs (20.6 s), bench 72 rows with 0 mismatched steps, burn-in scan 162 runs (34.0 s), long burn-in 36 runs (20.4 s), A1 diagnostic 16 runs (8.4 s). Reports via `swarm.cli report`; planning summary via `uv run python experiments/EXP-001/summarise_exploratory.py`. The smoke PDF (3 pages) was opened and inspected: tables, FIG-01 and FIG-02 render.
- `uptime` during these runs: load averages 32.27, 39.86, 22.07 on 10 cores (other processes), so the runtimes are inflated.

### Exploratory measurements (EXPL-001 to EXPL-006; not findings)

- Runtime per run (smoke cell, T = 1000): 0.385 s on the first run, 1.269 s under load with identical outputs. Projected EXP-002 (540 runs): 12.5 min serial under load, about 1.6 min with 8 workers. Budget 4 h: not binding.
- Seed spread: paired phi_post differences over 5 seeds in the smoke cell, A1 - A0 SD 0.059, A2 - A0 SD 0.058, against 0.2 assumed. Projected 95% CI half-width at 18 x 10 pairs about 0.009.
- Degenerate cases: A1 never orders (phi_pre 0.057 to 0.071 in all 18 cells; random level 0.071); the cohesion weight w_c = 1 causes it (EXPL-006). A0 is ordered in only 7 of 18 cells, never at eta = 0.5; some cells are still ordering after 500 steps. tau is degenerate where phi_pre is low.
- Neighbour search: cell list and brute force agree on every benchmarked step; N = 800, rho = 2, r = 1: 1.6 ms versus 16.3 ms per step.

### Decisions

DL-005 (freeze record and fail-closed runner), DL-006 (disjoint exploratory seeds; full-grid scans stop at t_d), DL-007 (angle wrapping), DL-008 (amendment proposals recorded, not applied).

### Files changed

New: `src/swarm/{config,rng,geometry,neighbors,rules,metrics,simulate,schema,manifest,runner,analysis,bench,report,cli}.py`, `tests/{conftest,reference,test_neighbors,test_rules,test_metrics_geometry,test_simulate,test_pipeline}.py`, `experiments/EXP-001/{smoke,bench,burnin_scan,burnin_long,a1_diagnostic}.json`, `experiments/EXP-001/summarise_exploratory.py`, `research/amendment_proposals.md`, `results/exploratory/` (EXP-001 outputs; burn-in per-run files git-ignored). Changed: `src/swarm/__init__.py`, `pyproject.toml`, `uv.lock`, `.gitignore`, `CONTRIBUTING.md` (development commands), `README.md`, `roadmap.md`, `progress.md`, `src/README.md`, `tests/README.md`, `experiments/README.md`, `results/README.md`, `research/{decision_log.md, experiment_journal.jsonl, experiment_registry.csv}`.

### Not done, and why

- No EXP-002 or EXP-003 configuration and no confirmatory run: the protocol is not frozen (G-FREEZE), and AP-1 and AP-2 should be decided first.
- No `research/experiments/EXP-001/report.md`: EXP-001's protocol is still a draft and its smoke design may change with AP-1 to AP-3; the generated exploratory reports live in `results/exploratory/`. The 12-part report is written when EXP-001 is run under its final protocol.
- Stratified bootstrap not applied to any data (exploratory data are not analysed as confirmatory).
- Runtime not re-measured on a quiet machine.
- No demo (M5).

### Decisions the owner must make

1. AP-1: A1 cohesion parameterisation (smaller w_c chosen from burn-in data, a turning-rate limit, or a reframed question).
2. AP-2: burn-in length and which cells are confirmatory; tau threshold floor.
3. AP-3: seed count (10 or 20), after a short exploratory re-check following 1 and 2.
4. The freeze itself (G-FREEZE), then the freeze record of DL-005.

### Outstanding risks

The primary contrast as drafted would measure a phase difference (AP-1). Runtime numbers are contaminated by machine load. The smoke spread comes from one cell.

### Next action

Owner decisions on AP-1 to AP-3; then one exploratory smoke run with the amended parameters (seed spread), then the freeze and M3.
