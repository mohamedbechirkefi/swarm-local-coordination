<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Claims audit

Status at M0: no claims exist (`research/claims_register.csv` has a header only).

Checklist, per claim, before any release:

- [ ] Claim has a row in `research/claims_register.csv` with type observed, inferred, simulated or external.
- [ ] Numerical claim maps to experiment ID, run IDs, result path, figure ID and config/protocol hash.
- [ ] External claim maps to a source actually opened (URL or DOI, access date).
- [ ] Number re-derived from raw outputs; denominators, units, precision, uncertainty and sample counts checked.
- [ ] Scope stated; no biological-fidelity or universal-guarantee wording.
- [ ] Second pass challenged the preferred hypothesis.
