<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Evidence audit (M4, master prompt 11.5)

Date: 2026-11-25. Performed by the AI research assistant as internal quality control; not external review. Scope: `research/paper/manuscript.md`, `research/paper/supplementary.md`, the three experiment reports, `research/claims_register.csv`, `research/limitations.md`, `research/publication/m4_interpretation.md` and `research/publication/review_pass_2.md`.

## 1. Tools and outputs

| step | command | output |
| --- | --- | --- |
| Raw integrity | `.venv/bin/python experiments/exploratory_m4.py` | `results/exploratory/M4-sensitivity/analysis.json` (`raw_integrity`): 1,584 files listed in the four confirmatory `raw_manifest.json` files, 0 mismatched or missing |
| Per-number trace | `.venv/bin/python experiments/audit_numbers.py` | `research/publication/number_audit.json`: 770 distinct decimal tokens (counted per document) across 10 documents, including this audit, 0 unmatched |
| Artifact manifest | `.venv/bin/python experiments/build_artifact_manifest.py` | `research/publication/artifact_manifest.json`: 11 artifacts (3 manuscript tables, 3 figures, 2 supplementary table groups, 3 number groups); every CL claim maps to at least one artifact |

**How the per-number trace works, and its limit.** Every decimal number printed in the audited documents is searched for among the numeric values of the committed result files (analysis outputs, per-cell tables, execution and launch records, the freeze record, the frozen configurations and the exploratory summaries), at the printed precision, allowing a dropped sign. Values quoted from the protocol text (for example the pre-freeze diagnostic 0.251) are matched against `research/protocol.md`. A match shows that the number exists in a committed output; it does not by itself show that it was attributed to the right quantity, because short numbers such as 0.063 occur in several files. The attribution of every number in the manuscript's abstract, tables and claims was therefore also checked by hand against the specific JSON key named in the artifact manifest (section 3). Integers (design parameters, counts, identifiers) are not traced automatically; the counts were checked by hand (section 2).

## 2. Denominators, units, precision, uncertainty and sample counts

| check | source | result |
| --- | --- | --- |
| EXP-002 runs by arm, failure rate | `analysis.json` `failures` | 360 per arm, failure rate 0 in every arm; 1080 rows in `provenance.csv` |
| Primary pairs and cells | `analysis.json` `primary` | n_pairs 360, n_cells 18; every per-cell contrast has 20 pairs and every arm 20 ok runs per cell |
| Flagged cells | `per_cell[*].a0_not_orderable_flag` | 10 flagged, 8 orderable, as stated |
| Restricted reference | `primary_restricted_to_exp003_cells` | 80 pairs (4 cells x 20) |
| EXP-003 runs and pairs | `EXP-003-analysis/analysis.json` | 160 runs per condition directory; Delta_S over 80 pairs in S1, S2a, S2b, S3; S2a and S2b share the one S2 directory (160 runs, 80 per weight), as the report states |
| Metric recomputation | `metric_check` | EXP-002 1080 checked, 0 mismatches; each EXP-003 condition 160 checked, 0 mismatches |
| S4 censoring | `S4.rows` | maximum 3 censored runs of 20 in any arm, cell and threshold |
| Bootstrap settings | `analysis.json` `primary` | 10,000 resamples, seed 20261124, level 0.95, as in the protocol and manuscript |
| Units | per-cell CSV | wall-clock is stored in seconds per step and printed in milliseconds per step in the EXP-002 report; the audit applies the x1000 conversion and all 54 values match |
| Precision | all documents | contrasts printed to 3 decimals, consistent across abstract, tables, reports and claims; elapsed times to 0.1 s |
| Uncertainty wording | manuscript Section 4.3 | CIs are stratified bootstrap percentile intervals over seeds; per-cell intervals descriptive; the M4 revision adds that the pooled CI is conditional on the 18 cells and equal weights |
| Elapsed time and load | `execution.json`, `launch.json` | 1138.7, 594.7, 181.9, 293.9 s; the 38.7 figure is the 15-minute load average at the S1 launch (manuscript wording made precise in M4) |

## 3. Hand trace of headline numbers

