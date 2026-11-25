// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
// Sandbox simulation in a Web Worker: the browser port of the engine's update rules
// (engine.ts), bounded in agents, steps per request and total steps.
import {
  applyShock, checkParams, drawNoise, drawShock, initialState, makeStreams, step,
  type Params, type State, type StepRecord,
} from "./engine";

export const MAX_TOTAL_STEPS = 20_000;
export const MAX_STEPS_PER_REQUEST = 500;

export type WorkerRequest =
  | { type: "reset"; params: Params; seed: number }
  | { type: "advance"; steps: number }
  | { type: "disturb"; fraction: number };

export type WorkerReply =
  | {
      type: "frame";
      t: number;
      box: number;
      x: Float32Array;
      theta: Float32Array;
      records: StepRecord[];
      shock: { t: number; agents: number } | null;
      limitReached: boolean;
      reset: boolean;
    }
  | { type: "error"; message: string };

let params: Params | null = null;
let state: State | null = null;
let streams: ReturnType<typeof makeStreams> | null = null;

function frame(records: StepRecord[], shock: { t: number; agents: number } | null, reset = false): WorkerReply {
  const s = state!;
  return {
    type: "frame", t: s.t, box: s.box, x: Float32Array.from(s.x), theta: Float32Array.from(s.theta),
    records, shock, limitReached: s.t >= MAX_TOTAL_STEPS, reset,
  };
}

onmessage = (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  try {
    if (m.type === "reset") {
      checkParams(m.params);
      if (!Number.isInteger(m.seed) || m.seed < 0 || m.seed > 1_000_000) throw new RangeError("seed must be an integer from 0 to 1000000");
      params = m.params;
      streams = makeStreams(m.seed);
      state = initialState(params, streams.init);
      postMessage(frame([], null, true));
      return;
    }
    if (!params || !state || !streams) throw new Error("sandbox not initialised");
    if (m.type === "disturb") {
      if (!(m.fraction >= 0 && m.fraction <= 1)) throw new RangeError("disturbance fraction must be in [0, 1]");
      const sh = drawShock(params.n, m.fraction, streams.disturb);
      applyShock(state, sh.agents, sh.headings);
      postMessage(frame([], { t: state.t, agents: sh.agents.length }));
      return;
    }
    const n = Math.max(0, Math.min(MAX_STEPS_PER_REQUEST, Math.floor(m.steps), MAX_TOTAL_STEPS - state.t));
    const records: StepRecord[] = [];
    for (let k = 0; k < n; k++) records.push(step(params, state, drawNoise(params.n, params.noise, streams.noise)));
    postMessage(frame(records, null));
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
