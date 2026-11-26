<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-003 report: sensitivity of the EXP-002 contrast to modelling choices

All results are simulated. This is a confirmatory experiment under protocol v1.0 (frozen, owner-approved 2026-11-24).

## 1. Identification

- **Experiment.** EXP-003. Runs were made on 2026-11-24/25 UTC. Report version 1.0.
- **Status.** Complete: 480 of 480 configured runs (S1, S2 and S3, 160 each), 0 failed, none excluded. S4 needed no runs.
- **Author.** Mohamed Bechir Kefi, independent researcher (owner-approved metadata, DL-010; owner, 2026-11-26, decision sheet, B3). The AI was a research and development assistant, not an author.
- **Protocol hash.** `research/experiments/EXP-003/protocol.md`: e954d29e4a8b4e8909b7ff34d24c311b77f4a18b62f4706109865a262253a1d8.
- **Configs** (canonical hashes in `research/protocol_freeze.json` and in each `execution.json`):
  - S1 69927a24d3b7ff2e0c4f225549d13a4ff7f5a73bcbfe5754624f320b49b054f3;
  - S2 47e3e9e6edfd78f971e37d8a6b998734f0d4e4ed0f77a6bb738009f6c02d1398;
  - S3 b34d9128a0a43526c395dc8a63c8a3ae3ee3d8f2da2641f5a789f4b3786ad6c9.
- **Code revision of every run.** `075cf7c5f571c03ede9b8d551c3ba43766172a39`. A dirty-tree flag affects most runs; see section 7.
- **Analysis generator.** `experiments/analyse_confirmatory.py`, committed before any confirmatory output (DL-012).
- **Written.** After M3, from committed results only, on the owner's approval of 2026-11-25 (DL-014).

## 2. Executive summary

- **Question.** Do the sign and CI of EXP-002's contrast survive three modelling changes?
  - topological neighbours, k = 7 (S1);
  - cohesion weight 0.25 or 1.0 (S2a, S2b);
  - reflecting walls (S3).
  
  S4 asks how the secondary recovery time depends on its threshold.
- **Method.**
  - Reduced matrix: A0 and A1, rho in {0.5, 2}, eta in {0.1, 0.5}, r = 1, 20 seeds.
  - S2 pairs its A1 runs with the EXP-002 A0 runs of the same cells and seeds.
- **Outcome.**
  - Every Delta_S is negative, with a CI far from zero:
    - S1: -0.415 [-0.429, -0.398];
    - S2a: -0.268 [-0.282, -0.257];
    - S2b: -0.507 [-0.515, -0.498];
    - S3: -0.449 [-0.463, -0.434].
  - No condition invalidates or weakens the EXP-002 interpretation, under either the primary or the secondary reading.
- **Principal caveat.** The robustness is of a phase difference: A1 is disordered before the shock in EXP-002, and S1 and S3 show the same pre-shock gap. The magnitude increases with w_c. Under every tested change, EXP-002's phase confound remains (limitation 13).

## 3. Rationale

Three alternative explanations could produce EXP-002's contrast, and one secondary metric needs a check:

- **Coupling strength rather than rule content.** Probed by S2.
- **Metric neighbourhoods coupling density and neighbour count.** Probed by S1. Field evidence suggests starlings interact with about 6 to 7 neighbours (Ballerini et al., 2008, PNAS 105:1232-1237).
- **Periodic-boundary artefacts.** Probed by S3.
- **The recovery threshold of tau.** S4 checks it.

## 4. Hypotheses and criteria

- **Delta_S.** For each condition S, Delta_S is the equal-weight mean over the 4 reduced cells of within-cell mean paired differences phi_post(A1) - phi_post(A0). It uses the EXP-002 bootstrap: 10,000 resamples, seed 20261124, 95% CI.
- **Invalidated.** The main interpretation is invalidated for S if the CI of Delta_S lies entirely on the opposite side of zero from the EXP-002 point estimate.
- **Weakened.** It is weakened if the CI of Delta_S contains zero while the EXP-002 CI does not.
- **Reading fixed before any data (DL-012).**
  - Primary classification: against the pooled 18-cell EXP-002 Delta, -0.307 [-0.313, -0.302].
  - Secondary classification: against EXP-002 restricted to the same 4 cells, -0.434 [-0.443, -0.424].
  - "Contains zero" uses a closed interval.

