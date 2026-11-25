<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# M4 interpretation: confounders, sensitivity, expected versus observed

Date: 2026-11-25. Milestone M4. All results are simulated. Confirmatory numbers come from `results/confirmatory/EXP-002/analysis/analysis.json` and `results/confirmatory/EXP-003-analysis/analysis.json` (revision `075cf7c`). Exploratory numbers (labelled X1 to X5) come from `results/exploratory/M4-sensitivity/analysis.json` (journal EXPL-M4-01, generator `experiments/exploratory_m4.py`); they were computed after the confirmatory outputs were seen, from the same committed runs with no new simulation, and they never change a frozen verdict.

## 1. Confirmatory conclusions under inspection

- **C-A (EXP-002 primary).** Delta = phi_post(A1) - phi_post(A0) = -0.307, 95% CI [-0.313, -0.302], 18 cells, 360 pairs: rejects H0.
- **C-B (EXP-003).** The sign and CI of the contrast survive S1 (topological k = 7), S2a and S2b (w_c 0.25 and 1.0) and S3 (reflecting walls): no condition invalidates or weakens C-A.

## 2. Competing explanations named in the protocol

The EXP-002 protocol (section 3) and `research/protocol.md` section 9 name four competing explanations. The table states what the committed results address.

| id | competing explanation (protocol) | evidence | status after M4 |
| --- | --- | --- | --- |
| (a) | Coupling strength, not rule content | EXP-003 S2: Delta_S -0.268 [-0.282, -0.257] at w_c 0.25, -0.434 [-0.443, -0.424] at 0.5 (EXP-002, same 4 cells), -0.507 [-0.515, -0.498] at 1.0 | Not removed. The contrast grows with w_c, so the strength of the cohesion term matters. The results cannot separate "cohesion content" from "more coupling", because w_c changes both. The sign holds over a fourfold range. |
| (b) | Metric neighbourhoods couple density and neighbour count | EXP-003 S1: -0.415 [-0.429, -0.398] | Addressed for these 4 cells: the sign and size hold with k = 7 topological neighbours. |
| (c) | Periodic-boundary artefacts | EXP-003 S3: -0.449 [-0.463, -0.434] | Addressed for these 4 cells: the sign and size hold with reflecting walls. |
| (d) | Pre-disturbance differences in order | phi_pre A1 - A0 = -0.312 [-0.319, -0.304] (confirmatory, descriptive); X1 change score 0.004 [-0.004, 0.012] (exploratory) | **Realised and dominant.** The pre-shock gap is as large as Delta. Once each run's own pre-shock level is removed, the A1 - A0 difference lies inside the SESOI band (exploratory). C-A is a difference in stationary order, not in recovery. |

Two further explanations were not named in the protocol but follow from the data:

| id | explanation | evidence | status |
| --- | --- | --- | --- |
| (e) | The disturbance is too weak or too brief to dominate a 500-step mean | A0 tau median 1.0 to 10.5 steps in the 8 orderable cells at the 0.9 threshold (EXP-002 per-cell table); X4 cell-mean early drop of A0 over [t_d, t_d + 50) is 0.012 to 0.069 in the 8 orderable cells (exploratory per-cell values in `results/exploratory/M4-sensitivity/analysis.json`) | Supported as a description: in ordered A0 cells the group re-forms within a few steps, so phi_post is close to phi_pre for every arm. phi_post was a poor choice for measuring recovery in this model. |
| (f) | The pooled Delta is an average of two regimes | X2: -0.618 [-0.629, -0.607] over the 8 orderable cells and -0.059 [-0.064, -0.054] over the 10 flagged cells (exploratory) | Supported. The pooled -0.307 mixes cells where A0 orders (large contrast) with cells where both arms are disordered (small contrast of either sign). The equal-weight pooling is frozen and stands; the split is descriptive. |

## 3. Exploratory sensitivity (X1 to X5)

All rows are A1 - A0 with the frozen bootstrap settings. Source: `results/exploratory/M4-sensitivity/summary.md`.

