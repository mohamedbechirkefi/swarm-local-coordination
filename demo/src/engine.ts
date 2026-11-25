// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
// Browser port of the SWARM research engine's update rules (src/swarm/simulate.py,
// rules.py, geometry.py, metrics.py), periodic boundary and metric neighbourhoods only.
// The port follows the engine's step order and floating-point summation order;
// demo/src/engine.test.ts checks it against a fixture written by the Python engine
// (scripts/make_sandbox_fixture.py). Differences from the research engine:
//   - neighbours are found by brute force (the engine's cell list returns the same
//     pairs; it is tested against brute force in the Python suite), so the
//     distance-evaluation count is not reproduced;
//   - random numbers come from a small seeded generator (mulberry32), not numpy's
//     PCG64, so a seed here does not reproduce the research run with that seed.
// Units: lengths in model units u, time in steps, angles in radians.

export type Arm = "A0" | "A1" | "A2";

export interface Params {
  arm: Arm;
  n: number;
  density: number;
  noise: number;
  radius: number;
  speed: number;
  sepRatio: number;
  wAlign: number;
  wCohesion: number;
  collisionRatio: number;
}

export interface State {
  x: Float64Array; // 2n, interleaved (x0, y0, x1, y1, ...)
  theta: Float64Array; // n
  box: number;
  t: number;
}

export interface StepRecord {
  t: number;
  phi: number;
  cohesion: number;
  collisions: number;
}

export const ZERO_TOL = 1e-12;
const PI = Math.PI;
const TWO_PI = 2 * Math.PI;

export const LIMITS = {
  n: [20, 300],
  density: [0.25, 2],
  noise: [0, 1],
  radius: [0.25, 1.5],
  wCohesion: [0, 2],
} as const;

export function boxSide(n: number, density: number): number {
  return Math.sqrt(n / density);
}

/** Throws on parameters outside the bounded sandbox range (explicit error path). */
export function checkParams(p: Params): void {
  const inRange = (v: number, [lo, hi]: readonly [number, number], name: string) => {
    if (!Number.isFinite(v) || v < lo || v > hi) throw new RangeError(`${name} must be in [${lo}, ${hi}]`);
  };
  if (!["A0", "A1", "A2"].includes(p.arm)) throw new RangeError("unknown arm");
  if (!Number.isInteger(p.n)) throw new RangeError("n must be an integer");
  inRange(p.n, LIMITS.n, "n");
  inRange(p.density, LIMITS.density, "density");
  inRange(p.noise, LIMITS.noise, "noise");
  inRange(p.radius, LIMITS.radius, "radius");
  inRange(p.wCohesion, LIMITS.wCohesion, "cohesion weight");
  if (p.radius >= boxSide(p.n, p.density) / 2) throw new RangeError("radius must be below half the box side");
}

/** numpy.mod for floats (result takes the sign of the divisor). */
export function pyMod(a: number, b: number): number {
  let m = a % b;
  if (m !== 0) {
    if (b < 0 !== m < 0) m += b;
  } else {
    m = b < 0 ? -0 : 0;
  }
  return m;
}

/** numpy.round: round half to even. */
export function roundHalfEven(v: number): number {
  const r = Math.round(v);
  if (Math.abs(v % 1) === 0.5 && r % 2 !== 0) return r - 1;
  return r;
}

/** geometry.wrap_angle: map to (-pi, pi], values already inside unchanged. */
export function wrapAngle(a: number): number {
  if (a > -PI && a <= PI) return a;
  let out = pyMod(a + PI, TWO_PI) - PI;
  if (out <= -PI) out += TWO_PI;
  return out;
}

/** geometry.wrap_positions for one coordinate. */
export function wrapPos(v: number, box: number): number {
  const y = pyMod(v, box);
  return y >= box ? y - box : y;
}

