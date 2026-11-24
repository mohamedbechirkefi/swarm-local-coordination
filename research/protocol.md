<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# SWARM research protocol

**Status: v1.0, frozen (owner-approved 2026-11-24).** Draft v0.1 plus the owner-approved amendments in section 13. The freeze record is `research/protocol_freeze.json` (SHA-256 of this file, of the EXP-002 and EXP-003 protocols and of their configs; git revision). Any later change is a dated post-freeze amendment (section 12).

Per-experiment protocols: `research/experiments/EXP-001/protocol.md`, `EXP-002/protocol.md`, `EXP-003/protocol.md`. Where this file and an experiment protocol disagree, the experiment protocol is more specific and wins for that experiment; the conflict must be logged.

## 1. Research question

Master prompt section 10: *How do local interaction rules affect collective coordination under disturbances?*

Operational form (proposal): in a 2-D self-propelled particle model with constant speed, local metric neighbourhoods and angular noise, does adding short-range separation and longer-range cohesion to pure alignment change how well the group stays aligned after a heading disturbance, compared with alignment alone, under matched initial conditions, noise and disturbance?

## 2. Model (formal sketch, to be finalised in M1)

- **Agents.** N agents in a square box of side L, positions x_i in R^2 (length units, "u"), headings theta_i in (-pi, pi], constant speed v0 (u per step). Discrete time t = 0, 1, ..., T. Synchronous update.
- **Boundary.** Periodic (torus) in the primary design. Reflecting boundary is a sensitivity condition (EXP-003).
- **Neighbourhood.** Metric: N_i(t) = { j != i : |x_j - x_i|_torus <= r }, with communication radius r. Topological (k nearest, k = 7) is a sensitivity condition (EXP-003).
- **Noise.** Each step, heading noise xi_i(t) ~ Uniform(-eta*pi, eta*pi), eta in [0, 1] (dimensionless).
- **Arms (rules).**
  - **A0 Alignment-only (baseline).** Vicsek-style: theta_i(t+1) = arg( sum_{j in N_i ∪ {i}} e^{i theta_j(t)} ) + xi_i(t).
  - **A1 Separation + cohesion + alignment.** Desired direction d_i = w_a * a_i + w_s * s_i + w_c * c_i, where a_i is the unit mean neighbour heading (including self), s_i is the unit repulsion vector from neighbours within r_s = 0.25 r (sum of -(x_j - x_i)/|x_j - x_i|), c_i is the unit vector to the neighbour centroid. Zonal priority as in Couzin et al. (2002): if any neighbour is within r_s, d_i = s_i; otherwise d_i = w_a a_i + w_c c_i. Default w_a = 1, w_c = 0.5 (amended AM-1; draft value 1; EXP-003 varies w_c). Maximum turn per step: none in the primary design (same as A0). theta_i(t+1) = arg(d_i) + xi_i(t).
  - **A2 Centralized reference.** Every agent aligns to the global mean heading of all N agents (an omniscient leader-free broadcast), plus the same noise. It is a reference ceiling for alignment, not a candidate local rule.
- **Disturbance.** At step t_d, a heading shock: a fraction f = 0.5 of agents, chosen by the run's disturbance RNG, receive headings drawn uniformly on (-pi, pi]. The same agents and the same new headings are used in every arm for a given seed (common random numbers).
- **Run length.** Burn-in t_d = 3000 steps (amended AM-2 by rule R-BI; draft value 500), post-disturbance window W = 500 steps, T = 3500.

## 3. Hypotheses (draft)

- **H0 (primary).** The pooled mean paired difference in post-disturbance polarization between A1 and A0 is zero: Delta = E[ phi_post(A1) - phi_post(A0) ] = 0.
- **H1 (primary, nondirectional).** Delta != 0. A nondirectional H1 is proposed because the literature read so far supports both directions: cohesion may keep neighbourhoods connected so alignment information propagates (helping recovery), while repulsion injects direction changes unrelated to heading (hurting it).
- **Practical equivalence.** Smallest effect size of interest delta = 0.05 polarization units. If the 95% CI of Delta lies entirely within (-0.05, 0.05), the result is reported as practically equivalent; if it excludes 0 the result rejects H0; otherwise it is inconclusive. Non-significance is never reported as equivalence without this test.

What would contradict H1: a 95% CI for Delta that contains zero. What would contradict a directional reading in either direction: a CI entirely on the other side of zero.

## 4. Metrics

