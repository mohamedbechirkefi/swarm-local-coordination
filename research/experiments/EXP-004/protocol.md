<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-004: Recovery from a heading disturbance with matched pre-shock order

- **Status:** registered, not frozen (2026-11-25). Written before any data for this experiment exist. No calibration, smoke or confirmatory run has been made. The freeze needs the owner's G-FREEZE word; until then no confirmatory run is allowed, and the runner refuses one (the protocol and configuration are not in `research/protocol_freeze.json`).
- **Version:** 0.1 (draft), 2026-11-25. Protocol hash: assigned at freeze.
- **Authority:** owner, 2026-11-25, "Approve all" (post-M4), item 3: "SWARM: recovery with matched pre-shock order. Each gets a protocol and config written before any data. The freeze needs the owner's G-FREEZE word as usual." Decision log DL-016.
- **Depends on:** EXP-001 (verification checks V1 to V4 pass), the frozen design of EXP-002 v1.0 (`research/protocol.md`, `research/experiments/EXP-002/protocol.md`), and the calibration stage of section 7, which must be run and its rule applied before the freeze.
- **Configuration:** `experiments/EXP-004/config.json` (draft; it contains open fields and cannot be loaded by the runner until they are fixed).

**Parameter rule.** Every parameter below is taken from the frozen EXP-002 design unless stated otherwise. A parameter that cannot be derived from that design is marked **open, owner decision at freeze**; the session that wrote this draft did not choose it. Open items are collected in section 21.

## 1. Precise question

In the SWARM 2-D model, when the zonal rule A1 and the alignment-only rule A0 hold matched levels of order before a heading disturbance, does A1 change how much order the group regains after the disturbance, relative to its own pre-shock level, compared with A0, under matched seeds?

## 2. Why this experiment exists

EXP-002 rejected its H0 (Delta = -0.307 [-0.313, -0.302]), but the same gap was present before the shock (phi_pre A1 - A0 = -0.312 [-0.319, -0.304]); A1 was weakly ordered in every cell, so phi_post measured a difference in sustained order, not recovery (limitations 13, 17; DL-015). The exploratory change score (X1, 0.004 [-0.004, 0.012]) and the matched-cell subset (X3) were chosen after the results were seen and cover only cells where both arms are disordered. The manuscript's conclusion states the requirements of a follow-up: arms matched in pre-shock order, an outcome normalised to the pre-shock level, a disturbance that produces a measurable transient, a steady-state check for each arm before the shock, and a direct measurement of the proposed mechanism. This protocol registers that follow-up as a new experiment ID, because the question and the outcome differ materially from EXP-002 (CLAUDE.md section 2).

## 3. Mechanism and rationale (sources as read)

- Alignment-only models show a noise- and density-driven transition between disordered and ordered motion (Vicsek et al., 1995; abstract read).
- In zonal models, zone parameters shift the collective state (Couzin et al., 2002; record and abstract read). In SWARM, EXP-003 found that the order gap grows with the cohesion weight (S2a w_c 0.25, S2b w_c 1.0), so the A1 parameterisation controls A1's order level.
- The H1 mechanism of EXP-002 (cohesion preserves connectivity and so helps alignment recover) was not supported at w_c 0.5: A1 was more connected and less aligned. The M4 hypothesis that repulsion with priority keeps changing headings inside tight clusters was not measured. Both remain candidate mechanisms for a recovery difference once order is matched.
- Gap: no matched-order comparison of recovery between these rules exists in this project, and none was found in the sources read; the literature review was targeted, not systematic, and novelty is not claimed.

## 4. Competing explanations

(a) Residual pre-shock order differences (controlled by calibration and checked by the manipulation check of section 9). (b) The matching lever itself (a different cohesion weight, or a turning-rate limit applied to both arms) rather than the rule family. (c) Floor or ceiling effects in the change score when phi_pre is near the random level or near 1. (d) Non-stationarity: an arm still drifting at t_d (steady-state check, section 7). (e) Neighbourhood type and boundary artefacts (not varied here; EXP-003 found no reversal for the order gap, but did not test recovery).

## 5. Hypotheses, estimand and contradiction criteria

- **Primary outcome per run:** the change score R = phi_post - phi_pre (dimensionless), with phi_post and phi_pre as in `research/protocol.md` section 4. This is the definition of the exploratory X1, now registered in advance.
- **Estimand:** Delta_R = mean over cells (equal weight) of the within-cell mean paired difference R(A1) - R(A0) over seeds.
- **H0:** Delta_R = 0. **H1 (nondirectional):** Delta_R != 0.
- **SESOI:** 0.05 polarization units (as EXP-002).
- **Decision rule (as EXP-002):** 95% CI excludes 0 -> reject H0; CI inside (-0.05, 0.05) -> practically equivalent; otherwise inconclusive.
- **What contradicts H1:** a 95% CI for Delta_R that contains zero. A CI inside (-0.05, 0.05) supports practical equivalence of recovery under matched order.
- **Validity condition (manipulation check, pre-stated):** the confirmatory runs must show matched pre-shock order: the 95% CI of the pooled phi_pre(A1) - phi_pre(A0) lies inside (-0.05, 0.05). If it does not, the verdict on Delta_R is still reported, but it is labelled "matching failed" and is not read as a statement about recovery.