## 5. Methodology

- **Reduced matrix.** A0 and A1; rho in {0.5, 2}; eta in {0.1, 0.5}; r = 1; seeds 1001 to 1020; t_d = 3000, T = 3500; N = 200. Everything else is as in EXP-002.
- **S1.** Topological neighbourhood: the k = 7 nearest agents by torus distance. 160 runs (A0 and A1).
- **S2a, S2b.** A1 with w_c = 0.25 and w_c = 1.0. 160 A1 runs, paired with the EXP-002 A0 runs at matching cells and seeds.
- **S3.** Reflecting walls. 160 runs (A0 and A1).
- **S4.** tau at thresholds 0.8, 0.9 and 0.95 x phi_pre, computed from the stored EXP-002 phi series (A0 and A1, all 18 cells). No new runs.
- **Statistics.** As EXP-002: failure-only exclusion, and an analysis stop if more than 5% of runs in an arm fail.
- **Hardware and software.** Apple M1 Pro, macOS 15.3.1, Python 3.12.1, numpy 2.5.4. 2 worker processes under `nice -n 10`.
- **Budget.** 2 hours wall-clock.

## 6. Implementation verification

- **Before the runs.** The test suite passed (133 tests at `075cf7c`). Topological neighbours, reflecting walls and the cohesion weight have unit tests (`tests/test_neighbors.py`, `tests/test_rules.py`, `tests/test_simulate.py`).
- **Every run.** phi_pre, phi_post and tau were recomputed from the stored series: 160 of 160 runs per condition checked, with 0 mismatches.

## 7. Execution record

| condition | command (`--workers 2`, under `nice -n 10`) | runs by arm | failed | elapsed (execution.json) |
| --- | --- | --- | --- | --- |
| S1 | `swarm.cli run --config experiments/EXP-003/config_S1.json` | A0 80, A1 80 | 0 | 594.7 s |
| S2 | `swarm.cli run --config experiments/EXP-003/config_S2.json` | A1 160 | 0 | 181.9 s |
| S3 | `swarm.cli run --config experiments/EXP-003/config_S3.json` | A0 80, A1 80 | 0 | 293.9 s |

- **Timing.** Runs took place from 2026-11-24 23:54:15 to 2026-11-25 00:12:18 UTC, within the 2-hour budget. The load average from unrelated processes was up to 38.7 at launch.
- **Provenance per run.** `results/confirmatory/EXP-003-S*/provenance.csv`, `launch.json` and `raw_manifest.json`.
- **Deviation (DL-013): provenance flag.**
  - 134 of 160 S1 runs and all 160 S2 and 160 S3 runs record `git_dirty: true`. The cause was an uncommitted append to `research/experiment_journal.jsonl` made by the session during S1.
  - `git diff HEAD` over `src`, `experiments`, the protocols and the freeze record was empty, so no code, configuration or protocol differed from `075cf7c`.
  - 6 flagged runs (2 per condition) re-simulated from the committed code gave bit-identical phi series and metrics.
  - The runs were kept and not repeated.
- **Other notes.**
  - 2 worker processes instead of 8 (no effect on outputs).
  - S2's config holds A1 only, as frozen. Its A0 comparison reuses the EXP-002 runs.
  - The owner approved writing this report from committed results (DL-014).

## 8. Results

### Delta_S per condition and verdicts

