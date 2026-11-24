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
