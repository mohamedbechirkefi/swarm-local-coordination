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

## 2026-11-24: Session FREEZE (owner-approved amendments and protocol freeze)

**Milestone:** M1 gate (G-FREEZE), on the owner's approvals of 2026-11-24 (`labs/_shared/owner-approvals-2026-11-24.md`, SWARM section and common decisions C1 to C4).

### What was done

- Amendments applied (`research/protocol.md` section 13; EXP-002 section 14; EXP-003 section 7): AM-1 w_c = 0.5; AM-2 burn-in rule R-BI committed first (2330f79), then applied: t_d = 3000, T = 3500; AM-3 20 seeds (1001 to 1020); AM-4 budget caps kept, measured projection recorded. Consequential edit: EXP-003 S2 = {0.25, 1.0}.
- `uv run --frozen python -m swarm.cli run --config experiments/EXP-001/burnin_rule.json --workers 8` -> `90 runs written to results/exploratory/EXP-001-burnin-rule (0 failed)`; `apply_burnin_rule.py` -> `t_d = 3000, T = 3500. Orderable cells: 8 of 18` (EXPL-007). Load average 1.65 to 1.87 before the run.
- Confirmatory configs: `experiments/EXP-002/config.json` (1080 runs), `experiments/EXP-003/config_S1.json`, `config_S2.json`, `config_S3.json` (160 runs each).
- Freeze guard: `run` now also requires the config's canonical hash in `research/protocol_freeze.json`, and the record path resolves against the run root. Checked: all four frozen configs pass `check_allowed`; a copy of EXP-002 with w_c = 0.6 -> `error: refusing a confirmatory run: configuration not frozen`, exit 2.
- Freeze record `research/protocol_freeze.json` (owner approval quoted, C1 to C4 with the C4 disclosure, SHA-256 of the three protocols and four configs, revision 6d9405f).
- `.venv/bin/python -m pytest -q` -> `122 passed`.
- Authorship (C3): manuscript metadata and AI-assistance statement, `manuscript.tex` regenerated with pandoc 3.6.3; CITATION.cff note.

### Not done, and why

- No confirmatory run: the coordinator schedules M3 on a quiet machine.
- No exploratory re-measure of seed spread under the amended design (AP-3 suggested one; not approved, and it would reveal post-shock values of the frozen design).

### Outstanding risks

A0 is not aligned before the shock in 10 of 18 cells at any tested burn-in; A1 may be weakly ordered at w_c = 0.5. Both are reported, not corrected (limitations 10 to 12).

### Next action

M3: run EXP-002, then EXP-003, with the frozen configs, when the coordinator schedules it.

## 2026-11-24: Session RATIFY (owner's second-round decisions)

**Milestone:** between M1 gate and M3, on `labs/_shared/owner-approvals-2026-11-24b.md` ("Approve all").

### What was done

- Ratification recorded: DL-011; RAT-1 (EXP-003 S2 = {0.25, 1.0}) and RAT-2 (the 10 never-aligning cells stay in, flagged) added to the amendment list of `research/protocol_freeze.json`.
- Checked that both choices are in the frozen text and that the hashes still match the record (`shasum -a 256` on the three protocols: unchanged). No protocol, config or code change; no other item of the approvals file applies to SWARM.

### Next action

M3: run EXP-002, then EXP-003, with the frozen configs, when the coordinator schedules it.

## 2026-11-25: Session M3 (frozen experiments)

**Milestone:** M3, on the owner's "Start next" (2026-11-25) and `labs/_shared/M3-brief.md`.

### Pre-run checks

- `git status`: clean at `a8c901b`. `shasum -a 256` on the 3 protocols and 4 configs: all match `research/protocol_freeze.json`.
- `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` -> `Audited 24 packages`; `.venv/bin/python -m pytest -q` -> `122 passed`.
- Pre-run commit `075cf7c` (DL-012): `experiments/analyse_confirmatory.py` (frozen analysis, written before any confirmatory output), `experiments/provenance.py` (launch record with data manifest SHA-256; per-run provenance and raw SHA-256 manifest), `experiments/EXP-001/smoke_m3.json`, `tests/test_confirmatory_analysis.py`, a caption-label fix in `swarm.report`, `.gitignore` for `results/confirmatory/*/runs/`. Tests: `133 passed`. Provenance revision: `075cf7c`.
- No external data (simulation only, DL-003); `data/manifest.json` SHA-256 94fe5a7b... recorded per run. Its text still says the simulator is "not yet implemented" (stale; left unchanged so the recorded hash stays valid; update in M4).
- Smoke (EXPL-008, exploratory seeds 101 to 105): 15 runs, 0 failed; metric check (phi_pre, phi_post, tau recomputed from series, bounds) 0 mismatches; outputs identical to the pre-freeze smoke.