<!-- BEGIN GENERATED:exp003-main -->
| condition | runs (failed) | Delta_S [95% CI] | pairs | verdict vs pooled EXP-002 | verdict vs EXP-002 on the 4 cells |
| --- | --- | --- | --- | --- | --- |
| EXP-002, 18 cells (reference) | | -0.307 [-0.313, -0.302] | 360 | | |
| EXP-002, 4 reduced cells (reference) | | -0.434 [-0.443, -0.424] | 80 | | |
| S1 | 160 (0) | -0.415 [-0.429, -0.398] | 80 | neither invalidated nor weakened | neither invalidated nor weakened |
| S2a | 160 (0) | -0.268 [-0.282, -0.257] | 80 | neither invalidated nor weakened | neither invalidated nor weakened |
| S2b | 160 (0) | -0.507 [-0.515, -0.498] | 80 | neither invalidated nor weakened | neither invalidated nor weakened |
| S3 | 160 (0) | -0.449 [-0.463, -0.434] | 80 | neither invalidated nor weakened | neither invalidated nor weakened |
<!-- END GENERATED:exp003-main -->

The "160 (0)" entries for S2a and S2b both refer to the single S2 directory of 160 A1 runs, of which 80 have w_c = 0.25 and 80 have w_c = 1.0.

Pre-shock order, from `analysis.json` (descriptive):

- S1: phi_pre A1 - A0 = -0.438 [-0.454, -0.422].
- S3: phi_pre A1 - A0 = -0.434 [-0.460, -0.405].

### Per-cell mean differences (descriptive)

<!-- BEGIN GENERATED:exp003-cells -->
| condition | cell | mean A1 - A0 in phi_post | pairs |
| --- | --- | --- | --- |
| S1 | rho=0.5, eta=0.1, r=1 | -0.748 | 20 |
| S1 | rho=0.5, eta=0.5, r=1 | -0.123 | 20 |
| S1 | rho=2, eta=0.1, r=1 | -0.647 | 20 |
| S1 | rho=2, eta=0.5, r=1 | -0.140 | 20 |
| S2a | rho=0.5, eta=0.1, r=1 | -0.437 | 20 |
| S2a | rho=0.5, eta=0.5, r=1 | 0.053 | 20 |
| S2a | rho=2, eta=0.1, r=1 | -0.530 | 20 |
| S2a | rho=2, eta=0.5, r=1 | -0.157 | 20 |
| S2b | rho=0.5, eta=0.1, r=1 | -0.790 | 20 |
| S2b | rho=0.5, eta=0.5, r=1 | -0.050 | 20 |
| S2b | rho=2, eta=0.1, r=1 | -0.907 | 20 |
| S2b | rho=2, eta=0.5, r=1 | -0.281 | 20 |
| S3 | rho=0.5, eta=0.1, r=1 | -0.737 | 20 |
| S3 | rho=0.5, eta=0.5, r=1 | -0.003 | 20 |
| S3 | rho=2, eta=0.1, r=1 | -0.805 | 20 |
| S3 | rho=2, eta=0.5, r=1 | -0.252 | 20 |
<!-- END GENERATED:exp003-cells -->

### S4: recovery time at thresholds 0.8, 0.9 and 0.95 (EXP-002 runs, A0 and A1; descriptive)

