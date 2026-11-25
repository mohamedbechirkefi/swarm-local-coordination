// SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects an unknown experiment kind", () => {
    const r = good();
    r.experiments[0].kind = "confirmed";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a missing per-cell table", () => {
    const r = good();
    delete r.per_cell;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a per-cell polarization outside [0, 1]", () => {
    const r = good();
    r.per_cell[0].arms.A1.phi_pre = 1.2;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a per-cell interval with reversed bounds", () => {
    const r = good();
    r.per_cell[0].a1_a0.ci_low = 0.5;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a missing post hoc label", () => {
    const r = good();
    delete r.post_hoc.label;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects design windows that do not fit", () => {
    const r = good();
    r.design.pre_window = 0;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("keeps EXP-004 as registered with no estimates", () => {
    const e = validateResults(good()).experiments.find((x) => x.id === "EXP-004");
    expect(e?.kind).toBe("registered");
    expect(e?.estimates.length).toBe(0);
  });
});