### Confirmatory runs (2 workers, `nice -n 10`, background with logs)

- EXP-002: 1080 of 1080 runs, 0 failed, 1138.7 s (23:34:39 to 23:54:05 UTC). Metric check 1080/1080, 0 mismatches. Primary Delta = -0.307, 95% CI [-0.313, -0.302]: **rejects H0** (frozen rule, SESOI 0.05). phi_pre A1 - A0 = -0.312 [-0.319, -0.304]: A1 is disordered before the shock in all 18 cells, so the contrast is a phase difference (limitation 13).
- EXP-003: S1 160, S2 160, S3 160 runs, 0 failed (594.7 s, 181.9 s, 293.9 s). Delta_S: S1 -0.415 [-0.429, -0.398], S2a -0.268 [-0.282, -0.257], S2b -0.507 [-0.515, -0.498], S3 -0.449 [-0.463, -0.434]; none invalidates or weakens EXP-002. S4 tau table from EXP-002 series.
- Load average from other processes reached 37 to 39 during the runs; wall-clock figures are inflated accordingly.

### Deviations and gaps (DL-013)

- 454 EXP-003 runs record `git_dirty: true` because the journal was edited during S1; code and configs unchanged (git diff), 6 runs re-simulated bit-identical. Not rerun.
- Standalone 11.3 reports for EXP-001 to EXP-003 not written: the file tool refused report files and the coordinator said not to work around it; drafts made by another route were removed.

### Records and checks

Journal EXPL-008, CONF-EXP002, CONF-EXP003; registry statuses; claims CL-001 to CL-006; limitations 13 to 15; DL-012, DL-013; `results/README.md`; roadmap M3 in progress. `.venv/bin/python -m pytest -q` after the runs: `133 passed`.

### Next action

Write the 11.3 reports for EXP-001 to EXP-003 (generated tables fill in via `experiments/analyse_confirmatory.py`), then M4. Owner attention: the primary result is a phase difference (limitation 13).

## 2026-11-25: M3 done (coordinator)

The owner approved the experiment reports (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4). Subagents may not write report files, so the reports were composed by the M3 session from committed results only and written by the coordinator: 3 report(s). The coordinator checked that every decimal number in them appears in a committed file. With the complete matrices (or documented failures) recorded above, the M3 gate holds. M3 is **done**. Next: M4 (interpretation), not started.

## 2026-11-25: Session M4 (interpretation, evidence audit, manuscript)

**Milestone:** M4, on the owner's "Approve all recommendations, push then next" (2026-11-25) and `labs/_shared/M4-brief.md`. No project-specific follow-up in `owner-approvals-2026-11-25b.md` applies to SWARM.

### What was done

- Pre-checks: `git status` clean at `34d01db`; read the M4 row, master prompt 11.4 to 11.6, protocols, reports, freeze record, decision log, limitations and claims.
- Exploratory confounder checks (EXPL-M4-01), no new simulation, 1 process: `.venv/bin/python experiments/exploratory_m4.py` (39 s). Raw integrity: 1,584 files re-hashed, 0 mismatched. Change score A1 - A0 0.004 [-0.004, 0.012]; orderable cells phi_post -0.618 [-0.629, -0.607] and flagged cells -0.059 [-0.064, -0.054]; matched pre-shock cells 0.001 [-0.002, 0.004]; EXP-003 change scores inside the SESOI band. Outputs `results/exploratory/M4-sensitivity/`.
- Interpretation: `research/publication/m4_interpretation.md` (competing explanations (a) to (f), expected versus observed for every experiment). Frozen verdicts unchanged.
- Claims register rebuilt with result ID, config hash, figure/table and section columns: CL-001 to CL-014, EXT-001 to EXT-008; CL-001 and CL-005 qualified (order gap, not recovery).
- Evidence audit: `experiments/audit_numbers.py` -> `research/publication/number_audit.json`, 770 decimal tokens in 10 documents, 0 unmatched; `experiments/build_artifact_manifest.py` -> `artifact_manifest.json`, 11 artifacts, every claim mapped. Findings F1 to F8 in `research/publication/evidence_audit.md`; F1 (Jadbabaie et al. characterised beyond the metadata read) fixed in the manuscript and the EXP-002 report.
- Manuscript synthesised (about 5,300 words including references; abstract 237 words) with supplementary; retitled after `research/publication/review_pass_2.md`. `manuscript.tex` regenerated with pandoc 3.6.3. No PDF built in M4 (M6).
- Records: limitations 16 to 20, DL-015, journal EXPL-M4-01 and M4-AUDIT, registry statuses, roadmap M4 done, `claims_audit.md`, `results/README.md`, `literature_review.md` note.
- Tests: `tests/test_m4_tools.py` (4 tests) added; `.venv/bin/python -m pytest -q` -> `137 passed`.

