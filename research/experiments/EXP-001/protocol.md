<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# EXP-001: Implementation verification and smoke matrix

- **Status:** exploratory, run before the freeze on 2026-11-24 (journal EXPL-001 to EXPL-007; EXPL-007 is the A0-only burn-in scan that applies rule R-BI for amendment AM-2, `research/protocol.md` section 13). Exploratory by design: EXP-001 never supports a confirmatory claim.
- **Version:** draft 0.1, 2026-11-24. Protocol hash: recorded at freeze.
- **Depends on:** M2 core engine (A0, A1, A2, cell-list index, metrics).

## 1. Question

Is the simulator correct enough, and fast enough, to run EXP-002 as specified? Specifically: (a) does the cell-list neighbour index return exactly the same neighbour sets as brute force; (b) are updates deterministic under a fixed seed; (c) do metrics stay within their bounds; (d) what is the per-run runtime and the spread of paired differences in phi_post, to check the EXP-002 budget and sample-size assumption?

## 2. Mechanism and rationale

A cell list (grid of side >= r) restricts pair checks to adjacent cells, reducing expected work from O(N^2) to about O(N * rho * r^2) per step at fixed density. Correctness must be shown by differential testing against brute force, including the periodic wrap. Rationale for verification-first: master prompt section 10 "Project-specific verification" and M2 gate "correctness before UI polish".

## 3. Competing explanations to rule out

Apparent arm differences in EXP-002 could come from index bugs (missed neighbours across the wrap), RNG streams not shared across arms, or angle-averaging errors near +/- pi. EXP-001 checks each.

## 4. Hypotheses (verification, not scientific)

- V1: for 1,000 random configurations (N in {2, 50, 200}, rho and r spanning the EXP-002 grid, including agents within 1e-9 u of the box edges), neighbour sets from the cell list equal those from brute force, exactly.
- V2: two runs with the same config and seed produce bit-identical state trajectories on the same machine.
- V3: |heading vector| = 1 within 1e-12 for every agent and step; 0 <= phi <= 1; 0 < C <= 1; positions remain in [0, L).
- V4: hand-computed examples (2 and 3 agents) match the update rule exactly.
- Disconfirmation: any mismatch in V1 to V4 stops the pipeline (stop rule: engine incorrect means no experiments).

## 5. Smoke matrix

3 arms (A0, A1, A2) x 1 cell (rho = 1.0, eta = 0.3, r = 1.0, N = 200) x 5 seeds = 15 runs, T = 1000, t_d = 500, W = 500.

- **Experimental unit:** one run; arms paired by seed.
- **Outputs:** all primary and secondary metrics per run; runtime per run; peak memory where feasible; the standard deviation of paired differences phi_post(A1) - phi_post(A0) across the 5 seeds.
- **Use of outputs:** budget projection for EXP-002 and the sample-size check in `research/protocol.md` section 6. These numbers are exploratory and are never pooled with EXP-002.

## 6. Neighbour computation benchmark

Pair distance evaluations per step (exact count) and wall-clock per step for cell list versus brute force, N in {100, 200, 400, 800}, at each EXP-002 density and radius, 3 repeats, A0 only, 50 steps each. Reported descriptively (median and range of repeats).

## 7. Exclusion and stopping

No exclusions. Any verification failure stops EXP-001 and is reported; the fix is a new code revision and EXP-001 is re-run in full.

## 8. Anticipated failure modes

Floating-point ties at distance exactly r (rule: <= r, tested at r +/- 1e-12); empty neighbourhoods; cells smaller than r for small L; arg of a zero vector in A1 (rule: keep the current heading).

## 9. Reproducibility commands (planned, not yet implemented)

```
uv run pytest -q
uv run python -m swarm.cli smoke --config experiments/EXP-001/smoke.json
uv run python -m swarm.cli bench --config experiments/EXP-001/bench.json
```
