<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-001 report: implementation verification and smoke matrix

**EXPLORATORY.** EXP-001 is exploratory by design (protocol section 4). Nothing here is a finding, and nothing here is pooled with EXP-002 or EXP-003. All results are simulated.

## 1. Identification

- Experiment: EXP-001, "Implementation verification and smoke matrix". Status: exploratory, complete. The runs before the freeze were on 2026-11-24 (EXPL-001 to EXPL-007), and the M3 smoke re-run was on 2026-11-25 (EXPL-008).
- Protocol: `research/experiments/EXP-001/protocol.md` (draft 0.1). EXP-001 is exploratory and was not hash-frozen.
- Author: Mohamed Bechir Kefi, independent researcher (owner-approved metadata, DL-010; owner, 2026-11-26, decision sheet, B3). The AI was a research and development assistant, not an author.
- Code revisions: the pre-freeze runs used `99cc0c4` (smoke, benchmark, burn-in scans, A1 diagnostic) and `2330f79` (burn-in rule scan). The M3 smoke re-run used `075cf7c` with a clean tree.
- The report was written after M3 from committed results only, on the owner's approval of 2026-11-25 (DL-014).

## 2. Executive summary

- **Question.** Is the simulator correct and fast enough to run EXP-002 as specified?
- **Method.**
  - Differential, property, determinism and hand-computed tests (V1 to V4).
  - A 15-run smoke matrix.
  - A neighbour-search benchmark.
  - Burn-in scans, including the A0-only scan that applied the pre-stated burn-in rule R-BI.
- **Outcome.**
  - V1 to V4 pass.
  - The cell list and brute force agree on every benchmarked step.
  - Runtime is far below budget.
  - The M3 re-run of the smoke matrix reproduces the pre-freeze smoke outputs exactly, and every metric recomputes from the stored series.
  - The scans exposed two design problems that led to the owner's amendments AM-1 to AM-4 before the freeze:
    - A1 never ordered at the draft cohesion weight w_c = 1.
    - A0 was disordered before the shock in many cells.
- **Principal caveat.** The smoke cell's primary values were seen before the freeze, under the draft design. The C4 disclosure is in `research/protocol_freeze.json`.

## 3. Rationale

Verification comes first (master prompt section 10, "correctness before UI"). Three kinds of bug could each create spurious arm differences in EXP-002:

- index bugs across the periodic wrap;
- RNG streams that are not shared across arms;
- angle-averaging errors near +/- pi.

## 4. Hypotheses (verification, not scientific)

- **V1.** Cell-list neighbour sets equal brute-force sets exactly.
- **V2.** Repeated runs are bit-identical.
- **V3.** The bounds hold: |heading| = 1, 0 <= phi <= 1, 0 < C <= 1, and positions stay in [0, L).
- **V4.** Hand-computed 2- and 3-agent examples match the update rule.

Disconfirmation: any mismatch stops the pipeline (stop rule "engine incorrect").

## 5. Methodology

- **Smoke matrix.** 3 arms (A0, A1, A2) x 1 cell (rho = 1, eta = 0.3, r = 1, N = 200) x seeds 101 to 105, with T = 1000, t_d = 500, W = 500 and the draft w_c = 1.
  - Config: `experiments/EXP-001/smoke.json`.
  - The M3 copy `smoke_m3.json` is identical except for its output directory and description.
  - Seeds 101 to 105 are disjoint from the confirmatory seeds 1001 to 1020.
- **Other configurations.** The benchmark, burn-in scan and diagnostic configurations are `experiments/EXP-001/*.json`.
- **Hardware and software.** Apple M1 Pro (10 cores, 16 GB), macOS 15.3.1, Python 3.12.1, numpy 2.5.4.

## 6. Implementation verification

- **Test suite.**
  - The suite covers V1 to V4, plus property, differential, boundary and determinism tests.
  - 107 tests passed at M2 and 122 at the freeze.
  - 133 passed at the M3 revision `075cf7c`, including tests of the confirmatory-analysis and provenance helpers.