| number in manuscript | file and key |
| --- | --- |
| Delta -0.307 [-0.313, -0.302] | `results/confirmatory/EXP-002/analysis/analysis.json` `primary.estimate`, `ci_low`, `ci_high` |
| phi_pre gap -0.312 [-0.319, -0.304] | same file, `secondary_pooled.phi_pre.A1-A0` |
| A1 phi_pre 0.097 to 0.229 | same file, `per_cell[*].A1_phi_pre_mean` (min row 4, max row 12) |
| Per-cell range -0.810 to +0.037; -0.406 to -0.810 in orderable cells | `per_cell[*].A1-A0_mean` |
| A2 - A0 0.374 [0.369, 0.379]; A2 - A1 0.681 [0.679, 0.684] | `reference_contrasts` |
| Cohesion 0.080 [0.065, 0.094]; collisions -2.951 [-3.027, -2.874]; A2 rows | `secondary_pooled` |
| A0 tau 1.0 to 10.5 in orderable cells | `per_cell[*].A0_tau_median` over unflagged rows |
| Distance evaluations 8087, 3562, 2203 | `per_cell.csv` row rho 2, eta 0.1, r 1, `A*_dist_evals_per_step` (rounded) |
| Table 2 values and verdicts | `results/confirmatory/EXP-003-analysis/analysis.json` `conditions.*.delta_s`, `verdict_primary`, `verdict_secondary`, `reference_*` |
| S1 and S3 phi_pre gaps -0.438, -0.434 | `conditions.S1/S3.phi_pre_A1_minus_A0` |
| Table 3 (X1 to X5) | `results/exploratory/M4-sensitivity/analysis.json` `results.*` |
| Draft smoke -0.480, SD 0.059 | `research/protocol_freeze.json` `c4_disclosure.values.paired_difference_A1_minus_A0` |
| Draft A1 phi_pre 0.057 to 0.071 | `results/exploratory/EXP-001-summary.json` `burnin_scan` (A1 column) |
| Random level 0.063 and 0.071 | `results.X4_random_level_b`; the EXP-001 summary text (1/sqrt(200)) |

## 4. External claims

All eight references were checked for bibliographic metadata against Crossref on 2026-11-24 (`research/literature_review.md`). None was read in full. The manuscript reference list now marks the level read for each entry, and the claims register has one row per external source (EXT-001 to EXT-008).

| source | level read | use in the manuscript |
| --- | --- | --- |
| Vicsek et al. 1995 | abstract | definition of A0 and the ordering transition |
| Couzin et al. 2002 | repository record and abstract | zonal rule; zone sizes shift the collective state (qualitative comparison only) |
| Reynolds 1987 | author's page and metadata | origin of separation, alignment and cohesion rules |
| Jadbabaie, Lin and Morse 2003 | **metadata record only** | topic only (see finding F1) |
| Olfati-Saber 2006 | technical-report record and abstract | flocking with alignment, separation and cohesion; "flocks need no leaders" |
| Cucker and Smale 2007 | record and abstract | convergence related to distance-decaying coupling |
| Ballerini et al. 2008 | abstract | topological interaction (motivation for S1) |
| Vicsek and Zafeiris 2012 | abstract | review of models and order parameters |

## 5. Findings and fixes

| id | finding | severity | fix |
| --- | --- | --- | --- |
| F1 | The first M4 manuscript draft and the EXP-002 report (section 3) said that Jadbabaie, Lin and Morse (2003) show convergence under connectivity conditions. Only the bibliographic record of that paper was accessed, so no read source supports the statement about its results. | medium (external claim without a read source) | Manuscript sections 2 and 6 rewritten to cite the paper for its topic only; EXP-002 report section 3 corrected with a dated note; EXT-004 marked "metadata only"; `research/literature_review.md` annotated. The same wording remains in the frozen EXP-002 protocol (section 2), which is not edited; it is background, not a tested claim. |
| F2 | The manuscript said the load average was "up to 38.7" at launch; 38.7 is the 15-minute average at the S1 launch, while the 1-minute values at the four launches were 16.3, 6.5, 3.3 and 3.5. | low (imprecise) | Wording made precise. |
| F3 | The first draft described the order gap as "stationary". No check of A1's steady state exists. | medium (unsupported qualifier) | Replaced by "sustained" or "pre-shock"; limitation 18 (found by the second review pass). |
| F4 | `data/manifest.json` still says the simulator is "not yet implemented (M2)". Its SHA-256 (94fe5a7b...) is recorded in every confirmatory run's provenance, so editing it would break the recorded link. | low (stale text, no number) | Not edited. Recorded here and in limitations for the owner's decision (option: add a separate dated note file rather than edit the hashed file). |
| F5 | The claims register lacked result IDs, config hashes, figure or table and section columns, and had no rows for external sources, exploratory checks, resources or the pre-freeze disclosure. | medium (register incomplete) | Register rebuilt with those columns: CL-001 to CL-014 and EXT-001 to EXT-008; CL-001 and CL-005 qualified (order gap, not recovery). |
| F6 | The M0 artifact manifest was empty. | medium | Built by `experiments/build_artifact_manifest.py`; every CL claim maps to an artifact. |
| F7 | Number trace: 0 unmatched decimal tokens after accounting for section numbers, DOIs, the 1.96 figure constant and the millisecond conversion. No numerical mismatch between documents and committed outputs was found. | none | none |
| F8 | No failed, aborted or repeated confirmatory attempt was found: one launch per directory in `run.log`, provenance rows equal planned runs. | none | none |

## 6. Gate check (M4)

- Every numerical claim in the manuscript maps to a result file and key, a config or protocol hash and a figure or table (artifact manifest, claims register, number audit). Claims with no figure or table (CL-009, CL-010, CL-013, CL-014) map to a result file and section.
- Every external claim maps to a source that was actually accessed, with the level read stated; the one claim that exceeded the read level (F1) was removed.
- Contradictory, null and exploratory results are in the manuscript (Sections 5.2 to 5.4 and 7).
