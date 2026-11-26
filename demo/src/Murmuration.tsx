// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
// Hero illustration: a decorative boids flock in the dusk sky. It is not the
// study's engine and shows no number. On load the birds start scattered and
// fold into one murmuration; a little later half of them get random headings
// (the study's kind of disturbance) and the flock regroups. The visitor can
// repeat the disturbance. It pauses off screen and in background tabs; under
// reduced motion it draws one still frame of a formed flock.
import { useCallback, useEffect, useRef, useState } from "react";

interface Flock { x: Float32Array; y: Float32Array; vx: Float32Array; vy: Float32Array; n: number; t: number }

function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function prefersReduced(): boolean {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true;
}

const SPEED = 2.2, VIEW = 44, SEP = 14;

function makeFlock(n: number, w: number, h: number, r: () => number): Flock {
  const f: Flock = { x: new Float32Array(n), y: new Float32Array(n), vx: new Float32Array(n), vy: new Float32Array(n), n, t: 0 };
  for (let i = 0; i < n; i++) {
    f.x[i] = w * (0.15 + 0.85 * r()); f.y[i] = h * (0.25 + 0.75 * r());
    const a = r() * Math.PI * 2;
    f.vx[i] = Math.cos(a) * SPEED; f.vy[i] = Math.sin(a) * SPEED;
  }
  return f;
}

/** Where the flock is drawn towards: a slow figure-of-eight in the glow. */
function anchor(t: number, w: number, h: number): [number, number] {
  const wide = w > 720;
  const cx = wide ? w * 0.7 : w * 0.5, cy = wide ? h * 0.66 : h * 0.74;
  const ax = wide ? w * 0.14 : w * 0.26, ay = wide ? h * 0.09 : h * 0.06;
  return [cx + ax * Math.sin(t * 0.0042), cy + ay * Math.sin(t * 0.0084)];
}

function step(f: Flock, w: number, h: number) {
  const { x, y, vx, vy, n } = f;
  const [tx, ty] = anchor(f.t, w, h);
  const nvx = new Float32Array(n), nvy = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    let ax = 0, ay = 0, cx = 0, cy = 0, sx = 0, sy = 0, k = 0;
    for (let j = 0; j < n; j++) {
      if (i === j) continue;
      const dx = x[j] - x[i], dy = y[j] - y[i];
      const d2 = dx * dx + dy * dy;
      if (d2 < VIEW * VIEW) {
        ax += vx[j]; ay += vy[j]; cx += dx; cy += dy; k++;
        if (d2 < SEP * SEP) { const d = Math.sqrt(d2) || 1; sx -= dx / d; sy -= dy / d; }
      }
    }
    let ux = vx[i], uy = vy[i];
    if (k > 0) {
      ux += (ax / k - vx[i]) * 0.06 + (cx / k) * 0.003;
      uy += (ay / k - vy[i]) * 0.06 + (cy / k) * 0.003;
    }
    ux += sx * 0.065; uy += sy * 0.065;
    {
      // Turn towards the anchor, harder the further away; keep off the edges.
      const dx = tx - x[i], dy = ty - y[i], d = Math.hypot(dx, dy) || 1;
      const pull = 0.07 * Math.min(2, d / 140);
      ux += (dx / d) * pull; uy += (dy / d) * pull;
      const m = 50;
      if (x[i] < m) ux += 0.12; else if (x[i] > w - m) ux -= 0.12;
      if (y[i] < m) uy += 0.12; else if (y[i] > h - m) uy -= 0.12;
    }
    const s = Math.hypot(ux, uy) || 1;
    const sp = Math.min(SPEED * 1.25, Math.max(SPEED * 0.75, s));
    nvx[i] = (ux / s) * sp; nvy[i] = (uy / s) * sp;
  }
  for (let i = 0; i < n; i++) { vx[i] = nvx[i]; vy[i] = nvy[i]; x[i] += vx[i]; y[i] += vy[i]; }
  f.t++;
}