<!-- BEGIN GENERATED:exp003-s4 -->
| cell | arm | tau median at 0.8 (censored) | at 0.9 (censored) | at 0.95 (censored) |
| --- | --- | --- | --- | --- |
| rho=0.5, eta=0.1, r=0.5 | A0 | 2.0 (0) | 7.5 (2) | 22.0 (3) |
| rho=0.5, eta=0.1, r=0.5 | A1 | 3.0 (0) | 9.0 (0) | 16.5 (0) |
| rho=0.5, eta=0.1, r=1 | A0 | 1.0 (0) | 2.0 (1) | 14.0 (2) |
| rho=0.5, eta=0.1, r=1 | A1 | 19.5 (0) | 41.0 (0) | 60.5 (0) |
| rho=0.5, eta=0.3, r=0.5 | A0 | 17.5 (0) | 30.0 (1) | 30.0 (1) |
| rho=0.5, eta=0.3, r=0.5 | A1 | 30.0 (0) | 42.0 (0) | 43.5 (0) |
| rho=0.5, eta=0.3, r=1 | A0 | 8.0 (1) | 18.0 (2) | 14.0 (3) |
| rho=0.5, eta=0.3, r=1 | A1 | 11.0 (0) | 17.5 (0) | 21.5 (0) |
| rho=0.5, eta=0.5, r=0.5 | A0 | 67.0 (0) | 126.5 (0) | 126.5 (0) |
| rho=0.5, eta=0.5, r=0.5 | A1 | 25.5 (0) | 42.5 (0) | 60.0 (1) |
| rho=0.5, eta=0.5, r=1 | A0 | 12.5 (0) | 19.0 (1) | 20.0 (1) |
| rho=0.5, eta=0.5, r=1 | A1 | 14.0 (0) | 19.5 (0) | 28.5 (0) |
| rho=1, eta=0.1, r=0.5 | A0 | 1.0 (0) | 3.5 (0) | 34.0 (1) |
| rho=1, eta=0.1, r=0.5 | A1 | 7.5 (0) | 17.5 (0) | 19.0 (1) |
| rho=1, eta=0.1, r=1 | A0 | 1.0 (0) | 1.0 (0) | 2.0 (0) |
| rho=1, eta=0.1, r=1 | A1 | 3.0 (0) | 11.0 (1) | 13.0 (1) |
| rho=1, eta=0.3, r=0.5 | A0 | 6.0 (0) | 18.5 (0) | 34.0 (0) |
| rho=1, eta=0.3, r=0.5 | A1 | 17.5 (0) | 34.0 (0) | 39.5 (0) |
| rho=1, eta=0.3, r=1 | A0 | 1.5 (0) | 10.5 (0) | 14.5 (0) |
| rho=1, eta=0.3, r=1 | A1 | 11.5 (0) | 14.0 (0) | 14.0 (0) |
| rho=1, eta=0.5, r=0.5 | A0 | 53.0 (0) | 75.5 (0) | 84.0 (0) |
| rho=1, eta=0.5, r=0.5 | A1 | 28.5 (0) | 36.5 (0) | 71.5 (0) |
| rho=1, eta=0.5, r=1 | A0 | 6.5 (0) | 8.5 (0) | 12.0 (0) |
| rho=1, eta=0.5, r=1 | A1 | 28.0 (0) | 35.0 (1) | 43.0 (1) |
| rho=2, eta=0.1, r=0.5 | A0 | 1.0 (0) | 2.0 (0) | 10.0 (1) |
| rho=2, eta=0.1, r=0.5 | A1 | 19.5 (0) | 25.0 (1) | 29.0 (2) |
| rho=2, eta=0.1, r=1 | A0 | 1.0 (0) | 1.0 (0) | 2.0 (0) |
| rho=2, eta=0.1, r=1 | A1 | 15.5 (0) | 16.5 (0) | 16.5 (0) |
| rho=2, eta=0.3, r=0.5 | A0 | 1.0 (0) | 1.5 (0) | 9.5 (0) |
| rho=2, eta=0.3, r=0.5 | A1 | 16.0 (0) | 33.5 (0) | 35.0 (0) |
| rho=2, eta=0.3, r=1 | A0 | 1.0 (0) | 2.0 (0) | 3.5 (0) |
| rho=2, eta=0.3, r=1 | A1 | 21.0 (0) | 29.0 (0) | 35.5 (0) |
| rho=2, eta=0.5, r=0.5 | A0 | 25.5 (0) | 37.0 (0) | 37.0 (0) |
| rho=2, eta=0.5, r=0.5 | A1 | 20.0 (0) | 31.5 (0) | 31.5 (0) |
| rho=2, eta=0.5, r=1 | A0 | 18.5 (0) | 26.5 (0) | 32.5 (0) |
| rho=2, eta=0.5, r=1 | A1 | 28.0 (0) | 35.5 (0) | 42.5 (0) |
<!-- END GENERATED:exp003-s4 -->

Medians are taken over uncensored runs only. As the threshold rises, more runs are censored, so a median can fall from one threshold to the next. One example is A0 at rho = 0.5, eta = 0.3, r = 1: 18.0 at 0.9 and 14.0 at 0.95.

### Figure