/** numpy pairwise summation (float64 add.reduce) for contiguous data. */
export function pairwiseSum(a: ArrayLike<number>, start = 0, n = a.length - start): number {
  if (n < 8) {
    let res = 0;
    for (let i = 0; i < n; i++) res += a[start + i];
    return res;
  }
  if (n <= 128) {
    const r = [a[start], a[start + 1], a[start + 2], a[start + 3], a[start + 4], a[start + 5], a[start + 6], a[start + 7]];
    let i = 8;
    for (; i < n - (n % 8); i += 8) {
      for (let k = 0; k < 8; k++) r[k] += a[start + i + k];
    }
    let res = (r[0] + r[1] + (r[2] + r[3])) + (r[4] + r[5] + (r[6] + r[7]));
    for (; i < n; i++) res += a[start + i];
    return res;
  }
  let n2 = Math.floor(n / 2);
  n2 -= n2 % 8;
  return pairwiseSum(a, start, n2) + pairwiseSum(a, start + n2, n - n2);
}

/** metrics.polarization: |mean of unit heading vectors|, clipped to 1. */
export function polarization(theta: Float64Array): number {
  const n = theta.length;
  if (n === 0) throw new RangeError("polarization of an empty group is undefined");
  const c = new Float64Array(n);
  const s = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    c[i] = Math.cos(theta[i]);
    s[i] = Math.sin(theta[i]);
  }
  return Math.min(1, Math.hypot(pairwiseSum(c) / n, pairwiseSum(s) / n));
}

export interface Pairs {
  i: Int32Array;
  j: Int32Array;
  dx: Float64Array; // displacement from i to j (minimum image)
  dy: Float64Array;
  dist: Float64Array;
  count: number;
}

/** All pairs i < j with distance <= r, in lexicographic order (brute force). */
export function metricPairs(x: Float64Array, box: number, radius: number): Pairs {
  const n = x.length / 2;
  const cap = 1024;
  let size = cap;
  let I = new Int32Array(size), J = new Int32Array(size);
  let DX = new Float64Array(size), DY = new Float64Array(size), D = new Float64Array(size);
  let k = 0;
  for (let i = 0; i < n; i++) {
    const xi = x[2 * i], yi = x[2 * i + 1];
    for (let j = i + 1; j < n; j++) {
      let dx = x[2 * j] - xi;
      let dy = x[2 * j + 1] - yi;
      dx = dx - box * roundHalfEven(dx / box);
      dy = dy - box * roundHalfEven(dy / box);
      const d = Math.hypot(dx, dy);
      if (d <= radius) {
        if (k === size) {
          size *= 2;
          const grow = <T extends Int32Array | Float64Array>(a: T, C: new (n: number) => T): T => {
            const b = new C(size);
            b.set(a);
            return b;
          };
          I = grow(I, Int32Array); J = grow(J, Int32Array);
          DX = grow(DX, Float64Array); DY = grow(DY, Float64Array); D = grow(D, Float64Array);
        }
        I[k] = i; J[k] = j; DX[k] = dx; DY[k] = dy; D[k] = d;
        k++;
      }
    }
  }
  return { i: I, j: J, dx: DX, dy: DY, dist: D, count: k };
}

function headingOrKeep(vx: number, vy: number, theta: number): number {
  return Math.hypot(vx, vy) > ZERO_TOL ? Math.atan2(vy, vx) : theta;
}

/**
 * Desired headings before noise. Accumulation follows numpy.bincount over the
 * directed edge list concat(i -> j, j -> i): first every pair where the agent is i,
 * then every pair where it is j, each in lexicographic pair order.
 */
