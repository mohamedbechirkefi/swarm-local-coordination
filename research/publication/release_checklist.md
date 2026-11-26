<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Release checklist

Status at M0: not releasable. Publication is owner-controlled; nothing is pushed or published without explicit approval.

Status on 2026-11-25 (M6): release candidate prepared, awaiting owner review and G-PUBLIC. Items 1 to 7 were verified in the M6 session with the evidence given; the two owner items are open. Nothing has been tagged or released.

Correction on 2026-11-26 (owner, 2026-11-26, decision sheet, A1): the repository was pushed on 2026-11-25 and is public at https://github.com/mohamedbechirkefi/swarm-local-coordination, with everything committed in it. The demo address is https://swarm-local-coordination.kefimohamedbechir.workers.dev (Cloudflare Workers static assets, free plan, deployed by the coordinator). No tag, release, DOI or preprint exists.

- [x] Every experiment that has run has a truthful standalone report (including failed, null and exploratory). Evidence: `research/experiments/EXP-001/report.md` (exploratory), `EXP-002/report.md` and `EXP-003/report.md` (confirmatory), each compiled to PDF and inspected in M6. EXP-004 is registered, not frozen and not run, so it has a protocol and no report; the registry and the demo say so.
- [x] Integrated manuscript complete; PDFs generated and visually inspected. Evidence: `.venv/bin/python scripts/build_pdfs.py` -> 5 PDFs (manuscript 15 pages, supplementary 4, EXP-001 4, EXP-002 11, EXP-003 8); all 15 manuscript pages and the first and figure pages of each report rendered and read; seven layout faults fixed in the builder (`reproducibility_report.md` section 5).
- [x] Claims audit complete; artifact manifest complete. Evidence: `experiments/audit_numbers.py` -> 770 tokens, 0 unmatched; artifact manifest 22 paths present and 16 path-and-hash pairs equal; references checked against free full texts for 7 of 8 sources (`evidence_audit.md` section 7). The owner's own review of claims remains open in `author_review.md`.
- [x] Reproducibility report complete from a clean clone. Evidence: `reproducibility_report.md` sections 1 to 4 (143 passed; smoke 165 fields, 0 mismatches; 22 vitest tests; A11Y-CHECK PASS; export leaves `git status` empty).
- [x] README experiment table and status current. Evidence: `README.md` table (EXP-001 to EXP-004) checked against `research/experiment_registry.csv`; status line updated to M6 in this session.
- [x] Demo, paper, reports and articles use identical verified numbers and labels. Evidence: `tests/test_demo_export.py` (6 tests: export byte-equal, display strings in the manuscript, README, articles and `demo/README.md` decimals traced) passes in the full suite.
- [x] No e-mail address or secret in committed files. Evidence: scan of 274 tracked and new text files: 0 e-mail addresses, 0 tokens or keys, 0 private key headers, 0 `.env` files; home-directory paths removed from current public files, kept in `CLAUDE.md` and in two append-only journals for the owner's decision (`reproducibility_report.md` section 7); on 2026-11-26 (B9) they were removed from `CLAUDE.md` as well, and the two append-only journal lines remain (`reproducibility_report.md` section 9). The author's name is present by the owner's decision C3.
- [ ] Owner sign-off of `author_review.md` (owner only).
- [ ] Owner approval to publish recorded in `research/decision_log.md` (owner only, G-PUBLIC).

## Version at release (B8)

Owner, 2026-11-26, decision sheet, B8: the release candidate keeps version `0.1.0-rc1` in `CITATION.cff` and no `date-released`. At the release step the version becomes `0.1.0` and `date-released` is set to the release day. `pyproject.toml` stays at `0.0.0`, because changing it would change the lockfile and the recorded environments.

## Release notes (draft)

- External build and check tools are used but not redistributed by this repository: pandoc (GPL-2.0-or-later) converts Markdown for the PDFs, Google Chrome runs the demo accessibility check, and the MPL-2.0 package `lightningcss` is used by Vite at build time (`hypothesis`, also MPL-2.0, in development only), as listed in `research/publication/dependency_licences.md`.
- No figure of this repository is in the decision sheet's list of figures with small or clipped labels (B11), so no figure note is needed.
- Source-level labels (sources read in full, passage-checked or at abstract level, as stated in the manuscript and in `evidence_audit.md` section 7) are accepted by the owner (B14).
