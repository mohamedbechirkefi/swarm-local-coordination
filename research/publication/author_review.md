<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Author review (owner)

To be completed by the owner before any release. The AI assistant is a disclosed research and development assistant, not an author.

- [ ] Authorship and metadata approved (no affiliation unless the owner adds one). Recorded owner decision C3, 2026-11-24: "Mohamed Bechir Kefi", no affiliation; the AI is disclosed as a research and development assistant, not an author (DL-010). Box left for the owner to tick (an agent had ticked it; unticked in M5, DL-017).
- [ ] Protocols frozen by the owner, hashes recorded.
- [ ] Claims and limitations reviewed.
- [ ] AI-assistance disclosure reviewed for accuracy.
- [ ] Licence wording reviewed (source-available, not open source).
- [ ] Publication approved, with venue eligibility and fees checked (paid venues out of scope).

State on 2026-11-25 (M5): the owner approved the manuscript title and the funding, competing-interest and AI-use wording ("Approve all", post-M4; DL-016). The owner has not yet reviewed the full manuscript text; that review belongs to M6. Only the owner ticks these boxes.

## Prepared for the owner (M6, 2026-11-25)

No box above was ticked by an agent at the start of M6 (checked: 0 ticked boxes); none was ticked in M6. The authorship box had been ticked by an earlier agent session and was unticked in M5 (DL-017). Only the owner ticks these boxes.

What to read for each box:

