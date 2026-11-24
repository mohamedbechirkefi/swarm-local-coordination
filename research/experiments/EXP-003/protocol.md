<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-003: Sensitivity of the EXP-002 contrast to modelling choices

- **Status:** planned (protocol draft, awaiting owner freeze).
- **Version:** draft 0.1, 2026-11-24. Protocol hash: recorded at freeze.
- **Depends on:** EXP-001 passed. Runs after EXP-002 but its design is fixed now, before any EXP-002 output is seen.

## 1. Question

Does the sign and CI of Delta (A1 - A0 in phi_post) survive changes to the neighbourhood definition, cohesion weight and boundary condition? If not, the EXP-002 interpretation is restricted to its exact modelling choices.

## 2. Conditions (one change at a time from the EXP-002 defaults)

| ID | Change | Rationale |
| --- | --- | --- |
| S1 | Topological neighbourhood, k = 7 nearest (torus distance) | Field evidence that starlings interact with about 6 to 7 neighbours rather than within a fixed distance (Ballerini et al., 2008, PNAS 105:1232-1237); decouples neighbour count from density |
| S2a, S2b | Cohesion weight w_c = 0.5 and 2.0 | Separates rule content from coupling strength |
| S3 | Reflecting walls instead of periodic | Removes wrap-around artefacts |
| S4 | Recovery threshold 0.8 and 0.95 | Affects tau only; computed from EXP-002 outputs, no new runs |

## 3. Reduced matrix

A0 and A1 only; density rho in {0.5, 2.0}; noise eta in {0.1, 0.5}; r = 1.0; 10 seeds (1001 to 1010). Runs: S1, S2a, S2b, S3 = 4 conditions x 2 arms x 4 cells x 10 seeds = 320 runs (S2 changes A1 only, so A0 runs of S2 reuse the EXP-002 A0 runs at matching cells; the count above is an upper bound).

## 4. Hypotheses and invalidation criterion

For each condition, Delta_S is estimated as in EXP-002 on the reduced cells, together with Delta restricted to the same cells from EXP-002. The main interpretation is **invalidated** for a condition if the 95% CI of Delta_S lies entirely on the opposite side of zero from the EXP-002 point estimate, and **weakened** if the CI of Delta_S contains zero while the EXP-002 CI does not. Both outcomes are reported.

## 5. Uncertainty, exclusion, stopping, budget

As EXP-002 (stratified seed bootstrap, 10,000 resamples, 95% CI; failure-only exclusion; 5% failure stop). Budget at most 2 hours wall-clock.

## 6. Reproducibility commands (planned)

```
uv run python -m swarm.cli run --config experiments/EXP-003/config.json
uv run python -m swarm.cli analyse --exp EXP-003
```
