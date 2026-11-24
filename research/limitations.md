<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Limitations (living document, M0)

No results exist yet. This file lists limitations known by design; result-dependent limitations are added in M4.

1. **Simulation only.** Every outcome is a property of the simulated model. No claim of biological fidelity, robot performance or universal distributed-system guarantees (master prompt section 10, claims boundary).
2. **Two dimensions, constant speed, discrete synchronous updates.** Results may not transfer to 3-D, variable-speed, asynchronous or continuous-time models.
3. **One disturbance type in the primary design** (heading shock of half the agents). Other disturbances (noise bursts, predators, agent loss, communication dropout) are not tested in the confirmatory design.
4. **Parameter ranges.** Conclusions hold within the tested grid of density, noise and radius; extrapolation is not supported.
5. **A2 is not a realistic controller.** The centralized reference is an idealised global-broadcast ceiling without delay or bandwidth limits.
6. **Arm A1 is one parameterisation** of separation and cohesion (zonal priority, fixed weights); EXP-003 tests a few alternatives, not the space of rules.
7. **Non-systematic literature review.** Related work may be incomplete; no novelty is claimed.
8. **Single machine.** Determinism is verified on one platform; cross-platform floating-point differences are documented, not eliminated.
9. **No PDF from a TeX engine.** PDFs are produced through Typst; `manuscript.tex` is generated but not compiled locally (DL-002).
10. **A0 is disordered before the shock in 10 of 18 cells** of the frozen design, even after the lengthened burn-in (rule R-BI, t_d = 3000; m(4000) between 0.070 and 0.347). In those cells phi_post says little about recovery; they are kept in the pooled estimand and flagged.
11. **A1 may be weakly ordered before the shock at w_c = 0.5** (pre-freeze diagnostic: phi_pre 0.251 in the most favourable cell at T = 500). The A1 - A0 contrast can still carry a pre-shock phase difference; phi_pre is reported per arm and cell.
12. **Primary values were seen before the freeze** in one smoke cell under the draft design (C4 disclosure in `research/protocol_freeze.json`).