## 6. Experimental unit and scope

The independent unit is the (cell, seed) pair; arms are paired within seed by common random numbers (initial state, per-step noise, disturbance), as in EXP-002. Time steps are never treated as independent. Scope: the simulated SWARM model only; no biological, robotic or distributed-system claim.

## 7. Pre-freeze calibration stage (exploratory, shock-free)

The matched level of order is obtained by a rule stated now and applied before the freeze, in the same way rule R-BI was applied for EXP-002.

- **Rule R-MATCH.** For each candidate value of the matching lever (section 21, items 1 and 2), run A0 and A1 without a shock (shock_fraction 0) on calibration seeds disjoint from every confirmatory seed, for the cell set of section 8. Compute the cell-mean phi_pre per arm over [t_d - 100, t_d). Select the candidate that minimises the largest absolute cell-mean gap |phi_pre(A1) - phi_pre(A0)| over the cell set. The match is accepted only if that gap is below the SESOI (0.05) in every cell of the set. If no candidate is accepted, EXP-004 is not run in this form; the outcome is recorded and the owner decides (abandon, widen the candidate set, or change the lever).
- **Rule R-SS (steady state, both arms).** In the same shock-free runs, for each arm and cell, compare mean phi over [t_d - 200, t_d - 100) with mean phi over [t_d - 100, t_d). The arm is at steady state in that cell if the absolute difference of the cell means is below the tolerance (open, item 5). If any arm fails in any cell, t_d is lengthened by the R-BI candidate ladder before the freeze (open, item 5); t_d is never chosen from post-shock data.
- **Why this cannot leak the primary outcome:** the calibration runs contain no shock and use seeds disjoint from the confirmatory seeds, so no post-shock value of the confirmatory matrix is seen.
- Calibration runs are labelled exploratory, written under `results/exploratory/`, and journalled. Their rule script is committed before their data are generated.

## 8. Variables

- **Independent:** arm in {A0, A1, A2}.
- **Cells:** density rho in {0.5, 1.0, 2.0} (N = 200), noise eta in {0.1, 0.3, 0.5}, radius r in {0.5, 1.0}, as EXP-002. Whether the confirmatory cell set is all 18 cells or only the 8 cells in which rule R-BI found A0 orderable is **open (item 3)**: in the 10 other cells A0 is disordered before the shock, so there is little order for either arm to recover.
- **Fixed (from EXP-002 v1.0):** v0 = 0.05 u/step, W = 500, pre_window 100, r_s = 0.25 r (sep_ratio 0.25), w_a = 1, recovery threshold 0.9 of phi_pre held for 10 steps, collision ratio 0.1, periodic boundary, metric neighbourhoods, cell-list index.
- **Burn-in:** t_d = 3000 and T = t_d + W = 3500 from R-BI, subject to R-SS (section 7).
- **Matching lever:** A1 cohesion weight w_c, or a turning-rate limit applied identically to A0 and A1 (amendment proposal AP-1, option 2); **open (items 1 and 2)**.
- **Disturbance:** at t_d, a fraction f of agents receive uniform random headings, the same agents and headings in every arm for a seed. EXP-002 used f = 0.5; whether to keep it or use a stronger disturbance so that the transient is measurable is **open (item 4)**.
- **Dependent (primary):** R = phi_post - phi_pre.
- **Dependent (secondary, descriptive):** phi_pre and phi_post per arm; early drop phi_pre - mean phi over [t_d, t_d + 50) (definition of the exploratory X4); recovery time tau; cohesion C; collisions K; neighbour evaluations and wall-clock per step. The fraction of agents with a neighbour inside r_s per step (the M4 mechanism measurement) is not implemented; whether to implement it before the freeze is **open (item 7)**.

## 9. Treatment, control, baseline

Control and baseline: A0 alignment-only. Treatment: A1 at the calibrated lever value. Reference: A2 centralized global alignment (descriptive ceiling; its tau is uninformative, as in EXP-002). The manipulation check of section 5 is part of the analysis, not optional.

## 10. Sampling and seeds

20 seeds per cell, identical across arms (as EXP-002, AM-3). The seeds must be disjoint from every seed already used in this project, because rerunning A0 at the frozen EXP-002 settings on seeds 1001 to 1020 would reproduce runs whose post-shock outcomes have been seen. Known used seeds include 101 to 105 (smoke), 321 to 325 (R-BI scan) and 1001 to 1020 (EXP-002, EXP-003); the complete list is checked against the journal before the freeze. The confirmatory and calibration seed ranges are **open (item 6)**.