export function desiredHeadings(p: Params, theta: Float64Array, pr: Pairs): Float64Array {
  const n = theta.length;
  const out = new Float64Array(n);
  const cos = new Float64Array(n), sin = new Float64Array(n);
  for (let a = 0; a < n; a++) {
    cos[a] = Math.cos(theta[a]);
    sin[a] = Math.sin(theta[a]);
  }
  if (p.arm === "A2") {
    const gx = pairwiseSum(cos), gy = pairwiseSum(sin);
    if (Math.hypot(gx, gy) <= ZERO_TOL) return Float64Array.from(theta);
    out.fill(Math.atan2(gy, gx));
    return out;
  }
  const sx = new Float64Array(n), sy = new Float64Array(n);
  const visit = (f: (recv: number, other: number, dx: number, dy: number, d: number) => void) => {
    for (let k = 0; k < pr.count; k++) f(pr.i[k], pr.j[k], pr.dx[k], pr.dy[k], pr.dist[k]);
    for (let k = 0; k < pr.count; k++) f(pr.j[k], pr.i[k], -pr.dx[k], -pr.dy[k], pr.dist[k]);
  };
  visit((r, o) => {
    sx[r] += cos[o];
    sy[r] += sin[o];
  });
  if (p.arm === "A0") {
    for (let a = 0; a < n; a++) out[a] = headingOrKeep(cos[a] + sx[a], sin[a] + sy[a], theta[a]);
    return out;
  }
  // A1: separation has priority within r_sep; otherwise w_a * a + w_c * c.
  const rSep = p.sepRatio * p.radius;
  const hasSep = new Uint8Array(n);
  const sepx = new Float64Array(n), sepy = new Float64Array(n);
  const cnt = new Float64Array(n), mx = new Float64Array(n), my = new Float64Array(n);
  visit((r, _o, dx, dy, d) => {
    const inSep = d <= rSep;
    if (inSep) hasSep[r] = 1;
    const w = inSep && d > 0 ? 1 / d : 0;
    sepx[r] += dx * w;
    sepy[r] += dy * w;
    cnt[r] += 1;
    mx[r] += dx;
    my[r] += dy;
  });
  for (let a = 0; a < n; a++) {
    let ax = cos[a] + sx[a], ay = sin[a] + sy[a];
    const an = Math.hypot(ax, ay);
    if (an > ZERO_TOL) { ax /= an; ay /= an; } else { ax = 0; ay = 0; }
    const safe = cnt[a] > 0 ? cnt[a] : 1;
    let cx = mx[a] / safe, cy = my[a] / safe;
    const cn = Math.hypot(cx, cy);
    if (cn > ZERO_TOL) { cx /= cn; cy /= cn; } else { cx = 0; cy = 0; }
    const dx = hasSep[a] ? -sepx[a] : p.wAlign * ax + p.wCohesion * cx;
    const dy = hasSep[a] ? -sepy[a] : p.wAlign * ay + p.wCohesion * cy;
    out[a] = headingOrKeep(dx, dy, theta[a]);
  }
  return out;
}

/** metrics.largest_component_fraction (union-find with path halving). */
export function largestComponentFraction(n: number, pr: Pairs): number {
  const parent = new Int32Array(n);
  for (let a = 0; a < n; a++) parent[a] = a;
  const find = (a: number) => {
    while (parent[a] !== a) {
      parent[a] = parent[parent[a]];
      a = parent[a];
    }
    return a;
  };
  for (let k = 0; k < pr.count; k++) {
    const ra = find(pr.i[k]), rb = find(pr.j[k]);
    if (ra !== rb) {
      if (ra < rb) parent[rb] = ra;
      else parent[ra] = rb;
    }
  }
  const size = new Int32Array(n);
  let best = 0;
  for (let a = 0; a < n; a++) best = Math.max(best, ++size[find(a)]);
  return best / n;
}

/** Applies a heading shock: the listed agents take the given headings. */
export function applyShock(s: State, agents: ArrayLike<number>, headings: ArrayLike<number>): void {
  for (let k = 0; k < agents.length; k++) s.theta[agents[k]] = headings[k];
}

/**
 * One synchronous step, in the engine's order: neighbours of the state at t,
 * record phi(t), cohesion and collisions, desired headings, noise, move, wrap.
 * `noise` holds one draw per agent from Uniform(-eta*pi, eta*pi).
 */
