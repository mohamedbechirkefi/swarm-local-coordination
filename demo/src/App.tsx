// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
import { useEffect, useMemo, useState } from "react";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, ARMS, type ArmId, type Estimate, type Experiment, type Results } from "./results";
import { Sandbox } from "./Sandbox";
import { ForestPlot, LineChart, type ForestRow, type Series } from "./charts";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

const ARM_NAME: Record<ArmId, string> = {
  A0: "A0 alignment only",
  A1: "A1 separation, alignment, cohesion",
  A2: "A2 centralized reference",
};
const ARM_DASH: Record<ArmId, string | undefined> = { A0: undefined, A1: "7 4", A2: "2 4" };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="site">
        <div className="wrap">
          <p className="kicker">SWARM · a preregistered simulation study</p>
          <h1>How do local interaction rules affect collective coordination under disturbances?</h1>
          <nav aria-label="Sections">
            <a href="#overview">Overview</a>
            <a href="#results">Published results</a>
            <a href="#assumptions">Assumptions</a>
            <a href="#method">Method and limitations</a>
            <a href="#sandbox">Sandbox</a>
          </nav>
        </div>
      </header>
      <main id="main" className="wrap">
        {state.kind === "loading" && <p role="status" className="panel">Loading the published results.</p>}
        {state.kind === "error" && (
          <div role="alert" className="panel error">
            <h2>Results unavailable</h2>
            <p>The published results file failed validation, so no numbers are shown.</p>
            <p><code>{state.message}</code></p>
          </div>
        )}
        {state.kind === "ready" && <Published r={state.results} />}
        <Sandbox />
      </main>
      <footer className="site">
        <div className="wrap">
          <p>
            Runs offline after the first load. No data about visitors is collected, stored or sent anywhere; the page
            makes no request to any other host.
          </p>
          <p>
            Repository and demo URL: [to be added by the owner on release]. Source-available under the SWARM
            Source-Available Non-Commercial Research License v1.0; not open source.
          </p>
        </div>
      </footer>
    </>
  );
}

function LabelKey() {
  return (
    <ul className="label-key" aria-label="How values are labelled on this page">
      <li><span className="label label-published">Published result</span> measured in the committed simulation runs (simulated, not real-world)</li>
      <li><span className="label label-exploratory">Exploratory</span> computed after the confirmatory results were seen; changes no verdict</li>
      <li><span className="label label-assumption">Assumption</span> a fixed input of the model or analysis, not a result</li>
      <li><span className="label label-sandbox">Sandbox output</span> computed in your browser from your settings</li>
    </ul>
  );
}