1. **Authorship and metadata.** `research/paper/manuscript.md` front matter (title, author line) and section "Funding, competing interests and AI assistance"; `CITATION.cff` (title, author, version `0.1.0-rc1`, no `date-released`); `README.md` section "Citation"; the PDF metadata of `research/paper/manuscript.pdf` (title and author only).
2. **Protocols frozen by the owner, hashes recorded.** `research/protocol_freeze.json`; `research/protocol.md` section 13 (amendments AM-1 to AM-4); `research/paper/supplementary.md` section S3 (hashes). EXP-004 is registered and not frozen: `research/experiments/EXP-004/protocol.md` section 21.
3. **Claims and limitations.** `research/paper/manuscript.pdf` in full (15 pages; Sections 5 to 7 carry the claims); `research/claims_register.csv` (CL-001 to CL-014, EXT-001 to EXT-008); `research/limitations.md`; `research/publication/evidence_audit.md` sections 5 and 7 (findings, and the M6 reference check with the level read for each source); `research/publication/review_pass_2.md`.
4. **AI-assistance disclosure.** Manuscript section "Funding, competing interests and AI assistance"; `research/experiments/EXP-00N/report.md` section 1 ("Author"); `articles/medium.md` and `articles/linkedin.md`.
5. **Licence wording.** `README.md` section "Licence", `CITATION.cff` header comments, manuscript Section 8; the licence files themselves are unchanged. Dependency licences: `research/publication/dependency_licences.md` (one flag for information: pandoc, a GPL build tool used as an external program).
6. **Publication.** `research/publication/release_checklist.md` and `research/publication/reproducibility_report.md`; nothing was tagged or released. (Corrected 2026-11-26: the repository was pushed on 2026-11-25 and is public at https://github.com/mohamedbechirkefi/swarm-local-coordination; owner, 2026-11-26, decision sheet, A1.)

Open decisions for this repository, each the owner's:

- Whether to approve publication of anything at all (push, release, tag, licence change or any publication; G-PUBLIC, owner-approvals-2026-11-25e).
- Whether and when to freeze EXP-004, after deciding its eight open parameters in `research/experiments/EXP-004/protocol.md` section 21 (G-FREEZE; DL-016).
- The repository and demo URL, which appear as placeholders in the files listed below.
- Confirmation that no funding was received and that there are no competing interests (the wording is approved; the facts are the owner's to confirm).
- The author line and the affiliation (recorded decision C3: "Mohamed Bechir Kefi", no affiliation), to be confirmed by ticking box 1.
- Whether the repository title in `CITATION.cff` and `README.md` should differ from the approved manuscript title; M6 made the CFF title quote the approved manuscript title in full and set no other title.
- The version label: M6 set `0.1.0-rc1` in `CITATION.cff`; the release version and `date-released` are added at the owner's publication step.
- Whether `CLAUDE.md` (agent operating instructions, which name local workspace paths) and the session journals (`progress.md`, `research/experiment_journal.jsonl`, which keep one local path each) are published as they are.
- Whether the committed PDFs and `manuscript.tex` are part of a release; M6 committed them because no `.gitignore` rule or decision excludes them.

Owner placeholders at the M6 commit (all filled on 2026-11-26, see the section below; none remains):

- `CITATION.cff` line 8: "Repository URL: [to be added by the owner on release]".
- `README.md` line 57: "Repository and demo URL: [to be added by the owner on release]".
- `README.md` line 75 and `research/paper/manuscript.md` line 223 (`manuscript.tex` line 816): funding and competing interests "both to be confirmed by the author".
- `research/paper/manuscript.md` line 219 (`manuscript.tex` line 801): repository URL "[to be added by the owner on release]".
- `articles/linkedin.md` lines 14 and 15: repository and demo links.
- `articles/medium.md` line 61: repository and demo links.
- `demo/README.md` line 21 and `demo/src/App.tsx` line 62: repository and demo URL.

## Owner answers recorded (2026-11-26)

Source: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md` and `labs/_shared/owner-approvals-2026-11-26.md`, outside this repository). Applied as DL-019. No box above was ticked; only the owner ticks them.

Answers that concern this repository:

- **A1.** The repository is public since 2026-11-25; the out-of-date "no remote / nothing pushed" sentences in this file, `release_checklist.md`, `reproducibility_report.md` and `README.md` are corrected. Append-only records (`progress.md`, `research/decision_log.md`, `research/experiment_journal.jsonl`) are not edited.
- **B1.** Repository URL: https://github.com/mohamedbechirkefi/swarm-local-coordination (`CITATION.cff` `repository-code`, README, manuscript, articles, demo README and footer).
- **B2.** Demo URL: https://swarm-local-coordination.kefimohamedbechir.workers.dev, Cloudflare Workers static assets on the free plan (`demo/wrangler.jsonc`, assets only, directory `./dist`), deployed by the coordinator.
- **B3.** Author line "Mohamed Bechir Kefi, independent researcher" (manuscript front matter with affiliation "Independent researcher", manuscript statement, experiment reports, `CITATION.cff` `affiliation`, README, articles, demo README and footer). This supersedes the earlier "no affiliation" record C3, which stays in the frozen `research/protocol_freeze.json` unchanged.
- **B4.** "No funding was received." and "The author declares no competing interests." (manuscript and README); the "to be confirmed" marks are removed.
- **B6 and B7.** The manuscript title is owner-approved; `CITATION.cff` `title` now equals the manuscript title (the "SWARM: simulation code and results for" prefix is dropped).
- **B8.** Version `0.1.0-rc1` and no `date-released` kept; at the release, `0.1.0` and the release day (`release_checklist.md`).
- **B9.** Home paths removed from `CLAUDE.md`; two lines remain in append-only journals (`reproducibility_report.md` section 9).
- **B10.** Committed PDFs stay and are attached to a release.
- **B13.** Build-tool licence sentence added to the release notes (draft) in `release_checklist.md`. B11 lists no figure of this repository.
- **B14.** Source-level labels accepted (no text change needed).
- **R-SWARM-1.** EXP-004: registered, not frozen, not run; the owner will freeze later (`roadmap.md`, README).

What remains open (the owner's):

- B15: the article drafts (`articles/medium.md`, `articles/linkedin.md`) and their titles, before any posting.
- B16: the full-text review of the manuscript, then the sign-off of every box above.
- B18: the release (tag, GitHub release with the PDFs attached, optional zero-cost DOI or preprint).
- Freeze: EXP-004, after the owner sets its eight open parameters (G-FREEZE).

Placeholders that remain: none (checked with `git grep` for "to be added", "to be confirmed" and "placeholder" on 2026-11-26).
