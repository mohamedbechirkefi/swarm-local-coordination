<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# demo/

Static page for SWARM (M5): TypeScript, React and Vite, versions pinned by the shared lab template and `package-lock.json`. It works offline after the first load, has no runtime service and makes no request to another host. No visitor data is collected or stored.

What it shows:

- **Published results** (from `public/data/results.json`, written by `scripts/export_demo_data.py` from committed results only): the overview and status label, the primary contrast Delta = -0.307 [-0.313, -0.302] and the pre-shock gap -0.312 [-0.319, -0.304], a per-cell forest plot with 95% CIs, a published metric timeline of window means around the shock, one panel per registered experiment (EXP-001 exploratory, EXP-002 and EXP-003 confirmatory, EXP-004 registered and not run), and the post hoc exploratory checks, each with its own label.
- **Assumptions** (fixed design inputs, labelled as such) and **method and limitations**.
- **Sandbox** (labelled sandbox output): a real-time swarm in a Web Worker with rule, size, density, radius, noise, cohesion weight and seed, Run, Pause, Step, Reset, a disturbance control and a live timeline of polarization and cohesion, downloadable as CSV. The worker runs `src/engine.ts`, a port of the research engine's update rules; `src/engine.test.ts` compares it with a fixture from the Python engine (`scripts/make_sandbox_fixture.py`) to an absolute tolerance of 1e-9. It uses its own random number generator, so a seed does not reproduce a published run. With reduced motion (system setting or the page's checkbox), the swarm is not animated: Run computes 300 steps and shows the final state.

The results loader fails closed: if `results.json` is missing or malformed, no number is shown.

Commands (Node from the feasibility toolchain):

    npm ci && npm test && npm run build && npm run preview
    node tools/a11y_check.mjs dist --screenshots <dir>

`tools/a11y_check.mjs` is the shared template's checker with SWARM additions (Run and Pause control the animation; reduced motion computes without animating; published and sandbox labels stay apart). It must print `A11Y-CHECK PASS`.

Repository: https://github.com/mohamedbechirkefi/swarm-local-coordination. Demo: https://swarm-local-coordination.kefimohamedbechir.workers.dev.

Hosting: the built page (`dist/`) is hosted as Cloudflare Workers static assets on the free plan, configured by `wrangler.jsonc` (assets only, no Worker script). It is deployed by the coordinator, not by any script of this repository. The page loads only same-origin files (Content-Security-Policy `default-src 'self'`).

Design (owner request of 2026-11-26): brand, typography and motion are planned in `DESIGN.md` (a starling murmuration at dusk). The hero flock (`src/Murmuration.tsx`) is a decorative boids illustration, not the research engine, labelled "Illustration, not study data"; it shows no number, pauses off screen and draws one still frame under reduced motion.

Brand files in `public/brand/`: `swarm-mark.svg` (pale, for the dusk background), `swarm-mark-ink.svg` (dark, for light backgrounds), `swarm-lockup.svg` and `swarm-lockup-ink.svg` (mark and wordmark, the wordmark drawn as paths from Bodoni Moda italic), `favicon.svg`, `favicon-32.png` and `og.png` (1200 x 630, rendered from an HTML page with headless Chrome).

Third-party notes: fonts are bundled from Fontsource packages (versions pinned in `package.json`) and served from this site.

| Family | Package and version | Licence | Used |
|---|---|---|---|
| Bodoni Moda (the Bodoni Moda Project Authors) | `@fontsource/bodoni-moda` 5.3.0 | SIL Open Font License 1.1 | latin 500 roman, 400 italic: headings, wordmark |
| Schibsted Grotesk (the Schibsted Grotesk Project Authors) | `@fontsource/schibsted-grotesk` 5.3.0 | SIL Open Font License 1.1 | latin 400, 500, 700: body, controls, figures |

Mohamed Bechir Kefi, independent researcher.