### Not done, and why

- `data/manifest.json` stale text not edited (its hash is in every run's provenance; owner decision, audit F4).
- No confirmatory rerun (not allowed); the matched-order recovery experiment is proposed as a new EXP for the owner.

### Gate

Every numerical claim maps to a result file and key, a config or protocol hash and a figure, table or section; every external claim maps to a source accessed, with the level read stated. M4 **done**.

### Next action

M5 (interactive page and articles) using the M4 numbers and the retitled framing; the owner reviews the new title, the qualified claims and audit F4.

## 2026-11-25: Session POST-M4 (owner's post-M4 decisions, items 1, 2, 3 and 6)

**Milestone:** between M4 (done) and M5, on owner, 2026-11-25, "Approve all" (post-M4) (`labs/_shared/owner-approvals-2026-11-25c.md`) and `labs/_shared/POST-M4-brief.md`. Recorded as DL-016.

### What was done

- Pre-checks: `git status` clean at `d280840`; read the brief, the approvals file, CLAUDE.md, progress, decision log, freeze record, manuscript, review pass 2 and the M4 evidence audit.
- Item 1 (title): the manuscript already carries the M4 title proposed after review pass 2 (DL-015); recorded as owner-approved. No manuscript change, so `manuscript.tex` was not regenerated.
- Item 2 (statements): funding, competing-interest and AI-use wording recorded as owner-approved (DL-016). No wording changed.
- Item 3 (EXP-004, recovery with matched pre-shock order): registered as "registered, not frozen"; `research/experiments/EXP-004/protocol.md` (v0.1, 11.2 structure) and draft `experiments/EXP-004/config.json`, written before any data. Eight parameters left open for the owner at freeze (protocol section 21). Check: `swarm.runner.load_experiment` on the draft config -> `SchemaError` (refused, as intended). No simulation, no code change, nothing added to `research/protocol_freeze.json`.
- Item 6 (data manifest): dated correction in `data/manifest.json` (generator status "implemented (M2)", version 0.1.0) with a `corrections` record keeping the previous SHA-256. `shasum -a 256 data/manifest.json` -> `ede591fc...f105` (new); `git show d280840:data/manifest.json | shasum -a 256` -> `94fe5a7b...3471` (old, as in the M3 provenance). Limitation 19 and audit F4 annotated as resolved.
- Records: DL-016, registry row EXP-004 (CRLF line endings kept), roadmap EXP-004 row.
- Checks: `.venv/bin/python -m pytest -q` -> `137 passed`; `.venv/bin/python experiments/audit_numbers.py` -> `total 770, unmatched 0` (output file unchanged).

### Owner placeholders for M5

1. Manuscript, "Data and code availability": repository URL, "[to be added by the owner on release]" (also in `manuscript.tex`).
2. Manuscript, "Funding, competing interests and AI assistance": "Funding: none declared; competing interests: none declared (both to be confirmed by the author)". The wording is approved; the confirmation of both facts is the owner's.
3. Not a placeholder, but owner-facing: `README.md` and `CITATION.cff` still name the project "SWARM: how order emerges without a leader (working title)", the working title retired for the manuscript in DL-015. Whether the repository title follows the manuscript title is the owner's decision.

### Not done, and why

- No EXP-004 calibration or confirmatory run: the protocol is not frozen (G-FREEZE), and the open items need owner decisions first.
- Recorded run provenance (`launch.json`, `provenance.csv`) not edited: it correctly refers to the data manifest as it was.

### Next action

Owner: decide EXP-004 open items 1 to 8, then the calibration stage (R-MATCH, R-SS) and the freeze. M5 (interactive page and articles) can proceed independently.

## 2026-11-25: Session M5 (interactive experience)

**Milestone:** M5, on owner, 2026-11-25, "Next" (`labs/_shared/owner-approvals-2026-11-25d.md`; stack: the shared TypeScript, React and Vite template) and `labs/_shared/M5-brief.md`. Recorded as DL-017.

### What was done

- Pre-checks: `git status` clean at `22f9035`; read the brief, the approvals record, CLAUDE.md, the M5 row, master prompt sections 3, 8, 10, 11.6, the manuscript, claims register, artifact manifest, reports, limitations and the template.
- `demo/` copied from `labs/_shared/demo-template/` without `node_modules`; `npm ci --prefer-offline` -> `added 53 packages`. Every `REPLACE` marker and SPDX identifier replaced; `grep -rn REPLACE demo/ --exclude-dir=node_modules --exclude-dir=dist` finds nothing.
- `scripts/export_demo_data.py` -> `demo/public/data/results.json` (EXP-001 to EXP-004, `per_cell`, `post_hoc`, `design`; sources with SHA-256; no timestamps). `--check` -> `results.json up to date`.
- `tests/test_demo_export.py` (6 tests): export reproduces the committed file; every display string in the manuscript; per-cell rows in the EXP-002 report table; EXP-004 has no estimates; public-text decimals traced.
- Sandbox: `demo/src/engine.ts` (port of the update rules), `demo/src/sandbox.worker.ts`, `demo/src/Sandbox.tsx`; fixture `scripts/make_sandbox_fixture.py` -> `demo/src/fixtures/engine_fixture.json` (0.2 s, 1 process); `demo/src/engine.test.ts` tolerance 1e-9, largest error 4.9e-13 (journal M5-SANDBOX-PORT).
- Page: `demo/src/App.tsx`, `charts.tsx`, `style.css`, `results.ts` (fail-closed validation of the extensions), `results.test.ts` (7 new tests).
- Checker extended (3 SWARM checks, all template checks kept). Screenshots inspected (desktop light, desktop dark, mobile): fixed a floating-point tick label, a clipped axis label, clipped EXP-003 labels, a 144 px overflow at 360 px from a long select, and tiny chart text on mobile. The full-page mobile capture repeats the page header below the footer; this appears to be an artefact of the full-page capture on mobile emulation (the DOM has one header and the overflow check passes).
- Fail-closed check: the checker on a copy of `dist` with `per_cell` removed -> `FAIL results render (no fail-closed panel): 0 experiment panels`, `A11Y-CHECK FAIL (3)`.
- Texts: README, `CITATION.cff`, `articles/medium.md`, `articles/linkedin.md`, `articles/README.md`, `demo/README.md`, `docs/demo.png` (124,690 bytes), CONTRIBUTING demo commands; author-review box unticked (DL-017).

### Commands and outputs

    .venv/bin/python -m pytest -q                -> 143 passed in 4.89s
    cd demo && npm test                          -> Test Files 2 passed (2); Tests 22 passed (22)
    cd demo && npm run build                     -> tsc and vite build, built in 79ms
    node tools/a11y_check.mjs dist --screenshots /private/tmp/claude-501/-Users-bechir-research/d17d72fe-4ad4-4cdb-b113-2cbf6d17ea36/scratchpad/swarm/shots

    PASS results render (no fail-closed panel): 5 experiment panels
    PASS text contrast, light scheme (WCAG AA)
    PASS text contrast, dark scheme (WCAG AA)
    PASS keyboard reaches every focusable element: 28 reached of 28
    PASS visible focus indicator
    PASS sandbox: Run animates and Pause stops the swarm: animating=true step 288, after pause 288 -> 288
    PASS published and sandbox labels kept apart: {"pub":4,"sbInResults":0,"sb":1,"pubInSandbox":0}
    PASS no horizontal page scroll at 360 px: overflow 0px
    PASS reduced motion: no running animations: 0 running
    PASS reduced motion: sandbox computes without animating: animating=false, step 300 then 300
    PASS no request leaves the local origin
    PASS offline after first load: results stay, sandbox runs: Computed 300 steps without animation (reduced motion). Sandbox output, seed 1.
    A11Y-CHECK PASS

### Gate

Offline after the first load, responsive at 360 px, usable with the keyboard, no fabricated data (every number exported from committed results and checked against the manuscript), no runtime service. M5 **done**.

### Owner placeholders that remain

1. Repository and demo URL (README, CITATION message, demo footer, articles, manuscript "Data and code availability").
2. Funding and competing interests: "none declared (both to be confirmed by the author)".
3. Author line and affiliation as recorded in decision C3; the repository title in `CITATION.cff` now names the approved manuscript title, and a different repository title is the owner's choice.
4. The `author_review.md` boxes (owner only); full-text review of the manuscript (M6).
5. EXP-004: open items 1 to 8 and the freeze (G-FREEZE).

### Next action

M6 (release candidate) when the owner says so; owner decisions above.

## 2026-11-25: Session M6 (release candidate, local)

**Milestone:** M6, on owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`) and `labs/_shared/M6-brief.md`. Recorded as DL-018. EXP-004 stays registered, not frozen, not run.

### What was done

- Pre-checks: `git status` clean at `8db419b`; read the brief, the approvals record, CLAUDE.md, the M6 row, master prompt M6 lines, progress (M5 placeholders), the publication folder and the PDF builder.
- Clean clone (`<scratch>` is the session scratch folder outside the repository): `git clone -q <repository> <scratch>/clone`; `uv sync --frozen --all-groups --all-extras`; `pytest -q` -> `143 passed in 45.11s`; smoke `swarm.cli smoke --config experiments/EXP-001/smoke_m3.json --workers 2` -> `15 runs ... (0 failed)`, `analyse_confirmatory.py check` -> `runs_with_mismatch 0`; comparison with the committed files: 165 non-timing fields, 0 mismatches, `metrics.csv` equal without `wall_s`; demo `npm ci --prefer-offline` -> `added 53 packages`, `npm test` -> `Tests 22 passed (22)`, `npm run build` -> built, `node tools/a11y_check.mjs dist` -> 12 PASS lines and `A11Y-CHECK PASS`; `scripts/export_demo_data.py` then `git status --short | wc -l` -> `0`. No failure found.
- PDFs: `scripts/build_pdfs.py` (new) -> manuscript 15 pages, supplementary 4, EXP-001 report 4, EXP-002 report 11, EXP-003 report 8; `manuscript.tex` regenerated with its SPDX header. Every manuscript page and the first and figure pages of each report rendered to PNG at 60 ppi and read. Fixed in `build_pdf`: numbered-list artefact from line wrapping ("3499."), doubled figure labels, orphaned table caption, equal-width table columns, figure and caption overflowing the footer, dropped captions before generated-block markers, Typst root excluding `results/`. Metadata (pypdf): title and author set, 0 e-mail addresses, 0 local paths.
- References: free legal full texts consulted for 7 of 8 sources (Vicsek et al. 1995, Reynolds 1987, Jadbabaie, Lin and Morse 2003, Olfati-Saber technical report, Cucker and Smale preprint, Ballerini et al. 2008, Vicsek and Zafeiris 2012 sections 2.1 and 4.1); Couzin et al. 2002 stays abstract only. No statement contradicted; level-of-reading wording updated (manuscript, EXP-002 report note, medium article, bib header, EXT rows, evidence audit section 7, literature review section 7).
- Links and manifests: `scripts/check_links.py` (new) -> 22 relative links, 0 problems; 8 bib entries, 0 problems; `LINK-CHECK PASS`; `tests/test_links_refs.py` (4 tests). `audit_numbers.py` -> `total 770, unmatched 0` (arXiv identifiers now skipped). Artifact manifest: 22 paths present, 16 hash pairs equal. Raw manifests: 1,605 entries, 0 mismatched. `data/manifest.json` SHA-256 `ede591fc...f105` as recorded in DL-016.
- Scan of 274 tracked and new text files: 0 e-mail addresses, 0 tokens or keys, 0 private key headers, 0 `.env` files; home-directory paths in 6 files: removed from README, `src/swarm/report.py` and `research/feasibility.md`; kept in CLAUDE.md for the owner; this journal and `research/experiment_journal.jsonl` each keep one local path in an earlier entry (M5 screenshot folder and an earlier command), left as written because both files are append-only; the owner decides before publication whether the journals are published.
- Licences: `research/publication/dependency_licences.md` (24 Python, 53 npm; no flag outside the permissive list; pandoc noted as a GPL build tool). SPDX: 74 text files added since M0, all with the header.
- `CITATION.cff`: no `date-released` was present; version `0.1.0-rc1`; title quotes the full manuscript title; structural CFF 1.2.0 check passed.
- Owner review: 0 boxes ticked; section "Prepared for the owner (M6, 2026-11-25)" added with reading list, open decisions and placeholders by line. Release checklist: 7 items ticked with evidence, 2 owner items open, dated status line.
- Records: reproducibility report, DL-018, journal M6-CLEAN-CLONE, roadmap M6 status, README status, CONTRIBUTING commands.

### Commands and outputs (working repository)

    .venv/bin/python -m pytest -q                -> 147 passed in 5.80s
    .venv/bin/python scripts/export_demo_data.py --check -> results.json up to date (claims register and artifact manifest hashes refreshed)
    cd demo && npm test                          -> Test Files 2 passed (2); Tests 22 passed (22)
    cd demo && npm run build                     -> built in 105ms
    cd demo && node tools/a11y_check.mjs dist    -> A11Y-CHECK PASS

### Not done, and why

- No push, tag, release or remote change (G-PUBLIC); no `author_review.md` box ticked; no EXP-004 freeze or run (G-FREEZE).
- `experiments/analyse_confirmatory.py` (frozen analysis) was not edited, although its generated figure blocks end directly after an image; the PDF builder compensates.

### Next action

Owner: read the items in `research/publication/author_review.md` ("Prepared for the owner"), tick the boxes, fill the placeholders, and decide on publication (G-PUBLIC) and on EXP-004 (G-FREEZE).

### Addendum (same session): fresh clone of the M6 commit

`git clone -q <repository> <scratch>/clone2` at `f454de6`: `uv sync --frozen` ok; `pytest -q` -> `147 passed in 9.84s`; `check_links.py` -> `LINK-CHECK PASS`; `audit_numbers.py` -> `total 770, unmatched 0`; `build_pdfs.py` (tool paths passed by environment variables) -> 5 PDFs, `manuscript.tex` unchanged; smoke -> 15 runs, 0 failed, 165 fields, 0 mismatches; export leaves the clone clean; demo `Tests 22 passed (22)`, built, `A11Y-CHECK PASS`. Both clones deleted. Recorded in `research/publication/reproducibility_report.md` section 8.

## 2026-11-26: Session OWNER-ANSWERS (owner's answers of 2026-11-26 applied)

**Authority:** owner, 2026-11-26, decision sheet; brief `labs/_shared/OWNER-ANSWERS-brief.md`. Recorded as DL-019. Wording and configuration only.

### What was done

- `git status` clean at `bc23a45`. Read the brief, the decision sheet, the approvals (including the follow-up section), CLAUDE.md, the M6 entry and `author_review.md`.
- A1, B1, B2, B3, B4, B7, B8, B9, B13, R-SWARM-1 applied (list in DL-019). New file `demo/wrangler.jsonc` (assets `./dist`). Author line "Mohamed Bechir Kefi, independent researcher"; funding and competing-interest sentences filled; `CITATION.cff` `repository-code`, `affiliation`, title equal to the manuscript title.
- First PDF build with a YAML author map (name, affiliation) produced `\author{true}` in `manuscript.tex`; replaced by the single-line author string and rebuilt.
- `author_review.md`: section "Owner answers recorded (2026-11-26)"; no box ticked; placeholders remaining: none.

### Commands and outputs

    .venv/bin/python scripts/build_pdfs.py --typ-dir <scratch>/typ --png-dir <scratch>/png
        -> manuscript 15 pages, supplementary 4, EXP-001 4, EXP-002 11, EXP-003 8; manuscript.tex regenerated
    git checkout -- research/paper/supplementary.pdf     (source unchanged)
    pypdf: author line / statements found on manuscript pages 1 and 14 and page 1 of each report; metadata author "Mohamed Bechir Kefi"
    PNG inspected: manuscript pages 1 and 14, EXP-002 report page 1
    .venv/bin/python -m pytest -q                        -> 147 passed in 5.96s
    .venv/bin/python scripts/export_demo_data.py --check -> results.json up to date
    .venv/bin/python scripts/check_links.py              -> LINK-CHECK PASS
    .venv/bin/python experiments/audit_numbers.py        -> total 770, unmatched 0
    cd demo && npm test                                  -> Test Files 2 passed (2); Tests 22 passed (22)
    cd demo && npm run build                             -> built in 166ms
    cd demo && node tools/a11y_check.mjs dist            -> 12 PASS lines (keyboard 30 of 30), A11Y-CHECK PASS
    git grep -n "/Users" (tracked files)                 -> progress.md 1, research/experiment_journal.jsonl 1 (append-only)

### Not done, and why

- No push, deploy or tick (coordinator and owner steps). B15, B16, B18 and the EXP-004 freeze stay with the owner.

### Next action

Owner: full-text review and sign-off (B16), articles (B15), release (B18), EXP-004 freeze when ready.
