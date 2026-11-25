// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
// Visitor sandbox: a small swarm simulated in a Web Worker with the browser port of the
// research engine's update rules. Its output is labelled sandbox output and is never
// mixed with the published results. Nothing is stored or sent anywhere.
import { useCallback, useEffect, useRef, useState } from "react";
import type { Arm, Params, StepRecord } from "./engine";
import { MAX_TOTAL_STEPS, type WorkerReply, type WorkerRequest } from "./sandbox.worker";
import { LineChart, type Series } from "./charts";

const HISTORY = 2000;
const BATCH_REDUCED = 300;

interface Form {
  arm: Arm;
  n: number;
  density: number;
  noise: number;
  radius: number;
  wCohesion: number;
  seed: number;
}

const DEFAULTS: Form = { arm: "A0", n: 200, density: 1, noise: 0.3, radius: 1, wCohesion: 0.5, seed: 1 };

const ARM_LABEL: Record<Arm, string> = {
  A0: "A0 alignment only",
  A1: "A1 separation, alignment, cohesion",
  A2: "A2 centralized reference",
};

function toParams(f: Form): Params {
  return {
    arm: f.arm, n: f.n, density: f.density, noise: f.noise, radius: f.radius, speed: 0.05,
    sepRatio: 0.25, wAlign: 1, wCohesion: f.wCohesion, collisionRatio: 0.1,
  };
}

function prefersReduced(): boolean {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true;
}

function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || "#888";
}

