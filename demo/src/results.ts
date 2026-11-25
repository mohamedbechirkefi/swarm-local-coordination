// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
}

export type Kind = "exploratory" | "confirmatory" | "registered";
export const KINDS: readonly Kind[] = ["exploratory", "confirmatory", "registered"];

export interface Experiment {
  id: string;
  /** SWARM extension: exploratory, confirmatory, or registered (not run). */
  kind: Kind;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface CellInterval {
  estimate: number;
  ci_low: number;
  ci_high: number;
  display: string;
  interval_display: string;
}

export interface ArmCell {
  phi_pre: number;
  phi_post: number;
  phi_pre_display: string;
  phi_post_display: string;
}

export type ArmId = "A0" | "A1" | "A2";
export const ARMS: readonly ArmId[] = ["A0", "A1", "A2"];

export interface PerCell {
  cell: string;
  density: number;
  noise: number;
  radius: number;
  a0_not_aligned: boolean;
  a1_a0: CellInterval;
  arms: Record<ArmId, ArmCell>;
}

export interface PostHoc {
  id: string;
  label: string;
  claim_ids: string[];
  source: string;
  estimates: Estimate[];
}

export interface Design {
  t_disturb: number;
  pre_window: number;
  window: number;
  sesoi: number;
  primary: Estimate;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  per_cell: PerCell[];
  post_hoc: PostHoc;
  design: Design;
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
  };
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    const kind = str(e, "kind", w) as Kind;
    if (!KINDS.includes(kind)) throw new ResultsError(`${w}.kind: unknown kind ${kind}`);
    return {
      id: str(e, "id", w),
      kind,
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  const perCell = arr(o, "per_cell", "results").map((v, i) => perCellEntry(v, `per_cell[${i}]`));
  if (perCell.length === 0) throw new ResultsError("results.per_cell: empty");
  const ph = obj(o.post_hoc, "post_hoc");
  const postHoc: PostHoc = {
    id: str(ph, "id", "post_hoc"),
    label: str(ph, "label", "post_hoc"),
    claim_ids: strArr(ph, "claim_ids", "post_hoc"),
    source: str(ph, "source", "post_hoc"),
    estimates: arr(ph, "estimates", "post_hoc").map((x, j) => estimate(x, `post_hoc.estimates[${j}]`)),
  };
  if (postHoc.estimates.length === 0) throw new ResultsError("post_hoc.estimates: empty");
  const dz = obj(o.design, "design");
  const design: Design = {
    t_disturb: num(dz, "t_disturb", "design") as number,
    pre_window: num(dz, "pre_window", "design") as number,
    window: num(dz, "window", "design") as number,
    sesoi: num(dz, "sesoi", "design") as number,
    primary: estimate(dz.primary, "design.primary"),
  };
  if (design.pre_window <= 0 || design.window <= 0 || design.t_disturb < design.pre_window) {
    throw new ResultsError("design: windows are not positive or do not fit before t_d");
  }
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    per_cell: perCell,
    post_hoc: postHoc,
    design,
  };
}

function cellInterval(v: unknown, where: string): CellInterval {
  const o = obj(v, where);
  const c: CellInterval = {
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where) as number,
    ci_high: num(o, "ci_high", where) as number,
    display: str(o, "display", where),
    interval_display: str(o, "interval_display", where),
  };
  if (c.ci_low > c.ci_high) throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  return c;
}

function unitInterval(o: Obj, k: string, where: string): number {
  const v = num(o, k, where) as number;
  if (v < 0 || v > 1) throw new ResultsError(`${where}.${k}: polarization outside [0, 1]`);
  return v;
}

function perCellEntry(v: unknown, where: string): PerCell {
  const o = obj(v, where);
  if (typeof o.a0_not_aligned !== "boolean") throw new ResultsError(`${where}.a0_not_aligned: expected a boolean`);
  const armsObj = obj(o.arms, `${where}.arms`);
  const arms = {} as Record<ArmId, ArmCell>;
  for (const a of ARMS) {
    const w = `${where}.arms.${a}`;
    const x = obj(armsObj[a], w);
    arms[a] = {
      phi_pre: unitInterval(x, "phi_pre", w),
      phi_post: unitInterval(x, "phi_post", w),
      phi_pre_display: str(x, "phi_pre_display", w),
      phi_post_display: str(x, "phi_post_display", w),
    };
  }
  return {
    cell: str(o, "cell", where),
    density: num(o, "density", where) as number,
    noise: num(o, "noise", where) as number,
    radius: num(o, "radius", where) as number,
    a0_not_aligned: o.a0_not_aligned,
    a1_a0: cellInterval(o.a1_a0, `${where}.a1_a0`),
    arms,
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
