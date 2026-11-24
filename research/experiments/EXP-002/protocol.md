<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-002: Local rules and recovery from a heading disturbance (primary comparison)

- **Status:** frozen (owner-approved 2026-11-24), not yet run.
- **Version:** 1.0, 2026-11-24 (draft 0.1 plus the owner-approved amendments in section 14). Protocol hash: recorded in `research/protocol_freeze.json`.
- **Depends on:** EXP-001 passed (all verification checks), budget projection within 4 hours (measured: 15.3 min serial, section 14).

## 1. Precise question

In the SWARM 2-D model, does adding separation and cohesion to alignment (A1) change mean post-disturbance polarization compared with alignment alone (A0), under matched seeds, across the 18-cell density x noise x radius grid?

## 2. Mechanism and rationale (verified sources)

- Alignment-only models show a noise- and density-driven transition between disordered and ordered motion (Vicsek et al., 1995, PRL 75:1226).
- Zonal models with repulsion, orientation and attraction show qualitatively different collective states for small changes in zone widths, and history dependence ("collective memory") (Couzin et al., 2002, J. Theor. Biol. 218:1-11).
- Control-theoretic work proves convergence of nearest-neighbour heading rules under connectivity conditions (Jadbabaie, Lin and Morse, 2003, IEEE TAC 48:988-1001) and designs flocking with separation and cohesion terms (Olfati-Saber, 2006, IEEE TAC 51:401-420). Connectivity is the link: cohesion may preserve the neighbour graph after a shock.
- Gap addressed: a matched-seed, disturbance-focused comparison of alignment-only versus zonal rules with a centralized reference, reporting uncertainty at the seed level. Novelty is not claimed; the literature review is not systematic.

## 3. Competing explanations

(a) Coupling strength rather than rule content (tested in EXP-003, S2); (b) neighbour-count effects of metric neighbourhoods (EXP-003, S1); (c) periodic-boundary artefacts (EXP-003, S3); (d) pre-disturbance differences in order (phi_pre is reported).

## 4. Hypotheses and estimand

- H0: Delta = 0; H1: Delta != 0 (two-sided). Delta = mean over cells of the within-cell mean paired difference phi_post(A1) - phi_post(A0).
- SESOI delta = 0.05. Decision rule: CI excludes 0 -> reject H0; CI within (-0.05, 0.05) -> practically equivalent; otherwise inconclusive.
- Contradicting result for H1: 95% CI containing 0.

## 5. Variables

- Independent: arm (A0, A1, A2); density rho in {0.5, 1.0, 2.0} (N = 200); noise eta in {0.1, 0.3, 0.5}; radius r in {0.5, 1.0}.
- Fixed: v0 = 0.05 u/step, T = 3500, t_d = 3000, W = 500, shock fraction f = 0.5, separation radius r_s = 0.25 r, w_a = 1, w_c = 0.5, periodic boundary, metric neighbourhoods (t_d, T and w_c amended, section 14).
- Dependent: phi_post (primary); tau, C, K, neighbour evaluations and wall-clock per step, phi_pre (secondary). Formulas and units: `research/protocol.md` section 4.

## 6. Treatment, control, baseline

Control/baseline: A0 alignment-only (the simplest rule). Treatment: A1. Reference: A2 centralized global alignment (descriptive ceiling).

## 7. Sampling and seeds

Seeds 1001 to 1020 (20 seeds, amended AM-3), identical across arms and cells; each seed derives independent RNG streams (initial state, per-step noise, disturbance) through `numpy.random.SeedSequence` spawning, so arms share streams. 1080 runs.

## 8. Sample-size rationale and compute budget

See `research/protocol.md` section 6. Budget: at most 4 hours wall-clock on the reference machine (Apple M1 Pro, 10 cores), parallel by run. EXP-001 must project this before the freeze.

## 9. Uncertainty method

Stratified seed-level percentile bootstrap, 10,000 resamples, bootstrap seed 20261124, 95% CI. Per-cell paired differences with CIs and raw distributions are reported.

## 10. Exclusion and stopping

Exclusion only for software failure, reported per run. More than 5% failed runs in any arm stops the experiment. No interim analysis; all planned runs execute.

## 11. Anticipated failure modes

Censoring of tau at low density or high noise; A0 disordered before the shock in the 10 cells that rule R-BI found not orderable (every eta = 0.5 cell; eta = 0.3 except rho in {1, 2} with r = 1), making phi_post less informative there. Those cells are reported and flagged, not dropped. A1 may also be weakly ordered before the shock at w_c = 0.5 (EXPL-006: phi_pre 0.251 in the best cell at T = 500); phi_pre is reported per arm and cell. A2 recovers in one step by construction, so its tau is uninformative and reported as such.

## 12. Sensitivity tests

EXP-003.

## 13. Reproducibility commands

```
uv run --frozen python -m swarm.cli run --config experiments/EXP-002/config.json --workers 8
uv run --frozen python -m swarm.cli report --results results/confirmatory/EXP-002
```

There is no separate `analyse` verb: the paired differences, the stratified seed bootstrap and the decision rule are in `swarm.analysis` and are wired into the report at M3.

## 14. Amendments before freeze (owner-approved 2026-11-24)

Applied as stated in `research/protocol.md` section 13:

- **AM-1.** A1 cohesion weight w_c = 0.5 (draft 1), set by the owner, not tuned on any outcome.
- **AM-2.** Burn-in t_d = 3000 steps (draft 500), T = 3500, chosen by the pre-stated rule R-BI from an A0-only, no-shock scan (seeds 321 to 325; `results/exploratory/EXP-001-burnin-rule-decision.md`). A0 is aligned (m >= 0.5) before the shock in 8 of 18 cells; the other 10 are flagged, not dropped.
- **AM-3.** 20 seeds, 1001 to 1020 (draft 10); 1080 runs.
- **AM-4.** Budget cap kept at 4 hours; measured projection 15.3 min serial, about 1.9 min with 8 workers.
- **Configuration.** `experiments/EXP-002/config.json` (confirmatory; outputs to `results/confirmatory/EXP-002`). Its SHA-256 is in the freeze record.
- **Unchanged:** hypotheses, estimand, SESOI, decision rule, bootstrap (10,000 resamples, seed 20261124), exclusion and stopping rules.