## 11. Sample-size rationale

As `research/protocol.md` section 6: with 20 seeds per cell and an assumed paired-difference SD of at most 0.2, the pooled standard error over the cells is small next to the SESOI (0.2 / sqrt(360) = 0.011 for 18 cells; 0.2 / sqrt(160) = 0.016 for 8 cells). This is a planning assumption, not a measurement for R. If the calibration stage shows a larger spread, the seed count is reconsidered before the freeze (owner decision).

## 12. Compute budget

At most 4 hours wall-clock on the reference machine (Apple M1 Pro, 10 cores) for the confirmatory matrix, as EXP-002, and at most 2 hours for the calibration stage. Runs use 2 worker processes under `nice` unless the coordinator allows more (DL-012). The projection is made from the calibration runs before the freeze. If the chosen lever or a longer t_d breaks the cap, N or T is reduced before the freeze, never after.

## 13. Metric formulas and units

As `research/protocol.md` section 4: phi(t) = |(1/N) sum_i e^{i theta_i(t)}| in [0, 1]; phi_pre = mean phi over [t_d - 100, t_d); phi_post = mean phi over [t_d, t_d + W); R = phi_post - phi_pre (dimensionless, in [-1, 1]); tau in steps, right-censored at W; C dimensionless; K per agent per 100 steps; neighbour evaluations per step (count) and seconds per step.

## 14. Uncertainty method

Stratified seed-level percentile bootstrap within cells, 10,000 resamples, 95% CI, preserving pairing, as EXP-002. The bootstrap seed is fixed at the freeze (EXP-002 used 20261124; reusing it is acceptable because it only drives resampling). Per-cell paired differences with CIs and per-seed values are reported; no per-cell tests.

## 15. Exclusion and stopping

Exclusion only for a recorded software failure. More than 5% failed runs in any arm stops the experiment before analysis. No interim analysis; all planned runs execute. The analysis script is written, tested and committed before any confirmatory output exists (as DL-012).

## 16. Anticipated failure modes

- No lever value matches pre-shock order in every cell (R-MATCH fails): EXP-004 is not run in this form.
- A turning-rate limit changes A0 as well as A1, so A0 differs from the EXP-002 A0; the comparison stays paired within EXP-004 but is not comparable with EXP-002 numbers.
- A strong disturbance (f near 1) may push both arms near the random level, making R dominated by phi_pre; a weak one (f = 0.5) is absorbed within a few steps in ordered cells (M4 observation).
- The matched level may be low (both arms weakly ordered), giving a floor effect in R; reported through phi_pre per cell.
- Change scores near the bounds in cells where phi_pre is close to 1.

## 17. Sensitivity tests

Descriptive, reported beside the primary result: (S-a) R restricted to the cells in which the calibration gap was smallest; (S-b) the early-drop outcome over [t_d, t_d + 50); (S-c) recovery thresholds 0.8 and 0.95 from the stored series, as EXP-003 S4. Whether to add a topological-neighbourhood or reflecting-wall condition is left to the owner at the freeze (not required by this protocol).

## 18. Analysis outputs

`results/confirmatory/EXP-004/analysis/analysis.json` (Delta_R with CI and decision, manipulation check, per-cell tables, secondary metrics), figures generated from it, provenance and raw SHA-256 manifest as in M3 (`experiments/provenance.py`).

## 19. Reproducibility commands (after the freeze only)

```
uv run --frozen python -m swarm.cli run --config experiments/EXP-004/config.json --workers 2
```

The calibration command and the analysis command are added when their scripts are committed (before the freeze). Until the freeze, the runner refuses this configuration.

## 20. What is not done at registration

No simulation of any kind for EXP-004, no code change, no hash added to `research/protocol_freeze.json`. The frozen EXP-002 and EXP-003 protocols, configurations, seeds and results are not changed.

## 21. Open items (owner decision at freeze)

1. **Matching lever:** A1 cohesion weight w_c only, or a turning-rate limit applied identically to A0 and A1 (AP-1 option 2). A turning-rate limit is not implemented in `swarm.rules`; it would need code and tests before the calibration stage.
2. **Candidate set** for the lever searched by R-MATCH (for w_c: values below 0.25, since EXP-003 showed the gap shrinking as w_c falls; the exact values are not derivable from the frozen design).
3. **Cell set:** all 18 EXP-002 cells, or the 8 cells R-BI found orderable for A0.
4. **Disturbance strength f:** keep 0.5 (EXP-002) or a stronger shock.
5. **Steady-state tolerance** for R-SS and the t_d ladder if it fails.
6. **Seed ranges** for calibration and confirmatory runs (disjoint from all used seeds).
7. **Mechanism metric:** implement the per-step fraction of agents with a neighbour inside r_s as a secondary metric, or not.
8. **Bootstrap seed** (reuse 20261124 or a new fixed value).
