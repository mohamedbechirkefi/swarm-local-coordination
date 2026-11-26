<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
<!-- Draft for LinkedIn (M5). Not published. Publication is owner-controlled. Numbers are taken from research/paper/manuscript.md. -->

I preregistered a simulation study to measure how a swarm recovers from a shock. The result was robust, and it answered a different question.

What I built: a 2-D simulation of 200 self-propelled agents comparing alignment alone with a rule that adds separation and cohesion, plus a centralized reference, under a matched heading shock. Protocol, analysis and seeds were frozen first; 1,080 confirmatory runs, none failed. There is also a static interactive page with a live swarm, a disturbance button and a metric timeline.

One defensible finding: with the cohesion weight used, the separation-cohesion rule held much less order than alignment alone, Delta = -0.307 (95% CI [-0.313, -0.302]) in post-shock polarization.

The caveat is the point: the same gap existed before the shock (-0.312 [-0.319, -0.304]). The design measured sustained order, not recovery, and I report that as the main result. A follow-up with matched pre-shock order is registered but not run.

All results are simulated; nothing here is a claim about real animals or robots. Independent preprint draft, not peer-reviewed.

Repository: https://github.com/mohamedbechirkefi/swarm-local-coordination
Demo: https://swarm-local-coordination.kefimohamedbechir.workers.dev

Mohamed Bechir Kefi, independent researcher