- **Primary: post-disturbance polarization phi_post.** phi(t) = | (1/N) sum_i e^{i theta_i(t)} |, dimensionless in [0, 1]. phi_post = mean of phi(t) over t in [t_d, t_d + W). Justification: it directly measures coordination (alignment) under disturbance; it is bounded, defined for every run (no censoring, unlike recovery time), and comparable across all three arms.
- **Secondary.**
  1. **Recovery time tau** (steps): first t >= t_d such that phi(s) >= 0.9 * phi_pre for all s in [t, t + 10), where phi_pre = mean phi over [t_d - 100, t_d). Right-censored at W; censoring frequency reported separately.
  2. **Cohesion C** (dimensionless): fraction of agents in the largest connected component of the radius-r neighbour graph, averaged over the post window.
  3. **Collisions K** (count per agent per 100 steps): ordered pairs i < j with torus distance < d_c = 0.1 r at a step, summed over the post window, normalised.
  4. **Neighbour computation cost:** number of pair distance evaluations per step (deterministic count) and wall-clock seconds per step, for the cell-list index versus brute force.
  5. **Pre-disturbance polarization phi_pre**, reported to show baseline differences between arms.

## 5. Experimental unit, design and matrix

- **Experimental unit:** one simulation run, identified by (arm, density, noise, radius, seed). Arms are compared within seed: the seed fixes initial positions, initial headings, the per-step noise stream and the disturbance draw for all arms (common random numbers). The independent unit for inference is the (cell, seed) pair; time steps within a run are never treated as independent.
- **Factors (full matrix, EXP-002):** arm in {A0, A1, A2}; density rho = N/L^2 in {0.5, 1.0, 2.0} with N = 200 fixed (L adjusted); noise eta in {0.1, 0.3, 0.5}; radius r in {0.5, 1.0}; speed v0 = 0.05 u per step. That is 3 x 3 x 2 = 18 cells x 3 arms.
- **Seeds:** 20 per cell (amended AM-3; draft value 10), the same 20 seeds in every arm. Full matrix: 18 x 3 x 20 = 1080 runs.
- **Smoke matrix (EXP-001, exploratory):** 3 arms x 1 cell (rho = 1, eta = 0.3, r = 1) x 5 seeds = 15 runs, T = 1000.

## 6. Sample-size rationale

Planning assumption, not a measurement: if the standard deviation of per-seed paired differences in phi_post is at most 0.2 within a cell, the pooled estimate over 360 independent (cell, seed) pairs (20 seeds, AM-3; the draft had 180) has a standard error near 0.2 / sqrt(360) = 0.011, giving a 95% CI half-width near 0.02, below delta = 0.05. EXP-001 (exploratory) measures this standard deviation; if it exceeds 0.3, the seed count is raised before the freeze (the owner decides). Seeds are cheap if the measured runtime allows it.

## 7. Analysis and uncertainty

- **Primary estimand:** Delta = mean over the 18 cells (equal weight) of the within-cell mean paired difference phi_post(A1) - phi_post(A0).
- **Uncertainty:** stratified percentile bootstrap, 10,000 resamples, resampling seeds with replacement within each cell, preserving pairing; 95% CI. Bootstrap RNG seed fixed and recorded.
- **Per-cell reporting:** paired differences per cell with bootstrap CIs, raw per-seed values and distributions. No per-cell significance claims (18 cells; they are descriptive). Secondary metrics are descriptive with CIs; no multiplicity-adjusted confirmatory claims are made for them.
- **A2:** reported as a reference (A2 - A0, A2 - A1), descriptive.
- **Effect sizes:** absolute differences in metric units; relative differences only where the baseline is far from zero.

## 8. Exclusion and stopping rules

- **Exclusion:** a run is excluded only for a recorded software failure (exception, non-finite state, invariant violation). Every excluded run is reported with its reason; there is no outcome-based exclusion. If more than 5% of runs in any arm fail, the experiment stops and the failure is diagnosed before any analysis.
- **Stopping:** fixed design; all 1080 runs are executed; no interim looks at the primary outcome. Compute budget: the full matrix must finish within 4 hours of wall-clock on the reference machine; if EXP-001 projects more, N or T is reduced *before the freeze*, never after. Measured projection for the amended matrix (AM-4): 15.3 min serial, about 1.9 min with 8 workers.

## 9. Controls and confounders

- Same N, speed, noise process, disturbance and step count in every arm.
- **Confounder: effective interaction strength.** A1 changes the direction rule and also how strongly neighbours pull; an effect could come from overall coupling rather than separation/cohesion specifically. EXP-003 varies w_c.
- **Confounder: neighbourhood definition.** Metric neighbourhoods couple density and neighbour count. EXP-003 tests topological k = 7.
- **Confounder: boundary.** Periodic boundaries can create artefacts (band states, wrap-around cohesion). EXP-003 tests reflecting walls.
- **Confounder: tuning on evaluation data.** Parameters above are fixed before any run. Any change after observing EXP-002 outputs is exploratory.

## 10. Sensitivity analyses (EXP-003)

Each could invalidate the main interpretation if the sign of Delta flips or its CI moves across zero:

- S1 topological neighbours (k = 7) instead of metric;
- S2 cohesion weight w_c in {0.25, 1.0} (half and double the primary value; amended with AM-1, draft {0.5, 2.0} around the draft value 1);
- S3 reflecting boundary instead of periodic;
- S4 recovery threshold 0.8 and 0.95 instead of 0.9 (affects the secondary metric only).