function Published({ r }: { r: Results }) {
  const p = r.design.primary;
  const pre = r.experiments.find((e) => e.id === "EXP-002")?.estimates.find((e) => e.label.includes("phi_pre"));
  return (
    <>
      <section id="overview" aria-labelledby="h-overview">
        <h2 id="h-overview">Overview</h2>
        <p className="status-label"><span className="badge">{r.status_label}</span></p>
        <p className="lede">
          In a two-dimensional simulation of 200 self-propelled agents, a zonal rule that adds separation and cohesion
          to alignment (A1) kept much less order than alignment alone (A0), both before and after half the agents were
          given random headings. The frozen test rejects the null hypothesis, but the gap was already present before
          the shock, so the study measured a difference in sustained order, not in recovery.
        </p>
        <div className="headline">
          <div className="headline-item">
            <p className="label label-published">Published result</p>
            <p className="big">{fmtEstimate(p)}</p>
            <p className="meta">Delta, A1 - A0 in mean post-disturbance polarization; 95% CI {fmtInterval(p)}</p>
          </div>
          {pre && (
            <div className="headline-item">
              <p className="label label-published">Published result</p>
              <p className="big">{fmtEstimate(pre)}</p>
              <p className="meta">The same contrast before the shock (phi_pre); 95% CI {fmtInterval(pre)}</p>
            </div>
          )}
          <div className="headline-item">
            <p className="label label-registered">Registered, not run</p>
            <p className="big">EXP-004</p>
            <p className="meta">Recovery with matched pre-shock order: not frozen, no data</p>
          </div>
        </div>
        <LabelKey />
      </section>

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <p className="note">
          Numbers in this section come from the committed results at revision <code>{r.code_revision.slice(0, 12)}</code> and
          are identical to the manuscript. They are separate from anything the sandbox produces. Polarization phi runs
          from 0 (no common direction) to 1 (all agents aligned).
        </p>
        <CellForest r={r} />
        <WindowTimeline r={r} />
        {r.experiments.map((e) => <ExperimentPanel key={e.id} e={e} sesoi={r.design.sesoi} />)}
        <PostHocPanel r={r} />
      </section>

      <section id="assumptions" aria-labelledby="h-assumptions">
        <h2 id="h-assumptions">Assumptions</h2>
        <p className="note"><span className="label label-assumption">Assumption</span> These are fixed inputs of the frozen design, not results.</p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          Three rules were compared under common random numbers: for each seed, every rule starts from the same
          positions and headings, sees the same noise and receives the same disturbance. The protocol, analysis code and
          seeds were frozen by the owner before the confirmatory runs. The independent unit is the (cell, seed) pair;
          time steps are never treated as independent. Decision rule: if the 95% CI excludes 0, the null hypothesis is
          rejected; if it lies inside the smallest effect of interest, the arms are practically equivalent; otherwise the
          result is inconclusive.
        </p>
        <h3>Limitations</h3>
        <ul className="limits">
          {r.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <details>
          <summary>Source files and SHA-256 hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}

function cellLabel(c: { density: number; noise: number; radius: number }): string {
  return `rho ${c.density}, eta ${c.noise}, r ${c.radius}`;
}

function CellForest({ r }: { r: Results }) {
  const [open, setOpen] = useState(false);
  const p = r.design.primary;
  const rows: ForestRow[] = r.per_cell.map((c) => ({
    key: c.cell,
    label: `${cellLabel(c)}${c.a0_not_aligned ? " *" : ""}`,
    estimate: c.a1_a0.estimate,
    lo: c.a1_a0.ci_low,
    hi: c.a1_a0.ci_high,
    text: `${c.a1_a0.display} ${c.a1_a0.interval_display}`,
    hollow: c.a0_not_aligned,
  }));
  const flagged = r.per_cell.filter((c) => c.a0_not_aligned).length;
  return (
    <figure className="panel figure" aria-labelledby="cap-forest">
      <p className="label label-published">Published result · EXP-002, confirmatory</p>
      <h3 id="cap-forest">Per-cell difference A1 - A0 in phi_post, with 95% CIs</h3>
      <div id="fig-forest" className="scroll-x" role="region" aria-label="Per-cell forest plot, scrollable" tabIndex={0}>
        <ForestPlot
          title={`Forest plot of the A1 - A0 difference in post-disturbance polarization for ${r.per_cell.length} cells`}
          rows={rows}
          domain={[-0.9, 0.1]}
          sesoi={r.design.sesoi}
          band={p.ci_low !== null && p.ci_high !== null ? { lo: p.ci_low, hi: p.ci_high, estimate: p.estimate } : undefined}
          xLabel="A1 - A0, phi_post (polarization units)"
        />
      </div>
      <figcaption>
        Each row is one cell of density rho, noise eta and radius r, with the mean paired difference over 20 seeds and
        its 95% stratified-bootstrap CI (printed on the right). The shaded band and the line inside it are the pooled
        Delta {fmtEstimate(p)} {fmtInterval(p)}. Dotted lines mark the smallest effect of interest, plus or minus{" "}
        {r.design.sesoi}. Hollow markers and * mark the {flagged} cells where A0 is not aligned before the shock. In
        words: in every cell where A0 aligns, A1 is far less polarized; where both rules are disordered, the difference
        is near zero.
      </figcaption>
      <details onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}>
        <summary>Per-cell values as a table</summary>
        {open && <div id="tbl-cells" className="table-scroll" role="region" aria-label="Per-cell values" tabIndex={0}>
          <table>
            <thead>
              <tr>
                <th scope="col">Cell</th>
                <th scope="col">A0 aligned before the shock</th>
                <th scope="col">A1 - A0, phi_post [95% CI]</th>
              </tr>
            </thead>
            <tbody>
              {r.per_cell.map((c) => (
                <tr key={c.cell}>
                  <th scope="row">{cellLabel(c)}</th>
                  <td>{c.a0_not_aligned ? "no (flagged)" : "yes"}</td>
                  <td>{c.a1_a0.display} {c.a1_a0.interval_display}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>}
      </details>
    </figure>
  );
}

function WindowTimeline({ r }: { r: Results }) {
  const d = r.design;
  const [idx, setIdx] = useState(() => {
    const k = r.per_cell.findIndex((c) => c.density === 1 && c.noise === 0.1 && c.radius === 1);
    return k >= 0 ? k : 0;
  });
  const c = r.per_cell[Math.min(idx, r.per_cell.length - 1)];
  const x0 = d.t_disturb - d.pre_window, x1 = d.t_disturb + d.window;
  const series: Series[] = useMemo(
    () =>
      ARMS.map((a) => ({
        id: a,
        label: `${ARM_NAME[a]}: phi_pre ${c.arms[a].phi_pre_display}, phi_post ${c.arms[a].phi_post_display}`,
        color: `var(--${a.toLowerCase()})`,
        dash: ARM_DASH[a],
        points: [[x0, c.arms[a].phi_pre], [d.t_disturb, c.arms[a].phi_pre], null, [d.t_disturb, c.arms[a].phi_post], [x1, c.arms[a].phi_post]],
      })),
    [c, d.t_disturb, x0, x1],
  );
  return (
    <figure className="panel figure" aria-labelledby="cap-window">
      <p className="label label-published">Published result · EXP-002, confirmatory</p>
      <h3 id="cap-window">Published metric timeline: window means around the shock</h3>
      <label className="inline">
        Cell{" "}
        <select id="pub-cell" value={idx} onChange={(e) => setIdx(Number(e.target.value))}>
          {r.per_cell.map((x, i) => (
            <option key={x.cell} value={i}>{cellLabel(x)}{x.a0_not_aligned ? " (A0 not aligned before the shock)" : ""}</option>
          ))}
        </select>
      </label>
      <LineChart
        title={`Mean polarization before and after the shock in the cell ${cellLabel(c)}`}
        series={series}
        markers={[d.t_disturb]}
        markerLabel={`shock at t_d = ${d.t_disturb}`}
        xLabel="step"
        yLabel="mean phi"
        empty="No data for this cell."
        xDomain={[x0, x1]}
      />
      <figcaption>
        For each rule, the cell mean over 20 seeds of phi over the {d.pre_window} steps before the shock (phi_pre) and
        over the {d.window} steps from the shock (phi_post). These are window means, not step-by-step curves: the
        per-step series are not committed (they are regenerated bit for bit by the frozen configurations). The
        uncertainty of the A1 - A0 difference in this cell is {c.a1_a0.display} {c.a1_a0.interval_display} (95% CI);
        seed-level spreads of each arm are in the EXP-002 report. In every cell phi_post is close to phi_pre for every
        rule: the windows mostly show each rule's sustained order level.
      </figcaption>
    </figure>
  );
}

function kindLabel(e: Experiment): { cls: string; text: string } {
  if (e.kind === "confirmatory") return { cls: "label-published", text: "Published result · confirmatory" };
  if (e.kind === "exploratory") return { cls: "label-exploratory", text: "Exploratory" };
  return { cls: "label-registered", text: "Registered, not run" };
}

function EstimateTable({ id, estimates }: { id: string; estimates: Estimate[] }) {
  return (
    <div id={`tbl-${id}`} className="table-scroll" role="region" aria-label={`${id} estimates`} tabIndex={0}>
      <table>
        <thead>
          <tr>
            <th scope="col">Quantity</th>
            <th scope="col">Estimate</th>
            <th scope="col">Uncertainty</th>
            <th scope="col">Unit</th>
          </tr>
        </thead>
        <tbody>
          {estimates.map((x) => (
            <tr key={x.label}>
              <th scope="row">{x.label}</th>
              <td className="num">{fmtEstimate(x)}</td>
              <td className="num">{x.ci_level !== null ? `${Math.round(x.ci_level * 100)}% CI ` : ""}{fmtInterval(x)}</td>
              <td>{x.unit}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ExperimentPanel({ e, sesoi }: { e: Experiment; sesoi: number }) {
  const k = kindLabel(e);
  const sens = e.id === "EXP-003";
  return (
    <article className={`panel exp exp-${e.kind}`} aria-labelledby={`h-${e.id}`}>
      <p className={`label ${k.cls}`}>{k.text}</p>
      <h3 id={`h-${e.id}`}>{e.id}: {e.title}</h3>
      <p><span className="badge">{e.status}</span></p>
      <p><strong>Verdict under the frozen rule:</strong> {e.verdict}</p>
      {e.estimates.length > 0 ? (
        <EstimateTable id={e.id} estimates={e.estimates} />
      ) : (
        <p className="empty-state">No data: this experiment has not been run, so there is no estimate to show.</p>
      )}
      {sens && (
        <div id="fig-exp003" className="scroll-x" role="region" aria-label="EXP-003 interval plot, scrollable" tabIndex={0}>
          <ForestPlot
            title="Interval plot of Delta for the EXP-002 references and each EXP-003 condition"
            rows={e.estimates.map((x, i) => ({
              key: x.label, label: x.label.replace("Delta_S, ", "").replace(" (reference)", ""), estimate: x.estimate,
              lo: x.ci_low ?? x.estimate, hi: x.ci_high ?? x.estimate,
              text: `${fmtEstimate(x)} ${fmtInterval(x)}`, emphasis: i < 2,
            }))}
            domain={[-0.6, 0.1]}
            labelWidth={210}
            sesoi={sesoi}
            xLabel="A1 - A0, phi_post (polarization units)"
          />
        </div>
      )}
      {e.notes.map((n, i) => (
        <p key={i} className="note">{n}</p>
      ))}
      <p className="meta">
        Report: <code>{e.report_path}</code>
        {e.claim_ids.length > 0 ? <> · Claims: {e.claim_ids.join(", ")}</> : <> · Claims: none</>}
      </p>
    </article>
  );
}

function PostHocPanel({ r }: { r: Results }) {
  const ph = r.post_hoc;
  return (
    <article className="panel exp exp-exploratory" aria-labelledby="h-posthoc">
      <p className="label label-exploratory">Exploratory</p>
      <h3 id="h-posthoc">{ph.id}: checks of the pre-shock confound</h3>
      <p><span className="badge">{ph.label}</span></p>
      <p>
        Subtracting each run's own pre-shock level removes the difference: the change score lies inside the smallest
        effect of interest. This does not show that the rules recover equally, because A1 had little order to lose.
      </p>
      <EstimateTable id={ph.id} estimates={ph.estimates} />
      <p className="meta">
        Source: <code>{ph.source}</code> · Claims: {ph.claim_ids.join(", ")}
      </p>
    </article>
  );
}
