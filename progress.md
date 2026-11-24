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