- **Benchmark (EXPL-003).** 72 rows, with 0 mismatched steps between cell list and brute force (`results/exploratory/EXP-001-bench/`).
- **M3 metric validation (EXPL-008).**
  - For all 15 smoke runs, phi_pre, phi_post and tau were recomputed from the stored phi series and the bounds were checked.
  - Result: 15 runs checked, 0 mismatches.
- **M3 reproduction (EXPL-008).** The 15 runs re-executed at `075cf7c` match the pre-freeze run at `99cc0c4` exactly: 0 differing metric values in `metrics.csv`, and identical phi series.
- **A1 reduction.** With r_s = 0 and w_c = 0, A1 reproduces A0 to 1e-9 (test). A1 also matches a loop reference.

## 7. Execution record

| journal | what | runs | failed |
| --- | --- | --- | --- |
| EXPL-001, EXPL-002 | smoke matrix, runtime and seed spread | 15 | 0 |
| EXPL-003 | neighbour-search benchmark | 72 rows | 0 mismatched steps |
| EXPL-004, EXPL-005 | burn-in scans (no shock) | 162, 36 | 0 |
| EXPL-006 | A1 diagnostic (no shock) | 16 | 0 |
| EXPL-007 | burn-in rule R-BI scan (A0 only, no shock, seeds 321 to 325) | 90 | 0 |
| EXPL-008 | M3 smoke re-run and metric validation | 15 | 0 |

- **Commands.** Exact commands are in `research/experiment_journal.jsonl`.
- **M3 re-run command.** `nice -n 10 .venv/bin/python -m swarm.cli smoke --config experiments/EXP-001/smoke_m3.json --workers 2`.
- **M3 re-run provenance.** `results/exploratory/EXP-001-smoke-m3/launch.json`, `provenance.csv` (15 rows) and `raw_manifest.json`.
- **Deviations.** The EXP-001 protocol did not list the burn-in and diagnostic scans. They are labelled exploratory. They computed only pre-shock order, except the smoke matrix.

## 8. Results

Generated summaries (not retyped here):

- `results/exploratory/EXP-001-summary.md`: runtime, seed spread, order before the shock, burn-in length.
- `results/exploratory/EXP-001-burnin-rule-decision.md`: rule R-BI.
- `results/exploratory/*/report/report.md`: per-directory generated reports.

Key planning values, as recorded in those files and the journal:

- **Smoke runtime.** Mean 1.269 s per run under heavy unrelated load.
- **Smoke seed spread.** Paired phi_post differences had SD 0.059 (A1 - A0) and 0.058 (A2 - A0) over 5 seeds, against the 0.2 assumed in the sample-size plan.
- **A1 order (draft w_c = 1).** A1 never ordered: phi_pre was 0.057 to 0.071 in all 18 cells.
- **Rule R-BI.**
  - 8 of 18 cells are orderable.
  - It chose t_d = 3000 (T = 3500).
  - In the other 10 cells, m(4000) was between 0.070 and 0.347.
- **Smoke values seen before the freeze.** These were under the draft design, not the frozen one (C4 disclosure). In the smoke cell, mean phi_post was:

  | arm | mean phi_post |
  | --- | --- |
  | A0 | 0.544 |
  | A1 | 0.064 |
  | A2 | 0.858 |

## 9. Interpretation

- The implementation passes every verification check, so the stop rule "engine incorrect" does not apply.
- The planning scans made the draft primary contrast questionable, because it would have compared an ordered phase with a disordered one. The owner's amendments (DL-009) responded to that before the freeze.
- The amendments did not fully remove the problem: EXP-002 shows A1 still weakly ordered at w_c = 0.5. See the EXP-002 report and limitation 13.

## 10. Threats to validity

- Determinism is shown on one machine only.
- Runtimes were measured under different conditions:
  - EXPL-001 to EXPL-006: heavy unrelated load (load averages 32 to 40).
  - EXPL-007: a quiet machine (load average about 1.7).
  - EXPL-008: a load average of about 10 at launch.
- The seed spread was measured in one cell under the draft design.

## 11. Conclusion and next experiment

EXP-001 passed its verification checks. EXP-002 and EXP-003 were run in M3; see their reports.

## 12. Reproduction appendix

See `reproduction.md` in this folder.
