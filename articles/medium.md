<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
<!-- Draft for Medium (M5). Not published. Publication is owner-controlled. Every number is taken from research/paper/manuscript.md; tests/test_demo_export.py checks that each decimal here appears there or in the reports. -->

# I set out to measure how a swarm recovers from a shock. The experiment measured something else.

*A preregistered simulation of 200 agents, a robust result, and an honest account of why it does not answer the question it was built for. All results are simulated.*

## The question

Flocks of birds and schools of fish are often described as coordinating "without a leader": each individual follows a few local rules, and order appears at the level of the group. Simple models reproduce this. In the alignment-only model of Vicsek and colleagues (1995), each agent turns towards the average heading of its neighbours, plus some noise. Other models add two more rules: keep a little distance from very close neighbours (separation) and move towards the local group (cohesion).

I wanted to know what those two extra rules do when the group is disturbed. Do they help a group regain order, for example by keeping neighbourhoods together, or do they get in the way? The project's question was: *how do local interaction rules affect collective coordination under disturbances?*

## The experiment

I compared three rules in a two-dimensional simulation of 200 agents moving at constant speed:

- **A0, alignment only.** The baseline.
- **A1, separation, alignment and cohesion.** Repulsion from very close neighbours takes priority; otherwise an agent combines alignment with cohesion at weight 0.5.
- **A2, a centralized reference.** Every agent adopts the global average heading. No real swarm can do this; it is a ceiling, not a candidate.

After 3,000 steps, half the agents were given random headings. For each random seed, all three rules started from the same positions, saw the same noise and received the same disturbance, so the comparison is paired. The outcome was the average polarization over the 500 steps after the shock. Polarization is 1 when all agents move in the same direction and close to 0 when there is no common direction.

The protocol, the analysis code and the seeds were frozen before the confirmatory runs. I ran 18 combinations of density, noise and neighbourhood radius with 20 seeds each: 1,080 runs, none failed.

## The result

The difference A1 minus A0 in post-disturbance polarization was **Delta = -0.307**, with a 95% stratified bootstrap confidence interval of **[-0.313, -0.302]**. The interval excludes zero and lies far outside the smallest effect I had decided would matter (0.05), so the frozen rule rejects the null hypothesis. Four frozen sensitivity conditions (topological neighbours, half and double the cohesion weight, reflecting walls) kept the sign and excluded zero.

So far, this reads like a clean finding: separation and cohesion make the group worse at recovering. That reading is wrong.

## The negative finding

The same gap was there **before** the shock: -0.312 [-0.319, -0.304]. With these weights, A1 was only weakly ordered in every condition, with mean pre-shock polarization between 0.097 and 0.229. A0, where it was ordered, dipped at the shock and returned within tens of steps. A 500-step average after the shock therefore mostly measured how much order each rule sustains, not how it recovers.

After seeing this, I computed a change score for each run: post-shock order minus that run's own pre-shock order. This analysis is exploratory, chosen after the results were seen, and it changes no frozen verdict. The paired difference in change score was 0.004 [-0.004, 0.012], inside the smallest effect of interest. That removes the "A1 recovers worse" reading. It does not show that the two rules recover equally: a rule with little order has little order to lose.

The honest summary is narrow. At this parameterisation, adding prioritised separation and cohesion can cost most of the alignment that alignment alone achieves, and the design could not measure recovery. The manuscript's title says exactly that.

## What a better experiment would need

A follow-up, registered as EXP-004, would match the two rules' order before the shock, use an outcome normalised to the pre-shock level, check that each rule has reached a steady state, and use a disturbance strong enough to produce a visible transient. It is registered, not frozen, and has not been run, so it has no results.

## Limitations

- Everything here is a property of a simulated model: two dimensions, constant speed, synchronous updates, one disturbance type, one population size. Nothing is claimed about real animals, robots or distributed systems in general.
- A0 could not align before the shock in 10 of the 18 conditions; those conditions compare two disordered states and are kept and flagged.
- The change-score analysis is exploratory.
- Each cited source was checked only for the statement made about it, at the level stated in the manuscript's reference list, and the review was not systematic.

## Figures

**Figure 1.** Per-cell mean paired difference in post-disturbance polarization, A1 minus A0, with 95% stratified-bootstrap confidence intervals over 20 seeds per cell. Simulated data, confirmatory.
*Alt text: a forest plot in which most cells lie well below zero, the 8 ordered cells furthest below, and the high-noise cells near zero.*

**Figure 2.** Interactive page: a live swarm in the browser with a disturbance button and a metric timeline. The sandbox uses the same update rules as the research engine but its own random numbers; its output is not a research result.
*Alt text: a square box of short strokes, one per agent, next to a line chart of polarization and cohesion over time with vertical lines at each disturbance.*

## Reproduce it

Code, frozen protocols, per-run metrics, checksums and the interactive page: [repository link to be added by the owner on release]. Demo: [demo link to be added by the owner on release]. Manuscript: `research/paper/manuscript.md` in the repository.

*Independent research manuscript / preprint draft, not peer-reviewed. An AI system assisted with code, analysis and drafting under the author's direction; it is not an author.*