## 11. Claims boundary

No claim of biological fidelity, of universal distributed-system guarantees, or of real-world robot or animal behaviour. Results are statements about this simulated model within the tested parameter ranges.

## 12. Amendments after freeze

None. Any amendment after freezing is dated, justified, versioned and kept separate from the frozen analysis.

## 13. Amendments before freeze (owner-approved 2026-11-24)

The owner approved four SWARM amendments on 2026-11-24 (quoted in the freeze record `research/protocol_freeze.json`). They are applied here and in the EXP-002 and EXP-003 protocols. Sections 1 to 12 above are the draft as it stood before the amendments; where they disagree with this section, this section wins.

### AM-2 Burn-in rule R-BI (pre-stated 2026-11-24, before the data that apply it were generated)

Approval: "Lengthen the burn-in until A0 is aligned before the shock, under a pre-stated rule."

- **Data.** A new exploratory scan (`experiments/EXP-001/burnin_rule.json`): arm A0 only, the 18 EXP-002 cells, seeds 321 to 325 (disjoint from every other seed), T = t_d = 4000, no shock. Only pre-shock A0 polarization exists in these runs; no A1 run and no post-disturbance outcome is computed, so the rule cannot see the primary contrast.
- **Statistic.** For cell c and step t, m_c(t) = mean over the 5 seeds of the mean of phi over steps [t - 100, t).
- **Aligned.** A0 is aligned in cell c at t if m_c(t) >= 0.5 (the same threshold used in the EXP-001 planning summary).
- **Orderable.** Cell c is orderable if m_c(4000) >= 0.5.
- **Choice.** t_d is the smallest candidate in {500, 1000, 1500, 2000, 3000, 4000} at which A0 is aligned in every orderable cell. The post-disturbance window stays W = 500, so T = t_d + 500.
- **Cells that are not orderable.** Lengthening the burn-in cannot align A0 where the alignment-only model is disordered at stationarity (expected at high noise; EXP-001 summary). Such cells stay in the matrix and in the pooled estimand (no outcome-based exclusion, section 8); they are flagged "A0 not aligned before the shock at any tested burn-in" in every per-cell table.
- **Application.** `experiments/EXP-001/apply_burnin_rule.py` computes the choice; its output is `results/exploratory/EXP-001-burnin-rule-decision.{json,md}`.
- **Result** (`results/exploratory/EXP-001-burnin-rule-decision.md`, journal EXPL-007; 90 A0 runs, 0 failed). Orderable cells: 8 of 18 (all eta = 0.1 cells, and eta = 0.3 with r = 1 at rho = 1 and 2). The smallest candidate at which A0 is aligned in all 8 is **t_d = 3000** (at 2000, rho = 0.5, eta = 0.1, r = 0.5 has m = 0.369). So T = 3500. The other 10 cells (every eta = 0.5 cell, and eta = 0.3 except the two above) have m(4000) between 0.070 and 0.347: A0 is not aligned before the shock there at any tested burn-in. They are kept and flagged as stated above. This residual is a limitation of the design, not something lengthening can fix.

### AM-1 Cohesion weight of A1

Approval: "Set A1's cohesion weight to 0.5, fixed now without tuning on the contrast." Applied: w_c = 0.5 in A1 for EXP-002 and for EXP-003 S1 and S3 (draft value 1). The value is set by the owner's statement, not chosen from data; no run was made to select it. The only pre-freeze evidence at w_c = 0.5 is the burn-in diagnostic EXPL-006 (rho = 2, eta = 0.1, r = 1, T = 500, no shock): A1 mean phi_pre 0.251 with r_s/r = 0.25. A1 may therefore still be weakly ordered before the shock in many cells; this is reported, not corrected. **Consequential edit:** EXP-003 S2 was {0.5, 2.0}, half and double the draft value 1; 0.5 is now the primary value, so S2 keeps the same design (half and double the primary value) and becomes {0.25, 1.0}.

### AM-3 Seeds

Approval: "20 seeds." Applied: EXP-002 and EXP-003 use seeds 1001 to 1020 in every arm and cell (draft 1001 to 1010). EXP-003 reuses EXP-002 A0 runs for S2, which requires the same seeds.

### AM-4 Budget

Approval: "Budget headroom as measured." Applied: the 4-hour cap for EXP-002 and the 2-hour cap for EXP-003 are kept, and the measured projection for the amended design is recorded (`results/exploratory/EXP-001-burnin-rule-decision.md`, quiet machine, load average about 1.7 on 10 cores): EXP-002 1080 runs at T = 3500, 15.3 min serial, about 1.9 min with 8 workers; EXP-003 at most 640 runs, 13.5 min serial, about 1.7 min with 8 workers. Method: A0 seconds per step per cell from the R-BI scan, times the arm runtime ratio from the smoke cell (A1 1.29, A2 0.45), times the steps; linear parallel scaling assumed. The headroom (more than 10 times) is what allowed the longer burn-in and the doubled seeds.