| id | quantity | cells / pairs | estimate [95% CI] | what it says |
| --- | --- | --- | --- | --- |
| X1 | change score phi_post - phi_pre, all cells | 18 / 360 | 0.004 [-0.004, 0.012] | No difference in the shift from pre- to post-shock level beyond the SESOI |
| X1 | change score, 8 orderable cells | 8 / 160 | 0.012 [-0.002, 0.026] | Same where A0 is ordered |
| X1 | change score, 10 flagged cells | 10 / 200 | -0.002 [-0.011, 0.007] | Same where A0 is disordered |
| X2 | phi_post, 8 orderable cells | 8 / 160 | -0.618 [-0.629, -0.607] | Large contrast where A0 orders |
| X2 | phi_pre, 8 orderable cells | 8 / 160 | -0.630 [-0.645, -0.616] | And the same gap before the shock |
| X2 | phi_post, 10 flagged cells | 10 / 200 | -0.059 [-0.064, -0.054] | Small contrast where both are disordered |
| X3 | phi_post, 7 cells with matched pre-shock order | 7 / 140 | 0.001 [-0.002, 0.004] | No contrast when pre-shock order is matched, but all 7 cells are high-noise cells where both arms are disordered |
| X4 | early drop over [t_d, t_d + 50) | 18 / 360 | -0.017 [-0.026, -0.008] | A1 loses less order at the shock, because it has less to lose |
| X5 | change score S1, S2a, S2b, S3 | 4 / 80 each | 0.023 [0.005, 0.042]; 0.014 [-0.002, 0.030]; 0.020 [0.008, 0.032]; -0.015 [-0.038, 0.005] | Within the SESOI band in every condition |

The X4 retained-fraction ratio (0.172 [0.010, 0.388], 11 cells) is not interpreted: A1's phi_pre is only about 0.03 to 0.17 above the random level b = 0.0627, so the ratio is unstable.

**Limit of the exploratory reading.** A change score near zero does not show that A1 recovers as well as A0. A1 is disordered before the shock, so there is little order to lose or recover; a small change is expected for a disordered arm whatever its recovery dynamics. The design cannot measure A1's recovery of order at all. The exploratory checks therefore remove the "A1 recovers worse" reading of C-A but do not support "A1 recovers equally well".

## 4. Effect on the conclusions

- **C-A stands as frozen** (rejects H0). Its content is narrowed: at w_c = 0.5, A1 is less polarized than A0, before and after the shock, in this model and grid. The data give no evidence that separation and cohesion change recovery from a heading shock in either direction.
- **C-B stands as frozen.** What is robust to topology, boundary and cohesion weight is the order gap, not a recovery effect. Explanation (a) is not resolved.
- **Manuscript title and framing.** The working title "How order emerges without a leader" overstates what was found. The manuscript is retitled to name the phase difference.

## 5. Expected versus observed (all registered experiments)

| experiment | prediction (protocol, before data) | observation (committed results) | verdict under the frozen rule |
| --- | --- | --- | --- |
| EXP-001 V1 | Cell-list neighbour sets equal brute-force sets | 72 benchmark rows, 0 mismatched steps | pass (exploratory, verification) |
| EXP-001 V2 | Repeated runs bit-identical | M3 smoke re-run: 0 differing metric values, identical phi series | pass |
| EXP-001 V3, V4 | Bounds hold; hand examples match | Test suite passes (133 at `075cf7c`); metric check 15 of 15 runs, 0 mismatches | pass |
| EXP-001 planning | Paired phi_post SD at most 0.2 (planning assumption) | SD 0.059 (A1 - A0), 5 seeds, draft design | assumption met (planning only) |
| EXP-002 primary | H1: Delta != 0, direction not predicted | Delta -0.307 [-0.313, -0.302] | rejects H0 |
| EXP-002 failure mode | A0 disordered before the shock in 10 cells; A1 possibly weakly ordered (protocol section 11) | A0 flagged cells as predicted; A1 phi_pre 0.097 to 0.229 in every cell | anticipated risk realised (limitation 13) |
| EXP-002 mechanism | Cohesion might preserve connectivity and help recovery | Cohesion A1 - A0 0.080 [0.065, 0.094]; no gain in phi_post | mechanism not supported for alignment (descriptive) |
| EXP-002 A2 | A2 is a ceiling, tau = 1 by construction | A2 - A0 0.374 [0.369, 0.379]; A2 tau median 1.0 in every cell | as expected (descriptive) |
| EXP-003 S1 | Invalidated if the CI lies on the other side of zero; weakened if it contains zero | -0.415 [-0.429, -0.398] | neither |
| EXP-003 S2a | same | -0.268 [-0.282, -0.257] | neither |
| EXP-003 S2b | same | -0.507 [-0.515, -0.498] | neither |
| EXP-003 S3 | same | -0.449 [-0.463, -0.434] | neither |
| EXP-003 S4 | tau depends on the threshold (secondary only) | medians rise with the threshold; censoring at most 3 of 20 per arm and cell | descriptive, as expected |
