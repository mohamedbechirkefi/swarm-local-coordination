// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
// Compares the browser port (engine.ts) with a fixture written by the Python research
// engine (scripts/make_sandbox_fixture.py): same initial state, same shock and the same
// per-step noise draws, so any difference comes from the update rules or from
// floating-point library differences. Tolerance: 1e-9 absolute on every value.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import {
  applyShock, checkParams, drawShock, initialState, makeStreams, mean, pairwiseSum,
  recoveryTime, step, wrapAngle, type Arm, type Params, type State,
} from "./engine";

const TOL = 1e-9;
const fx = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8"));
const c = fx.config;

function params(arm: Arm): Params {
  return {
    arm, n: c.n_agents, density: c.density, noise: c.noise, radius: c.radius, speed: c.speed,
    sepRatio: c.sep_ratio, wAlign: c.w_align, wCohesion: c.w_cohesion, collisionRatio: c.collision_ratio,
  };
}

function runPort(arm: Arm) {
  const p = params(arm);
  const s: State = { x: Float64Array.from(fx.init.x), theta: Float64Array.from(fx.init.theta), box: fx.box, t: 0 };
  const phi: number[] = [], coh: number[] = [];
  let collisions = 0;
  let x10: Float64Array | null = null;
  for (let t = 0; t < c.steps; t++) {
    if (t === c.t_disturb) applyShock(s, fx.init.shock_agents, fx.init.shock_headings);
    const r = step(p, s, fx.init.noise[t]);
    phi.push(r.phi);
    if (t >= c.t_disturb && t < c.t_disturb + c.window) {
      coh.push(r.cohesion);
      collisions += r.collisions;
    }
    if (t === 9) x10 = Float64Array.from(s.x);
  }
  const phiPre = mean(phi, c.t_disturb - c.pre_window, c.t_disturb);
  return {
    s, phi, x10: x10!, phiPre,
    phiPost: mean(phi, c.t_disturb, c.t_disturb + c.window),
    cohesion: mean(coh, 0, coh.length),
    collisions: (100 * collisions) / (c.n_agents * c.window),
    tau: recoveryTime(phi, c.t_disturb, c.window, phiPre, c.recovery_threshold, c.recovery_hold),
  };
}

const maxAbs = (a: ArrayLike<number>, b: ArrayLike<number>) => {
  expect(a.length).toBe(b.length);
  let m = 0;
  for (let k = 0; k < a.length; k++) m = Math.max(m, Math.abs(a[k] - b[k]));
  return m;
};

describe("engine port against the Python research engine fixture", () => {
  for (const arm of ["A0", "A1", "A2"] as Arm[]) {
    it(`${arm}: phi series, positions, headings and metrics within ${TOL}`, () => {
      const got = runPort(arm);
      const want = fx.arms[arm];
      const ePhi = maxAbs(got.phi, want.phi);
      expect(ePhi).toBeLessThanOrEqual(TOL);
      expect(maxAbs(got.x10, want.x_step10)).toBeLessThanOrEqual(TOL);
      expect(maxAbs(got.s.x, want.x_final)).toBeLessThanOrEqual(TOL);
      // Headings compared on the circle.
      let dth = 0;
      for (let k = 0; k < got.s.theta.length; k++) {
        dth = Math.max(dth, Math.abs(wrapAngle(got.s.theta[k] - want.theta_final[k])));
      }
      expect(dth).toBeLessThanOrEqual(TOL);
      const m = want.metrics;
      expect(Math.abs(got.phiPre - m.phi_pre)).toBeLessThanOrEqual(TOL);
      expect(Math.abs(got.phiPost - m.phi_post)).toBeLessThanOrEqual(TOL);
      expect(Math.abs(got.cohesion - m.cohesion_post)).toBeLessThanOrEqual(TOL);
      expect(Math.abs(got.collisions - m.collisions_per_agent_per_100)).toBeLessThanOrEqual(TOL);
      expect(got.tau[0]).toBe(m.tau);
      expect(got.tau[1]).toBe(m.tau_censored);
    });
  }
});

describe("engine helpers", () => {
  it("wrapAngle maps to (-pi, pi] and keeps values already inside", () => {
    expect(wrapAngle(Math.PI)).toBe(Math.PI);
    expect(wrapAngle(-Math.PI)).toBeCloseTo(Math.PI, 15);
    expect(wrapAngle(0.25)).toBe(0.25);
    expect(wrapAngle(3 * Math.PI + 0.5)).toBeCloseTo(-Math.PI + 0.5, 12);
  });
  it("pairwiseSum agrees with a plain sum on small exact inputs", () => {
    const a = Array.from({ length: 300 }, (_, i) => i);
    expect(pairwiseSum(a)).toBe(44850);
  });
  it("sandbox runs are deterministic for a seed", () => {
    const p = params("A1");
    const run = () => {
      const st = makeStreams(42);
      const s = initialState(p, st.init);
      const sh = drawShock(p.n, 0.5, st.disturb);
      applyShock(s, sh.agents, sh.headings);
      return step(p, s, new Float64Array(p.n)).phi;
    };
    expect(run()).toBe(run());
  });
  it("drawShock picks round(f n) distinct agents", () => {
    const sh = drawShock(40, 0.5, makeStreams(3).disturb);
    expect(new Set(sh.agents).size).toBe(20);
  });
  it("rejects parameters outside the bounded range", () => {
    expect(() => checkParams({ ...params("A0"), n: 5000 })).toThrow(RangeError);
    expect(() => checkParams({ ...params("A0"), noise: 2 })).toThrow(RangeError);
    expect(() => checkParams({ ...params("A0"), n: 40.5 })).toThrow(RangeError);
    expect(() => checkParams(params("A0"))).not.toThrow();
  });
});
