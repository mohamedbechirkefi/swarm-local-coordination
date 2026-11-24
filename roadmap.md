<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# SWARM roadmap

Five focused development days (planning estimate). Status values: not started, in progress, done, blocked. Nothing is marked done until its gate is checked.

| ID | Milestone | Depends on | Acceptance criteria (gate) | Priority | Effort | Status | Blockers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M0 | Bootstrap and feasibility | none | Control files and 11.1 tree exist; feasibility audit with commands; source audit; budget, scope and fallback explicit; zero-cost toolchain confirmed; dependency lock produced. Gate: the owner can understand question, cost and exclusions. | P0 | 0.5 day | done (2026-11-24), pending owner review | none |
| M1 | Research and preregistration | M0 | Evidence review extended (disturbance-recovery literature); formal model finalised; baselines justified; `research/protocol.md` and EXP-001..003 protocols complete per 11.2; registry populated; manuscript skeleton; fixture manifest. Gate: owner freezes confirmatory protocols (hash recorded) before EXP-002/003 run; exploratory work visibly separated. | P0 | 0.5 day | in progress (drafts written 2026-11-24) | owner freeze (G-FREEZE); owner decisions listed in `progress.md` |
| M2 | Core implementation | M1 drafts (freeze not needed for code) | A0 reference first, then A1, A2; cell list and brute-force reference; metrics; seeded RNG streams shared across arms; versioned JSON result schema with validation; run manifests; report generator; CLI (smoke, run, analyse, report, test). Unit, property, differential, boundary and determinism tests run and pass; hand-computed examples. Gate: correctness before UI. | P0 | 1 day | done (2026-11-24), pending owner review: all acceptance items implemented and 107 tests pass; `analyse` is a module (`swarm.analysis`), not a CLI verb; the pooled bootstrap is wired into reports at M3 | none |
| M3 | Experiments | M2; owner decisions on AP-1, AP-2; owner freeze for EXP-002/003 | EXP-001 passes, then EXP-002 and EXP-003 full matrices; raw machine-readable outputs; figures with uncertainty; every run, failure and deviation recorded; each report generated as its experiment finishes. Gate: complete planned matrix or documented failure, no silently dropped runs. | P0 | 0.75 day | not started | freeze |
| M4 | Interpretation | M3 | Confounders inspected; sensitivity analysis; expected vs observed; claims register and limitations; all reports complete; evidence audit; manuscript synthesised with contradictory results. Gate: every numeric claim maps to result ID, config and figure; every external claim to a verified source. | P0 | 0.75 day | not started | none |
| M5 | Interactive experience | M4 results (demo sandbox can start after M2) | Static page: real-time swarm, disturbance control, metric timeline; published vs sandbox vs hypothetical clearly separated; keyboard, reduced motion, mobile, empty/error/loading states; offline after load; Web Worker. Articles drafted (Medium, LinkedIn). Gate: offline, responsive, accessible, no fabricated data, identical numbers across demo, paper, reports and articles. | P1 (cut first if late) | 1 day | not started | none |
| M6 | Release candidate | M4, M5 | Clean clone; `uv sync --frozen`; tests; smoke reproduction; demo build; data manifest and link checks; secret and licence scan; manuscript and report PDFs compiled and inspected; owner review checklist. Gate: verified facts only; owner approves any publication. | P0 | 0.5 day | not started | owner approval (G-PUBLIC) |

## Registered experiments

| ID | Title | Depends on | Status |
| --- | --- | --- | --- |
| EXP-001 | Implementation verification and smoke matrix (exploratory) | M2 | exploratory run 2026-11-24 (pre-freeze; V1-V4 pass; amendment proposals AP-1 to AP-5 in `research/amendment_proposals.md`) |
| EXP-002 | Local rules and recovery from a heading disturbance (primary) | EXP-001 | planned (protocol draft, awaiting owner freeze) |
| EXP-003 | Sensitivity of the EXP-002 contrast | EXP-001 | planned (protocol draft, awaiting owner freeze) |

## Cut order if the five-day target is threatened

1. Demo polish and secondary visuals (M5). 2. EXP-003 reduced to S1. 3. EXP-002 grid reduced to r = 1.0 (before freeze only). Scientific reporting, controls and evidence audits are never cut.
