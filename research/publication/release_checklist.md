<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Release checklist

Status at M0: not releasable. Publication is owner-controlled; nothing is pushed or published without explicit approval.

Status on 2026-11-25 (M6): release candidate prepared, awaiting owner review and G-PUBLIC. Items 1 to 7 were verified in the M6 session with the evidence given; the two owner items are open. Nothing has been pushed, tagged or released.

- [x] Every experiment that has run has a truthful standalone report (including failed, null and exploratory). Evidence: `research/experiments/EXP-001/report.md` (exploratory), `EXP-002/report.md` and `EXP-003/report.md` (confirmatory), each compiled to PDF and inspected in M6. EXP-004 is registered, not frozen and not run, so it has a protocol and no report; the registry and the demo say so.
- [x] Integrated manuscript complete; PDFs generated and visually inspected. Evidence: `.venv/bin/python scripts/build_pdfs.py` -> 5 PDFs (manuscript 15 pages, supplementary 4, EXP-001 4, EXP-002 11, EXP-003 8); all 15 manuscript pages and the first and figure pages of each report rendered and read; seven layout faults fixed in the builder (`reproducibility_report.md` section 5).
- [x] Claims audit complete; artifact manifest complete. Evidence: `experiments/audit_numbers.py` -> 770 tokens, 0 unmatched; artifact manifest 22 paths present and 16 path-and-hash pairs equal; references checked against free full texts for 7 of 8 sources (`evidence_audit.md` section 7). The owner's own review of claims remains open in `author_review.md`.
- [x] Reproducibility report complete from a clean clone. Evidence: `reproducibility_report.md` sections 1 to 4 (143 passed; smoke 165 fields, 0 mismatches; 22 vitest tests; A11Y-CHECK PASS; export leaves `git status` empty).
- [x] README experiment table and status current. Evidence: `README.md` table (EXP-001 to EXP-004) checked against `research/experiment_registry.csv`; status line updated to M6 in this session.
- [x] Demo, paper, reports and articles use identical verified numbers and labels. Evidence: `tests/test_demo_export.py` (6 tests: export byte-equal, display strings in the manuscript, README, articles and `demo/README.md` decimals traced) passes in the full suite.
- [x] No e-mail address or secret in committed files. Evidence: scan of 274 tracked and new text files: 0 e-mail addresses, 0 tokens or keys, 0 private key headers, 0 `.env` files; home-directory paths removed from current public files, kept in `CLAUDE.md` and in two append-only journals for the owner's decision (`reproducibility_report.md` section 7). The author's name is present by the owner's decision C3.
- [ ] Owner sign-off of `author_review.md` (owner only).
- [ ] Owner approval to publish recorded in `research/decision_log.md` (owner only, G-PUBLIC).
