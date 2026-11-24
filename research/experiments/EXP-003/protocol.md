<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-003: Sensitivity of the EXP-002 contrast to modelling choices

- **Status:** frozen (owner-approved 2026-11-24), not yet run.
- **Version:** 1.0, 2026-11-24 (draft 0.1 plus the owner-approved amendments in section 7). Protocol hash: recorded in `research/protocol_freeze.json`.
- **Depends on:** EXP-001 passed. Runs after EXP-002 but its design is fixed now, before any EXP-002 output is seen.

## 1. Question

Does the sign and CI of Delta (A1 - A0 in phi_post) survive changes to the neighbourhood definition, cohesion weight and boundary condition? If not, the EXP-002 interpretation is restricted to its exact modelling choices.

## 2. Conditions (one change at a time from the EXP-002 defaults)

| ID | Change | Rationale |
| --- | --- | --- |
| S1 | Topological neighbourhood, k = 7 nearest (torus distance) | Field evidence that starlings interact with about 6 to 7 neighbours rather than within a fixed distance (Ballerini et al., 2008, PNAS 105:1232-1237); decouples neighbour count from density |
| S2a, S2b | Cohesion weight w_c = 0.25 and 1.0 (half and double the primary 0.5; draft 0.5 and 2.0 around the draft 1) | Separates rule content from coupling strength |
| S3 | Reflecting walls instead of periodic | Removes wrap-around artefacts |
| S4 | Recovery threshold 0.8 and 0.95 | Affects tau only; computed from EXP-002 outputs, no new runs |

## 3. Reduced matrix

A0 and A1 only; density rho in {0.5, 2.0}; noise eta in {0.1, 0.5}; r = 1.0; 20 seeds (1001 to 1020, amended AM-3). All other parameters as EXP-002 (t_d = 3000, T = 3500, w_c = 0.5 except in S2). Runs: S1, S2a, S2b, S3 = 4 conditions x 2 arms x 4 cells x 20 seeds = 640 runs (S2 changes A1 only, so A0 runs of S2 reuse the EXP-002 A0 runs at matching cells; the count above is an upper bound, and the frozen configurations hold 480 runs).

## 4. Hypotheses and invalidation criterion

For each condition, Delta_S is estimated as in EXP-002 on the reduced cells, together with Delta restricted to the same cells from EXP-002. The main interpretation is **invalidated** for a condition if the 95% CI of Delta_S lies entirely on the opposite side of zero from the EXP-002 point estimate, and **weakened** if the CI of Delta_S contains zero while the EXP-002 CI does not. Both outcomes are reported.

## 5. Uncertainty, exclusion, stopping, budget

As EXP-002 (stratified seed bootstrap, 10,000 resamples, 95% CI; failure-only exclusion; 5% failure stop). Budget at most 2 hours wall-clock.

## 6. Reproducibility commands

```
uv run --frozen python -m swarm.cli run --config experiments/EXP-003/config_S1.json --workers 8
uv run --frozen python -m swarm.cli run --config experiments/EXP-003/config_S2.json --workers 8
uv run --frozen python -m swarm.cli run --config experiments/EXP-003/config_S3.json --workers 8
uv run --frozen python -m swarm.cli report --results results/confirmatory/EXP-003-S1
```

One configuration per condition, because each changes a different parameter; S2 contains A1 only (its A0 comparison reuses the EXP-002 A0 runs of the same cells and seeds); S4 needs no run. The report command is repeated for each output directory. The bootstrap and decision rule live in `swarm.analysis` (no `analyse` verb).

## 7. Amendments before freeze (owner-approved 2026-11-24)

Applied as stated in `research/protocol.md` section 13:

- **AM-1 and its consequence.** The primary w_c is now 0.5, so S2 becomes {0.25, 1.0} to keep the draft design (half and double the primary value). S1 and S3 use w_c = 0.5.
- **AM-2.** t_d = 3000, T = 3500, as EXP-002. Of the four reduced cells, A0 is aligned before the shock (rule R-BI) at eta = 0.1 (rho = 0.5 and 2.0) and not at eta = 0.5; this is reported per cell.
- **AM-3.** 20 seeds, 1001 to 1020; at most 640 runs (480 in the configurations).
- **AM-4.** Budget cap kept at 2 hours; measured projection 13.5 min serial, about 1.7 min with 8 workers (priced as metric periodic runs).
- **Configurations.** `experiments/EXP-003/config_S1.json`, `config_S2.json`, `config_S3.json`; their SHA-256 values are in the freeze record.
