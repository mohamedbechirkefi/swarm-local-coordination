<!-- SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0 -->
# experiments/

Runnable experiment configurations (`experiments/EXP-NNN/*.json`, experiment schema 1.0.0) consumed by the CLI. Protocols, reports and per-experiment manifests live in `research/experiments/EXP-NNN/`.

- `EXP-001/smoke.json`: EXP-001 smoke matrix (exploratory).
- `EXP-001/burnin_scan.json`: pre-disturbance scan of the 18 planned cells (exploratory; no post-disturbance outcome).
- `EXP-001/bench.json`: neighbour-search benchmark (exploratory).

No EXP-002 or EXP-003 configuration is committed: they are written when the owner freezes the protocol, and they must carry `"confirmatory": true`, which the runner refuses until `research/protocol_freeze.json` exists and matches.