export function step(p: Params, s: State, noise: ArrayLike<number>): StepRecord {
  const n = s.theta.length;
  const pr = metricPairs(s.x, s.box, p.radius);
  const phi = polarization(s.theta);
  const cohesion = largestComponentFraction(n, pr);
  const dc = p.collisionRatio * p.radius;
  let collisions = 0;
  for (let k = 0; k < pr.count; k++) if (pr.dist[k] < dc) collisions++;
  const desired = desiredHeadings(p, s.theta, pr);
  for (let a = 0; a < n; a++) {
    const th = wrapAngle(desired[a] + noise[a]);
    s.theta[a] = th;
    const nx = s.x[2 * a] + p.speed * Math.cos(th);
    const ny = s.x[2 * a + 1] + p.speed * Math.sin(th);
    s.x[2 * a] = wrapPos(nx, s.box);
    s.x[2 * a + 1] = wrapPos(ny, s.box);
    if (!Number.isFinite(s.x[2 * a]) || !Number.isFinite(s.x[2 * a + 1]) || !Number.isFinite(th)) {
      throw new Error(`non-finite state at step ${s.t}`);
    }
  }
  const rec = { t: s.t, phi, cohesion, collisions };
  s.t += 1;
  return rec;
}

/** Seeded 32-bit generator (mulberry32); sandbox only, not numpy's PCG64. */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Three independent sandbox streams from one seed (initial state, noise, disturbance). */
export function makeStreams(seed: number) {
  const mix = (k: number) => Math.imul(seed ^ (k * 0x9e3779b9), 0x85ebca6b) ^ (k * 0xc2b2ae35);
  return { init: mulberry32(mix(1)), noise: mulberry32(mix(2)), disturb: mulberry32(mix(3)) };
}

export function initialState(p: Params, rand: () => number): State {
  const box = boxSide(p.n, p.density);
  const x = new Float64Array(2 * p.n);
  for (let k = 0; k < 2 * p.n; k++) x[k] = wrapPos(rand() * box, box);
  const theta = new Float64Array(p.n);
  for (let a = 0; a < p.n; a++) theta[a] = wrapAngle(-PI + rand() * TWO_PI);
  return { x, theta, box, t: 0 };
}

/** Picks round(f * n) distinct agents and new uniform headings (partial Fisher-Yates). */
export function drawShock(n: number, fraction: number, rand: () => number): { agents: number[]; headings: number[] } {
  const k = Math.round(fraction * n);
  const idx = Array.from({ length: n }, (_, i) => i);
  for (let a = 0; a < k; a++) {
    const b = a + Math.floor(rand() * (n - a));
    [idx[a], idx[b]] = [idx[b], idx[a]];
  }
  const agents = idx.slice(0, k).sort((u, v) => u - v);
  return { agents, headings: agents.map(() => wrapAngle(-PI + rand() * TWO_PI)) };
}

export function drawNoise(n: number, eta: number, rand: () => number): Float64Array {
  const half = eta * PI;
  const out = new Float64Array(n);
  for (let a = 0; a < n; a++) out[a] = -half + 2 * half * rand();
  return out;
}

/** metrics.recovery_time on a recorded phi series (steps after t_d, censored flag). */
export function recoveryTime(phi: ArrayLike<number>, tD: number, window: number, phiPre: number, threshold: number, hold: number): [number | null, boolean] {
  const target = threshold * phiPre;
  const end = Math.min(tD + window, phi.length);
  if (end - tD < hold) return [null, true];
  let run = 0;
  for (let k = 0; k < end - tD; k++) {
    run = phi[tD + k] >= target ? run + 1 : 0;
    if (run >= hold) return [k - hold + 1, false];
  }
  return [null, true];
}

export function mean(a: ArrayLike<number>, lo: number, hi: number): number {
  let s = 0;
  for (let k = lo; k < hi; k++) s += a[k];
  return s / (hi - lo);
}