function scatter(f: Flock, r: () => number) {
  for (let i = 0; i < f.n; i++) {
    if (r() < 0.5) {
      const a = r() * Math.PI * 2;
      f.vx[i] = Math.cos(a) * SPEED * 1.2; f.vy[i] = Math.sin(a) * SPEED * 1.2;
    }
  }
}

export function Murmuration() {
  const cv = useRef<HTMLCanvasElement>(null);
  const flock = useRef<Flock | null>(null);
  const rand = useRef(rng(7));
  const [reduced, setReduced] = useState(prefersReduced);

  useEffect(() => {
    const mq = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (!mq) return;
    const on = () => setReduced(mq.matches);
    mq.addEventListener?.("change", on);
    return () => mq.removeEventListener?.("change", on);
  }, []);

  useEffect(() => {
    const c = cv.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    let w = 0, h = 0, raf = 0, visible = true, alpha = 0, autoShock = 260;
    const resize = () => {
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      const rect = c.getBoundingClientRect();
      const nw = Math.max(1, Math.round(rect.width)), nh = Math.max(1, Math.round(rect.height));
      c.width = nw * dpr; c.height = nh * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (!flock.current || Math.abs(nw - w) > 80) flock.current = makeFlock(nw < 720 ? 180 : 340, nw, nh, rand.current);
      w = nw; h = nh;
    };
    const draw = () => {
      const f = flock.current!;
      ctx.clearRect(0, 0, w, h);
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = "#15122a";
      ctx.lineWidth = 2.4;
      ctx.lineCap = "round";
      ctx.beginPath();
      for (let i = 0; i < f.n; i++) {
        const s = Math.hypot(f.vx[i], f.vy[i]) || 1;
        ctx.moveTo(f.x[i] - (f.vx[i] / s) * 3.4, f.y[i] - (f.vy[i] / s) * 3.4);
        ctx.lineTo(f.x[i] + (f.vx[i] / s) * 3.4, f.y[i] + (f.vy[i] / s) * 3.4);
      }
      ctx.stroke();
      ctx.globalAlpha = 1;
    };
    resize();
    if (reduced) {
      for (let k = 0; k < 600; k++) step(flock.current!, w, h);
      alpha = 0.9; draw();
      const ro = new ResizeObserver(() => { resize(); for (let k = 0; k < 600; k++) step(flock.current!, w, h); draw(); });
      ro.observe(c);
      return () => ro.disconnect();
    }
    const loop = () => {
      if (!visible || document.hidden) { raf = 0; return; }
      step(flock.current!, w, h);
      if (alpha < 0.9) alpha = Math.min(0.9, alpha + 0.03);
      if (autoShock > 0 && --autoShock === 0) scatter(flock.current!, rand.current);
      draw();
      raf = requestAnimationFrame(loop);
    };
    const start = () => { if (!raf && visible && !document.hidden) raf = requestAnimationFrame(loop); };
    const io = new IntersectionObserver((es) => { visible = es.some((e) => e.isIntersecting); start(); });
    io.observe(c);
    const ro = new ResizeObserver(resize);
    ro.observe(c);
    document.addEventListener("visibilitychange", start);
    start();
    return () => { cancelAnimationFrame(raf); io.disconnect(); ro.disconnect(); document.removeEventListener("visibilitychange", start); };
  }, [reduced]);

  const disturb = useCallback(() => { if (flock.current) scatter(flock.current, rand.current); }, []);

  return (
    <div className="flock">
      <canvas ref={cv} className="flock-canvas" aria-hidden="true" />
      <div className="flock-note">
        {!reduced && <button type="button" className="ghost" onClick={disturb}>Scatter half the flock</button>}
        <p>Illustration, not study data: a decorative flock drawn in your browser, not the study's model.</p>
      </div>
    </div>
  );
}
