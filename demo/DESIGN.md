<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# SWARM demo: design plan

Owner request of 2026-11-26: each lab demo gets its own brand, motion and premium UI. This file is the plan written before the code, then reviewed against the frontend-design tells and the other demos' directions.

## Subject, audience, job

- **Subject.** A preregistered simulation of 200 self-propelled agents: alignment only (A0), zonal separation-alignment-cohesion (A1) and a centralized reference (A2), compared under a heading shock that gives half the agents random headings.
- **Audience.** A curious technical reader, an admissions committee reading quickly, a researcher checking the intervals, the frozen rule and the confound.
- **Primary job.** Ask the question, answer it in one sentence (A1 kept much less order than A0, before and after the shock, so the study measured sustained order, not recovery), show the two contrasts on one axis, then the evidence, the sandbox and the limitations.

## Direction: a starling murmuration at dusk

Collective motion is best known from starlings over a reed bed at sunset: thousands of dark birds against an afterglow, folding into one shape, torn apart by a falcon, regrouping. The page is that sky. The top is a deep dusk indigo; the horizon glows apricot and mauve behind a live flock; everything below the hero is the darker sky after sunset, where the evidence is read by lamplight colours.

## Colour (dark only; the subject is dusk)

| Name | Hex | Role |
|---|---|---|
| Dusk | `#1D1B33` | page background |
| Twilight | `#272546` | panels, the sandbox field |
| Afterglow | `#F0A86A` | horizon, links, focus ring, A1 |
| Mauve horizon | `#B8687A` | the middle of the horizon glow |
| Starling | `#15122A` | birds against the glow, the mark on light |
| Pale sky | `#EEE8F4` | text |

Supporting tokens: muted text `#BDB5D3`, rules `#403C68`, A0 sky blue `#8EC5F0`, A2 reed green `#A6D9A0`, sandbox lavender `#C9B3F2`, exploratory gold `#E8C35A`.

## Type

- **Bodoni Moda** (OFL 1.1), 500 roman and 400 italic: display. High contrast between thick and thin strokes, like birds against a bright sky; the italic carries the wordmark and the headline's motion.
- **Schibsted Grotesk** (OFL 1.1), 400, 500 and 700: body, controls and figures. A sturdy newsroom grotesk with lining figures. Its tabular figures (`tnum`) also widen the comma and the period, which broke intervals such as "[-0.313, -0.302]" into spaced fragments in the first build, so numbers use its proportional lining figures (a deliberate deviation from the brief's tabular-figures rule, recorded here).

Scale (1.25 ratio from a 17 px body): 13.6, 17, 21, 26.5, 33, 41.5, 52, 65 px. Body line height 1.6; measure under 70 characters.

## Layout

```
+---------------------------------------------------------------------+
| (mark) Swarm            Findings  Evidence  Sandbox  Method    bar  |  sticky
+---------------------------------------------------------------------+
| How do local interaction rules            .  . ..                   |  hero: dusk sky,
| affect collective coordination           .::::::::.  .              |  live flock in the
| under disturbances?  (Bodoni, 60 px)       ':::::::::'   .          |  afterglow
|                                                                     |
| Answer: A1 kept much less order ...     [ Scatter half the flock ]  |
| author line                       Illustration, not study data      |
|~~~~~~~~~~~~~~~~~~~~~ horizon glow ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
+---------------------------------------------------------------------+
| The answer on one axis: Delta after the shock, the same gap before  |
|   |-----o-----|  after          (both far outside the SESOI band)   |
|   |-----o-----|  before                                             |
+---------------------------------------------------------------------+
| Evidence: forest plot, window timeline, experiment panels           |
| Sandbox (lavender dashed field)                                     |
| Assumptions, method and limitations, footer                         |
+---------------------------------------------------------------------+
```

Left-aligned text; the flock sits to the right on wide screens and below the text on phones.

## Motion

- **One orchestrated hero moment.** On load the birds start scattered across the sky and fold into one murmuration within about three seconds; a little later half of them are given random headings (the study's own disturbance) and the flock tears and regroups. It is a decorative boids flock, labelled "Illustration, not study data", and it shows no number. It pauses when off screen or in a background tab.
- **Motion that answers actions.** "Scatter half the flock" repeats the disturbance on demand. Navigation underline slides to the section being read. Charts draw in once when scrolled into view. The sandbox keeps its own Run and Pause behaviour.
- **Reduced motion.** The hero shows one still frame of a formed flock and hides the scatter button; charts appear without the wipe; the sandbox computes without animating (unchanged).
- **Hover** only inside `(hover: hover) and (pointer: fine)`. No `transition: all`.

## The one memorable thing

The live murmuration in the afterglow, and the visitor's own falcon: one button that scatters half the flock, which is exactly the study's shock.

## Review against the tells and the other demos (revisions made)

1. *First draft:* near-black `#111` background with a single orange accent. That is the "near-black plus one accent" default. **Changed** to a dusk indigo base with a full horizon gradient (indigo, mauve, apricot) and three arm colours drawn from the sky, the glow and the reeds.
2. *First draft:* Cormorant Garamond with a geometric sans, the "luxury serif" pairing every search returns. **Changed** to Bodoni Moda (stroke contrast as silhouette) with Schibsted Grotesk.
3. *First draft:* three headline numbers in three equal cards. **Changed** to the two measured contrasts on one shared axis with the equivalence band, and the unrun EXP-004 as a plain line of text, which is what it is.
4. *First draft:* uppercase tracked kicker above the headline and uppercase value labels. **Changed** to sentence-case labels; the value labels keep their distinct borders (solid, dotted, double, dashed) so they never depend on colour alone.
5. *Against the other demos:* PULSE is a broadcast control room, VIRAL a network map, MARKET a trading floor, FLOW a transit map. SWARM is the only sky, and the only one with a live flock; EVOLVE (the sibling of this session) is a pale green notebook page, so the two never meet.
6. *Removed accessory:* a moon in the hero sky. It competed with the flock and added nothing.
