<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-002: Local rules and recovery from a heading disturbance (primary comparison)

- **Status:** planned (protocol draft, awaiting owner freeze). Confirmatory only after the owner freezes this protocol and records approval.
- **Version:** draft 0.1, 2026-11-24. Protocol hash: recorded at freeze.
- **Depends on:** EXP-001 passed (all verification checks), budget projection within 4 hours.

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
- Fixed: v0 = 0.05 u/step, T = 1000, t_d = 500, W = 500, shock fraction f = 0.5, separation radius r_s = 0.25 r, w_a = w_c = 1, periodic boundary, metric neighbourhoods.
- Dependent: phi_post (primary); tau, C, K, neighbour evaluations and wall-clock per step, phi_pre (secondary). Formulas and units: `research/protocol.md` section 4.

## 6. Treatment, control, baseline

Control/baseline: A0 alignment-only (the simplest rule). Treatment: A1. Reference: A2 centralized global alignment (descriptive ceiling).

## 7. Sampling and seeds

Seeds 1001 to 1010, identical across arms and cells; each seed derives independent RNG streams (initial state, per-step noise, disturbance) through `numpy.random.SeedSequence` spawning, so arms share streams. 540 runs.

## 8. Sample-size rationale and compute budget

See `research/protocol.md` section 6. Budget: at most 4 hours wall-clock on the reference machine (Apple M1 Pro, 10 cores), parallel by run. EXP-001 must project this before the freeze.

## 9. Uncertainty method

Stratified seed-level percentile bootstrap, 10,000 resamples, bootstrap seed 20261124, 95% CI. Per-cell paired differences with CIs and raw distributions are reported.

## 10. Exclusion and stopping

Exclusion only for software failure, reported per run. More than 5% failed runs in any arm stops the experiment. No interim analysis; all planned runs execute.

## 11. Anticipated failure modes

Censoring of tau at low density or high noise; A0 disordered before the shock at eta = 0.5 and low density (phi_pre near 0), making phi_post uninformative in those cells, which is reported, not dropped.

## 12. Sensitivity tests

EXP-003.

## 13. Reproducibility commands (planned)

```
uv run python -m swarm.cli run --config experiments/EXP-002/config.json
uv run python -m swarm.cli analyse --exp EXP-002
uv run python -m swarm.cli report --exp EXP-002
```
