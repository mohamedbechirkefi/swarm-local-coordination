<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# Literature review (M0, not systematic)

This is a targeted review, not a systematic one: no search protocol, inclusion criteria or screening log was followed. "Opened" means the session fetched the listed page on the access date and read its metadata and abstract (not the full text unless stated). The bibliographic metadata (authors, title, venue, volume, issue, pages, year) of all eight entries was also checked against `api.crossref.org/works/<DOI>` on 2026-11-24.

## 1. Sources opened (access date 2026-11-24)

| Key | Reference | What was opened | Relevance |
| --- | --- | --- | --- |
| vicsek1995 | T. Vicsek, A. Czirok, E. Ben-Jacob, I. Cohen, O. Shochet, "Novel type of phase transition in a system of self-driven particles", Phys. Rev. Lett. 75(6):1226-1229, 1995. DOI 10.1103/PhysRevLett.75.1226 | arXiv abstract page https://arxiv.org/abs/cond-mat/0611743 (journal reference listed there) | Defines the alignment-only baseline (A0) and the polarization order parameter; noise- and density-driven ordering transition |
| couzin2002 | I. D. Couzin, J. Krause, R. James, G. D. Ruxton, N. R. Franks, "Collective memory and spatial sorting in animal groups", J. Theor. Biol. 218(1):1-11, 2002. DOI 10.1006/jtbi.2002.3065 | Repository record https://kops.uni-konstanz.de/handle/123456789/39961 | Zonal repulsion/orientation/attraction rule (basis of A1); small rule changes cause large collective transitions; history dependence |
| reynolds1987 | C. W. Reynolds, "Flocks, herds and schools: A distributed behavioral model", ACM SIGGRAPH Computer Graphics 21(4):25-34, 1987. DOI 10.1145/37402.37406 (Crossref) | Author's page https://www.red3d.com/cwr/boids/ and Crossref record | Separation, alignment and cohesion steering rules |
| jadbabaie2003 | A. Jadbabaie, J. Lin, A. S. Morse, "Coordination of groups of mobile autonomous agents using nearest neighbor rules", IEEE Trans. Autom. Control 48(6):988-1001, 2003. DOI 10.1109/TAC.2003.812781 (Crossref) | Crossref record only (the UPenn repository returned HTTP 403; dblp returned a bot block) | Convergence of Vicsek-type heading consensus under joint connectivity |
| olfatisaber2006 | R. Olfati-Saber, "Flocking for multi-agent dynamic systems: Algorithms and theory", IEEE Trans. Autom. Control 51(3):401-420, 2006. DOI 10.1109/TAC.2005.864190 (Crossref) | Caltech technical report record https://authors.library.caltech.edu/28030 (CaltechCDSTR:2004.005) and Crossref record | Flocking algorithms with alignment, separation and cohesion; "flocks need no leaders"; split/rejoin manoeuvres |
| cucker2007 | F. Cucker, S. Smale, "Emergent behavior in flocks", IEEE Trans. Autom. Control 52(5):852-862, 2007. DOI 10.1109/TAC.2007.895842 | CityU Scholars record https://scholars.cityu.edu.hk/en/publications/emergent-behavior-in-flocks/ | Velocity consensus with distance-decaying coupling; convergence conditions |
| ballerini2008 | M. Ballerini et al. (12 authors), "Interaction ruling animal collective behavior depends on topological rather than metric distance: Evidence from a field study", PNAS 105:1232-1237, 2008. DOI 10.1073/pnas.0711437105 | arXiv abstract page https://arxiv.org/abs/0709.1916 | Topological (about 6 to 7 neighbours) versus metric interaction; motivates sensitivity S1 |
| vicsek2012 | T. Vicsek, A. Zafeiris, "Collective motion", Physics Reports 517:71-140, 2012. DOI 10.1016/j.physrep.2012.03.004 | arXiv abstract page https://arxiv.org/abs/1010.5017 | Review of models, order parameters and transitions |

## 2. Synthesis

- Alignment-only models (vicsek1995) already produce ordered collective motion at low noise and sufficient density, so A0 is a meaningful baseline, not a strawman.
- Zonal models (couzin2002, reynolds1987) add repulsion and attraction; couzin2002 reports that small changes in zone widths shift the collective state, which predicts that A1 versus A0 differences may depend strongly on parameters. EXP-002 therefore spans a grid rather than one cell.
- Control theory (jadbabaie2003, olfatisaber2006, cucker2007) ties convergence to graph connectivity or coupling decay. This gives the candidate mechanism for H1: cohesion may help by preserving connectivity after a shock.
- Field evidence for topological interaction (ballerini2008) is a reason to test whether conclusions depend on metric neighbourhoods (S1). The project does not claim biological fidelity.

## 3. Gap and contribution (bounded)

The narrow contribution proposed is methodological and reproducible: a matched-seed, preregistered comparison of alignment-only and zonal rules, with a centralized reference, after a defined heading shock, reporting seed-level uncertainty and sensitivity. No novelty claim is made: the search was not systematic, and similar comparisons may exist.

## 4. Not yet verified (do not cite as read)

- Full texts of all items above (only abstracts and metadata were read).
- Literature specifically on disturbance recovery or perturbation response in flocking models; a targeted search is an M1 task.
- Cell-list / spatial hashing references for neighbour search; to be cited from a verified source in M1 or described without citation.

## 5. Datasets

No external dataset is used (decision DL-003). Empirical trajectory datasets (for example, starling flock reconstructions) were not searched for redistribution terms because they are out of scope; any future use requires a licence check and is a blocker until checked.

## 6. M4 audit note (2026-11-25)

- jadbabaie2003 was accessed at metadata level only (Crossref record). The "Relevance" column above describes the expected content, not something read. From M4 the manuscript and the EXP-002 report cite it for its topic only (evidence audit F1, `research/publication/evidence_audit.md`).
- No source in this list was read in full; the manuscript reference list states the level read for each entry.
- The targeted search for disturbance-recovery literature listed in section 4 was not carried out; the manuscript makes no claim about that literature.
