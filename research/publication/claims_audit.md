<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Claims audit

Status at M4 (2026-11-25): `research/claims_register.csv` holds 14 result claims (CL-001 to CL-014) and 8 external-source rows (EXT-001 to EXT-008). The audit record is `research/publication/evidence_audit.md`; the per-number trace is `research/publication/number_audit.json`; the artifact map is `research/publication/artifact_manifest.json`; the challenge pass is `research/publication/review_pass_2.md`.

Checklist, per claim:

- [x] Claim has a row in `research/claims_register.csv` with its type (confirmatory, descriptive, exploratory, verification, disclosure, external).
- [x] Numerical claim maps to experiment ID, run IDs, result path, figure or table and config/protocol hash (claims register columns and artifact manifest).
- [x] External claim maps to a source actually opened, with the level read (abstract or record); one claim beyond the read level was removed (audit F1).
- [x] Number re-derived from or traced to raw outputs; denominators, units, precision, uncertainty and sample counts checked (audit sections 2 and 3).
- [x] Scope stated; no biological-fidelity or universal-guarantee wording.
- [x] Second pass challenged the preferred hypothesis (`review_pass_2.md`).
- [ ] Owner review of claims and limitations (M6, `author_review.md`).

Strength and scope of evidence per conclusion:

| conclusion | strength | scope |
| --- | --- | --- |
| A1 (w_c 0.5) is less polarized than A0 after the shock (CL-001) | confirmatory, frozen rule, narrow CI | simulated model, 18 tested cells, equal weights |
| The same gap exists before the shock (CL-002) | descriptive, narrow CI | same |
| The gap survives topology, cohesion weight and boundary changes (CL-005) | confirmatory sensitivity | 4 cells, r = 1 |
| No difference in change from pre- to post-shock level (CL-007) | exploratory, post hoc | same; cannot show equal recovery |
| A1 more resilient (CL-008) | not supported (floor effect) | |
