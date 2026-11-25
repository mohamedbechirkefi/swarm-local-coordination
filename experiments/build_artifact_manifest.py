# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Build research/publication/artifact_manifest.json (master prompt 11.5).

Maps every quantitative table, figure and claim of the manuscript to its experiment ID,
run IDs, metric definition, result path and key, generator script, config and protocol
hashes and code revision, and records the SHA-256 of each result file at build time.
Per-number tracing of the publication texts is in research/publication/number_audit.json
(experiments/audit_numbers.py).

  .venv/bin/python experiments/build_artifact_manifest.py
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = "075cf7c5f571c03ede9b8d551c3ba43766172a39"


def sha(rel: str) -> str | None:
    p = ROOT / rel
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def main() -> int:
    freeze = json.loads((ROOT / "research" / "protocol_freeze.json").read_text(encoding="utf-8"))
    cfg = {c["path"]: c["canonical_sha256"] for c in freeze["configs"]}
    proto = {p["path"]: p["sha256"] for p in freeze["protocols"]}
    p_main = proto["research/protocol.md"]
    exp2 = {"experiment_id": "EXP-002", "label": "confirmatory",
            "run_ids": "EXP-002_<arm>_density<rho>_noise<eta>_radius<r>_s<seed>, 1080 runs, listed in "
                       "results/confirmatory/EXP-002/provenance.csv",
            "config_hash": cfg["experiments/EXP-002/config.json"],
            "protocol_hash": {"research/protocol.md": p_main,
                              "research/experiments/EXP-002/protocol.md": proto["research/experiments/EXP-002/protocol.md"]},
            "code_revision": REV, "generator": "experiments/analyse_confirmatory.py exp002"}
    exp3 = {"experiment_id": "EXP-003", "label": "confirmatory",
            "run_ids": "EXP-003 run IDs in results/confirmatory/EXP-003-S{1,2,3}/provenance.csv (480 runs); "
                       "S2 controls are EXP-002 A0 runs",
            "config_hash": {k: v for k, v in cfg.items() if "EXP-003" in k},
            "protocol_hash": {"research/protocol.md": p_main,
                              "research/experiments/EXP-003/protocol.md": proto["research/experiments/EXP-003/protocol.md"]},
            "code_revision": REV + " (454 runs flagged git_dirty by a journal edit; DL-013)",
            "generator": "experiments/analyse_confirmatory.py exp003"}
    expl = {"experiment_id": "EXP-002, EXP-003 (re-analysis)", "label": "exploratory (post hoc, M4)",
            "run_ids": "all EXP-002 and EXP-003 runs (no new runs)", "config_hash": "none (re-analysis)",
            "protocol_hash": "none (not preregistered)", "code_revision": "M4 commit (script added in M4)",
            "generator": "experiments/exploratory_m4.py"}
    phi = "phi(t) = |mean_i exp(i theta_i(t))|; phi_post mean over [3000, 3500); phi_pre mean over [2900, 3000)"
    boot = "stratified percentile bootstrap over seeds within cells, 10,000 resamples, seed 20261124, 95% CI"
    A2 = "results/confirmatory/EXP-002/analysis/analysis.json"
    A3 = "results/confirmatory/EXP-003-analysis/analysis.json"
    AX = "results/exploratory/M4-sensitivity/analysis.json"
    items = [
        {"id": "TAB-MS-1", "what": "Manuscript Table 1, pooled EXP-002 contrasts", **exp2,
         "metric": f"{phi}; cohesion = largest-component fraction (post window); collisions per agent per 100 steps; {boot}",
         "result_path": A2, "keys": ["primary", "secondary_pooled", "reference_contrasts"],
         "claims": ["CL-001", "CL-002", "CL-003", "CL-004"]},
        {"id": "FIG-EXP002-01", "what": "Manuscript Figure 1, per-cell forest plot", **exp2, "metric": f"phi_post A1 - A0; {boot}",
         "result_path": "results/confirmatory/EXP-002/analysis/fig_exp002_01_forest.png", "keys": ["per_cell"],
         "claims": ["CL-001"]},
        {"id": "FIG-EXP002-02", "what": "Manuscript Figure 2, phi(t) around the shock", **exp2,
         "metric": "mean phi(t) across 20 seeds per arm, +/- 1.96 SE", "keys": [],
         "result_path": "results/confirmatory/EXP-002/analysis/fig_exp002_02_timeseries.png", "claims": ["CL-002"]},
        {"id": "TAB-S2-S3", "what": "Supplementary Tables S2 and S3 (per-cell EXP-002)", **exp2,
         "metric": f"{phi}; tau first step with phi >= 0.9 phi_pre for 10 steps, censored at 500; distance evaluations per step",
         "result_path": "results/confirmatory/EXP-002/analysis/per_cell.csv", "keys": ["all columns"],
         "claims": ["CL-002", "CL-006", "CL-011"]},
        {"id": "TAB-MS-2", "what": "Manuscript Table 2, EXP-003 Delta_S and verdicts", **exp3,
         "metric": f"phi_post A1 - A0 on 4 reduced cells; {boot}; invalidation rule EXP-003 protocol section 4",
         "result_path": A3, "keys": ["conditions.*.delta_s", "conditions.*.verdict_primary",
                                     "conditions.*.verdict_secondary", "conditions.*.phi_pre_A1_minus_A0",
                                     "reference_primary", "reference_restricted"],
         "claims": ["CL-005"]},
        {"id": "FIG-EXP003-01", "what": "Manuscript Figure 3, sensitivity intervals", **exp3, "metric": f"Delta_S; {boot}",
         "result_path": "results/confirmatory/EXP-003-analysis/fig_exp003_01_sensitivity.png", "keys": [],
         "claims": ["CL-005"]},
        {"id": "TAB-S4", "what": "Supplementary Table S4 (EXP-003 per cell and S4 thresholds)", **exp3,
         "metric": "per-cell mean A1 - A0; tau at 0.8, 0.9, 0.95 x phi_pre", "result_path": A3,
         "keys": ["conditions.*.per_cell", "S4.rows"], "claims": ["CL-006"]},
        {"id": "TAB-MS-3", "what": "Manuscript Table 3, exploratory checks X1 to X5", **expl,
         "metric": f"X1 change score phi_post - phi_pre; X2 subsets; X3 matched cells; X4 drop over [t_d, t_d + 50); {boot}",
         "result_path": AX, "keys": ["results.X1_*", "results.X2_*", "results.X3_*", "results.X4_*",
                                     "results.X5_exp003_change_score"],
         "claims": ["CL-007", "CL-008", "CL-012"]},
        {"id": "NUM-INTEGRITY", "what": "Raw-file re-hash (Section 4.5)", **expl, "metric": "SHA-256 against raw_manifest.json",
         "result_path": AX, "keys": ["raw_integrity"], "claims": ["CL-014"]},
        {"id": "NUM-EXEC", "what": "Wall-clock and load (Section 4.5)", **exp2, "metric": "elapsed seconds; load average",
         "result_path": "results/confirmatory/EXP-002/execution.json; results/confirmatory/EXP-003-S*/execution.json; launch.json",
         "keys": ["elapsed_s", "load_average"], "claims": ["CL-010"]},
        {"id": "NUM-EXP001", "what": "EXP-001 verification and planning values (Sections 4.1, 4.4, 5.1)",
         "experiment_id": "EXP-001", "label": "exploratory", "run_ids": "results/exploratory/EXP-001-*/ (journal EXPL-001 to EXPL-008)",
         "config_hash": "experiments/EXP-001/*.json (not frozen)", "protocol_hash": "none (exploratory)",
         "code_revision": "99cc0c4, 2330f79, 075cf7c", "generator": "experiments/EXP-001/summarise_exploratory.py; experiments/EXP-001/apply_burnin_rule.py",
         "metric": "phi_pre, seed spread SD, benchmark mismatches", "keys": ["seed_spread_smoke_phi_post", "burnin_scan"],
         "result_path": "results/exploratory/EXP-001-summary.json; results/exploratory/EXP-001-burnin-rule-decision.json; research/protocol_freeze.json (c4_disclosure)",
         "claims": ["CL-009", "CL-013"]},
    ]
    for it in items:
        it["result_sha256"] = {p.strip(): sha(p.strip()) for p in it["result_path"].split(";") if "*" not in p and sha(p.strip())}
    with open(ROOT / "research" / "claims_register.csv", newline="", encoding="utf-8") as fh:
        claims = [r["claim_id"] for r in csv.DictReader(fh)]
    mapped = {c for it in items for c in it["claims"]}
    out = {"schema_version": "1.0", "updated": "2026-11-25",
           "note": "Maps every quantitative table, figure and claim to experiment, runs, metric, result path, generator, "
                   "config and protocol hash and code revision. Per-number trace: research/publication/number_audit.json.",
           "artifacts": items,
           "claims_without_artifact": [c for c in claims if c not in mapped and not c.startswith("EXT")],
           "external_claims": "EXT-001 to EXT-008 map to sources in research/literature_review.md; the level consulted for each (M6: full text for seven, abstract for Couzin et al. 2002) is in research/claims_register.csv and research/publication/evidence_audit.md section 7"}
    (ROOT / "research" / "publication" / "artifact_manifest.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"{len(items)} artifacts; claims without artifact: {out['claims_without_artifact']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