<!-- BEGIN GENERATED:exp003-figures -->
![FIG-EXP003-01. Delta (A1 - A0 in phi_post) with 95% stratified-bootstrap CIs (20 seeds per cell, 10,000 resamples) for EXP-002 (all 18 cells and the 4 reduced cells) and each EXP-003 condition: S1 topological k = 7, S2a/S2b w_c = 0.25/1.0, S3 reflecting walls. Dotted lines: SESOI +/- 0.05. Simulated data, confirmatory.](../../../results/confirmatory/EXP-003-analysis/fig_exp003_01_sensitivity.png)
<!-- END GENERATED:exp003-figures -->

- **Machine-readable outputs.**
  - Analysis: `results/confirmatory/EXP-003-analysis/analysis.json`.
  - Per-run metrics: `results/confirmatory/EXP-003-S{1,2,3}/metrics.csv`.
  - Generated run reports: `results/confirmatory/EXP-003-S{1,2,3}/report/report.md`.

## 9. Interpretation

- **Expected vs observed.** The protocol anticipated that a sign flip or a CI crossing zero would restrict the EXP-002 interpretation. Neither occurred. Every Delta_S CI lies below -0.25 and well outside the SESOI band.
- **S1 (topological).** -0.415 [-0.429, -0.398], against -0.434 [-0.443, -0.424] for EXP-002 on the same cells. The contrast is not an artefact of metric neighbourhoods coupling density and neighbour count.
- **S3 (reflecting walls).** -0.449 [-0.463, -0.434], so the contrast is not a periodic-boundary artefact.
- **S2 (cohesion weight).**
  - The magnitude increases monotonically with w_c: -0.268 at 0.25, -0.434 at 0.5 (EXP-002 on these cells) and -0.507 at 1.0.
  - This is consistent with the cohesion term driving A1's loss of order. It agrees with the pre-freeze diagnostic EXPL-006, in which phi_pre fell as w_c rose.
  - At w_c = 0.25 the contrast is still clearly negative, so the effect is not specific to the chosen weight.
- **What robustness does and does not mean.**
  - In S1 and S3 the pre-shock gap (-0.438 and -0.434) again nearly equals Delta_S.
  - So EXP-003 shows that the phase difference is robust. It does not show that recovery differs, and the phase confound of EXP-002 remains under every tested change (limitation 13).
- **S4.**
  - Recovery times grow with the threshold, as expected, and censoring stays low: at most 3 of 20 runs in any arm and cell.
  - A0 recovers within a few steps in the ordered, high-density cells, and A1 takes tens of steps. But A1's tau measures a return to its own low phi_pre, so the two are not comparable as recovery of order.
- **Negative and null details.** At high noise some per-cell differences are near zero or positive: S2a +0.053 and S3 -0.003 at rho = 0.5, eta = 0.5. These cells carry little information because both arms are disordered there.

## 10. Threats to validity

- **Construct.** This is the same phase confound as EXP-002.
- **Reduced cells.** Only 4 cells, with r = 1 only. Two of them are high-noise cells in which A0 is not aligned before the shock.
- **S2 pairing.** S2 pairs new A1 runs with EXP-002 A0 runs. This is valid under common random numbers, which share seeds and streams across runs, but it means the S2 runs are not a self-contained matrix.
- **Coverage of the rule space.** One alternative is tested per factor; the space of rules is not covered.
- **Provenance flag.** 454 runs carry `git_dirty: true` (DL-013). Code identity was checked by diff and by bit-identical re-simulation of 6 runs, not by re-running every run.
- **Hardware.** Runtimes were measured under heavy unrelated load.
- **External.** These are statements about a simulated model only.

## 11. Conclusion and next experiment

- **Answer.** In this simulated model, the sign and CI of the A1 - A0 contrast in phi_post survive topological neighbours, cohesion weights of 0.25 and 1.0, and reflecting walls. No condition invalidates or weakens EXP-002.
- **What survives is a robust difference in order, not evidence about recovery.**
- **Next experiment.** Separately registered, as proposed in the EXP-002 report: compare recovery under matched pre-shock order.

## 12. Reproduction appendix

See `reproduction.md` in this folder.
