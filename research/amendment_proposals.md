<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Proposed amendments to the draft protocol (for the owner)

**Status:** proposals from session M2, 2026-11-24. **Decided by the owner on 2026-11-24** and applied as AM-1 to AM-4 (`research/protocol.md` section 13, DL-009): AP-1 option 1 with w_c = 0.5 fixed by the owner; AP-2 option 1 under the pre-stated rule R-BI (t_d = 3000); AP-3 20 seeds; AP-4 budget as measured. AP-2 options 2 and 3 were not approved. The text below is the proposal as written before the decision. Evidence comes only from exploratory pre-freeze runs (journal entries EXPL-002 to EXPL-006; summary in `results/exploratory/EXP-001-summary.md`). These numbers are planning measurements, not findings.

## AP-1: A1 is disordered in every planned cell at w_c = 1

**Observation.** In the burn-in scan (EXPL-004), A1 has mean phi_pre between 0.057 and 0.071 in all 18 cells, the level expected from random headings (1/sqrt(200) = 0.071). A0 is ordered (phi_pre >= 0.5) in 7 cells and A2 in all 18. The diagnostic (EXPL-006, rho = 2, eta = 0.1, r = 1) shows the cohesion weight drives this: with r_s/r = 0.25, phi_pre is 0.969 at w_c = 0, 0.449 at 0.25, 0.251 at 0.5 and 0.060 at 1. Tests show A1 reduces exactly to A0 when r_s = 0 and w_c = 0 and matches a loop reference, so no code fault is indicated.

**Consequence.** As drafted, EXP-002 would compare a polarised baseline with a group that never polarises. The A1 - A0 contrast in phi_post would mostly measure that phase difference, not recovery from the disturbance. EXP-003 S2 (w_c = 0.5 and 2.0) would not resolve it either.

**Options for the owner (choose before the freeze).**

1. Fix a smaller cohesion weight, chosen now from burn-in data only (no post-disturbance outcome), for example the largest w_c in a pre-declared grid at which A1 is ordered in the reference cell; adjust the S2 values around it.
2. Add a maximum turning rate per step to A1 (Couzin et al., 2002, use one), applied identically to A0, and recalibrate.
3. Keep w_c = 1 and reframe the question as a phase comparison; the disturbance-recovery interpretation would then be dropped.

## AP-2: the baseline A0 is not ordered in most cells, and 500 burn-in steps are short

**Observation.** A0 has phi_pre < 0.5 in 11 of 18 cells, including every cell with eta = 0.5 (EXPL-004). In the long burn-in (EXPL-005, A0, T = 2000) some cells are still ordering after 500 steps: rho = 0.5, eta = 0.1, r = 0.5 goes from 0.290 over [400, 500) to 0.522 over [1900, 2000); rho = 1, eta = 0.1, r = 0.5 from 0.608 to 0.846. Others are stationary (rho = 1, eta = 0.1, r = 1: 0.956 and 0.953).

**Consequence.** In cells where the group is disordered before the shock, phi_post carries little information about recovery. The draft protocol (section 11 of EXP-002) already plans to report such cells, not drop them, but with 11 of 18 cells affected the pooled estimand would be dominated by them. The recovery time tau is also degenerate there: its threshold is 0.9 x phi_pre, so a low phi_pre gives tau near 1 step (seen in the smoke cell: A0 median tau = 1 with phi_pre = 0.493).

**Options.**

1. Lengthen the burn-in (t_d) to 2,000 steps; runtime allows it (AP-4).
2. Restrict the confirmatory grid to cells where the baseline orders, defined now from burn-in data, for example eta in {0.1, 0.3} and r = 1; keep the excluded cells as descriptive.
3. Add an absolute floor to the tau threshold (for example recovery to max(0.9 phi_pre, 0.5)), or report tau only for runs with phi_pre above a fixed level.

## AP-3: seed count

**Observation.** In the smoke cell, the SD of per-seed paired differences in phi_post is 0.059 for A1 - A0 and 0.058 for A2 - A0 (5 seeds; EXPL-002), well below the 0.2 assumed in protocol section 6. The projected 95% CI half-width with 18 cells x 10 seeds is about 0.009.

**Caveat.** One cell, five seeds, and an A1 arm that is disordered (its variance is small for that reason). After AP-1 or AP-2 changes, the spread may be larger.

**Proposal.** Keep 10 seeds as the minimum, or raise to 20 because runs are cheap (AP-4). Re-measure the spread in one exploratory smoke run after AP-1 and AP-2 are decided, before the freeze.

## AP-4: compute budget is not binding

**Observation.** Mean runtime per run in the smoke cell: 0.385 s at revision 57f66f3 (EXPL-001) and 1.269 s at revision 99cc0c4 (EXPL-002) with identical outputs; the second measurement ran while the machine's load average was 32 to 40 on 10 cores, so it is inflated by contention. The projected EXP-002 matrix (540 runs, T = 1000) is 12.5 minutes serial under that load, about 1.6 minutes with 8 workers (EXPL-004 method in the summary). The draft budget is 4 hours.

**Proposal.** The budget allows a longer burn-in (AP-2), more seeds (AP-3) or larger N. Runtime should be re-measured on a quiet machine; the runner records per-run runtime and peak memory in every manifest.

## AP-5: minor

- The A2 reference recovers in one step by construction (every agent adopts the global mean heading), so its tau is uninformative; report A2 tau as such.
- EXP-001 protocol section 9 names a `swarm.cli smoke --config` command; it exists. The planned `analyse` command is not a separate CLI verb: `swarm.analysis` implements paired differences (used by the report generator), the stratified seed bootstrap and the decision rule (tested, deliberately not applied to exploratory data). Wiring the bootstrap into the report for confirmatory results is M3 work.