export function Sandbox() {
  const worker = useRef<Worker | null>(null);
  const canvas = useRef<HTMLCanvasElement | null>(null);
  const [form, setForm] = useState<Form>(DEFAULTS);
  const [applied, setApplied] = useState<Form>(DEFAULTS);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [reduced, setReduced] = useState(prefersReduced);
  const [stepsPerFrame, setStepsPerFrame] = useState(4);
  const [fraction, setFraction] = useState(0.5);
  const [status, setStatus] = useState("");
  const [t, setT] = useState(0);
  const [records, setRecords] = useState<StepRecord[]>([]);
  const [shocks, setShocks] = useState<number[]>([]);
  const busy = useRef(false);
  const runningRef = useRef(false);
  const lastFrame = useRef<{ x: Float32Array; theta: Float32Array; box: number } | null>(null);
  const hist = useRef<StepRecord[]>([]);
  const shockRef = useRef<number[]>([]);
  const lastUi = useRef(0);

  const draw = useCallback(() => {
    const cv = canvas.current, f = lastFrame.current;
    if (!cv || !f) return;
    const ctx = cv.getContext("2d");
    if (!ctx) return;
    const size = cv.width;
    ctx.fillStyle = cssVar("--canvas");
    ctx.fillRect(0, 0, size, size);
    ctx.strokeStyle = cssVar(`--${applied.arm.toLowerCase()}`);
    ctx.lineWidth = Math.max(1.5, size / 300);
    const scale = size / f.box;
    const len = Math.max(5, size / 70);
    ctx.beginPath();
    for (let a = 0; a < f.theta.length; a++) {
      const px = f.x[2 * a] * scale, py = size - f.x[2 * a + 1] * scale;
      ctx.moveTo(px, py);
      ctx.lineTo(px + len * Math.cos(f.theta[a]), py - len * Math.sin(f.theta[a]));
    }
    ctx.stroke();
  }, [applied.arm]);

  const drawRef = useRef(draw);
  drawRef.current = draw;

  const flushUi = useCallback((force = false) => {
    const now = performance.now();
    if (!force && now - lastUi.current < 120) return;
    lastUi.current = now;
    setRecords(hist.current.slice(-HISTORY));
    setShocks([...shockRef.current]);
  }, []);

  const post = (m: WorkerRequest) => worker.current?.postMessage(m);

  // Worker lifetime.
  useEffect(() => {
    let w: Worker;
    try {
      w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    } catch {
      setError("The browser could not start the sandbox worker.");
      return;
    }
    w.onerror = () => {
      setError("The sandbox worker stopped with an error.");
      runningRef.current = false;
      setRunning(false);
    };
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      busy.current = false;
      if (m.type === "error") {
        setError(m.message);
        runningRef.current = false;
        setRunning(false);
        return;
      }
      setError(null);
      setReady(true);
      if (m.reset) {
        hist.current = [];
        shockRef.current = [];
      }
      lastFrame.current = { x: m.x, theta: m.theta, box: m.box };
      if (m.records.length) {
        hist.current.push(...m.records);
        if (hist.current.length > HISTORY * 2) hist.current = hist.current.slice(-HISTORY);
      }
      if (m.shock) shockRef.current.push(m.shock.t);
      setT(m.t);
      drawRef.current();
      flushUi(m.reset || !runningRef.current || m.shock !== null);
      if (m.limitReached && runningRef.current) {
        runningRef.current = false;
        setRunning(false);
        flushUi(true);
        setStatus(`Sandbox stopped at the ${MAX_TOTAL_STEPS.toLocaleString("en")}-step limit. Reset to start again.`);
      }
    };
    worker.current = w;
    w.postMessage({ type: "reset", params: toParams(DEFAULTS), seed: DEFAULTS.seed } satisfies WorkerRequest);
    return () => w.terminate();
  }, [flushUi]);

  // Follow the system reduced-motion setting while the visitor has not chosen.
  useEffect(() => {
    const mq = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (!mq) return;
    const on = () => setReduced(mq.matches);
    mq.addEventListener?.("change", on);
    return () => mq.removeEventListener?.("change", on);
  }, []);

  // Animation loop (only while running and motion is allowed).
  useEffect(() => {
    if (!running || reduced) return;
    let raf = 0;
    const tick = () => {
      if (!runningRef.current) return;
      if (!busy.current) {
        busy.current = true;
        post({ type: "advance", steps: stepsPerFrame });
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [running, reduced, stepsPerFrame]);

  useEffect(() => {
    if (reduced && runningRef.current) {
      runningRef.current = false;
      setRunning(false);
      setStatus("Animation paused because reduced motion is on.");
    }
  }, [reduced]);

  useEffect(draw, [draw]);

  const atLimit = t >= MAX_TOTAL_STEPS;

  const run = () => {
    if (!ready || atLimit) return;
    if (reduced) {
      busy.current = true;
      post({ type: "advance", steps: BATCH_REDUCED });
      setStatus(`Computed ${BATCH_REDUCED} steps without animation (reduced motion). Sandbox output, seed ${applied.seed}.`);
      return;
    }
    if (running) {
      runningRef.current = false;
      setRunning(false);
      flushUi(true);
      setStatus("Sandbox paused.");
    } else {
      runningRef.current = true;
      setRunning(true);
      setStatus(`Sandbox running: ${ARM_LABEL[applied.arm]}, seed ${applied.seed}.`);
    }
  };

  const stepOnce = () => {
    if (!ready || running || atLimit) return;
    busy.current = true;
    post({ type: "advance", steps: 10 });
  };

  const reset = () => {
    runningRef.current = false;
    setRunning(false);
    setApplied(form);
    setT(0);
    post({ type: "reset", params: toParams(form), seed: form.seed });
    setStatus(`Sandbox reset: ${ARM_LABEL[form.arm]}, ${form.n} agents, seed ${form.seed}.`);
  };

  const disturb = () => {
    if (!ready || atLimit) return;
    post({ type: "disturb", fraction });
    setStatus(`Disturbance at step ${t}: ${Math.round(fraction * applied.n)} agents given random headings.`);
  };

  const download = () => {
    const p = applied;
    const lines = [
      "# SWARM sandbox output, produced in the browser. Not a research result.",
      `# arm=${p.arm} n=${p.n} density=${p.density} noise=${p.noise} radius=${p.radius} w_cohesion=${p.wCohesion} seed=${p.seed}`,
      `# disturbances at steps: ${shockRef.current.join(" ") || "none"}`,
      "t,phi,cohesion,collision_pairs",
      ...hist.current.map((r) => `${r.t},${r.phi},${r.cohesion},${r.collisions}`),
    ];
    const url = URL.createObjectURL(new Blob([lines.join("\n") + "\n"], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `swarm-sandbox-${p.arm}-seed${p.seed}.csv`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const last = records.length ? records[records.length - 1] : null;
  const series: Series[] = [
    { id: "phi", label: "polarization phi", color: "var(--fg)", points: records.map((r) => [r.t, r.phi]) },
    { id: "coh", label: "cohesion C", color: "var(--sandbox)", dash: "5 4", points: records.map((r) => [r.t, r.cohesion]) },
  ];
  const changed = JSON.stringify(form) !== JSON.stringify(applied);
  const set = <K extends keyof Form>(k: K, v: Form[K]) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox" data-animating={running && !reduced ? "true" : "false"} data-step={t}>
      <p className="label label-sandbox">Sandbox output</p>
      <h2 id="h-sandbox">Swarm sandbox</h2>
      <p className="note">
        Everything in this box is computed in your browser from your settings. It uses the same update rules as the
        research engine (checked against a Python fixture to within 1e-9), but a different random number generator,
        fewer steps and brute-force neighbour search, so a seed here does not reproduce any published run. It is not a
        research result and is not comparable to the published numbers above.
      </p>

      {error && (
        <div role="alert" className="panel error">
          <p><strong>The sandbox stopped.</strong> {error}</p>
          <p>The published results above are not affected. Press Reset to try again.</p>
        </div>
      )}

      <fieldset className="controls">
        <legend>Model settings (applied on Reset)</legend>
        <label>
          Rule
          <select id="sb-arm" value={form.arm} onChange={(e) => set("arm", e.target.value as Arm)}>
            {(["A0", "A1", "A2"] as Arm[]).map((a) => <option key={a} value={a}>{ARM_LABEL[a]}</option>)}
          </select>
        </label>
        <label>
          Agents N
          <select id="sb-n" value={form.n} onChange={(e) => set("n", Number(e.target.value))}>
            {[50, 100, 200, 300].map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </label>
        <label>
          Density rho
          <select id="sb-density" value={form.density} onChange={(e) => set("density", Number(e.target.value))}>
            {[0.5, 1, 2].map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </label>
        <label>
          Radius r
          <select id="sb-radius" value={form.radius} onChange={(e) => set("radius", Number(e.target.value))}>
            {[0.5, 1].map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </label>
        <label>
          Noise eta: {form.noise.toFixed(2)}
          <input type="range" min={0} max={1} step={0.05} id="sb-noise" value={form.noise} onChange={(e) => set("noise", Number(e.target.value))} />
        </label>
        <label>
          Cohesion weight w_c (A1): {form.wCohesion.toFixed(2)}
          <input type="range" min={0} max={2} step={0.05} id="sb-wc" value={form.wCohesion} disabled={form.arm !== "A1"} onChange={(e) => set("wCohesion", Number(e.target.value))} />
        </label>
        <label>
          Seed
          <input type="number" min={0} max={1_000_000} step={1} id="sb-seed" value={form.seed} onChange={(e) => set("seed", Math.max(0, Math.min(1_000_000, Math.floor(Number(e.target.value) || 0))))} />
        </label>
        <button type="button" onClick={reset}>Reset{changed ? " with new settings" : ""}</button>
      </fieldset>

      <div className="controls">
        <button type="button" onClick={run} disabled={!ready || atLimit} aria-pressed={reduced ? undefined : running}>
          {running ? "Pause" : reduced ? "Run 300 steps" : "Run"}
        </button>
        <button type="button" onClick={stepOnce} disabled={!ready || running || atLimit}>Step 10</button>
        <label>
          Disturbance size: {Math.round(fraction * 100)}% of agents
          <input type="range" min={0} max={1} step={0.05} id="sb-fraction" value={fraction} onChange={(e) => setFraction(Number(e.target.value))} />
        </label>
        <button type="button" onClick={disturb} disabled={!ready || atLimit}>Disturb now</button>
        <label>
          Steps per frame
          <select id="sb-spf" value={stepsPerFrame} onChange={(e) => setStepsPerFrame(Number(e.target.value))} disabled={reduced}>
            {[1, 2, 4, 8].map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </label>
        <label className="check">
          <input type="checkbox" id="sb-reduced" checked={reduced} onChange={(e) => setReduced(e.target.checked)} /> Reduce motion
        </label>
      </div>

      <p aria-live="polite" className="sandbox-out">{status}</p>

      <div className="sandbox-grid">
        <figure className="swarm-fig">
          <canvas
            ref={canvas}
            width={480}
            height={480}
            role="img"
            aria-label={`Swarm sandbox, ${ARM_LABEL[applied.arm]}, ${applied.n} agents, step ${t}${last ? `, polarization ${last.phi.toFixed(2)}` : ""}. Each stroke is one agent pointing along its heading.`}
          />
          <figcaption className="meta">
            {!ready && !error ? "Starting the sandbox engine." : `Step ${t} of at most ${MAX_TOTAL_STEPS.toLocaleString("en")}. Periodic box; each stroke is one agent and points along its heading.`}
          </figcaption>
        </figure>
        <figure className="timeline-fig">
          <p className="readout" aria-hidden={!last}>
            {last ? (
              <>phi {last.phi.toFixed(3)} · cohesion {last.cohesion.toFixed(3)} · step {last.t}</>
            ) : (
              <>No sandbox steps yet. Press Run or Step 10.</>
            )}
          </p>
          <LineChart
            title="Sandbox metric timeline"
            series={series}
            markers={shocks}
            xLabel="step"
            yLabel="value (0 to 1)"
            empty="No sandbox steps yet."
          />
          <figcaption className="meta">
            Sandbox metric timeline: polarization phi (solid) and cohesion C, the fraction of agents in the largest
            group of agents within radius r of each other (dashed), for the last {HISTORY.toLocaleString("en")} steps.
            Vertical lines mark your disturbances. Phi near 1 means agents move in one direction; near 0, no common
            direction.
          </figcaption>
          <button type="button" onClick={download} disabled={records.length === 0}>Download sandbox series (CSV)</button>
        </figure>
      </div>
    </section>
  );
}
